# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

import tinyget.gui.tinyget_pb2 as tinyget__pb2

GRPC_GENERATED_VERSION = '1.66.1'
GRPC_VERSION = grpc.__version__
_version_not_supported = False

try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True

if _version_not_supported:
    raise RuntimeError(
        f'The grpc package installed is at version {GRPC_VERSION},'
        + f' but the generated code in tinyget_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class TinygetGRPCStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.SoftsGet = channel.unary_unary(
                '/tinyget_grpc.TinygetGRPC/SoftsGet',
                request_serializer=tinyget__pb2.SoftsResquest.SerializeToString,
                response_deserializer=tinyget__pb2.SoftsResp.FromString,
                _registered_method=True)
        self.SoftsGetStream = channel.unary_stream(
                '/tinyget_grpc.TinygetGRPC/SoftsGetStream',
                request_serializer=tinyget__pb2.SoftsResquest.SerializeToString,
                response_deserializer=tinyget__pb2.Package.FromString,
                _registered_method=True)
        self.SoftsGetBidiStream = channel.stream_stream(
                '/tinyget_grpc.TinygetGRPC/SoftsGetBidiStream',
                request_serializer=tinyget__pb2.SoftsResquest.SerializeToString,
                response_deserializer=tinyget__pb2.Package.FromString,
                _registered_method=True)
        self.SoftsInstall = channel.unary_unary(
                '/tinyget_grpc.TinygetGRPC/SoftsInstall',
                request_serializer=tinyget__pb2.SoftsInstallRequests.SerializeToString,
                response_deserializer=tinyget__pb2.SoftsInstallResp.FromString,
                _registered_method=True)
        self.SoftsInstallStream = channel.unary_stream(
                '/tinyget_grpc.TinygetGRPC/SoftsInstallStream',
                request_serializer=tinyget__pb2.SoftsInstallRequests.SerializeToString,
                response_deserializer=tinyget__pb2.SoftsInstallResp.FromString,
                _registered_method=True)
        self.SoftsInstallBidiStream = channel.stream_stream(
                '/tinyget_grpc.TinygetGRPC/SoftsInstallBidiStream',
                request_serializer=tinyget__pb2.SoftsInstallRequests.SerializeToString,
                response_deserializer=tinyget__pb2.SoftsInstallResp.FromString,
                _registered_method=True)
        self.SoftsUninstall = channel.unary_unary(
                '/tinyget_grpc.TinygetGRPC/SoftsUninstall',
                request_serializer=tinyget__pb2.SoftsUninstallRequests.SerializeToString,
                response_deserializer=tinyget__pb2.SoftsUninstallResp.FromString,
                _registered_method=True)
        self.SoftsUninstallStream = channel.unary_stream(
                '/tinyget_grpc.TinygetGRPC/SoftsUninstallStream',
                request_serializer=tinyget__pb2.SoftsUninstallRequests.SerializeToString,
                response_deserializer=tinyget__pb2.SoftsUninstallResp.FromString,
                _registered_method=True)
        self.SoftsUninstallBidiStream = channel.stream_stream(
                '/tinyget_grpc.TinygetGRPC/SoftsUninstallBidiStream',
                request_serializer=tinyget__pb2.SoftsUninstallRequests.SerializeToString,
                response_deserializer=tinyget__pb2.SoftsUninstallResp.FromString,
                _registered_method=True)
        self.SysUpdate = channel.unary_unary(
                '/tinyget_grpc.TinygetGRPC/SysUpdate',
                request_serializer=tinyget__pb2.SysUpdateRequest.SerializeToString,
                response_deserializer=tinyget__pb2.SysUpdateResp.FromString,
                _registered_method=True)
        self.SysUpdateStream = channel.unary_stream(
                '/tinyget_grpc.TinygetGRPC/SysUpdateStream',
                request_serializer=tinyget__pb2.SysUpdateRequest.SerializeToString,
                response_deserializer=tinyget__pb2.SysUpdateResp.FromString,
                _registered_method=True)
        self.SysUpdateBidiStream = channel.stream_stream(
                '/tinyget_grpc.TinygetGRPC/SysUpdateBidiStream',
                request_serializer=tinyget__pb2.SysUpdateRequest.SerializeToString,
                response_deserializer=tinyget__pb2.SysUpdateResp.FromString,
                _registered_method=True)
        self.SysHistory = channel.unary_unary(
                '/tinyget_grpc.TinygetGRPC/SysHistory',
                request_serializer=tinyget__pb2.SysHistoryRequest.SerializeToString,
                response_deserializer=tinyget__pb2.SysHistoryResp.FromString,
                _registered_method=True)
        self.SysHistoryStream = channel.unary_stream(
                '/tinyget_grpc.TinygetGRPC/SysHistoryStream',
                request_serializer=tinyget__pb2.SysHistoryRequest.SerializeToString,
                response_deserializer=tinyget__pb2.History.FromString,
                _registered_method=True)
        self.SysHistoryBidiStream = channel.stream_stream(
                '/tinyget_grpc.TinygetGRPC/SysHistoryBidiStream',
                request_serializer=tinyget__pb2.SysHistoryRequest.SerializeToString,
                response_deserializer=tinyget__pb2.History.FromString,
                _registered_method=True)


