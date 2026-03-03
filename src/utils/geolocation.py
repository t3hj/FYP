from io import BytesIO

from PIL import Image


def _to_float(value):
    try:
        return float(value)
    except Exception:
        if hasattr(value, "numerator") and hasattr(value, "denominator"):
            if value.denominator == 0:
                return 0.0
            return float(value.numerator) / float(value.denominator)
        raise


def _dms_to_decimal(dms, ref):
    degrees = _to_float(dms[0])
    minutes = _to_float(dms[1])
    seconds = _to_float(dms[2])
    decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)
    if ref in ("S", "W"):
        decimal = -decimal
    return decimal


def extract_gps_from_image_bytes(file_bytes):
    try:
        image = Image.open(BytesIO(file_bytes))
        exif = image.getexif()
        if not exif:
            return None, None

        gps_info = exif.get(34853)
        if not gps_info:
            return None, None

        latitude = gps_info.get(2)
        latitude_ref = gps_info.get(1)
        longitude = gps_info.get(4)
        longitude_ref = gps_info.get(3)

        if not latitude or not longitude or not latitude_ref or not longitude_ref:
            return None, None

        lat = _dms_to_decimal(latitude, latitude_ref)
        lon = _dms_to_decimal(longitude, longitude_ref)
        return lat, lon
    except Exception:
        return None, None
