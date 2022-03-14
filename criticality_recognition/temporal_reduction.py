import logging
import owlready2

from auto import auto

logger = logging.getLogger(__name__)


def reduce(world: owlready2.World, augmentation_concepts=None):
    """
    Removes all individuals from the ABox of the world which rely on only concepts that are not used in a temporal
    criticality phenomenon. Returns a dict of undo functions to revert the reduction.
    :world: The world with the ABox to reduce.
    :augmentation_concepts: The concepts with which temporal augmentations will rely on.
    """
    temporal_concepts = _get_temporal_concepts(world)
    tm = auto.get_ontology(auto.Ontology.Traffic_Model, world)
    ti = auto.get_ontology(auto.Ontology.Time, world)
    global_temporal_concepts = {tm.Scenario, tm.Scene, ti.TimePosition, ti.Duration}
    temporal_concepts = temporal_concepts.union(global_temporal_concepts)
    logger.debug("Identified the following temporal concepts in CP formalization: " + str(temporal_concepts))
    logger.debug("Identified the following augmentation concepts: " + str(augmentation_concepts))
    temporal_individuals = _get_temporal_individuals(world, temporal_concepts)
    if augmentation_concepts:
        temporal_augmentation_individuals = _get_temporal_individuals(world, augmentation_concepts)
    else:
        temporal_augmentation_individuals = set()
    logger.debug("Satisfied by " + str(len(temporal_individuals)) + " individuals: " + str(temporal_individuals))
    undos = []
    aug_undos = []
    for individual in (temporal_augmentation_individuals - temporal_individuals):
        undo = owlready2.destroy_entity(individual, undoable=True)
        aug_undos.append((undo, individual))
    for individual in (set(world.individuals()) - temporal_individuals):
        undo = owlready2.destroy_entity(individual, undoable=True)
        undos.append((undo, individual))
    return undos, aug_undos


def _get_temporal_concepts(world: owlready2.World) -> set:
    """
    Fetches all classes, data and object properties that are used within the definition (equivalence or subclass) of
    some temporal criticality phenomenon. Also regards SWRL rules.
    :param world: World to get temporal concepts in.
    :return: A set of temporal concepts (classes, data and object properties) in the world.
    """
    concepts = set()
    # Fetch relevant ontologies
    ac = auto.get_ontology(auto.Ontology.Act, world)
    ti = auto.get_ontology(auto.Ontology.Time, world)
    cp = auto.get_ontology(auto.Ontology.Criticality_Phenomena, world)
    cp_form = auto.get_ontology(auto.Ontology.Criticality_Phenomena_Formalization, world)
    cp_cls = set(world.search(subclass_of=cp.Criticality_Phenomenon))
    ac_cls = set(world.search(subclass_of=ac.Activity))
    in_cls = set(world.search(subclass_of=ti.Interval))
    temporal_cps = cp_cls.intersection(ac_cls.union(in_cls))
    for temporal_cp in temporal_cps:
        # First, check if SWRL rules are available for this CP.
        for rule in world.rules():
            if len(rule.head) == 1 and hasattr(rule.head[0], "is_a") and owlready2.swrl.ClassAtom in rule.head[0].is_a \
                    and rule.head[0].class_predicate == temporal_cp:
                for concept in rule.body:
                    if owlready2.swrl.ClassAtom in concept.is_a:
                        concepts.add(concept.class_predicate)
                    elif owlready2.swrl.IndividualPropertyAtom in concept.is_a:
                        concepts.add(concept.property_predicate)
        # Secondly, check if OWL equivalences or sub-classifications are available for this CP.
        if len(temporal_cp.equivalent_to) > 0:
            concepts = concepts.union(set(temporal_cp.equivalent_to))
        else:
            concepts = concepts.union(set(filter(lambda x: not isinstance(x, owlready2.entity.ThingClass) or
                                                 (x.namespace != cp and x.namespace != cp_form), temporal_cp.is_a)))
    # Recursively identify all sub-concepts
    res = set([x for concept in concepts for x in _get_sub_concepts_from_axiom(concept or [])])
    return set(res)


def _get_sub_concepts_from_axiom(axiom) -> set:
    """
    Recursively searches for basic concepts within a possibly complex axiom.
    :param axiom: The axiom to analyze.
    :return: A set of all concepts used within an axiom.
    """
    if isinstance(axiom, owlready2.entity.ThingClass) or isinstance(axiom, owlready2.prop.ObjectPropertyClass) \
            or isinstance(axiom, owlready2.prop.DataPropertyClass):
        return {axiom}
    elif hasattr(axiom, "Classes"):
        res = set()
        for cls in axiom.Classes:
            res = res.union(_get_sub_concepts_from_axiom(cls))
        return res
    elif hasattr(axiom, "Class"):
        return _get_sub_concepts_from_axiom(axiom.Class)
    elif hasattr(axiom, "value"):
        return _get_sub_concepts_from_axiom(axiom.value)
    else:
        return set()


def _get_temporal_individuals(world: owlready2.World, temporal_concepts: set) -> set:
    """
    Fetches all individuals within the world which are directly related (in the graph) to some temporal concept.
    :param world: World to get individuals from
    :return: A set of all individuals within the world that are related to a temporal concept.
    """
    def filter_func(y):
        concepts = set()
        for axiom in y.INDIRECT_is_a + list(y.get_properties()):
            concepts = concepts.union(_get_sub_concepts_from_axiom(axiom))
        return len(concepts.intersection(temporal_concepts)) > 0
    return set(filter(filter_func, set(world.individuals())))
