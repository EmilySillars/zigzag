# Latency Estimate:

# dispatch_8_matmul_transpose_b_1x600x600_f64

[back to landing page](https://github.com/CAPS-UMU/Quidditch/tree/zigzag/zigzag_tiling/grapeFruit/zigzag-tiled-nsnet)

## ZigZag-y Tiling

### Input to Quidditch Tiling Pass

Linalg Operation:

```
%9 = linalg.matmul_transpose_b 
ins(%4, %5 : tensor<1x600xf64>, tensor<600x600xf64>) 
outs(%8 : tensor<1x600xf64>) -> tensor<1x600xf64>
```

ZigZag-recommended tiling and loop interchange configuration:

```
l1Tiles[0] = 0;
l1Tiles[1] = 200;
l1Tiles[2] = 5;
l1Interchange = {0, 1, 2}; 
```

- *Note that tile sizes of [0, 200, 5] correspond to zigzag bounds of [1, 3, 120] because [1, 600, 600] / [1, 200, 5] = [1, 3, 120]*
- Dimension B will be unrolled spatially

### Equivalent Input to ZigZag

ZigZag Workload: [dispatch_8_matmul_transpose_b_1x600x600_f64.yaml](../zigzag/inputs/workload/dispatch_8_matmul_transpose_b_1x600x600_f64.yaml)

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

Temporal and Spatial Mappings: [1x600x600-zigzag-nerfed-mapping.yaml](../zigzag/inputs/mapping/1x600x600-zigzag-nerfed-mapping.yaml)

```
- name: default
  core_allocation: [1]
  spatial_mapping:
    D2:
      - B, 8
  temporal_ordering:
    - [B, 3]
    - [C, 120]
    - [C, 5]
    - [B, 25]
  memory_operand_links:
    O: O
    W: I2
    I: I1
```

### ZigZag Run

```
sh tiling-nsnet-custom-mapping.sh dispatch_8_matmul_transpose_b_1x600x600_f64 1x600x600-zigzag-nerfed-mapping
```

```
{
    "energy": 62038202.0,
    "latency": 107527.0
}
```

## Original Quidditch Tiling

### Input to Quidditch Tiling Pass

Linalg Operation:

```
%9 = linalg.matmul_transpose_b 
ins(%4, %5 : tensor<1x600xf64>, tensor<600x600xf64>) 
outs(%8 : tensor<1x600xf64>) -> tensor<1x600xf64>
```

Original tiling and loop interchange configuration:

```
 SmallVector<int64_t> l1Interchange = {2, 0, 1}; // C, A, B
 l1Tiles[0] = 0;
 l1Tiles[1] = 40;
 l1Tiles[2] = 100;
```

- *Note that tile sizes of [0, 40, 100] correspond to zigzag bounds of [1, 15, 6] because [1, 600, 600] / [1, 40, 100] = [1, 15, 6]*
- Dimension B gets spatially unrolled

### Equivalent Input to ZigZag

ZigZag Workload: [dispatch_8_matmul_transpose_b_1x600x600_f64.yaml](../zigzag/inputs/workload/dispatch_8_matmul_transpose_b_1x600x600_f64.yaml) (same as above)

Temporal and Spatial Mappings: [1x600x600-quidditch-mapping.yaml](../zigzag/inputs/mapping/1x600x600-quidditch-mapping.yaml)

```
- name: default
  core_allocation: [1]
  spatial_mapping:
    D2:
      - B, 8
  temporal_ordering:
    - [C, 6]
    - [B, 15]
    - [C, 100]
    - [B, 5]
  memory_operand_links:
    O: O
    W: I2
    I: I1
```

### ZigZag Run

```
sh tiling-nsnet-custom-mapping.sh dispatch_8_matmul_transpose_b_1x600x600_f64 1x600x600-quidditch-mapping
```

```
{
    "energy": 59842680.4,
    "latency": 144731.0
}
```

## Extra Notes: dispatch 8 tiled original Quidditch Style

```
<eval_with_key>.0 from /home/hoppip/Quidditch/venv/lib/python3.11/site-packages/torch/fx/experimental/proxy_tensor.py:551 in wrapped:105:0: warning: SLICEDCUCUMBER tiling level Thread This is the rewritten kernel!!!!!

/home/hoppip/Quidditch/runtime/samples/nsnet2/NsNet2.py:90:0: note: called from
<eval_with_key>.0 from /home/hoppip/Quidditch/venv/lib/python3.11/site-packages/torch/fx/experimental/proxy_tensor.py:551 in wrapped:105:0: note: see current operation: 
func.func @main$async_dispatch_8_matmul_transpose_b_1x600x600_f64() attributes {translation_info = #iree_codegen.translation_info<None>} {
  %c40 = arith.constant 40 : index
  %c100 = arith.constant 100 : index
  %c600 = arith.constant 600 : index
  %cst = arith.constant 0.000000e+00 : f64
  %c0 = arith.constant 0 : index
  %c17841600 = arith.constant 17841600 : index
  %c20721600 = arith.constant 20721600 : index
  %c4800 = arith.constant 4800 : index
  %0 = hal.interface.binding.subspan set(0) binding(0) type(storage_buffer) alignment(64) offset(%c0) flags(ReadOnly) : !flow.dispatch.tensor<readonly:tensor<1x600xf64>>
  %1 = hal.interface.binding.subspan set(0) binding(1) type(storage_buffer) alignment(64) offset(%c17841600) flags(ReadOnly) : !flow.dispatch.tensor<readonly:tensor<600x600xf64>>
  %2 = hal.interface.binding.subspan set(0) binding(1) type(storage_buffer) alignment(64) offset(%c20721600) flags(ReadOnly) : !flow.dispatch.tensor<readonly:tensor<1x600xf64>>
  %3 = hal.interface.binding.subspan set(0) binding(2) type(storage_buffer) alignment(64) offset(%c4800) : !flow.dispatch.tensor<writeonly:tensor<1x600xf64>>
  %4 = flow.dispatch.tensor.load %3, offsets = [0, 0], sizes = [1, 600], strides = [1, 1] : !flow.dispatch.tensor<writeonly:tensor<1x600xf64>> -> tensor<1x600xf64>
  %5 = flow.dispatch.tensor.load %0, offsets = [0, 0], sizes = [1, 600], strides = [1, 1] : !flow.dispatch.tensor<readonly:tensor<1x600xf64>> -> tensor<1x600xf64>
  %6 = flow.dispatch.tensor.load %1, offsets = [0, 0], sizes = [600, 600], strides = [1, 1] : !flow.dispatch.tensor<readonly:tensor<600x600xf64>> -> tensor<600x600xf64>
  %7 = flow.dispatch.tensor.load %2, offsets = [0, 0], sizes = [1, 600], strides = [1, 1] : !flow.dispatch.tensor<readonly:tensor<1x600xf64>> -> tensor<1x600xf64>
  %8 = tensor.empty() : tensor<1x600xf64>
  %result, %token = dma.start_tensor_copy of %8 to #quidditch_snitch.l1_encoding  -> tensor<1x600xf64>
  %9 = dma.wait_for_tensor_copy of %8 : tensor<1x600xf64> to %result using %token -> tensor<1x600xf64>
  
  // fill a 1x600 size tensor with zeroes in parallel (using the 8 compute cores)
  %10 = scf.forall (%arg0) = (0) to (600) step (75) shared_outs(%arg1 = %9) -> (tensor<1x600xf64>) {
    %extracted_slice = tensor.extract_slice %arg1[0, %arg0] [1, 75] [1, 1] : tensor<1x600xf64> to tensor<1x75xf64>
    %16 = linalg.fill ins(%cst : f64) outs(%extracted_slice : tensor<1x75xf64>) -> tensor<1x75xf64>
    scf.forall.in_parallel {
      tensor.parallel_insert_slice %16 into %arg1[0, %arg0] [1, 75] [1, 1] : tensor<1x75xf64> into tensor<1x600xf64>
    }
  }
  
  // tile dimension C by tile size of 100
  %11 = scf.for %arg0 = %c0 to %c600 step %c100 iter_args(%arg1 = %10) -> (tensor<1x600xf64>) {
    %extracted_slice = tensor.extract_slice %5[0, %arg0] [1, 100] [1, 1] : tensor<1x600xf64> to tensor<1x100xf64>
    %result_6, %token_7 = dma.start_tensor_copy of %extracted_slice to #quidditch_snitch.l1_encoding  -> tensor<1x100xf64>
    %16 = dma.wait_for_tensor_copy of %extracted_slice : tensor<1x100xf64> to %result_6 using %token_7 -> tensor<1x100xf64>
   
   // tile dimension B by tile size of 40
   %17 = quidditch_snitch.pipeline %c0 to %c600 step %c40 inits(%arg1) -> tensor<1x600xf64> {
    ^bb0(%arg2: index, %arg3: tensor<1x600xf64>):
      %extracted_slice_8 = tensor.extract_slice %6[%arg2, %arg0] [40, 100] [1, 1] : tensor<600x600xf64> to tensor<40x100xf64>
      %result_9, %token_10 = dma.start_tensor_copy of %extracted_slice_8 to #quidditch_snitch.l1_encoding  -> tensor<40x100xf64>
      %extracted_slice_11 = tensor.extract_slice %arg3[0, %arg2] [1, 40] [1, 1] : tensor<1x600xf64> to tensor<1x40xf64>
      %result_12, %token_13 = dma.start_tensor_copy of %extracted_slice_11 to #quidditch_snitch.l1_encoding  -> tensor<1x40xf64>
      quidditch_snitch.pipeline_yield %arg3, %extracted_slice_8, %result_9, %token_10, %extracted_slice_11, %result_12, %token_13 : tensor<1x600xf64>, tensor<40x100xf64>, tensor<40x100xf64>, !dma.token, tensor<1x40xf64>, tensor<1x40xf64>, !dma.token
    }, {
    ^bb0(%arg2: index, %arg3: tensor<1x600xf64>, %arg4: tensor<40x100xf64>, %arg5: tensor<40x100xf64>, %arg6: !dma.token, %arg7: tensor<1x40xf64>, %arg8: tensor<1x40xf64>, %arg9: !dma.token):
      %18 = dma.wait_for_tensor_copy of %arg4 : tensor<40x100xf64> to %arg5 using %arg6 -> tensor<40x100xf64>
      %19 = dma.wait_for_tensor_copy of %arg7 : tensor<1x40xf64> to %arg8 using %arg9 -> tensor<1x40xf64>
      
      // tile dimension B by tile size of 5 
      %20 = scf.forall (%arg10) = (0) to (40) step (5) shared_outs(%arg11 = %19) -> (tensor<1x40xf64>) {
        %extracted_slice_8 = tensor.extract_slice %16[0, 0] [1, 100] [1, 1] : tensor<1x100xf64> to tensor<1x100xf64>
        %extracted_slice_9 = tensor.extract_slice %18[%arg10, 0] [5, 100] [1, 1] : tensor<40x100xf64> to tensor<5x100xf64>
        %extracted_slice_10 = tensor.extract_slice %arg11[0, %arg10] [1, 5] [1, 1] : tensor<1x40xf64> to tensor<1x5xf64>
        %21 = linalg.matmul_transpose_b {lowering_config = #quidditch_snitch.lowering_config<
        l1_tiles = [0, 40, 100], 
        l1_tiles_interchange = [2, 0, 1], 
        dual_buffer = true>} 
        ins(%extracted_slice_8, %extracted_slice_9 : tensor<1x100xf64>, tensor<5x100xf64>) 
        outs(%extracted_slice_10 : tensor<1x5xf64>) -> tensor<1x5xf64>
        scf.forall.in_parallel {
          tensor.parallel_insert_slice %21 into %arg11[0, %arg10] [1, 5] [1, 1] : tensor<1x5xf64> into tensor<1x40xf64>
        }
      }
      %inserted_slice = tensor.insert_slice %20 into %arg3[0, %arg2] [1, 40] [1, 1] : tensor<1x40xf64> into tensor<1x600xf64>
      quidditch_snitch.pipeline_yield %inserted_slice : tensor<1x600xf64>
    }
    scf.yield %17 : tensor<1x600xf64>
  }
  
  // addition operation
  %result_0, %token_1 = dma.start_tensor_copy of %11 to #quidditch_snitch.l1_encoding  -> tensor<1x600xf64>
  %12 = dma.wait_for_tensor_copy of %11 : tensor<1x600xf64> to %result_0 using %token_1 -> tensor<1x600xf64>
  %result_2, %token_3 = dma.start_tensor_copy of %7 to #quidditch_snitch.l1_encoding  -> tensor<1x600xf64>
  %13 = dma.wait_for_tensor_copy of %7 : tensor<1x600xf64> to %result_2 using %token_3 -> tensor<1x600xf64>
  %result_4, %token_5 = dma.start_tensor_copy of %4 to #quidditch_snitch.l1_encoding  -> tensor<1x600xf64>
  %14 = dma.wait_for_tensor_copy of %4 : tensor<1x600xf64> to %result_4 using %token_5 -> tensor<1x600xf64>
  %15 = scf.forall (%arg0) = (0) to (600) step (75) shared_outs(%arg1 = %14) -> (tensor<1x600xf64>) {
    %extracted_slice = tensor.extract_slice %12[0, %arg0] [1, 75] [1, 1] : tensor<1x600xf64> to tensor<1x75xf64>
    %extracted_slice_6 = tensor.extract_slice %13[0, %arg0] [1, 75] [1, 1] : tensor<1x600xf64> to tensor<1x75xf64>
    %extracted_slice_7 = tensor.extract_slice %arg1[0, %arg0] [1, 75] [1, 1] : tensor<1x600xf64> to tensor<1x75xf64>
    %16 = linalg.generic {indexing_maps = [affine_map<(d0, d1) -> (d0, d1)>, affine_map<(d0, d1) -> (d0, d1)>, affine_map<(d0, d1) -> (d0, d1)>], iterator_types = ["parallel", "parallel"]} ins(%extracted_slice, %extracted_slice_6 : tensor<1x75xf64>, tensor<1x75xf64>) outs(%extracted_slice_7 : tensor<1x75xf64>) {
    ^bb0(%in: f64, %in_8: f64, %out: f64):
      %17 = arith.addf %in, %in_8 : f64
      %18 = arith.cmpf ugt, %17, %cst : f64
      %19 = arith.select %18, %17, %cst : f64
      linalg.yield %19 : f64
    } -> tensor<1x75xf64>
    scf.forall.in_parallel {
      tensor.parallel_insert_slice %16 into %arg1[0, %arg0] [1, 75] [1, 1] : tensor<1x75xf64> into tensor<1x600xf64>
    }
  }
  flow.dispatch.tensor.store %15, %3, offsets = [0, 0], sizes = [1, 600], strides = [1, 1] : tensor<1x600xf64> -> !flow.dispatch.tensor<writeonly:tensor<1x600xf64>>
  return
}
```

## Extra Notes: dispatch 8 tiled ZigZag-y Style

```
<eval_with_key>.0 from /home/hoppip/Quidditch/venv/lib/python3.11/site-packages/torch/fx/experimental/proxy_tensor.py:551 in wrapped:105:0: warning: SLICEDCUCUMBER tiling level Thread This is the rewritten kernel!!!!!

/home/hoppip/Quidditch/runtime/samples/grapeFruit/grapeFruit.py:90:0: note: called from
<eval_with_key>.0 from /home/hoppip/Quidditch/venv/lib/python3.11/site-packages/torch/fx/experimental/proxy_tensor.py:551 in wrapped:105:0: note: see current operation: 
func.func @main$async_dispatch_8_matmul_transpose_b_1x600x600_f64() attributes {translation_info = #iree_codegen.translation_info<None>} {
  %c5 = arith.constant 5 : index
  %c200 = arith.constant 200 : index
  %c600 = arith.constant 600 : index
  %cst = arith.constant 0.000000e+00 : f64
  %c0 = arith.constant 0 : index
  %c17841600 = arith.constant 17841600 : index
  %c20721600 = arith.constant 20721600 : index
  %c4800 = arith.constant 4800 : index
  %0 = hal.interface.binding.subspan set(0) binding(0) type(storage_buffer) alignment(64) offset(%c0) flags(ReadOnly) : !flow.dispatch.tensor<readonly:tensor<1x600xf64>>
  %1 = hal.interface.binding.subspan set(0) binding(1) type(storage_buffer) alignment(64) offset(%c17841600) flags(ReadOnly) : !flow.dispatch.tensor<readonly:tensor<600x600xf64>>
  %2 = hal.interface.binding.subspan set(0) binding(1) type(storage_buffer) alignment(64) offset(%c20721600) flags(ReadOnly) : !flow.dispatch.tensor<readonly:tensor<1x600xf64>>
  %3 = hal.interface.binding.subspan set(0) binding(2) type(storage_buffer) alignment(64) offset(%c4800) : !flow.dispatch.tensor<writeonly:tensor<1x600xf64>>
  %4 = flow.dispatch.tensor.load %3, offsets = [0, 0], sizes = [1, 600], strides = [1, 1] : !flow.dispatch.tensor<writeonly:tensor<1x600xf64>> -> tensor<1x600xf64>
  %5 = flow.dispatch.tensor.load %0, offsets = [0, 0], sizes = [1, 600], strides = [1, 1] : !flow.dispatch.tensor<readonly:tensor<1x600xf64>> -> tensor<1x600xf64>
  %6 = flow.dispatch.tensor.load %1, offsets = [0, 0], sizes = [600, 600], strides = [1, 1] : !flow.dispatch.tensor<readonly:tensor<600x600xf64>> -> tensor<600x600xf64>
  %7 = flow.dispatch.tensor.load %2, offsets = [0, 0], sizes = [1, 600], strides = [1, 1] : !flow.dispatch.tensor<readonly:tensor<1x600xf64>> -> tensor<1x600xf64>
  %8 = tensor.empty() : tensor<1x600xf64>
  %result, %token = dma.start_tensor_copy of %8 to #quidditch_snitch.l1_encoding  -> tensor<1x600xf64>
  %9 = dma.wait_for_tensor_copy of %8 : tensor<1x600xf64> to %result using %token -> tensor<1x600xf64>
  
  %10 = scf.forall (%arg0) = (0) to (600) step (75) shared_outs(%arg1 = %9) -> (tensor<1x600xf64>) {
    %extracted_slice = tensor.extract_slice %arg1[0, %arg0] [1, 75] [1, 1] : tensor<1x600xf64> to tensor<1x75xf64>
    %16 = linalg.fill ins(%cst : f64) outs(%extracted_slice : tensor<1x75xf64>) -> tensor<1x75xf64>
    scf.forall.in_parallel {
      tensor.parallel_insert_slice %16 into %arg1[0, %arg0] [1, 75] [1, 1] : tensor<1x75xf64> into tensor<1x600xf64>
    }
  }
  
  // tile dimension B by tile size of 200 (bound of 3)
  %11 = scf.for %arg0 = %c0 to %c600 step %c200 iter_args(%arg1 = %10) -> (tensor<1x600xf64>) {
  
  // tile dimension C by tile size of 5 (bound of 120) 
    %16 = quidditch_snitch.pipeline %c0 to %c600 step %c5 inits(%arg1) -> tensor<1x600xf64> {
    ^bb0(%arg2: index, %arg3: tensor<1x600xf64>):
      %extracted_slice = tensor.extract_slice %5[0, %arg2] [1, 5] [1, 1] : tensor<1x600xf64> to tensor<1x5xf64>
      %result_6, %token_7 = dma.start_tensor_copy of %extracted_slice to #quidditch_snitch.l1_encoding  -> tensor<1x5xf64>
      %extracted_slice_8 = tensor.extract_slice %6[%arg0, %arg2] [200, 5] [1, 1] : tensor<600x600xf64> to tensor<200x5xf64>
      %result_9, %token_10 = dma.start_tensor_copy of %extracted_slice_8 to #quidditch_snitch.l1_encoding  -> tensor<200x5xf64>
      %extracted_slice_11 = tensor.extract_slice %arg3[0, %arg0] [1, 200] [1, 1] : tensor<1x600xf64> to tensor<1x200xf64>
      %result_12, %token_13 = dma.start_tensor_copy of %extracted_slice_11 to #quidditch_snitch.l1_encoding  -> tensor<1x200xf64>
      quidditch_snitch.pipeline_yield %arg3, %extracted_slice, %result_6, %token_7, %extracted_slice_8, %result_9, %token_10, %extracted_slice_11, %result_12, %token_13 : tensor<1x600xf64>, tensor<1x5xf64>, tensor<1x5xf64>, !dma.token, tensor<200x5xf64>, tensor<200x5xf64>, !dma.token, tensor<1x200xf64>, tensor<1x200xf64>, !dma.token
    }, {
    ^bb0(%arg2: index, %arg3: tensor<1x600xf64>, %arg4: tensor<1x5xf64>, %arg5: tensor<1x5xf64>, %arg6: !dma.token, %arg7: tensor<200x5xf64>, %arg8: tensor<200x5xf64>, %arg9: !dma.token, %arg10: tensor<1x200xf64>, %arg11: tensor<1x200xf64>, %arg12: !dma.token):
      %17 = dma.wait_for_tensor_copy of %arg4 : tensor<1x5xf64> to %arg5 using %arg6 -> tensor<1x5xf64>
      %18 = dma.wait_for_tensor_copy of %arg7 : tensor<200x5xf64> to %arg8 using %arg9 -> tensor<200x5xf64>
      %19 = dma.wait_for_tensor_copy of %arg10 : tensor<1x200xf64> to %arg11 using %arg12 -> tensor<1x200xf64>
      
      // tile dimension B by tile size of 25 (bounds 8)
      %20 = scf.forall (%arg13) = (0) to (200) step (25) shared_outs(%arg14 = %19) -> (tensor<1x200xf64>) {
        %extracted_slice = tensor.extract_slice %17[0, 0] [1, 5] [1, 1] : tensor<1x5xf64> to tensor<1x5xf64>
        %extracted_slice_6 = tensor.extract_slice %18[%arg13, 0] [25, 5] [1, 1] : tensor<200x5xf64> to tensor<25x5xf64>
        %extracted_slice_7 = tensor.extract_slice %arg14[0, %arg13] [1, 25] [1, 1] : tensor<1x200xf64> to tensor<1x25xf64>
        %21 = linalg.matmul_transpose_b {lowering_config = #quidditch_snitch.lowering_config<
        l1_tiles = [0, 200, 5], 
        l1_tiles_interchange = [0, 1, 2], 
        dual_buffer = true, zigzagID = 89>} 
        ins(%extracted_slice, %extracted_slice_6 : tensor<1x5xf64>, tensor<25x5xf64>) 
        outs(%extracted_slice_7 : tensor<1x25xf64>) -> tensor<1x25xf64>
        scf.forall.in_parallel {
          tensor.parallel_insert_slice %21 into %arg14[0, %arg13] [1, 25] [1, 1] : tensor<1x25xf64> into tensor<1x200xf64>
        }
      }
      %inserted_slice = tensor.insert_slice %20 into %arg3[0, %arg0] [1, 200] [1, 1] : tensor<1x200xf64> into tensor<1x600xf64>
      quidditch_snitch.pipeline_yield %inserted_slice : tensor<1x600xf64>
    }
    scf.yield %16 : tensor<1x600xf64>
  }
  %result_0, %token_1 = dma.start_tensor_copy of %11 to #quidditch_snitch.l1_encoding  -> tensor<1x600xf64>
  %12 = dma.wait_for_tensor_copy of %11 : tensor<1x600xf64> to %result_0 using %token_1 -> tensor<1x600xf64>
  %result_2, %token_3 = dma.start_tensor_copy of %7 to #quidditch_snitch.l1_encoding  -> tensor<1x600xf64>
  %13 = dma.wait_for_tensor_copy of %7 : tensor<1x600xf64> to %result_2 using %token_3 -> tensor<1x600xf64>
  %result_4, %token_5 = dma.start_tensor_copy of %4 to #quidditch_snitch.l1_encoding  -> tensor<1x600xf64>
  %14 = dma.wait_for_tensor_copy of %4 : tensor<1x600xf64> to %result_4 using %token_5 -> tensor<1x600xf64>
  %15 = scf.forall (%arg0) = (0) to (600) step (75) shared_outs(%arg1 = %14) -> (tensor<1x600xf64>) {
    %extracted_slice = tensor.extract_slice %12[0, %arg0] [1, 75] [1, 1] : tensor<1x600xf64> to tensor<1x75xf64>
    %extracted_slice_6 = tensor.extract_slice %13[0, %arg0] [1, 75] [1, 1] : tensor<1x600xf64> to tensor<1x75xf64>
    %extracted_slice_7 = tensor.extract_slice %arg1[0, %arg0] [1, 75] [1, 1] : tensor<1x600xf64> to tensor<1x75xf64>
    %16 = linalg.generic {indexing_maps = [affine_map<(d0, d1) -> (d0, d1)>, affine_map<(d0, d1) -> (d0, d1)>, affine_map<(d0, d1) -> (d0, d1)>], iterator_types = ["parallel", "parallel"]} ins(%extracted_slice, %extracted_slice_6 : tensor<1x75xf64>, tensor<1x75xf64>) outs(%extracted_slice_7 : tensor<1x75xf64>) {
    ^bb0(%in: f64, %in_8: f64, %out: f64):
      %17 = arith.addf %in, %in_8 : f64
      %18 = arith.cmpf ugt, %17, %cst : f64
      %19 = arith.select %18, %17, %cst : f64
      linalg.yield %19 : f64
    } -> tensor<1x75xf64>
    scf.forall.in_parallel {
      tensor.parallel_insert_slice %16 into %arg1[0, %arg0] [1, 75] [1, 1] : tensor<1x75xf64> into tensor<1x600xf64>
    }
  }
  flow.dispatch.tensor.store %15, %3, offsets = [0, 0], sizes = [1, 600], strides = [1, 1] : tensor<1x600xf64> -> !flow.dispatch.tensor<writeonly:tensor<1x600xf64>>
  return
}
```

