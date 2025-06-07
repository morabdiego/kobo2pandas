"""HTTP client for KoboAPI interactions."""

import requests
from typing import Any, Dict, Optional


class HTTPClient:
    """Simple HTTP client for KoboAPI."""

    def __init__(self, token: str, base_url: str, debug: bool = False):
        self.token = token
        self.base_url = base_url.rstrip('/')
        self.debug = debug
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Token {token}',
            'Content-Type': 'application/json'
        })

    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make GET request to API."""
        url = f"{self.base_url}/api/v2{endpoint}"

        if self.debug:
            print(f"Making request to: {url}")
            if params:
                print(f"With parameters: {params}")

        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if self.debug:
                print(f"Request failed: {e}")
            raise
