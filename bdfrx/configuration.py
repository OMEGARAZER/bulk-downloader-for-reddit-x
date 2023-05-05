import logging
from argparse import Namespace
from pathlib import Path
from typing import Optional

import click
import yaml

logger = logging.getLogger(__name__)


class Configuration(Namespace):
    def __init__(self) -> None:
        super().__init__()
        self.authenticate = False
        self.config = None
        self.db = False
        self.db_file: Optional[str] = None
        self.directory: str = "."
        self.disable_module: list[str] = []
        self.downvoted: bool = False
        self.exclude_id = []
        self.exclude_id_file = []
        self.file_scheme: str = "{REDDITOR}_{TITLE}_{POSTID}"
        self.filename_restriction_scheme = None
        self.folder_scheme: str = "{SUBREDDIT}"
        self.ignore_user = []
        self.include_id_file = []
        self.limit: Optional[int] = None
        self.link: list[str] = []
        self.log: Optional[str] = None
        self.make_hard_links = False
        self.max_wait_time = None
        self.min_score = None
        self.max_score = None
        self.min_score_ratio = None
        self.max_score_ratio = None
        self.multireddit: list[str] = []
        self.no_dupes: bool = False
        self.opts: Optional[str] = None
        self.saved: bool = False
        self.search: Optional[str] = None
        self.search_existing: bool = False
        self.skip: list[str] = []
        self.skip_domain: list[str] = []
        self.skip_subreddit: list[str] = []
        self.sort: str = "hot"
        self.submitted: bool = False
        self.subscribed: bool = False
        self.subreddit: list[str] = []
        self.time: str = "all"
        self.time_format = None
        self.upvoted: bool = False
        self.user: list[str] = []
        self.verbose: int = 0

    def process_click_arguments(self, context: click.Context) -> None:
        if context.params.get("opts") is not None:
            self.parse_yaml_options(context.params["opts"])
        for arg_key in context.params:
            if not hasattr(self, arg_key):
                logger.warning(f"Ignoring an unknown CLI argument: {arg_key!r}")
                continue
            click_value = context.params[arg_key]
            if click_value is None or click_value == ():
                # don't overwrite with an empty value
                continue
            setattr(self, arg_key, click_value)

    def parse_yaml_options(self, file_path: str) -> None:
        yaml_file_loc = Path(file_path)
        if not yaml_file_loc.exists():
            logger.error(f"No YAML file found at {yaml_file_loc}")
            return
        with yaml_file_loc.open() as file:
            try:
                opts = yaml.safe_load(file)
            except yaml.YAMLError as e:
                logger.error(f"Could not parse YAML options file: {e}")
                return
        for arg_key, yaml_value in opts.items():
            if not hasattr(self, arg_key):
                logger.warning(f"Ignoring an unknown YAML argument: {arg_key!r}")
                continue
            setattr(self, arg_key, yaml_value)
