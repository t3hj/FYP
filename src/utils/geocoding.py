from geopy.geocoders import Nominatim


_geolocator = Nominatim(user_agent="local_lens_app")


def geocode_location(location_text):
    if not location_text or not location_text.strip():
        return None, None

    try:
        result = _geolocator.geocode(location_text, timeout=10)
        if not result:
            return None, None
        return float(result.latitude), float(result.longitude)
    except Exception:
        return None, None


def reverse_geocode_location(latitude, longitude):
    """
    Convert latitude/longitude to a human-readable address.
    Returns the address string, or None if reverse geocoding fails.
    """
    if latitude is None or longitude is None:
        return None

    try:
        result = _geolocator.reverse(f"{latitude}, {longitude}", timeout=10, language="en")
        if result:
            return result.address
        return None
    except Exception:
        return None

