#!/usr/bin/env python3
"""Tests for the Draw Things gRPCServer installer."""
import os
import socket
import unittest
import sys
import importlib.util
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import the installer script by path since it has a hyphen in the name
SCRIPT_PATH = Path(__file__).parent.parent / 'src' / 'install-gRPCServerCLI.py'
spec = importlib.util.spec_from_file_location("installer", SCRIPT_PATH)
installer_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer_module)

class TestDrawThingsInstaller(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test."""
        # Set up HOME before creating installer
        self.orig_home = os.environ.get('HOME')
        self.temp_home = Path('/tmp/test_home')
        self.temp_home.mkdir(parents=True, exist_ok=True)
        os.environ['HOME'] = str(self.temp_home)

        # Now create installer with modified HOME
        self.installer = installer_module.DrawThingsInstaller()

    def tearDown(self):
        """Clean up after each test."""
        # Restore original HOME
        if self.orig_home:
            os.environ['HOME'] = self.orig_home
        else:
            del os.environ['HOME']

        # Clean up temp directory
        if self.temp_home.exists():
            import shutil
            shutil.rmtree(self.temp_home)

    def test_default_port(self):
        """Test that the default port is 7859."""
        self.assertEqual(self.installer.DEFAULT_PORT, 7859)

    def test_default_name(self):
        """Test that the default name is derived from hostname."""
        hostname = socket.gethostname()
        # Remove .local suffix if present
        if hostname.endswith('.local'):
            hostname = hostname[:-6]
        self.assertEqual(self.installer.DEFAULT_NAME, hostname)

    def test_default_model_path(self):
        """Test that the default model path is in the Draw Things container."""
        expected_path = Path(self.temp_home) / "Library/Containers/com.liuliu.draw-things/Data/Documents/Models"
        self.assertEqual(self.installer.default_model_path, expected_path)

    def test_validate_join_config(self):
        """Test join configuration validation."""
        # Test valid configurations
        valid_configs = [
            '{"host": "proxy.local", "port": 7859}',
            '{"host": "proxy.local", "port": 7859, "servers": [{"address": "gpu1.local", "port": 7859, "priority": 1}]}'
        ]
        for config in valid_configs:
            with self.subTest(config=config):
                self.assertTrue(self.installer.validate_join_config(config))

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
            with self.subTest(config=config):
                with self.assertRaises(ValueError):
                    self.installer.validate_join_config(config)

    @patch('socket.socket')
    def test_check_port_available(self, mock_socket_class):
        """Test port availability checking."""
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket

        # Test port is available
        mock_socket.connect_ex.return_value = 1
        self.assertTrue(self.installer.check_port_available(7859))

        # Test port is in use
        mock_socket.connect_ex.return_value = 0
        self.assertFalse(self.installer.check_port_available(7859))

    @patch('subprocess.run')
    def test_restart_service(self, mock_run):
        """Test service restart functionality."""
        # Create service file using temp home directory
        service_path = Path(self.temp_home) / "Library/LaunchAgents" / f'{self.installer.SERVICE_NAME}.plist'
        service_path.parent.mkdir(parents=True, exist_ok=True)
        service_path.touch()

        # Update installer's AGENTS_DIR to use temp home
        self.installer.AGENTS_DIR = Path(self.temp_home) / "Library/LaunchAgents"

        self.installer.restart_service()

        # Verify unload and load commands were called
        self.assertEqual(mock_run.call_count, 2)
        unload_call, load_call = mock_run.call_args_list

        # Compare string representations of paths
        expected_unload = ['launchctl', 'unload', str(service_path)]
        expected_load = ['launchctl', 'load', str(service_path)]

        actual_unload = [str(arg) if isinstance(arg, Path) else arg for arg in unload_call[0][0]]
        actual_load = [str(arg) if isinstance(arg, Path) else arg for arg in load_call[0][0]]

        self.assertEqual(actual_unload, expected_unload)
        self.assertEqual(actual_load, expected_load)

    @patch('subprocess.run')
    def test_restart_service_not_installed(self, mock_run):
        """Test service restart when service is not installed."""
        # Update installer's AGENTS_DIR to use temp home
        self.installer.AGENTS_DIR = Path(self.temp_home) / "Library/LaunchAgents"

        # Don't create the service file - this should trigger the error
        with self.assertRaises(SystemExit) as cm:
            self.installer.restart_service()

        self.assertEqual(cm.exception.code, 1)  # Verify exit code is 1
        mock_run.assert_not_called()

    def test_prompt_user_quiet_mode(self):
        """Test user prompts in quiet mode."""
        self.installer.quiet = True

        # Test with default 'n'
        self.assertFalse(self.installer.prompt_user("Continue?"))

        # Test with default 'y'
        self.assertTrue(self.installer.prompt_user("Continue?", default='y'))

    @patch('builtins.input')
    def test_prompt_user_interactive(self, mock_input):
        """Test user prompts in interactive mode."""
        self.installer.quiet = False

        # Test 'y' response
        mock_input.return_value = 'y'
        self.assertTrue(self.installer.prompt_user("Continue?"))

        # Test 'n' response
        mock_input.return_value = 'n'
        self.assertFalse(self.installer.prompt_user("Continue?"))

        # Test empty input (uses default)
        mock_input.return_value = ''
        self.assertTrue(self.installer.prompt_user("Continue?", default='y'))
        self.assertFalse(self.installer.prompt_user("Continue?", default='n'))

if __name__ == '__main__':
    unittest.main()