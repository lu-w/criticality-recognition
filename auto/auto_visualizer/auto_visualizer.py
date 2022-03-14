# Visualizer is for debugging purposes only
import logging
import math
import random
import threading
import http.server
import socketserver
import os
import re

from shapely import wkt
import matplotlib.pyplot as plt
import mpld3
import screeninfo
import tempfile
import webbrowser
import owlready2
import numpy as np
import auto.auto

from criticality_recognition import phenomena_extraction

# TODO
# - visualize scenario level CPs
# - show has distance to in table for each individual - as ternary relations - instead of omitting it

####################
# Config constants #
####################

# Classes to not show in visualization
_NO_PRINTING_CLASSES = {"physics.Has_Distance_To", "perception.Is_Full_Occlusion"}
# Data/object properties to hide from the individual tables shown when hovering
_NO_PRINTING_PROPERTIES = {"perceptional_property", "traffic_related_concept_property",
                           "descriptive_traffic_entity_property", "traffic_entity_property", "activity_property",
                           "physical_property", "traffic_modeling_property", "traffic_entity_property",
                           "automotive_urban_traffic_property", "L1_property", "L2_property", "L3_property",
                           "L4_property", "L5_property", "L6_property", "traffic_model_element_property",
                           "criticality_phenomenon_as_object_property", "has_positional_relation",
                           "has_spatial_relation", "has_dynamical_relation", "SF_spatial_relation",
                           "performance_spatial_relation", "EH_spatial_relation", "RCC8_spatial_relation", "rcc8dc",
                           "ehDisjoint"}
# If one hides long property lists, this is the number after which the list is cut off
_MAX_PROPS_DISPLAY = 4

# Logging
logger = logging.getLogger(__name__)


# Helper function for sorting CPs & individuals
def natural_sort_key(s, _nsre=re.compile("([0-9]+)")):
    return [int(text) if text.isdigit() else text.lower() for text in _nsre.split(str(s))]


#######
# CSS #
#######

# Scene CSS (added is iframes to scenario HTML)
scene_css = """
        <style>
            svg * {
                font-size: 4pt;
            }
            table {
                border: solid 1px #DDEEEE;
                border-collapse: collapse;
                border-spacing: 0;
                font: normal 8px, sans-serif;
            }
            thead th {
                background-color: #DDEFEF;
                border: solid 1px #DDEEEE;
                color: #336B6B;
                padding: 3px;
                text-align: left;
                text-shadow: 1px 1px 1px #fff;
                font-size: 10pt;
            }
            tbody td {
                background-color: #FFFFFF;
                border: solid 1px #DDEEEE;
                color: #333;
                padding: 3px;
                text-shadow: 1px 1px 1px #fff;
                font-size: 8pt;
            }
            .cp-tooltip {}
        </style>
        """

# Scenario CSS (main CSS)
scenario_css = """
        <style>
            .slider {
              -webkit-appearance: none;  /* Override default CSS styles */
              appearance: none;
              width: 100%; /* Full-width */
              height: 25px; /* Specified height */
              background: #d3d3d3; /* Grey background */
              outline: none; /* Remove outline */
              opacity: 0.7; /* Set transparency (for mouse-over effects on hover) */
              -webkit-transition: .2s; /* 0.2 seconds transition on hover */
              transition: opacity .2s;
            }
            .slider:hover {
              opacity: 1; /* Fully shown on mouse-over */
            }
            .slider::-webkit-slider-thumb {
              -webkit-appearance: none; /* Override default look */
              appearance: none;
              width: 25px; /* Set a specific slider handle width */
              height: 25px; /* Slider handle height */
              background: #04AA6D; /* Green background */
              cursor: pointer; /* Cursor on hover */
            }
            .slider::-moz-range-thumb {
              width: 25px; /* Set a specific slider handle width */
              height: 25px; /* Slider handle height */
              background: #04AA6D; /* Green background */
              cursor: pointer; /* Cursor on hover */
            }
        </style>"""


