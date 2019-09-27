import argparse


def bfg_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--controller-host', default='localhost', help='IP/address running controller service')
    parser.add_argument('-r', '--registrator-port', default='9500', help='port Registrator service is listening on')
    parser.add_argument('-t', '--task-port', default='9501', help='port TaskPusher service is listening on')
    parser.add_argument('-p', '--poller-port', default='9502', help='port AgentPoller service is listening on')
    return parser
