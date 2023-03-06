import argparse
import logging

import owlready2
import os
import psutil

from pyauto import auto
from criticality_recognition import criticality_recognition, phenomena_extraction
import omega2auto
from inputs import example_fuc_2_3

# Instantiate the parser
parser = argparse.ArgumentParser(description="Inference of criticality phenomena with A.U.T.O. Performs criticality "
                                             "phenomena reasoning on either an A.U.T.O. A-Box or an OMEGA hdf5 file.")
parser.add_argument("--auto", type=str, default="auto/ontology", metavar="FOLDER_PATH",
                    help="Path to folder with A.U.T.O. Default: auto/ontology")
parser.add_argument("--format", type=str, default="natural", metavar="{csv, natural, none}",
                    help="Whether and how to print the criticality phenomena output. Default: natural")
parser.add_argument("--output", type=str, nargs="?", metavar="FILE", help="Optional. Store the resulting inferences in "
                                                                          "an output file")
parser.add_argument("--convert-only", action="store_true", help="If flag is set, does not run any inferencing. It "
                                                                "only converts the inputs into A.U.T.O. and (if, "
                                                                "--output is given) stores them (one OWL file for "
                                                                "each scenario)")
parser.add_argument("--memory", type=int, metavar="N", help="Maximum memory (GB) for Pellet JVM. Default: 70 percent of"
                                                            " available RAM")
parser.add_argument("--scenarios", type=int, nargs="+", metavar="N", help="The ID(s) of the scenario to analyze. "
                                                                          "Default: Empty, therefore all fitting "
                                                                          "scenarios.")
parser.add_argument("--start", type=float, metavar="N", help="Optional start offset (added) for scenarios (in s).")
parser.add_argument("--end", type=float, metavar="N", help="Optional end offset (subtracted) for scenarios (in s).")
parser.add_argument("--hertz", type=float, metavar="N", help="The sampling rate to reduce the input scenarios to. Can "
                                                             "also be a fraction. Default: 1 Hz.")
parser.add_argument("--logging", type=str, metavar="{critical, error, warning, info, debug}", help="Log level. Default:"
                                                                                                   " info")
parser.add_argument("--pellet-output", action="store_true", help="If flag is set, shows Pellet's output")
parser.add_argument("input", type=str, metavar="FILE", help="Input file. A .hdf5 file in OMEGA-format or the string \""
                                                            "fuc23\" (will run the provided use case example)")
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

# Java memory
if args.memory:
    owlready2.reasoning.JAVA_MEMORY = args.memory
else:
    owlready2.reasoning.JAVA_MEMORY = int((psutil.virtual_memory().available >> 20) * 0.7)  # using 70% of available RAM
logger.info("Pellet will use a maximum of " + str(owlready2.reasoning.JAVA_MEMORY) + " MB RAM.")

# Reading inputs
if args.input.endswith(".hdf5"):
    scenarios = omega2auto.convert(os.path.abspath(args.input), args.auto, cp=True, scenarios=args.scenarios,
                                      sampling_rate=args.hertz, start_offset=args.start, end_offset=args.end)
elif args.input == "fuc23":
    scenarios = [example_fuc_2_3.get_fuc23_worlds()]
else:
    scenarios = []
    logger.info("No scenarios found - is this the right file name?")

# Augmentation & reasoning for every scenario
for i, scenario_worlds in enumerate(scenarios):
    logger.info("Criticality reasoning on scenario " + str(i + 1) + "/" + str(len(scenarios)) + " (" +
                str(len(scenario_worlds)) + " scenes) ...")

    scenario = criticality_recognition.reason_scenario(scenario_worlds, pellet_output=args.pellet_output,
                                                       no_reasoning=args.convert_only, scenario_number=i + 1)

    # Nicer scenario name for FUC 2.3
    if args.input == "fuc23":
        scenario.search(type=auto.get_ontology(auto.Ontology.Traffic_Model, scenario).Scenario)[0].identifier = \
            "Functional Use Case 2.3"

    # Printing inferences
    cps = phenomena_extraction.phenomena_scenario(scenario)
    cps_list = phenomena_extraction.list_cps(cps, args.format)
    if args.format != "none":
        print(cps_list)

    # Saving OWL
    if args.output:
        if len(scenarios) > 1:
            number = "_" + str(i + 1)
        else:
            number = ""
        scenario_owl_file = args.output.replace(".owl", "") + number + ".owl"
        scenario.save(scenario_owl_file)
        logger.info("Saved scenario " + str(i + 1) + "/" + str(len(scenarios)) + " to file://" + os.path.abspath(
            scenario_owl_file))
