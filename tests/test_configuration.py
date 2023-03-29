from unittest.mock import MagicMock

import pytest

from bdfrx.configuration import Configuration


@pytest.mark.parametrize(
    "arg_dict",
    (
        {"directory": "test_dir"},
        {
            "directory": "test_dir",
            "no_dupes": True,
        },
    ),
)
def test_process_click_context(arg_dict: dict):
    test_config = Configuration()
    test_context = MagicMock()
    test_context.params = arg_dict
    test_config.process_click_arguments(test_context)
    test_config = vars(test_config)
    assert all(test_config[arg] == arg_dict[arg] for arg in arg_dict)


def test_yaml_file_read():
    yaml_file = "./tests/yaml_test_configuration.yaml"
    test_config = Configuration()
    test_config.parse_yaml_options(yaml_file)
    assert test_config.subreddit == ["EarthPorn", "TwoXChromosomes", "Mindustry"]
    assert test_config.sort == "new"
    assert test_config.limit == 10
