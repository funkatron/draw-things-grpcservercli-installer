# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

import image_generation_pb2 as image__generation__pb2

GRPC_GENERATED_VERSION = '1.71.0'
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
        + f' but the generated code in image_generation_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class ImageGenerationServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Echo = channel.unary_unary(
                '/drawthings.ImageGenerationService/Echo',
                request_serializer=image__generation__pb2.EchoRequest.SerializeToString,
                response_deserializer=image__generation__pb2.EchoResponse.FromString,
                _registered_method=True)
        self.FilesExist = channel.unary_unary(
                '/drawthings.ImageGenerationService/FilesExist',
                request_serializer=image__generation__pb2.FilesExistRequest.SerializeToString,
                response_deserializer=image__generation__pb2.FilesExistResponse.FromString,
                _registered_method=True)
        self.GenerateImage = channel.unary_unary(
                '/drawthings.ImageGenerationService/GenerateImage',
                request_serializer=image__generation__pb2.ImageGenerationRequest.SerializeToString,
                response_deserializer=image__generation__pb2.ImageGenerationResponse.FromString,
                _registered_method=True)
        self.UploadFile = channel.stream_unary(
                '/drawthings.ImageGenerationService/UploadFile',
                request_serializer=image__generation__pb2.UploadFileRequest.SerializeToString,
                response_deserializer=image__generation__pb2.UploadFileResponse.FromString,
                _registered_method=True)


class ImageGenerationServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def Echo(self, request, context):
        """Echo endpoint for health check
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def FilesExist(self, request, context):
        """Check if model files exist
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GenerateImage(self, request, context):
        """Generate images based on parameters
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def UploadFile(self, request_iterator, context):
        """Upload model files
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ImageGenerationServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Echo': grpc.unary_unary_rpc_method_handler(
                    servicer.Echo,
                    request_deserializer=image__generation__pb2.EchoRequest.FromString,
                    response_serializer=image__generation__pb2.EchoResponse.SerializeToString,
            ),
            'FilesExist': grpc.unary_unary_rpc_method_handler(
                    servicer.FilesExist,
                    request_deserializer=image__generation__pb2.FilesExistRequest.FromString,
                    response_serializer=image__generation__pb2.FilesExistResponse.SerializeToString,
            ),
            'GenerateImage': grpc.unary_unary_rpc_method_handler(
                    servicer.GenerateImage,
                    request_deserializer=image__generation__pb2.ImageGenerationRequest.FromString,
                    response_serializer=image__generation__pb2.ImageGenerationResponse.SerializeToString,
            ),
            'UploadFile': grpc.stream_unary_rpc_method_handler(
                    servicer.UploadFile,
                    request_deserializer=image__generation__pb2.UploadFileRequest.FromString,
                    response_serializer=image__generation__pb2.UploadFileResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'drawthings.ImageGenerationService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('drawthings.ImageGenerationService', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class ImageGenerationService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def Echo(request,
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
            '/drawthings.ImageGenerationService/Echo',
            image__generation__pb2.EchoRequest.SerializeToString,
            image__generation__pb2.EchoResponse.FromString,
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
    def FilesExist(request,
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
            '/drawthings.ImageGenerationService/FilesExist',
            image__generation__pb2.FilesExistRequest.SerializeToString,
            image__generation__pb2.FilesExistResponse.FromString,
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
    def GenerateImage(request,
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
            '/drawthings.ImageGenerationService/GenerateImage',
            image__generation__pb2.ImageGenerationRequest.SerializeToString,
            image__generation__pb2.ImageGenerationResponse.FromString,
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
    def UploadFile(request_iterator,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.stream_unary(
            request_iterator,
            target,
            '/drawthings.ImageGenerationService/UploadFile',
            image__generation__pb2.UploadFileRequest.SerializeToString,
            image__generation__pb2.UploadFileResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
