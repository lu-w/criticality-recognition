from ..utils import *


@monkeypatch(omega_format.RoadObject)
def to_auto(cls, world: owlready2.World, scenes, identifier=None, parent_identifier=None):

    # Fetches ontologies
    ph = auto.get_ontology(auto.Ontology.Physics, world)
    l1_core = auto.get_ontology(auto.Ontology.L1_Core, world)
    l1_de = auto.get_ontology(auto.Ontology.L1_DE, world)
    l2_de = auto.get_ontology(auto.Ontology.L2_DE, world)
    l5_de = auto.get_ontology(auto.Ontology.L5_DE, world)

    # Creates road object instance
    road_object = ph.Spatial_Object()
    road_object.identifier = str(parent_identifier) + "_" + str(identifier)
    for scene in scenes:
        scene.has_traffic_entity.append(road_object)

    if cls.type == omega_format.ReferenceTypes.RoadObjectType.STREET_LAMP:
        road_object.is_a.append(l2_de.Street_Light)
    elif cls.type == omega_format.ReferenceTypes.RoadObjectType.TRAFFIC_ISLAND:
        road_object.is_a.append(l1_de.Traffic_Island)
    elif cls.type == omega_format.ReferenceTypes.RoadObjectType.ROUNDABOUT_CENTER:
        road_object.is_a.append(l1_de.Roundabout_Center)
    elif cls.type == omega_format.ReferenceTypes.RoadObjectType.PARKING:
        road_object.is_a.append(l2_de.Parking_Space)
    elif cls.type == omega_format.ReferenceTypes.RoadObjectType.CROSSING_AID:
        road_object.is_a.append(l1_de.Traffic_Island)
    elif cls.type == omega_format.ReferenceTypes.RoadObjectType.SPEED_BUMP:
        road_object.is_a.append(l1_de.Speed_Bump)
    elif cls.type == omega_format.ReferenceTypes.RoadObjectType.POT_HOLE:
        road_object.is_a.append(l1_de.Pothole)
    elif cls.type == omega_format.ReferenceTypes.RoadObjectType.REFLECTOR:
        road_object.is_a.append(l1_de.Reflecting_Guidance_System)
    elif cls.type == omega_format.ReferenceTypes.RoadObjectType.STUD:
        road_object.is_a.append(l1_de.Raised_Pavement_Marker)
    elif cls.type == omega_format.ReferenceTypes.RoadObjectType.BOLLARD:
        road_object.is_a.append(l2_de.Bollard)
    elif cls.type == omega_format.ReferenceTypes.RoadObjectType.CRASH_ABSORBER:
        road_object.is_a.append(l2_de.Impact_Attenuator)
    elif cls.type == omega_format.ReferenceTypes.RoadObjectType.BITUMEN:
        road_object.is_a.append(l1_de.Bitumen_Repair)
    elif cls.type == omega_format.ReferenceTypes.RoadObjectType.MANHOLE_COVER:
        road_object.is_a.append(l1_de.Manhole_Cover)
    elif cls.type == omega_format.ReferenceTypes.RoadObjectType.GRATING:
        road_object.is_a.append(l1_de.Grating)
    elif cls.type == omega_format.ReferenceTypes.RoadObjectType.RUT:
        road_object.is_a.append(l1_de.Rut)
    elif cls.type == omega_format.ReferenceTypes.RoadObjectType.PUDDLE:
        road_object.is_a.append(l5_de.Rain_Puddle)

    if cls.walkable:
        road_object.is_a.append(l1_core.Walkable_Road_Element)
    else:
        road_object.is_a.append(l1_core.Non_Walkable_Road_Element)

    if cls.drivable:
        road_object.is_a.append(l1_core.Driveable_Road_Element)
    else:
        road_object.is_a.append(l1_core.Non_Driveable_Road_Element)

    road_object.has_height = float(cls.height)
    add_geometry_from_polygon(cls, road_object, world)

    add_layer_3_information(cls, road_object, world)

    return [(cls, [road_object])]
