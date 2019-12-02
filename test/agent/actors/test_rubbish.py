# def test_runner_handle_process(mocker):
#     mock_subprocess = mocker.patch('bfgg.agent.actors.gatling_runner.subprocess', autospec=True, **{
#         'stdout': mocker.PropertyMock()
#     })
#     mock_futures = mocker.patch('bfgg.agent.actors.gatling_runner.futures', autospec=True, **{
#         'ThreadPoolExecutor.return_value.submit.return_value.result.return_value': b'Success!'
#     })
#     #mocker.patch.object('bfgg.agent.actors.gatling_runner.TestRunner', 'is_running')
#    # m = mocker.patch('bfgg.agent.actors.gatling_runner.TestRunner.is_running', new_callable=mocker.PropertyMock(side_effect=[True, False]))
#    #  m = mocker.patch('bfgg.agent.actors.gatling_runner.TestRunner.is_running',
#    #                   new_callable=mocker.PropertyMock(side_effect=[True, False]))
#     mocker.patch.object(TestRunner, 'is_running', side_effect=[True, False])
#
#    # m.side_effect = [True, False]
#   #  mocker.PropertyMock('bfgg.agent.actors.gatling_runner.TestRunner.is_running')
#     # mock_test_running = mocker.patch.object('bfgg.agent.actors.gatling_runner.TestRunner', 'is_running')
#     # mock_test_running.return_value.is_running.return_value=mocker.PropertyMock(return_value=True)
#     result = TestRunner(gatling_location, tests_location, results_folder, project, test,
#                            java_opts)
#    # mocker.patch('bfgg.agent.actors.gatling_runner.TestRunner.is_running', return_value=True)
#     result._handle_process(mock_subprocess)
#
#     # assert mock_subprocess.Popen.return_value == result
#
#   #  mocker.patch.multiple('bfgg.agent.actors.gatling_runner.TestRunner', is_running=False)