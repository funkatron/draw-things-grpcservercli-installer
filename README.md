# Draw Things gRPCServer Installer

A Python script to install and manage the Draw Things Community gRPCServer on macOS. This installer handles downloading the latest gRPCServer binary, setting up a LaunchAgent service, and managing the server configuration.

## Requirements

- macOS 15
- Python 3.9+

## Installation

1. Download the installer script:
```bash
git clone https://github.com/funkatron/draw-things-grpcservercli-installer.git
```

## Usage

```bash
# Basic installation with defaults
./install-grpcservercli.py

# Install with custom model path
./install-grpcservercli.py -m /path/to/models

# Install with custom port and server name
./install-grpcservercli.py -p 7860 -n "MyServer"

# Install with security options
./install-grpcservercli.py -s "mysecret"

# Install with model browser enabled
./install-grpcservercli.py --model-browser

# Install with proxy configuration
./install-grpcservercli.py --join '{"host":"proxy.local", "port":7859}'

# Restart the service
./install-grpcservercli.py --restart

# Quiet install with defaults
./install-grpcservercli.py -q

# Uninstall
./install-grpcservercli.py --uninstall
```

## Options

### Installer Options
- `-m, --model-path`: Custom path to store models (default: Draw Things app models directory)
- `-h, --help`: Show help message
- `--uninstall`: Uninstall gRPCServerCLI and remove all related files
- `--restart`: Restart the gRPCServerCLI service
- `-q, --quiet`: Minimize output and assume default answers to prompts

### gRPCServerCLI Options
- `-n, --name`: Server name in local network (default: machine name)
- `-p, --port`: Port to run the server on (default: 7859)
- `-a, --address`: Address to bind to (default: 0.0.0.0)
- `-g, --gpu`: GPU index to use (default: 0)
- `-d, --datadog-api-key`: Datadog API key for logging backend
- `-s, --shared-secret`: Shared secret for server security
- `--no-tls`: Disable TLS for connections (not recommended)
- `--no-response-compression`: Disable response compression
- `--model-browser`: Enable model browsing
- `--no-flash-attention`: Disable Flash Attention
- `--debug`: Enable verbose model inference logging
- `--join`: JSON configuration for proxy setup

## Advanced Configuration

### Proxy Setup
The `--join` option accepts a JSON string for proxy configuration:
```json
{
  "host": "proxy.example.com",
  "port": 7859,
  "servers": [
    {
      "address": "gpu1.local",
      "port": 7859,
      "priority": 1
    }
  ]
}
```

Required fields:
- `host`: The proxy server hostname
- `port`: The proxy server port

Optional fields:
- `servers`: List of GPU servers with:
  - `address`: Server hostname
  - `port`: Server port
  - `priority`: Server priority (1=high, 2=low)

## Service Management

The installer creates a LaunchAgent service that:
- Starts automatically on login
- Restarts automatically if it crashes
- Can be managed with:
  ```bash
  # Stop the service
  launchctl unload ~/Library/LaunchAgents/com.drawthings.grpcserver.plist

  # Start the service
  launchctl load ~/Library/LaunchAgents/com.drawthings.grpcserver.plist

  # Restart the service
  ./install-grpcservercli.py --restart
  ```

## Troubleshooting

1. **Port already in use**
   - The installer will detect if the port is in use and show which process is using it
   - Use a different port with `-p` or stop the conflicting process

2. **Permission denied when installing to /usr/local/bin**
   - The installer will automatically fall back to ~/.local/bin
   - You can run with sudo if you need to install in /usr/local/bin

3. **Service fails to start**
   - Check the system log for errors: `log show --predicate 'processImagePath contains "gRPCServerCLI"' --last 5m`
   - Ensure the model path exists and is accessible
   - Try restarting with `--restart` option

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Draw Things](https://drawthings.ai/)
- [Draw Things Community](https://github.com/drawthingsai/draw-things-community)