import requests
from typing import Optional, Dict, Any
from .types import JSONData, ProcessingConfig


class KoboHTTPClient:
    """Cliente HTTP especializado para la API de KoboToolbox."""

    def __init__(self, token: str, base_url: str, config: ProcessingConfig):
        self._token = token
        self._base_url = base_url.rstrip('/')
        self._config = config
        self._session = self._create_session()

    def _create_session(self) -> requests.Session:
        session = requests.Session()
        session.headers.update({
            'Authorization': f'Token {self._token}',
            'Content-Type': 'application/json'
        })
        return session

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> JSONData:
        """Realiza petición GET a la API."""
        url = f"{self._base_url}/api/v2{endpoint}"

        try:
            response = self._session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            if self._config.debug:
                print(f"❌ Error en petición HTTP: {e}")
            raise
