# Modeling Snitch with ZigZag

## Setup

1. Clone this forked ZigZag repo: `git clone https://github.com/EmilySillars/zigzag.git`

2. Make sure you can see remote branches: `git fetch origin`

3. Checkout this branch: `git checkout manual-examples`

4. Install dependencies

   - create conda environment:

     ```
     conda create -n zigzag-env python=3.11
     ```

   - install requirements inside the environment

     ```
     source activate base
     conda activate zigzag-env
     pip install -r requirements.txt
     ```

   - When you are finished using ZigZag, deactivate conda environment with

     ```
     conda deactivate zigzag-env
     ```

## Run

### I. Inputs needed

To run ZigZag, you need to specify a **hardware description**, a **workload**, a **default temporal and spatial mapping**, and a folder **location to dump the output**. We specify these file paths as arguments to a python main file that runs ZigZag.

![image-20240626163738939](snitch_cluster_only_integers.png)

- Hardware Description: [snitch-cluster-only-integers.yaml](zigzag/inputs/hardware/snitch-cluster-only-integers.yaml)
- Workload: [matmul-104-x-104.yaml](zigzag/inputs/workload/matmul-104-x-104.yaml)
- Default Mapping File: [matmul-104-x-104-empty-mapping.yaml](zigzag/inputs/mapping/matmul-104-x-104-empty-mapping.yaml)
- location to dump output: `outputs/`
- Main File: [main_zigzag_integration.py](main_zigzag_integration.py)

### II. Command to run:

```
python main_zigzag_integration.py --model=zigzag/inputs/workload/matmul-104-x-104.yaml --mapping=zigzag/inputs/mapping/matmul-104-x-104-empty-mapping.yaml --accelerator=zigzag/inputs/hardware/snitch-cluster-only-integers.yaml
```

### III. Output:
```
python main_zigzag_integration.py --model=zigzag/inputs/workload/matmul-104-x-104.yaml --mapping=zigzag/inputs/mapping/matmul-104-x-104-empty-mapping.yaml --accelerator=zigzag/inputs/hardware/snitch-cluster-only-integers.yaml
2024-08-23 19:56:28,105 - zigzag.parser.workload_factory.__init__ +208 - WARNING - Operator MatMul not defined in mapping. Using default mapping instead.
2024-08-23 19:56:28,117 - zigzag.stages.WorkloadStage.run +52 - INFO - Processing  matmul_104_104...
2024-08-23 19:56:28,117 - zigzag.stages.SpatialMappingGeneratorStage.run +95 - INFO - matmul_104_104: Launching spatial mapping 1/3 :{D1: {C: 8}}.
100%|████████████████████████████████████████████████████████████████████████████████████████████████████████| 720/720 [00:00<00:00, 973.11it/s]
2024-08-23 19:56:28,859 - zigzag.stages.SpatialMappingGeneratorStage.run +95 - INFO - matmul_104_104: Launching spatial mapping 2/3 :{D1: {B: 8}}.
100%|████████████████████████████████████████████████████████████████████████████████████████████████████████| 720/720 [00:00<00:00, 998.09it/s]
2024-08-23 19:56:29,581 - zigzag.stages.SpatialMappingGeneratorStage.run +95 - INFO - matmul_104_104: Launching spatial mapping 3/3 :{D1: {A: 8}}.
100%|████████████████████████████████████████████████████████████████████████████████████████████████████████| 720/720 [00:00<00:00, 959.67it/s]
2024-08-23 19:56:30,343 - zigzag.stages.save_stages.run +48 - INFO - Saved CostModelEvaluation(matmul_104_104, core 1) with energy 3.362e+06 and latency 2.966e+05 to outputs/snitch-cluster-only-integers-matmul-104-x-104/matmul_104_104_complete.json
2024-08-23 19:56:30,546 - zigzag.stages.save_stages.run +95 - INFO - Saved CumulativeCME with energy 3.362e+06 and latency 2.966e+05 to outputs/snitch-cluster-only-integers-matmul-104-x-104/overall_simple.json
2024-08-23 19:56:30,547 - zigzag.stages.save_stages.run +150 - INFO - Saved pickled list of 1 CMEs to outputs/snitch-cluster-only-integers-matmul-104-x-104-saved_list_of_cmes.pickle.
```
```
cat outputs/snitch-cluster-only-integers-matmul-104-x-104/loop_ordering.txt 
```

```
Loop ordering for matmul_104_104
===========================================================================================
Temporal Loops                    O                  W                  I                  
===========================================================================================
for A in [0, 8):                  l3                 l1                 l3                 
-------------------------------------------------------------------------------------------
  for B in [0, 13):               l3                 l1                 l1                 
-------------------------------------------------------------------------------------------
    for C in [0, 2):              rf_x1_thru_x31     l1                 l1                 
-------------------------------------------------------------------------------------------
      for C in [0, 13):           rf_x1_thru_x31     l1                 l1                 
-------------------------------------------------------------------------------------------
        for C in [0, 4):          rf_x1_thru_x31     rf_x1_thru_x31     rf_x1_thru_x31     
-------------------------------------------------------------------------------------------
          for A in [0, 13):       rf_x1_thru_x31     rf_x1_thru_x31     rf_x1_thru_x31     
-------------------------------------------------------------------------------------------
===========================================================================================
Spatial Loops                                                                              
===========================================================================================
            parfor B in [0, 8):                                                            
-------------------------------------------------------------------------------------------
```

