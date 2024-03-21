import logging
import os
import sys
import re
import timeit
import owlready2
from pyauto import auto
import owlready2_augmentator
from auto_extensions import time, perception, physics, l1_core, l1_de, l4_core
from . import world_merger
from . import temporal_reduction

logger = logging.getLogger(__name__)


def reason_scenario(scenario: list, pellet_output=False, no_reasoning=False, scenario_number=0) -> owlready2.World:
    """
    Augments and reasons on the given scenario (in-place). The main algorithm to infer the presence of criticality
    phenomena.
    :param scenario: A list of worlds, each world representing a single scene.
    :param pellet_output: Whether to show the output of Pellet (can be quite long sometimes, but this will also supress
    errors!).
    :param no_reasoning: Whether to actually perform augmentation and reasoning steps. Can be used for 'dry-runs'.
    :param scenario_number: The identifier of the scenario as an integer (useful if the scenario comes in a sequence of
    scenarios and needs to be distinguished later on).
    :return: A world containing the fully merged and reasoned / augmented scenario.
    """
    t1 = timeit.default_timer()
    if not no_reasoning:
        # Reasoning on every scene
        for i, scene_world in enumerate(scenario):
            logger.debug("Criticality reasoning on scene " + str(i + 1) + "/" + str(len(scenario)))
            _reason(scene_world, pellet_output=pellet_output)

    # Merging inferred worlds & re-adding temporal individual identity information
    logger.debug("Merging scene worlds into a single scenario world")
    for i, scene_world in enumerate(scenario[1:]):
        logger.debug("Merging scene world " + str(i + 2) + " into scene world 1")
        world_merger.merge(scenario[0], scene_world, add_temporal_identity=False)

    # Destroying large ontologies in the scene worlds (some will remain because of global references)
    for scene_world in scenario[1:]:
        for ont in set(scene_world.ontologies.values()):
            try:
                ont.destroy()
            except KeyError:
                logger.warning("Could not delete ontology " + str(ont) + ".")

    # Create scenario in world
    merged_scenario = scenario[0]
    world_merger.add_temporal_identity(merged_scenario)
    tm = auto.get_ontology(auto.Ontology.Traffic_Model, merged_scenario)
    ti = auto.get_ontology(auto.Ontology.Time, merged_scenario)
    scenes = merged_scenario.search(type=tm.Scene)
    scenes.sort(key=lambda x: x.inTimePosition[0].numericPosition[0])
    for i in range(len(scenes) - 1):
        scenes[i].before = [scenes[i + 1]]
        scenes[i + 1].after = [scenes[i]]
    scenario_inst = tm.Scenario()
    scenario_inst.identifier = scenario_number
    scenario_inst.hasBeginning = [scenes[0]]
    scenario_inst.hasEnd = [scenes[-1]]
    scenario_duration = ti.Duration()
    scenario_duration.numericDuration = [scenes[-1].inTimePosition[0].numericPosition[0] -
                                         scenes[0].inTimePosition[0].numericPosition[0]]
    scenario_inst.hasDuration = [scenario_duration]
    for scene in scenes:
        scenario_inst.has_traffic_model.append(scene)

    # Reduce scenario to temporal individuals only as to create a manageable ABox
    logger.debug("Reducing ABox to temporal concepts only")
    logger.debug("Full scenario individuals: " + str(len(list(merged_scenario.individuals()))))
    # Get functions which will be used for augmentation (to not remove any temporal concepts that they may rely on)
    aug_concepts = set()
    for onto in merged_scenario.ontologies.values():
        for cls in onto.classes():
            for func in vars(cls).values():
                if hasattr(func, "_used_concepts"):
                    concepts = getattr(func, "_used_concepts")
                    if concepts and isinstance(concepts, set):
                        aug_concepts = aug_concepts.union(concepts)
    undos, aug_undos = temporal_reduction.reduce(merged_scenario, aug_concepts)
    logger.debug("Reduced scenario individuals: " + str(len(list(merged_scenario.individuals()))))

    # Reasoning on complete scenario for temporal inference
    if not no_reasoning:
        logger.debug("Performing temporal criticality reasoning on scenario")
        aug_undos = _reason(merged_scenario, aug_undos, pellet_output)

    # Restore scenario
    for undo, individual in reversed(undos + aug_undos):
        # Final undo: Undoing deletion of individual
        try:
            undo()
        except:
            pass
        # Hacky bugfix, Python seems to cache some properties badly... We need to call __getattr__, otherwise the
        # cached properties will be used (which may be empty because of the previous deletion).
        for prop in individual.__dict__.keys():
            if individual.namespace.world._props.get(prop):
                try:
                    getattr(individual, "__getattr__")(prop)
                except TypeError:
                    pass
                    # TODO this seems not to impact anything (i.e. properties are there). investigate further.
                    # logger.error("Undo deletion: Not in graph: " + str(individual) + "." + str(prop))
        # Store for later undoing

    # Get all individuals with some geometrical representation.
    geometrical_individuals = list(filter(lambda x: hasattr(x, "hasGeometry") and len(x.hasGeometry) > 0,
                                          merged_scenario.individuals()))

    # Check if individual has multiple geometries after merge resulting from multiple time slices.
    # If so, do undo the undo.
    def natural_sort_key(s, _nsre=re.compile("([0-9]+)")):
        return [int(text) if text.isdigit() else text.lower() for text in _nsre.split(str(s))]
    for individual in geometrical_individuals:
        if len(individual.hasGeometry) > 1:
            for geom in sorted(individual.hasGeometry, key=natural_sort_key)[1:]:
                try:
                    owlready2.destroy_entity(geom)
                except:
                    pass

    logger.debug("Restored full scenario individuals: " + str(len(list(merged_scenario.individuals()))))
    logger.debug("Fully finished criticality reasoning on scenario. Took %.2f s" % (timeit.default_timer() - t1))

    return merged_scenario


