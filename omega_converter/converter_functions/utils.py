import owlready2
import logging

from auto import auto
import omega_format
from shapely import geometry, affinity, wkt

# Logging
logger = logging.getLogger(__name__)


# Decorator for patching methods within OMEGA module.

def monkeypatch(cls):
    def decorator(func):
        setattr(cls, func.__name__, func)
        return func

    return decorator


# Utils

def add_relation(owl_entity, owl_relation: str, target_rr_entity, scene=None):
    # Note: this is untested code
    # Connected object was already converted for this scene
    if scene and hasattr(target_rr_entity, "last_owl_instance") and \
            target_rr_entity.last_owl_instance[0].in_scene[0] == scene:
        setattr(owl_entity, owl_relation, target_rr_entity.last_owl_instance)
    # Connected object does not yet exist, store relation to be added later
    else:
        if hasattr(target_rr_entity, "owl_relations"):
            target_rr_entity.owl_relations.append((owl_entity, owl_relation))
        else:
            target_rr_entity.owl_relations = [(owl_entity, owl_relation)]


def instantiate_relations(to_rr_entity):
    if hasattr(to_rr_entity, "owl_relations"):
        for from_owl_entity, owl_relation in to_rr_entity.owl_relations:
            if hasattr(to_rr_entity, "last_owl_entity"):
                getattr(from_owl_entity, owl_relation).append(to_rr_entity.last_owl_entity)
            else:
                logger.warning("Tried to add relation " + owl_relation + " to " + str(from_owl_entity) +
                               " but could not identify target.")


def add_layer_3_information(cls, owl_entity, world):
    if hasattr(cls, "layer_flag") and cls.layer_flag:
        owl_entity.is_a.append(auto.get_ontology(auto.Ontology.L3_Core, world).Modifying_Entity)
        if hasattr(cls, "overrides") and cls.overrides:
            for overrides in cls.overrides.data.values():
                # overriddenBy is omitted since it is modelled as the inverse of modifies in OWL
                add_relation(owl_entity, "modifies", overrides)


def add_bounding_box(cls, owl_inst):
    if len(cls.bb.vec) > 0:
        owl_inst.has_length = float(cls.bb.vec[0])
    if len(cls.bb.vec) > 1:
        owl_inst.has_width = float(cls.bb.vec[1])
    if len(cls.bb.vec) > 2:
        owl_inst.has_height = float(cls.bb.vec[2])


def add_geometry_from_polygon(cls, owl_inst, world):
    poly = cls.polyline
    wkt_string = "POLYGON (("
    if max(poly.pos_z) == 0 and cls.height > 0:
        # Note: untested code
        for i in range(len(poly.pos_x)):
            wkt_string += str(poly.pos_x[i]) + " " + str(poly.pos_y[i]) + " " + str(poly.pos_z[i]) + ", "
        for i in range(len(poly.pos_x)):
            wkt_string += str(poly.pos_x[i]) + " " + str(poly.pos_y[i]) + " " + str(cls.height) + ", "
        wkt_string += str(poly.pos_x[0]) + " " + str(poly.pos_y[0]) + " " + str(poly.pos_z[0]) + " ))"
    else:
        for i in range(len(poly.pos_x)):
            wkt_string += str(poly.pos_x[i]) + " " + str(poly.pos_y[i]) + " " + str(poly.pos_z[i]) + ", "
        wkt_string = wkt_string[0:-2] + " ))"
    geom = wkt.loads(wkt_string)
    inst_geom = auto.get_ontology(auto.Ontology.GeoSPARQL, world).Geometry()
    inst_geom.asWKT = [str(geom)]
    owl_inst.hasGeometry = [inst_geom]


def add_geometry_from_trajectory(cls, owl_inst, time, world):
    owl_inst_geometry = auto.get_ontology(auto.Ontology.GeoSPARQL, world).Geometry()
    l11 = (cls.tr.pos_x[time] - 0.5 * owl_inst.has_length, cls.tr.pos_y[time] -
           0.5 * owl_inst.has_width, cls.tr.pos_z[time])
    l12 = (cls.tr.pos_x[time] - 0.5 * owl_inst.has_length, cls.tr.pos_y[time] +
           0.5 * owl_inst.has_width, cls.tr.pos_z[time])
    l21 = (cls.tr.pos_x[time] + 0.5 * owl_inst.has_length, cls.tr.pos_y[time] -
           0.5 * owl_inst.has_width, cls.tr.pos_z[time])
    l22 = (cls.tr.pos_x[time] + 0.5 * owl_inst.has_length, cls.tr.pos_y[time] +
           0.5 * owl_inst.has_width, cls.tr.pos_z[time])
    h11 = (cls.tr.pos_x[time] - 0.5 * owl_inst.has_length, cls.tr.pos_y[time] -
           0.5 * owl_inst.has_width, cls.tr.pos_z[time] +
           owl_inst.has_height)
    h12 = (cls.tr.pos_x[time] - 0.5 * owl_inst.has_length, cls.tr.pos_y[time] +
           0.5 * owl_inst.has_width, cls.tr.pos_z[time] +
           owl_inst.has_height)
    h21 = (cls.tr.pos_x[time] + 0.5 * owl_inst.has_length, cls.tr.pos_y[time] -
           0.5 * owl_inst.has_width, cls.tr.pos_z[time] +
           owl_inst.has_height)
    h22 = (cls.tr.pos_x[time] + 0.5 * owl_inst.has_length, cls.tr.pos_y[time] +
           0.5 * owl_inst.has_width, cls.tr.pos_z[time] +
           owl_inst.has_height)
    bb = geometry.Polygon([l11, l12, l22, l21, l11, h11, h12, h22, h21, h11, l11, l12, h12, h22, l22, l21, h21, h11,
                           l11])
    rotated_bb = affinity.rotate(bb, cls.tr.heading[time])
    owl_inst_geometry.asWKT = [rotated_bb.wkt]
    owl_inst.hasGeometry = [owl_inst_geometry]


def add_physical_properties(cls, owl_inst, time):
    if cls.tr.vel_longitudinal is not None:
        owl_inst.has_velocity_x = float(cls.tr.vel_longitudinal[time])
    if cls.tr.vel_lateral is not None:
        owl_inst.has_velocity_y = float(cls.tr.vel_lateral[time])
    if cls.tr.vel_z is not None:
        owl_inst.has_velocity_z = float(cls.tr.vel_z[time])
    if cls.tr.acc_longitudinal is not None:
        owl_inst.has_acceleration_x = float(cls.tr.acc_longitudinal[time])
    if cls.tr.acc_lateral is not None:
        owl_inst.has_acceleration_y = float(cls.tr.acc_lateral[time])
    if cls.tr.acc_z is not None:
        owl_inst.has_acceleration_z = float(cls.tr.acc_z[time])
    if cls.tr.roll is not None:
        owl_inst.has_roll = float(cls.tr.roll[time])
    if cls.tr.pitch is not None:
        owl_inst.has_pitch = float(cls.tr.pitch[time])
    if cls.tr.heading is not None:
        owl_inst.has_yaw = float(cls.tr.heading[time])
    if cls.tr.roll_der is not None:
        owl_inst.has_roll_rate = float(cls.tr.roll_der[time])
    if cls.tr.pitch_der is not None:
        owl_inst.has_pitch_rate = float(cls.tr.pitch_der[time])
    if cls.tr.heading_der is not None:
        owl_inst.has_yaw_rate = float(cls.tr.heading_der[time])