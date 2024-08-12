import os
import sys
import argparse
import re

from zigzag.stages.MainStage import MainStage
from zigzag.stages.WorkloadParserStage import WorkloadParserStage
from zigzag.stages.AcceleratorParserStage import AcceleratorParserStage
from zigzag.stages.save_stages import SimpleSaveStage
from zigzag.stages.WorkloadStage import WorkloadStage
from zigzag.stages.SpatialMappingGeneratorStage import SpatialMappingGeneratorStage
from zigzag.stages.reduce_stages import MinimalLatencyStage
from zigzag.stages.temporal_mapping_generator_stage import TemporalMappingGeneratorStage
from zigzag.stages.CostModelStage import CostModelStage
from zigzag.visualization.results.plot_cme import (
    bar_plot_cost_model_evaluations_breakdown,
)

# Get the onnx model, the mapping and accelerator arguments
parser = argparse.ArgumentParser(description="Setup zigzag inputs")
parser.add_argument(
    "--model",
    metavar="path",
    required=False,
    default="zigzag/inputs/workload/matmul-104-x-104.yaml",
    help="path to onnx model, e.g. zigzag/inputs/workload/my_model.onnx",
)
parser.add_argument(
    "--mapping",
    metavar="path",
    required=False,
    default="zigzag/inputs/mapping/snitch-cluster-only-integers-mapping.yaml",
    help="path to mapping file, e.g., zigzag/inputs/mapping/my_mapping.yaml",
)
parser.add_argument(
    "--accelerator",
    metavar="path",
    required=False,
    default="zigzag/inputs/hardware/snitch-cluster-only-integers.yaml",
    help="module path to the accelerator, e.g. zigzag/inputs/hardware/my_accelerator.yaml",
)
args = parser.parse_args()

# Initialize the logger
import logging as _logging

_logging_level = _logging.INFO
# _logging_format = "%(asctime)s - %(funcName)s +%(lineno)s - %(levelname)s - %(message)s"
_logging_format = "%(asctime)s - %(levelname)s - %(message)s"
_logging.basicConfig(level=_logging_level, format=_logging_format)

hw_name = args.accelerator.split(".")[-1]
wl_name = re.split(r"/|\.", args.model)[-1]
if wl_name == "onnx":
    wl_name = re.split(r"/|\.", args.model)[-2]
experiment_id = f"{hw_name}-{wl_name}"

# Initialize the MainStage which will start execution.
# The first argument of this init is the list of stages that will be executed in sequence.
# The second argument of this init are the arguments required for these different stages.
mainstage = MainStage(
    [  # Initializes the MainStage as entry point
        WorkloadParserStage,  # Parses the manual definition into the workload
        AcceleratorParserStage,  # Parses the accelerator
        SimpleSaveStage,
        WorkloadStage,  # Iterates through the different layers in the workload
        SpatialMappingGeneratorStage,  # Generates multiple spatial mappings (SM)
        MinimalLatencyStage,  # Reduces all CMEs, returning minimal latency one
        TemporalMappingGeneratorStage,  # find "best" temporal mapping
        CostModelStage,  # Evaluates generated SM and TM through cost model
    ],
    accelerator=args.accelerator,  # required by AcceleratorParserStage
    workload=args.model,  # required by ONNXModelParserStage
    mapping=args.mapping,  # required by ONNXModelParserStage
    dump_folder=f"outputs/",  # where outputs will be saved to
    loma_lpf_limit=6,  # required by LomaStage
    loma_show_progress_bar=True,  # shows a progress bar while iterating over temporal mappings
)

# Launch the MainStage
answers = mainstage.run()

cme = answers[0][0]

from zigzag.visualization.results.print_mapping import get_temporal_spatial_loops, print_mapping

print_mapping(cme)

fname = "outputs/matmul_104_104_simple.json"

with open(fname, 'r') as fin:
    print(fin.read())