import logging
import re

from zigzag.api import get_hardware_performance_zigzag
from zigzag.parser.arguments import get_arg_parser

# for the gemm accelerator 16x16 example, we use the following options
# --model=zigzag/inputs/workload/matmul-16-x-16.yaml \
# --mapping=zigzag/inputs/mapping/matmul-104-x-104-empty-mapping.yaml \
# --accelerator=zigzag/inputs/hardware/gemm.yaml

# for the gemm accelerator 104x104 example, we use the following options
# --model=zigzag/inputs/workload/matmul-104-x-104.yaml \
# --mapping=zigzag/inputs/mapping/matmul-104-x-104-empty-mapping.yaml \
# --accelerator=zigzag/inputs/hardware/gemm.yaml


parser = get_arg_parser()
args = parser.parse_args()

# Initialize the logger
logging_level = logging.INFO
logging_format = "%(asctime)s - %(name)s.%(funcName)s +%(lineno)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging_level, format=logging_format)

hw_name = (args.accelerator.split(".")[-2]).split("/")[-1]
workload_name = (args.model.split(".")[-2]).split("/")[-1]
experiment_id = f"{hw_name}-{workload_name}"
pickle_name = f"{experiment_id}-saved_list_of_cmes"


dump_folder = f"outputs/{experiment_id}"
pickle_filename = f"outputs/{pickle_name}.pickle"


get_hardware_performance_zigzag(
    accelerator=args.accelerator,
    workload=args.model,
    mapping=args.mapping,
    opt="latency",
    dump_folder=f"outputs/{experiment_id}",
    pickle_filename=f"outputs/{pickle_name}.pickle",
)

# Cost Model Stages used by the api function "get_hardware_performance_zigzag":
    # stages = [
    #     # Parse the ONNX Model into the workload
    #     workload_parser_stage,
    #     # Parse the accelerator module/passthrough given accelerator
    #     AcceleratorParserStage,
    #     # Save the summed CME energy and latency to a json
    #     SimpleSaveStage,
    #     # Save all received CMEs in a list to a pickle file
    #     PickleSaveStage,
    #     # Sum up the received best CME across all layers of the workload
    #     SumStage,
    #     # Search the lowest allowed memory level per operand per layer
    #     SearchInterLayerDataLocalityStage if do_exploint_inter_layer_locality else None,
    #     # Iterate through the different layers in the workload
    #     WorkloadStage,
    #     # Save the chosen loop ordering and memory hierarchy
    #     VisualizationStage,
    #     # Remove unused memories
    #     ExploitInterLayerDataLocalityStage if do_exploint_inter_layer_locality else None,
    #     # Save each processed layer to a json
    #     CompleteSaveStage,
    #     # Reduce all CMEs, returning minimal energy/latency one
    #     opt_stage,
    #     # Generate multiple spatial mappings (SM)
    #     SpatialMappingGeneratorStage,
    #     # Reduce all CMEs, returning minimal energy/latency one
    #     opt_stage,
    #     # Generate multiple temporal mappings (TM)
    #     TemporalMappingGeneratorStage,
    #     # Evaluate generated SM and TM through cost model
    #     CostModelStage,
    # ]
