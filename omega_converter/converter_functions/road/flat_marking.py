from ..utils import *


@monkeypatch(omega_format.FlatMarking)
def to_auto(cls, world: owlready2.World, scenes, identifier=None, parent_identifier=None):

    # Fetches ontologies
    ph = auto.get_ontology(auto.Ontology.Physics, world)
    geo = auto.get_ontology(auto.Ontology.GeoSPARQL, world)
    l1_core = auto.get_ontology(auto.Ontology.L1_Core, world)
    l1_de = auto.get_ontology(auto.Ontology.L1_DE, world)

    # Creates marking instance
    marker = l1_core.Road_Marker()
    marker.identifier = str(parent_identifier) + "_" + str(identifier)
    for scene in scenes:
        scene.has_traffic_entity.append(marker)

    # Stores value (digits) as lettering
    if cls.value > 0:
        marker.has_lettering = str(cls.value)

    # Stores geometry (can only be 1 or 2 points according to OMEGA specification)
    if 0 < len(cls.polyline.pos_x) < 3:
        if len(cls.polyline.pos_x) == 1:
            wkt_string = "POINT ( " + str(cls.polyline.pos_x[0]) + " " + str(cls.polyline.pos_y[0]) + " " + \
                         str(cls.polyline.pos_z[0]) + ")"
        elif len(cls.polyline.pos_x) == 2:
            wkt_string = "LINESTRING ( " + str(cls.polyline.pos_x[0]) + " " + str(cls.polyline.pos_y[0]) + " " + \
                         str(cls.polyline.pos_z[0]) + ", " + str(cls.polyline.pos_x[1]) + " " + \
                         str(cls.polyline.pos_y[1]) + " " + str(cls.polyline.pos_z[1]) + " )"
        geom = wkt.loads(wkt_string)
        marker_geom = geo.Geometry()
        marker_geom.asWKT = [str(geom)]
        marker.hasGeometry = [marker_geom]

    # Stores marker color
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

    # Stores marker condition
    if cls.condition == omega_format.ReferenceTypes.FlatMarkingCondition.FINE:
        marker.has_degradation_degree = 0
    elif cls.condition == omega_format.ReferenceTypes.FlatMarkingCondition.CORRUPTED_1_OLD_VISIBIBLE:
        marker.has_degradation_degree = 25
    elif cls.condition == omega_format.ReferenceTypes.FlatMarkingCondition.CORRUPTED_2_FADED:
        marker.has_degradation_degree = 75

    # Stores marker type
    if cls.type == omega_format.ReferenceTypes.FlatMarkingType.NOTICE_ARROW:
        marker.is_a.append(l1_de.Indicational_Arrow)
    elif cls.type == omega_format.ReferenceTypes.FlatMarkingType.ZIG_ZAG:
        marker.is_a.append(l1_de.Boundary_Marker_For_Parking_Zone)
    elif cls.type == omega_format.ReferenceTypes.FlatMarkingType.KEEPOUT_AREA:
        marker.is_a.append(l1_de.Keepout_Arial_Road_Marker)
    elif cls.type == omega_format.ReferenceTypes.FlatMarkingType.ARROW_LEFT:
        marker.is_a.append(l1_de.Directional_Arrow_Left)
    elif cls.type == omega_format.ReferenceTypes.FlatMarkingType.ARROW_RIGHT:
        marker.is_a.append(l1_de.Directional_Arrow_Right)
    elif cls.type == omega_format.ReferenceTypes.FlatMarkingType.ARROW_LEFT_RIGHT:
        marker.is_a.append(l1_de.Directional_Arrow_Left_Right)
    elif cls.type == omega_format.ReferenceTypes.FlatMarkingType.ARROW_LEFT_STRAIGHT:
        marker.is_a.append(l1_de.Directional_Arrow_Straight_Left)
    elif cls.type == omega_format.ReferenceTypes.FlatMarkingType.ARROW_RIGHT_STRAIGHT:
        marker.is_a.append(l1_de.Directional_Arrow_Straight_Right)
    elif cls.type == omega_format.ReferenceTypes.FlatMarkingType.ARROW_LEFT_STRAIGHT_RIGHT:
        marker.is_a.append(l1_de.Directional_Arrow_Straight_Left_Right)
    elif cls.type == omega_format.ReferenceTypes.FlatMarkingType.ARROW_STRAIGHT:
        marker.is_a.append(l1_de.Directional_Arrow_Straight)
    elif cls.type == omega_format.ReferenceTypes.FlatMarkingType.VEHICLEFRONT:
        marker.is_a.append(l1_de.Road_Marker_Vehicle_Front)
    elif cls.type == omega_format.ReferenceTypes.FlatMarkingType.TRUCK:
        marker.is_a.append(l1_de.Road_Marker_Truck)
    elif cls.type == omega_format.ReferenceTypes.FlatMarkingType.BICYCLE:
        marker.is_a.append(l1_de.Road_Marker_Bicycle)
    elif cls.type == omega_format.ReferenceTypes.FlatMarkingType.DELIVERYBIKE:
        marker.is_a.append(l1_de.Road_Marker_Delivery_Bike)
    elif cls.type == omega_format.ReferenceTypes.FlatMarkingType.PEDESTRIAN:
        marker.is_a.append(l1_de.Road_Marker_Pedestrian)
    elif cls.type == omega_format.ReferenceTypes.FlatMarkingType.HORSERIDER:
        marker.is_a.append(l1_de.Road_Marker_Horse_Rider)
    elif cls.type == omega_format.ReferenceTypes.FlatMarkingType.CATTLEDRIVE:
        marker.is_a.append(l1_de.Road_Marker_Cattle_Drive)
    elif cls.type == omega_format.ReferenceTypes.FlatMarkingType.TRAM:
        marker.is_a.append(l1_de.Road_Marker_Tram)
    elif cls.type == omega_format.ReferenceTypes.FlatMarkingType.BUS:
        marker.is_a.append(l1_de.Road_Marker_Bus)
    elif cls.type == omega_format.ReferenceTypes.FlatMarkingType.VEHICLE:
        marker.is_a.append(l1_de.Road_Marker_Vehicle)
    elif cls.type == omega_format.ReferenceTypes.FlatMarkingType.VEHICLEMULTIPLEPASSENGERS:
        marker.is_a.append(l1_de.Road_Marker_Vehicle_Multiple_Passengers)
    elif cls.type == omega_format.ReferenceTypes.FlatMarkingType.PKWWITHTRAILER:
        marker.is_a.append(l1_de.Road_Marker_Vehicle_With_Trailer)
    elif cls.type == omega_format.ReferenceTypes.FlatMarkingType.TRUCKWITHTRAILER:
        marker.is_a.append(l1_de.Road_Marker_Truck_With_Trailer)
    elif cls.type == omega_format.ReferenceTypes.FlatMarkingType.MOBILEHOME:
        marker.is_a.append(l1_de.Road_Marker_Mobile_Home)
    elif cls.type == omega_format.ReferenceTypes.FlatMarkingType.TRACTOR:
        marker.is_a.append(l1_de.Road_Marker_Tractor)
    elif cls.type == omega_format.ReferenceTypes.FlatMarkingType.MOTORCYCLE:
        marker.is_a.append(l1_de.Road_Marker_Motorcycle)
    elif cls.type == omega_format.ReferenceTypes.FlatMarkingType.MOPED:
        marker.is_a.append(l1_de.Road_Marker_Moped)
    elif cls.type == omega_format.ReferenceTypes.FlatMarkingType.ELECTRICBICYCLE:
        marker.is_a.append(l1_de.Road_Marker_Electric_Bicycle)
    elif cls.type == omega_format.ReferenceTypes.FlatMarkingType.ESCOOTER:
        marker.is_a.append(l1_de.Road_Marker_E_Scooter)
    elif cls.type == omega_format.ReferenceTypes.FlatMarkingType.CARRIAGE:
        marker.is_a.append(l1_de.Road_Marker_Carriage)
    elif cls.type == omega_format.ReferenceTypes.FlatMarkingType.SNOWICE:
        marker.is_a.append(l1_de.Road_Marker_Snow_Ice)
    elif cls.type == omega_format.ReferenceTypes.FlatMarkingType.ROCKFALL:
        marker.is_a.append(l1_de.Road_Marker_Rockfall)
    elif cls.type == omega_format.ReferenceTypes.FlatMarkingType.GRAVEL:
        marker.is_a.append(l1_de.Road_Marker_Gravel)
    elif cls.type == omega_format.ReferenceTypes.FlatMarkingType.MOVABLEBRIDGE:
        marker.is_a.append(l1_de.Road_Marker_Movable_Bridge)
    elif cls.type == omega_format.ReferenceTypes.FlatMarkingType.SHORE:
        marker.is_a.append(l1_de.Road_Marker_Shore)
    elif cls.type == omega_format.ReferenceTypes.FlatMarkingType.CROSSWALK:
        marker.is_a.append(l1_de.Road_Marker_Crosswalk)
    elif cls.type == omega_format.ReferenceTypes.FlatMarkingType.AMPHIBIAN:
        marker.is_a.append(l1_de.Road_Marker_Amphibian)
    elif cls.type == omega_format.ReferenceTypes.FlatMarkingType.AVENUE:
        marker.is_a.append(l1_de.Road_Marker_Avenue)
    elif cls.type == omega_format.ReferenceTypes.FlatMarkingType.PLAIN:
        marker.is_a.append(l1_de.Road_Marker_Plain)
    elif cls.type == omega_format.ReferenceTypes.FlatMarkingType.ELECTRICALVEHICLE:
        marker.is_a.append(l1_de.Road_Marker_Electrical_Vehicle)
    elif cls.type == omega_format.ReferenceTypes.FlatMarkingType.CARSHARING:
        marker.is_a.append(l1_de.Road_Marker_Carsharing)

    add_layer_3_information(cls, marker, world)

    return [(cls, [marker])]
