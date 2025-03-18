# Draw Things Protobuf Definitions

## Message Types

### Core Messages
- `ImageGenerationRequest`
- `ImageGenerationSignpostProto`
  - `TextEncoded`
  - `ImageEncoded`
  - `Sampling`
  - `ImageDecoded`
  - `SecondPassImageEncoded`
  - `SecondPassSampling`
  - `SecondPassImageDecoded`
  - `FaceRestored`
  - `ImageUpscaled`

### Google Protobuf Types Used
- `google.protobuf.Any`
- `google.protobuf.Duration`
- `google.protobuf.Empty`
- `google.protobuf.FieldMask`
- `google.protobuf.Timestamp`
- `google.protobuf.Value`
- `google.protobuf.ListValue`
- `google.protobuf.Struct`

### Wrapper Types
- `BoolValue`
- `BytesValue`
- `DoubleValue`
- `FloatValue`
- `Int32Value`
- `Int64Value`
- `StringValue`
- `UInt32Value`
- `UInt64Value`

## Service Configuration

### Service Descriptors
- Uses `ServiceDescriptorProto` for service definitions
- Implements `MethodDescriptorProto` for method definitions
- Supports service options via `ServiceOptions`

### Protocol Features
- Supports Protocol Buffers version 2 and 3
- Uses binary format for efficient transmission
- Implements reflection capabilities
- Supports custom options and extensions

### Message Generation
- Supports automatic code generation
- Uses Swift Protobuf for message handling
- Implements efficient binary serialization/deserialization

## Notes
- The service uses Protocol Buffers for all message serialization
- Implements standard Google Protobuf message types
- Supports both binary and text format protocols
- Uses reflection for runtime type information