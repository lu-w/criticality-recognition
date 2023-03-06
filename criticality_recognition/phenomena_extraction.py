import logging
import owlready2
import tqdm

from pyauto import auto

logger = logging.getLogger(__name__)

_CACHED_CP_CLASSES = dict()


class Criticality_Phenomenon:

    def __init__(self, traffic_model, cp, cp_cls, objects=None):
        """
        Constructor for criticality phenomena. Information about criticality phenomena are stored as follows:
        - traffic_model: The scene or scenario in which the CP occurs.
        - cp: The CP individual from the ontology (owlready2 object).
        - cp_cls: The class of the criticality phenomenon from the ontology (owlready2 class).
        - time: Either an interval tuple (start, end) or a time point as float.
        - subjects: A list of subjects (individuals within the ontology) of the CP.
        - objects: A dictionary mapping object properties to lists of objects (individuals within the ontology), e.g.
          {"prop1": [obj1, obj2], "prop2": [obj2, obj3]}.
        :param traffic_model: The scene or scenario in which the criticality phenomenon occurs.
        :param cp: An individual from the ABox that is a criticality phenomenon
        :param cp_cls: The class of the TBox of the criticality phenomenon (i.e. of cp)
        :param objects: If the objects of the criticality phenomenon were already extracted previously, they can be
        passed here as a dict, assigning each object property (str) a list of objects, e.g. {"prop1": [obj1, obj2],
        "prop2": [obj2, obj3]}. If None is given, objects will be extracted in the constructor.
        """
        self.traffic_model = traffic_model
        self.cp = cp
        self.cp_cls = cp_cls
        self.time = 0
        ac = auto.get_ontology(auto.Ontology.Act, self.cp.namespace.world)
        # Subjects
        if len(self.cp_cls.subject_extraction_code) > 0:
            try:
                local_dict = {"subject": self.cp, "subjects": []}
                exec(self.cp_cls.subject_extraction_code[0], globals(), local_dict)
                self.subjects = local_dict["subjects"] or []
            except Exception as e:
                logger.error("Invalid subject extraction code in OWL during CP extraction of: " + str(self.cp) + " (" +
                             str(self.cp_cls) + "): " + str(e))
                self.subjects = []
        elif ac.Activity in self.cp.INDIRECT_is_a and len(self.cp.conducted_by) > 0:
            self.subjects = self.cp.conducted_by
        else:
            self.subjects = [self.cp]
        # Predicate
        self.predicate = str(self.cp_cls).replace("criticality_phenomena.", "")
        if len(self.cp_cls.label.en) > 0:
            self.predicate += " (" + self.cp_cls.label.en[0] + ")"
        # Objects
        if objects is None and len(self.cp_cls.object_extraction_code) > 0:
            try:
                local_dict = {"subject": self.cp, "objects": []}
                exec(self.cp_cls.object_extraction_code[0], globals(), local_dict)
                self.objects = local_dict["objects"] or []
            except Exception as e:
                logger.error("Invalid object extraction code in OWL during CP extraction of: " + str(self.cp) + " (" +
                             str(self.cp_cls) + "): " + str(e))
                self.objects = []
        elif objects is None and ac.Activity in self.cp.INDIRECT_is_a:
            self.objects = {"participants": self.cp.has_participant}
        else:
            self.objects = objects or dict()

    def __str__(self) -> str:
        """
        Returns a string representation of the criticality phenomenon in the form 't = X: subject(s) -- predicate -->
        object(s)'.
        :return: String representation as described above.
        """
        # Time
        label = "t = " + str(self.at_time()) + ": "
        # Subjects
        if len(self.subjects) > 0:
            subj_and_classes = get_most_specific_classes(self.subjects)
            label += ", ".join([str(x[0]) + " (" + ", ".join(x[1]) + ")" for x in subj_and_classes]) + " -- "
        # Predicate
        label += self.predicate
        # Objects
        for obj_predicate in self.objects.keys():
            obj_and_classes = get_most_specific_classes(self.objects[obj_predicate])
            label += " -- " + obj_predicate + " --> " + ", ".join([str(x[0]) + " (" + ", ".join(x[1]) + ")" for x in
                                                                   obj_and_classes])
        return label

    def to_csv(self) -> str:
        """
        Returns a CSV representation (semicolon-separated) of the criticality phenomenon in the form 'time; predicate;
        subject(s); object(s)'.
        :return: CSV as a string as described above
        """
        # Time
        time = self.at_time()
        if isinstance(time, tuple):
            start, end = time
        else:
            start, end = time, time
        csv_res = str(start) + ";" + str(end) + ";"
        # Predicate
        csv_res += self.predicate + ";"
        # Subjects
        if len(self.subjects) > 0:
            subj_and_classes = get_most_specific_classes(self.subjects)
            csv_res += ", ".join([str(x[0]) + " (" + ", ".join(x[1]) + ")" for x in subj_and_classes])
        csv_res += ";"
        # Objects
        for obj_predicate in self.objects.keys():
            obj_and_classes = get_most_specific_classes(self.objects[obj_predicate])
            csv_res += obj_predicate + ": " + ", ".join([str(x[0]) + " (" + ", ".join(x[1]) + ")" for x in
                                                         obj_and_classes]) + " | "
        if csv_res.endswith(" | "):
            csv_res = csv_res[:-3]
        return csv_res

    def at_time(self):
        """
        Interface: returns the time at which the criticality phenomenon is occurring.
        :return: The time at which self occurs.
        """
        return self.time

    def is_representable_in_scene(self, scene) -> bool:
        """
        Returns True iff the criticality phenomenon is visualizable or representable in a given scene, i.e. iff
        all subjects and objects of the phenomenon are within the scene.
        :param scene: The scene to check against.
        :return: True iff self is representable in scene.
        """
        if len(self.subjects) > 0:
            for subj in self.subjects + [y for x in self.objects.values() for y in x]:
                if scene not in subj.in_traffic_model:
                    return False
            return True
        return False


