import logging
import tqdm
import owlready2
from owlready2.reasoning import _INFERRENCES_ONTOLOGY
import rdflib
from rdflib import RDF, OWL

logger = logging.getLogger(__name__)

# Predicates that shall not be considered during merging of two worlds.
_UNWANTED_PREDICATES = {"http://purl.org/auto/traffic_model#identical_to"}


def merge(world1: owlready2.World, world2: owlready2.World, add_temporal_identity=False, ignore_persistency=False):
    """
    Merges ABoxes of the two worlds world1 and world2. Optionally regards the special 'identical_to' relation to track
    temporal identity over time.
    :param world1: The world to merge into.
    :param world2: The world to merge.
    :param add_temporal_identity: Whether to restore temporal identity information within the merged world.
    :param ignore_persistency: Whether to ignore persistency among world individuals.
    """
    ontology1 = world1.get_ontology(_INFERRENCES_ONTOLOGY)
    ontology2 = world2.get_ontology(_INFERRENCES_ONTOLOGY)
    individuals = {}  # A dict of 'old' (world 2) iris to newly created individual objects (in world 1)
    world1.graph.acquire_write_lock()

    # Prepares logging
    if logger.level == logging.DEBUG:
        search_space = tqdm.tqdm(list(world2.individuals()))
    else:
        search_space = world2.individuals()

    # Actual merging
    # We first CREATE all the individuals by calling their constructors in the other world. For this we need to fetch
    # the correct classes and set the newly created individual's is_a relation correctly.
    for individual in search_space:
        if (ignore_persistency or not hasattr(individual, "is_persistent") or not individual.is_persistent) and \
                individual.namespace.base_iri in world1.ontologies.keys():
            cls = getattr(world1.ontologies[individual.__class__.namespace.base_iri], individual.__class__.__name__)
            if not cls:
                cls = []
                for c in individual.__class__.__bases__:
                    if c.namespace.base_iri in world1.ontologies.keys():
                        cls.append(getattr(world1.ontologies[c.namespace.base_iri], c.__name__))
                subject = cls[0](namespace=world1.ontologies[individual.namespace.base_iri])
                for c in cls[1:]:
                    subject.is_a.append(c)
            else:
                subject = cls(namespace=world1.ontologies[individual.namespace.base_iri])
            individuals[individual.iri] = subject
        # Handle persistent individuals.
        elif not ignore_persistency and hasattr(individual, "is_persistent") and individual.is_persistent:
            # TODO move all properties from identical persistent object in W2 into W1 (e.g. classifications, relations)
            # step 1: search corresponding individual in world 1 (individual_1)
            eq_individuals = list(filter(lambda x: str(x) == str(individual), world1.individuals()))
            if len(eq_individuals) > 0:
                individual_1 = eq_individuals[0]
                # step 2: for all classes in individual.is_a, individual.equivalent to: add to individual_1
                for is_a in individual.is_a:
                    if str(is_a) not in [str(x) for x in individual_1.is_a]:
                        individual_1.is_a.append(is_a)
                        logger.debug("Persistent " + str(individual_1) + ": Add is_a info: " + str(is_a))
                for equivalence in individual.equivalent_to:
                    if equivalence not in individual_1.equivalent_to:
                        individual_1.equivalent_to.append(equivalence)
                        logger.debug("Persistent " + str(individual_1) + ": Add equivalence info: " + str(equivalence))
                # step 3: for all properties of individual: add to individual_1
                props = [str(x._python_name) for x in individual.get_properties()]
                for prop in props:
                    if hasattr(individual, prop) and type(getattr(individual, prop)) is list:
                        old_relations = getattr(individual, prop)
                        # TODO we may need to check if new relations are actually there in world 1?
                        new_relations = getattr(individual_1, prop)
                        setattr(individual_1, prop, old_relations + new_relations)
                        logger.debug("Persistent " + str(individual_1) + ": Add info for property " + prop + ": " +
                                     str(new_relations))
            else:
                logger.warning("Can not find identical individual in world 1 for permanent world 2 individual " +
                               str(individual))

    # Individuals are now created. We then need to add every triple containing the individual either as its subject
    # or object to world 1. Note that some special triples were already considered (namely, the is_a information).
    for individual in world2.individuals():
        if individual.iri in individuals.keys():
            # Adding all triples containing individual as subject
            _add_to_world(ontology1, ontology2, world1, world2, individual.iri, individuals)
            # Adding all triples containing individual as object
            _add_to_world_inv(ontology1, ontology2, world1, world2, individual.iri, individuals)
            # Optional: Setting identical to relation (storing temporal identity)
            # TODO seems buggy on inD. Is currently not used, i.e. replaced by a-posteriori add_temporal_identity().
            if add_temporal_identity:
                for i in individual.identical_to:
                    p_storid = ontology1._abbreviate("http://purl.org/auto/traffic_model#identical_to", False)
                    # Assuming that always the identical individuals are already present in world 1.
                    o_storid = ontology1._abbreviate(i.iri, False)
                    if o_storid is not None:
                        world1._add_triples_with_update(ontology1, [(individuals[individual.iri].storid, p_storid,
                                                        o_storid)])
                    # else: this is fine - in this case, the individual just "appeared" in the world

    world1.graph.release_write_lock()


def add_temporal_identity(scenario: owlready2.World):
    """
    Adds the relation 'identical_to' between all individuals in scenario that have the same identifier (using the data
    property 'identifier').
    :param scenario: The scenario with multiple scenes for whose individuals to add temporal identities between.
    """
    for individual1 in scenario.search(identifier="*"):
        if not isinstance(individual1, owlready2.entity.ThingClass):
            individual1.identical_to = []
            for individual2 in scenario.search(identifier="*"):
                if not isinstance(individual2, owlready2.entity.ThingClass) and individual1 != individual2 and \
                        individual1.identifier[0] == individual2.identifier[0]:
                    individual1.identical_to.append(individual2)


