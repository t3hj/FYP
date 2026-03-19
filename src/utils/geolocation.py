"""
GPS extraction from image EXIF data.

Modern smartphones (iPhone iOS 14+, Android) embed GPS in a sub-IFD
pointed to by tag 34853 in the primary EXIF block. Pillow's getexif()
only reads the primary IFD; the GPS dict must be fetched with
exif.get_ifd(34853). The original code used exif.get(34853) which
returns the pointer integer rather than the GPS dict, causing silent
failures on all modern phone photos.
"""

from io import BytesIO

from PIL import Image


def _to_float(value) -> float:
    try:
        return float(value)
    except Exception:
        if hasattr(value, "numerator") and hasattr(value, "denominator"):
            if value.denominator == 0:
                return 0.0
            return float(value.numerator) / float(value.denominator)
        raise


def _dms_to_decimal(dms, ref: str) -> float:
    degrees = _to_float(dms[0])
    minutes = _to_float(dms[1])
    seconds = _to_float(dms[2])
    decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)
    if ref in ("S", "W"):
        decimal = -decimal
    return decimal


def _parse_gps_dict(gps: dict):
    """
    Extract lat/lon from a GPS tag dict (keys are ints 1-4).
    Returns (lat, lon) floats or (None, None).
    """
    latitude      = gps.get(2)
    latitude_ref  = gps.get(1)
    longitude     = gps.get(4)
    longitude_ref = gps.get(3)

    if not (latitude and longitude and latitude_ref and longitude_ref):
        return None, None

    try:
        lat = _dms_to_decimal(latitude,  latitude_ref)
        lon = _dms_to_decimal(longitude, longitude_ref)
        return lat, lon
    except Exception:
        return None, None


def extract_gps_from_image_bytes(file_bytes: bytes):
    """
    Return (latitude, longitude) floats from a JPEG/PNG's EXIF GPS data,
    or (None, None) if no GPS data is found.

    Tries three methods in order so it works on:
      - Modern iPhones / Androids  (GPS in sub-IFD via get_ifd)
      - Older cameras              (GPS directly in primary IFD)
      - Legacy Pillow builds       (_getexif() fallback)
    """
    try:
        image = Image.open(BytesIO(file_bytes))
    except Exception:
        return None, None

    # ── Method 1: sub-IFD (correct method for all modern smartphones) ─────────
    try:
        exif    = image.getexif()
        gps_ifd = exif.get_ifd(34853)      # 34853 = 0x8825 = GPSInfo tag
        if gps_ifd:
            lat, lon = _parse_gps_dict(gps_ifd)
            if lat is not None:
                return lat, lon
    except Exception:
        pass

    # ── Method 2: GPS dict directly in primary IFD (older cameras) ───────────
    try:
        exif     = image.getexif()
        gps_info = exif.get(34853)
        if isinstance(gps_info, dict):
            lat, lon = _parse_gps_dict(gps_info)
            if lat is not None:
                return lat, lon
    except Exception:
        pass

    # ── Method 3: legacy _getexif() (older Pillow / some edge cases) ─────────
    try:
        raw_exif = image._getexif()        # noqa: SLF001
        if raw_exif:
            gps_info = raw_exif.get(34853)
            if isinstance(gps_info, dict):
                lat, lon = _parse_gps_dict(gps_info)
                if lat is not None:
                    return lat, lon
    except Exception:
        pass

    return None, None