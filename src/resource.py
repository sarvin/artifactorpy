"""Classes representing different types of data in Artifactory"""
import logging
from enum import Enum
from datetime import datetime, timezone
from types import SimpleNamespace
from typing import List, Optional, TYPE_CHECKING, Union
from requests import exceptions

from hurry.filesize import size

if TYPE_CHECKING:
    from . import tools


class RepositoryType(Enum):
    """Describes the types of repositories in Artifactory"""
    LOCAL = 'local'
    REMOTE = 'remote'
    VIRTUAL = 'virtual'
    FEDERATED = 'federated'
    DISTRIBUTION = 'distribution'


class PackageType(Enum):
    """Describes the types of packages in Artifactory"""
    BOWER = 'Bower'
    CARGO = 'Cargo'
    CHEF = 'Chef'
    COCOAPODS = 'Cocoapods'
    COMPOSER = 'Composer'
    CONAN = 'Conan'
    CRAN = 'Cran'
    DEBIAN = 'Debian'
    DOCKER = 'Docker'
    GEMS = 'Gems'
    GITLFS = 'Gitlfs'
    GO = 'Go'
    GRADLE = 'Gradle'
    HELM = 'Helm'
    IVY = 'Ivy'
    MAVEN = 'Maven'
    NPM = 'Npm'
    NUGET = 'NuGet'
    OPKG = 'Opkg'
    PUB = 'Pub'
    PUPPET = 'Puppet'
    PYPI = 'Pypi'
    RPM = 'Rpm'
    SBT = 'Sbt'
    TERRAFORM = 'Terraform'
    VAGRANT = 'Vagrant'
    YUM = 'YUM'
    GENERIC = 'Generic'


class RepositoriesMixin: # pylint: disable=too-few-public-methods
    """Mixin supporting a request to list all repositories in Artifactory"""

    connection: 'tools.Connection'

    def get_repositories(
            self, repository_type: Optional[RepositoryType] = None,
            package_type: Optional[PackageType] = None) -> List['Repository']:
        """List repositories in Artifactory

        Returns:
            List[Repository]: list of repository objects
        """
        url = '/'.join([
            self.connection.base_url,
            'api/repositories'])

        params = {}
        if repository_type:
            params['type'] = repository_type.value

        if package_type:
            params['packageType'] = package_type.value

        response = self.connection.session.get(url, params=params)

        repositories = [
            Repository(
                self.connection,
                repository['key'],
                getattr(RepositoryType, repository['type']),
                repository['url'],
                PackageType(repository['packageType']))

            for repository in response.json()
        ]

        return repositories


class RepositoryMixin: # pylint: disable=too-few-public-methods
    """Mixin supporting a request to retrieve a single repository in Artifactory"""

    connection: 'tools.Connection'

    def get_repository(self, key) -> 'Repository':
        """List repositories in Artifactory

        Returns:
            Repository: A repository object
        """
        url = '/'.join([
            self.connection.base_url,
            'api/repositories'])

        response = self.connection.session.get(url)

        repository, = [
            Repository(
                self.connection,
                repository['key'],
                getattr(RepositoryType, repository['type']),
                repository['url'],
                PackageType(repository['packageType']))

            for repository in response.json()
            if repository['key'] == key
        ]

        return repository


class ParentMixin(RepositoryMixin): # pylint: disable=too-few-public-methods
    """Mixin to retrieve the parent of an File or Directory in Artifactory"""

    connection: 'tools.Connection'
    path: str
    repo: str

    def parent(self) -> Union['Directory', 'Repository']:
        """Return the parent of the current file object

        Returns:
            Either a directory or repository object
        """
        if self.path and self.path.split('/')[0:-1]:
            return Directory(
                self.connection,
                self.repo,
                '/'.join(self.path.split('/')[0:-1]))

        repository = self.get_repository(self.repo)

        return repository


