#!/usr/bin/env python3

import argparse
import os
import subprocess
import sys
from pathlib import Path
import shutil
import tempfile
import urllib.request
import plistlib
import time
import socket
from subprocess import PIPE
import json

class DrawThingsInstaller:
    # Default server settings
    DEFAULT_PORT = 7859
    DEFAULT_HOST = '0.0.0.0'
    DEFAULT_GPU = 0  # Default GPU index

    @property
    def DEFAULT_NAME(self):
        """Get cleaned up hostname for server name"""
        hostname = socket.gethostname()
        # Remove .local suffix if present
        if hostname.endswith('.local'):
            hostname = hostname[:-6]
        # Convert to ASCII if possible, otherwise keep Unicode
        try:
            return hostname.encode('ascii').decode('ascii')
        except UnicodeEncodeError:
            return hostname

    # File and directory names
    BINARY_NAME = "gRPCServerCLI"
    SERVICE_NAME = "com.drawthings.grpcserver"

    # System paths
    PREFERRED_BIN_DIR = Path('/usr/local/bin')
    LOCAL_BIN_DIR = Path.home() / '.local/bin'
    AGENTS_DIR = Path.home() / "Library/LaunchAgents"

    # GitHub API
    GITHUB_API_URL = "https://api.github.com/repos/drawthingsai/draw-things-community/tags"
    FALLBACK_VERSION = "v1.20250225.0"

    def __init__(self):
        self.default_model_path = Path.home() / "Library/Containers/com.liuliu.draw-things/Data/Documents/Models"
        self.model_path = None
        self.server_args = None
        self.quiet = False
        self.usage_text = f"""
Draw Things gRPCServerCLI Installer

This script installs the Draw Things gRPCServerCLI and sets it up as a LaunchAgent service.

Usage:
    ./install-grpcservercli.py [-m MODEL_PATH] [gRPCServerCLI options]
    ./install-grpcservercli.py --uninstall
    ./install-grpcservercli.py --restart

The installer will:
1. Download the gRPCServerCLI binary
2. Install it to {self.PREFERRED_BIN_DIR} (or {self.LOCAL_BIN_DIR} if {self.PREFERRED_BIN_DIR} is not writable)
3. Create and start a LaunchAgent service

Installer Options:
    -m, --model-path         Custom path to store models (default: Draw Things app models directory)
    -h, --help              Show this help message
    --uninstall            Uninstall gRPCServerCLI and remove all related files
    --restart             Restart the gRPCServerCLI service
    -q, --quiet            Minimize output and assume default answers to prompts

gRPCServerCLI Options:
    -n, --name             Server name in local network (default: machine name)
    -p, --port             Port to run the server on (default: {self.DEFAULT_PORT})
    -a, --address          Address to bind to (default: {self.DEFAULT_HOST})
    -g, --gpu              GPU index to use (default: {self.DEFAULT_GPU})
    -d, --datadog-api-key  Datadog API key for logging backend
    -s, --shared-secret    Shared secret for server security
    --no-tls               Disable TLS for connections (not recommended)
    --no-response-compression  Disable response compression
    --model-browser        Enable model browsing
    --no-flash-attention   Disable Flash Attention
    --debug                Enable verbose model inference logging
    --join                 JSON configuration for proxy setup (see below)

Advanced Options:
    The --join option accepts a JSON string for proxy configuration:
    Example: --join '{{"host":"proxy.example.com", "port":7859, "servers":[{{"address":"gpu1.local", "port":7859, "priority": 1}}]}}'

    Required fields for --join:
    - host: The proxy server hostname
    - port: The proxy server port
    Optional fields:
    - servers: List of GPU servers with required fields:
      - address: Server hostname
      - port: Server port
      - priority: Server priority (1=high, 2=low)

Examples:
    # Install using default settings
    ./install-grpcservercli.py

    # Install with custom model path
    ./install-grpcservercli.py -m /path/to/models

    # Install with custom port and server name
    ./install-grpcservercli.py -p 7860 -n "MyServer"

    # Install with security options (recommended for public networks)
    ./install-grpcservercli.py -s "mysecret"

    # Install with model browser enabled
    ./install-grpcservercli.py --model-browser

    # Install with proxy configuration
    ./install-grpcservercli.py --join '{{"host":"proxy.local", "port":7859}}'

    # Restart the service
    ./install-grpcservercli.py --restart

    # Quiet install with defaults
    ./install-grpcservercli.py -q
"""

    def parse_args(self):
        parser = argparse.ArgumentParser(
            description='Install Draw Things gRPCServerCLI',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=self.usage_text)

        # Add uninstall and restart actions
        group = parser.add_mutually_exclusive_group()
        group.add_argument('--uninstall', action='store_true',
                          help='Uninstall gRPCServerCLI and remove all related files')
        group.add_argument('--restart', action='store_true',
                          help='Restart the gRPCServerCLI service')

        # Installer arguments
        parser.add_argument('-m', '--model-path',
                          default=os.environ.get('DRAW_THINGS_MODEL_PATH', None),
                          help='Model directory path')
        parser.add_argument('-q', '--quiet', action='store_true',
                          help='Minimize output and assume default answers to prompts')

        # gRPCServerCLI arguments
        parser.add_argument('-n', '--name', default=None,
                          help=f'Server name in local network (default: machine name)')
        parser.add_argument('-p', '--port', type=int, default=self.DEFAULT_PORT,
                          help=f'Port to run the server on (default: {self.DEFAULT_PORT})')
        parser.add_argument('-a', '--address', default=self.DEFAULT_HOST,
                          help=f'Address to bind to (default: {self.DEFAULT_HOST})')
        parser.add_argument('-g', '--gpu', type=int, default=self.DEFAULT_GPU,
                          help=f'GPU index to use (default: {self.DEFAULT_GPU})')
        parser.add_argument('-d', '--datadog-api-key',
                          help='Datadog API key for logging backend')
        parser.add_argument('-s', '--shared-secret',
                          help='Shared secret for server security')
        parser.add_argument('--no-tls', action='store_true',
                          help='Disable TLS for connections')
        parser.add_argument('--no-response-compression', action='store_true',
                          help='Disable response compression')
        parser.add_argument('--model-browser', action='store_true',
                          help='Enable model browsing')
        parser.add_argument('--no-flash-attention', action='store_true',
                          help='Disable Flash Attention')
        parser.add_argument('--debug', action='store_true',
                          help='Enable verbose model inference logging')
        parser.add_argument('--join',
                          help='JSON configuration for proxy setup')

        args = parser.parse_args()

        # Handle restart
        if args.restart:
            self.restart_service()
            sys.exit(0)

        # Handle uninstall
        if args.uninstall:
            self.uninstall()
            sys.exit(0)

        self.quiet = args.quiet
        self.model_path = Path(args.model_path) if args.model_path else self.get_default_model_path()

        # Validate join configuration if provided
        if args.join:
            try:
                join_config = json.loads(args.join)
                required_fields = ['host', 'port']
                if not all(field in join_config for field in required_fields):
                    print("Error: --join configuration must include 'host' and 'port'")
                    sys.exit(1)
                if 'servers' in join_config:
                    for server in join_config['servers']:
                        if not all(field in server for field in ['address', 'port']):
                            print("Error: Each server in --join must have 'address' and 'port'")
                            sys.exit(1)
            except json.JSONDecodeError:
                print("Error: --join value must be valid JSON")
                sys.exit(1)

        # Security warning for no-tls
        if args.no_tls:
            if not self.quiet:
                print("\nWARNING: --no-tls disables encryption. Use only in trusted networks!")
                response = input("Are you sure you want to continue? (y/N): ")
                if response.lower() != 'y':
                    print("Installation cancelled.")
                    sys.exit(0)

        self.server_args = {
            'name': args.name if args.name is not None else self.DEFAULT_NAME,
            'port': args.port,
            'address': args.address,
            'gpu': args.gpu,
            'datadog_api_key': args.datadog_api_key,
            'shared_secret': args.shared_secret,
            'no_tls': args.no_tls,
            'no_response_compression': args.no_response_compression,
            'model_browser': args.model_browser,
            'no_flash_attention': args.no_flash_attention,
            'debug': args.debug,
            'join': args.join
        }

    def get_default_model_path(self):
        """Return the default model path if it exists, otherwise prompt user"""
        if self.default_model_path.exists():
            return self.default_model_path

        print(f"Default model path not found: {self.default_model_path}")
        print("\nUsage tip: You can specify a custom model path with:")
        print(f"    {sys.argv[0]} -m /path/to/models\n")

        while True:
            path = input("Please enter path for models (or 'h' for help, 'q' to quit): ")
            if path.lower() == 'q':
                sys.exit(0)
            if path.lower() == 'h':
                print(self.usage_text)
                continue
            if Path(path).exists():
                return Path(path)
            print("Path does not exist. Please try again.")

    def validate_join_config(self, config_str):
        """Validate join configuration string"""
        try:
            config = json.loads(config_str)
            if not isinstance(config, dict):
                raise ValueError("Join configuration must be a JSON object")

            # Check required fields
            if not all(field in config for field in ['host', 'port']):
                raise ValueError("Join configuration must include 'host' and 'port'")

            # Validate host
            if not isinstance(config['host'], str) or not config['host']:
                raise ValueError("Host must be a non-empty string")

            # Validate port
            if not isinstance(config['port'], int) or config['port'] < 1:
                raise ValueError("Port must be a positive integer")

            # Validate servers if present
            if 'servers' in config:
                if not isinstance(config['servers'], list):
                    raise ValueError("Servers must be a list")
                for server in config['servers']:
                    if not isinstance(server, dict):
                        raise ValueError("Each server must be an object")
                    if not all(field in server for field in ['address', 'port']):
                        raise ValueError("Each server must have 'address' and 'port'")
                    if not isinstance(server['address'], str) or not server['address']:
                        raise ValueError("Server address must be a non-empty string")
                    if not isinstance(server['port'], int) or server['port'] < 1:
                        raise ValueError("Server port must be a positive integer")

            return True
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format")

    def check_port_available(self, port):
        """Check if a port is available"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        try:
            result = sock.connect_ex(('localhost', port))
            return result != 0
        finally:
            sock.close()

    def restart_service(self):
        """Restart the gRPCServerCLI service"""
        print("Restarting gRPCServerCLI service...")
        service_path = self.AGENTS_DIR / f'{self.SERVICE_NAME}.plist'
        if not service_path.exists():
            print("Error: Service not installed")
            sys.exit(1)

        try:
            subprocess.run(['launchctl', 'unload', service_path], check=True)
            time.sleep(1)  # Give the service time to stop
            subprocess.run(['launchctl', 'load', service_path], check=True)
            print("Service restarted successfully")
        except subprocess.CalledProcessError as e:
            print(f"Failed to restart service: {e}")
            sys.exit(1)

    def prompt_user(self, message, default='n'):
        """Handle user prompts with quiet mode support"""
        if self.quiet:
            return default.lower() == 'y'
        response = input(message)
        return response.lower() == 'y' if response else default.lower() == 'y'

    def install(self):
        """Run the installation process"""
        try:
            self.parse_args()

            # Validate port availability
            if not self.check_port_available(self.server_args['port']):
                print(f"\nError: Port {self.server_args['port']} is already in use!")
                try:
                    lsof = subprocess.run(['lsof', '-i', f":{self.server_args['port']}"],
                                       stdout=PIPE, text=True, check=True)
                    print("\nProcess using the port:")
                    print(lsof.stdout)
                except subprocess.CalledProcessError:
                    pass
                sys.exit(1)

            # Check for existing services before proceeding
            self.check_existing_service()

            binary_path = self.download_grpcserver()
            self.create_launchd_service(binary_path)

            # Wait a moment for the service to start
            print("\nWaiting for service to start...")
            time.sleep(2)

            # Test if server is running
            if self.test_server_running():
                print("\nInstallation completed successfully!")
                print(f"Models directory: {self.model_path}")
                print(f"Binary location: {binary_path}")
                print("\nThe gRPCServerCLI service is running and will start automatically on login.")
                print("You can manage it with these commands:")
                print(f"    launchctl unload ~/Library/LaunchAgents/{self.SERVICE_NAME}.plist")
                print(f"    launchctl load ~/Library/LaunchAgents/{self.SERVICE_NAME}.plist")
            else:
                print("\nWARNING: Installation completed but server may not be running correctly.")
                print("Try these troubleshooting steps:")
                print("1. Check the system log for errors:")
                print("    log show --predicate 'process == \"gRPCServerCLI\"' --last 5m")
                print("2. Restart the service:")
                print(f"    launchctl unload ~/Library/LaunchAgents/{self.SERVICE_NAME}.plist")
                print(f"    launchctl load ~/Library/LaunchAgents/{self.SERVICE_NAME}.plist")
                print("3. Check if the models directory is accessible:")
                print(f"    ls {self.model_path}")
        except Exception as e:
            print(f"Installation failed: {e}")
            print("\nFor usage information, run:")
            print(f"    {sys.argv[0]} --help")
            sys.exit(1)

    def uninstall(self):
        """Remove gRPCServerCLI, service files, and clean up"""
        print("Uninstalling gRPCServerCLI...")

        # Stop and remove LaunchAgent
        service_path = self.AGENTS_DIR / f'{self.SERVICE_NAME}.plist'
        if service_path.exists():
            try:
                print("Stopping and removing service...")
                subprocess.run(['launchctl', 'unload', service_path], check=False)
                subprocess.run(['launchctl', 'remove', self.SERVICE_NAME], check=False)
                service_path.unlink()
            except Exception as e:
                print(f"Warning: Failed to fully remove service: {e}")

        # Stop any running gRPCServer processes
        try:
            subprocess.run(['pkill', '-f', 'gRPCServer'], check=False)
            time.sleep(1)  # Give processes time to stop
        except Exception as e:
            print(f"Warning: Failed to stop processes: {e}")

        # Remove binary from potential locations
        binary_paths = [
            self.PREFERRED_BIN_DIR / self.BINARY_NAME,
            self.LOCAL_BIN_DIR / self.BINARY_NAME
        ]

        for binary_path in binary_paths:
            if binary_path.exists():
                try:
                    print(f"Removing binary from {binary_path}...")
                    binary_path.unlink()
                except Exception as e:
                    print(f"Warning: Failed to remove binary at {binary_path}: {e}")

        # Check if the port is still in use
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', self.DEFAULT_PORT))
            sock.close()

            if result == 0:
                print(f"\nWARNING: Port {self.DEFAULT_PORT} is still in use!")
                print("You may need to restart your computer or check for other services using this port.")
        except Exception:
            pass

        print("\nUninstall complete!")
        print("Note: Model directory was not removed.")

if __name__ == "__main__":
    installer = DrawThingsInstaller()
    installer.install()