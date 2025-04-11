"""
Configuration utilities for the Scopewatch project.

This module provides helper functions for loading and validating configuration
from environment variables.
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, cast

from decouple import Config, RepositoryEnv
from decouple import config as decouple_config


def get_env_file_path() -> Optional[Path]:
    """
    Get the path to the .env file.

    This function attempts to locate a .env file in the current directory or parent directories.
    It returns None if no .env file is found.

    Returns:
        Path: Path to the .env file or None if not found
    """
    base_dir = Path(__file__).resolve().parent.parent

    # First, check for environment-specific .env files
    env = os.environ.get("ENV", "development")
    env_specific_path = base_dir / f".env.{env}"
    if env_specific_path.exists():
        return env_specific_path

    # Then, check if there's a .env file in the project root
    env_path = base_dir / ".env"
    if env_path.exists():
        return env_path

    # If not found in root, check parent directory (for some deployment scenarios)
    parent_env_path = base_dir.parent / ".env"
    if parent_env_path.exists():
        return parent_env_path

    return None


def get_config() -> Config:
    """
    Get the configuration source (either .env file or environment variables).

    Returns:
        Config: A configuration source object
    """
    env_path = get_env_file_path()
    if env_path:
        return cast(Config, RepositoryEnv(str(env_path)))
    return cast(Config, os)


def config(
    key: str, default: Any = None, cast: Any = str, required: bool = False
) -> Any:
    """
    Get a configuration value from environment variables or .env file.

    This function extends decouple.config by adding a 'required' parameter
    that raises an error if the key is not found and no default is specified.

    Args:
        key: The name of the environment variable
        default: The default value if the key is not found
        cast: A callable that converts the value to the desired type
        required: Whether the key is required

    Returns:
        The value of the environment variable, cast to the desired type

    Raises:
        ValueError: If the key is required but not found and no default is specified
    """
    if required and default is None:
        value = decouple_config(key, cast=cast)
        if value is None:
            raise ValueError(f"Required environment variable {key} is not set")
        return value
    return decouple_config(key, default=default, cast=cast)


def is_debug_mode() -> bool:
    """
    Check if the application is running in debug mode.

    Returns:
        bool: True if debug mode is enabled, False otherwise
    """
    return config("DEBUG", default=False, cast=bool)


def is_production() -> bool:
    """
    Check if the application is running in production mode.

    Returns:
        bool: True if in production environment, False otherwise
    """
    env = os.environ.get("ENV", "").lower()
    return env == "production" or (not is_debug_mode() and not is_test_environment())


def is_development() -> bool:
    """
    Check if the application is running in development mode.

    Returns:
        bool: True if in development environment, False otherwise
    """
    env = os.environ.get("ENV", "").lower()
    return env == "development" or (is_debug_mode() and not is_test_environment())


def is_test_environment() -> bool:
    """
    Check if the application is running in a test environment.

    Returns:
        bool: True if in a test environment, False otherwise
    """
    return (
        "test" in sys.argv
        or "pytest" in sys.modules
        or os.environ.get("ENV", "").lower() == "test"
    )
