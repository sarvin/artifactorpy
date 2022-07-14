import datetime
import random
import string
import unittest
from unittest.mock import Mock

import src.resource
import src.tools


class Directory(unittest.TestCase):
    def test_init(self):
        ### Arrange
        base_url = "".join(random.choices(string.ascii_lowercase + string.digits, k=10))
        repo_key = "".join(random.choices(string.ascii_lowercase + string.digits, k=3))
        path = repo_key = "".join(random.choices(string.ascii_lowercase + string.digits, k=3))

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

        session = Mock()
        session.get.return_value.json.return_value = response_json
        connection = src.tools.Connection(session, base_url)

        ### Act
        directory = src.resource.Directory(connection, repo_key, path)

        ### Assert
        self.assertIsInstance(directory, src.resource.Directory)

    def test_children(self):
        ### Arrange
        base_url = "".join(random.choices(string.ascii_lowercase + string.digits, k=10))
        repo_key = "".join(random.choices(string.ascii_lowercase + string.digits, k=3))
        path = repo_key = "".join(random.choices(string.ascii_lowercase + string.digits, k=3))

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

        session = Mock()
        session.get.return_value.json.return_value = response_json
        connection = src.tools.Connection(session, base_url)

        directory = src.resource.Directory(connection, repo_key, path)

        ### Act
        children = directory.children()

        ### Assert
        self.assertEqual(len(children), 2)
        session.get.return_value.json.assert_called_once()

