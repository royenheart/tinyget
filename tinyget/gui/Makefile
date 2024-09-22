.PHONY: main format

all: main format
	@echo "Done"

main: tinyget.proto
	python -m grpc_tools.protoc -I. --python_out=. --pyi_out=. --grpc_python_out=. ./tinyget.proto
	sed -i 's#import tinyget_pb2 as tinyget__pb#import tinyget.gui.tinyget_pb2 as tinyget__pb#g' tinyget_pb2_grpc.py

format:
	black . --verbose