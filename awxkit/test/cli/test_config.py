import os
import json
import pytest
from requests.exceptions import ConnectionError

from awxkit.cli import CLI
from awxkit import config
from awxkit.cli.format import get_config_credentials


def test_host_from_environment():
    cli = CLI()
    cli.parse_args(
        ['awx'],
        env={'TOWER_HOST': 'https://xyz.local'}
    )
    with pytest.raises(ConnectionError):
        cli.connect()
    assert config.base_url == 'https://xyz.local'

def test_host_from_argv():
    cli = CLI()
    cli.parse_args(['awx', '--conf.host', 'https://xyz.local'])
    with pytest.raises(ConnectionError):
        cli.connect()
    assert config.base_url == 'https://xyz.local'

def test_username_and_password_from_environment():
    cli = CLI()
    cli.parse_args(
        ['awx'],
        env={
            'TOWER_USERNAME': 'mary',
            'TOWER_PASSWORD': 'secret'
        }
    )
    with pytest.raises(ConnectionError):
        cli.connect()

    assert config.credentials.default.username == 'mary'
    assert config.credentials.default.password == 'secret'

def test_username_and_password_argv():
    cli = CLI()
    cli.parse_args([
        'awx', '--conf.username', 'mary', '--conf.password', 'secret'
    ])
    with pytest.raises(ConnectionError):
        cli.connect()

    assert config.credentials.default.username == 'mary'
    assert config.credentials.default.password == 'secret'

def test_config_precedence():
    cli = CLI()
    cli.parse_args(
        [
            'awx', '--conf.username', 'mary', '--conf.password', 'secret'
        ],
        env={
            'TOWER_USERNAME': 'IGNORE',
            'TOWER_PASSWORD': 'IGNORE'
        }
    )
    with pytest.raises(ConnectionError):
        cli.connect()

    assert config.credentials.default.username == 'mary'
    assert config.credentials.default.password == 'secret'

def test_config_file_precedence():
    """Ignores AWXKIT_CREDENTIAL_FILE if cli args are set"""
    os.mkdir('/tmp/awx-test/')
    with open('/tmp/awx-test/config.json', 'w') as f:
        json.dump({
            'default': {
                'username': 'IGNORE',
                'password': 'IGNORE'
            }
        }, f)

    cli = CLI()
    cli.parse_args(
        [
            'awx', '--conf.username', 'mary', '--conf.password', 'secret'
        ],
        env={
            'AWXKIT_CREDENTIAL_FILE': '/tmp/awx-test/config.json',
        }
    )
    with pytest.raises(ConnectionError):
        cli.connect()

    assert config.credentials.default.username == 'mary'
    assert config.credentials.default.password == 'secret'

def test_config_file_precedence_2():
    """Ignores AWXKIT_CREDENTIAL_FILE if TOWER_* vars are set."""
    os.mkdir('/tmp/awx-test/')
    with open('/tmp/awx-test/config.json', 'w') as f:
        json.dump({
            'default': {
                'username': 'IGNORE',
                'password': 'IGNORE'
            }
        }, f)

    cli = CLI()
    cli.parse_args(
        ['awx'],
        env={
            'AWXKIT_CREDENTIAL_FILE': '/tmp/awx-test/config.json',
            'TOWER_USERNAME': 'mary',
            'TOWER_PASSWORD': 'secret'
        }
    )
    with pytest.raises(ConnectionError):
        cli.connect()

    assert config.credentials.default.username == 'mary'
    assert config.credentials.default.password == 'secret'

def test_config_file():
    """Reads username and password from AWXKIT_CREDENTIAL_FILE."""
    os.mkdir('/tmp/awx-test/')
    with open('/tmp/awx-test/config.json', 'w') as f:
        json.dump({
            'default': {
                'username': 'mary',
                'password': 'secret'
            }
        }, f)

    cli = CLI()
    cli.parse_args(
        ['awx'],
        env={
            'AWXKIT_CREDENTIAL_FILE': '/tmp/awx-test/config.json',
        }
    )
    with pytest.raises(ConnectionError):
        cli.connect()

    assert config.credentials.default.username == 'mary'
    assert config.credentials.default.password == 'secret'
