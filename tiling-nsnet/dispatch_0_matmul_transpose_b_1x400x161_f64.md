# dispatch_0_matmul_transpose_b_1x400x161_f64
[back to landing page](https://github.com/CAPS-UMU/Quidditch/tree/zigzag/zigzag_tiling/grapeFruit/zigzag-tiled-nsnet)

## Linalg Operation

```
%9 = linalg.matmul_transpose_b 
ins(%4, %5 : tensor<1x161xf64>, tensor<400x161xf64>) 
outs(%8 : tensor<1x400xf64>) -> tensor<1x400xf64>  
```

## In C-like pseudocode

```
matmul_transpose_b (I : tensor<1x161xf64, W : tensor<400x161xf64>, O : tensor<1x400xf64>) {
    for a in [0, 1)
    for b in [0, 161)
    for c in [0, 400)
        O[a][b]+=I[a][c]*transpose(W)[b][c]
}
```

## As ZigZag Workload

```
- id: 0 
  name: dispatch_0_matmul_transpose_b_1x400x161_f64
  operator_type: Matmul_transpose_b
  equation: O[a][b]+=I[a][c]*W[b][c]
  dimension_relations: []
  loop_dims: [A,B,C]
  loop_sizes: [1, 161, 400]
  operand_precision:
    W: 64
    I: 64
    O: 64
    O_final: 64
  operand_source:
    I: 0
    W: 0
```

## ZigZag Run

Commands run:

```
python main_zigzag_integration.py --model=zigzag/inputs/workload/dispatch_0_matmul_transpose_b_1x400x161_f64.yaml --mapping=zigzag/inputs/mapping/empty-mapping.yaml --accelerator=zigzag/inputs/hardware/snitch-cluster-only-floats-no-ssrs.yaml
```

```
cat outputs/snitch-cluster-only-floats-no-ssrs-dispatch_0_matmul_transpose_b_1x400x161_f64/loop_ordering.txt
```

Output:

```
Loop ordering for dispatch_0_matmul_transpose_b_1x400x161_f64
===========================================================================================
Temporal Loops                    O                  W                  I                  
===========================================================================================
for B in [0, 7):                  l1                 l1                 l1                 
-------------------------------------------------------------------------------------------
  for C in [0, 5):                rf_f0_thru_f31     l1                 l1                 
-------------------------------------------------------------------------------------------
    for C in [0, 5):              rf_f0_thru_f31     l1                 l1                 
-------------------------------------------------------------------------------------------
      for C in [0, 2):            rf_f0_thru_f31     l1                 rf_f0_thru_f31     
-------------------------------------------------------------------------------------------
        for B in [0, 23):         rf_f0_thru_f31     l1                 rf_f0_thru_f31     
-------------------------------------------------------------------------------------------
===========================================================================================
Spatial Loops                                                                              
===========================================================================================
          parfor C in [0, 8):                                                              
-------------------------------------------------------------------------------------------
          parfor A in [0, 1):                                                              
-------------------------------------------------------------------------------------------
```

## Interpret Results

Since everything fits in L1, don't tile at all?!

No loop interchange either?!

```
l1Tiles[0] = 0;
l1Tiles[1] = 0;
l1Tiles[2] = 0;
l1Interchange = {0, 1, 2}; 
```

## JSON Summary

```
{
    "bounds":[[1], [1], [1]],
    "order":[[0,0], [1,0], [2,0]]
}
```

