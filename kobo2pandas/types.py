from typing import Any, Dict, List, Union
import pandas as pd
from dataclasses import dataclass
from enum import Enum

# Tipos centralizados
JSONData = Union[Dict[str, Any], List[Any], str, int, float, bool, None]
JSONDict = Dict[str, Any]
JSONList = List[JSONDict]
DataFrameDict = Dict[str, pd.DataFrame]
AssetList = List[Dict[str, Any]]


class KoboEndpoint(Enum):
    """Endpoints predefinidos de KoboToolbox."""
    DEFAULT = 'https://kf.kobotoolbox.org/'
    HUMANITARIAN = 'https://kc.humanitarianresponse.info/'


@dataclass
class ProcessingConfig:
    """Configuración centralizada para el procesamiento de datos."""
    debug: bool = False
    exclude_validation_fields: bool = True
    clean_column_names: bool = True
    max_sheet_name_length: int = 31
    excluded_fields: List[str] = None

    def __post_init__(self):
        if self.excluded_fields is None:
            self.excluded_fields = [
                '_validation_status',
                'formhub/uuid',
                'meta/instanceID',
                '_xform_id_string',
                'meta/rootUuid'
            ]
