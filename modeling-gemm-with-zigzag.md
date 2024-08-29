# Modeling Gemm Accelerator with ZigZag

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


- Hardware Description: [zigzag/inputs/hardware/gemm.yaml](zigzag/inputs/hardware/gemm.yaml)
- Workload: [matmul-104-x-104.yaml](zigzag/inputs/workload/matmul-104-x-104.yaml)
- Default Mapping File: [matmul-104-x-104-empty-mapping.yaml](zigzag/inputs/mapping/matmul-104-x-104-empty-mapping.yaml)
- location to dump output: `outputs/`
- Main File: [main_zigzag_integration.py](main_zigzag_integration.py)

### II. Command to run:

```
python main_zigzag_integration.py --model=zigzag/inputs/workload/matmul-104-x-104.yaml --mapping=zigzag/inputs/mapping/matmul-104-x-104-empty-mapping.yaml --accelerator=zigzag/inputs/hardware/gemm.yaml
```

### III. Output:
```
2024-08-23 19:36:12,614 - zigzag.parser.workload_factory.__init__ +208 - WARNING - Operator MatMul not defined in mapping. Using default mapping instead.
2024-08-23 19:36:12,626 - zigzag.stages.WorkloadStage.run +52 - INFO - Processing  matmul_104_104...
2024-08-23 19:36:12,626 - zigzag.stages.SpatialMappingGeneratorStage.conditional_log +191 - WARNING - Maximal spatial unrolling of A at D3 limited to 1 due to bandwidth of reg_O
2024-08-23 19:36:12,626 - zigzag.stages.SpatialMappingGeneratorStage.conditional_log +191 - WARNING - Maximal spatial unrolling of B at D3 limited to 1 due to bandwidth of reg_O
2024-08-23 19:36:12,647 - zigzag.stages.SpatialMappingGeneratorStage.run +95 - INFO - matmul_104_104: Launching spatial mapping 1/3 :{D1: {A: 8}, D2: {B: 8}, D3: {C: 8}}.
100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████| 6/6 [00:00<00:00, 1047.79it/s]
2024-08-23 19:36:12,656 - zigzag.stages.SpatialMappingGeneratorStage.run +95 - INFO - matmul_104_104: Launching spatial mapping 2/3 :{D1: {B: 8}, D2: {A: 8}, D3: {C: 8}}.
100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████| 6/6 [00:00<00:00, 1158.65it/s]
2024-08-23 19:36:12,662 - zigzag.stages.SpatialMappingGeneratorStage.run +95 - INFO - matmul_104_104: Launching spatial mapping 3/3 :{D1: {A: 8}, D2: {A: 8}, D3: {C: 8}}.
100%|████████████████████████████████████████████████████████████████████████████████████████████████████████| 120/120 [00:00<00:00, 817.86it/s]
2024-08-23 19:36:12,810 - zigzag.stages.save_stages.run +48 - INFO - Saved CostModelEvaluation(matmul_104_104, core 1) with energy 8.366e+05 and latency 5.107e+03 to outputs/gemm-matmul-104-x-104/matmul_104_104_complete.json
2024-08-23 19:36:13,007 - zigzag.stages.save_stages.run +95 - INFO - Saved CumulativeCME with energy 8.366e+05 and latency 5.107e+03 to outputs/gemm-matmul-104-x-104/overall_simple.json
2024-08-23 19:36:13,007 - zigzag.stages.save_stages.run +150 - INFO - Saved pickled list of 1 CMEs to outputs/gemm-matmul-104-x-104-saved_list_of_cmes.pickle.

```
```
cat outputs/gemm-matmul-104-x-104/loop_ordering.txt 
```

```
Loop ordering for matmul_104_104
==============================================================
Temporal Loops                  O         W         I         
==============================================================
for A in [0, 13):               l3        l1        l1        
--------------------------------------------------------------
  for B in [0, 13):             l1        l1        l1        
--------------------------------------------------------------
    for C in [0, 13):           reg_O     l1        l1        
--------------------------------------------------------------
==============================================================
Spatial Loops                                                 
==============================================================
      parfor A in [0, 8):                                     
--------------------------------------------------------------
      parfor B in [0, 8):                                     
--------------------------------------------------------------
      parfor C in [0, 8):                                     
--------------------------------------------------------------
```

## Manual Examples

For each example, the 

- Hardware Description: [zigzag/inputs/hardware/gemm.yaml](zigzag/inputs/hardware/gemm.yaml)
- Default Mapping File: [matmul-104-x-104-empty-mapping.yaml](zigzag/inputs/mapping/matmul-104-x-104-empty-mapping.yaml)
- location to dump output: `outputs/`
- Main File: [main_zigzag_integration.py](main_zigzag_integration.py)

all remain the same. The only change is the workload file...

### I. Matmul 16 x 16

Workload File: [matmul-16-x-16.yaml](zigzag/inputs/workload/matmul-16-x-16.yaml)

Command:

```
python main_zigzag_integration.py --model=zigzag/inputs/workload/matmul-16-x-16.yaml --mapping=zigzag/inputs/mapping/matmul-104-x-104-empty-mapping.yaml --accelerator=zigzag/inputs/hardware/gemm.yaml
```

Output:

```
cat outputs/gemm-matmul-16-x-16/loop_ordering.txt 
```

```
Loop ordering for matmul_16_x_16
==============================================================
Temporal Loops                  O         W         I         
==============================================================
for A in [0, 2):                l1        l1        l1        
--------------------------------------------------------------
  for B in [0, 2):              l1        l1        l1        
--------------------------------------------------------------
    for C in [0, 2):            reg_O     l1        l1        
--------------------------------------------------------------
==============================================================
Spatial Loops                                                 
==============================================================
      parfor B in [0, 8):                                     
--------------------------------------------------------------
      parfor A in [0, 8):                                     
--------------------------------------------------------------
      parfor C in [0, 8):                                     
--------------------------------------------------------------
```



### II. Matmul 104 x 104

Workload File: [matmul-104-x-104.yaml](zigzag/inputs/workload/matmul-104-x-104.yaml)

Command:

```
python main_zigzag_integration.py --model=zigzag/inputs/workload/matmul-104-x-104.yaml --mapping=zigzag/inputs/mapping/matmul-104-x-104-empty-mapping.yaml --accelerator=zigzag/inputs/hardware/gemm.yaml
```

Output:

```
cat outputs/gemm-matmul-104-x-104/loop_ordering.txt 
```

```
Loop ordering for matmul_104_104
==============================================================
Temporal Loops                  O         W         I         
==============================================================
for A in [0, 13):               l3        l1        l1        
--------------------------------------------------------------
  for B in [0, 13):             l1        l1        l1        
--------------------------------------------------------------
    for C in [0, 13):           reg_O     l1        l1        
--------------------------------------------------------------
==============================================================
Spatial Loops                                                 
==============================================================
      parfor A in [0, 8):                                     
--------------------------------------------------------------
      parfor B in [0, 8):                                     
--------------------------------------------------------------
      parfor C in [0, 8):                                     
--------------------------------------------------------------
```

### 
