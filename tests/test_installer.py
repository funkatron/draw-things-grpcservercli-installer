#!/usr/bin/env python3
"""Tests for the Draw Things gRPCServer installer."""
import os
import socket
import pytest
import sys
import importlib.util
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import the installer script by path since it has a hyphen in the name
SCRIPT_PATH = Path(__file__).parent.parent / 'src' / 'install-gRPCServerCLI.py'
spec = importlib.util.spec_from_file_location("installer", SCRIPT_PATH)
installer_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer_module)

@pytest.fixture
def installer(mock_home_dir):
    """Return a fresh DrawThingsInstaller instance."""
    return installer_module.DrawThingsInstaller()

def test_default_port(installer):
    """Test that the default port is 7859."""
    assert installer.DEFAULT_PORT == 7859

def test_default_name(installer):
    """Test that the default name is derived from hostname."""
    hostname = socket.gethostname()
    # Remove .local suffix if present
    if hostname.endswith('.local'):
        hostname = hostname[:-6]
    assert installer.DEFAULT_NAME == hostname

def test_default_model_path(installer, mock_home_dir):
    """Test that the default model path is in the Draw Things container."""
    expected_path = Path(mock_home_dir) / "Library/Containers/com.liuliu.draw-things/Data/Documents/Models"
    assert installer.default_model_path == expected_path

def test_validate_join_config(installer):
    """Test join configuration validation."""
    # Test valid configurations
    valid_configs = [
        '{"host": "proxy.local", "port": 7859}',
        '{"host": "proxy.local", "port": 7859, "servers": [{"address": "gpu1.local", "port": 7859, "priority": 1}]}'
    ]
    for config in valid_configs:
        assert installer.validate_join_config(config)

    # Test invalid configurations
    invalid_configs = [
        '{}',  # Empty
        '{"host": "proxy.local"}',  # Missing port
        '{"port": 7859}',  # Missing host
        '{"host": "", "port": 7859}',  # Empty host
        '{"host": "proxy.local", "port": -1}',  # Invalid port
        'invalid json'  # Invalid JSON
    ]
    for config in invalid_configs:
        with pytest.raises(ValueError):
            installer.validate_join_config(config)

def test_check_port_available(installer, mock_socket):
    """Test port availability checking."""
    # Test port is available
    mock_socket.connect_ex.return_value = 1
    assert installer.check_port_available(7859)

    # Test port is in use
    mock_socket.connect_ex.return_value = 0
    assert not installer.check_port_available(7859)

def test_restart_service(installer, mock_subprocess, mock_home_dir):
    """Test service restart functionality."""
    # Create service file using temp home directory
    service_path = Path(mock_home_dir) / "Library/LaunchAgents" / f'{installer.SERVICE_NAME}.plist'
    service_path.parent.mkdir(parents=True, exist_ok=True)
    service_path.touch()

    # Update installer's AGENTS_DIR to use temp home
    installer.AGENTS_DIR = Path(mock_home_dir) / "Library/LaunchAgents"

    installer.restart_service()

    # Verify unload and load commands were called
    assert mock_subprocess.call_count == 2
    unload_call, load_call = mock_subprocess.call_args_list

    # Compare string representations of paths
    expected_unload = ['launchctl', 'unload', str(service_path)]
    expected_load = ['launchctl', 'load', str(service_path)]

    actual_unload = [str(arg) if isinstance(arg, Path) else arg for arg in unload_call[0][0]]
    actual_load = [str(arg) if isinstance(arg, Path) else arg for arg in load_call[0][0]]

    assert actual_unload == expected_unload
    assert actual_load == expected_load

def test_restart_service_not_installed(installer, mock_subprocess, mock_home_dir):
    """Test service restart when service is not installed."""
    # Update installer's AGENTS_DIR to use temp home
    installer.AGENTS_DIR = Path(mock_home_dir) / "Library/LaunchAgents"

    # Don't create the service file - this should trigger the error
    with pytest.raises(SystemExit) as exc_info:
        installer.restart_service()

    assert exc_info.value.code == 1  # Verify exit code is 1
    mock_subprocess.assert_not_called()

def test_prompt_user_quiet_mode(installer):
    """Test user prompts in quiet mode."""
    installer.quiet = True

    # Test with default 'n'
    assert not installer.prompt_user("Continue?")

    # Test with default 'y'
    assert installer.prompt_user("Continue?", default='y')

def test_prompt_user_interactive(installer, monkeypatch):
    """Test user prompts in interactive mode."""
    installer.quiet = False

    # Test 'y' response
    monkeypatch.setattr('builtins.input', lambda _: 'y')
    assert installer.prompt_user("Continue?")

    # Test 'n' response
    monkeypatch.setattr('builtins.input', lambda _: 'n')
    assert not installer.prompt_user("Continue?")

    # Test empty input (uses default)
    monkeypatch.setattr('builtins.input', lambda _: '')
    assert installer.prompt_user("Continue?", default='y')
    assert not installer.prompt_user("Continue?", default='n')