from owl_augmentator.owl_augmentator import augment, augment_class, concepts, AugmentationType
import owlready2
from shapely import wkt
from .utils import *


def register(l1_de: owlready2.Ontology, l1_core: owlready2.Ontology, l4_de: owlready2.Ontology):
    with l1_de:

        @augment_class
        class Pedestrian_Crossing(owlready2.Thing):

            @augment(AugmentationType.OBJECT_PROPERTY, "sfIntersects_crosswalk_lane")
            def augment_intersects_crosswalk_lane(self, other: l1_core.Driveable_Lane):
                if same_scene(self, other) and has_geometry(self) and has_geometry(other):
                    geo_self = wkt.loads(self.hasGeometry[0].asWKT[0])
                    geo_other = wkt.loads(other.hasGeometry[0].asWKT[0])
                    return geo_self.intersects(geo_other)

            @augment(AugmentationType.OBJECT_PROPERTY, "sfIntersects_crosswalk_bicyclist")
            def augment_intersects_crosswalk_bicyclist(self, other: l4_de.Bicyclist):
                if same_scene(self, other) and has_geometry(self) and has_geometry(other):
                    geo_self = wkt.loads(self.hasGeometry[0].asWKT[0])
                    geo_other = wkt.loads(other.hasGeometry[0].asWKT[0])
                    return geo_self.intersects(geo_other)
