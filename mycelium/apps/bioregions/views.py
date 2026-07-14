import json
import re
import unicodedata
from copy import deepcopy
from urllib.error import URLError, HTTPError
from urllib.request import Request, urlopen

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.core.cache import caches
from django.conf import settings
from apps.acl.utils import get_permitted_objects, get_permitted_object, is_permitted
from .models import Bioregion
from .forms import BioregionForm
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.urls import reverse
from apps.utils.dump import dump
from apps.utils.pagination import paginate_queryset
from apps.utils.form_tokens import get_form_token, validate_form_token


TILE_PROVIDER_URLS = {
    "osm": "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
    "carto": "https://a.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png",
    "esri": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}",
}


def bioregion_tile_proxy_view(request, provider, z, x, y):
    template = TILE_PROVIDER_URLS.get(provider)
    if not template:
        return HttpResponse("Unknown tile provider", status=404, content_type="text/plain")

    if z < 0 or z > 22 or x < 0 or y < 0:
        return HttpResponse("Invalid tile coordinates", status=400, content_type="text/plain")

    try:
        tile_cache = caches["tiles"]
    except Exception:
        tile_cache = caches["default"]

    cache_key = f"tile:{provider}:{z}:{x}:{y}"
    cached_tile = tile_cache.get(cache_key)
    if cached_tile:
        body, content_type = cached_tile
        cached_response = HttpResponse(body, content_type=content_type)
        cached_response["Cache-Control"] = "public, max-age=300"
        cached_response["X-Tile-Cache"] = "HIT"
        return cached_response

    tile_url = template.format(z=z, x=x, y=y)
    upstream_request = Request(
        tile_url,
        headers={
            "User-Agent": "CommunityMyceliumTileProxy/1.0",
            "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
        },
    )

    try:
        with urlopen(upstream_request, timeout=10) as response:
            body = response.read()
            content_type = response.headers.get("Content-Type", "image/png")

        tile_cache.set(
            cache_key,
            (body, content_type),
            timeout=getattr(settings, "MAP_TILE_CACHE_TIMEOUT", 900),
        )

        proxy_response = HttpResponse(body, content_type=content_type)
        # Client can re-use tiles briefly while server keeps a short bounded cache.
        proxy_response["Cache-Control"] = "public, max-age=300"
        proxy_response["X-Tile-Cache"] = "MISS"
        return proxy_response
    except HTTPError as exc:
        return HttpResponse(
            f"Upstream tile error ({exc.code})",
            status=502,
            content_type="text/plain",
        )
    except URLError:
        return HttpResponse(
            "Unable to reach tile provider",
            status=502,
            content_type="text/plain",
        )


CHALLENGE_IMPORT_SCHEMA = {
    "schema_version": 1,
    "dry_run": False,
    "upsert_by_title": True,
    "challenges": [
        {
            "title": "Soil degradation from industrial farming",
            "description": "Topsoil loss exceeds regeneration rate in the valley's agricultural zones.",
            "level": -40,
            "facet_title": "Earth Erosion",
            "location": "",
            "latitude": None,
            "longitude": None,
        },
        {
            "title": "Community-led watershed restoration programme",
            "description": "Volunteers working to revegetate riparian zones and reduce runoff.",
            "level": 30,
            "facet_title": "Regenerative Abundance",
            "location": "",
            "latitude": None,
            "longitude": None,
        },
    ],
}

ALL_METACRISIS_FACET_TITLES = [
    # Problem facets
    "Extinction Edge",
    "Fragile Web",
    "Truth Tornado",
    "Soul Split",
    "Earth Erosion",
    "Power Pyramid",
    "Tech Tsunami",
    "Leadership Lapse",
    # Solution / response facets
    "Resilient Renaissance",
    "Interwoven Harmony",
    "Shared Light",
    "Cultural Wholeness",
    "Regenerative Abundance",
    "Equitable Commons",
    "Tech Symphony",
    "Adaptive Stewardship",
]


