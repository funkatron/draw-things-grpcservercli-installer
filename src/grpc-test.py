#!/usr/bin/env python3
"""
Test script for exploring and testing the Draw Things gRPC server API.
Uses discovered service and method names from the app bundle.
"""

import argparse
import grpc
import os
import sys
from pathlib import Path
from grpc_reflection.v1alpha import reflection_pb2, reflection_pb2_grpc
from google.protobuf import descriptor_pb2, descriptor_pool
import json

class ImageGenerationStub:
    """Stub for ImageGenerationService."""

    def __init__(self):
        self.service_name = "ImageGenerationService"

    def get_service_descriptor(self, channel):
        """Get the service descriptor using reflection."""
        reflection_stub = reflection_pb2_grpc.ServerReflectionStub(channel)

        try:
            # List services first
            list_request = reflection_pb2.ServerReflectionRequest(
                list_services=""
            )
            responses = reflection_stub.ServerReflectionInfo(iter([list_request]))

            for response in responses:
                if response.HasField('list_services_response'):
                    for service in response.list_services_response.service:
                        print(f"Found service: {service.name}")
                        if service.name == self.service_name:
                            # Now get the file descriptor for this service
                            file_request = reflection_pb2.ServerReflectionRequest(
                                file_containing_symbol=self.service_name
                            )
                            file_responses = reflection_stub.ServerReflectionInfo(iter([file_request]))

                            for file_response in file_responses:
                                if file_response.HasField('file_descriptor_response'):
                                    pool = descriptor_pool.DescriptorPool()
                                    for file_proto in file_response.file_descriptor_response.file_descriptor_proto:
                                        fd = descriptor_pb2.FileDescriptorProto()
                                        fd.ParseFromString(file_proto)
                                        pool.Add(fd)
                                    return pool.FindServiceByName(self.service_name)
                break

            print("Service not found in reflection data")
            return None

        except Exception as e:
            print(f"Error during reflection: {str(e)}")
            return None

    def Echo(self, request):
        """Test connection with Echo method."""
        method = '/ImageGenerationService/Echo'
        return self._channel.unary_unary(
            method,
            request_serializer=lambda x: b'',  # Empty request
            response_deserializer=lambda x: x,
        )(b'')

    def FilesExist(self, request):
        """Check if model files exist."""
        method = '/ImageGenerationService/FilesExist'
        return self._channel.unary_unary(
            method,
            request_serializer=lambda x: x.SerializeToString(),
            response_deserializer=lambda x: x,
        )(request)

    def GenerateImage(self, request):
        """Generate an image."""
        method = '/ImageGenerationService/GenerateImage'
        return self._channel.unary_unary(
            method,
            request_serializer=lambda x: x.SerializeToString(),
            response_deserializer=lambda x: x,
        )(request)

    def UploadFile(self, request_iterator):
        """Upload a file."""
        method = '/ImageGenerationService/UploadFile'
        return self._channel.stream_unary(
            method,
            request_serializer=lambda x: x.SerializeToString(),
            response_deserializer=lambda x: x,
        )(request_iterator)

    def files_exist(self, channel):
        """Test the FilesExist endpoint."""
        print("\nTesting FilesExist endpoint...")

        try:
            # Create a request with a list of files to check
            request = [
                "stable-diffusion/model.safetensors",
                "vae/model.safetensors",
                "nonexistent-file.txt"
            ]

            # Call the FilesExist method
            method = channel.unary_unary(
                f'/{self.service_name}/FilesExist',
                request_serializer=lambda x: json.dumps(x).encode('utf-8'),
                response_deserializer=lambda x: json.loads(x.decode('utf-8')) if x else None
            )

            print("\nSending request:", json.dumps(request, indent=2))
            response = method(request)
            print("\nFilesExist response:", json.dumps(response, indent=2) if response else "No response")
            return True

        except grpc.RpcError as e:
            print(f"\nRPC Error: {e.details()}")
            return False
        except Exception as e:
            print(f"\nError: {str(e)}")
            return False

def parse_args():
    parser = argparse.ArgumentParser(description='Test Draw Things gRPC server API')
    parser.add_argument('--host', default='localhost',
                      help='Server hostname (default: localhost)')
    parser.add_argument('--port', type=int, default=7859,
                      help='Server port (default: 7859)')
    parser.add_argument('--shared-secret',
                      help='Shared secret for authentication')
    parser.add_argument('--model-path',
                      default=str(Path.home() / "Library/Containers/com.liuliu.draw-things/Data/Documents/Models"),
                      help='Path to model directory')
    parser.add_argument('--tls', action='store_true',
                      help='Use TLS connection')
    parser.add_argument('--debug', action='store_true',
                      help='Enable debug logging')
    parser.add_argument('--method', choices=['echo', 'files_exist', 'generate', 'upload'],
                      default='echo',
                      help='Method to test (default: echo)')

    return parser.parse_args()

def create_channel(args):
    """Create a gRPC channel with appropriate options."""
    target = f"{args.host}:{args.port}"

    # Add authentication if provided
    options = []
    if args.shared_secret:
        options.append(('grpc.ssl_target_name_override', args.shared_secret))

    if args.tls:
        # Create secure channel with TLS
        credentials = grpc.ssl_channel_credentials()
        channel = grpc.secure_channel(target, credentials, options=options)
    else:
        # Create insecure channel
        channel = grpc.insecure_channel(target, options=options)

    return channel

def test_echo(stub):
    """Test the Echo endpoint."""
    try:
        response = stub.Echo(b'')
        print("\nEcho response:", response)
        return True
    except Exception as e:
        print(f"\nEcho failed: {e}")
        return False

def test_connection(channel, args):
    """Test connection to the server using the specified method."""
    try:
        stub = ImageGenerationStub()

        if args.method == 'echo':
            return test_echo(stub)
        elif args.method == 'files_exist':
            return stub.files_exist(channel)
        elif args.method == 'generate':
            print("\nGenerate image test not implemented yet")
            return True
        elif args.method == 'upload':
            print("\nUpload file test not implemented yet")
            return True

    except Exception as e:
        print(f"Failed to connect to server: {e}")
        return False

def main():
    args = parse_args()

    if args.debug:
        print(f"Connecting to {args.host}:{args.port}")
        print(f"Model path: {args.model_path}")
        print(f"TLS enabled: {args.tls}")
        print(f"Testing method: {args.method}")

    try:
        channel = create_channel(args)
        if test_connection(channel, args):
            print("\nServer test successful")
        else:
            print("\nServer test failed")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
