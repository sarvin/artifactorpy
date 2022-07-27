"""Test suites for Artifactory module"""
import random
import string
import unittest
from unittest.mock import Mock, patch

import src.aql
import src.resource
import src.tools


class Cursor(unittest.TestCase):
    def test_find(self):
        """List of two repositories should be returned"""

        ### Arrange
        base_url = "".join(random.choices(string.ascii_lowercase + string.digits, k=10))
        api_key = "".join(random.choices(string.ascii_lowercase + string.digits, k=10))

        query = {
            "repo": "docker-repository",
            "name": {"$eq":"manifest.json"},
            "stat.downloaded": {"$before":"4y"}}

        response_json = {
            'range': {
                'end_pos': 2,
                'start_pos': 0,
                'total': 2
            },
            'results': [
                {
                    'created': '2018-07-06T20:57:45.614Z',
                    'created_by': 'bud@manley',
                    'modified': '2018-07-06T20:57:45.546Z',
                    'modified_by': 'bud@manley',
                    'name': 'manifest.json',
                    'path': 'product_name/version1/foo',
                    'repo': 'docker',
                    'size': 1576,
                    'type': 'file',
                    'updated': '2018-07-06T20:57:45.546Z'},
                {
                    'created': '2018-07-06T20:57:45.614Z',
                    'created_by': 'bud@manley',
                    'modified': '2018-07-06T20:57:45.546Z',
                    'modified_by': 'bud@manley',
                    'name': 'manifest.json',
                    'path': 'product_name/version2/foo',
                    'repo': 'docker',
                    'size': 1576,
                    'type': 'file',
                    'updated': '2018-07-06T20:57:45.546Z'}]}

        session = Mock()
        session.post.return_value.json.return_value = response_json
        connection = src.tools.Connection(session, base_url)

        cursor = src.aql.FileCursor(connection)
        cursor = cursor.find(query)

        ### Act
        files = [file for file in cursor]

        ### Assert
        self.assertEqual(len(files), 2)
        session.post.assert_called_once_with(
            f'{base_url}/api/search/aql',
            data='items.find({"repo": "docker-repository", "name": {"$eq": "manifest.json"}, "stat.downloaded": {"$before": "4y"}})')
        session.post.return_value.json.assert_called_once()
        for file in files:
            with self.subTest(file=file):
                self.assertIsInstance(file, src.resource.File)

    def test_include(self):
        """List of two repositories should be returned"""

        ### Arrange
        base_url = "".join(random.choices(string.ascii_lowercase + string.digits, k=10))
        api_key = "".join(random.choices(string.ascii_lowercase + string.digits, k=10))

        query = {
            "repo": "docker-dev-local",
            "name": {"$eq":"manifest.json"},
            "stat.downloaded": {"$before":"4y"}}

        response_json = {
            'range': {
                'end_pos': 2,
                'start_pos': 0,
                'total': 2
            },
            'results': [
                {
                    'created': '2018-07-06T20:57:45.614Z',
                    'created_by': 'bud@manley',
                    'modified': '2018-07-06T20:57:45.546Z',
                    'modified_by': 'bud@manley',
                    'name': 'manifest.json',
                    'path': 'product_name/version1/foo',
                    'repo': 'docker',
                    'size': 1576,
                    'type': 'file',
                    'updated': '2018-07-06T20:57:45.546Z'},
                {
                    'created': '2018-07-06T20:57:45.614Z',
                    'created_by': 'bud@manley',
                    'modified': '2018-07-06T20:57:45.546Z',
                    'modified_by': 'bud@manley',
                    'name': 'manifest.json',
                    'path': 'product_name/version2/foo',
                    'repo': 'docker',
                    'size': 1576,
                    'type': 'file',
                    'updated': '2018-07-06T20:57:45.546Z'}]}

        session = Mock()
        session.post.return_value.json.return_value = response_json
        connection = src.tools.Connection(session, base_url)

        cursor = src.aql.FileCursor(connection)
        cursor = cursor.find(query).include(['repo', 'path', 'name'])

        ### Act
        files = [file for file in cursor]

        ### Assert
        self.assertEqual(len(files), 2)
        session.post.assert_called_once_with(
            f'{base_url}/api/search/aql',
            data='items.find({"repo": "docker-dev-local", "name": {"$eq": "manifest.json"}, "stat.downloaded": {"$before": "4y"}}).include("repo", "path", "name")')
        session.post.return_value.json.assert_called_once()
        for file in files:
            with self.subTest(file=file):
                self.assertIsInstance(file, src.resource.File)