class Scene_Criticality_Phenomenon(Criticality_Phenomenon):
    """
    Concretization for scene-level criticality phenomena. Note that member traffic_model is a list of scenes.
    """
    def __init__(self, traffic_model: list, cp, cp_cls, objects=None):
        if len(traffic_model) == 0:
            raise ValueError("Scene CP with scenes")
        Criticality_Phenomenon.__init__(self, traffic_model, cp, cp_cls, objects)
        self.time = traffic_model[0].inTimePosition[0].numericPosition[0]


class Scenario_Criticality_Phenomenon(Criticality_Phenomenon):
    """
    Concretization for scenario-level criticality phenomena.
    """
    def __init__(self, traffic_model, cp, cp_cls, objects=None):
        Criticality_Phenomenon.__init__(self, traffic_model, cp, cp_cls, objects)
        if hasattr(self.cp, "hasBeginning") and hasattr(self.cp, "hasEnd") and len(self.cp.hasBeginning) > 0 and \
                len(self.cp.hasBeginning[0].inTimePosition) > 0 and \
                len(self.cp.hasBeginning[0].inTimePosition[0].numericPosition) > 0 and len(self.cp.hasEnd) > 0 and \
                len(self.cp.hasEnd[0].inTimePosition) > 0 and \
                len(self.cp.hasEnd[0].inTimePosition[0].numericPosition) > 0:
            self.time = (self.cp.hasBeginning[0].inTimePosition[0].numericPosition[0],
                         self.cp.hasEnd[0].inTimePosition[0].numericPosition[0])
        else:
            self.time = (self.traffic_model.hasBeginning[0].inTimePosition[0].numericPosition[0],
                         self.traffic_model.hasEnd[0].inTimePosition[0].numericPosition[0])


