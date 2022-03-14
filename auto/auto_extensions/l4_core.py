from owl_augmentator.owl_augmentator import augment, augment_class, concepts, AugmentationType
import owlready2
from shapely import wkt
from .utils import *


def _rec_ids(i):
    ids = {i}
    change = True
    while change:
        update = ids.union(set([y for x in ids for y in x.identical_to]))
        if len(update) == len(ids):
            change = False
        else:
            ids = update
    return ids


def register(l4_core: owlready2.Ontology, l4_de: owlready2.Ontology, l2_de: owlready2.Ontology,
             physics: owlready2.Ontology, time: owlready2.Ontology):
    with l4_core:

        @augment_class
        class Driver(owlready2.Thing):
            @augment(AugmentationType.REIFIED_OBJECT_PROPERTY, l4_de.Pass,
                     ["conducted_by", "has_participant", "hasBeginning", "hasEnd", "belongs_to"])
            @concepts(l4_core.Driver, physics.Spatial_Object, time.TimePosition, physics.is_max_15_m_away)
            def augment_pass(self, other: l4_core.L4_Entity):
                if physics.Spatial_Object in other.INDIRECT_is_a and len(self.drives) > 0:
                    passes = False
                    scene_1 = None
                    scene_2 = self.in_traffic_model[0]
                    scenario = None
                    if len(scene_2.belongs_to) > 0 and len(self.drives) > 0:
                        scenario = scene_2.belongs_to[0]
                        self_veh = self.drives[0]
                        if self_veh in other.is_behind and self_veh in other.is_in_proximity:
                            self_veh_ids = [x for x in _rec_ids(self_veh) if len(x.in_traffic_model) > 0 and
                                            len(x.in_traffic_model[0].inTimePosition) > 0 and
                                            len(x.in_traffic_model[0].inTimePosition[0].numericPosition) > 0]
                            other_ids = [x for x in _rec_ids(other) if len(x.in_traffic_model) > 0 and
                                         len(x.in_traffic_model[0].inTimePosition) > 0 and
                                         len(x.in_traffic_model[0].inTimePosition[0].numericPosition) > 0]
                            self_veh_time_slices = sorted(filter(lambda x: x.in_traffic_model[0].inTimePosition[0].
                                                                 numericPosition[0] <= self_veh.in_traffic_model[0].
                                                                 inTimePosition[0].numericPosition[0],
                                                                 self_veh_ids),
                                                          key=lambda x: -x.in_traffic_model[0].inTimePosition[0].
                                                          numericPosition[0])
                            other_time_slices = sorted(filter(lambda x: x.in_traffic_model[0].inTimePosition[0].
                                                              numericPosition[0] <= other.in_traffic_model[0].
                                                              inTimePosition[0].numericPosition[0],
                                                              other_ids),
                                                       key=lambda x: -x.in_traffic_model[0].inTimePosition[0].
                                                       numericPosition[0])
                            time_slices = []
                            for s_ts in self_veh_time_slices[1:]:
                                for o_ts in other_time_slices[1:]:
                                    if s_ts.in_traffic_model[0] == o_ts.in_traffic_model[0]:
                                        time_slices.append((s_ts, o_ts))
                            if len(time_slices) > 0 and time_slices[-1][0] not in time_slices[-1][1].is_behind:
                                for t in time_slices:
                                    if t[0] in t[1].is_in_front_of and t[0] in t[1].is_in_proximity:
                                        passes = True
                                        scene_1 = t[0].in_traffic_model[0]
                                        break
                    return passes, scene_1, scene_2, scenario