def _normalize_facet_title(value):
    if value is None:
        return ""
    normalized = unicodedata.normalize("NFKC", str(value))
    normalized = normalized.replace("\u00A0", " ")
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip().lower()


def _normalize_challenge_title(value):
    return _normalize_facet_title(value)


def _bioregion_challenge_import_schema_for(bioregion):
    schema = deepcopy(CHALLENGE_IMPORT_SCHEMA)
    schema["facet_title_reference"] = {
        "all_available_facets": ALL_METACRISIS_FACET_TITLES,
        "problem_facets": ALL_METACRISIS_FACET_TITLES[:8],
        "solution_facets": ALL_METACRISIS_FACET_TITLES[8:],
        "facet_descriptions": {
            "Extinction Edge": "Existential risks — nuclear war, unchecked AI, catastrophic climate change.",
            "Fragile Web": "Systemic vulnerabilities in economic, political, environmental and technological networks.",
            "Truth Tornado": "Breakdown of shared understanding; misinformation, polarisation, erosion of expertise.",
            "Soul Split": "Fragmentation of cultural identity, meaning, and community bonds; mental-health crisis.",
            "Earth Erosion": "Ecological degradation, biodiversity loss, climate change, ecosystem disruption.",
            "Power Pyramid": "Extreme inequality; concentration of wealth and power; social unrest.",
            "Tech Tsunami": "Rapid tech change outpacing social, legal, and ethical governance capacity.",
            "Leadership Lapse": "Governance deficits — siloed, slow, corrupt, or short-term-focused institutions.",
            "Resilient Renaissance": "Adaptive systems and collaborative governance enabling long-term human flourishing.",
            "Interwoven Harmony": "Resilient, cooperative interdependencies that prevent cascading systemic failures.",
            "Shared Light": "Trustworthy knowledge ecosystems, open inquiry, and collective wisdom.",
            "Cultural Wholeness": "Flourishing diverse narratives, strong community bonds, psychological well-being.",
            "Regenerative Abundance": "Human activity regenerating ecosystems; biodiversity, circular economy, ecological stewardship.",
            "Equitable Commons": "Just distribution of power and resources; participatory governance; dignity for all.",
            "Tech Symphony": "Humane, ethical technology integration enhancing human agency and common good.",
            "Adaptive Stewardship": "Agile, wise, transparent leadership navigating complexity in service of shared futures.",
        },
    }
    schema["field_guide"] = {
        "title": "Required. Clear, specific challenge or response description for this bioregion.",
        "description": "Optional but recommended. Provide context, evidence, or narrative detail.",
        "level": "Integer from -100 to 100. Negative = problem severity; positive = solution/capacity strength. 0 = neutral.",
        "facet_title": "Optional. Must match exactly one of the 16 facet titles listed in facet_title_reference.",
        "location": "Optional text description of a specific place within the bioregion.",
        "latitude": "Optional float (decimal degrees).",
        "longitude": "Optional float (decimal degrees).",
    }
    return schema


