import os
import sys
import argparse
import re

from zigzag.stages.MainStage import MainStage
from zigzag.stages.WorkloadParserStage import WorkloadParserStage
from zigzag.stages.AcceleratorParserStage import AcceleratorParserStage
from zigzag.stages.save_stages import CompleteSaveStage
from zigzag.stages.WorkloadStage import WorkloadStage
from zigzag.stages.SpatialMappingGeneratorStage import SpatialMappingGeneratorStage
from zigzag.stages.reduce_stages import MinimalLatencyStage
from zigzag.stages.LomaStage import LomaStage
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
        CompleteSaveStage,  # Saves all received CMEs information to a json
        WorkloadStage,  # Iterates through the different layers in the workload
        SpatialMappingGeneratorStage,  # Generates multiple spatial mappings (SM)
        MinimalLatencyStage,  # Reduces all CMEs, returning minimal latency one
        LomaStage,  # find "best" temporal mapping
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
# Plot the energy and latency breakdown of our cost model evaluation
cme = answers[0][0]
save_path = "outputs/breakdown.png"
bar_plot_cost_model_evaluations_breakdown([cme], save_path=save_path, xtick_rotation=0)
from zigzag.visualization.results.print_mapping import print_mapping
print_mapping(cme)
mem_names = [ml.memory_instance.name for ml in cme.mem_level_list]
stall_slacks = cme.SS_comb_collect
print("Stall and slack per port of each memory instance:")
for mem_name, ports_ss in zip(mem_names, stall_slacks):
    print(f"  {mem_name}: {ports_ss}")
print(f"Latency: {cme.latency_total2:.3e}")