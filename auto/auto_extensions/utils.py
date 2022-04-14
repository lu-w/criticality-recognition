import math

"""
Some common functionality for A.U.T.O. extensions, especially for checking domain constraints for augmentation.
"""


def same_scene(x, y):
    """
    Returns true iff. x and y are in the same scene.
    """
    try:
        return hasattr(x, "in_traffic_model") and hasattr(y, "in_traffic_model") and x.in_traffic_model and \
               y.in_traffic_model and x.in_traffic_model[0] == y.in_traffic_model[0]
    except TypeError:
        return False


def has_geometry(x):
    """
    Returns true iff x has a geometry represented as a WKT literal.
    """
    try:
        return hasattr(x, "hasGeometry") and len(x.hasGeometry) > 0 and len(x.hasGeometry[0].asWKT) > 0 and \
               x.hasGeometry[0].asWKT[0] != "POLYGON EMPTY"
    except TypeError:
        return False


def is_valid_interval(x):
    """
    Returns true iff x is a well-shaped concrete time interval (i.e. has valid beginning and end).
    """
    try:
        return hasattr(x, "hasBeginning") and len(x.hasBeginning) > 0 and \
               len(x.hasBeginning[0].inTimePosition) > 0 and \
               len(x.hasBeginning[0].inTimePosition[0].numericPosition) > 0 and hasattr(x, "hasEnd") and \
               len(x.hasEnd) > 0 and len(x.hasEnd[0].inTimePosition) > 0 and \
               len(x.hasEnd[0].inTimePosition[0].numericPosition) > 0 and \
               x.hasBeginning[0].inTimePosition[0].numericPosition < x.hasEnd[0].inTimePosition[0].numericPosition
    except TypeError:
        return False


def is_valid_instant(x):
    """
    Returns true iff x is a well-shaped concrete time instant (i.e. has a numeric position).
    """
    try:
        return hasattr(x, "inTimePosition") and len(x.inTimePosition) > 0 and \
               len(x.inTimePosition[0].numericPosition) > 0
    except TypeError:
        return False


def get_angle_between_yaw_and_point(a, p, yaw):
    """
    Gets the angle between the point p and the vector starting from a's centroid with the given yaw angle.
    """
    p_yaw = [math.cos(math.radians(yaw)), math.sin(math.radians(yaw))]
    p_self = [p[0] - a.centroid.x, p[1] - a.centroid.y]
    angle = math.degrees(math.atan2(*p_yaw) - math.atan2(*p_self)) % 360
    return angle


def left_front_point(a, yaw):
    """
    Gets the left front point of a's boundary (front-left determined through given yaw).
    """
    try:
        for p in zip(a.boundary.xy[0], a.boundary.xy[1]):
            angle = get_angle_between_yaw_and_point(a, p, yaw)
            if 270 <= angle < 360:
                return p
    except NotImplementedError:
        return a.centroid


def right_front_point(a, yaw):
    """
    Gets the right front point of a's boundary (front-right determined through given yaw).
    """
    try:
        for p in zip(a.boundary.xy[0], a.boundary.xy[1]):
            angle = get_angle_between_yaw_and_point(a, p, yaw)
            if 0 <= angle < 90:
                return p
    except NotImplementedError:
        return a.centroid


def left_back_point(a, yaw):
    """
    Gets the left back point of a's boundary (left-back determined through given yaw).
    """
    try:
        for p in zip(a.boundary.xy[0], a.boundary.xy[1]):
            angle = get_angle_between_yaw_and_point(a, p, yaw)
            if 180 <= angle < 270:
                return p
    except NotImplementedError:
        return a.centroid


def right_back_point(a, yaw):
    """
    Gets the right back point of a's boundary (left-back determined through given yaw).
    """
    try:
        for p in zip(a.boundary.xy[0], a.boundary.xy[1]):
            angle = get_angle_between_yaw_and_point(a, p, yaw)
            if 90 <= angle < 180:
                return p
    except NotImplementedError:
        return a.centroid


def convert_local_to_global_vector(v: list, yaw: float):
    """
    Converts the given vector in vehicle coordinate system to the global one under the given vehicle yaw.
    """
    vx = math.cos(math.radians(yaw)) * v[0] - math.sin(math.radians(yaw)) * v[1]
    vy = math.sin(math.radians(yaw)) * v[0] + math.cos(math.radians(yaw)) * v[1]
    return [vx, vy]