def phenomena_scenario(scenario: list or owlready2.World) -> list:
    """
    scenario: Either a list of worlds, each world representing a single scene or a single world representing a whole
        scenario
    returns: A list of criticality phenomena objects (either scene or scenario) sorted by temporal occurrence
    """
    cps = []
    if type(scenario) == list:
        for scene in scenario:
            tm = auto.get_ontology(auto.Ontology.Traffic_Model, scene)
            cp_ont = auto.get_ontology(auto.Ontology.Criticality_Phenomena, scene)
            scenes = list(tm.search(type=tm.Scene))
            if len(scenes) > 0:
                for scene_cp in scenario.search(type=cp_ont.Criticality_Phenomenon):
                    scene_cp_obj = Scene_Criticality_Phenomenon(scenes[0], scene_cp, None)  # TODO
                    cps.append(scene_cp_obj)
            else:
                raise ValueError("No scenes found in scene world " + str(scene))

    elif type(scenario) == owlready2.World:
        tm = auto.get_ontology(auto.Ontology.Traffic_Model, scenario)
        ac = auto.get_ontology(auto.Ontology.Act, scenario)
        ti = auto.get_ontology(auto.Ontology.Time, scenario)
        cp_ont = auto.get_ontology(auto.Ontology.Criticality_Phenomena, scenario)
        scenarios = list(scenario.search(type=tm.Scenario))
        if len(scenarios) > 0:
            if logger.level == logging.DEBUG:
                search_space = tqdm.tqdm(list(scenario.search(type=cp_ont.Criticality_Phenomenon)))
            else:
                search_space = scenario.search(type=cp_ont.Criticality_Phenomenon)
            for cp in search_space:
                cp_clss = list(filter(lambda x: x in scenario.classes(),
                                      [y for y in cp.INDIRECT_is_a if hasattr(y, "namespace") and y.namespace.base_iri
                                       == "http://purl.org/auto/criticality_phenomena#"]))
                most_specific_cp_clss = [cp_cls for cp_cls in cp_clss if hasattr(cp_cls, "__subclasses__") and
                                         len(set(cp_cls.__subclasses__()).intersection(set(cp_clss))) == 0]
                for cp_cls in most_specific_cp_clss:
                    objects = [None]
                    if len(cp_cls.object_extraction_code) > 0:
                        try:
                            local_dict = {"subject": cp, "subjects": []}
                            exec(cp_cls.object_extraction_code[0], globals(), local_dict)
                            objects = local_dict["objects"] or []
                        except Exception as e:
                            logger.error("Invalid object extraction code in OWL during CP extraction of: " + str(cp) +
                                         " (" + str(cp_cls) + "): " + str(e))
                    for object_dict in objects:
                        if set(cp.INDIRECT_is_a).intersection({ac.Activity, ti.Interval}):
                            scenario_cp_obj = Scenario_Criticality_Phenomenon(scenarios[0], cp, cp_cls, object_dict)
                            cps.append(scenario_cp_obj)
                        elif len(cp.in_traffic_model) > 0 and tm.Scene in cp.in_traffic_model[0].INDIRECT_is_a:
                            scene_cp_obj = Scene_Criticality_Phenomenon(cp.in_traffic_model, cp, cp_cls, object_dict)
                            cps.append(scene_cp_obj)
                        else:
                            raise ValueError("CP with no scene or scenario found: " + str(cp))
        else:
            raise ValueError("No scenario found in scenario world " + str(scenario))
    else:
        raise ValueError("Wrong scenario type: neither a list nor a world, but found " + str(type(scenario)))

    cps.sort(key=lambda x: x.time if type(x) is Scene_Criticality_Phenomenon else x.time[0])

    return cps


