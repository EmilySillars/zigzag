# Modeling part of an IREE kernel in ZigZag

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

### 1. Ignoring SSRs

- [hardware description](zigzag/inputs/hardware/snitch-cluster-only-floats-no-ssrs.yaml)
- [workload](zigzag/inputs/workload/part-of-iree-kernel.yaml)
- [temporal and spatial mapping](zigzag/inputs/mapping/snitch-cluster-empty-mapping.yaml)
- location to dump output: `outputs_iree_kernel_no_ssrs/`
- [main file](main_iree_kernel_no_ssrs.py)

Command to run:

```
python main_iree_kernel_no_ssrs.py
```

### 2. Naively Modeling SSRs

- [hardware description](zigzag/inputs/hardware/snitch-cluster-only-floats-yes-ssrs.yaml)
- [workload](zigzag/inputs/workload/part-of-iree-kernel.yaml) (same as no. 1)
- [temporal and spatial mapping](zigzag/inputs/mapping/snitch-cluster-empty-mapping.yaml) (same as no. 1)
- location to dump output: `outputs_iree_kernel_yes_ssrs/`
- [main file](main_iree_kernel_yes_ssrs.py)

Command to run:

```
 python main_iree_kernel_yes_ssrs.py 
```