import math

from sqlalchemy import func as sa_func
from sqlalchemy.orm import Query

from app.models.store import Store


def haversine_filter(query: Query, lat: float, lng: float, radius_km: float) -> Query:
    """Filter stores within radius_km of (lat, lng) using simple Haversine approximation."""
    cos_lat = math.cos(math.radians(lat))
    distance_expr = sa_func.sqrt(
        sa_func.pow((Store.lat - lat) * 111.0, 2)
        + sa_func.pow((Store.lng - lng) * 111.0 * cos_lat, 2)
    )
    return query.filter(Store.lat.isnot(None), Store.lng.isnot(None), distance_expr <= radius_km)


def get_store_ids_in_radius(db, lat: float, lng: float, radius_km: float) -> list[int]:
    """Return IDs of stores within radius."""
    q = db.query(Store.id)
    q = haversine_filter(q, lat, lng, radius_km)
    return [row[0] for row in q.all()]
