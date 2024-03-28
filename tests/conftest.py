import os
import pytest

from src.ingest import WebhookIngester


@pytest.fixture
def ingester():
    return WebhookIngester()
