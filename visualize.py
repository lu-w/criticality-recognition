import argparse
import logging
import os
import tempfile

import owlready2

from pyauto import auto
from pyauto.visualizer import visualizer

# Instantiate the parser
from criticality_recognition import phenomena_extraction

parser = argparse.ArgumentParser(description="Visualization of criticality phenomena within inferred A.U.T.O. A-Boxes.")
parser.add_argument("--cps", type=str, default="natural", metavar="{natural, csv, csv-file, none}",
                    help="Whether and how to print criticality phenomena to stdout (or a file in the visualization "
                         "output folder (see --output) in case of csv-file). Default: natural")
parser.add_argument("--logging", type=str, metavar="{critical, error, warning, info, debug}", help="Log level. Default:"
                                                                                                   " info")
parser.add_argument("--output", type=str, nargs="?", default="/tmp/", metavar="FOLDER",
                    help="Optional. Store visualizations (folder with HTML files) in the given folder. Default: /tmp/")
parser.add_argument("input", type=str, metavar="FILE", help="Input file. One .owl file containing exactly one scenario "
                                                            "to visualize")
parser.add_argument("--no-visualization", action="store_true", help="If flag is set, does not produce visualization.")
args = parser.parse_args()

# Log configuration
logger = logging.getLogger(__name__)
logging.basicConfig(format="%(asctime)s %(levelname)s  %(message)s", datefmt="%H:%M:%S")
loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
if args.logging == "critical":
    log_lvl = logging.CRITICAL
elif args.logging == "error":
    log_lvl = logging.ERROR
elif args.logging == "warning":
    log_lvl = logging.WARNING
elif args.logging == "info":
    log_lvl = logging.INFO
elif args.logging == "debug":
    log_lvl = logging.DEBUG
else:
    log_lvl = logging.INFO
loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
for logger in loggers:
    logger.setLevel(log_lvl)
logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)
logging.getLogger("shapely.geos").setLevel(logging.WARNING)

# Extraction & Visualization
scenario = args.input
logger.info("Loading scenario from " + str(scenario))
world = owlready2.get_ontology("file://" + os.path.abspath(scenario)).load().world

# Extract CP objects
logger.info("Extracting criticality phenomena from scenario")
cps = phenomena_extraction.phenomena_scenario(world)

# Visualize
tmp_dir = tempfile.gettempdir()
if not args.no_visualization:
    logger.info("Creating visualization for scenario")
    tmp_dir = visualizer.visualize_scenario(world, cps)

if args.cps != "none":
    # Print CPs
    cps_list = phenomena_extraction.list_cps(cps, args.cps, world=world, print_non_visualizable_info=True)
    if args.cps != "csv-file":
        print(cps_list)
    else:
        csv_file_name = tmp_dir + "/cps_scenario.csv"
        with open(csv_file_name, "w+") as csv_file:
            csv_file.write(cps_list)
            logger.info("CSV file with criticality phenomena is available at: file://" + str(csv_file_name))
