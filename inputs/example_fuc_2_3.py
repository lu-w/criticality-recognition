# Represents Functional Use Case 2.3 within A.U.T.O.

import logging

import owlready2
from shapely import geometry

from auto import auto

# Logging
logger = logging.getLogger(__name__)


def get_fuc23_worlds():

    #################
    # Load A.U.T.O. #
    #################
    logger.info("Loading A.U.T.O.")

    # Create FUC 2.3 world and load A.U.T.O.
    fuc_2_3_world_1 = owlready2.World()
    fuc_2_3_world_2 = owlready2.World()
    fuc_2_3_world_3 = owlready2.World()
    auto.load_cp(folder="auto/ontology", world=fuc_2_3_world_1)
    auto.load_cp(folder="auto/ontology", world=fuc_2_3_world_2)
    auto.load_cp(folder="auto/ontology", world=fuc_2_3_world_3)

    # Shorthands
    cp_1 = auto.get_ontology(auto.Ontology.Criticality_Phenomena_Formalization, fuc_2_3_world_1)
    tm_1 = auto.get_ontology(auto.Ontology.Traffic_Model, fuc_2_3_world_1)
    ph_1 = auto.get_ontology(auto.Ontology.Physics, fuc_2_3_world_1)
    pe_1 = auto.get_ontology(auto.Ontology.Perception, fuc_2_3_world_1)
    ti_1 = auto.get_ontology(auto.Ontology.Time, fuc_2_3_world_1)
    ac_1 = auto.get_ontology(auto.Ontology.Act, fuc_2_3_world_1)
    ge_1 = auto.get_ontology(auto.Ontology.GeoSPARQL, fuc_2_3_world_1)
    l4_core_1 = auto.get_ontology(auto.Ontology.L4_Core, fuc_2_3_world_1)
    l4_de_1 = auto.get_ontology(auto.Ontology.L4_DE, fuc_2_3_world_1)
    l1_core_1 = auto.get_ontology(auto.Ontology.L1_Core, fuc_2_3_world_1)
    l1_de_1 = auto.get_ontology(auto.Ontology.L1_DE, fuc_2_3_world_1)
    cp_2 = auto.get_ontology(auto.Ontology.Criticality_Phenomena_Formalization, fuc_2_3_world_2)
    tm_2 = auto.get_ontology(auto.Ontology.Traffic_Model, fuc_2_3_world_2)
    ph_2 = auto.get_ontology(auto.Ontology.Physics, fuc_2_3_world_2)
    pe_2 = auto.get_ontology(auto.Ontology.Perception, fuc_2_3_world_2)
    ti_2 = auto.get_ontology(auto.Ontology.Time, fuc_2_3_world_2)
    ac_2 = auto.get_ontology(auto.Ontology.Act, fuc_2_3_world_2)
    ge_2 = auto.get_ontology(auto.Ontology.GeoSPARQL, fuc_2_3_world_2)
    l4_core_2 = auto.get_ontology(auto.Ontology.L4_Core, fuc_2_3_world_2)
    l4_de_2 = auto.get_ontology(auto.Ontology.L4_DE, fuc_2_3_world_2)
    l1_core_2 = auto.get_ontology(auto.Ontology.L1_Core, fuc_2_3_world_2)
    l1_de_2 = auto.get_ontology(auto.Ontology.L1_DE, fuc_2_3_world_2)
    cp_3 = auto.get_ontology(auto.Ontology.Criticality_Phenomena_Formalization, fuc_2_3_world_3)
    tm_3 = auto.get_ontology(auto.Ontology.Traffic_Model, fuc_2_3_world_3)
    ph_3 = auto.get_ontology(auto.Ontology.Physics, fuc_2_3_world_3)
    pe_3 = auto.get_ontology(auto.Ontology.Perception, fuc_2_3_world_3)
    ti_3 = auto.get_ontology(auto.Ontology.Time, fuc_2_3_world_3)
    ac_3 = auto.get_ontology(auto.Ontology.Act, fuc_2_3_world_3)
    ge_3 = auto.get_ontology(auto.Ontology.GeoSPARQL, fuc_2_3_world_3)
    l4_core_3 = auto.get_ontology(auto.Ontology.L4_Core, fuc_2_3_world_3)
    l4_de_3 = auto.get_ontology(auto.Ontology.L4_DE, fuc_2_3_world_3)
    l1_core_3 = auto.get_ontology(auto.Ontology.L1_Core, fuc_2_3_world_3)
    l1_de_3 = auto.get_ontology(auto.Ontology.L1_DE, fuc_2_3_world_3)

    #############################################
    # Populate scenario as specified in FUC 2.3 #
    #############################################
    logger.info("Populating Functional Use Case 2.3")

    ##################
    # Create scene 1 #
    ##################
    scene_1 = tm_1.Scene()
    time_1 = ti_1.TimePosition()
    time_1.numericPosition = [0]
    scene_1.inTimePosition.append(time_1)

    # Create traffic infrastructure
    # Western road
    road_west_1 = l1_de_1.Urban_Road()
    road_west_geometry_1 = ge_1.Geometry()
    road_west_geometry_1.asWKT = [geometry.Polygon([(0, 26), (42, 26), (42, 20), (0, 20), (0, 26)]).wkt]
    road_west_1.hasGeometry = [road_west_geometry_1]
    road_west_1.is_persistent = True
    # Eastern road
    road_east_1 = l1_de_1.Urban_Road()
    road_east_geometry_1 = ge_1.Geometry()
    road_east_geometry_1.asWKT = [geometry.Polygon([(48, 26), (78, 26), (78, 20), (48, 20), (48, 26)]).wkt]
    road_east_1.hasGeometry = [road_east_geometry_1]
    road_east_1.is_persistent = True
    # Southern road
    road_south_1 = l1_de_1.Urban_Road()
    road_south_geometry_1 = ge_1.Geometry()
    road_south_geometry_1.asWKT = [geometry.Polygon([(40, 20), (48, 20), (48, 0), (40, 0), (40, 20)]).wkt]
    road_south_1.hasGeometry = [road_south_geometry_1]
    road_south_1.is_persistent = True
    # Western upper lane
    western_upper_lane_1 = l1_core_1.Driveable_Lane()
    western_upper_lane_geometry_1 = ge_1.Geometry()
    western_upper_lane_geometry_1.asWKT = [geometry.Polygon([(0, 26), (42, 26), (42, 23), (0, 23), (0, 26)]).wkt]
    western_upper_lane_1.hasGeometry = [western_upper_lane_geometry_1]
    western_upper_lane_1.is_persistent = True
    # Western lower lane
    western_lower_lane_1 = l1_core_1.Driveable_Lane()
    western_lower_lane_geometry_1 = ge_1.Geometry()
    western_lower_lane_geometry_1.asWKT = [geometry.Polygon([(0, 23), (42, 23), (42, 20), (0, 20), (0, 23)]).wkt]
    western_lower_lane_1.hasGeometry = [western_lower_lane_geometry_1]
    western_lower_lane_1.is_persistent = True
    # Eastern upper lane
    eastern_upper_lane_1 = l1_core_1.Driveable_Lane()
    eastern_upper_lane_geometry_1 = ge_1.Geometry()
    eastern_upper_lane_geometry_1.asWKT = [geometry.Polygon([(48, 26), (78, 26), (78, 23), (48, 23), (48, 26)]).wkt]
    eastern_upper_lane_1.hasGeometry = [eastern_upper_lane_geometry_1]
    eastern_upper_lane_1.is_persistent = True
    # Eastern lower lane
    eastern_lower_lane_1 = l1_core_1.Driveable_Lane()
    eastern_lower_lane_geometry_1 = ge_1.Geometry()
    eastern_lower_lane_geometry_1.asWKT = [geometry.Polygon([(48, 23), (78, 23), (78, 20), (48, 20), (48, 23)]).wkt]
    eastern_lower_lane_1.hasGeometry = [eastern_lower_lane_geometry_1]
    eastern_lower_lane_1.is_persistent = True
    # Southern left lane
    southern_left_lane_1 = l1_core_1.Driveable_Lane()
    southern_left_lane_geometry_1 = ge_1.Geometry()
    southern_left_lane_geometry_1.asWKT = [geometry.Polygon([(42, 20), (45, 20), (45, 0), (42, 0), (42, 20)]).wkt]
    southern_left_lane_1.hasGeometry = [southern_left_lane_geometry_1]
    southern_left_lane_1.is_persistent = True
    # Southern right lane
    southern_right_lane_1 = l1_core_1.Driveable_Lane()
    southern_right_lane_geometry_1 = ge_1.Geometry()
    southern_right_lane_geometry_1.asWKT = [geometry.Polygon([(45, 20), (48, 20), (48, 0), (45, 0), (45, 20)]).wkt]
    southern_right_lane_1.hasGeometry = [southern_right_lane_geometry_1]
    southern_right_lane_1.is_persistent = True
    # Bicycle lane on southern road
    bicycle_lane_1 = l1_de_1.Bikeway_Lane()
    bicycle_lane_1.has_road = road_south_1
    bicycle_lane_geometry_1 = ge_1.Geometry()
    bicycle_lane_geometry_1.asWKT = [geometry.Polygon([(40, 20), (42, 20), (42, 0), (40, 0), (40, 20)]).wkt]
    bicycle_lane_1.hasGeometry = [bicycle_lane_geometry_1]
    bicycle_lane_1.is_persistent = True
    # Pedestrian crossing on western road
    pedestrian_crossing_1 = l1_de_1.Pedestrian_Crossing()
    pedestrian_crossing_1.has_road = road_west_1
    pedestrian_crossing_geometry_1 = ge_1.Geometry()
    pedestrian_crossing_geometry_1.asWKT = [geometry.Polygon([(39, 26), (42, 26), (42, 20), (39, 20), (39, 26)]).wkt]
    pedestrian_crossing_1.hasGeometry = [pedestrian_crossing_geometry_1]
    pedestrian_crossing_1.is_persistent = True
    # Logical lane & road connections
    road_west_1.has_lane = [western_lower_lane_1, eastern_upper_lane_1, pedestrian_crossing_1]
    road_east_1.has_lane = [eastern_lower_lane_1, eastern_upper_lane_1]
    road_south_1.has_lane = [southern_left_lane_1, southern_right_lane_1, bicycle_lane_1]
    western_lower_lane_1.has_successor_lane = [eastern_lower_lane_1, southern_left_lane_1]
    southern_right_lane_1.has_successor_lane = [eastern_lower_lane_1, western_upper_lane_1]
    eastern_upper_lane_1.has_successor_lane = [western_upper_lane_1, southern_left_lane_1]
    pedestrian_crossing_1.has_predecessor_lane = [bicycle_lane_1]
    bicycle_lane_1.has_successor_lane = [pedestrian_crossing_1]
    # Crossing
    crossing_1 = l1_de_1.Crossing()
    crossing_1.connects = [road_west_1, road_east_1, road_south_1]
    crossing_geometry_1 = ge_1.Geometry()
    crossing_geometry_1.asWKT = [geometry.Polygon([(42, 26), (48, 26), (48, 20), (42, 20), (42, 26)]).wkt]
    crossing_1.hasGeometry = [crossing_geometry_1]
    crossing_1.is_persistent = True

    # Creates road users
    # Ego
    ego_t0 = l4_de_1.Passenger_Car()
    ego_t0.identifier = "Ego-Vehicle"
    ego_t0.has_height = 2
    ego_t0.has_velocity_x = 8
    ego_t0.has_velocity_y = 0
    ego_t0.has_velocity_z = 0
    ego_t0.has_acceleration_x = 0
    ego_t0.has_acceleration_y = 0
    ego_t0.has_acceleration_z = 0
    ego_t0.has_yaw = 0
    ego_t0_geometry = ge_1.Geometry()
    ego_t0_geometry.asWKT = [geometry.Polygon([(4, 23), (9, 23), (9, 21), (4, 21), (4, 23)]).wkt]
    ego_t0.hasGeometry = [ego_t0_geometry]
    ego_driver_t0 = l4_core_1.Automated_Driving_Function()
    ego_driver_t0.identifier = "Ego-ADF"
    ego_driver_t0.has_horizontal_field_of_view = 3.14
    ego_driver_t0.has_visibility_range = 200
    ego_driver_t0_geometry = ge_1.Geometry()
    ego_driver_t0_geometry.asWKT = [geometry.Point([6.5, 22]).wkt]
    ego_driver_t0.hasGeometry = [ego_driver_t0_geometry]
    ego_driver_t0.drives = [ego_t0]
    ego_t0.driven_by = [ego_driver_t0]
    # Bicyclist
    bicycle_t0 = l4_de_1.Bicycle()
    bicycle_t0.identifier = "Bicycle"
    bicycle_t0.has_height = 1.5
    bicycle_t0.has_velocity_x = 0
    bicycle_t0.has_velocity_y = 6
    bicycle_t0.has_velocity_z = 0
    bicycle_t0.has_acceleration_x = 0
    bicycle_t0.has_acceleration_y = 0
    bicycle_t0.has_acceleration_z = 0
    bicycle_t0.has_yaw = 90
    bicycle_t0_geometry = ge_1.Geometry()
    bicycle_t0_geometry.asWKT = [geometry.Polygon
                                 ([(40.6, 12.2), (41.2, 12.2), (41.2, 10.4), (40.6, 10.4), (40.6, 12.2)]).wkt]
    bicycle_t0.hasGeometry = [bicycle_t0_geometry]
    bicyclist_t0 = l4_de_1.Bicyclist()
    bicyclist_t0.identifier = "Bicyclist"
    bicyclist_t0.has_horizontal_field_of_view = 3.14
    bicyclist_t0.has_visibility_range = 200
    bicyclist_t0_geometry = ge_1.Geometry()
    bicyclist_t0_geometry.asWKT = [geometry.Point([40.9, 11.3]).wkt]
    bicyclist_t0.hasGeometry = [bicyclist_t0_geometry]
    bicyclist_t0.drives = [bicycle_t0]
    bicycle_t0.driven_by = [bicyclist_t0]
    # Parking vehicles
    parking_vehicle_1_t0 = l4_de_1.Parking_Vehicle()
    parking_vehicle_1_t0.identifier = "Parking-Vehicle-#1"
    parking_vehicle_1_t0.has_yaw = 0
    parking_vehicle_1_t0.has_height = 2
    parking_vehicle_1_t0.has_velocity_x = 0
    parking_vehicle_1_t0.has_velocity_y = 0
    parking_vehicle_1_t0.has_velocity_z = 0
    parking_vehicle_1_geometry_t0 = ge_1.Geometry()
    parking_vehicle_1_geometry_t0.asWKT = [geometry.Polygon([(29, 21.5), (34, 21.5), (34, 19.5), (29, 19.5), (29, 21.5)]
                                                            ).wkt]
    parking_vehicle_1_t0.hasGeometry = [parking_vehicle_1_geometry_t0]
    parking_vehicle_2_t0 = l4_de_1.Parking_Vehicle()
    parking_vehicle_2_t0.identifier = "Parking-Vehicle-#2"
    parking_vehicle_2_t0.has_yaw = 0
    parking_vehicle_2_t0.has_height = 2
    parking_vehicle_2_t0.has_velocity_x = 0
    parking_vehicle_2_t0.has_velocity_y = 0
    parking_vehicle_2_t0.has_velocity_z = 0
    parking_vehicle_2_geometry_t0 = ge_1.Geometry()
    parking_vehicle_2_geometry_t0.asWKT = [geometry.Polygon
                                        ([(34.5, 21.5), (39, 21.5), (39, 19.5), (34.5, 19.5), (34.5, 21.5)]).wkt]
    parking_vehicle_2_t0.hasGeometry = [parking_vehicle_2_geometry_t0]

    # Traffic sign
    zone_30_sign_1 = l1_de_1.Beginn_einer_Tempo_30_Zone()
    zone_30_sign_geometry_1 = ge_1.Geometry()
    zone_30_sign_geometry_1.asWKT = [geometry.Point(4, 19).wkt]
    zone_30_sign_1.hasGeometry = [zone_30_sign_geometry_1]
    zone_30_sign_1.is_persistent = True

    # Register entities in scene 1
    scene_1.has_traffic_entity = [road_west_1, road_east_1, road_south_1, western_upper_lane_1, western_lower_lane_1,
                                  eastern_upper_lane_1, eastern_lower_lane_1, southern_left_lane_1,
                                  southern_right_lane_1, bicycle_lane_1, pedestrian_crossing_1, ego_t0, ego_driver_t0,
                                  bicycle_t0, bicyclist_t0, parking_vehicle_1_t0, parking_vehicle_2_t0, zone_30_sign_1,
                                  crossing_1]

    # Traffic sign applies to all entities over time
    zone_30_sign_1.applies_to = scene_1.has_traffic_entity

    ##################
    # Create scene 2 #
    ##################
    scene_2 = tm_2.Scene()
    time_2 = ti_2.TimePosition()
    time_2.numericPosition = [1]
    scene_2.inTimePosition.append(time_2)

    # Create traffic infrastructure
    # Western road
    road_west_2 = l1_de_2.Urban_Road()
    road_west_geometry_2 = ge_2.Geometry()
    road_west_geometry_2.asWKT = [geometry.Polygon([(0, 26), (42, 26), (42, 20), (0, 20), (0, 26)]).wkt]
    road_west_2.hasGeometry = [road_west_geometry_2]
    road_west_2.is_persistent = True
    # Eastern road
    road_east_2 = l1_de_2.Urban_Road()
    road_east_geometry_2 = ge_2.Geometry()
    road_east_geometry_2.asWKT = [geometry.Polygon([(48, 26), (78, 26), (78, 20), (48, 20), (48, 26)]).wkt]
    road_east_2.hasGeometry = [road_east_geometry_2]
    road_east_2.is_persistent = True
    # Southern road
    road_south_2 = l1_de_2.Urban_Road()
    road_south_geometry_2 = ge_2.Geometry()
    road_south_geometry_2.asWKT = [geometry.Polygon([(40, 20), (48, 20), (48, 0), (40, 0), (40, 20)]).wkt]
    road_south_2.hasGeometry = [road_south_geometry_2]
    road_south_2.is_persistent = True
    # Western upper lane
    western_upper_lane_2 = l1_core_2.Driveable_Lane()
    western_upper_lane_geometry_2 = ge_2.Geometry()
    western_upper_lane_geometry_2.asWKT = [geometry.Polygon([(0, 26), (42, 26), (42, 23), (0, 23), (0, 26)]).wkt]
    western_upper_lane_2.hasGeometry = [western_upper_lane_geometry_2]
    western_upper_lane_2.is_persistent = True
    # Western lower lane
    western_lower_lane_2 = l1_core_2.Driveable_Lane()
    western_lower_lane_geometry_2 = ge_2.Geometry()
    western_lower_lane_geometry_2.asWKT = [geometry.Polygon([(0, 23), (42, 23), (42, 20), (0, 20), (0, 23)]).wkt]
    western_lower_lane_2.hasGeometry = [western_lower_lane_geometry_2]
    western_lower_lane_2.is_persistent = True
    # Eastern upper lane
    eastern_upper_lane_2 = l1_core_2.Driveable_Lane()
    eastern_upper_lane_geometry_2 = ge_2.Geometry()
    eastern_upper_lane_geometry_2.asWKT = [geometry.Polygon([(48, 26), (78, 26), (78, 23), (48, 23), (48, 26)]).wkt]
    eastern_upper_lane_2.hasGeometry = [eastern_upper_lane_geometry_2]
    eastern_upper_lane_2.is_persistent = True
    # Eastern lower lane
    eastern_lower_lane_2 = l1_core_2.Driveable_Lane()
    eastern_lower_lane_geometry_2 = ge_2.Geometry()
    eastern_lower_lane_geometry_2.asWKT = [geometry.Polygon([(48, 23), (78, 23), (78, 20), (48, 20), (48, 23)]).wkt]
    eastern_lower_lane_2.hasGeometry = [eastern_lower_lane_geometry_2]
    eastern_lower_lane_2.is_persistent = True
    # Southern left lane
    southern_left_lane_2 = l1_core_2.Driveable_Lane()
    southern_left_lane_geometry_2 = ge_2.Geometry()
    southern_left_lane_geometry_2.asWKT = [geometry.Polygon([(42, 20), (45, 20), (45, 0), (42, 0), (42, 20)]).wkt]
    southern_left_lane_2.hasGeometry = [southern_left_lane_geometry_2]
    southern_left_lane_2.is_persistent = True
    # Southern right lane
    southern_right_lane_2 = l1_core_2.Driveable_Lane()
    southern_right_lane_geometry_2 = ge_2.Geometry()
    southern_right_lane_geometry_2.asWKT = [geometry.Polygon([(45, 20), (48, 20), (48, 0), (45, 0), (45, 20)]).wkt]
    southern_right_lane_2.hasGeometry = [southern_right_lane_geometry_2]
    southern_right_lane_2.is_persistent = True
    # Bicycle lane on southern road
    bicycle_lane_2 = l1_de_2.Bikeway_Lane()
    bicycle_lane_2.has_road = road_south_2
    bicycle_lane_geometry_2 = ge_2.Geometry()
    bicycle_lane_geometry_2.asWKT = [geometry.Polygon([(40, 20), (42, 20), (42, 0), (40, 0), (40, 20)]).wkt]
    bicycle_lane_2.hasGeometry = [bicycle_lane_geometry_2]
    bicycle_lane_2.is_persistent = True
    # Pedestrian crossing on western road
    pedestrian_crossing_2 = l1_de_2.Pedestrian_Crossing()
    pedestrian_crossing_2.has_road = road_west_2
    pedestrian_crossing_geometry_2 = ge_2.Geometry()
    pedestrian_crossing_geometry_2.asWKT = [geometry.Polygon([(39, 26), (42, 26), (42, 20), (39, 20), (39, 26)]).wkt]
    pedestrian_crossing_2.hasGeometry = [pedestrian_crossing_geometry_2]
    pedestrian_crossing_2.is_persistent = True
    # Logical lane & road connections
    road_west_2.has_lane = [western_lower_lane_2, eastern_upper_lane_2, pedestrian_crossing_2]
    road_east_2.has_lane = [eastern_lower_lane_2, eastern_upper_lane_2]
    road_south_2.has_lane = [southern_left_lane_2, southern_right_lane_2, bicycle_lane_2]
    western_lower_lane_2.has_successor_lane = [eastern_lower_lane_2, southern_left_lane_2]
    southern_right_lane_2.has_successor_lane = [eastern_lower_lane_2, western_upper_lane_2]
    eastern_upper_lane_2.has_successor_lane = [western_upper_lane_2, southern_left_lane_2]
    pedestrian_crossing_2.has_predecessor_lane = [bicycle_lane_2]
    bicycle_lane_2.has_successor_lane = [pedestrian_crossing_2]
    # Crossing
    crossing_2 = l1_de_2.Crossing()
    crossing_2.connects = [road_west_2, road_east_2, road_south_2]
    crossing_geometry_2 = ge_2.Geometry()
    crossing_geometry_2.asWKT = [geometry.Polygon([(42, 26), (48, 26), (48, 20), (42, 20), (42, 26)]).wkt]
    crossing_2.hasGeometry = [crossing_geometry_2]
    crossing_2.is_persistent = True

    # Creates road users
    # Ego
    ego_t1 = l4_de_2.Passenger_Car()
    ego_t1.identifier = "Ego"
    ego_t1.has_height = 2
    ego_t1.has_velocity_x = 8
    ego_t1.has_velocity_y = 0
    ego_t1.has_velocity_z = 0
    ego_t1.has_acceleration_x = 0
    ego_t1.has_acceleration_y = 0
    ego_t1.has_acceleration_z = 0
    ego_t1.has_yaw = 0
    ego_t1_geometry = ge_2.Geometry()
    ego_t1_geometry.asWKT = [geometry.Polygon([(23, 24), (28, 24), (28, 22), (23, 22), (23, 24)]).wkt]
    ego_t1.hasGeometry = [ego_t1_geometry]
    ego_t1.identical_to = [ego_t0]
    ego_driver_t1 = l4_core_2.Automated_Driving_Function()
    ego_driver_t1.identifier = "Ego-ADF"
    ego_driver_t1.has_horizontal_field_of_view = 3.14
    ego_driver_t1.has_visibility_range = 200
    ego_driver_t1_geometry = ge_2.Geometry()
    ego_driver_t1_geometry.asWKT = [geometry.Point([25.5, 23]).wkt]
    ego_driver_t1.hasGeometry = [ego_driver_t1_geometry]
    ego_driver_t1.drives = [ego_t1]
    ego_driver_t1.identical_to = [ego_driver_t0]
    ego_t1.driven_by = [ego_driver_t1]
    # Bicyclist
    bicycle_t1 = l4_de_2.Bicycle()
    bicycle_t1.identifier = "Bicycle"
    bicycle_t1.has_height = 1.5
    bicycle_t1.has_velocity_x = 0
    bicycle_t1.has_velocity_y = 6
    bicycle_t1.has_velocity_z = 0
    bicycle_t1.has_acceleration_x = 0
    bicycle_t1.has_acceleration_y = 0
    bicycle_t1.has_acceleration_z = 0
    bicycle_t1.has_yaw = 90
    bicycle_t1_geometry = ge_2.Geometry()
    bicycle_t1_geometry.asWKT = [geometry.Polygon([(41, 18), (41.6, 18), (41.6, 16.2), (41, 16.2), (41, 18)]).wkt]
    bicycle_t1.hasGeometry = [bicycle_t1_geometry]
    bicycle_t1.identical_to = [bicycle_t1]
    bicyclist_t1 = l4_de_2.Bicyclist()
    bicyclist_t1.identifier = "Bicyclist"
    bicyclist_t1.has_horizontal_field_of_view = 3.14
    bicyclist_t1.has_visibility_range = 200
    bicyclist_t1_geometry = ge_2.Geometry()
    bicyclist_t1_geometry.asWKT = [geometry.Point([41.3, 17.1]).wkt]
    bicyclist_t1.hasGeometry = [bicyclist_t1_geometry]
    bicyclist_t1.drives = [bicycle_t1]
    bicyclist_t1.identical_to = [bicyclist_t0]
    bicycle_t1.driven_by = [bicyclist_t1]
    # Parking vehicles
    parking_vehicle_1_t1 = l4_de_2.Parking_Vehicle()
    parking_vehicle_1_t1.identifier = "Parking-Vehicle-#1"
    parking_vehicle_1_t1.identical_to = [parking_vehicle_1_t0]
    parking_vehicle_1_t1.has_yaw = 0
    parking_vehicle_1_t1.has_height = 2
    parking_vehicle_1_t1.has_velocity_x = 0
    parking_vehicle_1_t1.has_velocity_y = 0
    parking_vehicle_1_t1.has_velocity_z = 0
    parking_vehicle_1_geometry_t1 = ge_2.Geometry()
    parking_vehicle_1_geometry_t1.asWKT = [geometry.Polygon([(29, 21.5), (34, 21.5), (34, 19.5), (29, 19.5), (29, 21.5)]
                                                            ).wkt]
    parking_vehicle_1_t1.hasGeometry = [parking_vehicle_1_geometry_t1]
    parking_vehicle_2_t1 = l4_de_2.Parking_Vehicle()
    parking_vehicle_2_t1.identifier = "Parking-Vehicle-#2"
    parking_vehicle_2_t1.identical_to = [parking_vehicle_2_t0]
    parking_vehicle_2_t1.has_yaw = 0
    parking_vehicle_2_t1.has_height = 2
    parking_vehicle_2_t1.has_velocity_x = 0
    parking_vehicle_2_t1.has_velocity_y = 0
    parking_vehicle_2_t1.has_velocity_z = 0
    parking_vehicle_2_geometry_t1 = ge_2.Geometry()
    parking_vehicle_2_geometry_t1.asWKT = [geometry.Polygon
                                        ([(34.5, 21.5), (39, 21.5), (39, 19.5), (34.5, 19.5), (34.5, 21.5)]).wkt]
    parking_vehicle_2_t1.hasGeometry = [parking_vehicle_2_geometry_t1]

    # Traffic sign
    zone_30_sign_2 = l1_de_2.Beginn_einer_Tempo_30_Zone()
    zone_30_sign_geometry_2 = ge_2.Geometry()
    zone_30_sign_geometry_2.asWKT = [geometry.Point(4, 19).wkt]
    zone_30_sign_2.hasGeometry = [zone_30_sign_geometry_2]
    zone_30_sign_2.is_persistent = True

    # Register entities in scene 3
    scene_2.has_traffic_entity = [road_west_2, road_east_2, road_south_2, western_upper_lane_2, western_lower_lane_2,
                                  eastern_upper_lane_2, eastern_lower_lane_2, southern_left_lane_2,
                                  southern_right_lane_2, bicycle_lane_2, pedestrian_crossing_2, ego_t1, ego_driver_t1,
                                  bicycle_t1, bicyclist_t1, parking_vehicle_1_t1, parking_vehicle_2_t1, zone_30_sign_2,
                                  crossing_2]

    # Traffic sign applies to all entities over time
    zone_30_sign_2.applies_to = scene_2.has_traffic_entity

    ##################
    # Create scene 3 #
    ##################
    scene_3 = tm_3.Scene()
    time_3 = ti_3.TimePosition()
    time_3.numericPosition = [2]
    scene_3.inTimePosition.append(time_3)

    # Create traffic infrastructure
    # Western road
    road_west_3 = l1_de_3.Urban_Road()
    road_west_geometry_3 = ge_3.Geometry()
    road_west_geometry_3.asWKT = [geometry.Polygon([(0, 26), (42, 26), (42, 20), (0, 20), (0, 26)]).wkt]
    road_west_3.hasGeometry = [road_west_geometry_3]
    road_west_3.is_persistent = True
    # Eastern road
    road_east_3 = l1_de_3.Urban_Road()
    road_east_geometry_3 = ge_3.Geometry()
    road_east_geometry_3.asWKT = [geometry.Polygon([(48, 26), (78, 26), (78, 20), (48, 20), (48, 26)]).wkt]
    road_east_3.hasGeometry = [road_east_geometry_3]
    road_east_3.is_persistent = True
    # Southern road
    road_south_3 = l1_de_3.Urban_Road()
    road_south_geometry_3 = ge_3.Geometry()
    road_south_geometry_3.asWKT = [geometry.Polygon([(40, 20), (48, 20), (48, 0), (40, 0), (40, 20)]).wkt]
    road_south_3.hasGeometry = [road_south_geometry_3]
    road_south_3.is_persistent = True
    # Western upper lane
    western_upper_lane_3 = l1_core_3.Driveable_Lane()
    western_upper_lane_geometry_3 = ge_3.Geometry()
    western_upper_lane_geometry_3.asWKT = [geometry.Polygon([(0, 26), (42, 26), (42, 23), (0, 23), (0, 26)]).wkt]
    western_upper_lane_3.hasGeometry = [western_upper_lane_geometry_3]
    western_upper_lane_3.is_persistent = True
    # Western lower lane
    western_lower_lane_3 = l1_core_3.Driveable_Lane()
    western_lower_lane_geometry_3 = ge_3.Geometry()
    western_lower_lane_geometry_3.asWKT = [geometry.Polygon([(0, 23), (42, 23), (42, 20), (0, 20), (0, 23)]).wkt]
    western_lower_lane_3.hasGeometry = [western_lower_lane_geometry_3]
    western_lower_lane_3.is_persistent = True
    # Eastern upper lane
    eastern_upper_lane_3 = l1_core_3.Driveable_Lane()
    eastern_upper_lane_geometry_3 = ge_3.Geometry()
    eastern_upper_lane_geometry_3.asWKT = [geometry.Polygon([(48, 26), (78, 26), (78, 23), (48, 23), (48, 26)]).wkt]
    eastern_upper_lane_3.hasGeometry = [eastern_upper_lane_geometry_3]
    eastern_upper_lane_3.is_persistent = True
    # Eastern lower lane
    eastern_lower_lane_3 = l1_core_3.Driveable_Lane()
    eastern_lower_lane_geometry_3 = ge_3.Geometry()
    eastern_lower_lane_geometry_3.asWKT = [geometry.Polygon([(48, 23), (78, 23), (78, 20), (48, 20), (48, 23)]).wkt]
    eastern_lower_lane_3.hasGeometry = [eastern_lower_lane_geometry_3]
    eastern_lower_lane_3.is_persistent = True
    # Southern left lane
    southern_left_lane_3 = l1_core_3.Driveable_Lane()
    southern_left_lane_geometry_3 = ge_3.Geometry()
    southern_left_lane_geometry_3.asWKT = [geometry.Polygon([(42, 20), (45, 20), (45, 0), (42, 0), (42, 20)]).wkt]
    southern_left_lane_3.hasGeometry = [southern_left_lane_geometry_3]
    southern_left_lane_3.is_persistent = True
    # Southern right lane
    southern_right_lane_3 = l1_core_3.Driveable_Lane()
    southern_right_lane_geometry_3 = ge_3.Geometry()
    southern_right_lane_geometry_3.asWKT = [geometry.Polygon([(45, 20), (48, 20), (48, 0), (45, 0), (45, 20)]).wkt]
    southern_right_lane_3.hasGeometry = [southern_right_lane_geometry_3]
    southern_right_lane_3.is_persistent = True
    # Bicycle lane on southern road
    bicycle_lane_3 = l1_de_3.Bikeway_Lane()
    bicycle_lane_3.has_road = road_south_3
    bicycle_lane_geometry_3 = ge_3.Geometry()
    bicycle_lane_geometry_3.asWKT = [geometry.Polygon([(40, 20), (42, 20), (42, 0), (40, 0), (40, 20)]).wkt]
    bicycle_lane_3.hasGeometry = [bicycle_lane_geometry_3]
    bicycle_lane_3.is_persistent = True
    # Pedestrian crossing on western road
    pedestrian_crossing_3 = l1_de_3.Pedestrian_Crossing()
    pedestrian_crossing_3.has_road = road_west_3
    pedestrian_crossing_geometry_3 = ge_3.Geometry()
    pedestrian_crossing_geometry_3.asWKT = [geometry.Polygon([(39, 26), (42, 26), (42, 20), (39, 20), (39, 26)]).wkt]
    pedestrian_crossing_3.hasGeometry = [pedestrian_crossing_geometry_3]
    pedestrian_crossing_3.is_persistent = True
    # Logical lane & road connections
    road_west_3.has_lane = [western_lower_lane_3, eastern_upper_lane_3, pedestrian_crossing_3]
    road_east_3.has_lane = [eastern_lower_lane_3, eastern_upper_lane_3]
    road_south_3.has_lane = [southern_left_lane_3, southern_right_lane_3, bicycle_lane_3]
    western_lower_lane_3.has_successor_lane = [eastern_lower_lane_3, southern_left_lane_3]
    southern_right_lane_3.has_successor_lane = [eastern_lower_lane_3, western_upper_lane_3]
    eastern_upper_lane_3.has_successor_lane = [western_upper_lane_3, southern_left_lane_3]
    pedestrian_crossing_3.has_predecessor_lane = [bicycle_lane_3]
    bicycle_lane_3.has_successor_lane = [pedestrian_crossing_3]
    # Crossing
    crossing_3 = l1_de_3.Crossing()
    crossing_3.connects = [road_west_3, road_east_3, road_south_3]
    crossing_geometry_3 = ge_3.Geometry()
    crossing_geometry_3.asWKT = [geometry.Polygon([(42, 26), (48, 26), (48, 20), (42, 20), (42, 26)]).wkt]
    crossing_3.hasGeometry = [crossing_geometry_3]
    crossing_3.is_persistent = True

    # Creates road users
    # Ego
    ego_t2 = l4_de_3.Passenger_Car()
    ego_t2.identifier = "Ego"
    ego_t2.has_height = 2
    ego_t2.has_velocity_x = 1
    ego_t2.has_velocity_y = 0
    ego_t2.has_velocity_z = 0
    ego_t2.has_acceleration_x = -5
    ego_t2.has_acceleration_y = 0
    ego_t2.has_acceleration_z = 0
    ego_t2.has_yaw = 0
    ego_t2_geometry = ge_3.Geometry()
    ego_t2_geometry.asWKT = [geometry.Polygon([(33.5, 24.5), (38.5, 24.5), (38.5, 22.5), (33.5, 22.5), (33.5, 24.5)]).
                                 wkt]
    ego_t2.hasGeometry = [ego_t2_geometry]
    ego_t2.identical_to = [ego_t1]
    ego_driver_t2 = l4_core_3.Automated_Driving_Function()
    ego_driver_t2.identifier = "Ego-ADF"
    ego_driver_t2.has_horizontal_field_of_view = 3
    ego_driver_t2.has_visibility_range = 100
    ego_driver_t2_geometry = ge_3.Geometry()
    ego_driver_t2_geometry.asWKT = [geometry.Point([36, 23.5]).wkt]
    ego_driver_t2.hasGeometry = [ego_driver_t2_geometry]
    ego_driver_t2.drives = [ego_t2]
    ego_driver_t2.identical_to = [ego_driver_t1]
    ego_t2.driven_by = [ego_driver_t2]
    # Bicyclist
    bicycle_t2 = l4_de_3.Bicycle()
    bicycle_t2.identifier = "Bicycle"
    bicycle_t2.has_height = 1.5
    bicycle_t2.has_velocity_x = 0
    bicycle_t2.has_velocity_y = 5
    bicycle_t2.has_velocity_z = 0
    bicycle_t2.has_acceleration_x = 0
    bicycle_t2.has_acceleration_y = -0.5
    bicycle_t2.has_acceleration_z = 0
    bicycle_t2.has_yaw = 90
    bicycle_t2_geometry = ge_3.Geometry()
    bicycle_t2_geometry.asWKT = [geometry.Polygon
                                 ([(40.9, 23.5), (41.5, 23.5), (41.5, 21.7), (40.9, 21.7), (40.9, 23.5)]).wkt]
    bicycle_t2.hasGeometry = [bicycle_t2_geometry]
    bicycle_t2.identical_to = [bicycle_t1]
    bicyclist_t2 = l4_de_3.Bicyclist()
    bicyclist_t2.identifier = "Bicyclist"
    bicyclist_t2.has_horizontal_field_of_view = 3
    bicyclist_t2.has_visibility_range = 100
    bicyclist_t2_geometry = ge_3.Geometry()
    bicyclist_t2_geometry.asWKT = [geometry.Point([41.2, 22.6]).wkt]
    bicyclist_t2.hasGeometry = [bicyclist_t2_geometry]
    bicyclist_t2.drives = [bicycle_t2]
    bicyclist_t2.identical_to = [bicyclist_t1]
    bicycle_t2.driven_by = [bicyclist_t2]
    # Parking vehicles
    parking_vehicle_1_t2 = l4_de_3.Parking_Vehicle()
    parking_vehicle_1_t2.identifier = "Parking-Vehicle-#1"
    parking_vehicle_1_t2.identical_to = [parking_vehicle_1_t1]
    parking_vehicle_1_t2.has_yaw = 0
    parking_vehicle_1_t2.has_height = 2
    parking_vehicle_1_t2.has_velocity_x = 0
    parking_vehicle_1_t2.has_velocity_y = 0
    parking_vehicle_1_t2.has_velocity_z = 0
    parking_vehicle_1_geometry_t2 = ge_3.Geometry()
    parking_vehicle_1_geometry_t2.asWKT = [geometry.Polygon([(29, 21.5), (34, 21.5), (34, 19.5), (29, 19.5), (29, 21.5)]
                                                            ).wkt]
    parking_vehicle_1_t2.hasGeometry = [parking_vehicle_1_geometry_t2]
    parking_vehicle_2_t2 = l4_de_3.Parking_Vehicle()
    parking_vehicle_2_t2.identifier = "Parking-Vehicle-#2"
    parking_vehicle_2_t2.identical_to = [parking_vehicle_2_t1]
    parking_vehicle_2_t2.has_yaw = 0
    parking_vehicle_2_t2.has_height = 2
    parking_vehicle_2_t2.has_velocity_x = 0
    parking_vehicle_2_t2.has_velocity_y = 0
    parking_vehicle_2_t2.has_velocity_z = 0
    parking_vehicle_2_geometry_t2 = ge_3.Geometry()
    parking_vehicle_2_geometry_t2.asWKT = [geometry.Polygon
                                        ([(34.5, 21.5), (39, 21.5), (39, 19.5), (34.5, 19.5), (34.5, 21.5)]).wkt]
    parking_vehicle_2_t2.hasGeometry = [parking_vehicle_2_geometry_t2]

    # Traffic sign
    zone_30_sign_3 = l1_de_3.Beginn_einer_Tempo_30_Zone()
    zone_30_sign_geometry_3 = ge_3.Geometry()
    zone_30_sign_geometry_3.asWKT = [geometry.Point(4, 19).wkt]
    zone_30_sign_3.hasGeometry = [zone_30_sign_geometry_3]
    zone_30_sign_3.is_persistent = True

    # Register entities in scene 3
    scene_3.has_traffic_entity = [road_west_3, road_east_3, road_south_3, western_upper_lane_3, western_lower_lane_3,
                                  eastern_upper_lane_3, eastern_lower_lane_3, southern_left_lane_3,
                                  southern_right_lane_3, bicycle_lane_3, pedestrian_crossing_3, ego_t2, ego_driver_t2,
                                  bicycle_t2, bicyclist_t2, parking_vehicle_1_t2, parking_vehicle_2_t2, zone_30_sign_3,
                                  crossing_3]

    # Traffic sign applies to all entities over time
    zone_30_sign_3.applies_to = scene_3.has_traffic_entity

    return [fuc_2_3_world_1, fuc_2_3_world_2, fuc_2_3_world_3]
