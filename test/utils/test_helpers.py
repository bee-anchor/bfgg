from bfgg.utils.helpers import create_or_empty_results_folder, ip_to_log_filename


def test_ip_to_log_filename():
    assert "1_1_1_1.log" == ip_to_log_filename("1.1.1.1")


def test_create_or_empty_folder_test_path_doesnt_exist(mocker):
    os_mock = mocker.patch("bfgg.utils.helpers.os")
    os_mock.path.exists.return_value = False
    os_mock.path.join.return_value = "path/to/stuff/ungrouped"

    create_or_empty_results_folder("path/to/stuff", "ungrouped")

    assert os_mock.path.exists.call_count == 2
    os_mock.mkdir.assert_has_calls(
        [mocker.call("path/to/stuff"), mocker.call("path/to/stuff/ungrouped")]
    )


def test_create_or_empty_folder_test_path_folder_exists(mocker):
    os_mock = mocker.patch(
        "bfgg.utils.helpers.os",
        **{
            "path.join.return_value": "path/to/stuff/ungrouped",
            "path.exists.return_value": True,
        }
    )
    shutil_mock = mocker.patch("bfgg.utils.helpers.shutil.rmtree")

    create_or_empty_results_folder("path/to/stuff", "ungrouped")

    shutil_mock.assert_called_once()
    os_mock.mkdir.assert_called_once_with("path/to/stuff/ungrouped")