def _add_to_world(ontology1: owlready2.Ontology, ontology2: owlready2.Ontology, world1: owlready2.World,
                  world2: owlready2.World, thing: int, things: dict):
    """
    Helper function for merging. Adds an individual (thing) from world 2 to world 1 by looking at all triples having
    thing as its subject and updating the quad store of world 1 accordingly. The subject shall be created previously
    in world 1 by e.g. using a constructor and stored in the things dictionary, e.g. things[thing] = thing_repr_world2.
    The predicate and objects (that live in world 1) are translated into corresponding quad-store IDs of world 2
    automatically by this method. Note that this functionality is not fully complete, e.g. for BNode types on the right
    side (those are virtual nodes representing e.g. complex axioms). It assumes that the predicates of world 2 are also
    present in  world 1.
    :param ontology1: An ontology of world 1 (needed to fetch quad-store IDs)
    :param ontology2: An ontology of world 2. (needed to fetch quad-store IDs)
    :param world1: The world to add to.
    :param world2: The world to add from.
    :param thing: The thing of world 2 to add world 1.
    :param things: Previously created things (to fetch correct quad-store IDs of previously created things).
    """
    s_storid = ontology2._abbreviate(str(thing), False)
    # Look for all triples that start with the subject (i.e. predicate object combinations) in world 2 and add them to
    # world 1.
    for _, predicate, obj in world2.as_rdflib_graph().triples((s_storid, None, None)):
        if (predicate != RDF.type or obj != OWL.NamedIndividual) and str(predicate) not in _UNWANTED_PREDICATES:
            # Predicate can be fetched easily from world 1.
            p_storid = ontology1._abbreviate(str(predicate), False)
            # Here we go - getting an object ID for world 1 is not so easy. Three cases: URIRef, Literal, BNode.
            o_storid = None
            d = None
            if isinstance(obj, rdflib.term.URIRef):
                # We either created the thing that we point to earlier (it was also merged) or it is just an object
                # present in both worlds, e.g. a constant / static thing.
                if str(obj) in things.keys():
                    o_storid = things[str(obj)].storid
                else:
                    o_storid = ontology1._abbreviate(obj, False)
                if o_storid is None:
                    # TODO check if this occurs in the test cases.
                    logger.warning("Object in triple not found during merge: " + str(thing) + " --" + str(predicate) +
                                   "--> " + str(obj))
            elif isinstance(obj, rdflib.term.Literal):
                if obj.language is None:
                    if obj.datatype:
                        d = ontology1._abbreviate(str(obj.datatype))
                        if isinstance(obj.value, bool):
                            o_storid = str(obj)
                        elif isinstance(obj.value, (int, float)):
                            o_storid = obj.value
                        else:
                            o_storid = str(obj)
                    else:
                        d = 0
                        o_storid = str(obj)
                else:
                    d = "@%s" % obj.language
                    o_storid = str(obj)
            elif isinstance(obj, rdflib.term.BNode):
                # TODO implement merger for BNode types
                logger.warning("Found BNode type during world merge - not implemented yet: " + str(thing) + " --" +
                               str(predicate) + "--> " + str(obj))
            # We finally found an object storage ID!
            # Note: parents in "is_a" were added already previously. Do not add again (second constraint)
            if o_storid is not None and \
                    (o_storid not in [x.storid for x in things[thing].is_a] and predicate != RDF.type):
                world1._add_triples_with_update(ontology1, [(things[thing].storid, p_storid, o_storid, d)])


def _add_to_world_inv(ontology1: owlready2.Ontology, ontology2: owlready2.Ontology, world1: owlready2.World,
                      world2: owlready2.World, thing: int, things: dict):
    """
    The inverse of the _add_to_world method. Looks at all triples containing the individual (thing) as its object. For
    more documentation, please refer to _add_to_world.
    :param ontology1: An ontology of world 1 (needed to fetch quad-store IDs)
    :param ontology2: An ontology of world 2. (needed to fetch quad-store IDs)
    :param world1: The world to add to.
    :param world2: The world to add from.
    :param thing: The thing of world 2 to add world 1.
    :param things: Previously created things (to fetch correct quad-store IDs of previously created things).
    """
    o_storid = ontology2._abbreviate(str(thing), False)
    # Look for all triples that end with the object (i.e. subject predicate combinations) in world 2 and add them to
    # world 1.
    for subject, predicate, _ in world2.as_rdflib_graph().triples((None, None, o_storid)):
        if str(predicate) not in _UNWANTED_PREDICATES:
            p_storid = ontology1._abbreviate(str(predicate), False)
            s_storid = None
            d = None
            # Cases: URIRef & Bnode. Note that here, we can ignore Literals as they are assumed to be always on the
            # right hand side.
            if isinstance(subject, rdflib.term.URIRef):
                if str(subject) in things.keys():
                    s_storid = things[str(subject)].storid
                else:
                    s_storid = ontology1._abbreviate(subject, False)
                if s_storid is None:
                    # TODO check if this occurs in the test cases.
                    logger.warning("Subject in triple not found during merge: " + str(subject) + " --" + str(predicate)
                                   + "--> " + str(thing))
            elif isinstance(subject, rdflib.term.BNode):
                # TODO implement merger for BNode types
                logger.warning("Found BNode type during world merge - not implemented yet: " + str(subject) + " --" +
                               str(predicate) + "--> " + str(thing))
            if s_storid is not None:
                world1._add_triples_with_update(ontology1, [(s_storid, p_storid, things[thing].storid, d)])
