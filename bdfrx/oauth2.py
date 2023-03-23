#!/usr/bin/env python3

import configparser
import logging
import random
import re
import socket
import webbrowser
from pathlib import Path

import praw
import requests

from bdfrx.exceptions import BulkDownloaderException, RedditAuthenticationError

logger = logging.getLogger(__name__)


class OAuth2Authenticator:
    def __init__(self, wanted_scopes: set[str], client_id: str, client_secret: str, user_agent: str) -> None:
        self._check_scopes(wanted_scopes, user_agent)
        self.scopes = wanted_scopes
        self.client_id = client_id
        self.client_secret = client_secret

    @staticmethod
    def _check_scopes(wanted_scopes: set[str], user_agent: str) -> None:
        try:
            response = requests.get(
                "https://www.reddit.com/api/v1/scopes.json",
                headers={"User-Agent": user_agent},
                timeout=16,
            )
        except TimeoutError:
            raise BulkDownloaderException("Reached timeout fetching scopes")
        known_scopes = [scope for scope, data in response.json().items()]
        known_scopes.append("*")
        for scope in wanted_scopes:
            if scope not in known_scopes:
                raise BulkDownloaderException(f"Scope {scope!r} is not known to reddit")

    @staticmethod
    def split_scopes(scopes: str) -> set[str]:
        scopes = re.split(r"[,: ]+", scopes)
        return set(scopes)

    def retrieve_new_token(self) -> str:
        reddit = praw.Reddit(
            redirect_uri="http://localhost:7634",
            user_agent="obtain_refresh_token for BDFRx",
            client_id=self.client_id,
            client_secret=self.client_secret,
        )
        state = str(random.randint(0, 65000))  # noqa: S311
        url = reddit.auth.url(scopes=self.scopes, state=state, duration="permanent")
        logger.warning("Authentication action required before the program can proceed")
        logger.warning(f"Authenticate at {url!r} if your browser does not open it for you")
        try:
            webbrowser.open_new_tab(url=url)
        except webbrowser.Error:
            logger.debug("Exception opening browser")

        client = self.receive_connection()
        data = client.recv(1024).decode("utf-8")
        param_tokens = data.split(" ", 2)[1].split("?", 1)[1].split("&")
        params = {key: value for (key, value) in [token.split("=") for token in param_tokens]}

        if state != params["state"]:
            self.send_message(client)
            raise RedditAuthenticationError(f"State mismatch in OAuth2. Expected: {state} Received: {params['state']}")
        elif "error" in params:
            self.send_message(client)
            raise RedditAuthenticationError(f"Error in OAuth2: {params['error']}")

        refresh_token = reddit.auth.authorize(params["code"])
        self.send_message(
            client, f"Refresh token: {refresh_token}<script>alert('You can go back to terminal window now.')</script>"
        )
        return refresh_token

    @staticmethod
    def receive_connection() -> socket.socket:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(("0.0.0.0", 7634))  # noqa: S104
        logger.log(9, "Server listening on 0.0.0.0:7634")

        server.listen(1)
        client = server.accept()[0]
        server.close()
        logger.log(9, "Server closed")

        return client

    @staticmethod
    def send_message(client: socket.socket, message: str = "") -> None:
        client.send(f"HTTP/1.1 200 OK\r\n\r\n{message}".encode())
        client.close()


class OAuth2TokenManager(praw.reddit.BaseTokenManager):
    def __init__(self, config: configparser.ConfigParser, config_location: Path) -> None:
        super().__init__()
        self.config = config
        self.config_location = config_location

    def pre_refresh_callback(self, authorizer: praw.reddit.Authorizer) -> None:
        if authorizer.refresh_token is None:
            if self.config.has_option("DEFAULT", "user_token"):
                authorizer.refresh_token = self.config.get("DEFAULT", "user_token")
                logger.log(9, "Loaded OAuth2 token for authoriser")
            else:
                raise RedditAuthenticationError("No auth token loaded in configuration")

    def post_refresh_callback(self, authorizer: praw.reddit.Authorizer) -> None:
        self.config.set("DEFAULT", "user_token", authorizer.refresh_token)
        with Path(self.config_location).open(mode="w") as file:
            self.config.write(file, space_around_delimiters=True)
        logger.log(9, f"Written OAuth2 token from authoriser to {self.config_location}")
