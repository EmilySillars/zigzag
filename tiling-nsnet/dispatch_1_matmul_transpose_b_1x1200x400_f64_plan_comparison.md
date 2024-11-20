# Compare tiling for dispatch_1_matmul_transpose_b_1x1200x400_f64

[back to landing page](https://github.com/CAPS-UMU/Quidditch/tree/zigzag/zigzag_tiling/grapeFruit/zigzag-tiled-nsnet)

UPDATE: I think I made a mistake. I get a "cannot fit in L1" error when trying to tile this kernel with the ZigZag tilling configuration.

Redo-ing this comparison except with dispatch 8...

Let's compare the output tiling plan to what Quidditch actually does!

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
    for b in [0, 1200)
    for c in [0, 400)       
    O[a][b] += I[a][c] * W[b][c]
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
  loop_sizes: [1, 1200, 400] 
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
sh tiling-nsnet.sh dispatch_1_matmul_transpose_b_1x1200x400_f64
```

Output:

```
Loop ordering for dispatch_1_matmul_transpose_b_1x1200x400_f64
=============================================================================================
Temporal Loops                      O                  W                  I                  
=============================================================================================
for C in [0, 5):                    l1                 l3                 l1                 
---------------------------------------------------------------------------------------------
  for B in [0, 5):                  l1                 l3                 l1                 
---------------------------------------------------------------------------------------------
    for C in [0, 5):                rf_f0_thru_f31     l1                 l1                 
---------------------------------------------------------------------------------------------
      for C in [0, 16):             rf_f0_thru_f31     l1                 l1                 
---------------------------------------------------------------------------------------------
        for B in [0, 6):            rf_f0_thru_f31     l1                 rf_f0_thru_f31     
---------------------------------------------------------------------------------------------
          for B in [0, 5):          rf_f0_thru_f31     l1                 rf_f0_thru_f31     
---------------------------------------------------------------------------------------------
=============================================================================================
Spatial Loops                                                                                
=============================================================================================
            parfor B in [0, 8):                                                              
---------------------------------------------------------------------------------------------
            parfor B in [0, 1):                                                              
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
  for B in [0, 5):                  l1                 l3                 l1                 
---------------------------------------------------------------------------------------------
    for C in [0, 5):                rf_f0_thru_f31     l1                 l1                           

```

Recall: `O[a][b]+=I[a][c]*W[b][c]`

```
 Zigzag Input:
 loop_dims: [A,B,C]
 loop_sizes: [1, 1200, 400] 
 
 Zigzag Output:
 new_loop_bounds = [1, 5, 5], new_loop_bounds_2 = [1, 1, 5]
 tile_sizes = loop_size / new_loop_bounds = [1, 1200, 400] / [1, 5, 5] = [1, 240, 80]
 tile_sizes2 = tile_sizes / new_loop_bounds_2 = [1, 240, 80] / [1, 1, 5] = [1, 1, 40]

```

BUT, Quidditch cannot handle second level tiling! So let's give it the **tile size of each dimension *once they fit in L1***:

```
l1Tiles[0] = 0;
l1Tiles[1] = 240;
l1Tiles[2] = 40;
Which as a list of bounds is [1, 5, 10]

Original Order was [A, B, C] = [0, 1, 2], and now we have C, B, C but Quidditch can't do multi-level tiling and A not mentioned.
l1Interchange = {0, 1, 2}; // no change because we remove the first level of C tiling that Quidditch can't do, ignore A. 
```

## JSON Summary

```
{
    "bounds":[[1], [5], [10]],
    "order":[[0,0], [1,0], [2,0]]
}
```

## NsNet2: Tile Sizes = [0, 40, 100]

```
NsNet: O[a][b] += I[a][c] * W[b][c]
 A is 1      l1Tiles[0]
 B is 1200   l1Tiles[40]
 C is 400    l1Tiles[100]
 
 // see mlir taken from Quidditch output after L1 Level Tiling, then after Thread Level Tiling
 matmul_transpose_b (I : tensor<1x400xf64, W : tensor<1200x400xf64>, O : tensor<1x1200xf64>) // tile (A, 1) (B, 1200) (C,400)
 matmul_transpose_b (I :  tensor<1x100xf64>, W: tensor<40x100xf64>, O : tensor <1x40xf64> )  // tile (A, 1) (B, 40) (C, 100)
 matmul_transpose_b (I : tensor<1x100xf64>, W : tensor<5x100xf64>, O :tensor<1x5xf64> )      // tile (A, 1) (B, 5) (C, 1)
 
 Loop Bounds are
 A 1 // arbitrarily placed
 B 30
 C 4
 B 8 // spatial
 B 5
 C 100
 
 // but recall that the quidditch default interchange is [2, 0, 1] -> [C, B, A]
 // see mlir taken from Quidditch output after Thread Level Tiling
 %c40 = arith.constant 40 : index
 %c1200 = arith.constant 1200 : index
 %c100 = arith.constant 100 : index
 %c400 = arith.constant 400 : index
 %c0 = arith.constant 0 : index
 scf.for %arg0 = %c0 to %c400 step %c100 iter_args(%arg1 = %23) -> (tensor<1x1200xf64>)  // C tile size of 100; 4 steps!
 scf.for %arg2 = %c0 to %c1200 step %c40 iter_args(%arg3 = %arg1) -> (tensor<1x1200xf64>) // B tile size of 40; 30 steps!
 scf.forall (%arg4) = (0) to (40) step (5) shared_outs(%arg5 = %32) -> (tensor<1x40xf64>) // B spatial loop; 8 steps!
 // A loop occurs inside linalg.matmul_tanspose_b
 
 So actual Quidditch Loop Bounds are
 C 4
 B 30
 B 8   // spatial
 A 1   // inside linalg.matmul_tanspose_b
 B 5   // inside linalg.matmul_tanspose_b
 C 100 // inside linalg.matmul_tanspose_b
 
```

Equivalent ZigZag Mapping for these loop bounds:

```
- name: default
  core_allocation: [1]
  spatial_mapping:
    D2:
      - B, 8
  temporal_ordering:
    - [C, 4]
    - [B, 30]
    - [B, 5]
    - [C, 100]
  memory_operand_links:
    O: O
    W: I2
    I: I1
```

### Estimated Latency from ZigZag

```
sh tiling-nsnet-custom-mapping.sh dispatch_1_matmul_transpose_b_1x1200x400_f64 1200x400-quidditch-mapping
```

```
{
    "energy": 87679256.0,
    "latency": 196155.0
}
```

## GrapeFruit: Tile Sizes = [0, 240, 40]

```
 inside linalg.matmul_tanspose_b
 B 30
 C 40GrapeFruit : O[a][b] += I[a][c] * W[b][c]
  A is 1      l1Tiles[0]
  B is 1200   l1Tiles[240]
  C is 400    l1Tiles[40]
 
// see mlir taken from Quidditch output after L1 Level Tiling, then after Thread Level Tiling
 matmul_transpose_b (I : tensor<1x400xf64, W : tensor<1200x400xf64>, O : tensor<1x1200xf64>) // tile (A, 1) (B, 1200) (C, 400)
 matmul_transpose_b (I : tensor<1x40xf64>, W : tensor<240x40xf64>, O : tensor<1x240xf64>)    // tile (A, 1) (B, 240) (C, 40)
 matmul_transpose_b (I : tensor<1x40xf64>, W : tensor<30x40xf64>, O : tensor<1x30xf64>)      // tile (A, 1) (B, 30) (C, 1)

So Quidditch Loop Bounds are
A 1 // arbitrarily placed
B 5
C 10
B 8 // spatial

// What about interchange and the rest of the loop bounds though?

// see mlir taken from Quidditch output after Thread Level Tiling
%c40 = arith.constant 40 : index
%c400 = arith.constant 400 : index
%c240 = arith.constant 240 : index
%c1200 = arith.constant 1200 : index
%c0 = arith.constant 0 : index
%c32_i64 = arith.constant 32 : i64
%cst = arith.constant 0.000000e+00 : f64
scf.for %arg0 = %c0 to %c1200 step %c240 iter_args(%arg1 = %23) -> (tensor<1x1200xf64>) // B tile of size 240; 5 steps!
scf.for %arg2 = %c0 to %c400 step %c40 iter_args(%arg3 = %arg1) -> (tensor<1x1200xf64>) // C tile of size 40; 10 steps!
scf.forall (%arg4) = (0) to (240) step (30) shared_outs(%arg5 = %32) -> (tensor<1x240xf64>) B // spatial loop; 8 steps!
// A loop occurs inside linalg.matmul_tanspose_b

So actual Quidditch Loop Bounds are
B 5
C 10
B 8  // spatial
A 1  // inside linalg.matmul_tanspose_b
B 30 // inside linalg.matmul_tanspose_b
C 40 // inside linalg.matmul_tanspose_b
```

Equivalent ZigZag mapping for these loop bounds:

```
- name: default
  core_allocation: [1]
    spatial_mapping:
    D2:
      - B, 8
  temporal_ordering:
    - [B, 5]
    - [C, 10]
    - [A, 1]
    - [B, 30]
    - [C, 40]
  memory_operand_links:
    O: O
    W: I2
    I: I1
```

### Estimated Latency from ZigZag

```
sh tiling-nsnet-custom-mapping.sh dispatch_1_matmul_transpose_b_1x1200x400_f64 1200x400-zigzag-nerfed-mapping
```

```
{
    "energy": 82386792.0,
    "latency": 137664.0
}
```

## ZigZag Estimation vs Quidditch Performance

| Name                | Latency Estimation        | Actual Latency |
| ------------------- | ------------------------- | -------------- |
| NsNet2              | 196155.0                  | 1318981        |
| GrapeFruit          | 137664.0                  | 11104854       |
| NsNet2 / GrapeFruit | 1.424882322175732 ~ 1.42x |                |

```
/home/hoppip/Quidditch/toolchain/bin/snitch_cluster.vlt /home/hoppip/Quidditch/build/runtime/samples/nsnet2/NsNet2
/home/hoppip/Quidditch/toolchain/bin/snitch_cluster.vlt /home/hoppip/Quidditch/build/runtime/samples/grapeFruit/GrapeFruit
```
