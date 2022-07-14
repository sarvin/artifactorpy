"""Test suites for Artifactory module"""
import random
import string
import unittest
from unittest.mock import patch

import src.artifactory
import src.resource
import src.tools


class ArtifactsAndStorage(unittest.TestCase):
    """Test suite for artifacts and storage"""

    def test_init(self):
        """ArtifactsAndStorage object is properly initialized"""
        ### Arrange
        base_url = "".join(random.choices(string.ascii_lowercase + string.digits, k=10))
        api_key = "".join(random.choices(string.ascii_lowercase + string.digits, k=10))

        ### Act
        artifactory_api = src.artifactory.ArtifactsAndStorage(base_url, api_key)

        ### Assert
        self.assertIsInstance(artifactory_api, src.artifactory.ArtifactsAndStorage)

    @patch('src.artifactory.requests')
    def test_get_directory(self, requests):
        """When a directory is requested a directory object is returned"""

        ### Arrange
        base_url = "".join(random.choices(string.ascii_lowercase + string.digits, k=10))
        api_key = "".join(random.choices(string.ascii_lowercase + string.digits, k=10))
        repo_key = "".join(random.choices(string.ascii_lowercase + string.digits, k=3))
        path = "".join(random.choices(string.ascii_lowercase + string.digits, k=3))

        response_json = {
            'repo': repo_key,
            'path': path,
            'created': '2017-07-17T18:03:29.959Z',
            'lastModified': '2017-07-17T18:03:29.959Z',
            'lastUpdated': '2017-07-17T18:03:29.959Z',
            'children': [
                {'uri': f'/{path}/Child.Folder', 'folder': True},
                {'uri': f'/{path}/Child.File.1.10.0.nupkg', 'folder': False}],
            'uri': f'https://{base_url}/artifactory/api/storage/{repo_key}/{path}'}

        session = requests.Session.return_value
        session.get.return_value.json.return_value = response_json

        artifactory_api = src.artifactory.ArtifactsAndStorage(base_url, api_key)

        ### Act
        directory = artifactory_api.get_directory(repo_key, path)


        ### Assert
        self.assertIsInstance(directory, src.resource.Directory)

    @patch('src.artifactory.requests')
    def test_get_repositories(self, requests):
        """List of two repositories should be returned"""

        ### Arrange
        base_url = "".join(random.choices(string.ascii_lowercase + string.digits, k=10))
        api_key = "".join(random.choices(string.ascii_lowercase + string.digits, k=10))

        response_json = [
            {
                'description': 'Fake docker registry',
                'key': 'docker',
                'packageType': 'Generic',
                'type': 'LOCAL',
                'url': f'{base_url}/artifactory/docker'},
            {
                'key': 'debian',
                'packageType': 'Debian',
                'type': 'LOCAL',
                'url': f'{base_url}/artifactory/debian'}]

        session = requests.Session.return_value
        session.get.return_value.json.return_value = response_json

        artifactory_api = src.artifactory.ArtifactsAndStorage(base_url, api_key)

        ### Act
        repositories = artifactory_api.get_repositories()


        ### Assert
        self.assertEqual(len(repositories), 2)
        for repository in repositories:
            with self.subTest(repository=repository):
                self.assertIsInstance(repository, src.resource.Repository)
