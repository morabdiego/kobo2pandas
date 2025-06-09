import json
import pandas as pd
from typing import Dict, List, Any, Optional, Union
from .json_processor import JSONProcessor
from .excel_exporter import ExcelExporter
from .table_name_manager import TableNameManager

# Type aliases
JSONData = Union[Dict[str, Any], List[Any], str, int, float, bool, None]
DataFrameDict = Dict[str, pd.DataFrame]
RecordsDict = Dict[str, List[Dict[str, Any]]]


class JSONFlattener:
    """Main class for flattening JSON data into pandas DataFrames."""

    def __init__(self) -> None:
        self.json_processor: JSONProcessor = JSONProcessor()
        self.excel_exporter: ExcelExporter = ExcelExporter()
        self.name_manager: TableNameManager = TableNameManager()

    def flatten_json(self, data: JSONData, table_name: str = "root",
                    parent_index: Optional[int] = None) -> DataFrameDict:
        """
        Flattens JSON data recursively into multiple DataFrames maintaining traceability.

        Args:
            data: Dictionary or list with JSON data
            table_name: Name for current table
            parent_index: Index of parent record

        Returns:
            Dictionary with generated DataFrames
        """
        records: RecordsDict = self.json_processor.process_json_data(data, table_name, parent_index)
        return self._convert_to_dataframes(records)

    def _convert_to_dataframes(self, records: RecordsDict) -> DataFrameDict:
        """Converts record lists to pandas DataFrames."""
        result: DataFrameDict = {}

        for table_name, record_list in records.items():
            if record_list:
                df: pd.DataFrame = pd.DataFrame(record_list)
                df = self._clean_column_names(df)
                result[table_name] = df

        return result

    def _clean_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """Cleans column names by taking last segment after '/'."""
        new_columns: Dict[str, str] = {}

        for col in df.columns:
            if col.startswith('_'):
                new_columns[col] = col
            else:
                clean_name = col.split('/')[-1]
                new_columns[col] = clean_name

        return df.rename(columns=new_columns)

    def export_to_excel(self, filename: str, dataframes: Optional[DataFrameDict] = None) -> bool:
        """
        Exports DataFrames to Excel file.

        Args:
            filename: Excel file path
            dataframes: DataFrames to export (uses current if None)

        Returns:
            True if export successful
        """
        if dataframes is None:
            print("⚠️ No DataFrames to export")
            return False

        return self.excel_exporter.export_dataframes(dataframes, filename)
