import omega_format
from ..utils import *


@monkeypatch(omega_format.LateralMarking)
def to_auto(cls, world: owlready2.World, scenes, identifier=None, parent_identifier=None):

    # Fetches ontologies
    ph = auto.get_ontology(auto.Ontology.Physics, world)
    geo = auto.get_ontology(auto.Ontology.GeoSPARQL, world)
    l1_de = auto.get_ontology(auto.Ontology.L1_DE, world)
    l2_de = auto.get_ontology(auto.Ontology.L2_DE, world)

    # Creates marker instance
    if not cls.type == omega_format.ReferenceTypes.LateralMarkingType.REFLECTORS_LAMPS:
        marker = l1_de.Lateral_Road_Marker()
        reflector_system = False
    else:
        marker = l2_de.Reflective_Raised_Pavement_Marker_Boundary_System()
        reflector_system = True
    marker.identifier = str(parent_identifier) + "_" + str(identifier)

    for scene in scenes:
        scene.has_traffic_entity.append(marker)

    # Type
    marked_object = None
    if cls.type == omega_format.ReferenceTypes.LateralMarkingType.STOP_LINE:
        marker.is_a.append(l1_de.Stop_Line)
    elif cls.type == omega_format.ReferenceTypes.LateralMarkingType.HOLD_LINE:
        marker.is_a.append(l1_de.Wait_Line)
    elif cls.type == omega_format.ReferenceTypes.LateralMarkingType.PEDESTRIAN_CROSSING_LINE:
        marker.is_a.append(l1_de.Road_Marker_Pedestrian_Ford)
        marked_object = l1_de.Pedestrian_Ford()
    elif cls.type == omega_format.ReferenceTypes.LateralMarkingType.BICYCLE_CROSSING:
        marker.is_a.append(l1_de.Road_Marker_Bicycle_Ford)
        marked_object = l1_de.Bicycle_Ford()
    elif cls.type == omega_format.ReferenceTypes.LateralMarkingType.CROSSWALK:
        marker.is_a.append(l1_de.Road_Marker_Pedestrian_Crossing)
        marked_object = l1_de.Pedestrian_Crossing()
    elif cls.type == omega_format.ReferenceTypes.LateralMarkingType.SHARK_TOOTH:
        marker.is_a.append(l1_de.Shark_Tooth_Marker)

    # Color
    if cls.color == omega_format.ReferenceTypes.FlatMarkingColor.RED:
        marker.has_color = [ph.Red]
    elif cls.color == omega_format.ReferenceTypes.FlatMarkingColor.BLUE:
        marker.has_color = [ph.Blue]
    elif cls.color == omega_format.ReferenceTypes.FlatMarkingColor.GREEN:
        marker.has_color = [ph.Green]
    elif cls.color == omega_format.ReferenceTypes.FlatMarkingColor.WHITE:
        marker.has_color = [ph.White]
    elif cls.color == omega_format.ReferenceTypes.FlatMarkingColor.YELLOW:
        marker.has_color = [ph.Yellow]

    # Condition
    if cls.condition == omega_format.ReferenceTypes.FlatMarkingCondition.FINE:
        marker.has_degradation_degree = 0
    elif cls.condition == omega_format.ReferenceTypes.FlatMarkingCondition.CORRUPTED_1_OLD_VISIBIBLE:
        marker.has_degradation_degree = 25
    elif cls.condition == omega_format.ReferenceTypes.FlatMarkingCondition.CORRUPTED_2_FADED:
        marker.has_degradation_degree = 75

    # Marked lanes
    for lane in cls.applicable_lanes.data.values():
        add_relation(marker, "applies_to", lane)

    # Geometry
    wkt_string = "LINESTRING ( "
    for i in range(0, len(cls.polyline.pos_x)):
        wkt_string += str(cls.polyline.pos_x[i]) + " " + str(cls.polyline.pos_y[i]) + " " + \
                      str(cls.polyline.pos_z[i]) + ", "
    wkt_string = wkt_string[:-2] + " )"
    geom = wkt.loads(wkt_string)
    geom = geom.buffer(float(cls.long_size), cap_style=2)
    mark_geom = geo.Geometry()
    mark_geom.asWKT = [str(geom)]
    # Case 1: Standard lateral marker
    if not reflector_system:
        # Width
        if cls.long_size > 0:
            marker.has_width = float(cls.long_size)
        # Need to create actual objects, not only the markings
        marker.hasGeometry = [mark_geom]
        if marked_object:
            marker.applies_to = [marked_object]
            marked_object.hasGeometry = [mark_geom]
    # Case 2: System of guiding lights
    else:
        marker.is_a.append(ph.System & ph.consists_of.only(ph.Spatial_Object & geo.sfWithin.value(mark_geom)))

    add_layer_3_information(cls, marker, world)

    return [(cls, [marker])]
