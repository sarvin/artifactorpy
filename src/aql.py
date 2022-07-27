"""Python representation of aql query language"""
import logging
import json
from typing import List, TYPE_CHECKING, Optional

from . import resource

if TYPE_CHECKING:
    from . import tools


class FileCursor():
    """Cursor for aql file queries. Split out so we can support .include().sort() etc"""
    logger = logging.getLogger(__name__)

    def __init__(self, connection: 'tools.Connection'):
        self.connection = connection
        self.query: Optional[str] = None
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

                api_resource = resource.File(
                    connection=self.connection,
                    path=path,
                    **json_resource)

                return api_resource

    def find(self, query: dict) -> 'FileCursor':
        json_query = json.dumps(query)
        json_query = f"items.find({json_query})"

        self.query = json_query

        return self

    def run_query(self):
        url_parts = [
            self.connection.base_url,
            'api/search/aql']

        url = '/'.join(url_parts)

        response = self.connection.session.post(url, data=self.query)
        response.raise_for_status()

        self.json = response.json()
        self.logger.debug("range %s", self.json['range'])

        self.index = -1

    def include(self, fields: List[str]):
        for required_field in ('repo', 'path', 'name'):
            if required_field not in fields:
                fields.append(required_field)

        fields_to_string = ', '.join([f'"{field.strip()}"' for field in fields if field])
        self.query = f"{self.query}.include({fields_to_string})"

        return self
