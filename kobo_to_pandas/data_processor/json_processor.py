import json
from typing import Dict, List, Any, Optional, Union
from collections import defaultdict

# Type aliases for JSON data
JSONData = Union[Dict[str, Any], List[Any], str, int, float, bool, None]
JSONDict = Dict[str, Any]
JSONList = List[JSONDict]
RecordsDict = Dict[str, List[JSONDict]]


class JSONProcessor:
    """Handles the core JSON flattening logic."""

    EXCLUDED_FIELDS: List[str] = [
        '_validation_status',
        'formhub/uuid',
        'meta/instanceID',
        '_xform_id_string',
        'meta/rootUuid'
    ]

    def __init__(self) -> None:
        self.dataframes: RecordsDict = {}
        self.counter: defaultdict[str, int] = defaultdict(int)

    def process_json_data(
            self, data: JSONData, table_name: str = "root",
            parent_index: Optional[int] = None
            ) -> RecordsDict:
        """
        Processes JSON data into structured records.

        Args:
            data: JSON data to process
            table_name: Name for root table
            parent_index: Index of parent record

        Returns:
            Dictionary of table records
        """
        self._reset_state()

        if isinstance(data, dict) and 'results' in data:
            for i, item in enumerate(data['results']):
                self._process_item(item, table_name, i + 1, parent_index)
        elif isinstance(data, list):
            for i, item in enumerate(data):
                self._process_item(item, table_name, i + 1, parent_index)
        else:
            self._process_item(data, table_name, 1, parent_index)

        return self.dataframes

    def _reset_state(self) -> None:
        """Resets internal state for new processing."""
        self.dataframes = {}
        self.counter = defaultdict(int)

    def _process_item(self, item: JSONData, table_name: str, item_index: int,
                     parent_index: Optional[int] = None, parent_table: Optional[str] = None) -> None:
        """Processes individual JSON item."""
        current_record, nested_data = self._extract_item_data(item, item_index, parent_index, parent_table)

        self._add_record_to_table(table_name, current_record)
        self._process_nested_items(nested_data, item_index, table_name)

    def _extract_item_data(self, item: JSONData, item_index: int,
                          parent_index: Optional[int], parent_table: Optional[str]) -> tuple[JSONDict, JSONDict]:
        """Extracts data from item, separating simple fields from nested ones."""
        current_record: JSONDict = {
            '_index': item_index
        }

        if parent_index is not None:
            current_record['_parent_index'] = parent_index
            current_record['_parent_table'] = parent_table

        nested_data: JSONDict = {}

        for key, value in item.items():
            if key in self.EXCLUDED_FIELDS:
                continue

            if isinstance(value, list) and len(value) > 0:
                if isinstance(value[0], dict):
                    nested_data[key] = value
                else:
                    current_record[key] = str(value)
            elif isinstance(value, dict):
                if value:
                    nested_data[key] = [value]
                else:
                    current_record[key] = str(value)
            else:
                current_record[key] = value

        return current_record, nested_data

    def _add_record_to_table(self, table_name: str, record: JSONDict) -> None:
        """Adds record to specified table."""
        if table_name not in self.dataframes:
            self.dataframes[table_name] = []
        self.dataframes[table_name].append(record)

    def _process_nested_items(self, nested_data: JSONDict, parent_index: int, parent_table: str) -> None:
        """Processes nested data items recursively."""
        for nested_key, nested_value in nested_data.items():
            self._process_nested_data(nested_value, nested_key, parent_index, parent_table)

    def _process_nested_data(self, nested_value: JSONList, nested_key: str,
                           parent_index: int, parent_table: str) -> None:
        """Processes nested data creating child tables."""
        child_table_name: str = f"{parent_table}_{nested_key}"

        for nested_item in nested_value:
            self.counter[child_table_name] += 1
            child_index: int = self.counter[child_table_name]

            self._process_item(nested_item, child_table_name, child_index,
                             parent_index, self._clean_parent_table_name(parent_table))

    def _clean_parent_table_name(self, parent_table: str) -> str:
        """Cleans parent table name for reference."""
        if parent_table == "root":
            return "root"

        if parent_table.startswith("root_"):
            clean_name = parent_table[5:]
        else:
            clean_name = parent_table

        parts = clean_name.split('_')
        if len(parts) > 1:
            relevant_parts = []
            for part in parts:
                if '/' in part:
                    relevant_parts.append(part.split('/')[-1])
                else:
                    relevant_parts.append(part)
            return relevant_parts[-1] if len(relevant_parts) == 1 else "_".join(relevant_parts[-2:])
        else:
            return clean_name