class File(unittest.TestCase):
    """Test cases for the File class"""
    def test_init(self):
        ### Arrange
        base_url = "".join(random.choices(string.ascii_lowercase + string.digits, k=10))
        repo_key = "".join(random.choices(string.ascii_lowercase + string.digits, k=3))
        path = "".join(random.choices(string.ascii_lowercase + string.digits, k=3))

        connection = src.tools.Connection(Mock(), base_url)

        ### Act
        file = src.resource.File(connection, repo_key, path)

        ### Assert
        self.assertIsInstance(file, src.resource.File)

    def test_file_info_sets_attribute(self):
        """when an attribute is requested that is served by the file info API call
        the attribute should be retrieved stored and returned
        """
        ### Arrange
        base_url = "".join(random.choices(string.ascii_lowercase + string.digits, k=10))
        repo_key = "".join(random.choices(string.ascii_lowercase + string.digits, k=3))
        path = "".join(random.choices(string.ascii_lowercase + string.digits, k=3))

        response_json = {
            'repo': repo_key,
            'path': path,
            'created': '2018-07-06T20:57:45.614Z',
            'createdBy': 'bud@manley.com',
            'lastModified': '2018-07-06T20:57:45.546Z',
            'modifiedBy': 'bud@manley.com',
            'lastUpdated': '2018-07-06T20:57:45.546Z',
            'downloadUri': f'{base_url}/{repo_key}/{path}',
            'mimeType': 'application/json',
            'size': '1576',
            'checksums': {
                'sha1': '727d06a0f230bddb4a2f076c1a72bbd409d21d0c',
                'md5': '938b54b3995eba3c35732be65cb87b5e',
                'sha256': '4e9826323c3dd4090b3b30b0a0799f4fda94092394b1a0b011196e6b41eecb29'},
            'originalChecksums': {
                'sha256': '4e9826323c3dd4090b3b30b0a0799f4fda94092394b1a0b011196e6b41eecb29'},
            'uri': f'{base_url}/{repo_key}/{path}'}

        session = Mock()
        session.get.return_value.json.return_value = response_json
        connection = src.tools.Connection(session, base_url)

        file = src.resource.File(connection, repo_key, path)

        ### Act
        size = file.size

        ### Assert
        self.assertEqual(size, response_json['size'])

    def test_file_statistics_sets_attribute(self):
        """when an attribute is requested that is served by the file statistics API call
        the attribute should be retrieved stored and returned
        """
        ### Arrange
        base_url = "".join(random.choices(string.ascii_lowercase + string.digits, k=10))
        repo_key = "".join(random.choices(string.ascii_lowercase + string.digits, k=3))
        path = "".join(random.choices(string.ascii_lowercase + string.digits, k=3))

        response_json = {
            'uri': f'{base_url}/{repo_key}/{path}',
            'downloadCount': 1,
            'lastDownloaded': 1530910689016,
            'lastDownloadedBy': 'xray',
            'remoteDownloadCount': 0,
            'remoteLastDownloaded': 0}

        session = Mock()
        session.get.return_value.json.return_value = response_json
        connection = src.tools.Connection(session, base_url)

        file = src.resource.File(connection, repo_key, path)

        ### Act
        lastDownloaded = file.lastDownloaded

        ### Assert
        self.assertEqual(lastDownloaded, response_json['lastDownloaded'])

    def test_bad_attribute_throws_exception(self):
        """when an attribute is requested that is served by the file statistics API call
        the attribute should be retrieved stored and returned
        """
        ### Arrange
        base_url = "".join(random.choices(string.ascii_lowercase + string.digits, k=10))
        repo_key = "".join(random.choices(string.ascii_lowercase + string.digits, k=3))
        path = "".join(random.choices(string.ascii_lowercase + string.digits, k=3))

        connection = src.tools.Connection(Mock(), base_url)

        file = src.resource.File(connection, repo_key, path)

        ### Act
        with self.assertRaises(AttributeError) as context:
            file.xyz

        self.assertIsInstance(context.exception, AttributeError)
        self.assertTrue("<class 'src.resource.File'> has no attribute xyz" in context.exception.__str__())

    def test_date_created(self):
        """date_created returns a datetime object
        """
        ### Arrange
        base_url = "".join(random.choices(string.ascii_lowercase + string.digits, k=10))
        repo_key = "".join(random.choices(string.ascii_lowercase + string.digits, k=3))
        path = "".join(random.choices(string.ascii_lowercase + string.digits, k=3))

        response_json = {
            'repo': repo_key,
            'path': path,
            'created': '2018-07-06T20:57:45.614Z',
            'createdBy': 'bud@manley.com',
            'lastModified': '2018-07-06T20:57:45.546Z',
            'modifiedBy': 'bud@manley.com',
            'lastUpdated': '2018-07-06T20:57:45.546Z',
            'downloadUri': f'{base_url}/{repo_key}/{path}',
            'mimeType': 'application/json',
            'size': '1576',
            'checksums': {
                'sha1': '727d06a0f230bddb4a2f076c1a72bbd409d21d0c',
                'md5': '938b54b3995eba3c35732be65cb87b5e',
                'sha256': '4e9826323c3dd4090b3b30b0a0799f4fda94092394b1a0b011196e6b41eecb29'},
            'originalChecksums': {
                'sha256': '4e9826323c3dd4090b3b30b0a0799f4fda94092394b1a0b011196e6b41eecb29'},
            'uri': f'{base_url}/{repo_key}/{path}'}

        session = Mock()
        session.get.return_value.json.return_value = response_json
        connection = src.tools.Connection(session, base_url)

        file = src.resource.File(connection, repo_key, path)

        ### Act
        date_created = file.date_created

        ### Assert
        self.assertIsInstance(date_created, datetime.datetime)

    def test_date_downloaded(self):
        """date_downloaded returns a datetime object"""
        ### Arrange
        base_url = "".join(random.choices(string.ascii_lowercase + string.digits, k=10))
        repo_key = "".join(random.choices(string.ascii_lowercase + string.digits, k=3))
        path = "".join(random.choices(string.ascii_lowercase + string.digits, k=3))

        response_json = {
            'uri': f'{base_url}/{repo_key}/{path}',
            'downloadCount': 1,
            'lastDownloaded': 1530910689016,
            'lastDownloadedBy': 'xray',
            'remoteDownloadCount': 0,
            'remoteLastDownloaded': 0}

        session = Mock()
        session.get.return_value.json.return_value = response_json
        connection = src.tools.Connection(session, base_url)

        file = src.resource.File(connection, repo_key, path)

        ### Act
        date_downloaded = file.date_downloaded

        ### Assert
        self.assertIsInstance(date_downloaded, datetime.datetime)

    def test_multiple_object_updates_retain_all_information(self):
        """When file_statistics and file_info are called both sets of information are retained"""
        ### Arrange
        base_url = "".join(random.choices(string.ascii_lowercase + string.digits, k=10))
        repo_key = "".join(random.choices(string.ascii_lowercase + string.digits, k=3))
        path = "".join(random.choices(string.ascii_lowercase + string.digits, k=3))

        file_info_json = {
            'repo': repo_key,
            'path': path,
            'created': '2018-07-06T20:57:45.614Z',
            'createdBy': 'bud@manley.com',
            'lastModified': '2018-07-06T20:57:45.546Z',
            'modifiedBy': 'bud@manley.com',
            'lastUpdated': '2018-07-06T20:57:45.546Z',
            'downloadUri': f'{base_url}/{repo_key}/{path}',
            'mimeType': 'application/json',
            'size': '1576',
            'checksums': {
                'sha1': '727d06a0f230bddb4a2f076c1a72bbd409d21d0c',
                'md5': '938b54b3995eba3c35732be65cb87b5e',
                'sha256': '4e9826323c3dd4090b3b30b0a0799f4fda94092394b1a0b011196e6b41eecb29'},
            'originalChecksums': {
                'sha256': '4e9826323c3dd4090b3b30b0a0799f4fda94092394b1a0b011196e6b41eecb29'},
            'uri': f'{base_url}/{repo_key}/{path}'}

        file_statistics_json = {
            'uri': f'{base_url}/{repo_key}/{path}',
            'downloadCount': 1,
            'lastDownloaded': 1530910689016,
            'lastDownloadedBy': 'xray',
            'remoteDownloadCount': 0,
            'remoteLastDownloaded': 0}

        session = Mock()
        session.get.return_value.json.side_effect = [file_info_json, file_statistics_json]
        connection = src.tools.Connection(session, base_url)

        file = src.resource.File(connection, repo_key, path)

        ### Act
        file.size
        file.downloadCount

        ### Assert
        self.assertEqual(file.size, file_info_json['size'])
        self.assertEqual(file.downloadCount, file_statistics_json['downloadCount'])
        self.assertEqual(session.get.return_value.json.call_count, 2)
