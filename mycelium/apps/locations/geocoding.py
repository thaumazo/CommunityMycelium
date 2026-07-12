import json
import socket
import time
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.conf import settings
from django.core.cache import caches


class GeocodingError(Exception):
    pass


@dataclass
class GeocodeResult:
    latitude: float
    longitude: float
    display_name: str
    cached: bool = False


_GEOCODE_CACHE_PREFIX = "nominatim:address:"
_GEOCODE_THROTTLE_KEY = "nominatim:throttle:lock"


def _geocode_cache():
    try:
        return caches["geocoding"]
    except Exception:
        return caches["default"]


def _normalize_address(address: str) -> str:
    return " ".join((address or "").split()).strip()


def _local_ip() -> str:
    try:
        hostname = socket.gethostname()
        return socket.gethostbyname(hostname)
    except Exception:
        return "unknown"


def _user_agent(extra_ip: str | None = None) -> str:
    hostname = socket.gethostname() or "unknown-host"
    local_ip = _local_ip()
    parts = [f"CommunityMycelium/1.0", f"host={hostname}", f"local-ip={local_ip}"]
    if extra_ip:
        parts.append(f"request-ip={extra_ip}")
    contact = getattr(settings, "NOMINATIM_CONTACT_EMAIL", "")
    if contact:
        parts.append(f"contact={contact}")
    return " ".join(parts)


def _throttle():
    cache = _geocode_cache()
    interval = float(getattr(settings, "NOMINATIM_MIN_INTERVAL_SECONDS", 1.1))
    timeout_seconds = max(1, int(interval) + 1)
    while not cache.add(_GEOCODE_THROTTLE_KEY, "1", timeout=timeout_seconds):
        time.sleep(interval)


def geocode_address(address: str, request_ip: str | None = None) -> GeocodeResult:
    normalized = _normalize_address(address)
    if not normalized:
        raise GeocodingError("Address is required for geocoding.")

    cache = _geocode_cache()
    cache_key = _GEOCODE_CACHE_PREFIX + normalized.lower()
    cached = cache.get(cache_key)
    if cached:
        return GeocodeResult(
            latitude=cached["latitude"],
            longitude=cached["longitude"],
            display_name=cached["display_name"],
            cached=True,
        )

    _throttle()

    params = {
        "q": normalized,
        "format": "jsonv2",
        "limit": 1,
        "addressdetails": 1,
    }
    contact = getattr(settings, "NOMINATIM_CONTACT_EMAIL", "")
    if contact:
        params["email"] = contact

    endpoint = getattr(settings, "NOMINATIM_GEOCODE_URL", "https://nominatim.openstreetmap.org/search")
    url = endpoint + "?" + urlencode(params)
    request = Request(
        url,
        headers={
            "User-Agent": _user_agent(request_ip),
            "Accept": "application/json",
        },
    )

    try:
        with urlopen(request, timeout=getattr(settings, "NOMINATIM_TIMEOUT_SECONDS", 10)) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        raise GeocodingError(f"Geocoding service returned HTTP {exc.code}.") from exc
    except URLError as exc:
        raise GeocodingError("Unable to reach geocoding service.") from exc
    except (ValueError, json.JSONDecodeError) as exc:
        raise GeocodingError("Geocoding service returned invalid data.") from exc

    if not payload:
        raise GeocodingError("No coordinates found for that address.")

    first = payload[0]
    try:
        result = GeocodeResult(
            latitude=float(first["lat"]),
            longitude=float(first["lon"]),
            display_name=first.get("display_name", normalized),
            cached=False,
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise GeocodingError("Geocoding result was missing coordinates.") from exc

    cache.set(
        cache_key,
        {
            "latitude": result.latitude,
            "longitude": result.longitude,
            "display_name": result.display_name,
        },
        timeout=int(getattr(settings, "NOMINATIM_CACHE_TIMEOUT", 60 * 60 * 24 * 30)),
    )
    return result
