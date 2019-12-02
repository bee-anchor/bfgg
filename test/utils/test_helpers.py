from bfgg.utils.helpers import ip_to_log_filename, create_or_empty_folder


def test_ip_to_log_filename():
    assert "1_1_1_1.log" == ip_to_log_filename("1.1.1.1")

def test_create_or_empty_folder_test_path_doesnt_exist(mocker):
    os_mock = mocker.patch('bfgg.utils.helpers.os')
    os_mock.path.exists.return_value = False

    create_or_empty_folder("path/to/stuff")

    os_mock.path.exists.assert_called_once()
    os_mock.mkdir.assert_called_once_with("path/to/stuff")

def test_create_or_empty_folder_test_path_folder_exists(mocker):
    os_mock = mocker.patch('bfgg.utils.helpers.os', **{
        'listdir.return_value': ["A", "B", "C"],
        'path.exists.return_value': True,
        'path.isfile.side_effect': [True, False, True],
        'path.isdir.return_value': True
    })
    shutil_mock = mocker.patch('bfgg.utils.helpers.shutil.rmtree')

    create_or_empty_folder("path/to/stuff")

    os_mock.listdir.assert_called_once()
    os_mock.path.isdir.assert_called_once()
    assert 2 == os_mock.remove.call_count
    shutil_mock.assert_called_once()