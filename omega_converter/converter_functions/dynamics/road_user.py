import auto.auto
from ..utils import *


@monkeypatch(omega_format.RoadUser)
def to_auto(cls, world: owlready2.World, scene, identifier=None):
    s = scene.inTimePosition[1].numericPosition[0] - cls.birth

    # Fetches ontologies
    ac = auto.get_ontology(auto.Ontology.Act, world)
    pe = auto.get_ontology(auto.Ontology.Perception, world)
    ph = auto.get_ontology(auto.Ontology.Physics, world)
    geo = auto.get_ontology(auto.Ontology.GeoSPARQL, world)
    l4_core = auto.get_ontology(auto.Ontology.L4_Core, world)
    l4_de = auto.get_ontology(auto.Ontology.L4_DE, world)

    # Creates road user instance
    if cls.sub_type == omega_format.ReferenceTypes.RoadUserSubTypeMOTORCYCLE.WITHOUT_RIDER or \
            cls.sub_type == omega_format.ReferenceTypes.RoadUserSubTypeBICYCLE.WITHOUT_RIDER or \
            cls.sub_type == omega_format.ReferenceTypes.RoadUserSubTypeWHEELCHAIR.WITHOUT_RIDER or \
            cls.sub_type == omega_format.ReferenceTypes.RoadUserSubTypePERSONAL_MOBILITY_DEVICE.WITHOUT_RIDER:
        ru = l4_core.Traffic_Object()
        traffic_object = True
    else:
        ru = l4_core.Human()
        ru.is_a.append(pe.Observer)
        traffic_object = False
    scene.has_traffic_entity.append(ru)
    ru.in_scene.append(scene)

    # Stores road user type
    if cls.type == omega_format.ReferenceTypes.RoadUserType.PEDESTRIAN:
        ru.is_a.append(l4_core.Pedestrian)
        if cls.sub_type == omega_format.ReferenceTypes.RoadUserSubTypePEDESTRIAN.CHILD:
            ru.is_a.append(l4_de.Child)
        elif cls.sub_type == omega_format.ReferenceTypes.RoadUserSubTypePEDESTRIAN.ADULT:
            ru.is_a.append(l4_de.Adult)
    elif cls.type == omega_format.ReferenceTypes.RoadUserType.REGULAR:
        ru.is_a.append(l4_core.Traffic_Subject)
    if len(ru.is_a) > 0 and cls.type == omega_format.ReferenceTypes.RoadUserSubTypeGeneral.CONSTRUCTION:
        ru.is_a.append(l4_de.Road_Worker)

    # Creates vehicle, if given
    drives_something = True
    is_a = []
    if cls.type == omega_format.ReferenceTypes.RoadUserType.CAR:
        is_a = l4_de.Passenger_Car
    elif cls.type == omega_format.ReferenceTypes.RoadUserType.TRUCK:
        is_a = l4_de.Truck
        if cls.sub_type == omega_format.ReferenceTypes.RoadUserSubTypeTRUCK.STREET_CLEANING:
            is_a.append(l4_de.Street_Cleaning_Truck)
    elif cls.type == omega_format.ReferenceTypes.RoadUserType.BUS:
        is_a = l4_de.Bus
        if cls.sub_type == omega_format.ReferenceTypes.RoadUserSubTypeBUS.BENDY_BUS:
            is_a.append(l4_de.Bendy_Bus)
        elif cls.sub_type == omega_format.ReferenceTypes.RoadUserSubTypeBUS.TROLLEY_BUS:
            is_a.append(l4_de.Trolleybus)
    elif cls.type == omega_format.ReferenceTypes.RoadUserType.MOTORCYCLE:
        is_a = l4_de.Motorcycle
    elif cls.type == omega_format.ReferenceTypes.RoadUserType.BICYCLE:
        is_a = l4_de.Bicycle
    elif cls.type == omega_format.ReferenceTypes.RoadUserType.WHEELCHAIR:
        is_a = l4_de.Wheelchair
    elif cls.type == omega_format.ReferenceTypes.RoadUserType.PERSONAL_MOBILITY_DEVICE:
        is_a = l4_de.Personal_Mobility_Device
    elif cls.type == omega_format.ReferenceTypes.RoadUserType.TRAILER:
        is_a = l4_de.Trailer
        if cls.sub_type == omega_format.ReferenceTypes.RoadUserSubTypeTRAILER.CAR_TRAILER:
            is_a.append(l4_de.Passenger_Vehicle_Trailer)
        elif cls.sub_type == omega_format.ReferenceTypes.RoadUserSubTypeTRAILER.CARAVAN:
            is_a.append(l4_de.Caravan)
        elif cls.sub_type == omega_format.ReferenceTypes.RoadUserSubTypeTRAILER.TRUCK_TRAILER:
            is_a.append(l4_de.Truck_Trailer)
        elif cls.sub_type == omega_format.ReferenceTypes.RoadUserSubTypeTRAILER.TRAIN_TRAILER:
            is_a.append(l4_de.Train_Trailer)
        elif cls.sub_type == omega_format.ReferenceTypes.RoadUserSubTypeTRAILER.BENDY_BUS_TRAILER:
            is_a.append(l4_de.Bendy_Bus_Trailer)
    elif cls.type == omega_format.ReferenceTypes.RoadUserType.FARMING:
        is_a = l4_de.Farming_Vehicle
    elif cls.type == omega_format.ReferenceTypes.RoadUserType.RAIL:
        is_a = l4_de.Rail_Vehicle
    elif cls.type == omega_format.ReferenceTypes.RoadUserType.CARRIAGE:
        is_a = l4_de.Carriage
    else:
        drives_something = False
    # Sub types
    if cls.sub_type == omega_format.ReferenceTypes.RoadUserSubTypeGeneral.EMERGENCY:
        is_a.append(l4_de.Emergency_Vehicle)
    if cls.sub_type == omega_format.ReferenceTypes.RoadUserSubTypeGeneral.CONSTRUCTION:
        is_a.append(l4_de.Construction_Vehicle)

    # Decide which individual is the physical representation (driven objects vs. non-driven objects)
    if drives_something and not traffic_object:
        veh = l4_core.Vehicle()
        veh.is_a.append(is_a)
        scene.has_traffic_entity.append(veh)
        ru.drives = [veh]
        phys_repr = veh
        # Vehicle will get its own geometrical properties later, store those for the driver now.
        ru_geometry = geo.Geometry()
        ru_geometry.asWKT = [geometry.Point(cls.tr.pos_x[s], cls.tr.pos_y[s], cls.tr.pos_z[s]).wkt]
        ru.hasGeometry = [ru_geometry]
    else:
        # If no vehicle is given, the road itself is the physical representation (e.g. a pedestrian).
        phys_repr = ru

    if cls.connected_to:
        add_relation(phys_repr, "connected_to", cls.connected_to, scene)

    # Store physical properties
    add_physical_properties(cls, phys_repr, s)
    # Store bounding box
    add_bounding_box(cls, phys_repr)
    # Store geometrical properties
    add_geometry_from_trajectory(cls, phys_repr, s, world)

    # Store vehicle lights
    if cls.vehicle_lights.indicator_right[s] != -1:
        light = l4_de.Indicator_Light_Right()
        if cls.vehicle_lights.indicator_right[s] == 0:
            light.is_a.append(ph.Inactive_Lamp)
        elif cls.vehicle_lights.indicator_right[s] == 1:
            light.is_a.append(ph.Active_Lamp)
        phys_repr.has_part.append(light)
    if cls.vehicle_lights.indicator_left[s] != -1:
        light = l4_de.Indicator_Light_Left()
        if cls.vehicle_lights.indicator_left[s] == 0:
            light.is_a.append(ph.Inactive_Lamp)
        elif cls.vehicle_lights.indicator_left[s] == 1:
            light.is_a.append(ph.Active_Lamp)
        phys_repr.has_part.append(light)
    if cls.vehicle_lights.brake_lights[s] != -1:
        light = l4_de.Brake_Light()
        if cls.vehicle_lights.brake_lights[s] == 0:
            light.is_a.append(ph.Inactive_Lamp)
        elif cls.vehicle_lights.brake_lights[s] == 1:
            light.is_a.append(ph.Active_Lamp)
        phys_repr.has_part.append(light)
    if cls.vehicle_lights.headlights[s] != -1:
        light = l4_de.Headlight()
        if cls.vehicle_lights.headlights[s] == 0:
            light.is_a.append(ph.Inactive_Lamp)
        elif cls.vehicle_lights.headlights[s] == 1:
            light.is_a.append(ph.Active_Lamp)
        phys_repr.has_part.append(light)
    if cls.vehicle_lights.reverseing_lights[s] != -1:
        light = l4_de.Reversing_Light()
        if cls.vehicle_lights.reverseing_lights[s] == 0:
            light.is_a.append(ph.Inactive_Lamp)
        elif cls.vehicle_lights.reverseing_lights[s] == 1:
            light.is_a.append(ph.Active_Lamp)
        phys_repr.has_part.append(light)
    if cls.vehicle_lights.blue_light[s] != -1:
        light = l4_de.Emergency_Light()
        if cls.vehicle_lights.blue_light[s] == 0:
            light.is_a.append(ph.Inactive_Lamp)
        elif cls.vehicle_lights.blue_light[s] == 1:
            light.is_a.append(ph.Active_Lamp)
        phys_repr.has_part.append(light)
    ru.identifier = identifier
    # TODO debug, remove
    if len(ru.drives) > 0 and len(ru.drives[0].hasGeometry) == 0:
        raise ValueError("Found RU that drives smth but the vehicle has no geom: " + str(ru) + " - " + str(ru.drives))
    # Map RR instance to one or two OWL individuals
    if phys_repr is ru:
        return [(cls, [ru])]
    else:
        phys_repr.identifier = "repr" + str(identifier)
        return [(cls, [ru, phys_repr])]