def visualize_scenario(scenario, cps=None):
    """
    Creates an HTML visualization of the given scenario. Starts a simple web server at localhost:8000 (blocking).
    :param scenario: Either a list of worlds, each world representing a single scene or a single world representing a
    whole scenario
    :param cps: A list of criticality phenomena which optionally to visualize as well.
    :return: The path to the directory in which to find the created HTML visualization.
    """
    pl_html = []
    scenario_inst = None
    if cps is None:
        cps = []

    # Fetch scene list
    if type(scenario) == list:
        scenes = [scene_world.search(type=auto.auto.get_ontology(auto.auto.Ontology.Traffic_Model, scene_world).Scene)
                  [0] for scene_world in scenario]
    elif type(scenario) == owlready2.namespace.World or type(scenario) == owlready2.World:
        tm = auto.auto.get_ontology(auto.auto.Ontology.Traffic_Model, scenario)
        scenario_inst = scenario.search(type=tm.Scenario)[0]
        scenes = list(filter(lambda x: tm.Scene in x.is_a, scenario_inst.has_traffic_model))
    else:
        raise ValueError
    scenes = sorted(scenes, key=lambda x: x.inTimePosition[0].numericPosition[0])

    # Assemble scenario title
    title = "Scenario"
    if scenario_inst and hasattr(scenario_inst, "identifier") and len(scenario_inst.identifier) > 0:
        title += " " + str(scenario_inst.identifier[0])
    scenario_info = "(" + str(len(scenes)) + " Scenes)"
    # Main HTML code for index.html
    html_body = """<!DOCTYPE html>
<html>
    <head>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-1BmE4kWBq78iYhFldvKuhfTAU6auU8tT94WrHftjDbrCEXSU1oBoqyl2QvZ6jIW3" crossorigin="anonymous">
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-ka7Sk0Gln4gmtz2MlQnikT1wXgYsOg+OMhuP+IlRH9sENBO0LRn5q+8nbTov4+1p" crossorigin="anonymous"></script>
        <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
        <meta charset="utf-8">""" + scenario_css + """
        <title>""" + title + """</title>
    </head>
    <body>
        <div class=\"d-flex flex-row justify-content-center\"><div class=\"mt-3 py-1 px-6 alert alert-info\" style=\"display: inline-block\" role=\"alert\"><center><h5>""" + title + """ """ + scenario_info + """</h5></center></div></div>
        <div class="slidecontainer m-2">
            <input type="range" min="1" max=\"""" + str(len(scenes)) + """\" value="1" class="slider" id="myRange">
        </div>
        <script>
            var slider = document.getElementById("myRange");
            var last_set = 1
            var show_all_cps = true
            slider.oninput = function() {
              var output = document.getElementById("plt" + this.value);
              var last_output = document.getElementById("plt" + last_set);
              last_output.style.display = 'none';
              output.style.display = 'block';
              last_set = this.value
            }
            function toggle_cps_all_iframes() {
                show_all_cps = !show_all_cps
                $(".cp-all-button").each(function(i) {
                  if (show_all_cps) {
                      this.parentElement.classList.add("active")
                      this.checked = true
                  } else {
                      this.parentElement.classList.remove("active")
                      this.checked = false
                  }
                })
                $(".cp-button").each(function(i) {
                  if (show_all_cps) {
                      this.parentElement.classList.add("active")
                      this.checked = true
                  } else {
                      this.parentElement.classList.remove("active")
                      this.checked = false
                  }
                })
                $(".scene-plot").each(function(i) {
                  this.contentWindow.toggle_cps(show_all_cps)
                })
            }
            function toggle_cp_class(ele, cp_cls_id) {
                // 0. disable automatically checked checkbox (will be added again at step 3)
                ele.checked = !ele.checked
                // 1. find active scene plot
                active_scene = $(".scene-plot-container").filter(function(i) {
                  return this.style.display !== "none"
                })[0]
                // 2. get CP pred. str for given cp_cls_id
                cp_pred = active_scene.getElementsByClassName("scene-plot")[0].contentWindow.cp_predicates[cp_cls_id]
                // 3. Toggle all buttons for this CP pred
                $("label > span:contains(" + cp_pred + ")").each(function(i) {
                  this.parentElement.classList.toggle("active")
                  this.parentElement.querySelector(".cp-button").checked = !this.parentElement.querySelector(".cp-button").checked
                })
                // 4. check if (and where) CP pred. str is present in cp_predicates, pass the resulting index
                $(".scene-plot").each(function(k) {
                  cp_cls_id_scene = -1
                  for (var i = 0; i < this.contentWindow.cp_predicates.length; i++) {
                    if (cp_pred === this.contentWindow.cp_predicates[i]) {
                        cp_cls_id_scene = i
                    }
                  }
                  if (cp_cls_id_scene >= 0) {
                    this.contentWindow.toggle_cp_class(cp_cls_id_scene, ele.checked)
                  }
                })
            }
        </script>
    """
    pl_html.append(html_body)
    iframes = []

    def get_color(p):
        # Fetches a different color each time, but ensures that it has a readable contrast.
        _LUMA_LIMIT = 170
        color = 0
        luma = _LUMA_LIMIT
        while luma >= _LUMA_LIMIT:
            color = random.randrange(0, 0xFFFFFF, 0xF)
            luma = 0.2126 * ((color >> 16) & 0xff) + 0.7152 * ((color >> 8) & 0xff) + 0.0722 * ((color >> 0) & 0xff)
        return "#" + "%06x" % color

    # Create HTML for each scene
    for i, scene in enumerate(scenes):
        scene_cps = [cp for cp in cps if cp.is_representable_in_scene(scene)]
        cp_colors = list(map(get_color, range(len([x for c in scene_cps for x in c.subjects]))))
        cp_color = 0
        no_geo_entities = []
        primary_screens = list(filter(lambda x: x.is_primary, screeninfo.get_monitors()))
        if len(primary_screens) > 0:
            width = (primary_screens[0].width_mm / 25.4) * 0.73
            height = (primary_screens[0].height_mm / 25.4) * 0.73
        else:
            width = 24.5
            height = 10
        fig = plt.figure(figsize=(width, height))
        plt.axis("equal")
        entity_labels = []
        entity_relations = []
        relations_per_cp_class = dict()
        cps_relations = []
        cps_for_tooltips = []
        centroids_x = []
        centroids_y = []
        cp_subj_centroids_x = []
        cp_subj_centroids_y = []
        for entity in scene.has_traffic_entity:
            if len(entity.hasGeometry) > 0:
                for geo in entity.hasGeometry:
                    shape = wkt.loads(geo.asWKT[0])
                    entity_cp_relations = []
                    points = None
                    if hasattr(shape, "exterior"):
                        points = shape.exterior.xy
                    try:
                        hasattr(shape, "coords")
                        points = shape.coords.xy
                    except NotImplementedError:
                        pass
                    if points:
                        if (np.isclose(centroids_x, shape.centroid.x) & np.isclose(centroids_y, shape.centroid.y))\
                                .any():
                            x = shape.centroid.x + 0.0
                            y = shape.centroid.y + 0.8
                            plt.plot((shape.centroid.x, x), (shape.centroid.y, y), "k-")
                        else:
                            x = shape.centroid.x
                            y = shape.centroid.y
                        centroids_x.append(x)
                        centroids_y.append(y)
                        plt.plot(*points, alpha=.6)
                        if auto.auto.get_ontology(auto.auto.Ontology.Physics, scenario).Dynamical_Object in \
                                entity.INDIRECT_is_a:
                            plt.fill(*points, alpha=.3)
                            if entity.has_yaw is not None:
                                x_dir = (0.3 * math.cos(math.radians(entity.has_yaw)))
                                y_dir = (0.3 * math.sin(math.radians(entity.has_yaw)))
                                plt.arrow(shape.centroid.x, shape.centroid.y, dx=x_dir, dy=y_dir, shape="full",
                                          length_includes_head=True, color="gray", alpha=0.6, head_width=0.6)
                        entity_labels.append(_describe_entity(entity))
                        # Plot CPs
                        entity_scene_cps = list(filter(lambda scp: entity in scp.subjects, scene_cps))
                        if len(entity_scene_cps) > 0:
                            cp_subj_centroids_x.append(x)
                            cp_subj_centroids_y.append(y)
                            ent_color = "red"
                        else:
                            ent_color = "black"
                        if entity.identifier and len(entity.identifier) > 0 and not entity.is_persistent and not \
                                (isinstance(entity.identifier[0], str) and entity.identifier[0].startswith("repr")):
                            plt.annotate(entity.identifier[0], (x+0.2, y+0.2), color=ent_color)
                        already_drawn_cps = []
                        # init dict
                        for cp in entity_scene_cps:
                            relations_per_cp_class[cp.predicate] = []
                        for cp in entity_scene_cps:
                            if cp not in already_drawn_cps:
                                same_line_cps = [x for x in entity_scene_cps if x.objects == cp.objects]
                                labels = [(x.predicate.split("(")[0],
                                           (x.predicate.split("(")[1].replace(")", ""), str(x)))
                                          for x in same_line_cps]
                                already_drawn_cps += same_line_cps
                                subj_x = x
                                subj_y = y
                                for obj in cp.objects:
                                    if len(obj.hasGeometry) > 0:
                                        geom_o = wkt.loads(obj.hasGeometry[0].asWKT[0])
                                        line = plt.plot((subj_x, geom_o.centroid.x), (subj_y, geom_o.centroid.y),
                                                        linestyle="-", color=cp_colors[cp_color], label=cp.predicate,
                                                        linewidth=2)[0]
                                        m = (geom_o.centroid.y - subj_y) / (geom_o.centroid.x - subj_x)
                                        b = subj_y - m * subj_x
                                        if subj_x > geom_o.centroid.x:
                                            x_off = 0.4
                                        else:
                                            x_off = -0.4
                                        arr_x = geom_o.centroid.x + x_off
                                        arr_y = m * arr_x + b
                                        tip = plt.arrow(arr_x, arr_y, dx=-x_off, dy=-(arr_y - geom_o.centroid.y),
                                                        color=cp_colors[cp_color], shape="full",
                                                        length_includes_head=True, head_width=0.2)
                                        if len(labels[0]) > 1:
                                            label_row = " ".join([label[0] for label in labels])
                                        else:
                                            label_row = labels[0]
                                        x_offset = (len(label_row) * 0.055) / 2 - 0.055
                                        if subj_x > geom_o.centroid.x:
                                            label_x = geom_o.centroid.x + abs(subj_x - geom_o.centroid.x) / 2 - x_offset
                                        else:
                                            label_x = geom_o.centroid.x - abs(subj_x - geom_o.centroid.x) / 2 - x_offset
                                        a = math.degrees(np.arctan(m))
                                        for l_i, label in enumerate(labels):
                                            label_y = m * label_x + b + 0.05
                                            annot = plt.annotate(label[0].replace("CP_", ""), (label_x, label_y),
                                                                 color=cp_colors[cp_color], rotation=a, fontsize=4,
                                                                 rotation_mode="anchor")
                                            label_x += len(label[0]) * 0.055 + 0.1
                                            entity_cp_relations.append(annot)
                                            cps_relations.append(annot)
                                            relations_per_cp_class[same_line_cps[l_i].predicate] += [annot, line, tip]
                                            cps_for_tooltips.append(same_line_cps[l_i])
                                        subj_x = geom_o.centroid.x
                                        subj_y = geom_o.centroid.y
                                        entity_cp_relations += [line, tip]
                                cp_color = (cp_color + 1) % len(cp_colors)
                        entity_relations.append(entity_cp_relations)
            elif len(set([str(y) for y in entity.is_a]).intersection(_NO_PRINTING_CLASSES)) == 0:
                no_geo_entities.append(_describe_entity(entity))
        if len(cp_subj_centroids_x) > 0:
            plt.plot(cp_subj_centroids_x, cp_subj_centroids_y, "o", color="r", mec="k", markersize=10, alpha=1)
        pl2 = plt.plot(centroids_x, centroids_y, "o", color="b", mec="k", mew=1, alpha=.4)
        tooltip_individuals = ToolTipAndClickInfo(pl2[0], labels=entity_labels, targets=entity_relations,
                                                  targets_per_cp=relations_per_cp_class)
        fig.tight_layout()
        mpld3.plugins.connect(fig, tooltip_individuals)
        for h, cp_text in enumerate(cps_relations):
            tooltip_cp = CPTooltip(cp_text, cps_for_tooltips[h])
            mpld3.plugins.connect(fig, tooltip_cp)
        html = "\n\t\t<div class=\"container-fluid scene-plot-container\" id=\"plt" + str(i + 1) + "\" style =\""
        if i != 0:
            html += "display: none;"
        html += "\">"
        html += """
            <div class="row">
                <div class="col-md-1">
                    """
        html += """<div class="">
                        <label class="btn btn-primary active" style="margin-bottom: 10px; width: %s">
                            <input type="checkbox" class="cp-all-button" id="cp-all-button-%s" autocomplete="off" onclick="toggle_cps_all_iframes();" checked>
                            <span>Show all criticality phenomena</span>
                        </label>""" % ("100%", str(i))
        for l, pred in enumerate(sorted(relations_per_cp_class.keys(), key=natural_sort_key)):
            html += """
                        <br />
                        <label class="btn btn-secondary active" style="margin-bottom: 5px; width: %s">
                            <input type="checkbox" class="cp-button" id="cp-button-%s-%s" autocomplete="off" onclick="toggle_cp_class(this, %s);" checked>
                            <span>%s</span>
                        </label>""" % ("100%", str(i), str(l), str(l), pred)
        html += """
                    </div>
                </div>
                <div class="col-md-11">
                    """
        html += "<div class=\"embed-responsive embed-responsive-16by9\">\n"
        html += "\t\t\t\t\t\t<iframe class=\"scene-plot\" src=\"scene" + str(i + 1) + ".html\" class=\"embed-responsive-item\" style=\"width: 100%; height: " + str(height*1.27) + "in\" allowfullscreen></iframe>\n\t\t\t\t\t</div>\n"
        iframe_html = """<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8">
        <meta HTTP-EQUIV="Access-Control-Allow-Origin" CONTENT="localhost">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-1BmE4kWBq78iYhFldvKuhfTAU6auU8tT94WrHftjDbrCEXSU1oBoqyl2QvZ6jIW3" crossorigin="anonymous">
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-ka7Sk0Gln4gmtz2MlQnikT1wXgYsOg+OMhuP+IlRH9sENBO0LRn5q+8nbTov4+1p" crossorigin="anonymous"></script>
        <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    </head>
    <body>"""
        iframe_html += scene_css
        iframe_html += """
        <div class="d-flex flex-row justify-content-center">
            <div class="btn-group btn-group-toggle" data-bs-toggle="buttons">
                <label class="btn btn-secondary active">
                    <input type="checkbox" id="tooltip_button" checked autocomplete="off" onclick="toggle_tooltips(this);"> Show tooltip with information of individuals
                </label>
                <label class="btn btn-secondary active">
                    <input type="checkbox" id="descr_button" checked autocomplete="off" onclick="toggle_all_ind_relations(this);"> Show full individual relations in tooltip
                </label>
            </div>
        </div>
        <script>
            var show_tooltips = true
            var show_long_ind = true
            cps = []
            cp_targets = []
            cp_targets_per_class = []
            function toggle_tooltips(ele) {
                ele.parentElement.classList.toggle("active")
                show_tooltips = !show_tooltips
            }
            function toggle_all_ind_relations(ele) {
                ele.parentElement.classList.toggle("active")
                show_long_ind = !show_long_ind
            }
            function toggle_cp_targets(targets, state) {
                for (let j = 0; j < targets.length; j++) {
                    var x = mpld3.get_element(targets[j])
                    if (x) {
                        if ("path" in x) {
                            tog = x.path
                        } else if ("obj" in x) {
                            tog = x.obj
                        }
                        for (var k = 0; k < tog._groups.length; k++) {
                            for (var l = 0; l < tog._groups[k].length; l++){
                                if (state) {
                                    tog._groups[k][l].style.display = "block"
                                } else {
                                    tog._groups[k][l].style.display = "none"
                                }
                            }
                        }
                    }
                }
            }
            function toggle_cps(state) {
                for (let i = 0; i < cp_targets.length; i++) {
                    toggle_cp_targets(cp_targets[i], state)
                }
            }
            function toggle_cp_class(cp_class, state) {
                targets = cp_targets_per_class[cp_class]
                toggle_cp_targets(targets, state)
            }
        </script>
        <div class="card m-2">
            <div class="card-title d-flex flex-row justify-content-center m-1">
                <h5>"""
        if len(scene.inTimePosition) > 0 and len(scene.inTimePosition[0].numericPosition) > 0:
            time = "%.2f s" % scene.inTimePosition[0].numericPosition[0]
            if scenario_inst and len(scenario_inst.hasEnd) > 0 and len(scenario_inst.hasEnd[0].inTimePosition) > 0 and \
                    len(scenario_inst.hasEnd[0].inTimePosition[0].numericPosition) > 0:
                time += " / %.2f s" % scenario_inst.hasEnd[0].inTimePosition[0].numericPosition[0]
            else:
                time += " / " + str(len(scenes))
        else:
            time = str(i) + " / " + str(len(scenes))
        iframe_html += "Scene " + time + "<br />"
        iframe_html += """
                </h5>
            </div>
            <div class="card-body m-0 p-0 d-flex justify-content-center">
        """
        scene_html = mpld3.fig_to_html(fig)
        iframe_html += ''.join("\t\t"+line+"\n" for line in scene_html.splitlines())
        iframe_html += """
            </div>
        </div>"""
        if len(no_geo_entities) > 0:
            iframe_html += """
        <div class="d-flex flex-row justify-content-center">
            <a class="btn btn-primary" data-bs-toggle="collapse" href="#noGeoCollapse" role="button" aria-expanded="false" aria-controls="noGeoCollapse">
                Show scene individuals with no geometric representation (%s)
            </a>
        </div>
        <div class="container-fluid collapse" id="noGeoCollapse">
            <div class="card card-body m-2">""" % str(len(no_geo_entities))
            iframe_html += "".join(no_geo_entities)
            iframe_html += """
            </div>
        </div>"""
        iframe_html += "\t</body>\n</html>"
        iframes.append(iframe_html)
        html += "\t\t\t\t</div>\n\t\t\t</div>\n\t\t</div>"
        pl_html.append(html)

    # Assemble main HTML
    pl_html.append("\n\t</body>\n</html>")
    # Write main HTML to index.html
    tmp_dir = tempfile.mkdtemp()
    index_path = tmp_dir + "/index.html"
    with open(index_path, "w") as file:
        for html in pl_html:
            file.write(html)

    # Write each scene HTML to a single file
    for i, iframe in enumerate(iframes):
        frame_path = tmp_dir + "/scene" + str(i + 1) + ".html"
        with open(frame_path, "w") as file:
            for html in iframe:
                file.write(html)

    # Starts webserver
    os.chdir(tmp_dir)
    threading.Thread(target=socketserver.TCPServer(("", 8000),
                                                   http.server.SimpleHTTPRequestHandler).serve_forever).start()
    logger.info("Visualization is available at: http://localhost:8000")
    webbrowser.open("http://localhost:8000")
    return tmp_dir


