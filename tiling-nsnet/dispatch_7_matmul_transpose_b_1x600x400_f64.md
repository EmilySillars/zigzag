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
    for b in [0, 400)
    for c in [0, 600)
        O[a][b]+=I[a][c]*transpose(W)[b][c]
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
  loop_sizes: [1, 400, 600] 
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



## JSON Summary

