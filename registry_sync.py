#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
---
name: registry-sync.py
description: Registry Sync - Sync container images between two registries
people:
  developers:
  - name: Marcio Pessoa
    email: marcio.pessoa@gmail.com
"""

import subprocess
import shlex
import sys
import argparse
import json
import requests

from src.log import Log, log


class RegistrySync():
    """ RegistrySync class """

    __version__ = '0.1.0'
    __date__ = '2023-05-25'
    __name = 'registry_sync.py'

    def __init__(self):
        Log().name = self.__name
        Log().verbosity = 'WARNING'
        Log().start()

        self.__parser = None
        self._argparser()

        if len(sys.argv) < 2:  # When no args given, run random game
            print(
                f'{self.__name}: missing registry positional argument\n'
                f"Try '{self.__name} --help' for more information."
            )
            sys.exit()

        args = self.__parser.parse_args()
        self.__timeout = args.timeout
        Log().verbosity = args.verbosity
        log.debug('Source registry: %s', args.source)
        log.debug('Destination registry: %s', args.destination)

        for container in self.get_catalog(args.source):
            for tag in self.get_tags(args.source, container):
                self.copy(args.source, args.destination, container, tag)

    def _argparser(self):
        self.__parser = argparse.ArgumentParser(
            prog='Registry Sync',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            add_help=True,
            usage=(
                f'{self.__name} <source> <destination>\n\n'
            ),
            epilog=(
                'example:\n'
                f'  {self.__name} 192.168.15.1:5000 192.168.15.2:5000\n'
                '\n'
                'Copyleft (c) 2023-2024 Marcio Pessoa\n'
                'License: GPLv3\n'
                'Website: https://github.com/marcio-pessoa/registry_sync\n'
                'Contact: Marcio Pessoa <marcio.pessoa@gmail.com>\n'
            ),
        )
        self.__parser.add_argument('source', help='Source registry')
        self.__parser.add_argument('destination', help='Destination registry')
        self.__parser.add_argument(
            '-v', '--verbosity',
            type=str,
            choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG'],
            default='ERROR',
            help=(
                'verbose mode, options: '
                'CRITICAL, ERROR (default), WARNING, INFO, DEBUG'
            )
        )
        self.__parser.add_argument(
            '-t', '--timeout',
            type=int,
            default=10,
            help='API timeout'
        )
        self.__parser.add_argument(
            '-V', '--version',
            action='version',
            help='show version information and exit',
            version=(f'{self.__name} {self.__version__} {self.__date__}'),
        )

    def get_catalog(self, registry: str) -> list[str]:
        """ Get registry catalog

        Args:
            registry (str): registry address

        Returns:
            list[str]: list of container images
        """
        log.info('Fetching source catalog...')

        prefix: str = 'http://'
        suffix: str = '/v2/_catalog'
        uri: str = f'{prefix}{registry}{suffix}'

        response = requests.get(uri, timeout=self.__timeout)
        result = json.loads(response.text)

        if 'repositories' not in result:
            log.error('Failed to fetch catalog')
            sys.exit(1)

        log.debug(json_pretty(result['repositories']))

        return result['repositories']

    def get_tags(self, registry: str, container: str) -> list[str]:
        """ Get container image tags

        Args:
            registry (str): registry address
            container (str): container image name

        Returns:
            list[str]: list of tags
        """
        log.info('Fetching source container image tags for %s...', container)

        prefix: str = 'http://'
        suffix: str = f'/v2/{container}/tags/list'
        uri: str = f'{prefix}{registry}{suffix}'

        response = requests.get(uri, timeout=self.__timeout)
        result = json.loads(response.text)

        if 'tags' not in result:
            log.error('Failed to fetch tags')
            sys.exit(1)

        log.debug(json_pretty(result['tags']))

        return result['tags']

    def copy(self, source: str, destination: str,
             container: str, tag: str) -> subprocess.CompletedProcess:
        """ Copy container image tag between registries

        Args:
            source (str): source registry
            destination (str): destination registry
            container (str): container image name
            tag (str): container image tag

        Returns:
            CompletedProcess: OK when .returncode = 0
        """
        log.info('Syncing %s:%s', container, tag)

        preffix = 'docker://'
        copy_cmd = 'skopeo copy'
        args = '--src-tls-verify=false --dest-tls-verify=false'
        cmd = f'{copy_cmd} {args} ' \
              f'{preffix}{source}/{container}:{tag} ' \
              f'{preffix}{destination}/{container}:{tag}'
        log.debug('Running: %s', cmd)

        result = subprocess.run(shlex.split(cmd), shell=False, check=True)
        if result.returncode != 0:
            log.error('Failed')

        return result


def json_pretty(data: dict) -> str:
    """ Pretty output JSON data

    Args:
        data (dict): dictionary to be formmated as JSON

    Returns:
        str: fancy JSON
    """
    return json.dumps(data, indent=2, separators=(", ", ": "))


if __name__ == '__main__':
    RegistrySync()
