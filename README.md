# Draw Things gRPC Server Utilities

A Python package providing utilities for interacting with the Draw Things gRPC server. This package includes tools for server installation, management, and client communication.

## Features

- Server installation and configuration
- gRPC client utilities for image generation
- File management tools
- Health check endpoints
- TLS encryption support
- Authentication via shared secrets

## Installation

Install directly from the repository:

```bash
git clone https://github.com/yourusername/draw-things-grpcserver-utilities.git
cd draw-things-grpcserver-utilities
pip install -e .
```

## Package Structure

```
src/
├── dts_util/
│   ├── __init__.py
│   ├── installer/
│   │   ├── __init__.py
│   │   └── server_installer.py
│   ├── grpc/
│   │   ├── __init__.py
│   │   ├── utils.py
│   │   └── proto/
│   │       ├── __init__.py
│   │       ├── image_generation.proto
│   │       ├── image_generation_pb2.py
│   │       └── image_generation_pb2_grpc.py
│   └── utils/
│       ├── __init__.py
│       └── common.py
```

## Usage

### Server Installation

Install the Draw Things gRPC server:

```bash
dts-util install
```

### Client Usage

```python
from dts_util.grpc.utils import create_channel_and_stub, handle_grpc_error
from dts_util.grpc.proto.image_generation_pb2 import GenerateImageRequest

# Create a channel and stub
channel, stub = create_channel_and_stub(
    host='localhost',
    port=50051,
    use_tls=True,
    shared_secret='your-secret'
)

# Make RPC calls with error handling
with handle_grpc_error():
    response = stub.GenerateImage(GenerateImageRequest(
        prompt="a beautiful landscape",
        negative_prompt="",
        width=512,
        height=512
    ))
```

### Server Health Check

```python
from dts_util.grpc.utils import is_server_running

if is_server_running(port=50051):
    print("Server is running!")
else:
    print("Server is not available")
```

## Documentation

- [API Documentation](API.md): Detailed API reference
- [Protocol Buffer Specifications](PROTOBUF.md): gRPC service and message definitions

## Development

### Requirements

- Python 3.8+
- gRPC tools
- Protocol Buffers compiler

### Running Tests

```bash
pip install -e ".[dev]"  # Install development dependencies
pytest tests/
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.