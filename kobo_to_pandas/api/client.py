"""HTTP client for KoboAPI interactions."""

import json
import requests
from typing import Any, Dict, Optional, Union

# Type aliases for JSON data
JSONData = Union[Dict[str, Any], list, str, int, float, bool, None]


class HTTPClient:
    """Simple HTTP client for KoboAPI."""

    def __init__(self, token: str, base_url: str, debug: bool = False) -> None:
        self.token: str = token
        self.base_url: str = base_url.rstrip('/')
        self.debug: bool = debug
        self.session: requests.Session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Token {token}',
            'Content-Type': 'application/json'
        })

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> JSONData:
        """Make GET request to API."""
        url: str = f"{self.base_url}/api/v2{endpoint}"

        if self.debug:
            print(f"Making request to: {url}")
            if params:
                print(f"With parameters: {params}")

        try:
            response: requests.Response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if self.debug:
                print(f"Request failed: {e}")
            raise
