"""Module holding various helper classes"""
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import requests

@dataclass
class Connection():
    """Store request session and base url in simple object"""
    session: 'requests.sessions.Session'
    base_url: str
    session_timeout: int = 15 #TODO Pass this value in to allow user configuration