def _describe_entity(entity):
    """
    Describes the given traffic entity as an HTML list.
    :param entity: An object of an owlready2 class.
    :return: The HTML-representation of entity.
    """
    cls = phenomena_extraction.get_most_specific_classes([entity])
    label = "<table class=\"m-2\"><thead><tr><th>Individual</th><th>" + str(entity)
    label += " (" + ", ".join(cls[0][1]) + ")</th></tr></thead><tbody><tr><td>is_a</td><td>"
    label += ", ".join([str(x) for x in entity.is_a])
    label += "</td></tr>"
    for prop in entity.get_properties():
        if str(prop.python_name) not in _NO_PRINTING_PROPERTIES:
            label += "<tr>"
            label += "<td>"
            label += str(prop.python_name)
            label += "</td>"
            label += "<td>"
            label += ", ".join([str(x) for x in prop[entity][:_MAX_PROPS_DISPLAY]])
            if len(prop[entity]) > _MAX_PROPS_DISPLAY:
                label += "<text class=\"extended_ind_props\">"
                label += ", ".join([str(x) for x in prop[entity][_MAX_PROPS_DISPLAY:]]) + "</text>"
                label += "<text class=\"extended_ind_props_dots\" style=\"display: none;\">...</text>"
            label += "</td>"
            label += "</tr>"
    label += "</tbody></table>"
    return label


