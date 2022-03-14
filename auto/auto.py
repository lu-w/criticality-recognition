import owlready2
import os
import logging
from enum import Enum

"""
Loads A.U.T.O. globally into owlready2. Also provides an easier enum interface to access the sub-ontologies of A.U.T.O.
"""

logger = logging.Logger(__name__)


class Ontology(Enum):
    """
    Contains an enumeration of all sub-ontologies of A.U.T.O. pointing to their IRIs.
    """
    Criticality_Phenomena = "http://purl.org/auto/criticality_phenomena#"
    Criticality_Phenomena_Formalization = "http://purl.org/auto/criticality_phenomena_formalization#"
    Traffic_Model = "http://purl.org/auto/traffic_model#"
    Physics = "http://purl.org/auto/physics#"
    Perception = "http://purl.org/auto/perception#"
    Time = "http://www.w3.org/2006/time#"
    Act = "http://purl.org/auto/act#"
    GeoSPARQL = "http://www.opengis.net/ont/geosparql#"
    L1_Core = "http://purl.org/auto/l1_core#"
    L1_DE = "http://purl.org/auto/l1_de#"
    L2_Core = "http://purl.org/auto/l2_core#"
    L2_DE = "http://purl.org/auto/l2_de#"
    L3_Core = "http://purl.org/auto/l3_core#"
    L3_DE = "http://purl.org/auto/l3_de#"
    L4_Core = "http://purl.org/auto/l4_core#"
    L4_DE = "http://purl.org/auto/l4_de#"
    L5_Core = "http://purl.org/auto/l5_core#"
    L5_DE = "http://purl.org/auto/l5_de#"
    L6_Core = "http://purl.org/auto/l6_core#"
    L6_DE = "http://purl.org/auto/l6_de#"


def get_ontology(ontology: Ontology, world: owlready2.World) -> owlready2.Ontology:
    """
    Can be used to fetch a specific sub-ontology of A.U.T.O. from a given world. Also handles the case of saving and
    re-loading ontologies into owlready2, where (due to import aggregation into a single ontology), ontologies were
    merged but namespaces remain.
    :param ontology: The ontology to fetch.
    :param world: The world to search for the ontology.
    :return: The ontology object corresponding to the given ontology.
    """
    iri = ontology.value
    if world.ontologies and iri in world.ontologies.keys():
        return world.ontologies[iri]
    else:
        return world.get_ontology("http://anonymous#").get_namespace(iri)


def load(folder="auto/ontology", world=None):
    """
    Loads A.U.T.O. from a given folder location.
    :param folder: The folder to look for, should contain the `automotive_urban_traffic_ontology.owl`.
    :param world: The world to load A.U.T.O. into. If None, loads into the default world.
    :raise FileNotFoundError: if given an invalid folder location.
    """
    if os.path.isdir(folder):
        # Setting correct path for owlready2
        for i, j, k in os.walk(folder + "/"):
            owlready2.onto_path.append(i)
        owlready2.onto_path.remove(folder + "/")
        # Loading ontology into world (or default world)
        if not world:
            world = owlready2.default_world
        world.get_ontology(folder + "/automotive_urban_traffic_ontology.owl").load()
    else:
        raise FileNotFoundError(folder)


def load_cp(folder="auto/ontology", world=None):
    """
    Loads A.U.T.O. along with the criticality phenomena ontologies (vocabulary, formalization) from a given folder
    location.
    :param folder: The folder to look for, should contain the `automotive_urban_traffic_ontology.owl`,
    criticality_phenomena.owl`, `criticality_phenomena_formalization.owl`
    :param world: The world to load A.U.T.O. & CPs into. If None, loads into the default world.
    :raise FileNotFoundError: if given an invalid folder location.
    """
    if os.path.isdir(folder):
        # Setting correct path for owlready2
        for i, j, k in os.walk(folder + "/"):
            owlready2.onto_path.append(i)
        owlready2.onto_path.remove(folder + "/")
        # Loading ontology into world (or default world)
        if not world:
            world = owlready2.default_world
        world.get_ontology(folder + "/automotive_urban_traffic_ontology.owl").load()
        world.get_ontology(folder + "/criticality_phenomena.owl").load()
        world.get_ontology(folder + "/criticality_phenomena_formalization.owl").load()
    else:
        raise FileNotFoundError(folder)