class Directory(ParentMixin):
    """Methods to represent a directory in Artifactory"""
    logger = logging.getLogger(__name__)

    def __init__(self, connection: 'tools.Connection', repo: str, path: str):
        """Init method

        Args:
            artifactory (rtpy.Rtpy): Instance of the class rtpy
            repo (str): top-level directory name in Artifactory
            path (str): file path, to a file, under repo argument
        """
        self.connection = connection
        self.repo = repo
        self.path = path

        self._context = None

    def __repr__(self):
        return f"Directory({self.repo}, {self.path})"

    def children(self):
        """List child files and directories contained within
            this directory.

        Returns:
            List[Union[Directory, File]]: a list of directories
                and files represented by Directory and File
        """
        children = []

        for child in self.context['children']:
            if child['folder']:
                children.append(
                    Directory(
                        self.connection,
                        self.repo,
                        self.path + child['uri'] if self.path else child['uri']))
            else:
                children.append(
                    File(
                        self.connection,
                        self.repo,
                        self.path + child['uri'] if self.path else child['uri']))

        return children

    @property
    def context(self):
        """store the infromation returned by Artifactory for a Directory"""
        if not self._context:
            url_parts = [
                self.connection.base_url, 'api/storage', self.repo]
            if self.path:
                url_parts.append(self.path)

            url = '/'.join(url_parts)

            response = self.connection.session.get(url)

            self._context = response.json()

        return self._context

    @property
    def uri(self):
        """URL for the directory location in Artifactory"""
        return self.context['uri']

    def file_list(self) -> dict:
        """Get a flat (the default) or deep listing of the files and folders
        (not included by default) within a folder. For deep listing you can
        specify an optional depth to limit the results.

        Returns:
            dict: dictionary containing keys uri, created, files
        """
        url_parts = [
            self.connection.base_url, 'api/storage', self.repo]
        if self.path:
            url_parts.append(self.path)

        url = '/'.join(url_parts)

        param_dict = {'list': None, 'deep': 1, 'ListFolders': 0, 'mdTimestamps': 0}
        param_str = '&'.join([k if v is None else f"{k}={v}" for k, v in param_dict.items()])

        response = self.connection.session.get(url, params=param_str)

        return response.json()

    def size(self, human_readable = False) -> Union[int, str]:
        """Determine the file size of all files contained within the directory

        Args:
            human_readable (bool, optional): If True return a human readable string.
            If False returns total disk size in bytes. Defaults to False.

        Returns:
            Union[int, str]: Either an int representing bytes or human readable string.
        """
        file_list = self.file_list()

        file_size = 0
        for file in file_list['files']:
            file_size += file['size']

        if human_readable:
            return size(file_size)

        return file_size

    def delete(self) -> bool:
        """Delete the directory from Artifactory

        Returns:
            True if object deleted successfully
            False if object failed to be removed
        """
        self.logger.info(
            "Deleting Artifactory directory %s/%s",
            self.repo,
            self.path)
        url_parts = [
            self.connection.base_url, self.repo, self.path]

        url = '/'.join(url_parts)

        response = self.connection.session.delete(url, timeout=self.connection.session_timeout)

        if response.ok:
            return True

        return False


class Repository(Directory):
    """Methods to represent a repository in Artifactory"""
    logger = logging.getLogger(__name__)

    def __init__(
            self, connection: 'tools.Connection', repo: str,
            repository_type: RepositoryType, url: str, package_type: PackageType):
        """Init method

        Args:
            artifactory (rtpy.Rtpy): Instance of the class rtpy
            repo (str): top-level directory name in Artifactory
            path (str): file path, to a file, under repo argument
        """
        self.repository_type = repository_type
        self.url = url
        self.package_type = package_type
        super().__init__(connection, repo, '')

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.repo}>'


