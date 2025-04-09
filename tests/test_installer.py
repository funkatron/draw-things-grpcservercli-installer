#!/usr/bin/env python3
"""Tests for the Draw Things gRPCServer installer."""
import os
import socket
import pytest
import sys
import json
import urllib.request
import tempfile
import shutil
import plistlib
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open, call
from dts_util.installer.server_installer import DTSServerInstaller

@pytest.fixture
def mock_home_dir():
    """Create a temporary home directory for testing."""
    temp_dir = tempfile.mkdtemp()
    original_home = os.environ.get('HOME')
    os.environ['HOME'] = temp_dir
    yield Path(temp_dir)
    os.environ['HOME'] = original_home
    shutil.rmtree(temp_dir)

@pytest.fixture
def installer():
    """Create a fresh installer instance for each test."""
    return DTSServerInstaller()

@pytest.fixture
def mock_urlretrieve():
    """Mock urllib.request.urlretrieve to simulate downloading binary."""
    with patch('urllib.request.urlretrieve') as mock:
        def side_effect(url, path):
            # Create a dummy binary file
            with open(path, 'wb') as f:
                f.write(b'dummy binary content')
        mock.side_effect = side_effect
        yield mock

def test_default_port(installer):
    """Test that the default port is 7859."""
    assert installer.DEFAULT_PORT == 7859

def test_default_name(installer):
    """Test that DEFAULT_NAME property returns valid hostname."""
    name = installer.DEFAULT_NAME
    assert isinstance(name, str)
    assert len(name) > 0
    assert not name.endswith('.local')

def test_default_model_path(installer, mock_home_dir):
    """Test that the default model path is in the Draw Things container."""
    # Update the installer's default model path to use the mock home directory
    installer.default_model_path = Path(mock_home_dir) / "Library/Containers/com.liuliu.draw-things/Data/Documents/Models"
    expected_path = Path(mock_home_dir) / "Library/Containers/com.liuliu.draw-things/Data/Documents/Models"
    assert installer.default_model_path == expected_path

def test_validate_join_config_valid(installer):
    """Test join config validation with valid config."""
    valid_config = {
        "host": "proxy.example.com",
        "port": 7859,
        "servers": [
            {"address": "gpu1.local", "port": 7859, "priority": 1}
        ]
    }
    assert installer.validate_join_config(json.dumps(valid_config)) == True

def test_validate_join_config_invalid_missing_fields(installer):
    """Test join config validation with missing required fields."""
    invalid_config = {
        "host": "proxy.example.com"
        # missing port
    }
    with pytest.raises(ValueError, match="must include 'host' and 'port'"):
        installer.validate_join_config(json.dumps(invalid_config))

def test_validate_join_config_invalid_port(installer):
    """Test join config validation with invalid port."""
    invalid_config = {
        "host": "proxy.example.com",
        "port": -1
    }
    with pytest.raises(ValueError, match="Port must be positive"):
        installer.validate_join_config(json.dumps(invalid_config))

def test_validate_join_config_invalid_json(installer):
    """Test join config validation with invalid JSON."""
    with pytest.raises(ValueError, match="must be valid JSON"):
        installer.validate_join_config("not json")

def test_check_port_available(installer):
    """Test port availability check."""
    # Test with a likely-available high port number
    assert installer.check_port_available(65432) == True

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

def test_parse_args_defaults(installer, monkeypatch, mock_home_dir):
    """Test argument parsing with defaults."""
    # Create a models directory to avoid the input prompt
    models_dir = mock_home_dir / "Library/Containers/com.liuliu.draw-things/Data/Documents/Models"
    models_dir.mkdir(parents=True)

    monkeypatch.setattr('sys.argv', ['script.py'])
    args = installer.parse_args()
    assert args.port == installer.DEFAULT_PORT
    assert args.address == installer.DEFAULT_HOST
    assert args.gpu == installer.DEFAULT_GPU
    assert not args.quiet
    assert not args.uninstall
    assert not args.restart

