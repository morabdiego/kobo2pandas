import pandas as pd
import os
from typing import Dict
from .table_name_manager import TableNameManager

# Type alias for DataFrame collections
DataFrameDict = Dict[str, pd.DataFrame]


class ExcelExporter:
    """Handles Excel export functionality for DataFrames."""

    def __init__(self) -> None:
        self.name_manager: TableNameManager = TableNameManager()

    def export_dataframes(self, dataframes: DataFrameDict, filename: str) -> bool:
        """
        Exports DataFrames to Excel file with systematic sheet names.

        Args:
            dataframes: Dictionary of DataFrames to export
            filename: Output Excel file path

        Returns:
            True if export successful, False otherwise
        """
        try:
            filtered_dataframes: DataFrameDict = self._filter_dataframes(dataframes)

            if not filtered_dataframes:
                print("⚠️ No valid DataFrames to export after filtering")
                return False

            self._ensure_directory_exists(filename)
            sheet_names: Dict[str, str] = self.name_manager.generate_sheet_names(list(filtered_dataframes.keys()))

            return self._write_excel_file(filtered_dataframes, sheet_names, filename)

        except Exception as e:
            print(f"❌ Error exporting to Excel: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def _filter_dataframes(self, dataframes: DataFrameDict) -> DataFrameDict:
        """Filters out problematic or empty DataFrames."""
        filtered: DataFrameDict = {}

        for table_name, df in dataframes.items():
            if '_validation_status' in table_name or df.empty:
                print(f"⚠️ Excluding problematic table: {table_name}")
                continue
            filtered[table_name] = df

        return filtered

    def _ensure_directory_exists(self, filename: str) -> None:
        """Creates directory if it doesn't exist."""
        directory: str = os.path.dirname(filename)
        if directory:
            os.makedirs(directory, exist_ok=True)

    def _write_excel_file(self, dataframes: DataFrameDict,
                         sheet_names: Dict[str, str], filename: str) -> bool:
        """Writes DataFrames to Excel file."""
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Order tables with root first
            table_order = ["root"] + [name for name in dataframes.keys() if name != "root"]

            for table_name in table_order:
                if table_name in dataframes:
                    df = dataframes[table_name]
                    sheet_name = sheet_names.get(table_name,
                                               self.name_manager.sanitize_sheet_name(table_name[:31]))

                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                    print(f"📄 {table_name} → sheet '{sheet_name}' ({df.shape[0]} rows, {df.shape[1]} columns)")

        print(f"📁 Excel file created successfully: {filename}")
        print(f"📊 Total sheets: {len(dataframes)}")
        return True
