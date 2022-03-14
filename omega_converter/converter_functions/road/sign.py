import omega_format
from ..utils import *


@monkeypatch(omega_format.Sign)
def to_auto(cls, world: owlready2.World, scenes, identifier=None, parent_identifier=None):

    # Fetches ontologies
    geo = auto.get_ontology(auto.Ontology.GeoSPARQL, world)
    l1_core = auto.get_ontology(auto.Ontology.L1_Core, world)
    l1_de = auto.get_ontology(auto.Ontology.L1_DE, world)

    # Creates sign instance
    sign = l1_core.Traffic_Sign()
    sign.identifier = str(parent_identifier) + "_" + str(identifier)
    for scene in scenes:
        scene.has_traffic_entity.append(sign)

    # Type
    if cls.type == omega_format.ReferenceTypes.SignType.GIVE_WAY:
        sign.is_a.append(l1_de.Vorfahrt_gewähren)
    elif cls.type == omega_format.ReferenceTypes.SignType.STOP_GIVE_WAY:
        sign.is_a.append(l1_de.Halt_Vorfahrt_gewähren)
    elif cls.type == omega_format.ReferenceTypes.SignType.NO_PARKING:
        sign.is_a.append(l1_de.Absolutes_Haltverbot)
    elif cls.type == omega_format.ReferenceTypes.SignType.NO_PARKING_START:
        sign.is_a.append(l1_de.Absolutes_Haltverbot_Anfang_Aufstellung_rechts)
    elif cls.type == omega_format.ReferenceTypes.SignType.RESTRICTED_PARKING:
        sign.is_a.append(l1_de.Eingeschränktes_Haltverbot)
    elif cls.type == omega_format.ReferenceTypes.SignType.PRIORITY:
        sign.is_a.append(l1_de.Vorfahrt)
    elif cls.type == omega_format.ReferenceTypes.SignType.PARKING:
        sign.is_a.append(l1_de.Parken)
    elif cls.type == omega_format.ReferenceTypes.SignType.DEAD_END:
        sign.is_a.append(l1_de.Sackgasse)
    elif cls.type == omega_format.ReferenceTypes.SignType.DEAD_END_CYCLISTS_AND_PEDESTRIANS_CAN_PASS:
        sign.is_a.append(l1_de.Sackgasse_für_Radverkehr_und_Fußgänger_durchlässige_Sackgasse)
    elif cls.type == omega_format.ReferenceTypes.SignType.DEAD_END_PEDESTRIANS_CAN_PASS:
        sign.is_a.append(l1_de.Sackgasse_für_Fußgänger_durchlässige_Sackgasse)
    elif cls.type == omega_format.ReferenceTypes.SignType.TL_REGULAR:
        sign.is_a.append(l1_de.Road_Vehicle_Traffic_Light)
    elif cls.type == omega_format.ReferenceTypes.SignType.TL_ARROW_STRAIGHT:
        sign.is_a.append(l1_de.Straight_Traffic_Light)
    elif cls.type == omega_format.ReferenceTypes.SignType.TL_ARROW_RIGHT:
        sign.is_a.append(l1_de.Left_Traffic_Light)
    elif cls.type == omega_format.ReferenceTypes.SignType.TL_ARROW_LEFT:
        sign.is_a.append(l1_de.Right_Traffic_Light)
    elif cls.type == omega_format.ReferenceTypes.SignType.TL_ARROW_STRAIGHT_RIGHT:
        sign.is_a.append(l1_de.Straight_Traffic_Light)
        sign.is_a.append(l1_de.Right_Traffic_Light)
    elif cls.type == omega_format.ReferenceTypes.SignType.TL_ARROW_STRAIGHT_LEFT:
        sign.is_a.append(l1_de.Straight_Traffic_Light)
        sign.is_a.append(l1_de.Left_Traffic_Light)
    elif cls.type == omega_format.ReferenceTypes.SignType.TL_PEDESTRIAN:
        sign.is_a.append(l1_de.Pedestrian_Traffic_Light)
    elif cls.type == omega_format.ReferenceTypes.SignType.TL_BICYCLE:
        sign.is_a.append(l1_de.Bicycle_Traffic_Light)
    elif cls.type == omega_format.ReferenceTypes.SignType.TL_PEDESTRIAN_BICYCLE:
        sign.is_a.append(l1_de.Pedestrian_Traffic_Light)
        sign.is_a.append(l1_de.Bicycle_Traffic_Light)
    elif cls.type == omega_format.ReferenceTypes.SignType.LIGHT_SINGLE:
        sign.is_a.append(l1_de.Single_Traffic_Light)
    elif cls.type == omega_format.ReferenceTypes.SignType.TL_RED_AMBER:
        sign.is_a.append(l1_de.Double_Traffic_Light)
    elif cls.type == omega_format.ReferenceTypes.SignType.LANE_LIGHT:
        sign.is_a.append(l1_de.Lane_Traffic_Light)
    elif cls.type == omega_format.ReferenceTypes.SignType.BUS_LIGHT:
        sign.is_a.append(l1_de.Bus_Traffic_Light)
    elif cls.type == omega_format.ReferenceTypes.SignType.SWITCHABLE:
        sign.is_a.append(l1_de.Switchable_Traffic_Light)
    elif cls.type == omega_format.ReferenceTypes.SignType.BARRIER:
        sign.is_a.append(l1_de.Double_Traffic_Light)
    elif cls.type == omega_format.ReferenceTypes.SignType.WALKWAY:
        sign.is_a.append(l1_de.Gehweg)
    elif cls.type == omega_format.ReferenceTypes.SignType.CROSSING:
        sign.is_a.append(l1_de.Kreuzung_oder_Einmündung)
    elif cls.type == omega_format.ReferenceTypes.SignType.BICYCLE_STREET_END:
        sign.is_a.append(l1_de.Ende_einer_Fahrradstraße)
    elif cls.type == omega_format.ReferenceTypes.SignType.ZONE_30_START:
        sign.is_a.append(l1_de.Beginn_einer_Tempo_30_Zone)
    elif cls.type == omega_format.ReferenceTypes.SignType.NO_CYCLING:
        sign.is_a.append(l1_de.Verbot_für_Radverkehr)
    elif cls.type == omega_format.ReferenceTypes.SignType.PARKING_WITH_TICKET:
        sign.is_a.append(l1_de.Mit_Parkschein)
    elif cls.type == omega_format.ReferenceTypes.SignType.PARKING_RESTRICTED_ZONE_START:
        sign.is_a.append(l1_de.Beginn_eines_eingeschränkten_Haltverbotes_für_eine_Zone)
    elif cls.type == omega_format.ReferenceTypes.SignType.PARKING_RESTRICTED_ZONE_END:
        sign.is_a.append(l1_de.Ende_eines_eingeschränkten_Haltverbotes_für_eine_Zon)
    elif cls.type == omega_format.ReferenceTypes.SignType.END_OF_ABSOLUT_PARKING_RESTRICTION_END_RIGHT:
        sign.is_a.append(l1_de.Absolutes_Haltverbot_Ende_Aufstellung_rechts)
    elif cls.type == omega_format.ReferenceTypes.SignType.BEGIN_OF_ABSOLUT_PARKING_RESTRICTION_END_RIGHT:
        sign.is_a.append(l1_de.Absolutes_Haltverbot_Mitte_Aufstellung_rechts)
    elif cls.type == omega_format.ReferenceTypes.SignType.PARKING_ON_SIDEWALK_HALF_RIGHT_CENTER:
        sign.is_a.append(l1_de.Parken_auf_Gehwegen_halb_in_Fahrtrichtung_rechts_Mitte)
    elif cls.type == omega_format.ReferenceTypes.SignType.PARKING_ON_SIDEWALK_HALF_RIGHT_START:
        sign.is_a.append(l1_de.Parken_auf_Gehwegen_halb_in_Fahrtrichtung_rechts_Anfang)
    elif cls.type == omega_format.ReferenceTypes.SignType.PEDESTRIAN_CROSSING_RIGHT:
        sign.is_a.append(l1_de.Fußgängerüberweg_Aufstellung_rechts)
    elif cls.type == omega_format.ReferenceTypes.SignType.PEDESTRIAN_CROSSING_LEFT:
        sign.is_a.append(l1_de.Fußgängerüberweg_Aufstellung_links)
    elif cls.type == omega_format.ReferenceTypes.SignType.PRIORITY_ROAD:
        sign.is_a.append(l1_de.Vorfahrtstraße)
    elif cls.type == omega_format.ReferenceTypes.SignType.NO_VEHICLES_ALLOWED:
        sign.is_a.append(l1_de.Verbot_für_Fahrzeuge_aller_Art)
    elif cls.type == omega_format.ReferenceTypes.SignType.NO_ENTRY:
        sign.is_a.append(l1_de.Verbot_der_Einfahrt)
    elif cls.type == omega_format.ReferenceTypes.SignType.CROSSING_BICYCLE_LEFT_RIGHT:
        sign.is_a.append(l1_de.Radverkehr_kreuzt_von_links_und_rechts)
    elif cls.type == omega_format.ReferenceTypes.SignType.TRAFFIC_CALM_AREA_START:
        sign.is_a.append(l1_de.Beginn_eines_verkehrsberuhigten_Bereichs)
    elif cls.type == omega_format.ReferenceTypes.SignType.TRAFFIC_CALM_AREA_END:
        sign.is_a.append(l1_de.Ende_eines_verkehrsberuhigten_Bereichs)
    elif cls.type == omega_format.ReferenceTypes.SignType.GUIDE_PLATE:
        sign.is_a.append(l1_de.Leitplatte_750_x_500)
    elif cls.type == omega_format.ReferenceTypes.SignType.PRESCRIBED_PASSING_RIGHT:
        sign.is_a.append(l1_de.Vorgeschriebene_Vorbeifahrt_rechts_vorbei)
    elif cls.type == omega_format.ReferenceTypes.SignType.PRESCRIBED_PASSING_LEFT:
        sign.is_a.append(l1_de.Vorgeschriebene_Vorbeifahrt_links_vorbei)
    elif cls.type == omega_format.ReferenceTypes.SignType.PRESCRIBED_DIRECTION_STRAIGHT_RIGHT:
        sign.is_a.append(l1_de.Vorgeschriebene_Fahrtrichtung_geradeaus_oder_rechts)
    elif cls.type == omega_format.ReferenceTypes.SignType.RESIDENTS_FREE:
        sign.is_a.append(l1_de.Anlieger_frei)
    elif cls.type == omega_format.ReferenceTypes.SignType.MOTORWAY_RIGHT:
        sign.is_a.append(l1_de.Pfeilwegweiser_zur_Autobahn_rechtsweisend)
    elif cls.type == omega_format.ReferenceTypes.SignType.CYCLISTS_ARE_ALLOWED:
        sign.is_a.append(l1_de.Radfahrer_frei)
    elif cls.type == omega_format.ReferenceTypes.SignType.MANDATORY_TURN_RIGHT:
        sign.is_a.append(l1_de.Vorgeschriebene_Fahrtrichtung_rechts)
    elif cls.type == omega_format.ReferenceTypes.SignType.MANDATORY_TURN_LEFT:
        sign.is_a.append(l1_de.Vorgeschriebene_Fahrtrichtung_links)
    elif cls.type == omega_format.ReferenceTypes.SignType.MANDATORY_STRAIGHT:
        sign.is_a.append(l1_de.Vorgeschriebene_Fahrtrichtung_geradeaus)
    elif cls.type == omega_format.ReferenceTypes.SignType.BUS_STOP:
        sign.is_a.append(l1_de.Haltestelle)
    elif cls.type == omega_format.ReferenceTypes.SignType.MAXIMUM_SPEED_50:
        sign.is_a.append(l1_de.Zulässige_Höchstgeschwindigkeit_50_km_h)

    # Geometry
    wkt_str = "POINT (" + str(cls.position.pos_x) + " " + str(cls.position.pos_y) + " " + str(cls.position.pos_z) + ")"
    geom = wkt.loads(wkt_str)
    inst_geom = geo.Geometry()
    inst_geom.asWKT = [str(geom)]
    sign.hasGeometry = [inst_geom]

    # Size
    # TODO size class depends on various factors such as road speeds and sign type.
    if cls.size_class == omega_format.ReferenceTypes.SignSizeClass.SMALL:
        pass
    elif cls.size_class == omega_format.ReferenceTypes.SignSizeClass.MIDDLE:
        pass
    elif cls.size_class == omega_format.ReferenceTypes.SignSizeClass.LARGE:
        pass

    # Numerical value
    if cls.value != 0:
        sign.has_sign_value = [int(cls.value)]

    # Fallback
    if cls.fallback:
        sign.is_a.append(l1_de.Fallback_Traffic_Post)

    # Weather dependent
    if cls.time_dependent:
        sign.is_a.append(l1_de.Wather_Dependent_Sign_Post)

    # Time dependent
    if cls.weather_dependent:
        sign.is_a.append(l1_de.Time_Dependent_Sign_Post)

    # Heading
    if cls.heading != 0:
        sign.has_yaw = float(cls.heading)

    # Marked lanes
    for lane in cls.applicable_lanes.data.values():
        add_relation(sign, "applies_to", lane)

    # Connected signs
    for con_sign in cls.connected_to.data.values():
        add_relation(sign, "connected_to", con_sign)

    add_layer_3_information(cls, sign, world)

    return [(cls, [sign])]