def test_parse_args_custom(installer, monkeypatch, mock_home_dir):
    """Test argument parsing with custom values."""
    # Create a custom path to avoid the input prompt
    custom_path = mock_home_dir / "custom_models"
    custom_path.mkdir(parents=True)

    monkeypatch.setattr('sys.argv', [
        'script.py',
        '-p', '7860',
        '-a', '127.0.0.1',
        '-g', '1',
        '-q',
        '-m', str(custom_path)
    ])
    args = installer.parse_args()
    assert args.port == 7860
    assert args.address == '127.0.0.1'
    assert args.gpu == 1
    assert args.quiet
    assert args.model_path == str(custom_path)

def test_get_latest_release_url_success(installer):
    """Test getting latest release URL when GitHub API succeeds."""
    mock_response = [{"name": "v1.0.0"}]

    with patch('urllib.request.urlopen') as mock_urlopen:
        # Mock the context manager returned by urlopen
        mock_cm = MagicMock()
        mock_cm.read.return_value = json.dumps(mock_response).encode()
        mock_urlopen.return_value.__enter__.return_value = mock_cm

        url = installer.get_latest_release_url()
        assert url == f"https://github.com/drawthingsai/draw-things-community/releases/download/v1.0.0/{installer.BINARY_NAME}-macOS"

def test_get_latest_release_url_no_tags(installer):
    """Test getting latest release URL when GitHub API returns no tags."""
    with patch('urllib.request.urlopen') as mock_urlopen:
        mock_cm = MagicMock()
        mock_cm.read.return_value = json.dumps([]).encode()
        mock_urlopen.return_value.__enter__.return_value = mock_cm

        url = installer.get_latest_release_url()
        assert url == f"https://github.com/drawthingsai/draw-things-community/releases/download/{installer.FALLBACK_VERSION}/{installer.BINARY_NAME}-macOS"

def test_get_latest_release_url_network_error(installer):
    """Test getting latest release URL when GitHub API request fails."""
    with patch('urllib.request.urlopen') as mock_urlopen:
        mock_urlopen.side_effect = urllib.error.URLError("Network error")

        url = installer.get_latest_release_url()
        assert url == f"https://github.com/drawthingsai/draw-things-community/releases/download/{installer.FALLBACK_VERSION}/{installer.BINARY_NAME}-macOS"

def test_get_latest_release_url_invalid_json(installer):
    """Test getting latest release URL when GitHub API returns invalid JSON."""
    with patch('urllib.request.urlopen') as mock_urlopen:
        mock_cm = MagicMock()
        mock_cm.read.return_value = b"invalid json"
        mock_urlopen.return_value.__enter__.return_value = mock_cm

        url = installer.get_latest_release_url()
        assert url == f"https://github.com/drawthingsai/draw-things-community/releases/download/{installer.FALLBACK_VERSION}/{installer.BINARY_NAME}-macOS"

def test_download_grpcserver_preferred_dir(installer, mock_urlretrieve, monkeypatch, tmp_path):
    """Test downloading gRPCServerCLI to preferred directory."""
    # Mock PREFERRED_BIN_DIR to use a temp directory
    preferred_dir = tmp_path / 'usr' / 'local' / 'bin'
    monkeypatch.setattr(installer, 'PREFERRED_BIN_DIR', preferred_dir)

    # Mock get_latest_release_url
    monkeypatch.setattr(installer, 'get_latest_release_url',
                       lambda: 'https://example.com/gRPCServerCLI-macOS')

    binary_path = installer.download_grpcserver()

    assert binary_path == preferred_dir / installer.BINARY_NAME
    assert binary_path.exists()
    assert os.access(binary_path, os.X_OK)  # Check executable permission

