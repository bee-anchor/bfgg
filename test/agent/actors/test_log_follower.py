from bfgg.agent.actors.log_follower import LogFollower, os

results_folder = '/results'

def test_log_follower_get_current_logfile(mocker):
    folders = ['A', 'B', 'C', 'D']
    os_mock = mocker.patch('bfgg.agent.actors.log_follower.os', **{
        'listdir.return_value': folders,
        'path.isdir.side_effect': [True, True, False, False],
        'path.getmtime.return_value': 5,
        'path.join': os.path.join
    })
    mock_max = mocker.patch('bfgg.agent.actors.log_follower.max', return_value=folders[0])
    mocker.patch('bfgg.agent.actors.log_follower.datetime', **{
        'now.return_value.timestamp.return_value': 5
    })

    result = LogFollower(results_folder)._get_current_logfile()

    mock_max.assert_called_once_with(list(map(lambda x: f'{results_folder}/{x}', folders[:2])), key=os_mock.path.getmtime)
    assert f'{folders[0]}/simulation.log' == result


def test_log_follower_get_current_logfile_folder_is_old(mocker):
    folders = ['A', 'B', 'C', 'D']
    mocker.patch('bfgg.agent.actors.log_follower.os', **{
        'listdir.return_value': folders,
        'path.isdir.side_effect': [True, True, False, False, True, True, False, False],
        'path.getmtime.side_effect': [10, 5],
        'path.join': os.path.join
    })
    mock_max = mocker.patch('bfgg.agent.actors.log_follower.max', return_value=folders[0])
    mocker.patch('bfgg.agent.actors.log_follower.datetime', **{
        'now.return_value.timestamp.side_effect': [20, 5]
    })

    result = LogFollower(results_folder)._get_current_logfile()

    assert 2 == mock_max.call_count
    assert f'{folders[0]}/simulation.log' == result


def test_log_follower_get_current_logfile_folder_doesnt_exist(mocker):
    folders = ['A', 'B', 'C', 'D']
    mocker.patch('bfgg.agent.actors.log_follower.os', **{
        'listdir.side_effect': folders,
        'path.isdir.side_effect': [True, True, False, False],
        'path.getmtime.side_effect': [10, 5],
        'path.join': os.path.join
    })
    mock_max = mocker.patch('bfgg.agent.actors.log_follower.max', side_effect=[ValueError, folders[0]])
    mocker.patch('bfgg.agent.actors.log_follower.datetime', **{
        'now.return_value.timestamp.return_value': 5
    })

    result = LogFollower(results_folder)._get_current_logfile()

    assert 2 == mock_max.call_count
    assert f'{folders[0]}/simulation.log' == result