class TinygetGRPCServicer(object):
    """Missing associated documentation comment in .proto file."""

    def SoftsGet(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SoftsGetStream(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SoftsGetBidiStream(self, request_iterator, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SoftsInstall(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SoftsInstallStream(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SoftsInstallBidiStream(self, request_iterator, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SoftsUninstall(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SoftsUninstallStream(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SoftsUninstallBidiStream(self, request_iterator, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SysUpdate(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SysUpdateStream(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SysUpdateBidiStream(self, request_iterator, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SysHistory(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SysHistoryStream(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SysHistoryBidiStream(self, request_iterator, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_TinygetGRPCServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'SoftsGet': grpc.unary_unary_rpc_method_handler(
                    servicer.SoftsGet,
                    request_deserializer=tinyget__pb2.SoftsResquest.FromString,
                    response_serializer=tinyget__pb2.SoftsResp.SerializeToString,
            ),
            'SoftsGetStream': grpc.unary_stream_rpc_method_handler(
                    servicer.SoftsGetStream,
                    request_deserializer=tinyget__pb2.SoftsResquest.FromString,
                    response_serializer=tinyget__pb2.Package.SerializeToString,
            ),
            'SoftsGetBidiStream': grpc.stream_stream_rpc_method_handler(
                    servicer.SoftsGetBidiStream,
                    request_deserializer=tinyget__pb2.SoftsResquest.FromString,
                    response_serializer=tinyget__pb2.Package.SerializeToString,
            ),
            'SoftsInstall': grpc.unary_unary_rpc_method_handler(
                    servicer.SoftsInstall,
                    request_deserializer=tinyget__pb2.SoftsInstallRequests.FromString,
                    response_serializer=tinyget__pb2.SoftsInstallResp.SerializeToString,
            ),
            'SoftsInstallStream': grpc.unary_stream_rpc_method_handler(
                    servicer.SoftsInstallStream,
                    request_deserializer=tinyget__pb2.SoftsInstallRequests.FromString,
                    response_serializer=tinyget__pb2.SoftsInstallResp.SerializeToString,
            ),
            'SoftsInstallBidiStream': grpc.stream_stream_rpc_method_handler(
                    servicer.SoftsInstallBidiStream,
                    request_deserializer=tinyget__pb2.SoftsInstallRequests.FromString,
                    response_serializer=tinyget__pb2.SoftsInstallResp.SerializeToString,
            ),
            'SoftsUninstall': grpc.unary_unary_rpc_method_handler(
                    servicer.SoftsUninstall,
                    request_deserializer=tinyget__pb2.SoftsUninstallRequests.FromString,
                    response_serializer=tinyget__pb2.SoftsUninstallResp.SerializeToString,
            ),
            'SoftsUninstallStream': grpc.unary_stream_rpc_method_handler(
                    servicer.SoftsUninstallStream,
                    request_deserializer=tinyget__pb2.SoftsUninstallRequests.FromString,
                    response_serializer=tinyget__pb2.SoftsUninstallResp.SerializeToString,
            ),
            'SoftsUninstallBidiStream': grpc.stream_stream_rpc_method_handler(
                    servicer.SoftsUninstallBidiStream,
                    request_deserializer=tinyget__pb2.SoftsUninstallRequests.FromString,
                    response_serializer=tinyget__pb2.SoftsUninstallResp.SerializeToString,
            ),
            'SysUpdate': grpc.unary_unary_rpc_method_handler(
                    servicer.SysUpdate,
                    request_deserializer=tinyget__pb2.SysUpdateRequest.FromString,
                    response_serializer=tinyget__pb2.SysUpdateResp.SerializeToString,
            ),
            'SysUpdateStream': grpc.unary_stream_rpc_method_handler(
                    servicer.SysUpdateStream,
                    request_deserializer=tinyget__pb2.SysUpdateRequest.FromString,
                    response_serializer=tinyget__pb2.SysUpdateResp.SerializeToString,
            ),
            'SysUpdateBidiStream': grpc.stream_stream_rpc_method_handler(
                    servicer.SysUpdateBidiStream,
                    request_deserializer=tinyget__pb2.SysUpdateRequest.FromString,
                    response_serializer=tinyget__pb2.SysUpdateResp.SerializeToString,
            ),
            'SysHistory': grpc.unary_unary_rpc_method_handler(
                    servicer.SysHistory,
                    request_deserializer=tinyget__pb2.SysHistoryRequest.FromString,
                    response_serializer=tinyget__pb2.SysHistoryResp.SerializeToString,
            ),
            'SysHistoryStream': grpc.unary_stream_rpc_method_handler(
                    servicer.SysHistoryStream,
                    request_deserializer=tinyget__pb2.SysHistoryRequest.FromString,
                    response_serializer=tinyget__pb2.History.SerializeToString,
            ),
            'SysHistoryBidiStream': grpc.stream_stream_rpc_method_handler(
                    servicer.SysHistoryBidiStream,
                    request_deserializer=tinyget__pb2.SysHistoryRequest.FromString,
                    response_serializer=tinyget__pb2.History.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'tinyget_grpc.TinygetGRPC', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('tinyget_grpc.TinygetGRPC', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class TinygetGRPC(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def SoftsGet(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/tinyget_grpc.TinygetGRPC/SoftsGet',
            tinyget__pb2.SoftsResquest.SerializeToString,
            tinyget__pb2.SoftsResp.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def SoftsGetStream(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(
            request,
            target,
            '/tinyget_grpc.TinygetGRPC/SoftsGetStream',
            tinyget__pb2.SoftsResquest.SerializeToString,
            tinyget__pb2.Package.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def SoftsGetBidiStream(request_iterator,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.stream_stream(
            request_iterator,
            target,
            '/tinyget_grpc.TinygetGRPC/SoftsGetBidiStream',
            tinyget__pb2.SoftsResquest.SerializeToString,
            tinyget__pb2.Package.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def SoftsInstall(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/tinyget_grpc.TinygetGRPC/SoftsInstall',
            tinyget__pb2.SoftsInstallRequests.SerializeToString,
            tinyget__pb2.SoftsInstallResp.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def SoftsInstallStream(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(
            request,
            target,
            '/tinyget_grpc.TinygetGRPC/SoftsInstallStream',
            tinyget__pb2.SoftsInstallRequests.SerializeToString,
            tinyget__pb2.SoftsInstallResp.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def SoftsInstallBidiStream(request_iterator,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.stream_stream(
            request_iterator,
            target,
            '/tinyget_grpc.TinygetGRPC/SoftsInstallBidiStream',
            tinyget__pb2.SoftsInstallRequests.SerializeToString,
            tinyget__pb2.SoftsInstallResp.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def SoftsUninstall(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/tinyget_grpc.TinygetGRPC/SoftsUninstall',
            tinyget__pb2.SoftsUninstallRequests.SerializeToString,
            tinyget__pb2.SoftsUninstallResp.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def SoftsUninstallStream(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(
            request,
            target,
            '/tinyget_grpc.TinygetGRPC/SoftsUninstallStream',
            tinyget__pb2.SoftsUninstallRequests.SerializeToString,
            tinyget__pb2.SoftsUninstallResp.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def SoftsUninstallBidiStream(request_iterator,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.stream_stream(
            request_iterator,
            target,
            '/tinyget_grpc.TinygetGRPC/SoftsUninstallBidiStream',
            tinyget__pb2.SoftsUninstallRequests.SerializeToString,
            tinyget__pb2.SoftsUninstallResp.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def SysUpdate(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/tinyget_grpc.TinygetGRPC/SysUpdate',
            tinyget__pb2.SysUpdateRequest.SerializeToString,
            tinyget__pb2.SysUpdateResp.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def SysUpdateStream(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(
            request,
            target,
            '/tinyget_grpc.TinygetGRPC/SysUpdateStream',
            tinyget__pb2.SysUpdateRequest.SerializeToString,
            tinyget__pb2.SysUpdateResp.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def SysUpdateBidiStream(request_iterator,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.stream_stream(
            request_iterator,
            target,
            '/tinyget_grpc.TinygetGRPC/SysUpdateBidiStream',
            tinyget__pb2.SysUpdateRequest.SerializeToString,
            tinyget__pb2.SysUpdateResp.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def SysHistory(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/tinyget_grpc.TinygetGRPC/SysHistory',
            tinyget__pb2.SysHistoryRequest.SerializeToString,
            tinyget__pb2.SysHistoryResp.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def SysHistoryStream(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(
            request,
            target,
            '/tinyget_grpc.TinygetGRPC/SysHistoryStream',
            tinyget__pb2.SysHistoryRequest.SerializeToString,
            tinyget__pb2.History.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def SysHistoryBidiStream(request_iterator,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.stream_stream(
            request_iterator,
            target,
            '/tinyget_grpc.TinygetGRPC/SysHistoryBidiStream',
            tinyget__pb2.SysHistoryRequest.SerializeToString,
            tinyget__pb2.History.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
