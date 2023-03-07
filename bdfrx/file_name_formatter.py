#!/usr/bin/env python3

import datetime
import logging
import platform
import re
import subprocess
from pathlib import Path
from typing import Optional, Union

from praw.models import Comment, Submission

from bdfrx.exceptions import BulkDownloaderException
from bdfrx.resource import Resource

logger = logging.getLogger(__name__)


class FileNameFormatter:
    key_terms = (
        "date",
        "flair",
        "postid",
        "redditor",
        "subreddit",
        "title",
        "upvotes",
    )
    WINDOWS_MAX_PATH_LENGTH = 260
    LINUX_MAX_PATH_LENGTH = 4096

    def __init__(
        self,
        file_format_string: str,
        directory_format_string: str,
        time_format_string: str,
        restriction_scheme: Optional[str] = None,
    ) -> None:
        if not self.validate_string(file_format_string):
            raise BulkDownloaderException(f"{file_format_string!r} is not a valid format string")
        self.file_format_string = file_format_string
        self.directory_format_string: list[str] = directory_format_string.split("/")
        self.time_format_string = time_format_string
        self.restiction_scheme = restriction_scheme.lower().strip() if restriction_scheme else None
        if self.restiction_scheme == "windows":
            self.max_path = self.WINDOWS_MAX_PATH_LENGTH
        else:
            self.max_path = self.find_max_path_length()

    def _format_name(self, submission: Union[Comment, Submission], format_string: str) -> str:
        if isinstance(submission, Submission):
            attributes = self._generate_name_dict_from_submission(submission)
        elif isinstance(submission, Comment):
            attributes = self._generate_name_dict_from_comment(submission)
        else:
            raise BulkDownloaderException(f"Cannot name object {type(submission).__name__}")
        result = format_string
        for key in attributes.keys():
            if re.search(rf"(?i).*{{{key}}}.*", result):
                key_value = str(attributes.get(key, "unknown"))
                key_value = FileNameFormatter._convert_unicode_escapes(key_value)
                key_value = key_value.replace("\\", "\\\\")
                result = re.sub(rf"(?i){{{key}}}", key_value, result)

        result = result.replace("/", "")

        if self.restiction_scheme is None:
            if platform.system() == "Windows":
                result = FileNameFormatter._format_for_windows(result)
        elif self.restiction_scheme == "windows":
            logger.debug("Forcing Windows-compatible filenames")
            result = FileNameFormatter._format_for_windows(result)
        return result

    @staticmethod
    def _convert_unicode_escapes(in_string: str) -> str:
        pattern = re.compile(r"(\\u\d{4})")
        matches = re.search(pattern, in_string)
        if matches:
            for match in matches.groups():
                converted_match = bytes(match, "utf-8").decode("unicode-escape")
                in_string = in_string.replace(match, converted_match)
        return in_string

    def _generate_name_dict_from_submission(self, submission: Submission) -> dict:
        submission_attributes = {
            "title": submission.title,
            "subreddit": submission.subreddit.display_name,
            "redditor": submission.author.name if submission.author else "DELETED",
            "postid": submission.id,
            "upvotes": submission.score,
            "flair": submission.link_flair_text,
            "date": self._convert_timestamp(submission.created_utc),
        }
        return submission_attributes

    def _convert_timestamp(self, timestamp: float) -> str:
        input_time = datetime.datetime.fromtimestamp(timestamp)
        if self.time_format_string.upper().strip() == "ISO":
            return input_time.isoformat()
        return input_time.strftime(self.time_format_string)

    def _generate_name_dict_from_comment(self, comment: Comment) -> dict:
        comment_attributes = {
            "title": comment.submission.title,
            "subreddit": comment.subreddit.display_name,
            "redditor": comment.author.name if comment.author else "DELETED",
            "postid": comment.id,
            "upvotes": comment.score,
            "flair": "",
            "date": self._convert_timestamp(comment.created_utc),
        }
        return comment_attributes

    def format_path(
        self,
        resource: Resource,
        destination_directory: Path,
        index: Optional[int] = None,
    ) -> Path:
        subfolder = Path(
            destination_directory,
            *[self._format_name(resource.source_submission, part) for part in self.directory_format_string],
        )
        index = f"_{index}" if index else ""
        if not resource.extension:
            raise BulkDownloaderException(f"Resource from {resource.url} has no extension")
        file_name = str(self._format_name(resource.source_submission, self.file_format_string))

        file_name = re.sub(r"\n", " ", file_name)

        if not re.match(r".*\.$", file_name) and not re.match(r"^\..*", resource.extension):
            ending = index + "." + resource.extension
        else:
            ending = index + resource.extension

        try:
            file_path = self.limit_file_name_length(file_name, ending, subfolder)
        except TypeError:
            raise BulkDownloaderException(f"Could not determine path name: {subfolder}, {index}, {resource.extension}")
        return file_path

    def limit_file_name_length(self, filename: str, ending: str, root: Path) -> Path:
        root = root.resolve().expanduser()
        possible_id = re.search(r"((?:_\w{6})?$)", filename)
        if possible_id:
            ending = possible_id.group(1) + ending
            filename = filename[: possible_id.start()]
        max_path = self.max_path
        max_file_part_length_chars = 255 - len(ending)
        max_file_part_length_bytes = 255 - len(ending.encode())
        max_path_length = max_path - len(ending) - len(str(root)) - 1

        out = Path(root, filename + ending)
        safe_ending = re.match(r".*\..*", ending)
        while any(
            [
                len(filename) > max_file_part_length_chars,
                len(filename.encode()) > max_file_part_length_bytes,
                len(str(out)) > max_path_length,
            ]
        ):
            filename = filename[:-1]
            if not safe_ending and filename[-1] != ".":
                filename = filename[:-1] + "."
            out = Path(root, filename + ending)

        return out

    @staticmethod
    def find_max_path_length() -> int:
        try:
            return int(subprocess.check_output(["getconf", "PATH_MAX", "/"]))
        except (ValueError, subprocess.CalledProcessError, OSError):
            if platform.system() == "Windows":
                return FileNameFormatter.WINDOWS_MAX_PATH_LENGTH
            else:
                return FileNameFormatter.LINUX_MAX_PATH_LENGTH

    def format_resource_paths(
        self,
        resources: list[Resource],
        destination_directory: Path,
    ) -> list[tuple[Path, Resource]]:
        out = []
        if len(resources) == 1:
            try:
                out.append((self.format_path(resources[0], destination_directory), resources[0]))
            except BulkDownloaderException as e:
                logger.error(f"Could not generate file path for resource {resources[0].url}: {e}")
                logger.exception("Could not generate file path")
        else:
            for i, res in enumerate(resources, start=1):
                logger.log(9, f"Formatting filename with index {i}")
                try:
                    out.append((self.format_path(res, destination_directory, i), res))
                except BulkDownloaderException as e:
                    logger.error(f"Could not generate file path for resource {res.url}: {e}")
                    logger.exception("Could not generate file path")
        return out

    @staticmethod
    def validate_string(test_string: str) -> bool:
        if not test_string:
            return False
        result = any([f"{{{key}}}" in test_string.lower() for key in FileNameFormatter.key_terms])
        if result:
            if "POSTID" not in test_string:
                logger.warning(
                    "Some files might not be downloaded due to name conflicts as filenames are"
                    " not guaranteed to be be unique without {POSTID}"
                )
            return True
        return False

    @staticmethod
    def _format_for_windows(input_string: str) -> str:
        invalid_characters = r'<>:"\/|?*'
        for char in invalid_characters:
            input_string = input_string.replace(char, "")
        input_string = FileNameFormatter._strip_emojis(input_string)
        return input_string

    @staticmethod
    def _strip_emojis(input_string: str) -> str:
        result = input_string.encode("ascii", errors="ignore").decode("utf-8")
        return result
