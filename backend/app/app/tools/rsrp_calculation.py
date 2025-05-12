import math
from typing import List
from app.models.Cell import Cell
from app.tools.distance import distance


def cartesian_from_haversine(lat, lng, lat0, lng0):
    """Uses haversine distance approximation to transform lat, lnt into cartesian
    coordinates
    """
    avg_lat = (lat0 + lat) / 2
    avg_lng = (lng0 + lng) / 2

    x = distance(avg_lat, lng0, avg_lat, lng)
    y = distance(lat0, avg_lng, lat, avg_lng)
    return x, y


def check_path_loss(ue_lat: float, ue_long: float, cells: List[Cell]):
    losses_by_cell = {}
    for cell in cells:
        loss = calc_path_loss(ue_lat, ue_long, cell.latitude, cell.longitude)
        losses_by_cell[cell.id] = loss
    return losses_by_cell


def calc_path_loss(
    ue_lat: float, ue_long: float, cell_lat: float, cell_long: float, fc=2.6475
):
    distance_3d = distance(ue_lat, ue_long, cell_lat, cell_long)
    path_loss = 28 + 22 * math.log(distance_3d) + 20 * math.log(fc)
    return path_loss


def check_rsrp(ue_lat: float, ue_long: float, cells: List[Cell], power=30):
    rsrps_by_cell = {}
    losses = check_path_loss(ue_lat, ue_long, cells)
    for key in losses:
        rsrp = power - losses[key]
        rsrps_by_cell[f"{key}"] = rsrp
    return rsrps_by_cell

