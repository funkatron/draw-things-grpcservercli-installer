# Draw Things Protobuf Definitions

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

## Message Definitions

### Echo Messages
```protobuf
message EchoRequest {
}

message EchoResponse {
  string message = 1;  // Contains "HELLO"
}
```
**Implementation Notes**:
- Empty request message serializes to zero bytes
- Response message uses minimal encoding
- Message field is always "HELLO"
- No error fields needed

### File Management Messages
```protobuf
message FilesExistRequest {
  repeated string files = 1;  // List of files to check
}

message FilesExistResponse {
  repeated string files = 1;   // List of checked files
  repeated bool exists = 2;    // Existence status for each file
  repeated string errors = 3;  // Error messages if any
}

message UploadFileRequest {
  string filename = 1;      // Target filename
  bytes chunk_data = 2;     // File data chunk
}

message UploadFileResponse {
  bool success = 1;         // Upload success status
  string message = 2;       // Status message or error
}
```
**Implementation Notes**:
- FilesExist uses parallel arrays for response
- File paths are relative to model directory
- Empty error strings indicate success
- Upload chunks should be reasonable size (e.g., 1MB)
- Last chunk may be smaller than others
- Filename should include relative path

### Image Generation Messages
```protobuf
message ImageGenerationRequest {
  string prompt = 1;              // Generation prompt
  string negative_prompt = 2;     // Negative prompt
  int32 width = 3;               // Image width
  int32 height = 4;              // Image height
  int32 steps = 5;               // Number of steps
  float cfg_scale = 6;           // CFG scale
  int64 seed = 7;               // Random seed
  string sampler = 8;            // Sampler name
  bool restore_faces = 9;        // Face restoration
  bool enable_hr = 10;           // High-res fix
  float denoising_strength = 11; // Denoising strength
  int32 batch_size = 12;         // Images per batch
  int32 batch_count = 13;        // Number of batches
}

message ImageGenerationResponse {
  repeated bytes images = 1;           // Generated images
  repeated string info = 2;            // Generation info
  repeated SignpostEvent events = 3;   // Progress events
}
```
**Implementation Notes**:
- All numeric fields have sensible defaults
- Images returned as PNG format in bytes
- Info strings contain generation parameters
- Events track generation progress
- Batch operations return multiple images
- High-res fix requires additional processing

### Progress Tracking
```protobuf
message SignpostEvent {
  string name = 1;
  int64 timestamp = 2;
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
**Implementation Notes**:
- Timestamps in milliseconds since epoch
- Events sent in chronological order
- Event names provide additional context
- Types indicate processing stage
- Second pass events for high-res fix

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

  - `string` for text fields
  - `bytes` for binary data
  - `int32`/`int64` for integers
  - `float` for floating-point numbers
  - `bool` for boolean values
  - `repeated` for lists/arrays

### Error Handling
- Error messages are included in response messages
- Uses standard gRPC status codes for transport-level errors
- Each response type includes fields for error reporting

### Testing
- Messages can be tested using the provided test script
- Echo endpoint returns a simple string message
- FilesExist endpoint returns parallel arrays for status
- Generated code handles serialization/deserialization