"""Pytest configuration"""

import pytest


def pytest_ignore_collect(collection_path, config):
    """Ignore collection from core/batch_robustness.py"""
    return str(collection_path).endswith("core/batch_robustness.py")
