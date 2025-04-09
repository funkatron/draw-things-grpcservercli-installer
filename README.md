# Draw Things gRPC Server Utilities

A Python package providing utilities for interacting with the Draw Things gRPC server. This package includes tools for server installation, management, and client communication.

## What This Package Provides

- **Server Management Tools**:
  - Installation and configuration of the Draw Things gRPC server
  - Server lifecycle management (start, stop, restart)
  - Health monitoring and status checks
  - Log file management

- **Client Utilities**:
  - Python helper functions for connecting to the gRPC server
  - Error handling utilities for gRPC calls
  - Connection management tools

- **Security Features**:
  - TLS configuration management
  - Authentication setup
  - Certificate management


## Features

- **Server Management**: One-command installation and configuration of the Draw Things gRPC server
- **gRPC Client Utilities**: Python library for easy integration with the image generation service
- **File Management**: Tools for handling server files and configurations
- **Health Monitoring**: Built-in health check endpoints for server status verification
- **Security Features**:
  - TLS encryption support for secure communication
  - Authentication via shared secrets
  - Certificate chain verification
  - Client certificate validation

## Installation

To install the package, follow these steps:

1. Clone the repository:
```bash
git clone https://github.com/yourusername/draw-things-grpcserver-utilities.git
cd draw-things-grpcserver-utilities
```

2. Create and activate a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
# or
.\venv\Scripts\activate  # On Windows
```

3. Install the package in development mode:
```bash
pip install -e .
```

## Getting Started

### Quick Start Guide

If you're new to the Draw Things gRPC server, here's a simple guide to get you started:

1. **Install the Server**:
```bash
# This will install the server with default settings
dts-util install
```

2. **Start the Server**:
```bash
dts-util start
```

3. **Verify the Server is Running**:
```bash
dts-util test
```

4. **Generate Your First Image**:
```python
from dts_util.grpc.utils import create_channel_and_stub, handle_grpc_error
from dts_util.grpc.proto.image_generation_pb2 import GenerateImageRequest

# Connect to the server
channel, stub = create_channel_and_stub(
    host='localhost',      # The server is running on your local machine
    port=50051,           # Default port
    use_tls=False,        # Disable TLS for local development
    shared_secret=''      # No shared secret needed for local development
)

# Generate an image
with handle_grpc_error():
    response = stub.GenerateImage(GenerateImageRequest(
        prompt="a beautiful sunset over mountains",  # Describe what you want to generate
        negative_prompt="",                          # What you don't want in the image
        width=512,                                   # Image width in pixels
        height=512                                   # Image height in pixels
    ))
```

### Common Tasks

#### Installing with Custom Settings

If you need to customize the server installation:

```bash
# Install on a specific port and GPU
dts-util install --port 7860 --gpu 1

# Install with a custom model
dts-util install --model-path /path/to/your/model

# Install with logging enabled
dts-util install --log-file /path/to/logfile.log
```

#### Managing the Server

Basic server management commands:

```bash
# Check if the server is running
dts-util status

# View server logs
dts-util logs

# Stop the server
dts-util stop

# Restart the server
dts-util restart
```

#### Secure Setup (Production)

For a secure production setup:

```bash
# Install with TLS and authentication
dts-util install \
    --tls-cert /path/to/cert.pem \
    --tls-key /path/to/key.pem \
    --shared-secret your-secret-here
```

Then connect securely from your Python code:

```python
channel, stub = create_channel_and_stub(
    host='your-server.com',
    port=50051,
    use_tls=True,
    shared_secret='your-secret-here'
)
```

### Troubleshooting

Common issues and solutions:

1. **Server Won't Start**
   - Check if the port is already in use: `dts-util status`
   - Check logs: `dts-util logs`

2. **Connection Errors**
   - Verify server is running: `dts-util test`
   - Check firewall settings

3. **Image Generation Fails**
   - Check server logs for errors
   - Verify model path is correct
   - Ensure sufficient GPU memory
   - Ensure sufficient storage space

## Advanced Usage

### Package Structure

The package is organized into several modules:

```
src/
├── dts_util/
│   ├── installer/               # Server installation and management
│   ├── grpc/                    # Client communication tools
│   └── utils/                   # Shared utilities
```

### Complete Installation Options

For advanced users, here are all available installation options:

```bash
# Basic settings
dts-util install --port 7860 --gpu 1 --model-path /path/to/model

# Security settings
dts-util install --tls-cert cert.pem --tls-key key.pem --shared-secret secret

# Advanced settings
dts-util install --work-dir /path/to/workdir --log-file /path/to/logfile
```

### Python Client Examples

#### Basic Image Generation

```python
from dts_util.grpc.utils import create_channel_and_stub, handle_grpc_error
from dts_util.grpc.proto.image_generation_pb2 import GenerateImageRequest

# Connect to server
channel, stub = create_channel_and_stub(
    host='localhost',
    port=50051,
    use_tls=False
)

# Generate image
with handle_grpc_error():
    response = stub.GenerateImage(GenerateImageRequest(
        prompt="a beautiful landscape",
        negative_prompt="blurry, low quality",
        width=512,
        height=512
    ))
```

#### Error Handling

```python
from dts_util.grpc.utils import handle_grpc_error

try:
    with handle_grpc_error():
        # Your code here
        pass
except Exception as e:
    print(f"Error occurred: {e}")
```

## Documentation

### Package Documentation
- [API Documentation](API.md): Documentation for this package's utilities and functions
- [CLI Reference](CLI.md): Complete reference for the `dts-util` command-line tool

### Draw Things gRPC Server Documentation
- [Protocol Buffer Specifications](PROTOBUF.md): Documentation of the gRPC server's API and message definitions
- For complete server documentation, please refer to the [Draw Things documentation](https://drawthings.ai/docs)

## Development

### Requirements

- Python 3.8+
- gRPC tools
- Protocol Buffers compiler

### Setting Up Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.