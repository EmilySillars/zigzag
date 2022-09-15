Workload
========

The recommended way of defining an algorithmic workload is through an onnx model. An onnx model can contain multiple operator types, which in the context of ML are often referred to as layers, some of which are automatically recognised and parsed by zigzag. Alternatively, the layers can be manually defined for more customization.

Supported onnx operators
------------------------

A complete list of all onnx operators can be found `here <https://github.com/onnx/onnx/blob/main/docs/Operators.md>`_.

Following operators are supported by zigzag and will automatically be parsed into ``LayerNode`` objects when using your onnx model within the framework:

* `QLinearConv <https://github.com/onnx/onnx/blob/main/docs/Operators.md#QLinearConv>`_
* `MatMul <https://github.com/onnx/onnx/blob/main/docs/Operators.md#MatMul>`_

All other operators will be parsed into a ``DummyNode`` object, which is assumed to not be accelerateable, incurring 0 hardware cost. If you have an onnx operator you would like to see supported, feel free to `open an issue <https://github.com/ZigZag-Project/zigzag/issues/new>`_ or manually add it yourself in the `ONNXModelParserStage <https://github.com/ZigZag-Project/zigzag/blob/8bce029a4284b720d8957357db74d629bd894dc6/classes/stages/ONNXModelParserStage.py#L314>`_ taking into account the :ref:`contributing guidelines`.


Manual layer definition
-----------------------

It is also possible to manually define your own workload layers. In that case there the ``main.py`` file should be executed instead of ``main_onnx.py``. Moreover, the workload file should be provided as input together with the accelerator, thus there is no onnx model and mapping file loaded. The mapping information is inserted for each layer alongside the layer shape definition, identically to how it was defined in the mapping file. 

An example can be found at: `inputs/examples/workloads/resnet18.py <https://github.com/ZigZag-Project/zigzag/blob/master/inputs/examples/workloads/resnet18.py>`_. 

Each layer definition is represented as a dict which should have the following attributes:

* **equation**: The operational equation for this layer. The dimensions should be small letters, where as the operands are large letters. 'O' should always be used for the output operand, the input operands can be named freely.
* **dimension_relations**: The relationship between different dimensions present in the equation. This is often used in convolutional layers, where there is a relationship between the spatial input indices and the spatial output indices through the stride and with the filter indices through the dilation rate.
* **loop_dim_size**: The size of the different dimensions present in the equation. Dimensions defined (i.e. on the left hand side) in the dimension_relations are not to be provided and are inferred automatically.
* **operand_precision**: The bit precision of the different operands present in the equation. 'O' should always be used, which represents the partial output precision. 'O_final' represents the final output precision.
* **operand_source**: The layer id the input operands of this layer come from. This is important to correctly build the NN graph edges.
* **constant_operands**: The operands of this layer which are constants and do not depend on prior computations.
* **core_allocation**: The core that will execute this layer.
* **spatial_mapping**: The spatial parallelization strategy used for this layer. If none is provided, the SpatialMappingGeneratorStage should be used within zigzag's execution pipeline.
* **memory_operand_links**: The link between the virtual memory operands and the actual algorithmic operands. For more information, read the hardware readme.