def _normalize_challenge_import_payload(raw_payload):
    try:
        payload = json.loads(raw_payload)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON: {exc}")

    if not isinstance(payload, dict):
        raise ValueError("JSON root must be an object.")

    challenges = payload.get("challenges")
    if not isinstance(challenges, list) or not challenges:
        raise ValueError("'challenges' must be a non-empty array.")

    normalized = []
    for index, item in enumerate(challenges, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"challenges[{index}] must be an object.")

        title = (item.get("title") or "").strip()
        if not title:
            raise ValueError(f"challenges[{index}].title is required.")

        raw_level = item.get("level", 0)
        try:
            level = int(raw_level)
        except (TypeError, ValueError):
            raise ValueError(f"challenges[{index}].level must be an integer.")
        if not (-100 <= level <= 100):
            raise ValueError(f"challenges[{index}].level must be between -100 and 100.")

        facet_title = (item.get("facet_title") or "").strip()
        if facet_title:
            valid_normalized = {_normalize_facet_title(t) for t in ALL_METACRISIS_FACET_TITLES}
            if _normalize_facet_title(facet_title) not in valid_normalized:
                raise ValueError(
                    f"challenges[{index}].facet_title '{facet_title}' is not a recognised facet. "
                    f"Use one of: {', '.join(ALL_METACRISIS_FACET_TITLES)}"
                )

        raw_lat = item.get("latitude")
        raw_lon = item.get("longitude")
        try:
            latitude = float(raw_lat) if raw_lat not in (None, "") else None
        except (TypeError, ValueError):
            raise ValueError(f"challenges[{index}].latitude must be a number or null.")
        try:
            longitude = float(raw_lon) if raw_lon not in (None, "") else None
        except (TypeError, ValueError):
            raise ValueError(f"challenges[{index}].longitude must be a number or null.")

        normalized.append({
            "title": title,
            "description": (item.get("description") or "").strip() or None,
            "level": level,
            "facet_title": facet_title,
            "location": (item.get("location") or "").strip() or None,
            "latitude": latitude,
            "longitude": longitude,
        })

    return {
        "challenges": normalized,
        "dry_run": bool(payload.get("dry_run", False)),
        "upsert_by_title": bool(payload.get("upsert_by_title", True)),
    }


def bioregion_list_view(request):
    if request.user.is_authenticated:
        bioregions = get_permitted_objects(request.user, "view", Bioregion)
    else:
        # Anonymous users can see all bioregions (title/description only in template)
        bioregions = Bioregion.objects.all()
    
    # Pagination using helper function
    bioregions_page, pagination_data = paginate_queryset(bioregions, request, per_page=10)
    
    return render(request, "bioregions/bioregion_list.html", {
        "bioregions": bioregions_page,
        "pagination": pagination_data,
    })


