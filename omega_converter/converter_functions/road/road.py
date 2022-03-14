from ..utils import *


@monkeypatch(omega_format.Road)
def to_auto(cls, world: owlready2.World, scenes, identifier=None):

    # Fetches ontologies
    geo = auto.get_ontology(auto.Ontology.GeoSPARQL, world)
    l1_core = auto.get_ontology(auto.Ontology.L1_Core, world)
    l1_de = auto.get_ontology(auto.Ontology.L1_DE, world)

    # Creates road instance
    road = l1_core.Road()
    road.identifier = identifier
    parent_id = "road" + str(identifier)
    for scene in scenes:
        scene.has_traffic_entity.append(road)

    # Stores road type
    if cls.location == omega_format.ReferenceTypes.RoadLocation.URBAN:
        road.is_a.append(l1_de.Urban_Road)
    elif cls.location == omega_format.ReferenceTypes.RoadLocation.NON_URBAN:
        road.is_a.append(l1_de.Rural_Road)
    elif cls.location == omega_format.ReferenceTypes.RoadLocation.HIGHWAY:
        road.is_a.append(l1_de.Highway_Road)

    # Creates lane instances
    wkt_string = "MULTIPOLYGON ("
    instances = []
    lane_instances = []
    for i, lane in enumerate(cls.lanes.values()):
        lane_insts = lane.to_auto(world, scenes, i, parent_id)
        instances += lane_insts
        lane_inst = lane_insts[0][1][0]
        lane_instances.append((lane, [lane_inst]))
        road.has_lane.append(lane_inst)
        lane_inst.has_road = road
        wkt_string += lane_inst.hasGeometry[0].asWKT[0].replace("POLYGON ", "") + ", "
        road.has_road_material += lane_inst.has_lane_material

    # Sets predecessor and successor relations of lanes
    for rr_inst, lane_inst in lane_instances:
        for rr_inst_1, lane_inst_1 in lane_instances:
            if rr_inst_1 in rr_inst.successors.data.values():
                lane_inst[0].has_successor_lane.append(lane_inst_1[0])
            if rr_inst_1 in rr_inst.predecessors.data.values():
                lane_inst[0].has_predecessor_lane.append(lane_inst_1[0])

    # Stores geometry of road as conjunction of lane polygons
    wkt_string = wkt_string[:-2] + "))"
    geom = wkt.loads(wkt_string)
    # Fix invalid roads (multipolygon may intersect itself due to taking the union of all lanes)
    if not geom.is_valid:
        geom = geom.buffer(0)
    road_geometry = geo.Geometry()
    road_geometry.asWKT = [str(geom)]
    road.hasGeometry = [road_geometry]

    # Add lateral markers
    for i, marker in enumerate(cls.lateral_markings.data.values()):
        marker_inst = marker.to_auto(world, scenes, i, parent_id)
        marker_inst[0][1][0].applies_to.append(road)
        instances += marker_inst

    # Add structural objects
    for i, structural_object in enumerate(cls.structural_objects.data.values()):
        struct_inst = structural_object.to_auto(world, scenes, i, parent_id)
        instances += struct_inst

    # Add road objects
    for i, road_object in enumerate(cls.road_objects.data.values()):
        obj_inst = road_object.to_auto(world, scenes, i, parent_id)
        instances += obj_inst

    # Add signs
    for i, sign in enumerate(cls.signs.data.values()):
        sign_inst = sign.to_auto(world, scenes, i, parent_id)
        instances += sign_inst

    instances.append((cls, [road]))
    return instances
