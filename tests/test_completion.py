import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from bdfrx.completion import Completion


@pytest.mark.skipif(sys.platform == "win32", reason="Completions are not currently supported on Windows.")
def test_cli_completion_all(tmp_path: Path):
    tmp_path = str(tmp_path)
    with patch("appdirs.user_data_dir", return_value=tmp_path):
        Completion("all").install()
        assert Path(tmp_path + "/bash-completion/completions/bdfrx").exists()
        assert Path(tmp_path + "/fish/vendor_completions.d/bdfrx.fish").exists()
        assert Path(tmp_path + "/zsh/site-functions/_bdfrx").exists()
        Completion("all").uninstall()
        assert not Path(tmp_path + "/bash-completion/completions/bdfrx").exists()
        assert not Path(tmp_path + "/fish/vendor_completions.d/bdfrx.fish").exists()
        assert not Path(tmp_path + "/zsh/site-functions/_bdfrx").exists()


@pytest.mark.skipif(sys.platform == "win32", reason="Completions are not currently supported on Windows.")
def test_cli_completion_bash(tmp_path: Path):
    tmp_path = str(tmp_path)
    with patch("appdirs.user_data_dir", return_value=tmp_path):
        Completion("bash").install()
        assert Path(tmp_path + "/bash-completion/completions/bdfrx").exists()
        Completion("bash").uninstall()
        assert not Path(tmp_path + "/bash-completion/completions/bdfrx").exists()


@pytest.mark.skipif(sys.platform == "win32", reason="Completions are not currently supported on Windows.")
def test_cli_completion_fish(tmp_path: Path):
    tmp_path = str(tmp_path)
    with patch("appdirs.user_data_dir", return_value=tmp_path):
        Completion("fish").install()
        assert Path(tmp_path + "/fish/vendor_completions.d/bdfrx.fish").exists()
        Completion("fish").uninstall()
        assert not Path(tmp_path + "/fish/vendor_completions.d/bdfrx.fish").exists()


@pytest.mark.skipif(sys.platform == "win32", reason="Completions are not currently supported on Windows.")
def test_cli_completion_zsh(tmp_path: Path):
    tmp_path = str(tmp_path)
    with patch("appdirs.user_data_dir", return_value=tmp_path):
        Completion("zsh").install()
        assert Path(tmp_path + "/zsh/site-functions/_bdfrx").exists()
        Completion("zsh").uninstall()
        assert not Path(tmp_path + "/zsh/site-functions/_bdfrx").exists()