def _describe_cp(cp):
    label = "<table class=\"m-2\"><thead><tr><th>Criticality Phenomenon</th><th>" + \
            str(cp.predicate).split("(")[1].replace(")", "")
    label += "</th></tr></thead><tbody><tr><td>Start time</td><td>"
    time = cp.at_time()
    if isinstance(time, tuple):
        label += str(time[0])
    else:
        label += str(time)
    label += "</td></tr><tr><td>End time</td><td>"
    if isinstance(time, tuple):
        label += str(time[1])
    else:
        label += str(time)
    label += "</td></tr><tr><td>Subject(s)</td><td>"
    if len(cp.subjects) > 0:
        subj_and_classes = phenomena_extraction.get_most_specific_classes(cp.subjects)
        label += "<br />".join([str(x[0]) + " (" + ", ".join(x[1]) + ")" for x in subj_and_classes])
    label += "</td></tr><tr><td>Predicate</td><td>"
    label += str(cp.predicate)
    label += "</td></tr><tr><td>Object(s)</td><td>"
    if len(cp.objects) > 0:
        obj_and_classes = phenomena_extraction.get_most_specific_classes(cp.objects)
        label += "<br />".join([str(x[0]) + " (" + ", ".join(x[1]) + ")" for x in obj_and_classes])
    label += "</td></tr>"
    label += "</tbody></table>"
    return label


