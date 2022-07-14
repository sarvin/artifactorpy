"""Artifactory REST API resources"""
import logging

import requests

from . import tools
from . import resource


class _Base(): # pylint: disable=too-few-public-methods
    """Base class for Artifactory API entry points"""
    logger = logging.getLogger(__name__)

    def __init__(self, base_url: str, api_key: str):
        session = requests.Session()
        headers = {"X-JFrog-Art-Api": api_key}
        session.headers.update(headers)

        self.connection = tools.Connection(session=session, base_url = base_url)


class ArtifactsAndStorage(_Base, resource.RepositoriesMixin):
    """Entry point into Artifactorie's Artifacts & Storage APIs"""

    def get_directory(self, repository_key: str, path: str) -> resource.Directory:
        """Find a single directory in Artifactory

        Args:
            repository_key (str): equivalent of the repo key in Artifactory API
            path (str, optional): path to a directory in Artifactory. Defaults to None.

        Returns:
            resource.Directory: object describing an Artifactory directory with helper methods.
        """
        url_parts = [
            self.connection.base_url, 'api/storage', repository_key]
        if path:
            url_parts.append(path)

        url = '/'.join(url_parts)

        response = self.connection.session.get(url)

        directory = resource.Directory(self.connection, repository_key, path)
        directory._context = response.json() # pylint: disable=protected-access

        return directory
