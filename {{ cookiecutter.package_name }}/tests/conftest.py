from pathlib import Path
from typing import Union
from unittest.mock import MagicMock

import pytest
from fastapi import BackgroundTasks, FastAPI
from sqlalchemy.orm import Session
from starlette.testclient import TestClient


@pytest.fixture(scope="session", autouse=True)
def _config():
    from {{ cookiecutter.module_name }} import config

    config.yaml_path = Path(__file__).parent / "test_config.yml"


# noinspection PyUnresolvedReferences
@pytest.yield_fixture
def session(_app, _config) -> Session:
    from {{ cookiecutter.module_name }}.database import SessionLocal, Base, get_session
    from {{ cookiecutter.module_name }} import models

    Base.metadata.drop_all()
    Base.metadata.create_all()
    try:
        session = SessionLocal()
        _app.dependency_overrides[get_session] = lambda: session
        yield session
    finally:
        if session:
            session.close()


@pytest.fixture
def mock_session(_app, mocker) -> MagicMock:
    from {{ cookiecutter.module_name }}.database import get_session

    mock_session = mocker.MagicMock()

    def _get_mock_db():
        yield mock_session

    _app.dependency_overrides[get_session] = _get_mock_db
    return mock_session


@pytest.fixture
def factory_session(request) -> Union[MagicMock, Session]:
    """ Return either mock_session or session, whichever is being used """
    fixture_names = set(request.fixturenames)
    if "mock_session" in fixture_names:
        return request.getfixturevalue("mock_session")
    elif "session" in fixture_names:
        return request.getfixturevalue("session")
    raise ValueError("Either mock_session or session fixture must be used by test function")


@pytest.fixture
def _app(_config) -> FastAPI:
    from {{ cookiecutter.module_name }}.main import app

    return app


@pytest.fixture
def client(_app) -> TestClient:
    """ A client to use for testing the API """
    return TestClient(_app)


# noinspection PyUnresolvedReferences
from .model_fixtures import *  # isort:skip