#################
# MPLD3 Plugins #
#################

class ToolTipAndClickInfo(mpld3.plugins.PointHTMLTooltip):
    # Handles:
    # 1. the criticality phenomena toggling when clicking on CP subjects (red circles)
    # 2. the mouse-overs when hovering over subjects
    # 3. the Ctrl+Click new window action when clicking on subjects

    JAVASCRIPT = """
    var scene_css = `""" + scene_css + """`
    mpld3.register_plugin("htmltooltip", HtmlTooltipPlugin);
    HtmlTooltipPlugin.prototype = Object.create(mpld3.Plugin.prototype);
    HtmlTooltipPlugin.prototype.constructor = HtmlTooltipPlugin;
    HtmlTooltipPlugin.prototype.requiredProps = ["id"];
    HtmlTooltipPlugin.prototype.defaultProps = {labels:null,
                                                targets_per_cp:null,
                                                cps:null,
                                                hoffset:0,
                                                voffset:10,
                                                targets:null};
    function HtmlTooltipPlugin(fig, props){
        mpld3.Plugin.call(this, fig, props);
    };

    HtmlTooltipPlugin.prototype.draw = function(){
        var obj = mpld3.get_element(this.props.id)
        var labels = this.props.labels
        cps = obj.elements()
        cp_targets = this.props.targets
        cp_targets_per_class = this.props.targets_per_cp
        cp_predicates = this.props.cps
        var tooltip = d3.select("body").append("div")
            .attr("class", "mpld3-tooltip")
            .style("position", "absolute")
            .style("z-index", "10")
            .style("visibility", "hidden");
        
        function show_cp(d, i) {
            if (!window.event.ctrlKey) {
                for (let j = 0; j < cp_targets[i].length; j++) { 
                    var x = mpld3.get_element(cp_targets[i][j]);
                    if (x) {
                        if ("path" in x) {
                            tog = x.path
                        } else if ("obj" in x) {
                            tog = x.obj
                        }
                        for (var k = 0; k < tog._groups.length; k++){
                            for (var l = 0; l < tog._groups[k].length; l++){
                                if (tog._groups[k][l].style.display === "none"){
                                    tog._groups[k][l].style.display = "block"
                                } else {
                                    tog._groups[k][l].style.display = "none"
                                }
                            }
                        }
                    }
                }
            }
        }

        obj.elements()
            .on("mouseover", function(d, i) {
                if (show_tooltips) {
                    tooltip.html(labels[i]).style("visibility", "visible");
                    var long_descrs = document.getElementsByClassName("extended_ind_props")
                    var dots_descrs = document.getElementsByClassName("extended_ind_props_dots")
                    for (let i = 0; i < long_descrs.length; i++) {
                        if(!show_long_ind) {
                            long_descrs[i].style.display = "none";
                        } else {
                            long_descrs[i].style.display = "inline";
                        }
                    }
                    for (let i = 0; i < dots_descrs.length; i++) {
                        if(!show_long_ind) {
                            dots_descrs[i].style.display = "inline";
                        } else {
                            dots_descrs[i].style.display = "none";
                        }
                    }
                }
            })
            .on("mousemove", function(d, i) {
                tooltip
                .style("top", d3.event.pageY + this.props.voffset + "px")
                .style("left",d3.event.pageX + this.props.hoffset + "px");
            }.bind(this))
            .on("mousedown.callout", show_cp)
            .on("mouseout", function(d, i){
                tooltip.style("visibility", "hidden");
            })
            .on("click", function(d, i) {
                if (window.event.ctrlKey) {
                    var newWindow = window.open();
                    newWindow.document.write(
                        `<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-1BmE4kWBq78iYhFldvKuhfTAU6auU8tT94WrHftjDbrCEXSU1oBoqyl2QvZ6jIW3" crossorigin="anonymous">` + scene_css + tooltip.html(labels[i])._groups[0][0].innerHTML
                    );
                }
            });
    };
    """

    def __init__(self, points, labels=None, targets=None, targets_per_cp=None, hoffset=0, voffset=10, css=None):
        targets_ = []
        for x in targets or []:
            x_ = []
            for y in x:
                x_.append(mpld3.utils.get_id(y))
            targets_.append(x_)
        self.targets_per_cp = []
        self.cps = []
        if targets_per_cp:
            self.cps = sorted(targets_per_cp.keys(), key=natural_sort_key)
            for cp in self.cps:
                x_ = []
                for y in targets_per_cp[cp]:
                    x_.append(mpld3.utils.get_id(y))
                self.targets_per_cp.append(x_)
        super().__init__(points, labels, targets_, hoffset, voffset, css)
        self.dict_["targets_per_cp"] = self.targets_per_cp
        self.dict_["cps"] = self.cps


