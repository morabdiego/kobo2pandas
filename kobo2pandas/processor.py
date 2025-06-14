import pandas as pd
import os
from typing import Dict
from .types import JSONData, JSONDict, DataFrameDict, ProcessingConfig
from .utils import DataValidationUtils, StringUtils


class JSONDataProcessor:
    """Procesador de datos JSON de KoboToolbox."""

    def __init__(self, config: ProcessingConfig):
        self._config = config
        self._reset_state()

    def process(self, data: JSONData, table_name: str = "root") -> DataFrameDict:
        """Procesa datos JSON en DataFrames relacionados."""
        self._reset_state()

        if not DataValidationUtils.is_valid_json_response(data):
            return {}

        records = DataValidationUtils.extract_results_from_response(data)

        for index, record in enumerate(records, 1):
            self._process_record(record, table_name, index)

        return self._convert_to_dataframes()

    def _reset_state(self) -> None:
        self._tables = {}
        self._counters = {}

    def _process_record(self, record: JSONDict, table_name: str, record_index: int,
                       parent_index: int = None, parent_table: str = None) -> None:
        base_record = {'_index': record_index}
        if parent_index is not None:
            base_record['_parent_index'] = parent_index
            base_record['_parent_table'] = parent_table

        simple_fields, nested_fields = self._separate_fields(record)
        base_record.update(simple_fields)

        self._add_to_table(table_name, base_record)
        self._process_nested_fields(nested_fields, table_name, record_index)

    def _separate_fields(self, record: JSONDict) -> tuple[JSONDict, JSONDict]:
        simple_fields = {}
        nested_fields = {}

        for key, value in record.items():
            if key in self._config.excluded_fields:
                continue

            if DataValidationUtils.is_nested_data(value):
                nested_fields[key] = value if isinstance(value, list) else [value]
            else:
                simple_fields[key] = str(value) if isinstance(value, (list, dict)) else value

        return simple_fields, nested_fields

    def _add_to_table(self, table_name: str, record: JSONDict) -> None:
        if table_name not in self._tables:
            self._tables[table_name] = []
        self._tables[table_name].append(record)

    def _process_nested_fields(self, nested_fields: JSONDict, parent_table: str, parent_index: int) -> None:
        for field_name, field_data in nested_fields.items():
            child_table_name = f"{parent_table}_{field_name}"

            for nested_item in field_data:
                child_index = self._get_next_child_index(child_table_name)
                clean_parent_name = StringUtils.extract_meaningful_name(parent_table)

                self._process_record(
                    nested_item,
                    child_table_name,
                    child_index,
                    parent_index,
                    clean_parent_name
                )

    def _get_next_child_index(self, child_table_name: str) -> int:
        if child_table_name not in self._counters:
            self._counters[child_table_name] = 0
        self._counters[child_table_name] += 1
        return self._counters[child_table_name]

    def _convert_to_dataframes(self) -> DataFrameDict:
        dataframes = {}

        for table_name, records in self._tables.items():
            if not records:
                continue

            df = pd.DataFrame(records)
            if self._config.clean_column_names:
                df = self._clean_column_names(df)
            dataframes[table_name] = df

        return dataframes

    def _clean_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        new_columns = {}
        for col in df.columns:
            if col.startswith('_'):
                new_columns[col] = col
            else:
                new_columns[col] = col.split('/')[-1]
        return df.rename(columns=new_columns)


class ExcelExporter:
    """Exportador especializado para archivos Excel."""

    def __init__(self, config: ProcessingConfig):
        self._config = config

    def export(self, dataframes: DataFrameDict, filename: str) -> bool:
        """Exporta DataFrames a archivo Excel."""
        try:
            valid_dataframes = self._filter_valid_dataframes(dataframes)
            if not valid_dataframes:
                return False

            self._ensure_directory_exists(filename)
            sheet_names = self._generate_sheet_names(valid_dataframes)
            return self._write_excel_file(valid_dataframes, sheet_names, filename)

        except Exception:
            return False

    def _filter_valid_dataframes(self, dataframes: DataFrameDict) -> DataFrameDict:
        return {
            table_name: df for table_name, df in dataframes.items()
            if '_validation_status' not in table_name and not df.empty
        }

    def _generate_sheet_names(self, dataframes: DataFrameDict) -> Dict[str, str]:
        sheet_names = {}
        used_names = set()

        for table_name in dataframes.keys():
            if table_name == "root":
                base_name = "root"
            else:
                meaningful_name = StringUtils.extract_meaningful_name(table_name)
                base_name = StringUtils.sanitize_sheet_name(
                    meaningful_name,
                    self._config.max_sheet_name_length
                )

            unique_name = self._ensure_unique_name(base_name, used_names)
            sheet_names[table_name] = unique_name
            used_names.add(unique_name)

        return sheet_names

    def _ensure_unique_name(self, base_name: str, used_names: set) -> str:
        if base_name not in used_names:
            return base_name

        counter = 1
        while True:
            suffix = f"_{counter}"
            max_length = self._config.max_sheet_name_length - len(suffix)
            candidate = base_name[:max_length] + suffix
            if candidate not in used_names:
                return candidate
            counter += 1

    def _ensure_directory_exists(self, filename: str) -> None:
        directory = os.path.dirname(filename)
        if directory:
            os.makedirs(directory, exist_ok=True)

    def _write_excel_file(self, dataframes: DataFrameDict, sheet_names: Dict[str, str], filename: str) -> bool:
        try:
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                table_order = (["root"] if "root" in dataframes else []) + \
                             [name for name in dataframes.keys() if name != "root"]

                for table_name in table_order:
                    df = dataframes[table_name]
                    sheet_name = sheet_names[table_name]
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
            return True
        except Exception:
            return False
