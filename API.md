# Draw Things gRPC Server API Documentation

## Overview

The Draw Things gRPC server provides a service for image generation and model management. It's implemented as a standalone CLI tool (`gRPCServerCLI`) that interfaces with the Draw Things app's model directory.

## Server Configuration

### Binary Location
- **CLI Tool**: `~/.local/bin/gRPCServerCLI` or `/usr/local/bin/gRPCServerCLI`
- **Default Settings**:
  - Port: 7859
  - Host: 0.0.0.0
  - TLS: Enabled by default
  - Service Name: `com.drawthings.grpcserver`

### Model Directory
Default location (macOS):
```
~/Library/Containers/com.liuliu.draw-things/Data/Documents/Models
```

Required model files:
- `stable-diffusion/model.safetensors`: Main Stable Diffusion model
- `vae/model.safetensors`: VAE model for image encoding/decoding

## API Endpoints

### 1. Echo
Health check endpoint to verify server connectivity.

**Request**: Empty message
```protobuf
message EchoRequest {
}
```

**Response**: Returns "HELLO"
```protobuf
message EchoResponse {
  string message = 1;
}
```

### 2. FilesExist
Verifies existence of model files in the server's model directory.

**Request**:
```protobuf
message FilesExistRequest {
  repeated string files = 1;  // List of files to check
}
```

**Response**:
```protobuf
message FilesExistResponse {
  repeated string files = 1;   // List of checked files
  repeated bool exists = 2;    // Existence status for each file
  repeated string errors = 3;  // Error messages if any
}
```

### 3. GenerateImage
Main endpoint for image generation.

**Request**:
```protobuf
message ImageGenerationRequest {
  string prompt = 1;              // Generation prompt
  string negative_prompt = 2;     // Negative prompt
  int32 width = 3;               // Image width
  int32 height = 4;              // Image height
  int32 steps = 5;               // Number of steps
  float cfg_scale = 6;           // CFG scale
  int64 seed = 7;                // Random seed
  string sampler = 8;            // Sampler name
  bool restore_faces = 9;        // Face restoration
  bool enable_hr = 10;           // High-res fix
  float denoising_strength = 11; // Denoising strength
  int32 batch_size = 12;         // Images per batch
  int32 batch_count = 13;        // Number of batches
}
```

**Response**:
```protobuf
message ImageGenerationResponse {
  repeated bytes images = 1;           // Generated images (PNG format)
  repeated string info = 2;            // Generation parameters
  repeated SignpostEvent events = 3;   // Progress events
}
```

### 4. UploadFile
Endpoint for uploading model files to the server.

**Request** (streaming):
```protobuf
message UploadFileRequest {
  string filename = 1;      // Target filename
  bytes chunk_data = 2;     // File data chunk
}
```

**Response**:
```protobuf
message UploadFileResponse {
  bool success = 1;         // Upload status
  string message = 2;       // Status/error message
}
```

## Progress Events

Generation progress is tracked via SignpostEvents:

```protobuf
message SignpostEvent {
  string name = 1;          // Event description
  int64 timestamp = 2;      // Milliseconds since epoch
  enum EventType {
    TEXT_ENCODED = 0;
    IMAGE_DECODED = 1;
    IMAGE_ENCODED = 2;
    SAMPLING = 3;
    FACE_RESTORED = 4;
    IMAGE_UPSCALED = 5;
    SECOND_PASS_IMAGE_DECODED = 6;
    SECOND_PASS_IMAGE_ENCODED = 7;
    SECOND_PASS_SAMPLING = 8;
  }
  EventType type = 3;
}
```

## Error Handling

- Uses standard gRPC status codes for transport errors
- Application errors are included in response messages
- Common status codes:
  - `OK`: Success
  - `INVALID_ARGUMENT`: Invalid request parameters
  - `NOT_FOUND`: Model file not found
  - `INTERNAL`: Server processing error
  - `UNIMPLEMENTED`: Method not supported

## Security

- TLS encryption enabled by default
- Optional shared secret authentication
- Server binds to all interfaces (0.0.0.0)
- Response compression enabled by default

For detailed protocol buffer specifications, see [PROTOBUF.md](PROTOBUF.md).