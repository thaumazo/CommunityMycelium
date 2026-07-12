from django.core.management.base import BaseCommand

from apps.locations.geocoding import GeocodingError, geocode_address
from apps.locations.models import Location


class Command(BaseCommand):
    help = "Geocode locations with addresses but missing latitude/longitude using Nominatim."

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=0, help="Maximum number of locations to process.")
        parser.add_argument("--dry-run", action="store_true", help="Show what would be geocoded without saving.")
        parser.add_argument("--force", action="store_true", help="Re-geocode even if one coordinate is already present.")

    def handle(self, *args, **options):
        queryset = Location.objects.exclude(address__isnull=True).exclude(address__exact="")
        if options["force"]:
            queryset = queryset.order_by("pk")
        else:
            queryset = queryset.filter(latitude__isnull=True, longitude__isnull=True).order_by("pk")

        if options["limit"]:
            queryset = queryset[: options["limit"]]

        processed = 0
        updated = 0
        failed = 0

        for location in queryset:
            processed += 1
            self.stdout.write(f"[{processed}] Geocoding location #{location.pk}: {location.title}")
            try:
                result = geocode_address(location.address)
            except GeocodingError as exc:
                failed += 1
                self.stderr.write(f"  Failed: {exc}")
                continue

            self.stdout.write(
                f"  -> {result.latitude:.6f}, {result.longitude:.6f}"
                + (" (cached)" if result.cached else "")
            )
            if options["dry_run"]:
                continue

            location.latitude = result.latitude
            location.longitude = result.longitude
            location.save(update_fields=["latitude", "longitude"])
            updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Processed {processed} locations; updated {updated}; failed {failed}."
            )
        )
