#!/usr/bin/env python3
"""
Test script for exploring and testing the Draw Things gRPC server API.
Uses discovered service and method names from the app bundle.
"""

import argparse
import grpc
import os
import sys
from pathlib import Path
from grpc_reflection.v1alpha import reflection_pb2, reflection_pb2_grpc
from google.protobuf import descriptor_pb2, descriptor_pool
import json
import pytest
from tests.conftest import *
from tests.test_grpc import *

if __name__ == '__main__':
    pytest.main(['-v', 'tests'])
