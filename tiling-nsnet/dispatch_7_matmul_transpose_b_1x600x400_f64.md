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
tile_sizes = loop_sizes / new_loop_bounds = [1, 600, 400] / [1, 20, 2] = [1, 30, 200]
tile_sizes2 = tile_sizes / new_loop_bounds2 = [1, 30, 200] / [1, 1, 5] = [1, 30, 40]
original loop order: [A, B, C] = [0, 1, 2]
new loop order: [0, 2, 1]
```

But Quidditch cannot do second level tiling! So let's give it the tile sizes when ALL operands are in L1: `[1, 30, 40]`

```
l1Tiles[0] = 0;
l1Tiles[1] = 30;
l1Tiles[2] = 40;
l1Interchange = {0, 2, 1}; 
```

## JSON Summary

```
{
    "bounds":[[1], [20], [10]],
    "order":[[0,0], [1,0], [2,0]]
}
```

### After L1 tiling

```
<eval_with_key>.0 from /home/hoppip/Quidditch/venv/lib/python3.11/site-packages/torch/fx/experimental/proxy_tensor.py:551 in wrapped:98:0: warning: SLICEDCUCUMBER tiling level L1 This is the rewritten kernel!!!!!

/home/hoppip/Quidditch/runtime/samples/grapeFruit/grapeFruit.py:90:0: note: called from
<eval_with_key>.0 from /home/hoppip/Quidditch/venv/lib/python3.11/site-packages/torch/fx/experimental/proxy_tensor.py:551 in wrapped:98:0: note: see current operation: 
func.func @main$async_dispatch_7_matmul_transpose_b_1x600x400_f64() attributes {translation_info = #iree_codegen.translation_info<None>} {
  %cst = arith.constant 0.000000e+00 : f64
  %c3200 = arith.constant 3200 : index
  %c15916800 = arith.constant 15916800 : index
  %c17836800 = arith.constant 17836800 : index
  %c0 = arith.constant 0 : index
  %0 = hal.interface.binding.subspan set(0) binding(0) type(storage_buffer) alignment(64) offset(%c3200) flags(ReadOnly) : !flow.dispatch.tensor<readonly:tensor<1x400xf64>>
  %1 = hal.interface.binding.subspan set(0) binding(1) type(storage_buffer) alignment(64) offset(%c15916800) flags(ReadOnly) : !flow.dispatch.tensor<readonly:tensor<600x400xf64>>
  %2 = hal.interface.binding.subspan set(0) binding(1) type(storage_buffer) alignment(64) offset(%c17836800) flags(ReadOnly) : !flow.dispatch.tensor<readonly:tensor<1x600xf64>>
  %3 = hal.interface.binding.subspan set(0) binding(2) type(storage_buffer) alignment(64) offset(%c0) : !flow.dispatch.tensor<writeonly:tensor<1x600xf64>>
  %4 = flow.dispatch.tensor.load %3, offsets = [0, 0], sizes = [1, 600], strides = [1, 1] : !flow.dispatch.tensor<writeonly:tensor<1x600xf64>> -> tensor<1x600xf64>
  %5 = flow.dispatch.tensor.load %0, offsets = [0, 0], sizes = [1, 400], strides = [1, 1] : !flow.dispatch.tensor<readonly:tensor<1x400xf64>> -> tensor<1x400xf64>
  %6 = flow.dispatch.tensor.load %1, offsets = [0, 0], sizes = [600, 400], strides = [1, 1] : !flow.dispatch.tensor<readonly:tensor<600x400xf64>> -> tensor<600x400xf64>
  %7 = flow.dispatch.tensor.load %2, offsets = [0, 0], sizes = [1, 600], strides = [1, 1] : !flow.dispatch.tensor<readonly:tensor<1x600xf64>> -> tensor<1x600xf64>
  %8 = tensor.empty() : tensor<1x600xf64>
  %9 = linalg.fill ins(%cst : f64) outs(%8 : tensor<1x600xf64>) -> tensor<1x600xf64>
  %c0_0 = arith.constant 0 : index
  %c400 = arith.constant 400 : index
  %c40 = arith.constant 40 : index
  %10 = scf.for %arg0 = %c0_0 to %c400 step %c40 iter_args(%arg1 = %9) -> (tensor<1x600xf64>) {
    %c0_1 = arith.constant 0 : index
    %c600 = arith.constant 600 : index
    %c30 = arith.constant 30 : index
    %12 = scf.for %arg2 = %c0_1 to %c600 step %c30 iter_args(%arg3 = %arg1) -> (tensor<1x600xf64>) {
      %extracted_slice = tensor.extract_slice %5[0, %arg0] [1, 40] [1, 1] : tensor<1x400xf64> to tensor<1x40xf64>
      %extracted_slice_2 = tensor.extract_slice %6[%arg2, %arg0] [30, 40] [1, 1] : tensor<600x400xf64> to tensor<30x40xf64>
      %extracted_slice_3 = tensor.extract_slice %arg3[0, %arg2] [1, 30] [1, 1] : tensor<1x600xf64> to tensor<1x30xf64>
      %13 = linalg.matmul_transpose_b {lowering_config = #quidditch_snitch.lowering_config<l1_tiles = [0, 30, 40], l1_tiles_interchange = [0, 2, 1], dual_buffer = true, zigzagID = 89>} ins(%extracted_slice, %extracted_slice_2 : tensor<1x40xf64>, tensor<30x40xf64>) outs(%extracted_slice_3 : tensor<1x30xf64>) -> tensor<1x30xf64>
      %inserted_slice = tensor.insert_slice %13 into %arg3[0, %arg2] [1, 30] [1, 1] : tensor<1x30xf64> into tensor<1x600xf64>
      scf.yield %inserted_slice : tensor<1x600xf64>
    }
    scf.yield %12 : tensor<1x600xf64>
  }
  %11 = linalg.generic {indexing_maps = [affine_map<(d0, d1) -> (d0, d1)>, affine_map<(d0, d1) -> (d0, d1)>, affine_map<(d0, d1) -> (d0, d1)>], iterator_types = ["parallel", "parallel"]} ins(%10, %7 : tensor<1x600xf64>, tensor<1x600xf64>) outs(%4 : tensor<1x600xf64>) {
  ^bb0(%in: f64, %in_1: f64, %out: f64):
    %12 = arith.addf %in, %in_1 : f64
    %13 = arith.cmpf ugt, %12, %cst : f64
    %14 = arith.select %13, %12, %cst : f64
    linalg.yield %14 : f64
  } -> tensor<1x600xf64>
  flow.dispatch.tensor.store %11, %3, offsets = [0, 0], sizes = [1, 600], strides = [1, 1] : tensor<1x600xf64> -> !flow.dispatch.tensor<writeonly:tensor<1x600xf64>>
  return
}
```

### After Spatial Unrolling:

```
<eval_with_key>.0 from /home/hoppip/Quidditch/venv/lib/python3.11/site-packages/torch/fx/experimental/proxy_tensor.py:551 in wrapped:98:0: warning: SLICEDCUCUMBER tiling level Thread This is the rewritten kernel!!!!!

/home/hoppip/Quidditch/runtime/samples/grapeFruit/grapeFruit.py:90:0: note: called from
<eval_with_key>.0 from /home/hoppip/Quidditch/venv/lib/python3.11/site-packages/torch/fx/experimental/proxy_tensor.py:551 in wrapped:98:0: note: see current operation: 
func.func @main$async_dispatch_7_matmul_transpose_b_1x600x400_f64() attributes {translation_info = #iree_codegen.translation_info<None>} {
  %c30 = arith.constant 30 : index
  %c600 = arith.constant 600 : index
  %c40 = arith.constant 40 : index
  %c400 = arith.constant 400 : index
  %cst = arith.constant 0.000000e+00 : f64
  %c3200 = arith.constant 3200 : index
  %c15916800 = arith.constant 15916800 : index
  %c17836800 = arith.constant 17836800 : index
  %c0 = arith.constant 0 : index
  %0 = hal.interface.binding.subspan set(0) binding(0) type(storage_buffer) alignment(64) offset(%c3200) flags(ReadOnly) : !flow.dispatch.tensor<readonly:tensor<1x400xf64>>
  %1 = hal.interface.binding.subspan set(0) binding(1) type(storage_buffer) alignment(64) offset(%c15916800) flags(ReadOnly) : !flow.dispatch.tensor<readonly:tensor<600x400xf64>>
  %2 = hal.interface.binding.subspan set(0) binding(1) type(storage_buffer) alignment(64) offset(%c17836800) flags(ReadOnly) : !flow.dispatch.tensor<readonly:tensor<1x600xf64>>
  %3 = hal.interface.binding.subspan set(0) binding(2) type(storage_buffer) alignment(64) offset(%c0) : !flow.dispatch.tensor<writeonly:tensor<1x600xf64>>
  %4 = flow.dispatch.tensor.load %3, offsets = [0, 0], sizes = [1, 600], strides = [1, 1] : !flow.dispatch.tensor<writeonly:tensor<1x600xf64>> -> tensor<1x600xf64>
  %5 = flow.dispatch.tensor.load %0, offsets = [0, 0], sizes = [1, 400], strides = [1, 1] : !flow.dispatch.tensor<readonly:tensor<1x400xf64>> -> tensor<1x400xf64>
  %6 = flow.dispatch.tensor.load %1, offsets = [0, 0], sizes = [600, 400], strides = [1, 1] : !flow.dispatch.tensor<readonly:tensor<600x400xf64>> -> tensor<600x400xf64>
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
  %11 = scf.for %arg0 = %c0 to %c400 step %c40 iter_args(%arg1 = %10) -> (tensor<1x600xf64>) {
    %extracted_slice = tensor.extract_slice %5[0, %arg0] [1, 40] [1, 1] : tensor<1x400xf64> to tensor<1x40xf64>
    %result_6, %token_7 = dma.start_tensor_copy of %extracted_slice to #quidditch_snitch.l1_encoding  -> tensor<1x40xf64>
    %16 = dma.wait_for_tensor_copy of %extracted_slice : tensor<1x40xf64> to %result_6 using %token_7 -> tensor<1x40xf64>
    %17 = quidditch_snitch.pipeline %c0 to %c600 step %c30 inits(%arg1) -> tensor<1x600xf64> {
    ^bb0(%arg2: index, %arg3: tensor<1x600xf64>):
      %extracted_slice_8 = tensor.extract_slice %6[%arg2, %arg0] [30, 40] [1, 1] : tensor<600x400xf64> to tensor<30x40xf64>
      %result_9, %token_10 = dma.start_tensor_copy of %extracted_slice_8 to #quidditch_snitch.l1_encoding  -> tensor<30x40xf64>
      %extracted_slice_11 = tensor.extract_slice %arg3[0, %arg2] [1, 30] [1, 1] : tensor<1x600xf64> to tensor<1x30xf64>
      %result_12, %token_13 = dma.start_tensor_copy of %extracted_slice_11 to #quidditch_snitch.l1_encoding  -> tensor<1x30xf64>
      quidditch_snitch.pipeline_yield %arg3, %extracted_slice_8, %result_9, %token_10, %extracted_slice_11, %result_12, %token_13 : tensor<1x600xf64>, tensor<30x40xf64>, tensor<30x40xf64>, !dma.token, tensor<1x30xf64>, tensor<1x30xf64>, !dma.token
    }, {
    ^bb0(%arg2: index, %arg3: tensor<1x600xf64>, %arg4: tensor<30x40xf64>, %arg5: tensor<30x40xf64>, %arg6: !dma.token, %arg7: tensor<1x30xf64>, %arg8: tensor<1x30xf64>, %arg9: !dma.token):
      %18 = dma.wait_for_tensor_copy of %arg4 : tensor<30x40xf64> to %arg5 using %arg6 -> tensor<30x40xf64>
      %19 = dma.wait_for_tensor_copy of %arg7 : tensor<1x30xf64> to %arg8 using %arg9 -> tensor<1x30xf64>
      %20 = scf.forall (%arg10) = (0) to (30) step (4) shared_outs(%arg11 = %19) -> (tensor<1x30xf64>) {
        %c30_8 = arith.constant 30 : index
        %21 = affine.min affine_map<(d0) -> (4, -d0 + 30)>(%arg10)
        %22 = affine.apply affine_map<(d0) -> (d0 - 1)>(%21)
        %23 = affine.apply affine_map<(d0) -> (d0 - 1)>(%21)
        %24 = affine.apply affine_map<(d0) -> (d0 - 1)>(%21)
        %extracted_slice_9 = tensor.extract_slice %16[0, 0] [1, 40] [1, 1] : tensor<1x40xf64> to tensor<1x40xf64>
        %extracted_slice_10 = tensor.extract_slice %18[%arg10, 0] [%21, 40] [1, 1] : tensor<30x40xf64> to tensor<?x40xf64>
        %extracted_slice_11 = tensor.extract_slice %arg11[0, %arg10] [1, %21] [1, 1] : tensor<1x30xf64> to tensor<1x?xf64>
        %25 = linalg.matmul_transpose_b {lowering_config = #quidditch_snitch.lowering_config<l1_tiles = [0, 30, 40], l1_tiles_interchange = [0, 2, 1], dual_buffer = true, zigzagID = 89>} ins(%extracted_slice_9, %extracted_slice_10 : tensor<1x40xf64>, tensor<?x40xf64>) outs(%extracted_slice_11 : tensor<1x?xf64>) -> tensor<1x?xf64>
        %26 = affine.apply affine_map<(d0) -> (d0 - 1)>(%21)
        %27 = affine.apply affine_map<(d0) -> (d0 - 1)>(%21)
        scf.forall.in_parallel {
          tensor.parallel_insert_slice %25 into %arg11[0, %arg10] [1, %21] [1, 1] : tensor<1x?xf64> into tensor<1x30xf64>
        }
      }
      %inserted_slice = tensor.insert_slice %20 into %arg3[0, %arg2] [1, 30] [1, 1] : tensor<1x30xf64> into tensor<1x600xf64>
      quidditch_snitch.pipeline_yield %inserted_slice : tensor<1x600xf64>
    }
    scf.yield %17 : tensor<1x600xf64>
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

### Error

#### applyPartialConversion failed / ConvertToLLVMPass Failed (quidditch-convert-to-llvm)

```
<eval_with_key>.0 from /home/hoppip/Quidditch/venv/lib/python3.11/site-packages/torch/fx/experimental/proxy_tensor.py:551 in wrapped:98:0: warning: 
RADDISH (q-convert-to-llvm) applyPartialConversion failed :'(
/home/hoppip/Quidditch/runtime/samples/grapeFruit/grapeFruit.py:90:0: note: called from
<eval_with_key>.0 from /home/hoppip/Quidditch/venv/lib/python3.11/site-packages/torch/fx/experimental/proxy_tensor.py:551 in wrapped:98:0: note: see current operation: 
module attributes {llvm.data_layout = "e-m:e-p:32:32-i64:64-n32-S128", llvm.target_triple = "riscv32-unknown-elf"} {
  func.func @main$async_dispatch_7_matmul_transpose_b_1x600x400_f64() attributes {quidditch_snitch.dma_specialization = @main$async_dispatch_7_matmul_transpose_b_1x600x400_f64$dma, translation_info = #iree_codegen.translation_info<None>} {
    %c29120 = arith.constant 29120 : index
    %c24320 = arith.constant 24320 : index
    %c14720 = arith.constant 14720 : index
    %c5120 = arith.constant 5120 : index
    %c4800 = arith.constant 4800 : index
    %c0 = arith.constant 0 : index
    %c400 = arith.constant 400 : index
    %c40 = arith.constant 40 : index
    %c600 = arith.constant 600 : index
    %c30 = arith.constant 30 : index
    %0 = quidditch_snitch.l1_memory_view -> memref<100000xi8>
    %view = memref.view %0[%c0][] : memref<100000xi8> to memref<600xf64>
    %reinterpret_cast = memref.reinterpret_cast %view to offset: [0], sizes: [1, 600], strides: [600, 1] : memref<600xf64> to memref<1x600xf64>
    %1 = quidditch_snitch.compute_core_index
    %2 = affine.apply affine_map<()[s0] -> (s0 * 75)>()[%1]
    %subview = memref.subview %reinterpret_cast[0, %2] [1, 75] [1, 1] : memref<1x600xf64> to memref<1x75xf64, strided<[600, 1], offset: ?>>
    quidditch_snitch.call_microkernel "main$async_dispatch_7_matmul_transpose_b_1x600x400_f64$xdsl_kernel0"(%subview) : memref<1x75xf64, strided<[600, 1], offset: ?>>[{
      ".text"
      ".globl main$async_dispatch_7_matmul_transpose_b_1x600x400_f64$xdsl_kernel0"
      ".p2align 2"
      "main$async_dispatch_7_matmul_transpose_b_1x600x400_f64$xdsl_kernel0:"
      "    mv t0, a0"
      "    fcvt.d.w ft3, zero"
      "    li t1, 74"
      "    scfgwi t1, 64                                # dm 0 dim 0 bound"
      "    li t1, 8"
      "    scfgwi t1, 192                               # dm 0 dim 0 stride"
      "    scfgwi zero, 32                              # dm 0 repeat"
      "    scfgwi t0, 896                               # dm 0 dim 0 destination"
      "    csrrsi zero, 1984, 1                         # SSR enable"
      "    li t0, 74"
      "    frep.o t0, 1, 0, 0"
      "    fmv.d ft0, ft3"
      "    csrrci zero, 1984, 1                         # SSR disable"
      "    ret"
      ""
    }]
    quidditch_snitch.microkernel_fence
    quidditch_snitch.barrier
    %view_0 = memref.view %0[%c4800][] : memref<100000xi8> to memref<40xf64>
    %reinterpret_cast_1 = memref.reinterpret_cast %view_0 to offset: [0], sizes: [1, 40], strides: [40, 1] : memref<40xf64> to memref<1x40xf64>
    %view_2 = memref.view %0[%c5120][] : memref<100000xi8> to memref<1200xf64>
    %reinterpret_cast_3 = memref.reinterpret_cast %view_2 to offset: [0], sizes: [30, 40], strides: [40, 1] : memref<1200xf64> to memref<30x40xf64>
    %view_4 = memref.view %0[%c14720][] : memref<100000xi8> to memref<1200xf64>
    %reinterpret_cast_5 = memref.reinterpret_cast %view_4 to offset: [0], sizes: [30, 40], strides: [40, 1] : memref<1200xf64> to memref<30x40xf64>
    %3 = affine.apply affine_map<()[s0] -> (s0 * 4)>()[%1]
    scf.for %arg0 = %c0 to %c400 step %c40 {
      quidditch_snitch.barrier
      %4 = scf.for %arg1 = %c30 to %c600 step %c30 iter_args(%arg2 = %reinterpret_cast_3) -> (memref<30x40xf64>) {
        %7 = affine.apply affine_map<(d0) -> ((d0 floordiv 30) mod 2)>(%arg1)
        %8 = scf.index_switch %7 -> memref<30x40xf64> 
        case 0 {
          scf.yield %reinterpret_cast_3 : memref<30x40xf64>
        }
        default {
          scf.yield %reinterpret_cast_5 : memref<30x40xf64>
        }
        quidditch_snitch.barrier
        %9 = affine.min affine_map<()[s0] -> (s0 * -4 + 30, 4)>()[%1]
        %subview_14 = memref.subview %arg2[%3, 0] [%9, 40] [1, 1] : memref<30x40xf64> to memref<?x40xf64, strided<[40, 1], offset: ?>>
        %10 = affine.apply affine_map<(d0)[s0] -> (d0 + s0 * 4 - 30)>(%arg1)[%1]
        %subview_15 = memref.subview %reinterpret_cast[0, %10] [1, %9] [1, 1] : memref<1x600xf64> to memref<1x?xf64, strided<[600, 1], offset: ?>>
        quidditch_snitch.call_microkernel "main$async_dispatch_7_matmul_transpose_b_1x600x400_f64$xdsl_kernel1"(%reinterpret_cast_1, %subview_14, %subview_15) : memref<1x40xf64>, memref<?x40xf64, strided<[40, 1], offset: ?>>, memref<1x?xf64, strided<[600, 1], offset: ?>>[{
          ".text"
          ".globl main$async_dispatch_7_matmul_transpose_b_1x600x400_f64$xdsl_kernel1"
          ".p2align 2"
          "main$async_dispatch_7_matmul_transpose_b_1x600x400_f64$xdsl_kernel1:"
          "    mv t1, a0"
          "    mv t0, a1"
          "    li t2, 39"
          "    scfgwi t2, 64                                # dm 0 dim 0 bound"
          "    li t2, -2"
          "    scfgwi t2, 96                                # dm 0 dim 1 bound"
          "    li t2, 8"
          "    scfgwi t2, 192                               # dm 0 dim 0 stride"
          "    li t2, -312"
          "    scfgwi t2, 224                               # dm 0 dim 1 stride"
          "    scfgwi zero, 32                              # dm 0 repeat"
          "    li t2, -41"
          "    scfgwi t2, 65                                # dm 1 dim 0 bound"
          "    li t2, 8"
          "    scfgwi t2, 193                               # dm 1 dim 0 stride"
          "    scfgwi zero, 33                              # dm 1 repeat"
          "    scfgwi t1, 800                               # dm 0 dim 1 source"
          "    scfgwi t0, 769                               # dm 1 dim 0 source"
          "    csrrsi zero, 1984, 1                         # SSR enable"
          "    csrrci zero, 1984, 1                         # SSR disable"
          "    ret"
          ""
        }]
        quidditch_snitch.microkernel_fence
        quidditch_snitch.barrier
        scf.yield %8 : memref<30x40xf64>
      }
      quidditch_snitch.barrier
      %5 = affine.min affine_map<()[s0] -> (s0 * -4 + 30, 4)>()[%1]
      %subview_12 = memref.subview %4[%3, 0] [%5, 40] [1, 1] : memref<30x40xf64> to memref<?x40xf64, strided<[40, 1], offset: ?>>
      %6 = affine.apply affine_map<()[s0] -> (s0 * 4 + 570)>()[%1]
      %subview_13 = memref.subview %reinterpret_cast[0, %6] [1, %5] [1, 1] : memref<1x600xf64> to memref<1x?xf64, strided<[600, 1], offset: ?>>
      quidditch_snitch.call_microkernel "main$async_dispatch_7_matmul_transpose_b_1x600x400_f64$xdsl_kernel2"(%reinterpret_cast_1, %subview_12, %subview_13) : memref<1x40xf64>, memref<?x40xf64, strided<[40, 1], offset: ?>>, memref<1x?xf64, strided<[600, 1], offset: ?>>[{
        ".text"
        ".globl main$async_dispatch_7_matmul_transpose_b_1x600x400_f64$xdsl_kernel2"
        ".p2align 2"
        "main$async_dispatch_7_matmul_transpose_b_1x600x400_f64$xdsl_kernel2:"
        "    mv t1, a0"
        "    mv t0, a1"
        "    li t2, 39"
        "    scfgwi t2, 64                                # dm 0 dim 0 bound"
        "    li t2, -2"
        "    scfgwi t2, 96                                # dm 0 dim 1 bound"
        "    li t2, 8"
        "    scfgwi t2, 192                               # dm 0 dim 0 stride"
        "    li t2, -312"
        "    scfgwi t2, 224                               # dm 0 dim 1 stride"
        "    scfgwi zero, 32                              # dm 0 repeat"
        "    li t2, -41"
        "    scfgwi t2, 65                                # dm 1 dim 0 bound"
        "    li t2, 8"
        "    scfgwi t2, 193                               # dm 1 dim 0 stride"
        "    scfgwi zero, 33                              # dm 1 repeat"
        "    scfgwi t1, 800                               # dm 0 dim 1 source"
        "    scfgwi t0, 769                               # dm 1 dim 0 source"
        "    csrrsi zero, 1984, 1                         # SSR enable"
        "    csrrci zero, 1984, 1                         # SSR disable"
        "    ret"
        ""
      }]
      quidditch_snitch.microkernel_fence
      quidditch_snitch.barrier
    }
    %view_6 = memref.view %0[%c24320][] : memref<100000xi8> to memref<600xf64>
    %reinterpret_cast_7 = memref.reinterpret_cast %view_6 to offset: [0], sizes: [1, 600], strides: [600, 1] : memref<600xf64> to memref<1x600xf64>
    quidditch_snitch.barrier
    %view_8 = memref.view %0[%c29120][] : memref<100000xi8> to memref<600xf64>
    %reinterpret_cast_9 = memref.reinterpret_cast %view_8 to offset: [0], sizes: [1, 600], strides: [600, 1] : memref<600xf64> to memref<1x600xf64>
    quidditch_snitch.barrier
    %subview_10 = memref.subview %reinterpret_cast_7[0, %2] [1, 75] [1, 1] : memref<1x600xf64> to memref<1x75xf64, strided<[600, 1], offset: ?>>
    %subview_11 = memref.subview %reinterpret_cast_9[0, %2] [1, 75] [1, 1] : memref<1x600xf64> to memref<1x75xf64, strided<[600, 1], offset: ?>>
    quidditch_snitch.call_microkernel "main$async_dispatch_7_matmul_transpose_b_1x600x400_f64$xdsl_kernel3"(%subview, %subview_10, %subview_11) : memref<1x75xf64, strided<[600, 1], offset: ?>>, memref<1x75xf64, strided<[600, 1], offset: ?>>, memref<1x75xf64, strided<[600, 1], offset: ?>>[{
      ".text"
      ".globl main$async_dispatch_7_matmul_transpose_b_1x600x400_f64$xdsl_kernel3"
      ".p2align 2"
      "main$async_dispatch_7_matmul_transpose_b_1x600x400_f64$xdsl_kernel3:"
      "    mv t2, a0"
      "    mv t1, a1"
      "    mv t0, a2"
      "    fcvt.d.w ft3, zero"
      "    li t3, 74"
      "    scfgwi t3, 95                                # dm 31 dim 0 bound"
      "    li t3, 8"
      "    scfgwi t3, 223                               # dm 31 dim 0 stride"
      "    scfgwi zero, 63                              # dm 31 repeat"
      "    scfgwi t2, 768                               # dm 0 dim 0 source"
      "    scfgwi t1, 769                               # dm 1 dim 0 source"
      "    scfgwi t0, 898                               # dm 2 dim 0 destination"
      "    csrrsi zero, 1984, 1                         # SSR enable"
      "    li t0, 74"
      "    frep.o t0, 2, 0, 0"
      "    fadd.d ft4, ft0, ft1"
      "    fmax.d ft2, ft4, ft3"
      "    csrrci zero, 1984, 1                         # SSR disable"
      "    ret"
      ""
    }]
    quidditch_snitch.microkernel_fence
    quidditch_snitch.barrier
    quidditch_snitch.barrier
    return
  }
  func.func @main$async_dispatch_7_matmul_transpose_b_1x600x400_f64$dma() attributes {translation_info = #iree_codegen.translation_info<None>} {
    %c29120 = arith.constant 29120 : index
    %c24320 = arith.constant 24320 : index
    %c14720 = arith.constant 14720 : index
    %c5120 = arith.constant 5120 : index
    %c4800 = arith.constant 4800 : index
    %c0 = arith.constant 0 : index
    %c17836800 = arith.constant 17836800 : index
    %c15916800 = arith.constant 15916800 : index
    %c3200 = arith.constant 3200 : index
    %c400 = arith.constant 400 : index
    %c40 = arith.constant 40 : index
    %c600 = arith.constant 600 : index
    %c30 = arith.constant 30 : index
    %0 = quidditch_snitch.l1_memory_view -> memref<100000xi8>
    %1 = hal.interface.binding.subspan set(0) binding(0) type(storage_buffer) alignment(64) offset(%c3200) flags(ReadOnly) : memref<1x400xf64, strided<[400, 1], offset: 400>>
    memref.assume_alignment %1, 64 : memref<1x400xf64, strided<[400, 1], offset: 400>>
    %2 = hal.interface.binding.subspan set(0) binding(1) type(storage_buffer) alignment(64) offset(%c15916800) flags(ReadOnly) : memref<600x400xf64, strided<[400, 1], offset: 1989600>>
    memref.assume_alignment %2, 64 : memref<600x400xf64, strided<[400, 1], offset: 1989600>>
    %3 = hal.interface.binding.subspan set(0) binding(1) type(storage_buffer) alignment(64) offset(%c17836800) flags(ReadOnly) : memref<1x600xf64, strided<[600, 1], offset: 2229600>>
    memref.assume_alignment %3, 64 : memref<1x600xf64, strided<[600, 1], offset: 2229600>>
    %4 = hal.interface.binding.subspan set(0) binding(2) type(storage_buffer) alignment(64) offset(%c0) : memref<1x600xf64>
    memref.assume_alignment %4, 64 : memref<1x600xf64>
    quidditch_snitch.barrier
    %view = memref.view %0[%c4800][] : memref<100000xi8> to memref<40xf64>
    %reinterpret_cast = memref.reinterpret_cast %view to offset: [0], sizes: [1, 40], strides: [40, 1] : memref<40xf64> to memref<1x40xf64>
    %view_0 = memref.view %0[%c5120][] : memref<100000xi8> to memref<1200xf64>
    %reinterpret_cast_1 = memref.reinterpret_cast %view_0 to offset: [0], sizes: [30, 40], strides: [40, 1] : memref<1200xf64> to memref<30x40xf64>
    %view_2 = memref.view %0[%c14720][] : memref<100000xi8> to memref<1200xf64>
    %reinterpret_cast_3 = memref.reinterpret_cast %view_2 to offset: [0], sizes: [30, 40], strides: [40, 1] : memref<1200xf64> to memref<30x40xf64>
    %cast = memref.cast %reinterpret_cast_1 : memref<30x40xf64> to memref<30x40xf64, strided<[40, 1]>>
    scf.for %arg0 = %c0 to %c400 step %c40 {
      %subview_11 = memref.subview %1[0, %arg0] [1, 40] [1, 1] : memref<1x400xf64, strided<[400, 1], offset: 400>> to memref<40xf64, strided<[1], offset: ?>>
      %subview_12 = memref.subview %reinterpret_cast[0, 0] [1, 40] [1, 1] : memref<1x40xf64> to memref<40xf64, strided<[1]>>
      %8 = dma.start_transfer from %subview_11 : memref<40xf64, strided<[1], offset: ?>> to %subview_12 : memref<40xf64, strided<[1]>>
      dma.wait_for_transfer %8
      quidditch_snitch.barrier
      %subview_13 = memref.subview %2[0, %arg0] [30, 40] [1, 1] : memref<600x400xf64, strided<[400, 1], offset: 1989600>> to memref<30x40xf64, strided<[400, 1], offset: ?>>
      %9 = dma.start_transfer from %subview_13 : memref<30x40xf64, strided<[400, 1], offset: ?>> to %cast : memref<30x40xf64, strided<[40, 1]>>
      %10 = scf.for %arg1 = %c30 to %c600 step %c30 iter_args(%arg2 = %9) -> (!dma.token) {
        %subview_14 = memref.subview %2[%arg1, %arg0] [30, 40] [1, 1] : memref<600x400xf64, strided<[400, 1], offset: 1989600>> to memref<30x40xf64, strided<[400, 1], offset: ?>>
        %11 = affine.apply affine_map<(d0) -> ((d0 floordiv 30) mod 2)>(%arg1)
        %12 = scf.index_switch %11 -> memref<30x40xf64> 
        case 0 {
          scf.yield %reinterpret_cast_1 : memref<30x40xf64>
        }
        default {
          scf.yield %reinterpret_cast_3 : memref<30x40xf64>
        }
        %cast_15 = memref.cast %12 : memref<30x40xf64> to memref<30x40xf64, strided<[40, 1]>>
        %13 = dma.start_transfer from %subview_14 : memref<30x40xf64, strided<[400, 1], offset: ?>> to %cast_15 : memref<30x40xf64, strided<[40, 1]>>
        dma.wait_for_transfer %arg2
        quidditch_snitch.barrier
        quidditch_snitch.barrier
        scf.yield %13 : !dma.token
      }
      dma.wait_for_transfer %10
      quidditch_snitch.barrier
      quidditch_snitch.barrier
    }
    %view_4 = memref.view %0[%c24320][] : memref<100000xi8> to memref<600xf64>
    %reinterpret_cast_5 = memref.reinterpret_cast %view_4 to offset: [0], sizes: [1, 600], strides: [600, 1] : memref<600xf64> to memref<1x600xf64>
    %subview = memref.subview %3[0, 0] [1, 600] [1, 1] : memref<1x600xf64, strided<[600, 1], offset: 2229600>> to memref<600xf64, strided<[1], offset: 2229600>>
    %subview_6 = memref.subview %reinterpret_cast_5[0, 0] [1, 600] [1, 1] : memref<1x600xf64> to memref<600xf64, strided<[1]>>
    %5 = dma.start_transfer from %subview : memref<600xf64, strided<[1], offset: 2229600>> to %subview_6 : memref<600xf64, strided<[1]>>
    dma.wait_for_transfer %5
    quidditch_snitch.barrier
    %view_7 = memref.view %0[%c29120][] : memref<100000xi8> to memref<600xf64>
    %reinterpret_cast_8 = memref.reinterpret_cast %view_7 to offset: [0], sizes: [1, 600], strides: [600, 1] : memref<600xf64> to memref<1x600xf64>
    %subview_9 = memref.subview %4[0, 0] [1, 600] [1, 1] : memref<1x600xf64> to memref<600xf64, strided<[1]>>
    %subview_10 = memref.subview %reinterpret_cast_8[0, 0] [1, 600] [1, 1] : memref<1x600xf64> to memref<600xf64, strided<[1]>>
    %6 = dma.start_transfer from %subview_9 : memref<600xf64, strided<[1]>> to %subview_10 : memref<600xf64, strided<[1]>>
    dma.wait_for_transfer %6
    quidditch_snitch.barrier
    quidditch_snitch.barrier
    %7 = dma.start_transfer from %subview_10 : memref<600xf64, strided<[1]>> to %subview_9 : memref<600xf64, strided<[1]>>
    dma.wait_for_transfer %7
    quidditch_snitch.barrier
    return
  }
  llvm.func @snrt_cluster_core_idx() -> i32 attributes {hal.import.bitcode}
  llvm.func @snrt_dma_start_1d(!llvm.ptr, !llvm.ptr, i32) -> i32 attributes {hal.import.bitcode}
  llvm.func @snrt_dma_start_2d(!llvm.ptr, !llvm.ptr, i32, i32, i32, i32) -> i32 attributes {hal.import.bitcode}
}
```

