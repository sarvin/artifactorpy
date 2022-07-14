"""Module holding various helper classes"""
from typing import NamedTuple, TYPE_CHECKING

if TYPE_CHECKING:
    import requests

class Connection(NamedTuple):
    """Store request session and base url in simple object"""
    session: 'requests.sessions.Session'
    base_url: str
