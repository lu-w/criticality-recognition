from ..utils import *


@monkeypatch(omega_format.Boundary)
def to_auto(cls, world: owlready2.World, scenes, lane, identifier=None, parent_identifier=None):
    if cls.type != omega_format.ReferenceTypes.BoundaryType.VIRTUAL:

        # Fetches ontologies
        tm = auto.get_ontology(auto.Ontology.Traffic_Model, world)
        ph = auto.get_ontology(auto.Ontology.Physics, world)
        geo = auto.get_ontology(auto.Ontology.GeoSPARQL, world)
        l1_de = auto.get_ontology(auto.Ontology.L1_DE, world)
        l2_core = auto.get_ontology(auto.Ontology.L2_Core, world)
        l2_de = auto.get_ontology(auto.Ontology.L2_DE, world)

        # Creates boundary instance
        boundary = tm.Traffic_Model_Element()
        boundary.identifier = str(parent_identifier) + "_" + str(identifier)
        for scene in scenes:
            scene.has_traffic_entity.append(boundary)

        # Type
        marker = False
        barrier = False
        boundary_system = False
        if cls.type == omega_format.ReferenceTypes.BoundaryType.SOLID:
            boundary.is_a.append(l1_de.Lane_Boundary_Marker)
            marker = True
        elif cls.type == omega_format.ReferenceTypes.BoundaryType.DASHED:
            boundary.is_a.append(l1_de.Line_Marker)
            marker = True
        elif cls.type == omega_format.ReferenceTypes.BoundaryType.SOLID_SOLID:
            boundary.is_a.append(l1_de.Double_Lane_Boundary_Marker)
            marker = True
        elif cls.type == omega_format.ReferenceTypes.BoundaryType.SOLID_DASHED:
            boundary.is_a.append(l1_de.Unilateral_Lane_Boundary_Marker)
            marker = True
        elif cls.type == omega_format.ReferenceTypes.BoundaryType.DASHED_SOLID:
            boundary.is_a.append(l1_de.Unilateral_Lane_Boundary_Marker)
            marker = True
        elif cls.type == omega_format.ReferenceTypes.BoundaryType.DASHED_CHANGE_DIRECTION_LANE:
            boundary.is_a.append(l1_de.Double_Line_Marker)
            marker = True
        elif cls.type == omega_format.ReferenceTypes.BoundaryType.HAPTIC_ACOUSTIC:
            # TODO: for all marker boundaries within same group add "Haptic_Road_Marker" as subclass
            pass
        elif cls.type == omega_format.ReferenceTypes.BoundaryType.STUDS:
            boundary.is_a.append(l2_de.Raised_Pavement_Marker_Boundary_System)
            boundary_system = True
        elif cls.type == omega_format.ReferenceTypes.BoundaryType.REFLECTOR_GUIDING_LAMPS:
            boundary.is_a.append(l2_de.
                                 Reflective_Raised_Pavement_Marker_Boundary_System)
            boundary_system = True
        elif cls.type == omega_format.ReferenceTypes.BoundaryType.GUARD_RAIL:
            boundary.is_a.append(l2_de.Guard_Rail)
            barrier = True
        elif cls.type == omega_format.ReferenceTypes.BoundaryType.GUARD_RAIL_ACCIDENT_PROTECTION:
            boundary.is_a.append(l2_de.Super_Rail_Guardrail)
            barrier = True
        elif cls.type == omega_format.ReferenceTypes.BoundaryType.CONCRETE_BARRIER:
            boundary.is_a.append(l2_de.Concrete_Step_Barrier)
            barrier = True
        elif cls.type == omega_format.ReferenceTypes.BoundaryType.REFLECTOR_POSTS:
            boundary.is_a.append(l2_de.Reflector_Post_Boundary_System)
            boundary_system = True
        elif cls.type == omega_format.ReferenceTypes.BoundaryType.SAFETY_BEACONS:
            boundary.is_a.append(l2_de.Safety_Beacon_Boundary_System)
            boundary_system = True
        elif cls.type == omega_format.ReferenceTypes.BoundaryType.DIVIDER:
            boundary.is_a.append(l2_de.Guidance_System)
            barrier = True
        elif cls.type == omega_format.ReferenceTypes.BoundaryType.NOISE_PROTECTION_WALL:
            boundary.is_a.append(l2_de.Noise_Protection_Wall)
            barrier = True
        elif cls.type == omega_format.ReferenceTypes.BoundaryType.CURB:
            boundary.is_a.append(l2_de.Curb)
            barrier = True
        elif cls.type == omega_format.ReferenceTypes.BoundaryType.ANTI_GLARE_SCREEN:
            boundary.is_a.append(l2_de.Anti_Glare_Screen)
            barrier = True
        elif cls.type == omega_format.ReferenceTypes.BoundaryType.FENCE:
            boundary.is_a.append(l2_de.Fence)
            barrier = True
        elif cls.type == omega_format.ReferenceTypes.BoundaryType.MISC:
            boundary.is_a.append(ph.Spatial_Object)
        elif cls.type == omega_format.ReferenceTypes.BoundaryType.STRUCTURAL_OBJECT:
            boundary.is_a.append(l2_core.Roadside_Construction)
            barrier = True

        # Sub type
        if marker:
            # TODO highway width (0.15 & 0.3) - need to fetch road type for this. We assume urban & rural roads for now.
            if cls.type == omega_format.ReferenceTypes.BoundarySubType.THIN:
                boundary.has_width = 0.12
            elif cls.type == omega_format.ReferenceTypes.BoundarySubType.THICK:
                boundary.has_width = 0.25
        elif barrier:
            if cls.type == omega_format.ReferenceTypes.BoundarySubType.METAL:
                boundary.is_a.append(ph.Metal)
            elif cls.type == omega_format.ReferenceTypes.BoundarySubType.WOODEN:
                boundary.is_a.append(ph.Wood)
        elif boundary_system:
            if cls.type == omega_format.ReferenceTypes.BoundarySubType.METAL:
                boundary.is_a.append(ph.System &
                                     ph.consists_of.only(
                                         ph.Metal))
            if cls.type == omega_format.ReferenceTypes.BoundarySubType.WOODEN:
                boundary.is_a.append(ph.System &
                                     ph.consists_of.only(
                                         ph.Wood))

        # Height
        if cls.height > 0:
            boundary.height = float(cls.height)

        if marker:
            # Color
            if cls.color == omega_format.ReferenceTypes.FlatMarkingColor.RED:
                boundary.has_color = [ph.Red]
            elif cls.color == omega_format.ReferenceTypes.FlatMarkingColor.BLUE:
                boundary.has_color = [ph.Blue]
            elif cls.color == omega_format.ReferenceTypes.FlatMarkingColor.GREEN:
                boundary.has_color = [ph.Green]
            elif cls.color == omega_format.ReferenceTypes.FlatMarkingColor.WHITE:
                boundary.has_color = [ph.White]
            elif cls.color == omega_format.ReferenceTypes.FlatMarkingColor.YELLOW:
                boundary.has_color = [ph.Yellow]
            # Condition
            if cls.condition == omega_format.ReferenceTypes.FlatMarkingCondition.FINE:
                boundary.has_degradation_degree = 0
            elif cls.condition == omega_format.ReferenceTypes.FlatMarkingCondition.CORRUPTED_1_OLD_VISIBIBLE:
                boundary.has_degradation_degree = 25
            elif cls.condition == omega_format.ReferenceTypes.FlatMarkingCondition.CORRUPTED_2_FADED:
                boundary.has_degradation_degree = 75

        # Geometry
        if cls.is_right_boundary:
            line = lane.border_right.value.polyline
        else:
            line = lane.border_left.value.polyline
        if not boundary.has_height or boundary.has_height == 0:
            wkt_string = "LINESTRING ( "
            for i in range(cls.poly_index_start, cls.poly_index_end + 1):
                wkt_string += str(line.pos_x[i]) + " " + str(line.pos_y[i]) + " " + str(line.pos_z[i]) + ", "
            wkt_string = wkt_string[:-2] + " )"
        else:
            wkt_string = "POLYGON (( "
            for i in range(cls.poly_index_start, cls.poly_index_end + 1):
                wkt_string += str(line.pos_x[i]) + " " + str(line.pos_y[i]) + " " + str(line.pos_z[i]) + ", "
            for i in range(cls.poly_index_end, cls.poly_index_start - 1, -1):
                wkt_string += str(line.pos_x[i]) + " " + str(line.pos_y[i]) + " " + str(boundary.has_height) + ", "
            wkt_string += str(line.pos_x[cls.poly_index_start]) + " " + str(line.pos_y[cls.poly_index_start]) + " " + \
                          str(line.pos_z[cls.poly_index_start]) + ", "
            wkt_string = wkt_string[:-2] + " ))"
        geom = wkt.loads(wkt_string)
        if boundary.has_width and boundary.has_width > 0:
            geom = geom.buffer(boundary.has_width, cap_style=2)
        bound_geo = geo.Geometry()
        bound_geo.asWKT = [str(geom)]
        if not boundary_system:
            boundary.hasGeometry = [bound_geo]
        else:
            # Do not give boundary system a concrete geometrical shape but rather constraint that every element of the
            # boundary system needs to be within the geometry
            boundary.is_a.append(ph.System & ph.consists_of.only(ph.Spatial_Object & geo.sfWithin.value(bound_geo)))

        add_layer_3_information(cls, boundary, world)

        return [(cls, [boundary])]
    else:
        return [(cls, [])]
