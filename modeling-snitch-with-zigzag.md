# Modeling Snitch with ZigZag

## Setup

1. Clone this forked ZigZag repo: `git clone https://github.com/EmilySillars/zigzag.git`

2. Make sure you can see remote branches: `git fetch origin`

3. Checkout this branch: `git checkout manual-examples`

4. Install dependencies

   - create conda environment:

     ```
     conda create -n zigzag-env
     ```

   - install requirements inside the environment

     ```
     conda activate zigzag-env
     pip install -r requirements.txt
     ```

   - When you are finished using ZigZag, deactivate conda environment with

     ```
     conda deactivate zigzag-env
     ```

## Run

To run ZigZag, you need to specify a **hardware description**, a **workload**, a **default temporal and spatial mapping**, and a folder **location to dump the output**. We specify these file paths inside a `main.py` file that runs ZigZag.

### I. matmul on Snitch Cluster

![image-20240626163738939](cluster.png)

- [Hardware Description](zigzag/inputs/hardware/snitch-cluster-only-integers.yaml)
- [Workload](zigzag/inputs/workload/matmul-104-x-104.yaml)
- [Default Mapping File](zigzag/inputs/mapping/snitch-cluster-empty-mapping.yaml)
- location to dump output: `outputs/`
- [main file](main_snitch_cluster_only_integers.py)

Command to run:

```
python main_snitch_cluster_only_integers.py
```

Output:

```
2024-07-12 13:33:06,339 - WARNING - Operator MatMul not defined in mapping. Using default mapping instead.
2024-07-12 13:33:06,353 - INFO - Processing  matmul_104_104...
2024-07-12 13:33:06,355 - INFO - matmul_104_104: Launching spatial mapping 1/3 :{D1: {B: 1}, D2: {B: 8}}.
100%|████████████████████████████████████████| 720/720 [00:01<00:00, 608.26it/s]
2024-07-12 13:33:07,542 - INFO - Saved CostModelEvaluation(matmul_104_104, core 1) with energy 1.228e+07 and latency 2.965e+05 to outputs//matmul_104_104_complete.json
2024-07-12 13:33:07,542 - INFO - matmul_104_104: Launching spatial mapping 2/3 :{D1: {B: 1}, D2: {A: 8}}.
100%|████████████████████████████████████████| 720/720 [00:01<00:00, 595.16it/s]
2024-07-12 13:33:08,754 - INFO - Saved CostModelEvaluation(matmul_104_104, core 1) with energy 1.228e+07 and latency 2.965e+05 to outputs//matmul_104_104_complete.json
2024-07-12 13:33:08,754 - INFO - matmul_104_104: Launching spatial mapping 3/3 :{D1: {B: 1}, D2: {C: 8}}.
100%|████████████████████████████████████████| 720/720 [00:01<00:00, 601.82it/s]
2024-07-12 13:33:09,952 - INFO - Saved CostModelEvaluation(matmul_104_104, core 1) with energy 4.730e+07 and latency 2.990e+05 to outputs//matmul_104_104_complete.json
Loop ordering for matmul_104_104
=============================================================================================
Temporal Loops                      W                  O                  I                  
=============================================================================================
for B in [0, 13):                   l1                 l3                 l1                 
---------------------------------------------------------------------------------------------
  for A in [0, 8):                  l1                 l1                 l1                 
---------------------------------------------------------------------------------------------
    for C in [0, 13):               l1                 rf_x1_thru_x31     l1                 
---------------------------------------------------------------------------------------------
      for C in [0, 4):              rf_x1_thru_x31     rf_x1_thru_x31     l1                 
---------------------------------------------------------------------------------------------
        for C in [0, 2):            rf_x1_thru_x31     rf_x1_thru_x31     rf_x1_thru_x31     
---------------------------------------------------------------------------------------------
          for A in [0, 13):         rf_x1_thru_x31     rf_x1_thru_x31     rf_x1_thru_x31     
---------------------------------------------------------------------------------------------
=============================================================================================
Spatial Loops                                                                                
=============================================================================================
            parfor B in [0, 8):                                                              
---------------------------------------------------------------------------------------------
            parfor B in [0, 1):                                                              
---------------------------------------------------------------------------------------------

Stall and slack per port of each memory instance:
  rf_x1_thru_x31: {'r_port_1': 152760, 'w_port_1': 0}
  l1: {'rw_port_1': 0}
  l3: {'rw_port_1': 0}
Latency: 2.965e+05
```

