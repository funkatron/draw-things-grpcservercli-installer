import pytest
import grpc
from unittest.mock import patch, MagicMock
from dts_util.grpc.utils import is_server_running, handle_grpc_error, create_channel_and_stub
from dts_util.grpc.proto.image_generation_pb2_grpc import ImageGenerationServiceStub

def test_is_server_running_nonexistent():
    """Test that is_server_running returns False for non-existent server."""
    # Test with a port that's unlikely to have a server
    assert not is_server_running(port=65432, timeout=0.1)

def test_is_server_running_invalid_host():
    """Test that is_server_running handles invalid hostnames gracefully."""
    assert not is_server_running(host="nonexistent.local", timeout=0.1)

def test_is_server_running_zero_timeout():
    """Test that is_server_running works with zero timeout."""
    assert not is_server_running(timeout=0)

def test_is_server_running_timeout():
    """Test that is_server_running handles FutureTimeoutError correctly."""
    with patch('grpc.insecure_channel') as mock_channel:
        mock_future = MagicMock()
        mock_future.result.side_effect = grpc.FutureTimeoutError()
        mock_channel.return_value.__enter__.return_value = MagicMock()
        with patch('grpc.channel_ready_future', return_value=mock_future):
            assert not is_server_running(timeout=0.1)

class MockInactiveRpcError(grpc.RpcError, Exception):
    """Mock gRPC error for testing."""
    def __init__(self, code, details):
        self._code = code
        self._details = details

    def code(self):
        return self._code

    def details(self):
        return self._details

def test_handle_grpc_error_unavailable():
    """Test that handle_grpc_error converts UNAVAILABLE errors to ConnectionError."""
    error = MockInactiveRpcError(grpc.StatusCode.UNAVAILABLE, "Server unavailable")

    with pytest.raises(ConnectionError, match="Server is unavailable"):
        with handle_grpc_error():
            raise error

def test_handle_grpc_error_other():
    """Test that handle_grpc_error preserves other gRPC errors."""
    error = MockInactiveRpcError(grpc.StatusCode.INTERNAL, "Internal error")

    with pytest.raises(grpc.RpcError):
        with handle_grpc_error():
            raise error

def test_handle_grpc_error_non_grpc():
    """Test that handle_grpc_error lets non-gRPC errors pass through."""
    with pytest.raises(ValueError, match="Regular error"):
        with handle_grpc_error():
            raise ValueError("Regular error")

def test_handle_grpc_error_no_code():
    """Test that handle_grpc_error handles gRPC errors without code method."""
    class NoCodeError(grpc.RpcError):
        pass

    with pytest.raises(grpc.RpcError):
        with handle_grpc_error():
            raise NoCodeError()

def test_create_channel_and_stub_insecure():
    """Test that create_channel_and_stub creates insecure channels correctly."""
    with patch('grpc.insecure_channel') as mock_channel, \
         patch('dts_util.grpc.utils.is_server_running', return_value=True):
        mock_channel.return_value = MagicMock()
        channel, stub = create_channel_and_stub(use_tls=False)
        mock_channel.assert_called_once()
        assert isinstance(stub, ImageGenerationServiceStub)

def test_create_channel_and_stub_secure():
    """Test that create_channel_and_stub creates secure channels correctly."""
    with patch('grpc.secure_channel') as mock_channel, \
         patch('grpc.ssl_channel_credentials') as mock_creds, \
         patch('dts_util.grpc.utils.is_server_running', return_value=True):
        mock_channel.return_value = MagicMock()
        channel, stub = create_channel_and_stub(use_tls=True)
        mock_channel.assert_called_once_with(
            'localhost:50051',
            mock_creds.return_value,
            options=[]
        )
        assert isinstance(stub, ImageGenerationServiceStub)

def test_create_channel_and_stub_shared_secret():
    """Test that create_channel_and_stub adds shared secret to options."""
    with patch('grpc.insecure_channel') as mock_channel, \
         patch('dts_util.grpc.utils.is_server_running', return_value=True):
        mock_channel.return_value = MagicMock()
        create_channel_and_stub(use_tls=False, shared_secret="test_secret")
        mock_channel.assert_called_once()
        call_args = mock_channel.call_args[1]
        assert ('grpc.primary_user_agent', 'secret=test_secret') in call_args['options']

def test_create_channel_and_stub_custom_host_port():
    """Test that create_channel_and_stub handles custom host and port."""
    with patch('grpc.insecure_channel') as mock_channel, \
         patch('dts_util.grpc.utils.is_server_running', return_value=True):
        mock_channel.return_value = MagicMock()
        create_channel_and_stub(host='example.com', port=12345, use_tls=False)
        mock_channel.assert_called_once_with('example.com:12345', options=[])

def test_create_channel_and_stub_server_not_running():
    """Test that create_channel_and_stub raises ConnectionError when server is not running."""
    with patch('dts_util.grpc.utils.is_server_running', return_value=False):
        with pytest.raises(ConnectionError, match="Unable to connect to server"):
            create_channel_and_stub(port=65432)  # Use a port that's not running