def test_download_grpcserver_local_dir(installer, mock_urlretrieve, monkeypatch, tmp_path):
    """Test downloading gRPCServerCLI to local directory when preferred is not writable."""
    # Mock directories
    preferred_dir = tmp_path / 'usr' / 'local' / 'bin'
    local_dir = tmp_path / 'home' / '.local' / 'bin'
    monkeypatch.setattr(installer, 'PREFERRED_BIN_DIR', preferred_dir)
    monkeypatch.setattr(installer, 'LOCAL_BIN_DIR', local_dir)

    # Make preferred dir read-only
    preferred_dir.mkdir(parents=True)
    os.chmod(preferred_dir, 0o555)

    # Mock get_latest_release_url
    monkeypatch.setattr(installer, 'get_latest_release_url',
                       lambda: 'https://example.com/gRPCServerCLI-macOS')

    # Mock input for PATH question
    monkeypatch.setattr('builtins.input', lambda _: 'n')

    binary_path = installer.download_grpcserver()

    assert binary_path == local_dir / installer.BINARY_NAME
    assert binary_path.exists()
    assert os.access(binary_path, os.X_OK)  # Check executable permission

def test_download_grpcserver_download_error(installer, monkeypatch):
    """Test handling of download errors."""
    # Mock urlretrieve to raise an error
    def mock_urlretrieve(*args):
        raise urllib.error.URLError("Failed to download")
    monkeypatch.setattr('urllib.request.urlretrieve', mock_urlretrieve)

    # Mock get_latest_release_url
    monkeypatch.setattr(installer, 'get_latest_release_url',
                       lambda: 'https://example.com/gRPCServerCLI-macOS')

    with pytest.raises(SystemExit) as exc_info:
        installer.download_grpcserver()
    assert exc_info.value.code == 1

def test_download_grpcserver_existing_binary(installer, mock_urlretrieve, monkeypatch, tmp_path):
    """Test handling of existing binary file."""
    # Mock directories and files
    preferred_dir = tmp_path / 'usr' / 'local' / 'bin'
    preferred_dir.mkdir(parents=True)
    binary_path = preferred_dir / installer.BINARY_NAME
    binary_path.write_bytes(b'existing binary')

    monkeypatch.setattr(installer, 'PREFERRED_BIN_DIR', preferred_dir)
    monkeypatch.setattr(installer, 'get_latest_release_url',
                       lambda: 'https://example.com/gRPCServerCLI-macOS')

    # Test overwrite confirmation
    monkeypatch.setattr('builtins.input', lambda _: 'y')

    # Mock service path
    service_path = tmp_path / 'LaunchAgents' / f'{installer.SERVICE_NAME}.plist'
    monkeypatch.setattr(installer, 'AGENTS_DIR', service_path.parent)

    new_binary_path = installer.download_grpcserver()

    assert new_binary_path == binary_path
    assert new_binary_path.exists()
    assert os.access(new_binary_path, os.X_OK)  # Check executable permission

def test_create_launchd_service_new(installer, monkeypatch, tmp_path):
    """Test creating a new launchd service."""
    # Mock directories
    agents_dir = tmp_path / "Library/LaunchAgents"
    agents_dir.mkdir(parents=True)
    monkeypatch.setattr(installer, 'AGENTS_DIR', agents_dir)

    # Mock binary path and model path
    binary_path = tmp_path / "usr/local/bin/gRPCServerCLI"
    installer.model_path = tmp_path / "Models"

    # Set some server args
    installer.server_args = {
        'name': 'test-server',
        'port': 7859,
        'address': '0.0.0.0',
        'gpu': 0,
        'datadog_api_key': None,
        'shared_secret': 'secret123',
        'no_tls': False,
        'no_response_compression': False,
        'model_browser': True,
        'no_flash_attention': False,
        'debug': True,
        'join': None
    }

    # Mock subprocess calls
    mock_subprocess = MagicMock()
    monkeypatch.setattr('subprocess.run', mock_subprocess)

    installer.create_launchd_service(binary_path)

    # Check plist file was created
    service_path = agents_dir / f'{installer.SERVICE_NAME}.plist'
    assert service_path.exists()

    # Verify plist content
    with open(service_path, 'rb') as f:
        plist = plistlib.load(f)
        assert plist['Label'] == installer.SERVICE_NAME
        assert plist['RunAtLoad'] is True
        assert plist['KeepAlive'] is True

        # Check command arguments
        cmd_args = plist['ProgramArguments']
        assert cmd_args[0] == str(binary_path)
        assert cmd_args[1] == str(installer.model_path)
        assert '--name' in cmd_args and cmd_args[cmd_args.index('--name') + 1] == 'test-server'
        assert '--shared-secret' in cmd_args and cmd_args[cmd_args.index('--shared-secret') + 1] == 'secret123'
        assert '--model-browser' in cmd_args
        assert '--debug' in cmd_args

    # Verify launchctl was called
    mock_subprocess.assert_called_once_with(['launchctl', 'load', service_path], check=True)

