"""
Configuration loading utilities for the Proxmox MCP server.

This module handles loading and validation of server configuration:
- JSON configuration file loading
- Environment variable handling
- Configuration validation using Pydantic models
- Error handling for invalid configurations

The module ensures that all required configuration is present
and valid before the server starts operation.
"""
import json
import os
from typing import Optional
from .models import Config

def load_config(config_path: Optional[str] = None) -> Config:
    """Load and validate configuration from JSON file.

    Performs the following steps:
    1. Verifies config path is provided
    2. Loads JSON configuration file
    3. Validates required fields are present
    4. Converts to typed Config object using Pydantic
    
    Configuration must include:
    - Proxmox connection settings (host, port, etc.)
    - Authentication credentials (user, token)
    - Logging configuration
    
    Args:
        config_path: Path to the JSON configuration file
                    If not provided, raises ValueError

    Returns:
        Config object containing validated configuration:
        {
            "proxmox": {
                "host": "proxmox-host",
                "port": 8006,
                ...
            },
            "auth": {
                "user": "username",
                "token_name": "token-name",
                ...
            },
            "logging": {
                "level": "INFO",
                ...
            }
        }

    Raises:
        ValueError: If:
                 - Config path is not provided
                 - JSON is invalid
                 - Required fields are missing
                 - Field values are invalid
    """
    if not config_path:
        raise ValueError("PROXMOX_MCP_CONFIG environment variable must be set")

    try:
        with open(config_path) as f:
            config_data = json.load(f)
            if not config_data.get('proxmox', {}).get('host'):
                raise ValueError("Proxmox host cannot be empty")
            return Config(**config_data)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in config file: {e}")
    except Exception as e:
        raise ValueError(f"Failed to load config: {e}")
