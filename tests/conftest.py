#!/usr/bin/env python3

import configparser
import platform
from pathlib import Path

import praw
import pytest

from bdfrx.oauth2 import OAuth2TokenManager


@pytest.fixture(scope="session")
def reddit_instance():
    rd = praw.Reddit(
        client_id="0vIJGSRQEHgi_r0esNWvjg",
        client_secret=None,
        user_agent="test",
    )
    return rd


@pytest.fixture(scope="session")
def authenticated_reddit_instance():
    test_config_path = Path("./tests/test_config.cfg")
    if not test_config_path.exists():
        pytest.skip("Refresh token must be provided to authenticate with OAuth2")
    cfg_parser = configparser.ConfigParser()
    cfg_parser.read(test_config_path)
    if not cfg_parser.has_option("DEFAULT", "user_token"):
        pytest.skip("Refresh token must be provided to authenticate with OAuth2")
    token_manager = OAuth2TokenManager(cfg_parser, test_config_path)
    reddit_instance = praw.Reddit(
        client_id=cfg_parser.get("DEFAULT", "client_id"),
        client_secret=None,
        user_agent=praw.const.USER_AGENT_FORMAT.format(":".join([platform.uname()[0], __package__, "test"])),
        token_manager=token_manager,
    )
    return reddit_instance