def test_create_launchd_service_existing(installer, monkeypatch, tmp_path):
    """Test updating an existing launchd service."""
    # Mock directories and create existing service
    agents_dir = tmp_path / "Library/LaunchAgents"
    agents_dir.mkdir(parents=True)
    service_path = agents_dir / f'{installer.SERVICE_NAME}.plist'
    service_path.write_bytes(b'existing service')
    monkeypatch.setattr(installer, 'AGENTS_DIR', agents_dir)

    # Mock binary path and model path
    binary_path = tmp_path / "usr/local/bin/gRPCServerCLI"
    installer.model_path = tmp_path / "Models"
    installer.server_args = {
        'name': 'test-server',
        'port': 7859,
        'address': '0.0.0.0',
        'gpu': 0,
        'datadog_api_key': None,
        'shared_secret': None,
        'no_tls': False,
        'no_response_compression': False,
        'model_browser': False,
        'no_flash_attention': False,
        'debug': False,
        'join': None
    }

    # Mock user input to confirm update
    monkeypatch.setattr('builtins.input', lambda _: 'y')

    # Mock subprocess calls
    mock_subprocess = MagicMock()
    monkeypatch.setattr('subprocess.run', mock_subprocess)

    installer.create_launchd_service(binary_path)

    # Verify service was unloaded and reloaded
    assert mock_subprocess.call_args_list == [
        call(['launchctl', 'unload', service_path], check=False),
        call(['launchctl', 'remove', installer.SERVICE_NAME], check=False),
        call(['launchctl', 'load', service_path], check=True)
    ]

def test_create_launchd_service_existing_no_update(installer, monkeypatch, tmp_path):
    """Test skipping update of existing service when user declines."""
    # Mock directories and create existing service
    agents_dir = tmp_path / "Library/LaunchAgents"
    agents_dir.mkdir(parents=True)
    service_path = agents_dir / f'{installer.SERVICE_NAME}.plist'
    original_content = b'existing service'
    service_path.write_bytes(original_content)
    monkeypatch.setattr(installer, 'AGENTS_DIR', agents_dir)

    # Mock binary path
    binary_path = tmp_path / "usr/local/bin/gRPCServerCLI"

    # Mock user input to decline update
    monkeypatch.setattr('builtins.input', lambda _: 'n')

    # Mock subprocess calls
    mock_subprocess = MagicMock()
    monkeypatch.setattr('subprocess.run', mock_subprocess)

    installer.create_launchd_service(binary_path)

    # Verify service file wasn't changed
    assert service_path.read_bytes() == original_content

    # Verify no launchctl calls were made
    mock_subprocess.assert_not_called()

