"""Python representation of aql query language"""
import logging
import json
from typing import List, Type

import requests

from . import tools
from . import resource


class Items():
    """item.find aql query class"""
    logger = logging.getLogger(__name__)

    def __init__(self, base_url: str, api_key: str):
        session = requests.Session()
        headers = {"X-JFrog-Art-Api": api_key}
        session.headers.update(headers)

        self.connection = tools.Connection(session=session, base_url=base_url)

    def find(self, query: dict) -> 'FileCursor':
        json_query = json.dumps(query)
        json_query = f"items.find({json_query})"

        cursor = FileCursor(self.connection, resource.File, json_query)

        return cursor

class FileCursor():
    """Cursor for aql file queries. Split out so we can support .include().sort() etc"""
    def __init__(self, connection: 'tools.Connection', api_class: Type[resource.File], query: str):
        self.connection = connection
        self.api_class = api_class
        self.query = query
        self.index = -1
        self.json = None

    def __iter__(self):
        return self

    def __next__(self):
        while True:
            self.index += 1
            try:
                json_resource = self.json['results'][self.index]
            except TypeError:
                self.run_query()
            except (IndexError) as error:
                raise StopIteration from error
            else:
                path = '/'.join([json_resource['path'], json_resource['name']])
                del json_resource['path']

                api_resource = self.api_class(
                    connection=self.connection,
                    path=path,
                    **json_resource)

                return api_resource

    def run_query(self):
        url_parts = [
            self.connection.base_url,
            'api/search/aql']

        url = '/'.join(url_parts)

        response = self.connection.session.post(url, data=self.query)
        response.raise_for_status()

        self.json = response.json()

        self.index = -1

    def include(self, fields: List[str]):
        for required_field in ('repo', 'path', 'name'):
            if required_field not in fields:
                fields.append(required_field)

        fields_to_string = ', '.join([f'"{field.strip()}"' for field in fields if field])
        self.query = f"{self.query}.include({fields_to_string})"

        return self
