import omega_format
from ..utils import *


@monkeypatch(omega_format.Lane)
def to_auto(cls, world: owlready2.World, scenes, identifier=None, parent_identifier=None):
    assert not (cls.border_right_is_inverted or cls.border_left_is_inverted)
    # Note: classification and sub_type are ignored as this can be easily inferred by spatial properties

    # Fetches ontologies
    geo = auto.get_ontology(auto.Ontology.GeoSPARQL, world)
    l1_core = auto.get_ontology(auto.Ontology.L1_Core, world)
    l1_de = auto.get_ontology(auto.Ontology.L1_DE, world)
    l2_core = auto.get_ontology(auto.Ontology.L2_Core, world)

    # Creates lane instance
    lane = l1_core.Lane()
    lane.identifier = str(parent_identifier) + "_" + str(identifier)
    for scene in scenes:
        scene.has_traffic_entity.append(lane)

    # Stores geometrical properties
    poly_left = cls.border_left.value.polyline
    poly_right = cls.border_right.value.polyline
    wkt_string = "POLYGON (("
    for i in range(len(poly_left.pos_x)):
        wkt_string += str(poly_left.pos_x[i]) + " " + str(poly_left.pos_y[i]) + " " + str(poly_left.pos_z[i]) + ", "
    for i in reversed(range(len(poly_right.pos_x))):
        wkt_string += str(poly_right.pos_x[i]) + " " + str(poly_right.pos_y[i]) + " " + str(poly_right.pos_z[i]) + ", "
    wkt_string += str(poly_left.pos_x[0]) + " " + str(poly_left.pos_y[0]) + " " + str(poly_left.pos_z[0]) + "))"
    geom = wkt.loads(wkt_string)
    lane_geometry = geo.Geometry()
    lane_geometry.asWKT = [str(geom)]
    lane.hasGeometry = [lane_geometry]

    # Stores lane type
    if cls.type == omega_format.ReferenceTypes.LaneType.BUS_LANE:
        lane.is_a.append(l1_de.Bus_Lane)
    elif cls.type == omega_format.ReferenceTypes.LaneType.BICYCLE_LANE:
        lane.is_a.append(l1_de.Bicycle_Lane)
    elif cls.type == omega_format.ReferenceTypes.LaneType.CARPOOL_LANE:
        lane.is_a.append(l1_de.Carpool_Lane)
    elif cls.type == omega_format.ReferenceTypes.LaneType.RAIL:
        lane.is_a.append(l1_de.Tram_Lane)
    elif cls.type == omega_format.ReferenceTypes.LaneType.BUS_BAY:
        lane.is_a.append(l1_de.Bus_Bay)
    elif cls.type == omega_format.ReferenceTypes.LaneType.BUS_BICYCLE_LANE:
        lane.is_a.append(l1_de.Bus_Lane)
        lane.is_a.append(l1_de.Bicycle_Lane)
    elif cls.type == omega_format.ReferenceTypes.LaneType.DRIVING:
        lane.is_a.append(l1_core.Driveable_Lane)
    elif cls.type == omega_format.ReferenceTypes.LaneType.KEEPOUT:
        lane.is_a.append(l1_de.Closed_Lane)
    elif cls.type == omega_format.ReferenceTypes.LaneType.OFF_RAMP:
        lane.is_a.append(l1_de.Deceleration_Lane)
    elif cls.type == omega_format.ReferenceTypes.LaneType.ON_RAMP:
        lane.is_a.append(l1_de.Acceleration_Lane)
    elif cls.type == omega_format.ReferenceTypes.LaneType.SHARED_WALKWAY:
        lane.is_a.append(l1_de.Walkway_Lane)
        lane.is_a.append(l1_de.Bikeway_Lane)
    elif cls.type == omega_format.ReferenceTypes.LaneType.SHOULDER:
        lane.is_a.append(l1_de.Shoulder)
    elif cls.type == omega_format.ReferenceTypes.LaneType.VEGETATION:
        lane.is_a.append(l1_de.Divider_Lane)
        veg = l2_core.Vegetation()
        veg.sfWithin.append(lane)
    elif cls.type == omega_format.ReferenceTypes.LaneType.VEHICLE_TURNOUT:
        lane.is_a.append(l1_de.Emergency_Bay)
    elif cls.type == omega_format.ReferenceTypes.LaneType.WALKWAY:
        lane.is_a.append(l1_de.Walkway_Lane)

    # Stores surface
    if cls.surface == omega_format.ReferenceTypes.SurfaceMaterial.ASPHALT:
        material = l1_de.Asphalt()
        lane.has_lane_material.append(material)
    elif cls.surface == omega_format.ReferenceTypes.SurfaceMaterial.CONCRETE:
        material = l1_de.Concrete()
        lane.has_lane_material.append(material)
    elif cls.surface == omega_format.ReferenceTypes.SurfaceMaterial.BRICK:
        material = l1_de.Cobblestone()
        lane.has_lane_material.append(material)
    elif cls.surface == omega_format.ReferenceTypes.SurfaceMaterial.GRAVEL:
        material = l1_de.Gravel()
        lane.has_lane_material.append(material)

    # Junction information
    if cls.classification == omega_format.ReferenceTypes.LaneClass.INTERSECTION:
        lane.is_a.append(l1_de.Intersection_Driveable_Lane)
    elif cls.classification == omega_format.ReferenceTypes.LaneClass.ROUNDABOUT:
        lane.is_a.append(l1_de.Roundabout_Driveable_Lane)

    # Add flat markers
    instances = []
    for i, marker in enumerate(cls.flat_markings.data.values()):
        marker_inst = marker.to_auto(world, scenes, i, lane.identifier[0])
        marker_inst[0][1][0].applies_to.append(lane)
        instances += marker_inst

    # Add boundaries
    for i, boundary in enumerate(cls.boundaries.data.values()):
        boundary_inst = boundary.to_auto(world, scenes, cls, i, lane.identifier[0])
        if len(boundary_inst[0][1]) > 0:
            boundary_inst[0][1][0].applies_to.append(lane)
            instances += boundary_inst

    # Add lane predecessor and successors
    for pred in cls.predecessors.data.values():
        add_relation(lane, "has_predecessor_lane", pred)
    for succ in cls.successors.data.values():
        add_relation(lane, "has_successor_lane", succ)

    add_layer_3_information(cls, lane, world)

    return [(cls, [lane])] + instances
