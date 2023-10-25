import pytest

from zigzag.api import get_hardware_performance_zigzag_with_mix_spatial_mapping

workloads = (
    "zigzag/inputs/examples/workload/alexnet.onnx",
    # "zigzag/inputs/examples/workload/mobilenetv2.onnx",
    # "zigzag/inputs/examples/workload/resnet18.onnx",
    # "zigzag.inputs.examples.workload.resnet18",
)

# Expected energy and latency for each workload defined above
ens_lats = {
    "zigzag/inputs/examples/workload/alexnet.onnx": (5667407342.66, 8528846),
    "zigzag/inputs/examples/workload/mobilenetv2.onnx": (1881386179.71, 6486685),
    "zigzag/inputs/examples/workload/resnet18.onnx": (1709089377.83, 3583047),
    "zigzag.inputs.examples.workload.resnet18": (2243493483.15, 4657130),
}


@pytest.fixture
def mapping():
    ascend_like_mapping = {
        "default": {
            "core_allocation": 1,
            "spatial_mapping": {
                "D1": ("K", 16),
                "D2": (("C", 4), ("FX", 3)),
                "D3": ("OX", 2),
                "D4": ("OY", 2),
            },
            "memory_operand_links": {"O": "O", "W": "I2", "I": "I1"},
        },
        "Add": {
            "core_allocation": 1,
            "spatial_mapping": {
                "D1": ("G", 16),
                "D2": ("C", 1),
                "D3": ("OX", 1),
                "D4": ("OY", 1),
            },
            "memory_operand_links": {"O": "O", "X": "I2", "Y": "I1"},
        },
    }

    return ascend_like_mapping


@pytest.fixture
def accelerator():
    return "zigzag.inputs.examples.hardware.Ascend_like"


@pytest.mark.parametrize("workload", workloads)
def test_api(workload, accelerator, mapping):
    (energy, latency, cmes) = get_hardware_performance_zigzag_with_mix_spatial_mapping(
        workload, accelerator, mapping
    )
    print(energy, latency)
    (expected_energy, expected_latency) = ens_lats[workload]
    assert energy == pytest.approx(expected_energy)
    assert latency == pytest.approx(expected_latency)
