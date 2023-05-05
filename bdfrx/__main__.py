#!/usr/bin/env python3

import logging
import sys

import click
import requests

from bdfrx import __version__
from bdfrx.completion import Completion
from bdfrx.configuration import Configuration
from bdfrx.downloader import RedditDownloader

logger = logging.getLogger()

_common_options = [
    click.argument("directory", type=str),
    click.option("--authenticate", is_flag=True, default=None),
    click.option("--config", type=str, default=None),
    click.option("--db", is_flag=True, default=None),
    click.option("--db-file", type=str, default=None),
    click.option("--disable-module", type=str, multiple=True, default=None),
    click.option("--downvoted", is_flag=True, default=None),
    click.option("--exclude-id", type=str, multiple=True, default=None),
    click.option("--exclude-id-file", type=str, multiple=True, default=None),
    click.option("--file-scheme", type=str, default=None),
    click.option("--filename-restriction-scheme", type=click.Choice(("linux", "windows")), default=None),
    click.option("--folder-scheme", type=str, default=None),
    click.option("--ignore-user", type=str, multiple=True, default=None),
    click.option("--include-id-file", type=str, multiple=True, default=None),
    click.option("-L", "--limit", type=int, default=None),
    click.option("-l", "--link", type=str, multiple=True, default=None),
    click.option("--log", type=str, default=None),
    click.option("-m", "--multireddit", type=str, multiple=True, default=None),
    click.option("--opts", type=str, default=None),
    click.option("--saved", is_flag=True, default=None),
    click.option("--search", type=str, default=None),
    click.option(
        "-S",
        "--sort",
        type=click.Choice(("hot", "top", "new", "controversial", "rising", "relevance")),
        default=None,
    ),
    click.option("--submitted", is_flag=True, default=None),
    click.option("-s", "--subreddit", type=str, multiple=True, default=None),
    click.option("--subscribed", is_flag=True, default=None),
    click.option("-t", "--time", type=click.Choice(("all", "hour", "day", "week", "month", "year")), default=None),
    click.option("--time-format", type=str, default=None),
    click.option("--upvoted", is_flag=True, default=None),
    click.option("-u", "--user", type=str, multiple=True, default=None),
    click.option("-v", "--verbose", count=True, default=None),
]

_downloader_options = [
    click.option("--make-hard-links", is_flag=True, default=None),
    click.option("--max-wait-time", type=int, default=None),
    click.option("--min-score", type=int, default=None),
    click.option("--max-score", type=int, default=None),
    click.option("--min-score-ratio", type=float, default=None),
    click.option("--max-score-ratio", type=float, default=None),
    click.option("--no-dupes", is_flag=True, default=None),
    click.option("--search-existing", is_flag=True, default=None),
    click.option("--skip", multiple=True, default=None),
    click.option("--skip-domain", multiple=True, default=None),
    click.option("--skip-subreddit", multiple=True, default=None),
]


def _add_options(opts: list):  # noqa: ANN202
    def wrap(func):  # noqa: ANN001,ANN202
        for opt in opts:
            func = opt(func)
        return func

    return wrap


def _check_version(context: click.core.Context, _param, value: bool) -> None:  # noqa: FBT001
    if not value or context.resilient_parsing:
        return
    current = __version__
    try:
        latest = requests.get("https://pypi.org/pypi/bdfrx/json", timeout=16).json()["info"]["version"]
        print(f"You are currently using v{current} the latest is v{latest}")
    except TimeoutError:
        logger.exception(f"Timeout reached fetching current version from Pypi - BDFRx v{current}")
        raise
    context.exit()


@click.group()
@click.help_option("-h", "--help")
@click.option(
    "--version",
    is_flag=True,
    is_eager=True,
    expose_value=False,
    callback=_check_version,
    help="Check version and exit.",
)
def cli() -> None:
    """BDFRx is used to download content from Reddit."""


@cli.command("download")
@_add_options(_common_options)
@_add_options(_downloader_options)
@click.help_option("-h", "--help")
@click.pass_context
def cli_download(context: click.Context, **_) -> None:
    """Used to download content posted to Reddit."""
    config = Configuration()
    config.process_click_arguments(context)
    silence_module_loggers()
    stream = make_console_logging_handler(config.verbose)
    try:
        reddit_downloader = RedditDownloader(config, [stream])
        reddit_downloader.download()
    except Exception:
        logger.exception(f"Downloader exited unexpectedly - BDFRx Downloader v{__version__}")
        raise
    else:
        logger.info(f"Program complete - BDFRx Downloader v{__version__}")


@cli.command("completion")
@click.argument("shell", type=click.Choice(("all", "bash", "fish", "zsh"), case_sensitive=False), default="all")
@click.help_option("-h", "--help")
@click.option("-u", "--uninstall", is_flag=True, default=False, help="Uninstall completion")
@click.pass_context
def cli_completion(context: click.Context, **_) -> None:
    """\b
    Installs shell completions for BDFRx.
    Options: all, bash, fish, zsh
    Default: all"""
    shell = context.params["shell"].lower()
    if sys.platform == "win32":
        print("Completions are not currently supported on Windows.")
        return
    if context.params["uninstall"] and click.confirm(f"Would you like to uninstall {shell} completions for BDFRx"):
        Completion(shell).uninstall()
        return
    if shell not in ("all", "bash", "fish", "zsh"):
        print(f"{shell!r} is not a valid option.")
        print("Options: all, bash, fish, zsh")
        return
    if click.confirm(f"Would you like to install {shell} completions for BDFRx"):
        Completion(shell).install()


def make_console_logging_handler(verbosity: int) -> logging.StreamHandler:
    class StreamExceptionFilter(logging.Filter):
        def filter(self, record: logging.LogRecord) -> bool:  # noqa: A003
            return not (record.levelno == logging.ERROR and record.exc_info)

    logger.setLevel(1)
    stream = logging.StreamHandler(sys.stdout)
    stream.addFilter(StreamExceptionFilter())

    formatter = logging.Formatter("[%(asctime)s - %(name)s - %(levelname)s] - %(message)s")
    stream.setFormatter(formatter)

    if verbosity <= 0:
        stream.setLevel(logging.INFO)
    elif verbosity == 1:
        stream.setLevel(logging.DEBUG)
    else:
        stream.setLevel(9)
    return stream


def silence_module_loggers() -> None:
    logging.getLogger("praw").setLevel(logging.CRITICAL)
    logging.getLogger("prawcore").setLevel(logging.CRITICAL)
    logging.getLogger("urllib3").setLevel(logging.CRITICAL)


if __name__ == "__main__":
    cli()
