import zigzag.api
from zigzag.visualization.results.print_mapping import print_mapping
from zigzag.visualization.graph.memory_hierarchy import visualize_memory_hierarchy_graph # debugging only

# mapping= "zigzag/inputs/mapping/emily-gemm.yaml" # gives ex 10 output
# accelerator = "zigzag/inputs/hardware/gemm.yaml" # gives ex 10 output
mapping= "zigzag/inputs/mapping/emily-snitch-cc-mapping.yaml"
accelerator = "zigzag/inputs/hardware/emily-snitch-riscv32imafd.yaml"
# takes in workload generated from a run of xdsl_opt_main.py
workload = "emily-workload.yaml"


answers = zigzag.api.get_hardware_performance_zigzag(workload, accelerator, mapping, "latency", "emily-zigzag-outputs/","emily-zigzag-outputs/list_of_cmes.pickle")

cme = answers[2][0][0]
visualize_memory_hierarchy_graph(cme.accelerator.cores[0].memory_hierarchy) # debugging only
print_mapping(cme)

# WORKFLOW 
# create conda environment:
# conda create -n zigzag-yaml 

# then install requirements:
# conda activate zigzag-yaml
# pip install -r requirements.txt

# run zigzag with workload and hardware description:
# rm emily-zigzag-outputs/loop_ordering.txt; python emily-run_zigzag.py 

# to deactivate environment:
# conda deactivate zigzag-yaml

