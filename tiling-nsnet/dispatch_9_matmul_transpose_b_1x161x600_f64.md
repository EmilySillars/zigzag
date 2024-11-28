# dispatch_9_matmul_transpose_b_1x161x600_f64

[back to landing page](https://github.com/CAPS-UMU/Quidditch/tree/zigzag/zigzag_tiling/grapeFruit/zigzag-tiled-nsnet)

## Linalg Operation

```
%9 = linalg.matmul_transpose_b 
ins(%4, %5 : tensor<1x600xf64>, tensor<161x600xf64>) 
outs(%8 : tensor<1x161xf64>) -> tensor<1x161xf64>
 
```

## In C-like pseudocode

```
matmul_transpose_b (I : tensor<1x600xf64, W : tensor<161x600xf64>, O : tensor<1x161xf64>) {
    for a in [0, 1)
    for b in [0, 161)
    for c in [0, 600)
        O[a][b]+=I[a][c]*W[b][c]
}
```

## As ZigZag Workload

```
- id: 0 
  name: dispatch_9_matmul_transpose_b_1x161x600_f64
  operator_type: Matmul_transpose_b
  equation: O[a][b]+=I[a][c]*W[b][c]
  dimension_relations: []
  loop_dims: [A,B,C]
  loop_sizes: [1, 161, 600] 
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
sh tiling-nsnet.sh dispatch_9_matmul_transpose_b_1x161x600_f64
```

Relevant Output:

```
Loop ordering for dispatch_9_matmul_transpose_b_1x161x600_f64
=============================================================================================
Temporal Loops                      O                  W                  I                  
=============================================================================================
for C in [0, 6):                    rf_f0_thru_f31     l3                 l1                 
---------------------------------------------------------------------------------------------
  for C in [0, 4):                  rf_f0_thru_f31     l1                 l1                 
---------------------------------------------------------------------------------------------
    for C in [0, 5):                rf_f0_thru_f31     l1                 l1                 
---------------------------------------------------------------------------------------------
      for C in [0, 5):              rf_f0_thru_f31     l1                 rf_f0_thru_f31     
---------------------------------------------------------------------------------------------
        for B in [0, 3):            rf_f0_thru_f31     l1                 rf_f0_thru_f31     
---------------------------------------------------------------------------------------------
          for B in [0, 7):          rf_f0_thru_f31     l1                 rf_f0_thru_f31     
---------------------------------------------------------------------------------------------
=============================================================================================
Spatial Loops                                                                                
=============================================================================================
            parfor B in [0, 7):                                                              
---------------------------------------------------------------------------------------------
            parfor C in [0, 1):                                                              
---------------------------------------------------------------------------------------------
```

## Interpret Results

Tile only to L1:

```
Loop ordering for dispatch_9_matmul_transpose_b_1x161x600_f64
=============================================================================================
Temporal Loops                      O                  W                  I                  
=============================================================================================
for C in [0, 6):                    rf_f0_thru_f31     l3                 l1                 
---------------------------------------------------------------------------------------------
  for C in [0, 4):                  rf_f0_thru_f31     l1                 l1    
```

```
loop_dims: [A,B,C]
loop_sizes: [1, 161, 600] 
new_loop_bounds = [1, 1, 6]
new_loop_bounds2 = [1, 1, 4]
tile_sizes = loop_sizes / new_loop_bounds = [1, 161, 600] / [1, 1, 6] = [1, 161, 100]
tile_sizes2 = tile_sizes / new_loop_bounds2 = [1, 161, 100] / [1, 1, 4] = [1, 161, 25]
```

Quidditch does not support second level tiling, so let's just provide tile sizes when ALL operands are in L1: `[1, 161, 25]`

```
l1Tiles[0] = 0;
l1Tiles[1] = 161;
l1Tiles[2] = 25;
l1Interchange = {0, 1, 2}; 
```

## JSON Summary

```
{
    "bounds":[[1], [1], [24]],
    "order":[[0,0], [1,0], [2,0]]
}
```

# Part II: Debugging

### Is the ZigZag plan correct?

Actual JSON output:

```
"temporal_mapping": {
            "O": [
                [
                    "(B, 7)",
                    "(B, 3)",
                    "(C, 5)",
                    "(C, 5)",
                    "(C, 4)",
                    "(C, 6)"
                ], // register file
                [],
                []
            ],
            "I": [
                [
                    "(B, 7)",
                    "(B, 3)",
                    "(C, 5)"
                ], // register file
                [
                    "(C, 5)",
                    "(C, 4)",
                    "(C, 6)"
                ], // L1
                []
            ],
            "W": [
                [],
                [
                    "(B, 7)",
                    "(B, 3)",
                    "(C, 5)",
                    "(C, 5)",
                    "(C, 4)"
                ],
                [
                    "(C, 6)"
                ] //L3
            ]
        }
```

spatial:

```
"spatial_mapping": {
            "O": [ [],["(C, 1)"
                ],
                [],
                [
                    "(B, 7)"
                ]
            ],
            "W": [
                [],
                [
                    "(C, 1)"
                ],
                [],
                [
                    "(B, 7)"
                ]
            ],
            "I": [
                [],
                [
                    "(C, 1)"
                ],
                [],
                [
                    "(B, 7)"
                ]
            ]
        },
```

Sent Arne an email.
