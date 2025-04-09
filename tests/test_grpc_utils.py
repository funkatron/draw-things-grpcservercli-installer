import pytest
from dts_util.grpc.utils import is_server_running, handle_grpc_error

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