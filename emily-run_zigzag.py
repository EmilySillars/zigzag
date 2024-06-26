import zigzag.api
from zigzag.visualization.results.print_mapping import print_mapping
from zigzag.visualization.graph.memory_hierarchy import visualize_memory_hierarchy_graph # debugging only


#workload = "zigzag/inputs/workload/matmul-104-x-104.yaml"
workload = "zigzag/inputs/workload/resnet18.yaml"      # debugging
mapping = "zigzag/inputs/mapping/tpu_like.yaml"         # debugging
accelerator = "zigzag/inputs/hardware/tpu_like.yaml"   # debugging

# THREE OPTIONS
# OPTION 1: SINGLE INTEGER COMPUTE CORE
accelerator = "zigzag/inputs/hardware/snitch-cc-only-integers.yaml"  
mapping = "zigzag/inputs/mapping/snitch-cc-only-integers-mapping.yaml"   

# OPTION 2: SINGLE FLOAT COMPUTE CORE
# todo

# OPTION 3: CLUSTER OF 8 FLOAT COMPUTE CORES
# todo


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

