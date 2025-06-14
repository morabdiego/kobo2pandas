from typing import Any, Dict, List, Optional, Union
from .types import JSONData, JSONDict, AssetList, DataFrameDict, ProcessingConfig, KoboEndpoint
from .client import KoboHTTPClient
from .processor import JSONDataProcessor, ExcelExporter
from .utils import DataValidationUtils, StringUtils


class KoboAPI:
    """API principal para extraer y procesar datos de KoboToolbox."""

    def __init__(self, token: str, endpoint: str = 'default', debug: bool = False):
        self._config = ProcessingConfig(debug=debug)
        resolved_endpoint = self._resolve_endpoint(endpoint)
        
        self._http_client = KoboHTTPClient(token, resolved_endpoint, self._config)
        self._data_processor = JSONDataProcessor(self._config)
        self._excel_exporter = ExcelExporter(self._config)

    def _resolve_endpoint(self, endpoint: str) -> str:
        endpoint_mapping = {
            'default': KoboEndpoint.DEFAULT.value,
            'humanitarian': KoboEndpoint.HUMANITARIAN.value
        }
        return endpoint_mapping.get(endpoint, endpoint)

    def list_assets(self) -> AssetList:
        """Lista todos los assets disponibles."""
        try:
            response = self._http_client.get('/assets.json')
            return DataValidationUtils.extract_results_from_response(response)
        except Exception:
            return []

    def list_uid(self) -> Dict[str, str]:
        """Retorna mapeo de nombres de assets a sus UIDs."""
        assets = self.list_assets()
        return {asset.get('name', ''): asset.get('uid', '') for asset in assets}

    def get_asset(self, asset_uid: str) -> JSONDict:
        """Obtiene detalles de un asset."""
        try:
            response = self._http_client.get(f'/assets/{asset_uid}.json')
            return response if isinstance(response, dict) else {}
        except Exception:
            return {}

    def get_data(self, asset_uid: str, **filters) -> JSONDict:
        """Obtiene datos de encuesta con filtros opcionales."""
        params = self._build_query_params(**filters)
        try:
            response = self._http_client.get(f'/assets/{asset_uid}/data.json', params)
            return response if isinstance(response, dict) else {}
        except Exception:
            return {}

    def get_dataframes(self, asset_uid: str, **kwargs) -> Optional[DataFrameDict]:
        """Obtiene datos de encuesta y los convierte a DataFrames."""
        try:
            data = self.get_data(asset_uid, **kwargs)
            if not data:
                return None
            return self._data_processor.process(data)
        except Exception:
            return None

    def export_excel(self, asset_uid: str, filename: Optional[str] = None, **kwargs) -> bool:
        """Exporta datos de encuesta a archivo Excel."""
        try:
            dataframes = self.get_dataframes(asset_uid, **kwargs)
            if not dataframes:
                return False

            if filename is None:
                filename = self._generate_filename(asset_uid)

            return self._excel_exporter.export(dataframes, filename)
        except Exception:
            return False

    def get_choices(self, asset: JSONDict) -> Dict[str, Dict[str, Any]]:
        """Extrae opciones de selección de un asset."""
        content = asset.get('content', {})
        choice_lists = {}
        sequence = 0

        for choice_data in content.get('choices', []):
            list_name = choice_data['list_name']
            if list_name not in choice_lists:
                choice_lists[list_name] = {}

            if 'label' in choice_data and isinstance(choice_data['label'], list):
                label = choice_data['label'][0] if choice_data['label'] else choice_data['name']
            else:
                label = choice_data.get('label', choice_data['name'])

            choice_lists[list_name][choice_data['name']] = {
                'label': label,
                'sequence': sequence
            }
            sequence += 1

        return choice_lists

    def get_questions(self, asset: JSONDict) -> List[JSONDict]:
        """Extrae preguntas de un asset."""
        content = asset.get('content', {})
        return content.get('survey', [])

    def _build_query_params(self, **filters) -> Dict[str, Union[str, int]]:
        """Construye parámetros de consulta a partir de filtros."""
        params = {}

        if 'query' in filters and filters['query']:
            params['query'] = filters['query']
        elif 'submitted_after' in filters and filters['submitted_after']:
            params['query'] = f'{{"_submission_time": {{"$gt": "{filters["submitted_after"]}"}}}}'

        for param in ['start', 'limit']:
            if param in filters and filters[param] is not None:
                params[param] = filters[param]

        return params

    def _generate_filename(self, asset_uid: str) -> str:
        """Genera nombre de archivo basado en el asset."""
        try:
            asset_details = self.get_asset(asset_uid)
            asset_name = asset_details.get('name', '')
            if asset_name:
                clean_name = StringUtils.clean_filename(asset_name)
                return f"./{asset_uid}_{clean_name}.xlsx"
            else:
                return f"./{asset_uid}.xlsx"
        except Exception:
            return f"./{asset_uid}.xlsx"
