import math

from owl_augmentator.owl_augmentator import augment, augment_class, AugmentationType
import owlready2
from .utils import *

import itertools
from shapely.geometry import Polygon, LineString
from shapely import wkt
import shapely.geometry


def register(time: owlready2.Ontology):
    with time:

        @augment_class
        class Instant:

            #@augment(AugmentationType.OBJECT_PROPERTY, "before")
            def augment_instant_before(self, other: time.Instant):
                if is_valid_instant(self) and is_valid_instant(other):
                    return self.inTimePosition[0].numericPosition[0] < other.inTimePosition[0].numericPosition[0]

            #@augment(AugmentationType.OBJECT_PROPERTY, "after")
            def augment_instant_after(self, other: time.Instant):
                if is_valid_instant(self) and is_valid_instant(other):
                    return self.inTimePosition[0].numericPosition[0] > other.inTimePosition[0].numericPosition[0]

        @augment_class
        class Interval(owlready2.Thing):

            #@augment(AugmentationType.DATA_PROPERTY, "hasDuration")
            def augment_duration(self):
                """
                This is kinda hacky. We 'misuse' the augmentator functionality here since we need to create Duration
                individuals.
                """
                if len(self.hasBeginning) > 0 and len(self.hasBeginning[0].inTimePosition) > 0 and \
                        len(self.hasBeginning[0].inTimePosition[0].numericPosition) > 0 and len(self.hasEnd) > 0 and \
                        len(self.hasEnd[0].inTimePosition) > 0 and \
                        len(self.hasEnd[0].inTimePosition[0].numericPosition) > 0:
                    dur = time.Duration()
                    self.hasDuration = [dur]
                    beg = self.hasBeginning[0].inTimePosition[0].numericPosition[0]
                    end = self.hasEnd[0].inTimePosition[0].numericPosition[0]
                    dur.numericDuration = [end - beg]

            #@augment(AugmentationType.OBJECT_PROPERTY, "after")
            def augment_interval_after(self, other: time.Interval):
                if is_valid_interval(self) and is_valid_interval(other):
                    return self.hasBeginning[0].inTimePosition[0].numericPosition[0] > \
                           other.hasBeginning[0].inTimePosition[0].numericPosition[0]

            #@augment(AugmentationType.OBJECT_PROPERTY, "before")
            def augment_interval_before(self, other: time.Interval):
                if is_valid_interval(self) and is_valid_interval(other):
                    return self.hasBeginning[0].inTimePosition[0].numericPosition[0] < \
                           other.hasBeginning[0].inTimePosition[0].numericPosition[0]

            # @augment(AugmentationType.OBJECT_PROPERTY, "inside")
            def augment_inside(self, other: time.Instant):
                if is_valid_interval(self) and is_valid_instant(other):
                    return self.hasBeginning[0].inTimePosition[0].numericPosition[0] <= \
                           other.inTimePosition[0].numericPosition[0] <= \
                           self.hasEnd[0].inTimePosition[0].numericPosition[0]

            @augment(AugmentationType.OBJECT_PROPERTY, "intervalContains")
            def augment_interval_contains(self, other: time.Interval):
                if is_valid_interval(self) and is_valid_interval(other):
                    return self.hasBeginning[0].inTimePosition[0].numericPosition[0] < \
                           other.hasBeginning[0].inTimePosition[0].numericPosition[0] and \
                           self.hasEnd[0].inTimePosition[0].numericPosition[0] > \
                           other.hasEnd[0].inTimePosition[0].numericPosition[0]

            #@augment(AugmentationType.OBJECT_PROPERTY, "intervalDuring")
            def augment_interval_during(self, other: time.Interval):
                if is_valid_interval(self) and is_valid_interval(other):
                    return self.hasBeginning[0].inTimePosition[0].numericPosition[0] > \
                           other.hasBeginning[0].inTimePosition[0].numericPosition[0] and \
                           self.hasEnd[0].inTimePosition[0].numericPosition[0] < \
                           other.hasEnd[0].inTimePosition[0].numericPosition[0]

            @augment(AugmentationType.OBJECT_PROPERTY, "intervalEquals")
            def augment_interval_equals(self, other: time.Interval):
                if self != other and is_valid_interval(self) and is_valid_interval(other):
                    return math.isclose(self.hasBeginning[0].inTimePosition[0].numericPosition[0],
                                        other.hasBeginning[0].inTimePosition[0].numericPosition[0]) and \
                           math.isclose(self.hasEnd[0].inTimePosition[0].numericPosition[0],
                                        other.hasEnd[0].inTimePosition[0].numericPosition[0])

            #@augment(AugmentationType.OBJECT_PROPERTY, "intervalFinishes")
            def augment_interval_finishes(self, other: time.Interval):
                if is_valid_interval(self) and is_valid_interval(other):
                    return self.hasBeginning[0].inTimePosition[0].numericPosition[0] > \
                           other.hasBeginning[0].inTimePosition[0].numericPosition[0] and \
                           math.isclose(self.hasEnd[0].inTimePosition[0].numericPosition[0],
                                        other.hasEnd[0].inTimePosition[0].numericPosition[0])

            #@augment(AugmentationType.OBJECT_PROPERTY, "intervalMeets")
            def augment_interval_meets(self, other: time.Interval):
                if is_valid_interval(self) and is_valid_interval(other):
                    return math.isclose(self.hasBeginning[0].inTimePosition[0].numericPosition[0],
                                        other.hasEnd[0].inTimePosition[0].numericPosition[0])

            #@augment(AugmentationType.OBJECT_PROPERTY, "intervalOverlaps")
            def augment_interval_overlaps(self, other: time.Interval):
                if is_valid_interval(self) and is_valid_interval(other):
                    return self.hasBeginning[0].inTimePosition[0].numericPosition[0] < \
                           other.hasBeginning[0].inTimePosition[0].numericPosition[0] < \
                           self.hasEnd[0].inTimePosition[0].numericPosition[0] < \
                           other.hasEnd[0].inTimePosition[0].numericPosition[0]

            #@augment(AugmentationType.OBJECT_PROPERTY, "intervalStarts")
            def augment_interval_starts(self, other: time.Interval):
                if is_valid_interval(self) and is_valid_interval(other):
                    return math.isclose(self.hasBeginning[0].inTimePosition[0].numericPosition[0],
                                        other.hasBeginning[0].inTimePosition[0].numericPosition[0]) and \
                           other.hasBeginning[0].inTimePosition[0].numericPosition[0] < \
                           self.hasEnd[0].inTimePosition[0].numericPosition[0] < \
                           other.hasEnd[0].inTimePosition[0].numericPosition[0]