def bioregion_detail_view(request, pk):
    if request.user.is_authenticated:
        bioregion = get_permitted_object(request.user, "view", Bioregion, pk)
    else:
        # Anonymous users can see bioregion title/description
        try:
            bioregion = Bioregion.objects.get(pk=pk)
        except Bioregion.DoesNotExist:
            from django.http import Http404
            raise Http404
    
    # Get communities connected to this bioregion
    from apps.communities.models import Community
    from apps.locations.models import Location
    from apps.projects.models import Project
    from apps.stories.models import Story, StoryAttachment
    from django.contrib.contenttypes.models import ContentType
    from django.contrib.auth import get_user_model
    from django.db.models import Q
    UserModel = get_user_model()
    if request.user.is_authenticated:
        user = request.user
        communities = Community.objects.filter(bioregions=bioregion).filter(
            Q(created_by=user) | Q(members=user) | Q(view_members=True) | Q(view_public=True)
        ).distinct()
        locations = Location.objects.filter(bioregions=bioregion).filter(
            Q(created_by=user) | Q(view_members=True) | Q(view_public=True)
        ).distinct()
        projects = Project.objects.filter(bioregions=bioregion).filter(
            Q(created_by=user) | Q(members=user) | Q(owners=user) | Q(admins=user) | Q(view_members=True) | Q(view_public=True)
        ).distinct()
        people = UserModel.objects.filter(user_bioregions=bioregion).filter(
            Q(id=user.id) | Q(view_members=True) | Q(view_public=True)
        ).distinct()
    else:
        communities = Community.objects.filter(bioregions=bioregion, view_public=True)
        locations = Location.objects.filter(bioregions=bioregion, view_public=True)
        projects = Project.objects.filter(bioregions=bioregion, view_public=True)
        people = UserModel.objects.filter(user_bioregions=bioregion, view_public=True)

    bioregion_content_type = ContentType.objects.get_for_model(Bioregion)
    attached_story_ids = StoryAttachment.objects.filter(
        content_type=bioregion_content_type,
        object_id=bioregion.pk,
    ).values_list("story_id", flat=True)
    attached_story_id_set = set(attached_story_ids)

    if request.user.is_authenticated:
        permitted_stories = get_permitted_objects(request.user, "view", Story)
        if hasattr(permitted_stories, "filter"):
            bioregion_stories = permitted_stories.filter(pk__in=attached_story_id_set).order_by("-created_at")
            bioregion_story_count = bioregion_stories.count()
            bioregion_stories_preview = bioregion_stories[:3]
        else:
            filtered_stories = [s for s in permitted_stories if s.pk in attached_story_id_set]
            filtered_stories.sort(key=lambda s: s.created_at, reverse=True)
            bioregion_story_count = len(filtered_stories)
            bioregion_stories_preview = filtered_stories[:3]
    else:
        bioregion_stories = Story.objects.filter(pk__in=attached_story_id_set, view_public=True).order_by("-created_at")
        bioregion_story_count = bioregion_stories.count()
        bioregion_stories_preview = bioregion_stories[:3]
    
    challenge_import_schema = json.dumps(_bioregion_challenge_import_schema_for(bioregion), indent=2)

    map_locations = []
    visible_locations_by_id = {}
    for location in locations:
        if location.latitude is None or location.longitude is None:
            continue
        visible_locations_by_id[location.pk] = location
        map_locations.append({
            "kind": "Location",
            "title": location.title,
            "description": (location.description or "")[:180],
            "latitude": float(location.latitude),
            "longitude": float(location.longitude),
            "url": reverse("location_detail", kwargs={"pk": location.pk}),
        })

    map_projects = []
    for project in projects.select_related("primary_location"):
        primary_location = project.primary_location
        if not primary_location:
            continue
        if not primary_location.bioregions.filter(pk=bioregion.pk).exists():
            continue
        if primary_location.latitude is None or primary_location.longitude is None:
            continue
        map_projects.append({
            "kind": "Project",
            "title": project.title,
            "description": (project.description or "")[:180],
            "latitude": float(primary_location.latitude),
            "longitude": float(primary_location.longitude),
            "url": reverse("project_detail", kwargs={"pk": project.pk}),
        })

    map_communities = []
    for community in communities.select_related("primary_location"):
        primary_location = community.primary_location
        if not primary_location:
            continue
        if not primary_location.bioregions.filter(pk=bioregion.pk).exists():
            continue
        if primary_location.latitude is None or primary_location.longitude is None:
            continue
        map_communities.append({
            "kind": "Community",
            "title": community.title,
            "description": (community.description or "")[:180],
            "latitude": float(primary_location.latitude),
            "longitude": float(primary_location.longitude),
            "url": reverse("community_detail", kwargs={"pk": community.pk}),
        })

    map_people = []
    for person in people.select_related("primary_location"):
        primary_location = person.primary_location
        if not primary_location:
            continue
        if not primary_location.bioregions.filter(pk=bioregion.pk).exists():
            continue
        if primary_location.latitude is None or primary_location.longitude is None:
            continue
        map_people.append({
            "kind": "Person",
            "title": person.get_full_name() or person.username,
            "description": (person.bio or person.user_location or "")[:180],
            "latitude": float(primary_location.latitude),
            "longitude": float(primary_location.longitude),
            "url": reverse("user_detail", kwargs={"pk": person.pk}),
        })

    if request.user.is_authenticated:
        visible_stories = get_permitted_objects(request.user, "view", Story)
        if hasattr(visible_stories, "filter"):
            stories_qs = visible_stories.select_related("primary_location").prefetch_related("locations", "attachments__content_type", "attachments__content_object")
        else:
            visible_story_ids = [s.pk for s in visible_stories]
            stories_qs = Story.objects.filter(pk__in=visible_story_ids).select_related("primary_location").prefetch_related("locations", "attachments__content_type", "attachments__content_object")
    else:
        stories_qs = Story.objects.filter(view_public=True).select_related("primary_location").prefetch_related("locations", "attachments__content_type", "attachments__content_object")

    from apps.locations.models import Location
    location_content_type = ContentType.objects.get_for_model(Location)
    visible_location_ids = set(visible_locations_by_id.keys())
    story_ids = list(stories_qs.values_list("id", flat=True))
    attached_story_location_pairs = StoryAttachment.objects.filter(
        story_id__in=story_ids,
        content_type=location_content_type,
        object_id__in=visible_location_ids,
    ).values_list("story_id", "object_id")
    attached_story_location_map = {}
    for story_id, object_id in attached_story_location_pairs:
        if story_id not in attached_story_location_map:
            attached_story_location_map[story_id] = object_id

    map_stories = []
    for story in stories_qs:
        marker_location = None
        primary_location = story.primary_location
        if primary_location and primary_location.pk in visible_location_ids:
            marker_location = primary_location

        if marker_location is None:
            for linked_location in story.locations.all():
                if linked_location.pk in visible_location_ids:
                    marker_location = linked_location
                    break

        if marker_location is None:
            attached_location_id = attached_story_location_map.get(story.pk)
            marker_location = visible_locations_by_id.get(attached_location_id)

        if marker_location is None:
            continue
        if marker_location.latitude is None or marker_location.longitude is None:
            continue

        map_stories.append({
            "kind": "Story",
            "title": story.title,
            "description": (story.text_content or "")[:180],
            "latitude": float(marker_location.latitude),
            "longitude": float(marker_location.longitude),
            "url": reverse("story_detail", kwargs={"pk": story.pk}),
            "relevant_tags": story.relevant_tags,
        })

    return render(request, "bioregions/bioregion_detail.html", {
        "bioregion": bioregion,
        "communities": communities,
        "locations": locations,
        "locations_count": locations.count() if hasattr(locations, "count") else len(locations),
        "projects": projects,
        "people": people,
        "bioregion_story_count": bioregion_story_count,
        "bioregion_stories_preview": bioregion_stories_preview,
        "challenge_import_schema": challenge_import_schema,
        "map_locations_json": map_locations,
        "map_projects_json": map_projects,
        "map_communities_json": map_communities,
        "map_people_json": map_people,
        "map_stories_json": map_stories,
    })


