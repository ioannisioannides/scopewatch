"""
Test credentials utility for Scopewatch.

This module provides functions to access test credentials from environment variables,
which are configured as secrets in the GitHub Development environment.
"""

from scopewatch.config import config


def get_test_credential(type_name, credential_type="password", default=None):
    """
    Get a test credential from environment variables.

    Args:
        type_name (str): The user type (e.g., 'default', 'certbody', 'api')
        credential_type (str): The credential type (e.g., 'username', 'password', 'email')
        default (str): Optional default value if the credential is not found

    Returns:
        str: The credential value from environment variables or a fallback value for local development
    """
    env_var = f"TEST_{type_name.upper()}_{credential_type.upper()}"

    # Fallback values for local development when environment variables aren't set
    # These should ONLY be used for local development and never in production
    fallback_values = {
        # Default test user
        "TEST_DEFAULT_USERNAME": "testuser",
        "TEST_DEFAULT_PASSWORD": "test_password123",
        "TEST_DEFAULT_EMAIL": "test@example.com",
        # Certification body users
        "TEST_CERTBODY_USERNAME": "certbody_staff",
        "TEST_CERTBODY_PASSWORD": "secure_password123",
        "TEST_CERTBODY_EMAIL": "staff@certbody.com",
        "TEST_CERTBODY_ALT_USERNAME": "other_staff",
        "TEST_CERTBODY_ALT_PASSWORD": "other_password",
        # Auditor users
        "TEST_AUDITOR_USERNAME": "auditor_user",
        "TEST_AUDITOR_PASSWORD": "secure_password",
        "TEST_AUDITOR_EMAIL": "auditor@example.com",
        # Unauthorized user
        "TEST_UNAUTHORIZED_USERNAME": "unauthorized",
        "TEST_UNAUTHORIZED_PASSWORD": "password123",
        # Consultant users
        "TEST_CONSULTANT_USERNAME": "consultant_user",
        "TEST_CONSULTANT_PASSWORD": "password",
        # API test users
        "TEST_API_USERNAME": "api_test_user",
        "TEST_API_PASSWORD": "test_password123",
        "TEST_API_EMAIL": "api@example.com",
        "TEST_API_ALT_USERNAME": "api_tester",
        "TEST_API_ALT_PASSWORD": "complex123",
    }

    # If a default is provided, use it as the final fallback
    final_default = default if default is not None else fallback_values.get(env_var, "test_default")

    # Use config function to read from environment variables with fallback
    return config(env_var, default=final_default)
