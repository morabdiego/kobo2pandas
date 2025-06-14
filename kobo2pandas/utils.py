from typing import Any, List
from .types import JSONData, JSONDict


class DataValidationUtils:
    """Utilidades para validación de datos."""

    @staticmethod
    def is_valid_json_response(data: JSONData) -> bool:
        return data is not None and isinstance(data, (dict, list))

    @staticmethod
    def extract_results_from_response(data: JSONData) -> List[JSONDict]:
        if isinstance(data, dict) and 'results' in data:
            return data.get('results', [])
        elif isinstance(data, list):
            return data
        return []

    @staticmethod
    def is_nested_data(value: Any) -> bool:
        if isinstance(value, list) and len(value) > 0:
            return isinstance(value[0], dict)
        return isinstance(value, dict) and bool(value)


class StringUtils:
    """Utilidades para manipulación de strings."""

    @staticmethod
    def clean_filename(text: str) -> str:
        if not text:
            return "unnamed"
        safe_chars = "".join(c for c in text if c.isalnum() or c in (' ', '-', '_'))
        return safe_chars.strip().replace(' ', '_') or "unnamed"

    @staticmethod
    def sanitize_sheet_name(name: str, max_length: int = 31) -> str:
        if not name:
            return "sheet"

        invalid_chars = ['/', '\\', '?', '*', '[', ']', ':']
        sanitized = name
        for char in invalid_chars:
            sanitized = sanitized.replace(char, '_')

        return sanitized.strip()[:max_length] if len(sanitized) > max_length else sanitized.strip()

    @staticmethod
    def extract_meaningful_name(full_path: str) -> str:
        if full_path == "root":
            return "root"

        clean_name = full_path[5:] if full_path.startswith("root_") else full_path
        parts = clean_name.split('_')

        if len(parts) > 1:
            relevant_parts = [part.split('/')[-1] for part in parts]
            return relevant_parts[-1] if len(relevant_parts) == 1 else "_".join(relevant_parts[-2:])

        return clean_name