@login_required
def bioregion_challenge_import_view(request, pk):
    from apps.challenges.models import Challenge
    from apps.metacrisis_facets.models import Metacrisis_facet

    bioregion = get_permitted_object(request.user, "change", Bioregion, pk)

    if request.method != "POST":
        return redirect("bioregion_detail", pk=bioregion.pk)

    raw_payload = (request.POST.get("challenge_import_json") or "").strip()
    if not raw_payload:
        messages.error(request, "Paste JSON into the import box before submitting.")
        return redirect("bioregion_detail", pk=bioregion.pk)

    try:
        payload = _normalize_challenge_import_payload(raw_payload)
    except ValueError as exc:
        messages.error(request, f"Import failed: {exc}")
        return redirect("bioregion_detail", pk=bioregion.pk)

    dry_run = (request.POST.get("dry_run") in {"1", "true", "on"}) or payload["dry_run"]
    upsert_by_title = payload["upsert_by_title"]

    # Build facet lookup: normalised title -> Metacrisis_facet
    facet_map = {
        _normalize_facet_title(f.title): f
        for f in Metacrisis_facet.objects.all()
    }

    # Build existing-challenge lookup for upsert
    existing_challenges = {}
    if upsert_by_title:
        for ch in Challenge.objects.filter(related_bioregion=bioregion).only("id", "title"):
            key = _normalize_challenge_title(ch.title)
            if key not in existing_challenges:
                existing_challenges[key] = ch

    created_count = 0
    updated_count = 0

    try:
        with transaction.atomic():
            for item in payload["challenges"]:
                title_key = _normalize_challenge_title(item["title"])

                facet = None
                if item["facet_title"]:
                    facet = facet_map.get(_normalize_facet_title(item["facet_title"]))
                    if facet is None:
                        raise ValueError(
                            f"Facet '{item['facet_title']}' not found in the database. "
                            f"Run the seed_metacrisis_facets management command first."
                        )

                existing = existing_challenges.get(title_key) if upsert_by_title else None

                if existing:
                    if not dry_run:
                        existing.description = item["description"]
                        existing.level = item["level"]
                        existing.related_facet = facet
                        existing.location = item["location"]
                        existing.latitude = item["latitude"]
                        existing.longitude = item["longitude"]
                        existing.save()
                    updated_count += 1
                else:
                    if not dry_run:
                        ch = Challenge.objects.create(
                            title=item["title"],
                            description=item["description"],
                            level=item["level"],
                            related_facet=facet,
                            related_bioregion=bioregion,
                            location=item["location"],
                            latitude=item["latitude"],
                            longitude=item["longitude"],
                            created_by=request.user,
                        )
                        if upsert_by_title:
                            existing_challenges[title_key] = ch
                    created_count += 1
    except ValueError as exc:
        messages.error(request, f"Import failed: {exc}")
        return redirect("bioregion_detail", pk=bioregion.pk)

    if dry_run:
        messages.success(
            request,
            f"Dry run: would create {created_count} challenge{'s' if created_count != 1 else ''} "
            f"and update {updated_count} existing challenge{'s' if updated_count != 1 else ''}. "
            f"No changes saved.",
        )
    else:
        parts = []
        if created_count:
            parts.append(f"Created {created_count} challenge{'s' if created_count != 1 else ''}.")
        if updated_count:
            parts.append(f"Updated {updated_count} challenge{'s' if updated_count != 1 else ''}.")
        messages.success(request, " ".join(parts) if parts else "Nothing to import.")

    return redirect("bioregion_detail", pk=bioregion.pk)


