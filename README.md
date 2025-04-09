# Draw Things gRPCServer CLI Installer

A Python-based installer and manager for the Draw Things Community gRPCServer on macOS. This tool manages the installation and configuration of the gRPCServer binary, enabling distributed AI image generation.

## Features

- 🚀 One-command installation of gRPCServer binary
- 🔄 Automatic service management via LaunchAgent (startup, crash recovery)
- ⚙️ Command-line configuration of all gRPCServer options
- 🔧 Easy service management (start/stop/restart)

## Requirements

- macOS 15 or later
- Python 3.9 or later
- Python packages (auto-installed):
  - grpcio ≥ 1.54.2
  - grpcio-reflection ≥ 1.54.2
  - grpcio-tools ≥ 1.54.2
  - protobuf ≥ 4.23.1
  - pytest ≥ 7.0.0 (for development)

## Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/funkatron/draw-things-grpcservercli-installer.git
   cd draw-things-grpcservercli-installer
   ```

2. Install with default settings:
   ```bash
   ./src/grpc_server_installer.py
   ```

### Example Installation Output

```
~/src/draw-things-grpcservercli-installer on main ● λ python3 ./src/grpc_server_installer.py
Checking for existing services...

Found running gRPC processes:
  - 45475 /Users/<username>/bin/gRPCServerCLI-macOS /Users/<username>/Library/Containers/com.liuliu.draw-things/Data/Documents/Models --model-browser --port=7590

Found existing Draw Things gRPC installation!
It's recommended to uninstall before proceeding.
Would you like to uninstall now? (Y/n): y
Uninstalling gRPCServerCLI...

Uninstall complete!
Note: Model directory was not removed.

Continuing with fresh installation...


Downloading gRPCServerCLI...
Checking for latest release...
Found latest version: v1.20250403.2
Cannot write to /usr/local/bin, using /Users/<username>/.local/bin instead
Service installed and started at /Users/<username>/Library/LaunchAgents/com.drawthings.grpcserver.plist
Server configuration:

Waiting for service to start...

Testing gRPCServerCLI...
Found gRPCServerCLI process (PID: 44328)
Server is listening on port 7859

Installation completed successfully!
Models directory: /Users/<username>/Library/Containers/com.liuliu.draw-things/Data/Documents/Models
Binary location: /Users/<username>/.local/bin/gRPCServerCLI

The gRPCServerCLI service is running and will start automatically on login.
You can manage it with these commands:
    launchctl unload ~/Library/LaunchAgents/com.drawthings.grpcserver.plist
    launchctl load ~/Library/LaunchAgents/com.drawthings.grpcserver.plist
```

## Installation Options

### Common Usage

```bash
# Custom model directory
./src/grpc_server_installer.py -m /path/to/models

# Custom port and server name
./src/grpc_server_installer.py -p 7860 -n "MyServer"

# Enable security (recommended)
./src/grpc_server_installer.py -s "your-secret-key"

# Enable model browser
./src/grpc_server_installer.py --model-browser

# Silent installation
./src/grpc_server_installer.py -q
```

### Configuration Options

#### Installer Settings
| Option | Description | Default |
|--------|-------------|---------|
| `-m, --model-path` | Model directory location | Draw Things app models directory |
| `-q, --quiet` | Silent installation | False |
| `--uninstall` | Remove installation | - |
| `--restart` | Restart service | - |

#### Server Settings
| Option | Description | Default |
|--------|-------------|---------|
| `-n, --name` | Network server name | Machine name |
| `-p, --port` | Server port | 7859 |
| `-a, --address` | Network address | 0.0.0.0 |
| `-g, --gpu` | GPU device index | 0 |
| `-s, --shared-secret` | Authentication key | None |
| `-d, --datadog-api-key` | Monitoring API key | None |
| `--no-tls` | Disable encryption | False |
| `--no-response-compression` | Disable compression | False |
| `--model-browser` | Enable model browser | False |
| `--no-flash-attention` | Disable Flash Attention | False |
| `--debug` | Verbose logging | False |

## Advanced Configuration

### Distributed Setup

Use `--join` for distributed configurations:

```bash
./src/grpc_server_installer.py --join '{
  "host": "proxy.example.com",
  "port": 7859,
  "servers": [
    {
      "address": "gpu1.local",
      "port": 7859,
      "priority": 1
    }
  ]
}'
```

Required fields:
- `host`: Proxy server address
- `port`: Proxy server port

Optional fields:
- `servers`: GPU server list
  - `address`: Server address
  - `port`: Server port
  - `priority`: Server priority (1=high, 2=low)

## Service Management

The installer creates a LaunchAgent (`com.drawthings.grpcserver`) that:
- Starts on user login
- Auto-restarts after crashes
- Can be managed via standard `launchctl` commands

```bash
# Stop service
launchctl unload ~/Library/LaunchAgents/com.drawthings.grpcserver.plist

# Start service
launchctl load ~/Library/LaunchAgents/com.drawthings.grpcserver.plist

# Restart service
./src/grpc_server_installer.py --restart
```

## API Endpoints

- `Echo`: Health check
- `FilesExist`: Model file verification
- `GenerateImage`: Image generation
- `UploadFile`: Model file upload

See [API.md](API.md) and [PROTOBUF.md](PROTOBUF.md) for detailed documentation.

## Debugging

Enable detailed logging:
```bash
./src/grpc_server_installer.py --debug
```

## Development

Run tests:
```bash
pytest tests/
```

### Project Structure
```
.
├── src/                    # Core source code
│   ├── grpc_server_installer.py  # Installer script
│   ├── image_generation.proto    # API definitions
│   └── grpc-test.py             # Test client
├── tests/                 # Test suite
├── utils/                 # Utilities
├── API.md                # API docs
└── PROTOBUF.md           # Protocol docs
```

## License

MIT License - see [LICENSE](LICENSE) file.

## Acknowledgments

- [Draw Things](https://drawthings.ai/) - Main application
- [Draw Things Community](https://github.com/drawthingsai/draw-things-community) - Community tools