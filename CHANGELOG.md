# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive test suite for gRPC utilities
  - Server availability checking
  - Error handling for various gRPC scenarios
  - Channel creation with different configurations
- Improved error handling in `handle_grpc_error`
  - Simplified error code checking
  - Better handling of missing code() methods