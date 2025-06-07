from enum import Enum
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
import pandas as pd

class NodeType(Enum):
    """Tipos de nodos en la jerarquía del formulario."""
    ROOT = "root"
    GROUP = "begin_group"
    REPEAT = "begin_repeat"
    FIELD = "field"

class FieldType(Enum):
    """Tipos de campos soportados en XLSForm."""
    TEXT = "text"
    INTEGER = "integer"
    DECIMAL = "decimal"
    DATE = "date"
    SELECT_ONE = "select_one"
    SELECT_MULTIPLE = "select_multiple"
    CALCULATE = "calculate"
    NOTE = "note"
    GEOPOINT = "geopoint"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    FILE = "file"
    BARCODE = "barcode"
    ACKNOWLEDGE = "acknowledge"
    HIDDEN = "hidden"

    @classmethod
    def from_string(cls, value: str) -> 'FieldType':
        """Convierte un string a FieldType."""
        try:
            return cls(value)
        except ValueError:
            # Para tipos como select_one list_name, extraer solo la parte principal
            if value.startswith('select_one'):
                return cls.SELECT_ONE
            elif value.startswith('select_multiple'):
                return cls.SELECT_MULTIPLE
            else:
                return cls.TEXT  # Default fallback

@dataclass
class FieldModel:
    """Modelo para representar un campo del formulario."""
    name: str
    field_type: FieldType
    label: str = ""
    xpath: str = ""
    level: int = 0
    required: bool = False
    readonly: bool = False
    relevant: str = ""
    constraint: str = ""
    constraint_message: str = ""
    appearance: str = ""
    default: str = ""
    choice_filter: str = ""
    calculation: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any], level: int = 0) -> 'FieldModel':
        """Crea un FieldModel desde un diccionario."""
        field_type_str = data.get('type', 'text')
        field_type = FieldType.from_string(field_type_str)

        # Extraer label (puede ser una lista o string)
        label_data = data.get('label', '')
        if isinstance(label_data, list) and label_data:
            label = label_data[0]
        else:
            label = str(label_data) if label_data else ''

        return cls(
            name=data.get('name', ''),
            field_type=field_type,
            label=label,
            xpath=data.get('$xpath', ''),
            level=level,
            required=data.get('required', '') == 'yes',
            readonly=data.get('readonly', '') == 'yes',
            relevant=data.get('relevant', ''),
            constraint=data.get('constraint', ''),
            constraint_message=data.get('constraint_message', ''),
            appearance=data.get('appearance', ''),
            default=data.get('default', ''),
            choice_filter=data.get('choice_filter', ''),
            calculation=data.get('calculation', '')
        )

@dataclass
class HierarchyNodeModel:
    """Modelo optimizado para representar un nodo en la jerarquía."""
    name: str
    node_type: NodeType
    level: int
    label: str = ""
    xpath: str = ""
    parent: Optional['HierarchyNodeModel'] = None
    children: List['HierarchyNodeModel'] = field(default_factory=list)
    fields: List[FieldModel] = field(default_factory=list)

    # Propiedades específicas para repeticiones
    repeat_count: str = ""

    # Propiedades específicas para grupos
    appearance: str = ""
    relevant: str = ""

    def add_child(self, child: 'HierarchyNodeModel') -> None:
        """Agrega un nodo hijo."""
        child.parent = self
        self.children.append(child)

    def add_field(self, field: FieldModel) -> None:
        """Agrega un campo al nodo."""
        self.fields.append(field)

    def is_repeat(self) -> bool:
        """Verifica si el nodo es una repetición."""
        return self.node_type == NodeType.REPEAT

    def is_group(self) -> bool:
        """Verifica si el nodo es un grupo."""
        return self.node_type == NodeType.GROUP

    def is_root(self) -> bool:
        """Verifica si el nodo es la raíz."""
        return self.node_type == NodeType.ROOT

    def get_path(self) -> List[str]:
        """Obtiene la ruta desde la raíz hasta este nodo."""
        path = []
        current = self
        while current and not current.is_root():
            path.insert(0, current.name)
            current = current.parent
        return path

    def get_all_fields(self, include_children: bool = True) -> List[FieldModel]:
        """Obtiene todos los campos del nodo y opcionalmente de sus hijos."""
        all_fields = self.fields.copy()

        if include_children:
            for child in self.children:
                all_fields.extend(child.get_all_fields(include_children=True))

        return all_fields

    def find_child_by_name(self, name: str) -> Optional['HierarchyNodeModel']:
        """Busca un hijo por nombre."""
        for child in self.children:
            if child.name == name:
                return child
        return None

    def get_depth(self) -> int:
        """Obtiene la profundidad máxima del árbol desde este nodo."""
        if not self.children:
            return 0
        return 1 + max(child.get_depth() for child in self.children)

