import logging
import math
import os
import owlready2
import tempfile

from auto import auto
import omega_format
from .converter_functions.utils import *
from .converter_functions.dynamics.road_user import *
from .converter_functions.dynamics.misc_object import *
from .converter_functions.weather.weather import *
from .converter_functions.road.road import *
from .converter_functions.road.road_object import *
from .converter_functions.road.sign import *
from .converter_functions.road.state import *
from .converter_functions.road.boundary import *
from .converter_functions.road.structural_object import *
from .converter_functions.road.flat_marking import *
from .converter_functions.road.lane import *
from .converter_functions.road.lateral_marking import *

# Constants
MAX_SCENARIO_DURATION = 5  # s, longer scenarios will not be converted
MAX_SCENES_PER_SCENARIO = 4  # how many scenes a scenario shall have - rest is removed (samples equidistantly)

# Logging
logger = logging.getLogger(__name__)


def _load_hdf5(omega_file="inD.hdf5"):
    """
    Loads OMEGA HDF5 from the given file location.
    :param omega_file: The path to the OMEGA HDF5 file.
    :return: The ReferenceRecording instance.
    """
    logger.debug("Loading OMEGA file " + str(omega_file))
    rr = omega_format.ReferenceRecording.from_hdf5(filename=omega_file)
    logger.debug("Finished loading OMEGA file")
    return rr


def _add_identity_information(instance_tuples):
    """
    Adds the identity relation that tracks same objects over multiple scenes based on the information returned by the
    `to_auto` functions.
    :param instance_tuples: A list of tuples with the first entry being a OMEGA object, the second one begin a list of
    corresponding OWL individuals representing the first entry. Each time iteration, the same list sorting of the second
    entry is expected.
    """
    for rr_inst, owl_inst in instance_tuples:
        for i, inst in enumerate(owl_inst):
            try:
                inst.identical_to = [rr_inst.last_owl_instance[i]]
            except AttributeError:
                pass
        setattr(rr_inst, "last_owl_instance", owl_inst)


def _get_speed_limit(rr: omega_format.ReferenceRecording) -> int or None:
    """
    Returns the speed limit in the given reference recording or None if the speed limit can not be determined.
    Determination works via a simple lookup of known locations and speed limits.
    :param rr: The reference recording
    """
    if math.isclose(rr.meta_data.reference_point_lat, 50.78563844942432) and \
            math.isclose(rr.meta_data.reference_point_lon, 6.128973907195158):
        # Charlottenburger Allee - Neuköllner Str. (Location 4)
        return 50
    elif math.isclose(rr.meta_data.reference_point_lat, 50.779082542457765) and \
            math.isclose(rr.meta_data.reference_point_lon, 6.164784245039574):
        # Von-Coels-Str. - Heckstr. (Location 3)
        return 50
    elif math.isclose(rr.meta_data.reference_point_lat, 50.768629564172194) and \
            math.isclose(rr.meta_data.reference_point_lon, 6.101500261218432):
        # Bismarckstr. - Schlossstr. (Location 2)
        return 30
    elif math.isclose(rr.meta_data.reference_point_lat, 50.78232943792871) and \
            math.isclose(rr.meta_data.reference_point_lon, 6.070376552691796):
        # Süsterfeldstr. - Kühlwetterstr. (Location 1)
        return 50
    return None


