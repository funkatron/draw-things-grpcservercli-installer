# Draw Things gRPC Server API Documentation

## Service: ImageGenerationService

The Draw Things gRPC server exposes an `ImageGenerationService` that provides various endpoints for image generation and file management.

### Connection Details

#### Server Configuration
- **Default Host**: localhost
- **Default Port**: 7859
- **Alternative Port**: 7860
- **Service Type**: `com.draw-things.image-generation-service`
- **Service Name**: `com.draw-things.grpc-service`

#### Authentication
- **Shared Secret**: Uses `gRPCSharedSecret` for authentication
- **TLS Support**: Optional

### Endpoints

#### 1. Echo
- **Method**: `/ImageGenerationService/Echo`
- **Type**: Unary RPC
- **Description**: Simple connectivity test endpoint
- **Request**: Empty
- **Response**: Returns "HELLO" if successful

#### 2. FilesExist
- **Method**: `/ImageGenerationService/FilesExist`
- **Type**: Unary RPC
- **Description**: Checks if specified model files exist in the server's model directory
- **Common Model Paths**:
  - `stable-diffusion/model.safetensors`
  - `vae/model.safetensors`

#### 3. GenerateImage
- **Method**: `/ImageGenerationService/GenerateImage`
- **Type**: Unary RPC
- **Description**: Generates images based on provided parameters
- **Response Fields**:
  - `generated_in_seconds`: Generation time
  - `generated_caption`: Generated image caption
  - `estimated_time_to_generate`: Estimated generation time
  - `have_not_generated_images`: Status flag

#### 4. UploadFile
- **Method**: `/ImageGenerationService/UploadFile`
- **Type**: Client Streaming RPC
- **Description**: Allows uploading files to the server

### Protocol Details

#### Content Types
- `application/grpc`
- `application/grpc+proto`
- `application/grpc-web`
- `application/grpc-web+proto`
- `application/grpc-web-text`
- `application/grpc-web-text+proto`

#### Headers
- `grpc-accept-encoding`: Used for compression negotiation

### Model Path
Default model path (macOS):
```
~/Library/Containers/com.liuliu.draw-things/Data/Documents/Models
```

### Service Discovery
- Uses Bonjour/mDNS for service discovery
- Service advertised as `com.draw-things.image-generation-service`
- Supports automatic server discovery on local network

### Error Handling
- Supports standard gRPC status codes
- Includes detailed error messages in responses
- Handles protocol violations and connection issues

### Notes
- The server implements gRPC reflection for runtime service discovery
- Supports both secure (TLS) and insecure connections
- Uses Protocol Buffers for message serialization
- Implements denial of service protection