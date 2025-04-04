# Draw Things Protocol Buffer Specifications

This document provides detailed protocol buffer specifications for the Draw Things gRPC server. For API usage, see [API.md](API.md).

## Service Definition

```protobuf
service ImageGenerationService {
  // Echo endpoint for health check
  rpc Echo(EchoRequest) returns (EchoResponse);

  // Check if model files exist
  rpc FilesExist(FilesExistRequest) returns (FilesExistResponse);

  // Generate images based on parameters
  rpc GenerateImage(ImageGenerationRequest) returns (ImageGenerationResponse);

  // Upload model files
  rpc UploadFile(stream UploadFileRequest) returns (UploadFileResponse);
}
```

## Message Specifications

### Health Check
```protobuf
message EchoRequest {
}

message EchoResponse {
  string message = 1;  // Always contains "HELLO"
}
```

### File Management
```protobuf
message FilesExistRequest {
  repeated string files = 1;  // Files to check
}

message FilesExistResponse {
  repeated string files = 1;   // Checked files
  repeated bool exists = 2;    // Existence status
  repeated string errors = 3;  // Error messages
}

message UploadFileRequest {
  string filename = 1;      // Target filename
  bytes chunk_data = 2;     // File chunk data
}

message UploadFileResponse {
  bool success = 1;         // Upload status
  string message = 2;       // Status message
}
```

### Image Generation
```protobuf
message ImageGenerationRequest {
  string prompt = 1;              // Generation prompt
  string negative_prompt = 2;     // Negative prompt
  int32 width = 3;               // Image width
  int32 height = 4;              // Image height
  int32 steps = 5;               // Sampling steps
  float cfg_scale = 6;           // CFG scale
  int64 seed = 7;                // Random seed
  string sampler = 8;            // Sampler name
  bool restore_faces = 9;        // Face restoration
  bool enable_hr = 10;           // High-res fix
  float denoising_strength = 11; // Denoising strength
  int32 batch_size = 12;         // Images per batch
  int32 batch_count = 13;        // Number of batches
}

message ImageGenerationResponse {
  repeated bytes images = 1;           // PNG format images
  repeated string info = 2;            // Generation info
  repeated SignpostEvent events = 3;   // Progress events
}
```

### Progress Tracking
```protobuf
message SignpostEvent {
  string name = 1;          // Event description
  int64 timestamp = 2;      // Milliseconds since epoch
  enum EventType {
    TEXT_ENCODED = 0;             // Text encoding complete
    IMAGE_DECODED = 1;            // Image decoding complete
    IMAGE_ENCODED = 2;            // Image encoding complete
    SAMPLING = 3;                 // Sampling in progress
    FACE_RESTORED = 4;            // Face restoration complete
    IMAGE_UPSCALED = 5;           // Upscaling complete
    SECOND_PASS_IMAGE_DECODED = 6; // HR fix decode complete
    SECOND_PASS_IMAGE_ENCODED = 7; // HR fix encode complete
    SECOND_PASS_SAMPLING = 8;      // HR fix sampling complete
  }
  EventType type = 3;
}
```

## Wire Format

### Field Encoding
- `string`: UTF-8 encoded text
- `bytes`: Raw binary data
- `int32`/`int64`: Variable-length encoding
- `float`: 32-bit IEEE 754
- `bool`: Varint encoded (0/1)
- `repeated`: Length-prefixed sequence
- `enum`: Varint encoded

### Message Format
- Messages are length-prefixed
- Fields are key-value pairs
- Keys encode field number and wire type
- Unknown fields are preserved
- Optional fields may be omitted
- Repeated fields may be empty

### Transport
- Uses standard gRPC over HTTP/2
- Binary protocol buffer encoding
- Messages framed with length prefix
- Streaming supported where specified
- TLS encryption available
- Optional response compression

## Implementation Notes

### Message Serialization
- Uses binary protobuf format for all messages
- Response messages include error details when needed
- Empty messages (like EchoRequest) are serialized as empty bytes
- Messages are length-prefixed in transport
- Uses standard protobuf wire format
- Handles UTF-8 encoding for strings

### Field Types
- Uses standard protobuf field types:
  - `string` for text fields (UTF-8 encoded)
  - `bytes` for binary data (raw bytes)
  - `int32`/`int64` for integers (varint encoded)
  - `float` for floating-point numbers (32-bit)
  - `bool` for boolean values (varint encoded)
  - `repeated` for lists/arrays (packed when possible)
- Field numbers are important for compatibility
- Optional fields may be omitted
- Repeated fields may be empty
- Unknown fields are preserved

### Error Handling
- Error messages are included in response messages
- Uses standard gRPC status codes for transport-level errors
- Each response type includes fields for error reporting

### Testing
- Messages can be tested using the provided test script
- Echo endpoint returns a simple string message
- FilesExist endpoint returns parallel arrays for status
- Generated code handles serialization/deserialization