class File(SimpleNamespace, ParentMixin):
    """Methods to represent a file in Artifactory"""
    logger = logging.getLogger(__name__)

    file_info_attrs = [
        'created',
        'createdBy',
        'lastModified',
        'modifiedBy',
        'lastUpdated',
        'downloadUri',
        'mimeType',
        'size',
        'checksums',
        'originalChecksums',
        'uri']

    file_statistics_attrs = [
        'downloadCount',
        'lastDownloaded',
        'lastDownloadedBy',
        'remoteDownloadCount',
        'remoteLastDownloaded']

    def __init__(self, connection: 'tools.Connection', repo: str, path: str, **kwargs):
        """Init method

        Args:
            artifactory (rtpy.Rtpy): Instance of the class rtpy
            repo (str): top-level directory name in Artifactory
            path (str): file path, to a file, under repo argument
        """
        self.connection = connection
        self.repo = repo
        self.path = path
        super().__init__(**kwargs)

    def  __getattr__(self, name):

        if name in self.file_statistics_attrs:
            file_statistics = self.file_statistics()
            self.__init__(
                self.connection,
                self.repo,
                self.path,
                **file_statistics)

            return getattr(self, name)

        if name in self.file_info_attrs:
            file_info = self.file_info()
            self.__init__(
                connection=self.connection,
                **file_info)

            return getattr(self, name)

        raise AttributeError(f"{self.__class__} has no attribute {name}")

    def __repr__(self):
        return f"File({self.repo}, {self.path})"

    def file_statistics(self):
        """Query and cache information about file
        statistics generated by Artifactory using File Statistics
        API

        Returns:
            dict: with keys lastDownloaded, downloadCount, lastDownloadedBy
        """
        self.logger.debug(
            "querying Artifactory for file statistics repo=%s, path=%s",
            self.repo,
            self.path)

        url_parts = [
            self.connection.base_url, 'api/storage', self.repo]
        if self.path:
            url_parts.append(self.path)

        url = '/'.join(url_parts)

        response = self.connection.session.get(
            url,
            params='stats',
            timeout=self.connection.session_timeout)
        try:
            response.raise_for_status()
        except exceptions.HTTPError as err:
            if response.status_code == 404:

                raise exceptions.HTTPError(
                    "This request fails for files in virtual repos: " + err.args[0],
                    response=err.response) from err

        file_statistics = response.json()

        return file_statistics

    def file_info(self):
        """Query and cache information about a file
        generated by Artifactory File Info API

        Returns:
            dict: information about a file
        """
        self.logger.debug(
            "querying Artifactory for file info repo=%s, path=%s",
            self.repo,
            self.path)

        url_parts = [
            self.connection.base_url, 'api/storage', self.repo]
        if self.path:
            url_parts.append(self.path)

        url = '/'.join(url_parts)

        response = self.connection.session.get(url)

        file_info = response.json()

        return file_info

    @property
    def date_downloaded(self):
        """Query Artifactory and cache the
        date a file was last downloaded

        Returns:
            datetime: date representing the last time a file was downloaded
                from Artifactory
        """
        date_downloaded = datetime.fromtimestamp(
            self.lastDownloaded/1000.0).replace(
                tzinfo=timezone.utc)

        return date_downloaded

    @property
    def date_created(self):
        """Query Artifactory and cache the
        date a file was created

        Returns:
            datetime: date representing when a file was created in Artifactory
        """
        date_created = datetime.strptime(
            self.created.replace(
                'Z',
                '+0000'),
            '%Y-%m-%dT%H:%M:%S.%f%z')

        return date_created

    def delete(self) -> bool:
        """Delete a file from Artifactory

        Returns:
            True if object deleted successfully
            False if object failed to be removed
        """
        self.logger.info(
            "Deleting Artifactory file %s/%s",
            self.repo,
            self.path)
        url_parts = [
            self.connection.base_url, self.repo, self.path]

        url = '/'.join(url_parts)

        response = self.connection.session.delete(url)

        if response.ok:
            return True

        return False

    @property
    def name(self):
        """Name of file without path

        Returns:
            str: the name of the file, in Artifactory, without
                file path data
        """
        file_name = self.path.split('/')[-1]

        return file_name
