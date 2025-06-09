from typing import Dict, Set, List


class TableNameManager:
    """Manages table naming, cleaning, and sheet name generation for Excel export."""

    def __init__(self) -> None:
        self.path_mapping: Dict[str, str] = {}

    def clean_table_name(self, table_name: str) -> str:
        """
        Cleans table name by removing 'root_' prefix and using relevant parts.

        Args:
            table_name: Original table name

        Returns:
            Cleaned table name
        """
        if table_name == "root":
            return "root"

        # Remove 'root_' prefix if exists
        if table_name.startswith("root_"):
            clean_name = table_name[5:]
        else:
            clean_name = table_name

        # Handle multiple parts separated by '_'
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

    def sanitize_sheet_name(self, name: str) -> str:
        """
        Sanitizes sheet name for Excel by removing invalid characters.

        Args:
            name: Original name

        Returns:
            Sanitized name
        """
        invalid_chars: List[str] = ['/', '\\', '?', '*', '[', ']', ':']

        sanitized = name
        for char in invalid_chars:
            sanitized = sanitized.replace(char, '_')

        sanitized = sanitized.strip()

        if not sanitized:
            sanitized = "sheet"

        return sanitized

    def generate_sheet_names(self, table_names: List[str]) -> Dict[str, str]:
        """
        Generates systematic sheet names for Excel export.

        Args:
            table_names: List of table names

        Returns:
            Dict mapping table names to sheet names
        """
        sheet_names: Dict[str, str] = {}

        for table_name in table_names:
            if table_name == "root":
                sheet_names[table_name] = "root"
            else:
                clean_name = self.clean_table_name(table_name)
                sheet_name = self.sanitize_sheet_name(clean_name)

                # Truncate if too long (Excel limit: 31 characters)
                if len(sheet_name) > 31:
                    sheet_name = sheet_name[:31]

                sheet_names[table_name] = sheet_name

        return self._ensure_unique_names(sheet_names)

    def _ensure_unique_names(self, sheet_names: Dict[str, str]) -> Dict[str, str]:
        """Ensures all sheet names are unique by adding counters if needed."""
        used_names: Set[str] = set()
        final_names: Dict[str, str] = {}

        for table_name, sheet_name in sheet_names.items():
            original_name = sheet_name
            counter = 1

            while sheet_name in used_names:
                suffix = f"_{counter}"
                max_length = 31 - len(suffix)
                sheet_name = original_name[:max_length] + suffix
                counter += 1

            used_names.add(sheet_name)
            final_names[table_name] = sheet_name

        return final_names
