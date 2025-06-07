import pandas as pd
import json
from typing import Dict, List, Tuple, Any, Optional
from .models import (
    HierarchyNodeModel, NodeType, FieldModel, FieldType,
    LevelInfo, FormStructure, FormValidator, ValidationError
)

class XLSFormParser:
    """
    Parser optimizado para estructuras XLSForm de KoBoToolbox que genera DataFrames
    separados por cada nivel de anidación (grupos y repeticiones).
    """

    def __init__(self, xlsform_data: List[Dict]):
        """
        Inicializa el parser con los datos del XLSForm.

        Args:
            xlsform_data: Lista de diccionarios del XLSForm
        """
        self.xlsform_data = xlsform_data
        self.structure = FormStructure(
            root=HierarchyNodeModel("root", NodeType.ROOT, -1)
        )

    def _build_hierarchy_tree(self, items: List[Dict], start_index: int = 0,
                             parent_node: HierarchyNodeModel = None,
                             current_level: int = 0) -> int:
        """
        Construye recursivamente el árbol de jerarquía usando modelos optimizados.

        Args:
            items: Lista de elementos del formulario
            start_index: Índice de inicio en la lista
            parent_node: Nodo padre actual
            current_level: Nivel actual en la jerarquía

        Returns:
            Índice donde terminó el procesamiento
        """
        if parent_node is None:
            parent_node = self.structure.root

        i = start_index
        while i < len(items):
            item = items[i]
            item_type = item.get('type', '')
            name = item.get('name', '')
            xpath = item.get('$xpath', '')
            label = item.get('label', [''])[0] if item.get('label') else ''

            if item_type == 'begin_group':
                # Crear nodo de grupo
                group_node = HierarchyNodeModel(
                    name=name,
                    node_type=NodeType.GROUP,
                    level=current_level,
                    label=label,
                    xpath=xpath,
                    appearance=item.get('appearance', ''),
                    relevant=item.get('relevant', '')
                )
                parent_node.add_child(group_node)

                # Procesar recursivamente el contenido del grupo
                i = self._build_hierarchy_tree(items, i + 1, group_node, current_level)

            elif item_type == 'begin_repeat':
                # Crear nodo de repetición (nuevo nivel)
                repeat_node = HierarchyNodeModel(
                    name=name,
                    node_type=NodeType.REPEAT,
                    level=current_level + 1,
                    label=label,
                    xpath=xpath,
                    repeat_count=item.get('repeat_count', '')
                )
                parent_node.add_child(repeat_node)

                # Procesar recursivamente el contenido de la repetición
                i = self._build_hierarchy_tree(items, i + 1, repeat_node, current_level + 1)

            elif item_type in ['end_group', 'end_repeat']:
                # Finalizar el procesamiento del grupo/repetición actual
                return i

            elif FieldType.from_string(item_type) in FieldType:
                # Crear modelo de campo optimizado
                field_model = FieldModel.from_dict(item, current_level)
                parent_node.add_field(field_model)

            i += 1

        return i

    def _extract_levels_from_tree(self, node: HierarchyNodeModel = None):
        """
        Extrae recursivamente los niveles del árbol de jerarquía.

        Args:
            node: Nodo actual (por defecto la raíz)
        """
        if node is None:
            node = self.structure.root

        # Procesar el nodo actual si es relevante
        if node.node_type in [NodeType.ROOT, NodeType.REPEAT] or (node.is_group() and node.fields):
            level_key = f'nivel_{max(0, node.level)}'

            if level_key not in self.structure.levels:
                level_info = LevelInfo(
                    name=node.name,
                    label=node.label,
                    level=max(0, node.level),
                    xpath=node.xpath,
                    node=node
                )

                if node.is_repeat():
                    level_info.repeat_count = node.repeat_count
                    level_info.parent_level = node.level - 1

                self.structure.add_level(level_key, level_info)

            # Agregar campos del nodo actual
            self.structure.levels[level_key].fields.extend(node.fields)

        # Procesar recursivamente los hijos
        for child in node.children:
            self._extract_levels_from_tree(child)

    def analyze_structure(self) -> FormStructure:
        """
        Analiza la estructura del formulario y identifica los niveles de anidación.

        Returns:
            FormStructure con información de cada nivel
        """
        # Construir el árbol de jerarquía
        self._build_hierarchy_tree(self.xlsform_data)

        # Extraer niveles del árbol
        self._extract_levels_from_tree()

        # Validar la estructura
        errors = FormValidator.validate_structure(self.structure)
        if errors:
            print("⚠️ Advertencias de validación:")
            for error in errors:
                print(f"   - {error}")

        return self.structure

    def get_structure(self) -> FormStructure:
        """
        Obtiene la estructura del formulario.

        Returns:
            FormStructure con modelos optimizados
        """
        return self.structure

    def generate_dataframe_structure(self) -> Dict[str, pd.DataFrame]:
        """
        Genera la estructura de DataFrames para cada nivel.

        Returns:
            Dict con DataFrames vacíos para cada nivel
        """
        return self.structure.generate_dataframes()

    def get_field_info(self) -> Dict[str, Dict]:
        """
        Obtiene información detallada de todos los campos por nivel.

        Returns:
            Dict con información de campos por nivel
        """
        field_info = {}

        for level_key, level_info in self.structure.levels.items():
            field_info[level_key] = {
                'nivel_info': {
                    'name': level_info.name,
                    'label': level_info.label,
                    'level': level_info.level
                },
                'fields': [
                    {
                        'name': field.name,
                        'type': field.field_type.value,
                        'label': field.label,
                        'xpath': field.xpath,
                        'level': field.level,
                        'required': field.required,
                        'readonly': field.readonly
                    }
                    for field in level_info.fields
                ]
            }

        return field_info

    def print_structure_summary(self):
        """
        Imprime un resumen de la estructura analizada.
        """
        print("=== RESUMEN DE ESTRUCTURA XLSForm ===\n")

        for level_key, level_info in self.structure.levels.items():
            print(f"📊 {level_key.upper()}")
            print(f"   Nombre: {level_info.name}")
            print(f"   Etiqueta: {level_info.label}")
            print(f"   Nivel de anidación: {level_info.level}")

            if level_info.parent_level is not None:
                print(f"   Nivel padre: {level_info.parent_level}")

            print(f"   Campos ({len(level_info.fields)}):")
            for field in level_info.fields:
                flags = []
                if field.required:
                    flags.append("requerido")
                if field.readonly:
                    flags.append("solo lectura")
                flag_str = f" ({', '.join(flags)})" if flags else ""

                print(f"     - {field.name} ({field.field_type.value}): {field.label}{flag_str}")
            print()

    def print_hierarchy_tree(self, node: HierarchyNodeModel = None, indent: str = ""):
        """
        Imprime recursivamente el árbol de jerarquía.

        Args:
            node: Nodo actual (por defecto la raíz)
            indent: Indentación actual
        """
        if node is None:
            node = self.structure.root
            print("=== ÁRBOL DE JERARQUÍA ===\n")

        if not node.is_root():
            node_type_icon = "🔁" if node.is_repeat() else "📁"
            print(f"{indent}{node_type_icon} {node.name} ({node.node_type.value}) - Nivel {node.level}")

            if node.fields:
                for field in node.fields:
                    field_icon = "📄"
                    if field.required:
                        field_icon = "📋"
                    elif field.readonly:
                        field_icon = "🔒"
                    print(f"{indent}  {field_icon} {field.name} ({field.field_type.value})")

        for child in node.children:
            self.print_hierarchy_tree(child, indent + "  ")


# Función de uso principal
def parse_xlsform_to_dataframes(xlsform_data: List[Dict]) -> Tuple[XLSFormParser, Dict[str, pd.DataFrame]]:
    """
    Función principal para parsear XLSForm y generar DataFrames.

    Args:
        xlsform_data: Datos del XLSForm

    Returns:
        Tupla con el parser y los DataFrames vacíos
    """
    parser = XLSFormParser(xlsform_data)
    parser.analyze_structure()
    dataframes = parser.generate_dataframe_structure()

    return parser, dataframes
