import math
from typing import List, Optional
from app.models.Cell import Cell


def distance(
    lat1: float, lon1: float, lat2: float, lon2: float
) -> float: 
    # Haversine formula: determines the great-circle distance between two points on a sphere given their longitudes and latitudes.
    R = 6371e3
    φ1 = lat1 * math.pi / 180  # φ, λ in radians
    φ2 = lat2 * math.pi / 180
    Δλ = (lon2 - lon1) * math.pi / 180
    Δφ = (lat2 - lat1) * math.pi / 180

    a = math.sin(Δφ / 2) * math.sin(Δφ / 2) + math.cos(φ1) * math.cos(φ2) * math.sin(
        Δλ / 2
    ) * math.sin(Δλ / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    d = R * c  # in metres

    return d


def check_distance(lat: float, lon: float, cells: List[Cell]) -> tuple[Optional[Cell], dict[str, float]]:

    # logging.info(f"Current cell {current_cell}")
    current_cell = None
    current_cell_dist = float("inf")
    distances = {}
    for cell in cells:
        dist = distance(lat, lon, cell.latitude, cell.longitude)
        distances[f"{cell.id}"] = dist
        # print(f"Distance = {dist} meters from Cell {cell.get('description')}")
        if dist <= cell.radius:
            if dist < current_cell_dist:
                current_cell_dist = dist
                current_cell = cell

    return current_cell, distances