def _to_auto(rr: omega_format.ReferenceRecording, world: owlready2.World, scene_number=None):
    """
    Main converter function - converts all instances within the reference recording to A.U.T.O. instances. Uses the
    monkey-patched converter functions.
    :param rr: The reference recording to convert from.
    :param world: The owlready2 world to convert into.
    :param scene_number: Whether to only convert a specific scene # (if None, converts all scenes modulo downsampling
    rate)
    """
    # Creates and populates scene for every time point
    scenes = []

    speed_limit = _get_speed_limit(rr)

    for s, t in enumerate(rr.timestamps.val):
        if s == scene_number:
            logger.debug("Scene " + str(s + 1) + "/" + str(len(rr.timestamps.val)))

            # Create scene
            time = auto.get_ontology(auto.Ontology.Time, world).TimePosition()
            sequence = auto.get_ontology(auto.Ontology.Time, world).TimePosition()
            time.numericPosition = [float(t)]
            sequence.numericPosition = [s]
            scene = auto.get_ontology(auto.Ontology.Traffic_Model, world).Scene()
            scene.inTimePosition.append(time)
            scene.inTimePosition.append(sequence)
            scene.has_speed_limit = speed_limit
            if len(scenes) > 0:
                scene.after = [scenes[-1]]

            # Convert road users
            road_users_s = [x for x in {k: v for k, v in rr.road_users.items()}.items() if x[1].birth <= s <= x[1].end]
            logger.debug("Converting " + str(len(road_users_s)) + " road users")
            for i, road_user in road_users_s:
                user_instances = road_user.to_auto(world, scene, i)
                road_user.owl_entity = user_instances
                _add_identity_information(user_instances)

            # Convert misc objects
            misc_objects_s = [x for x in {k: v for k, v in rr.misc_objects.items()}.items() if x[1].birth <= s <=
                              x[1].end]
            logger.debug("Converting " + str(len(misc_objects_s)) + " misc entities")
            for i, misc in misc_objects_s:
                misc_instances = misc.to_auto(world, scene, i)
                _add_identity_information(misc_instances)

            # Convert traffic sign states
            logger.debug("Converting " + str(len(rr.states.values())) + " traffic sign states")
            for traffic_sign_state in rr.states.values():
                state_s = traffic_sign_state.values[s]
                state_instances = state_s.to_auto(world, scene)
                _add_identity_information(state_instances)

            # Convert weather
            logger.debug("Converting weather")
            weather_instances = rr.weather.to_auto(world, scene)
            _add_identity_information(weather_instances)

            # Set correct relations between created entities in case those were not settable during time of creation
            for i, entity in road_users_s + misc_objects_s:
                if entity.last_owl_instance[0].in_scene[0] == scene:
                    if hasattr(entity, "owl_relations"):
                        for rel in entity.owl_relations:
                            if rel[1] == "connected_to":
                                rel[0].connected_to = entity.last_owl_instance
                        entity.owl_relations = []
                else:
                    logger.warning("Found traffic entity " + str(entity) + " that was not converted during scene!")

            scenes.append(scene)

    # Convert static infrastructure, same for every scene (at the end as we need to link against all scenes)
    logger.debug("Converting " + str(len(rr.roads.values())) + " roads")
    for i, road in enumerate(rr.roads.values()):
        road_instances = road.to_auto(world, scenes, i)
        # Road instances can be conveniently handled when merging to avoid creating multiple instances
        for ri in road_instances:
            for ri_list in ri[1]:
                ri_list.is_persistent = True
                if hasattr(ri_list, "hasGeometry"):
                    for geo in ri_list.hasGeometry:
                        geo.is_persistent = True

    # Extra iteration over all scenes for sign states as they can only be created after road infrastructure
    for scene in scenes:
        for sign_state in rr.states.values():
            sign_state.to_auto(world, scene)

    # Store temporal information on scenario
    if len(scenes) > 0 and scene_number is None:
        scenario = auto.get_ontology(auto.Ontology.Traffic_Model, world).Scenario()
        scenario.hasBeginning = [scenes[0]]
        scenario.hasEnd = [scenes[-1]]
        scenario_duration = auto.get_ontology(auto.Ontology.Time, world).Duration()
        scenario_duration.numericDuration = [scenes[-1].inTimePosition[0].numericPosition[0] -
                                             scenes[0].inTimePosition[0].numericPosition[0]]
        scenario.hasDuration = [scenario_duration]
        for scene in scenes:
            scenario.has_traffic_model.append(scene)

    # Remove scene index number from time information as it can lead to confusion of the reasoner (temporal rules)
    for scene in scenes:
        scene.inTimePosition = [scene.inTimePosition[0]]

    # Final step: Set references to relations correctly
    for rr_inst in list(rr.road_users.values()) + list(rr.misc_objects.values()) + list(rr.roads.values()) + \
                   list(rr.states.values()) + list(rr.states.values()) + [l for ll in rr.roads.values() for l in ll]:
        # TODO add more rr instances here?
        instantiate_relations(rr_inst)

    # Bonus: remove actors within parking vehicles as they should not have actors.
    l2_de = auto.get_ontology(auto.Ontology.L2_DE, world)
    l4_core = auto.get_ontology(auto.Ontology.L4_Core, world)
    for vehicle in world.search(type=l4_core.Vehicle):
        if vehicle.has_velocity_x is not None and vehicle.has_velocity_y is not None and \
                vehicle.has_velocity_z is not None:
            speed = math.sqrt(vehicle.has_velocity_x ** 2 + vehicle.has_velocity_y ** 2 + vehicle.has_velocity_z ** 2)
            if math.isclose(speed, 0) and len(vehicle.INVERSE_drives) > 0:
                for parking_space in world.search(type=l2_de.Parking_Space):
                    if hasattr(parking_space, "hasGeometry") and len(parking_space.hasGeometry) > 0:
                        geo_vehicle = wkt.loads(vehicle.hasGeometry[0].asWKT[0])
                        geo_parking_space = wkt.loads(parking_space.hasGeometry[0].asWKT[0])
                        if geo_vehicle.intersects(geo_parking_space):
                            if len(vehicle.INVERSE_drives) > 1:
                                for obs in vehicle.INVERSE_drives:
                                    obs.drives.remove(vehicle)
                            else:
                                owlready2.destroy_entity(vehicle.INVERSE_drives[0])

    logger.debug("Finished converting OMEGA to OWL")


