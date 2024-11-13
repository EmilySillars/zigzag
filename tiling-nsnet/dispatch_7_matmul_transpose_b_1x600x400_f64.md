# dispatch_7_matmul_transpose_b_1x600x400_f64
[back to landing page](https://github.com/CAPS-UMU/Quidditch/tree/zigzag/zigzag_tiling/grapeFruit/zigzag-tiled-nsnet)

## Linalg Operation

```
%9 = linalg.matmul_transpose_b 
ins(%4, %5 : tensor<1x400xf64>, tensor<600x400xf64>) 
outs(%8 : tensor<1x600xf64>) -> tensor<1x600xf64>
 
```

## In C-like pseudocode

```
matmul_transpose_b (I : tensor<1x400xf64, W : tensor<600x400xf64>, O : tensor<1x600xf64>) {
    for a in [0, 1)
    for b in [0, 600)
    for c in [0, 400)
        O[a][b]+=I[a][c]*W[b][c]
}
```

## As ZigZag Workload

```
- id: 0 
  name: dispatch_7_matmul_transpose_b_1x600x400_f64
  operator_type: Matmul_transpose_b
  equation: O[a][b]+=I[a][c]*W[b][c]
  dimension_relations: []
  loop_dims: [A,B,C]
  loop_sizes: [1, 600, 400] 
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
sh tiling-nsnet.sh dispatch_7_matmul_transpose_b_1x600x400_f64
```

Relevant Output:

```
Loop ordering for dispatch_7_matmul_transpose_b_1x600x400_f64
=============================================================================================
Temporal Loops                      O                  W                  I                  
=============================================================================================
for C in [0, 2):                    l1                 l3                 l1                 
---------------------------------------------------------------------------------------------
  for B in [0, 20):                 l1                 l3                 l1                 
---------------------------------------------------------------------------------------------
    for C in [0, 5):                rf_f0_thru_f31     l1                 l1                 
---------------------------------------------------------------------------------------------
      for C in [0, 5):              rf_f0_thru_f31     l1                 l1                 
---------------------------------------------------------------------------------------------
        for B in [0, 6):            rf_f0_thru_f31     l1                 rf_f0_thru_f31     
---------------------------------------------------------------------------------------------
          for B in [0, 5):          rf_f0_thru_f31     l1                 rf_f0_thru_f31     
---------------------------------------------------------------------------------------------
=============================================================================================
Spatial Loops                                                                                
=============================================================================================
            parfor C in [0, 8):                                                              
---------------------------------------------------------------------------------------------
            parfor C in [0, 1):                                                              
---------------------------------------------------------------------------------------------
```

## Interpret Results

Quidditch only tiles to L1

```
Loop ordering for dispatch_7_matmul_transpose_b_1x600x400_f64
=============================================================================================
Temporal Loops                      O                  W                  I                  
=============================================================================================
for C in [0, 2):                    l1                 l3                 l1                 
---------------------------------------------------------------------------------------------
  for B in [0, 20):                 l1                 l3                 l1                 
---------------------------------------------------------------------------------------------
    for C in [0, 5):                rf_f0_thru_f31     l1                 l1              
```

Recall operand sizes: `I : tensor<1x400xf64, W : tensor<600x400xf64>, O : tensor<1x600xf64>)`

Recall mac operation inside loops: `O[a][b]+=I[a][c]*transpose(W)[b][c]`

```
loop_dims: [A, B, C]
loop_sizes: [1, 600, 400]
new_loop_bounds: [1, 20, 2]
new_loop_bounds2: [1, 1, 5]
tile_sizes = loop_sizes / new_loop_bounds = [1, 600, 400] / [1, 2, 20] = [1, 30, 200]
tile_sizes2 = tile_sizes / new_loop_bounds2 = [1, 30, 200] / [1, 1, 5] = [1, 1, 40]
original loop order: [A, B, C] = [0, 1, 2]
new loop order: [0, 1, 2] (no change)
```

But Quidditch can do second level tiling! So let's give it the tile sizes when ALL operands are in L1: `[1, 30, 40]`

```
l1Tiles[0] = 0;
l1Tiles[1] = 30;
l1Tiles[2] = 40;
l1Interchange = {0, 1, 2}; 
```

## JSON Summary

```
{
    "bounds":[[1], [30], [10]],
    "order":[[0,0], [1,0], [2,0]]
}
```