def _reason(world: owlready2.World, aug_undos=None, pellet_output=False) -> list:
    """
    Augments the ABox & runs the Pellet reasoner on the given world. Can handle both scenes and scenarios, i.e. it
    checks whether there is a scenario (then, we run temporal scenario reasoning), or a scene in the world (then we run
    scene reasoning).
    :param world: The world containing a scenario or scene to augment and reason on.
    :param aug_undos: Only for scenario reasoning: If you have previously reduced the ABox by using the temporal
    reductions, you can pass the set of undo methods. This allows to restore the ABox to its non-reduced state
    and perform augmentation on this state (since reduction might reduce concrete information that are needed for
    augmentation). Before reasoning, we obviously use a reduced ABox.
    :param pellet_output: Whether to show the output of Pellet.
    :return: A list of undo methods that shall be executed in reverse order to restore the previous state.
    """
    # Fetch relevant ontologies
    tm = auto.get_ontology(auto.Ontology.Traffic_Model, world)
    ph = auto.get_ontology(auto.Ontology.Physics, world)
    pe = auto.get_ontology(auto.Ontology.Perception, world)
    ti = auto.get_ontology(auto.Ontology.Time, world)
    ac = auto.get_ontology(auto.Ontology.Act, world)
    l1core = auto.get_ontology(auto.Ontology.L1_Core, world)
    l1de = auto.get_ontology(auto.Ontology.L1_DE, world)
    l2de = auto.get_ontology(auto.Ontology.L2_DE, world)
    l4core = auto.get_ontology(auto.Ontology.L4_Core, world)
    l4de = auto.get_ontology(auto.Ontology.L4_DE, world)

    # Register loaded ontologies to augmentations
    perception.register(perception=pe)
    physics.register(physics=ph)
    time.register(time=ti)
    l1_core.register(l1_core=l1core, l4_core=l4core, l4_de=l4de)
    l1_de.register(l1_de=l1de, l1_core=l1core, l4_de=l4de)
    l4_core.register(l4_core=l4core, l4_de=l4de, l2_de=l2de, physics=ph, time=ti)

    # bugfix for owlready2 bug - creates storid for inferences ontology so that it will not be created when applying
    # reasoning results. then, this storid may be one of the storids of the cleaned up individuals which leads to a
    # crash after undoing their deletion.
    world.get_ontology("http://inferrences/")

    # Run reasoner & perform augmentation
    augmentation = True
    c = 0
    single_scene = len(world.search(type=tm.Scenario)) == 0

    while augmentation:
        c += 1
        logger.debug("Cleaning up A-Box before criticality reasoning...")
        # inferences into ontology
        cleanup_undos = _cleanup_abox_for_reasoning(world)
        logger.debug("Criticality reasoning iteration #" + str(c) + "...")
        # Reasoner
        t1 = timeit.default_timer()
        if not pellet_output:
            sys.stderr = open(os.devnull, "w")
            sys.stdout = open(os.devnull, "w")
        owlready2.sync_reasoner_pellet(world, infer_property_values=True)  # set debug=2 for explanation if inconsistent
        if not pellet_output:
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__
        t2 = timeit.default_timer()
        logger.debug("Criticality reasoning iteration #" + str(c) + " done. Took %.2f s" % (t2 - t1))
        logger.debug("Restoring cleaned up A-Box...")
        for undo, individual in reversed(cleanup_undos):
            try:
                undo()
            except:
                pass
            for prop in individual.__dict__.keys():
                if individual.namespace.world._props.get(prop):
                    try:
                        getattr(individual, "__getattr__")(prop)
                    except TypeError:
                        pass
        logger.debug("Augmentation iteration #" + str(c) + "...")

        # Augmentations
        # First, restore anything that may be necessary to perform (temporal) augmentations - will later be un-undone
        # for reasoning (as to not blow up the ABox)
        if aug_undos:
            for undo, individual in reversed(aug_undos):
                # Reasoning iteration: Undoing deletion of individual
                try:
                    undo()
                except:
                    pass
                for prop in individual.__dict__.keys():
                    if individual.namespace.world._props.get(prop):
                        try:
                            getattr(individual, "__getattr__")(prop)
                        except TypeError:
                            pass
                            # TODO this seems not to impact anything (i.e. properties are there). investigate further.
                            # logger.error("Undo deletion: Not in graph: " + str(individual) + "." + str(prop))
        logger.debug("Size of ABox before augmentation: " + str(len([x for x in world.graph._iter_triples()])) +
                     " triples")
        t3 = timeit.default_timer()

        augmentation, new_individuals = owlready2_augmentator.do_augmentation(ph, pe, l4core, ti, l1core, l1de)

        # Remove previously re-added individuals since they have now been used in augmentations and can safely be
        # deleted
        if aug_undos:
            new_aug_undos = []
            for undo, individual in aug_undos:
                # Reasoning iteration: Destroying individual
                try:
                    new_aug_undo = owlready2.destroy_entity(individual, undoable=True)
                    new_aug_undos.append((new_aug_undo, individual))
                except:
                    pass
            aug_undos = new_aug_undos
        # Add augmented entities to scene or scenario
        if single_scene:
            world.search(type=tm.Scene)[0].has_traffic_entity = world.search(type=tm.Scene)[0].has_traffic_entity + \
                                                                list(new_individuals)
        else:
            scenario = world.search(type=tm.Scenario)[0]
            for new_individual in new_individuals:
                if isinstance(new_individual, ac.Activity):
                    scenario.has_traffic_entity.append(new_individual)
                else:
                    logger.warning("Augmented scenario with individual that is not an activity: " + str(new_individual))
        t4 = timeit.default_timer()
        # Print debug information
        logger.debug("Size of ABox after augmentation : " + str(len([x for x in world.graph._iter_triples()])) +
                     " triples")
        logger.debug("Augmentation iteration #" + str(c) + " done. Took %.2f s" % (t4 - t3))
        logger.debug("Iteration #" + str(c) + " done. Took %.2f s" % (t4 - t1))

    return aug_undos


def _cleanup_abox_for_reasoning(world) -> list:
    """
    This helper method reduces the ABox before reasoning on each scene based on the owlready2 `destroy_entity` method.
    It can be very useful to avoid memory problems if one knows a-priori that certain classes can be ignored for
    scene-level reasoning. Right now, we remove every individual of the class GeoSPARQL.Geometry.
    :param world: The scene world to reduce.
    :return: A list of undo methods that shall be executed in reverse order to restore the previous state.
    """
    # Adjust this set to add more classes whose individuals shall be removed before scene reasoning.
    clean_clss = {auto.get_ontology(auto.Ontology.GeoSPARQL, world).Geometry}
    undos = []
    individuals = [x for x in world.individuals() if len(set(x.INDIRECT_is_a).intersection(clean_clss)) > 0]
    for individual in individuals:
        try:
            undo = owlready2.destroy_entity(individual, undoable=True)
            undos.append((undo, individual))
        except:
            pass
    return undos