def convert(omega_file="inD.hdf5", onto_path="auto/ontology", cp=False) -> list:
    """
    Main entry function for OMEGA to A.U.T.O. conversion.
    :param omega_file: the HDF5 file to load the OMEGA data from.
    :param onto_path: The path to the folder in which A.U.T.O. is located.
    :param cp: Whether to also load the two criticality phenomena ontologies (needed for criticality inference).
    :return: The scenarios as extracted by the OMEGA library from the HDF5 file as a list of owlready2 worlds.
    """
    worlds = []
    logger.debug("Extracting snippets from OMEGA file")
    snippets = list(filter(lambda x: (x.timestamps.val[-1] - x.timestamps.val[0]) <= MAX_SCENARIO_DURATION,
                           _load_hdf5(omega_file).extract_snippets()))[:1]  # TODO debug, remove
    for i, rr in enumerate(snippets):
        logger.debug("Creating OWL world for snippet " + str(i + 1) + "/" + str(len(snippets)) + " (" +
                     str(str(rr.timestamps.val[0])) + "s - " + str(str(rr.timestamps.val[-1])) + "s)")
        number_of_scenes = min(MAX_SCENES_PER_SCENARIO, len(rr.timestamps.val))
        if number_of_scenes > 1:
            scene_jumps = (len(rr.timestamps.val) - 1) // (number_of_scenes - 1)
        else:
            scene_jumps = 1
        brave_new_worlds = [owlready2.World(
            filename=os.path.join(tempfile.gettempdir(), next(tempfile._get_candidate_names())))
            for _ in range(number_of_scenes)]
        scene_number = 0
        for brave_new_world in brave_new_worlds:
            if cp:
                auto.load_cp(onto_path, brave_new_world)
            else:
                auto.load(onto_path, brave_new_world)
            if scene_number == 0:
                logger.debug("Size of TBox: " + str(len([x for x in brave_new_world.graph._iter_triples()])) +
                             " triples")
            _to_auto(rr, brave_new_world, scene_number=scene_number)
            scene_number += scene_jumps
        worlds.append(brave_new_worlds)
    return worlds
