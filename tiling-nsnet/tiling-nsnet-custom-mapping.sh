echo $1
cd ..

rm -r outputs/snitch-cluster-only-floats-no-ssrs-$1

python main_zigzag_integration.py \
--model=zigzag/inputs/workload/$1.yaml \
--mapping=zigzag/inputs/mapping/$2.yaml \
--accelerator=zigzag/inputs/hardware/snitch-cluster-only-floats-no-ssrs.yaml && \
cat outputs/snitch-cluster-only-floats-no-ssrs-$1/overall_simple.json

cd tiling-nsnet