@dataclass
class LevelInfo:
    """Información sobre un nivel específico en la jerarquía."""
    name: str
    label: str
    level: int
    xpath: str = ""
    fields: List[FieldModel] = field(default_factory=list)
    node: Optional[HierarchyNodeModel] = None
    repeat_count: str = ""
    parent_level: Optional[int] = None

    def get_column_names(self) -> List[str]:
        """Obtiene los nombres de columnas para este nivel."""
        columns = []

        # Agregar columnas de identificación
        for i in range(self.level + 1):
            if i == 0:
                columns.append('survey_id')
            else:
                columns.append(f'id_nivel_{i}')

        # Agregar columnas de campos
        for field in self.fields:
            columns.append(field.name)

        return columns

    def create_empty_dataframe(self) -> pd.DataFrame:
        """Crea un DataFrame vacío con las columnas apropiadas."""
        return pd.DataFrame(columns=self.get_column_names())

    def get_field_by_name(self, name: str) -> Optional[FieldModel]:
        """Busca un campo por nombre."""
        for field in self.fields:
            if field.name == name:
                return field
        return None

@dataclass
class FormStructure:
    """Estructura completa del formulario."""
    root: HierarchyNodeModel
    levels: Dict[str, LevelInfo] = field(default_factory=dict)
    field_mapping: Dict[str, FieldModel] = field(default_factory=dict)

    def add_level(self, level_key: str, level_info: LevelInfo) -> None:
        """Agrega información de un nivel."""
        self.levels[level_key] = level_info

        # Actualizar mapeo de campos
        for field in level_info.fields:
            self.field_mapping[field.name] = field

    def get_level_by_number(self, level_number: int) -> Optional[LevelInfo]:
        """Obtiene información de un nivel por su número."""
        level_key = f'nivel_{level_number}'
        return self.levels.get(level_key)

    def get_field_by_name(self, name: str) -> Optional[FieldModel]:
        """Busca un campo por nombre en todo el formulario."""
        return self.field_mapping.get(name)

    def get_max_level(self) -> int:
        """Obtiene el nivel máximo en la estructura."""
        if not self.levels:
            return 0
        return max(info.level for info in self.levels.values())

    def get_fields_by_type(self, field_type: FieldType) -> List[FieldModel]:
        """Obtiene todos los campos de un tipo específico."""
        return [field for field in self.field_mapping.values()
                if field.field_type == field_type]

    def get_repeat_levels(self) -> List[LevelInfo]:
        """Obtiene todos los niveles que corresponden a repeticiones."""
        return [info for info in self.levels.values()
                if info.node and info.node.is_repeat()]

    def generate_dataframes(self) -> Dict[str, pd.DataFrame]:
        """Genera DataFrames vacíos para todos los niveles."""
        return {
            level_key: level_info.create_empty_dataframe()
            for level_key, level_info in self.levels.items()
        }

class ValidationError(Exception):
    """Error de validación en la estructura del formulario."""
    pass

class FormValidator:
    """Validador para estructuras de formularios."""

    @staticmethod
    def validate_structure(structure: FormStructure) -> List[str]:
        """Valida la estructura del formulario y retorna una lista de errores."""
        errors = []

        # Validar que hay al menos un nivel
        if not structure.levels:
            errors.append("No se encontraron niveles en la estructura")

        # Validar nombres únicos de campos
        field_names = set()
        for field in structure.field_mapping.values():
            if field.name in field_names:
                errors.append(f"Campo duplicado: {field.name}")
            field_names.add(field.name)

        # Validar jerarquía de niveles
        for level_info in structure.levels.values():
            if level_info.parent_level is not None:
                parent_key = f'nivel_{level_info.parent_level}'
                if parent_key not in structure.levels:
                    errors.append(f"Nivel padre {parent_key} no encontrado para {level_info.name}")

        return errors

    @staticmethod
    def validate_field(field: FieldModel) -> List[str]:
        """Valida un campo específico."""
        errors = []

        if not field.name:
            errors.append("Campo sin nombre")

        if field.required and field.readonly:
            errors.append(f"Campo {field.name}: no puede ser requerido y solo lectura")

        return errors