@login_required
def bioregion_create_view(request):
    if not is_permitted(request.user, "add", "bioregions.bioregion"):
        raise PermissionDenied

    if request.method == "POST":
        if not validate_form_token(request, 'bioregion_create'):
            messages.error(request, "This form has already been submitted. Please don't use the back button after submitting.")
            form = BioregionForm()
            form_token = get_form_token(request, 'bioregion_create')
            return render(request, "bioregions/bioregion_form.html", {"form": form, "form_token": form_token})
        
        form = BioregionForm(request.POST, request.FILES)
        if form.is_valid():
            bioregion = form.save(commit=False)
            bioregion.created_by = request.user
            bioregion.save()
            form.save_m2m()  # Save many-to-many relationships
            messages.success(request, "Bioregion created successfully!")
            return redirect("bioregion_detail", pk=bioregion.pk)
    else:
        form = BioregionForm()

    form_token = get_form_token(request, 'bioregion_create')
    return render(
        request,
        "bioregions/bioregion_form.html",
        {"form": form, "form_token": form_token},
    )


@login_required
def bioregion_edit_view(request, pk):
    bioregion = get_permitted_object(request.user, "change", Bioregion, pk)

    if request.method == "POST":
        form = BioregionForm(request.POST, request.FILES, instance=bioregion)
        if form.is_valid():
            form.save()
            messages.success(request, "Bioregion updated successfully!")
            return redirect("bioregion_detail", pk=bioregion.pk)
    else:
        form = BioregionForm(instance=bioregion)

    return render(
        request,
        "bioregions/bioregion_form.html",
        {"form": form, "bioregion": bioregion},
    )


@login_required
def bioregion_delete_view(request, pk):
    bioregion = get_permitted_object(request.user, "delete", Bioregion, pk)

    if request.method == "POST":
        bioregion.delete()
        messages.success(request, "Bioregion deleted successfully!")
        return redirect("bioregion_list")

    return render(request, "bioregions/bioregion_confirm_delete.html", {"bioregion": bioregion})
