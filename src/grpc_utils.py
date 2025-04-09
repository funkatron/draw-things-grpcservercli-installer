"""Utility functions for working with the Draw Things gRPC server."""

import grpc
from contextlib import contextmanager
from typing import Optional, Tuple

def is_server_running(host: str = 'localhost', port: int = 50051, timeout: float = 1) -> bool:
    """Check if the gRPC server is running.

    Args:
        host: Server hostname
        port: Server port
        timeout: Connection timeout in seconds

    Returns:
        bool: True if server is running and accepting connections
    """
    try:
        with grpc.insecure_channel(f'{host}:{port}') as channel:
            try:
                grpc.channel_ready_future(channel).result(timeout=timeout)
                return True
            except grpc.FutureTimeoutError:
                return False
    except Exception:
        return False

@contextmanager
def handle_grpc_error():
    """Context manager to handle gRPC errors gracefully.

    Raises:
        grpc.RpcError: If a non-connection related error occurs
    """
    try:
        yield
    except grpc.RpcError as e:
        if isinstance(e, grpc._channel._InactiveRpcError):
            if e.code() == grpc.StatusCode.UNAVAILABLE:
                raise ConnectionError("Server is unavailable")
            else:
                raise
        else:
            raise

# Only import these if you need to create a channel with the specific service stub
try:
    from image_generation_pb2_grpc import ImageGenerationServiceStub

    def create_channel_and_stub(
        host: str = 'localhost',
        port: int = 50051,
        use_tls: bool = True,
        shared_secret: Optional[str] = None
    ) -> Tuple[grpc.Channel, ImageGenerationServiceStub]:
        """Create a gRPC channel and stub for communicating with the server.

        Args:
            host: Server hostname
            port: Server port
            use_tls: Whether to use TLS encryption
            shared_secret: Optional shared secret for authentication

        Returns:
            Tuple containing:
            - grpc.Channel: The created channel
            - ImageGenerationServiceStub: Stub for making RPC calls

        Raises:
            ConnectionError: If server is not running
        """
        # Build channel options
        options = []
        if shared_secret:
            options.append(('grpc.primary_user_agent', f'secret={shared_secret}'))

        # Create appropriate channel
        target = f'{host}:{port}'
        if use_tls:
            channel = grpc.secure_channel(target, grpc.ssl_channel_credentials(), options=options)
        else:
            channel = grpc.insecure_channel(target, options=options)

        # Verify connection
        if not is_server_running(host, port):
            raise ConnectionError(f"Unable to connect to server at {target}")

        return channel, ImageGenerationServiceStub(channel)
except ImportError:
    # The ImageGenerationServiceStub is not available
    pass