# Draw Things gRPC Server API Documentation

## Overview

The Draw Things gRPC server provides a service for image generation and model management. It's implemented as a standalone CLI tool (`gRPCServerCLI`) that interfaces with the Draw Things app's model directory.

## Server Configuration

### Binary Location
- **CLI Tool**: `/Users/<user>/.local/bin/gRPCServerCLI`
- **Arguments**:
  - `--port`: Server port (default: 7860)
  - `--no-tls`: Disable TLS (recommended for local use)
  - Model directory path (required)
- **Example**:
  ```bash
  gRPCServerCLI "/Users/user/Library/Containers/com.liuliu.draw-things/Data/Documents/Models" --port 7860 --no-tls
  ```

### Connection Details
- **Default Host**: localhost
- **Default Port**: 7860
- **TLS**: Optional, disabled by default
- **Service Type**: `com.draw-things.image-generation-service`
- **Process Name**: Appears as `gRPCServerCLI` in system processes

### Model Directory
Default location (macOS):
```
~/Library/Containers/com.liuliu.draw-things/Data/Documents/Models
```

Required model files:
- `stable-diffusion/model.safetensors`: Main Stable Diffusion model
- `vae/model.safetensors`: VAE model for image encoding/decoding

## Service: ImageGenerationService

### 1. Echo
- **Method**: `/ImageGenerationService/Echo`
- **Type**: Unary RPC
- **Description**: Simple connectivity test endpoint
- **Request**: Empty message
- **Response**: Returns "HELLO" in a protobuf message
- **Example Response**:
  ```
  b'\n\x06HELLO '
  ```
- **Usage**:
  - Use to verify server is running and accepting connections
  - No authentication required
  - Returns immediately without checking model files

### 2. FilesExist
- **Method**: `/ImageGenerationService/FilesExist`
- **Type**: Unary RPC
- **Description**: Checks if specified model files exist in the server's model directory
- **Request Format**:
  ```protobuf
  message FilesExistRequest {
    repeated string files = 1;
  }
  ```
- **Response Format**:
  ```protobuf
  message FilesExistResponse {
    repeated string files = 1;   // List of checked files
    repeated bool exists = 2;    // Existence status for each file
    repeated string errors = 3;  // Error messages if any
  }
  ```
- **Common Model Paths**:
  - `stable-diffusion/model.safetensors`
  - `vae/model.safetensors`
- **Response Behavior**:
  - Returns parallel arrays for files, existence status, and errors
  - Files array matches input order
  - Empty error strings for successful checks
  - Non-empty error strings indicate access or validation issues

### 3. GenerateImage
- **Method**: `/ImageGenerationService/GenerateImage`
- **Type**: Unary RPC
- **Description**: Generates images based on provided parameters
- **Request Format**:
  ```protobuf
  message ImageGenerationRequest {
    string prompt = 1;
    string negative_prompt = 2;
    int32 width = 3;
    int32 height = 4;
    int32 steps = 5;
    float cfg_scale = 6;
    int64 seed = 7;
    string sampler = 8;
    bool restore_faces = 9;
    bool enable_hr = 10;
    float denoising_strength = 11;
    int32 batch_size = 12;
    int32 batch_count = 13;
  }
  ```
- **Response Format**:
  ```protobuf
  message ImageGenerationResponse {
    repeated bytes images = 1;
    repeated string info = 2;
    repeated SignpostEvent events = 3;
  }
  ```

### 4. UploadFile
- **Method**: `/ImageGenerationService/UploadFile`
- **Type**: Client Streaming RPC
- **Description**: Allows uploading files to the server
- **Request Format**:
  ```protobuf
  message UploadFileRequest {
    string filename = 1;
    bytes chunk_data = 2;
  }
  ```
- **Response Format**:
  ```protobuf
  message UploadFileResponse {
    bool success = 1;
    string message = 2;
  }
  ```

## Implementation Notes

### Protocol Details
- Uses Protocol Buffers for message serialization
- Supports both binary and text formats
- Content types supported:
  - `application/grpc`
  - `application/grpc+proto`
- Binary format preferred for efficiency

### Error Handling
- Returns standard gRPC status codes
- Includes detailed error messages in responses
- Common error cases:
  - `UNIMPLEMENTED`: Method not available
  - `INTERNAL`: Request processing error
  - `INVALID_ARGUMENT`: Malformed request
- Error details included in response messages where possible
- Transport-level errors use gRPC status codes
- Application-level errors use message-specific error fields

### Testing
- Echo endpoint can be used to verify connectivity
- FilesExist endpoint can verify model installation
- All endpoints support error details in responses
- Server does not support gRPC reflection API
- Test script provided for endpoint verification
- Recommended testing order:
  1. Echo - verify basic connectivity
  2. FilesExist - verify model installation
  3. GenerateImage - test image generation
  4. UploadFile - test model management

### Security
- Local-only service by default
- Optional TLS support
- No authentication required for local connections
- Server binds to localhost interface
- Access restricted to local machine by default

### Performance
- Server runs as a standalone process
- Single instance per machine
- Maintains model files in memory
- Supports concurrent requests
- Uses efficient binary protocol
- Minimizes data copying with streaming responses

### Debugging
- Server logs to stdout/stderr
- Process can be monitored via standard tools
- Error messages are descriptive
- Response messages include detailed status
- Test script provides verbose output option