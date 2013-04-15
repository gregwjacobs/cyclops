#!/usr/bin/env python
# -*- coding: utf-8 -*-

_multiprocess_can_split_ = True

from os.path import abspath, join, dirname

from preggy import expect

from cyclops.server import LOGS, ROOT_PATH, DEFAULT_CONFIG_PATH, main

EXPECTED_ROOT_PATH = abspath(join(dirname(__file__), '..'))
EXPECTED_DEFAULT_CONFIG_PATH = join(ROOT_PATH, 'cyclops', 'local.conf')


def test_server_logs_values():
    expect(LOGS).to_include(0)
    expect(LOGS[0]).to_equal("error")

    expect(LOGS).to_include(1)
    expect(LOGS[1]).to_equal("warning")

    expect(LOGS).to_include(2)
    expect(LOGS[2]).to_equal("info")

    expect(LOGS).to_include(3)
    expect(LOGS[3]).to_equal("debug")


def test_paths():
    expect(ROOT_PATH).to_equal(EXPECTED_ROOT_PATH)
    expect(DEFAULT_CONFIG_PATH).to_equal(EXPECTED_DEFAULT_CONFIG_PATH)


class FakeLoop(object):
    def __init__(self):
        self.started = False

    def start(self):
        self.started = True


class FakeServer(object):
    called_with = {}

    def __init__(self, application, xheaders):
        self.application = application
        self.xheaders = xheaders

        FakeServer.called_with['application'] = application
        FakeServer.called_with['xheaders'] = xheaders

    @classmethod
    def forget(cls):
        FakeServer.called_with = {}

    def bind(self, port, ip):
        self.port = port
        self.ip = ip
        self.called_with['port'] = port
        self.called_with['ip'] = ip

    def start(self, procs):
        FakeServer.called_with['procs'] = procs


class App(object):
    called_with = {}

    def __init__(self, config, log_level, debug, main_loop):
        self.config = config
        self.log_level = log_level
        self.debug = debug
        self.main_loop = main_loop

        App.called_with['config'] = config
        App.called_with['log_level'] = log_level
        App.called_with['debug'] = debug
        App.called_with['main_loop'] = main_loop

    @classmethod
    def forget(cls):
        App.called_with = {}


def forget():
    App.forget()
    FakeServer.forget()


def test_main_works_as_expected():
    argv = []
    main_loop = FakeLoop()

    main(args=argv, main_loop=main_loop, app=App, server_impl=FakeServer)

    expect(App.called_with).to_include('config')
    expect(App.called_with).to_include('log_level')
    expect(App.called_with).to_include('debug')
    expect(App.called_with).to_include('main_loop')

    expect(App.called_with['log_level']).to_equal('ERROR')
    expect(App.called_with['debug']).to_be_false()

    expect(main_loop.started).to_be_true()

    expect(FakeServer.called_with).to_include('application')
    expect(FakeServer.called_with['application']).to_be_instance_of(App)
    expect(FakeServer.called_with).to_include('xheaders')
    expect(FakeServer.called_with['xheaders']).to_be_true()

    expect(FakeServer.called_with).to_include('port')
    expect(FakeServer.called_with['port']).to_equal(9999)

    expect(FakeServer.called_with).to_include('ip')
    expect(FakeServer.called_with['ip']).to_equal("0.0.0.0")

    expect(FakeServer.called_with).to_include('procs')
    expect(FakeServer.called_with['procs']).to_equal(1)

    forget()


def test_main_with_debug():
    argv = ['--debug']
    main_loop = FakeLoop()

    main(args=argv, main_loop=main_loop, app=App, server_impl=FakeServer)

    expect(App.called_with).to_include('debug')
    expect(App.called_with['debug']).to_be_true()

    forget()


def test_main_with_port_and_bind():
    argv = ['--port', '7654', '--bind', '1.2.3.4']
    main_loop = FakeLoop()

    main(args=argv, main_loop=main_loop, app=App, server_impl=FakeServer)

    expect(FakeServer.called_with).to_include('port')
    expect(FakeServer.called_with['port']).to_equal(7654)

    expect(FakeServer.called_with).to_include('ip')
    expect(FakeServer.called_with['ip']).to_equal("1.2.3.4")

    forget()
