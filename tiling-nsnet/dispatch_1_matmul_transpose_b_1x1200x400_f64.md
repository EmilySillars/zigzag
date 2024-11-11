# dispatch_1_matmul_transpose_b_1x1200x400_f64

[back to landing page](https://github.com/CAPS-UMU/Quidditch/tree/zigzag/zigzag_tiling/grapeFruit/zigzag-tiled-nsnet)

## Linalg Operation

```
%22 = linalg.matmul_transpose_b 
ins(%17, %18 : tensor<1x400xf64>, tensor<1200x400xf64>) 
outs(%21 : tensor<1x1200xf64>) -> tensor<1x1200xf64>  
```

## In C-like pseudocode

```
matmul_transpose_b (I : tensor<1x400xf64, W : tensor<1200x400xf64>, O : tensor<1x1200xf64>) {
    for a in [0, 1)
    for b in [0, 400)
    for c in [0, 1200)
                            
}
```

## As ZigZag Workload

```
- id: 0 
  name: dispatch_1_matmul_transpose_b_1x1200x400_f64  # name can be used to specify mapping
  operator_type: Matmul_transpose_b # operator_type can be used to specify mapping
  equation: O[a][b]+=I[a][c]*W[b][c]
  dimension_relations: []
  loop_dims: [A,B,C]
  loop_sizes: [1, 400, 1200] 
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

Commands Run:

```
python main_zigzag_integration.py --model=zigzag/inputs/workload/dispatch_1_matmul_transpose_b_1x1200x400_f64.yaml --mapping=zigzag/inputs/mapping/empty-mapping.yaml --accelerator=zigzag/inputs/hardware/snitch-cluster-only-floats-no-ssrs.yaml
```

```
cat outputs/snitch-cluster-only-floats-no-ssrs-dispatch_1_matmul_transpose_b_1x1200x400_f64/loop_ordering.txt
```

Output:

```
Loop ordering for dispatch_1_matmul_transpose_b_1x1200x400_f64
=============================================================================================
Temporal Loops                      O                  W                  I                  
=============================================================================================
for C in [0, 5):                    l1                 l3                 l1                 
---------------------------------------------------------------------------------------------
  for B in [0, 16):                 l1                 l3                 l1                 
---------------------------------------------------------------------------------------------
    for C in [0, 5):                rf_f0_thru_f31     l1                 l1                 
---------------------------------------------------------------------------------------------
      for C in [0, 6):              rf_f0_thru_f31     l1                 rf_f0_thru_f31     
---------------------------------------------------------------------------------------------
        for B in [0, 5):            rf_f0_thru_f31     l1                 rf_f0_thru_f31     
---------------------------------------------------------------------------------------------
          for B in [0, 5):          rf_f0_thru_f31     l1                 rf_f0_thru_f31     
---------------------------------------------------------------------------------------------
=============================================================================================
Spatial Loops                                                                                
=============================================================================================
            parfor C in [0, 8):                                                              
---------------------------------------------------------------------------------------------
            parfor A in [0, 1):                                                              
---------------------------------------------------------------------------------------------
```

## Interpret Results

If we only care about tiling to the L1 level, tiling scheme looks like

```
Loop ordering for dispatch_1_matmul_transpose_b_1x1200x400_f64
=============================================================================================
Temporal Loops                      O                  W                  I                  
=============================================================================================
for C in [0, 5):                    l1                 l3                 l1                 
---------------------------------------------------------------------------------------------
  for B in [0, 16):                 l1                 l3                 l1                 
---------------------------------------------------------------------------------------------
...
```

```
Loop-Dims: [A, B, C]
Loop-Sizes: [1, 400, 1200]
Loop-Tiles = Loop-Sizes / [1, 16, 5] = [1, 400, 1200]  /  [1,  16, 5] = [1, 25, 240]
Old Loop Order: A, B, C = 0, 1, 2.
New Loop Order: A, C, B = 0, 2, 1.
```

BUT when we feed to the upstream mlir tiling function, the transpose part of the operation has not occurred yet - need to pass tile sizes [1, 240, 25], to match the tensor size of `1200x400xf64>` ...

```
l1Tiles[0] = 0;
l1Tiles[1] = 240;
l1Tiles[2] = 25;
l1Interchange = {0, 2, 1}; 
```

## JSON Summary

```
{
    "bounds":[[1], [16], [5]],
    "order":[[0,0], [2,0], [1,0]]
}
```
