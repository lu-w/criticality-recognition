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
        return hasattr(x, "hasGeometry") and len(x.hasGeometry) > 0 and len(x.hasGeometry[0].asWKT[0]) > 0
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
