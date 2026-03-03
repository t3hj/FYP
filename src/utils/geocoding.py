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
