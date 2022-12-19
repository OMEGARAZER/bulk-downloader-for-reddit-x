#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from bdfr.completion import Completion


@pytest.mark.skipif(sys.platform == "win32", reason="Completions are not currently supported on Windows.")
def test_cli_completion_all(tmp_path: Path):
    with patch("appdirs.user_data_dir", return_value=str(tmp_path)):
        Completion("all").install()
        assert Path.exists(Path(str(tmp_path) + "/bash-completion/completions/bdfr")) == 1
        assert Path.exists(Path(str(tmp_path) + "/fish/vendor_completions.d/bdfr.fish")) == 1
        assert Path.exists(Path(str(tmp_path) + "/zsh/site-functions/_bdfr")) == 1
        Completion("all").uninstall()
        assert Path.exists(Path(str(tmp_path) + "/bash-completion/completions/bdfr")) == 0
        assert Path.exists(Path(str(tmp_path) + "/fish/vendor_completions.d/bdfr.fish")) == 0
        assert Path.exists(Path(str(tmp_path) + "/zsh/site-functions/_bdfr")) == 0


@pytest.mark.skipif(sys.platform == "win32", reason="Completions are not currently supported on Windows.")
def test_cli_completion_bash(tmp_path: Path):
    with patch("appdirs.user_data_dir", return_value=str(tmp_path)):
        Completion("bash").install()
        assert Path.exists(Path(str(tmp_path) + "/bash-completion/completions/bdfr")) == 1
        Completion("bash").uninstall()
        assert Path.exists(Path(str(tmp_path) + "/bash-completion/completions/bdfr")) == 0


@pytest.mark.skipif(sys.platform == "win32", reason="Completions are not currently supported on Windows.")
def test_cli_completion_fish(tmp_path: Path):
    with patch("appdirs.user_data_dir", return_value=str(tmp_path)):
        Completion("fish").install()
        assert Path.exists(Path(str(tmp_path) + "/fish/vendor_completions.d/bdfr.fish")) == 1
        Completion("fish").uninstall()
        assert Path.exists(Path(str(tmp_path) + "/fish/vendor_completions.d/bdfr.fish")) == 0


@pytest.mark.skipif(sys.platform == "win32", reason="Completions are not currently supported on Windows.")
def test_cli_completion_zsh(tmp_path: Path):
    with patch("appdirs.user_data_dir", return_value=str(tmp_path)):
        Completion("zsh").install()
        assert Path.exists(Path(str(tmp_path) + "/zsh/site-functions/_bdfr")) == 1
        Completion("zsh").uninstall()
        assert Path.exists(Path(str(tmp_path) + "/zsh/site-functions/_bdfr")) == 0
