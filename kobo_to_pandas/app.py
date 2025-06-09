"""Main KoboAPI class with exposed methods."""

import json
from typing import Any, Dict, List, Optional, Union
import pandas as pd
from api.client import HTTPClient
from data_processor.parser import JSONFlattener

# Type aliases for JSON data and common structures
JSONData = Union[Dict[str, Any], List[Any], str, int, float, bool, None]
AssetList = List[Dict[str, Any]]
UIDMapping = Dict[str, str]
DataFrameDict = Dict[str, pd.DataFrame]


class KoboAPI:
    """Extracts collected data from KoBoToolbox with improved architecture."""

    # Predefined endpoints
    ENDPOINTS: Dict[str, str] = {
        'default': 'https://kf.kobotoolbox.org/',
        'humanitarian': 'https://kc.humanitarianresponse.info/'
    }

    def __init__(self, token: str, endpoint: str = 'default', debug: bool = False) -> None:
        """Initialize the Kobo client.

        Args:
            token: Your authentication token
            endpoint: The KoBoToolbox API endpoint. Options:
                    - 'default': https://kf.kobotoolbox.org/ (default)
                    - 'humanitarian': https://kc.humanitarianresponse.info/
                    - Custom URL string
            debug: Enable debugging output
        """
        # Resolve endpoint
        if endpoint in self.ENDPOINTS:
            resolved_endpoint: str = self.ENDPOINTS[endpoint]
        else:
            resolved_endpoint = endpoint

        self.client: HTTPClient = HTTPClient(token, resolved_endpoint, debug)
        self.debug: bool = debug
        self.flattener: JSONFlattener = JSONFlattener()

    def list_assets(self) -> AssetList:
        """List all assets as dictionaries."""
        response: JSONData = self.client.get('/assets.json')
        if isinstance(response, dict):
            return response.get('results', [])
        return []

    def list_uid(self) -> UIDMapping:
        """Return a dictionary mapping asset names to their UIDs."""
        assets: AssetList = self.list_assets()
        return {asset.get('name', ''): asset.get('uid', '') for asset in assets}

    def get_asset(self, asset_uid: str) -> Dict[str, Any]:
        """Get detailed asset information."""
        response: JSONData = self.client.get(f'/assets/{asset_uid}.json')
        return response if isinstance(response, dict) else {}

    def get_data(
            self,
            asset_uid: str,
            query: Optional[str] = None,
            start: Optional[int] = None,
            limit: Optional[int] = None,
            submitted_after: Optional[str] = None
            ) -> Dict[str, Any]:
        """Get survey data with improved parameter handling."""
        params: Dict[str, Union[str, int]] = {}

        if query:
            params['query'] = query
            if self.debug and submitted_after:
                print("Ignoring 'submitted_after' because 'query' is specified.")
        elif submitted_after:
            params['query'] = f'{{"_submission_time": {{"$gt": "{submitted_after}"}}}}'

        if start is not None:
            params['start'] = start
        if limit is not None:
            params['limit'] = limit

        response: JSONData = self.client.get(f'/assets/{asset_uid}/data.json', params)
        return response if isinstance(response, dict) else {}

    def get_choices(self, asset: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Get choices from asset content."""
        content: Dict[str, Any] = asset.get('content', {})
        choice_lists: Dict[str, Dict[str, Any]] = {}
        sequence: int = 0

        for choice_data in content.get('choices', []):
            list_name = choice_data['list_name']
            if list_name not in choice_lists:
                choice_lists[list_name] = {}

            label = choice_data.get('label', [''])[0] if 'label' in choice_data else choice_data['name']

            choice_lists[list_name][choice_data['name']] = {
                'label': label,
                'sequence': sequence
            }
            sequence += 1

        return choice_lists

    def get_questions(self, asset: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get questions from asset content."""
        content: Dict[str, Any] = asset.get('content', {})
        return content.get('survey', [])

    def get_dataframes(self, asset_uid: str, **kwargs: Any) -> Optional[DataFrameDict]:
        """
        Get survey data and convert it to DataFrames.

        Args:
            asset_uid: The asset UID to process
            **kwargs: Additional parameters for get_data (query, start, limit, submitted_after)

        Returns:
            Dictionary of DataFrames or None if error
        """
        try:
            if self.debug:
                print(f"🔄 Getting data for asset: {asset_uid}")

            # Get the raw data
            data: Dict[str, Any] = self.get_data(asset_uid, **kwargs)

            if self.debug:
                results_count: int = len(data.get('results', []))
                print(f"📊 Retrieved {results_count} records")

            # Process into DataFrames
            dataframes: DataFrameDict = self.flattener.flatten_json(data)

            if self.debug:
                print(f"✅ Generated {len(dataframes)} DataFrames")
                for table_name, df in dataframes.items():
                    print(f"   - {table_name}: {df.shape}")

            return dataframes

        except Exception as e:
            if self.debug:
                print(f"❌ Error getting DataFrames: {str(e)}")
                import traceback
                traceback.print_exc()
            return None

    def export_excel(self, asset_uid: str, filename: Optional[str] = None, **kwargs: Any) -> bool:
        """
        Export survey data to Excel file.

        Args:
            asset_uid: The asset UID to export
            filename: Output file path. If None, uses ./{asset_uid}_{name}.xlsx
            **kwargs: Additional parameters for get_data (query, start, limit, submitted_after)

        Returns:
            True if export successful, False otherwise
        """
        try:
            # Get DataFrames
            dataframes: Optional[DataFrameDict] = self.get_dataframes(asset_uid, **kwargs)

            if not dataframes:
                if self.debug:
                    print("❌ No DataFrames to export")
                return False

            # Generate filename if not provided
            if filename is None:
                try:
                    asset: Dict[str, Any] = self.get_asset(asset_uid)
                    asset_name: str = asset.get('name', '')
                    # Clean asset name for filename
                    safe_name: str = "".join(c for c in asset_name if c.isalnum() or c in (' ', '-', '_')).strip()
                    safe_name = safe_name.replace(' ', '_')
                    filename = f"./{asset_uid}_{safe_name}.xlsx"
                except:
                    filename = f"./{asset_uid}.xlsx"

            if self.debug:
                print(f"📁 Exporting to: {filename}")

            # Export to Excel
            success = self.flattener.export_to_excel(filename, dataframes)

            if success and self.debug:
                print("✅ Export completed successfully")

            return success

        except Exception as e:
            if self.debug:
                print(f"❌ Error exporting to Excel: {str(e)}")
                import traceback
                traceback.print_exc()
            return False
