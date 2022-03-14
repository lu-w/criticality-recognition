from owl_augmentator.owl_augmentator import augment, augment_class, concepts, AugmentationType
import owlready2
from shapely import wkt
from .utils import *


def register(l1_core: owlready2.Ontology, l4_core: owlready2.Ontology, l4_de: owlready2.Ontology):
    with l1_core:

        @augment_class
        class Driveable_Lane(owlready2.Thing):

            @augment(AugmentationType.OBJECT_PROPERTY, "sfIntersects_lane_driver")
            def augment_intersects_lane_driver(self, other: l4_core.Driver):
                if same_scene(self, other) and has_geometry(self) and has_geometry(other):
                    geo_self = wkt.loads(self.hasGeometry[0].asWKT[0])
                    geo_other = wkt.loads(other.hasGeometry[0].asWKT[0])
                    return geo_self.intersects(geo_other)

        @augment_class
        class Non_Driveable_Lane(owlready2.Thing):
            @augment(AugmentationType.OBJECT_PROPERTY, "sfIntersects_nonlane_bicyclist")
            def augment_intersects_nonlane_bicyclist(self, other: l4_de.Bicyclist):
                if same_scene(self, other) and has_geometry(self) and has_geometry(other):
                    geo_self = wkt.loads(self.hasGeometry[0].asWKT[0])
                    geo_other = wkt.loads(other.hasGeometry[0].asWKT[0])
                    return geo_self.intersects(geo_other)
