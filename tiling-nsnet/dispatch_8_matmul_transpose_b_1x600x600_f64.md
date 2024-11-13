# dispatch_8_matmul_transpose_b_1x600x600_f64
[back to landing page](https://github.com/CAPS-UMU/Quidditch/tree/zigzag/zigzag_tiling/grapeFruit/zigzag-tiled-nsnet)

## Linalg Operation

```
%9 = linalg.matmul_transpose_b 
ins(%4, %5 : tensor<1x600xf64>, tensor<600x600xf64>) 
outs(%8 : tensor<1x600xf64>) -> tensor<1x600xf64>
 
```

## In C-like pseudocode

```
matmul_transpose_b (I : tensor<1x600xf64, W : tensor<600x600xf64>, O : tensor<1x600xf64>) {
    for a in [0, 1)
    for b in [0, 600)
    for c in [0, 600)
        O[a][b]+=I[a][c]*[b][c]
}
```

## As ZigZag Workload

```
- id: 0 
  name: dispatch_8_matmul_transpose_b_1x600x600_f64
  operator_type: Matmul_transpose_b
  equation: O[a][b]+=I[a][c]*W[b][c]
  dimension_relations: []
  loop_dims: [A,B,C]
  loop_sizes: [1, 600, 600] 
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

Command Run:

```
sh tiling-nsnet.sh dispatch_8_matmul_transpose_b_1x600x600_f64
```

Relevant Output:

```
Loop ordering for dispatch_8_matmul_transpose_b_1x600x600_f64
=============================================================================================
Temporal Loops                      O                  W                  I                  
=============================================================================================
for B in [0, 3):                    l1                 l3                 l1                 
---------------------------------------------------------------------------------------------
  for C in [0, 20):                 rf_f0_thru_f31     l3                 l1                 
---------------------------------------------------------------------------------------------
    for C in [0, 6):                rf_f0_thru_f31     l1                 l1                 
---------------------------------------------------------------------------------------------
      for C in [0, 5):              rf_f0_thru_f31     l1                 rf_f0_thru_f31     
---------------------------------------------------------------------------------------------
        for B in [0, 5):            rf_f0_thru_f31     l1                 rf_f0_thru_f31     
---------------------------------------------------------------------------------------------
          for B in [0, 5):          rf_f0_thru_f31     l1                 rf_f0_thru_f31     
---------------------------------------------------------------------------------------------
=============================================================================================
Spatial Loops                                                                                
=============================================================================================
            parfor B in [0, 8):                                                              
---------------------------------------------------------------------------------------------
            parfor A in [0, 1):                                                              
---------------------------------------------------------------------------------------------
```

## Interpret Results

Only tile to L1 level:

```
Loop ordering for dispatch_8_matmul_transpose_b_1x600x600_f64
=============================================================================================
Temporal Loops                      O                  W                  I                  
=============================================================================================
for B in [0, 3):                    l1                 l3                 l1                 
---------------------------------------------------------------------------------------------
  for C in [0, 20):                 rf_f0_thru_f31     l3                 l1                 
---------------------------------------------------------------------------------------------
    for C in [0, 6):                rf_f0_thru_f31     l1                 l1      
```

```
loop_dims: [A,B,C]
loop_sizes: [1, 600, 600]
new_loop_bounds = [1, 3, 20]
new_loop_bounds2 = [1, 1, 6]
tile_sizes = loop_size / loop_bounds = [1, 600, 600] / [1, 3, 20] = [1, 200, 30]
tile_sizes2 = tile_sizes / loop_bounds2 = [1, 200, 30] / [1, 1, 6] = [1, 1, 5]
No loop interchange.
```

But Quidditch can do second level tiling! So let's give it the tile sizes when ALL operands are in L1: `[1, 200, 5]`

```
l1Tiles[0] = 0;
l1Tiles[1] = 200;
l1Tiles[2] = 5;
l1Interchange = {0, 1, 2}; 
```

## JSON Summary

```
{
    "bounds":[[1], [3], [120]],
    "order":[[0,0], [1,0], [2,0]]
}
```

