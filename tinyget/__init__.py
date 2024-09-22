import warnings

# protobuf outdated warnings
# see: https://github.com/grpc/grpc/issues/37609
warnings.filterwarnings(
    "ignore", ".*obsolete", UserWarning, "google.protobuf.runtime_version"
)