def test_create_launchd_service_error(installer, monkeypatch, tmp_path):
    """Test handling of launchctl errors."""
    # Mock directories
    agents_dir = tmp_path / "Library/LaunchAgents"
    agents_dir.mkdir(parents=True)
    monkeypatch.setattr(installer, 'AGENTS_DIR', agents_dir)

    # Mock binary path and model path
    binary_path = tmp_path / "usr/local/bin/gRPCServerCLI"
    installer.model_path = tmp_path / "Models"
    installer.server_args = {
        'name': 'test-server',
        'port': 7859,
        'address': '0.0.0.0',
        'gpu': 0,
        'datadog_api_key': None,
        'shared_secret': None,
        'no_tls': False,
        'no_response_compression': False,
        'model_browser': False,
        'no_flash_attention': False,
        'debug': False,
        'join': None
    }

    # Mock subprocess to raise error
    def mock_run(*args, **kwargs):
        raise subprocess.CalledProcessError(1, args[0])
    monkeypatch.setattr('subprocess.run', mock_run)

    with pytest.raises(SystemExit) as exc_info:
        installer.create_launchd_service(binary_path)
    assert exc_info.value.code == 1

def test_server_running_success(installer, monkeypatch):
    """Test server running check when server is running properly."""
    # Set server args
    installer.server_args = {'port': 7859}

    # Mock pgrep to return a PID
    def mock_run(*args, **kwargs):
        if args[0][0] == 'pgrep':
            return MagicMock(stdout='12345\n', returncode=0)
        elif args[0][0] == 'lsof':
            return MagicMock(
                stdout='gRPCServerCLI 12345 user   TCP *:7859 (LISTEN)\n',
                returncode=0
            )
        return MagicMock(returncode=0)
    monkeypatch.setattr('subprocess.run', mock_run)

    assert installer.test_server_running() is True

def test_server_running_no_process(installer, monkeypatch):
    """Test server running check when process is not found."""
    # Set server args
    installer.server_args = {'port': 7859}

    # Mock pgrep to return no PID
    def mock_run(*args, **kwargs):
        if args[0][0] == 'pgrep':
            return MagicMock(stdout='', returncode=1)
        return MagicMock(returncode=1)
    monkeypatch.setattr('subprocess.run', mock_run)

    assert installer.test_server_running() is False

def test_server_running_port_check_fallback(installer, monkeypatch):
    """Test server running check falls back to direct port check when lsof fails."""
    # Set server args
    installer.server_args = {'port': 7859}

    # Mock pgrep to return a PID but lsof to fail
    def mock_run(*args, **kwargs):
        if args[0][0] == 'pgrep':
            return MagicMock(stdout='12345\n', returncode=0)
        elif args[0][0] == 'lsof':
            return MagicMock(returncode=1)
        return MagicMock(returncode=0)
    monkeypatch.setattr('subprocess.run', mock_run)

    # Mock socket connection success
    mock_socket = MagicMock()
    monkeypatch.setattr('socket.socket', lambda *args: mock_socket)

    assert installer.test_server_running() is True
    mock_socket.connect.assert_called_once_with(('localhost', 7859))

def test_server_running_port_not_listening(installer, monkeypatch):
    """Test server running check when port is not accepting connections."""
    # Set server args
    installer.server_args = {'port': 7859}

    # Mock pgrep to return a PID but lsof to fail
    def mock_run(*args, **kwargs):
        if args[0][0] == 'pgrep':
            return MagicMock(stdout='12345\n', returncode=0)
        elif args[0][0] == 'lsof':
            return MagicMock(returncode=1)
        return MagicMock(returncode=0)
    monkeypatch.setattr('subprocess.run', mock_run)

    # Mock socket connection failure
    mock_socket = MagicMock()
    mock_socket.connect.side_effect = ConnectionRefusedError()
    monkeypatch.setattr('socket.socket', lambda *args: mock_socket)

    assert installer.test_server_running() is False

def test_server_running_command_error(installer, monkeypatch):
    """Test server running check when commands fail."""
    # Set server args
    installer.server_args = {'port': 7859}

    # Mock commands to raise exceptions
    def mock_run(*args, **kwargs):
        raise subprocess.CalledProcessError(1, args[0])
    monkeypatch.setattr('subprocess.run', mock_run)

    # Mock socket to also fail
    mock_socket = MagicMock()
    mock_socket.connect.side_effect = socket.error()
    monkeypatch.setattr('socket.socket', lambda *args: mock_socket)

    assert installer.test_server_running() is False