def list_cps(cps: list, output_format="natural", world=None, print_non_visualizable_info=False) -> str:
    """
    Lists the given criticality phenomena in a given output format. If a world is given, checks if the phenomena are
    visualizable in the traffic model of the world.
    If format is natural, it returns a string of lines where each line represents the string represention of the CP.
    If format is csv, it returns  a string of ;-separated CSV lines including a file header of the format
    'Start Time;End Time;Criticality Phenomenon;Subject(s);Object(s)[;Visualizable In Scene]'.
    :param cps: A list of criticality phenomena
    :param output_format: "natural" or ("csv" or "csv-file" (no difference))
    :param world: The world with the traffic model of the CP list
    :param print_non_visualizable_info: Whether to check if CPs
    :return: A string with each line representing a criticality phenomenon
    """
    output = ""
    scene_cps = []
    if print_non_visualizable_info and world:
        tm = auto.get_ontology(auto.Ontology.Traffic_Model, world)
        scenes = list(filter(lambda x: tm.Scene in x.is_a, world.search(type=tm.Scenario)[0].has_traffic_model))
        for scene in scenes:
            scene_cps += [cp for cp in cps if cp.is_representable_in_scene(scene)]
    if output_format == "natural":
        output += "Result:\n"
    elif output_format == "csv" or output_format == "csv-file":
        csv_header = "Start Time;End Time;Criticality Phenomenon;Subject(s);Object(s)"
        if print_non_visualizable_info and world:
            csv_header += ";Visualizable In Scene"
        output += csv_header + "\n"
    if len(cps) > 0:
        for cp in cps:
            if output_format == "natural":
                visualizable = ""
                if print_non_visualizable_info and world:
                    if cp not in scene_cps:
                        visualizable = "[Non visualizable] "
                output += visualizable + str(cp) + "\n"
            elif output_format == "csv" or output_format == "csv-file":
                visualizable = ""
                if print_non_visualizable_info and world:
                    visualizable = ";" + str(cp in scene_cps)
                output += cp.to_csv() + visualizable + "\n"
    elif output_format == "natural":
        output += "No criticality phenomenon found.\n"
    return output[:-1]


def _get_individual_id(individual) -> str:
    """
    Returns a unique identifier as string for the given individual.
    :param individual: The individual to get the ID for.
    :return: A string representing the ID.
    """
    if hasattr(individual, "identifier") and (isinstance(individual.identifier, list) and
                                              len(individual.identifier) > 0 and
                                              type(individual.identifier[0]) in [int, str]) or (
            type(individual.identifier) in [int, str]):
        return str(individual.identifier[0])
    else:
        return str(individual)


def get_most_specific_classes(list_of_individuals, caching=True):
    """
    Helper function that looks up the subsumption hierarchy and returns the most specific classes of a list of
    individuals(i.e. removes all classes that are a parent of some class of the individuals). It looks only at the
    subsumption hierarchy spanned by the domain (L1-L6) and perception, physics, and act ontologies.
    :param list_of_individuals: A list of individuals
    :return: A list of tuples containing the individual in the first entry and a list of most specific classes in the
    second entry (as strings)
    """
    res = []
    noncached_list_of_individuals = []
    if caching:
        for i in list_of_individuals:
            if i in _CACHED_CP_CLASSES.keys():
                i_id = _get_individual_id(i)
                res.append((i_id, _CACHED_CP_CLASSES[i]))
            else:
                noncached_list_of_individuals.append(i)
    relevant_iris = [auto.Ontology.L1_Core.value, auto.Ontology.L2_Core.value,
                     auto.Ontology.L3_Core.value, auto.Ontology.L4_Core.value,
                     auto.Ontology.L5_Core.value, auto.Ontology.L6_Core.value, auto.Ontology.L1_DE.value,
                     auto.Ontology.L2_DE.value, auto.Ontology.L3_DE.value, auto.Ontology.L4_DE.value,
                     auto.Ontology.L5_DE.value, auto.Ontology.L6_DE.value]
    relevant_additional_iris = [auto.Ontology.Perception.value, auto.Ontology.Physics.value,
                                auto.Ontology.Act.value]
    for individual in noncached_list_of_individuals:
        relevant_classes = [x for x in individual.namespace.ontology.classes() if x.namespace.base_iri in relevant_iris]
        relevant_additional_classes = [x for x in individual.namespace.ontology.classes() if x.namespace.base_iri in
                                       relevant_additional_iris]
        individual_clss = list(filter(lambda x: x in relevant_classes, individual.INDIRECT_is_a))
        if len(individual_clss) == 0:
            # Retry finding something outside of domain ontologies, e.g. physics
            individual_clss = list(filter(lambda x: x in relevant_additional_classes, individual.INDIRECT_is_a))
        individual_id = _get_individual_id(individual)
        most_specific_individual_clss = [str(individual_cls) for individual_cls in individual_clss if
                                         hasattr(individual_cls, "__subclasses__") and len(
                                             set(individual_cls.__subclasses__()).intersection(set(individual_clss)))
                                         == 0]
        res.append((individual_id, most_specific_individual_clss))
        if caching:
            _CACHED_CP_CLASSES[individual] = most_specific_individual_clss
    return res
