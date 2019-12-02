from queue import Empty

from bfgg.agent.actors.status_poller import StatusPoller
from bfgg.utils.statuses import Statuses


def test_status_poller_get_latest_status(mocker):
    new_state = {
        'status': Statuses.TEST_STOPPED,
        'cloned_repos': {'b'},
        'test_running': 'Test',
        'extra_info': 'interesting stuff'

    }
    mocker.patch('bfgg.agent.actors.status_poller.STATE_QUEUE', **{
        'get_nowait.side_effect': [new_state,Empty]
    })

    status_poller = StatusPoller()
    status_poller.state.attributes = {
        'status': Statuses.AVAILABLE,
        'cloned_repos': {'a'},
        'test_running': 'None',
        'extra_info': 'None'
    }
    status_poller._get_latest_status()

    expected = {
        'status': Statuses.TEST_STOPPED,
        'cloned_repos': {'a', 'b'},
        'test_running': 'Test',
        'extra_info': 'interesting stuff'
    }

    assert expected == status_poller.state.attributes
