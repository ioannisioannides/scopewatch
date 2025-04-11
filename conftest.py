import pytest
from django.conf import settings
from django.test import RequestFactory


@pytest.fixture
def request_factory():
    return RequestFactory()


@pytest.fixture(autouse=True)
def configure_settings():
    settings.MIGRATION_MODULES = {
        "audits": "audits.migrations",
    }