class CPTooltip(mpld3.plugins.PluginBase):
    # Handles the Ctrl+Click action on criticality phenomena ID (opens a new tab).

    JAVASCRIPT = """
    var scene_css = `""" + scene_css + """`
    mpld3.register_plugin("cpstooltip", CPTooltip);
    CPTooltip.prototype = Object.create(mpld3.Plugin.prototype);
    CPTooltip.prototype.constructor = CPTooltip;
    CPTooltip.prototype.requiredProps = ["id", "tooltip_html"];
    function CPTooltip(fig, props){
        mpld3.Plugin.call(this, fig, props);
    };

    CPTooltip.prototype.draw = function(){
        var obj = mpld3.get_element(this.props.id);
        var tooltip_html = this.props.tooltip_html;
        var tooltip = d3.select("body").append("div")
            .attr("class", "cp-tooltip")
            .style("position", "absolute")
            .style("z-index", "10")
            .style("visibility", "hidden");
            
        obj.obj._groups[0][0].onmouseover = function(d, i) {
            tooltip.html(tooltip_html).style("visibility", "visible");
        };
        
        obj.obj._groups[0][0].onmousemove = function(d, i) {
            tooltip
                .style("top", d.clientY + 10 + "px")
                .style("left", d.clientX + 0 + "px");
        }.bind(this);
        
        obj.obj._groups[0][0].onclick = function(d, i) {
            if (window.event.ctrlKey) {
                var newWindow = window.open();
                newWindow.document.write(
                    `<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-1BmE4kWBq78iYhFldvKuhfTAU6auU8tT94WrHftjDbrCEXSU1oBoqyl2QvZ6jIW3" crossorigin="anonymous">` + scene_css + tooltip_html
                );
            }
        };
        
        obj.obj._groups[0][0].onmouseout = function(d, i) {
            tooltip.style("visibility", "hidden");
        };
    }
    """

    def __init__(self, text, cp):
        tooltip_html = _describe_cp(cp)
        self.dict_ = {"type": "cpstooltip",
                      "id": mpld3.utils.get_id(text),
                      "tooltip_html": tooltip_html}
