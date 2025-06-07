import os
import json
from dotenv import load_dotenv
from app import KoboAPI
from xlsform_parser.xlsforrm_parser import parse_xlsform_to_dataframes

load_dotenv()
API_KEY = os.getenv("API_KEY")
client = KoboAPI(token=API_KEY, debug=True)

uid = client.list_uid()['simple']
survey = client.get_asset(asset_uid=uid)['content']['survey']

# Test del XLSForm Parser
def test_xlsform_parser():
    print("=" * 60)
    print("TESTING XLSForm Parser")
    print("=" * 60)

    try:
        # Parsear la estructura del formulario
        parser, dataframes = parse_xlsform_to_dataframes(survey)

        # Mostrar resumen de la estructura
        parser.print_structure_summary()

        # Mostrar árbol de jerarquía
        parser.print_hierarchy_tree()

        # Mostrar información de DataFrames generados
        print("=== DATAFRAMES GENERADOS ===\n")
        for nivel_key, df in dataframes.items():
            print(f"📊 DataFrame: {nivel_key}")
            print(f"   Columnas ({len(df.columns)}): {list(df.columns)}")
            print(f"   Filas: {len(df)}")
            print()

        # Mostrar información detallada de campos
        field_info = parser.get_field_info()
        print("=== INFORMACIÓN DETALLADA DE CAMPOS ===\n")
        for nivel_key, info in field_info.items():
            print(f"📋 {nivel_key}:")
            print(f"   Nivel: {info['nivel_info']['level']}")
            print(f"   Nombre: {info['nivel_info']['name']}")
            print(f"   Etiqueta: {info['nivel_info']['label']}")
            print(f"   Campos: {len(info['fields'])}")
            for field in info['fields']:
                flags = []
                if field.get('required', False):
                    flags.append("requerido")
                if field.get('readonly', False):
                    flags.append("solo lectura")
                flag_str = f" ({', '.join(flags)})" if flags else ""
                print(f"     - {field['name']} ({field['type']}){flag_str}")
            print()

        return parser, dataframes

    except Exception as e:
        print(f"❌ Error durante el test: {str(e)}")
        import traceback
        traceback.print_exc()
        return None, None

if __name__ == "__main__":
    # Ejecutar el test
    parser, dataframes = test_xlsform_parser()

    if parser and dataframes:
        print("✅ Test completado exitosamente!")
        print(f"📊 Se generaron {len(dataframes)} DataFrames")
        print(f"🏗️ Se identificaron {len(parser.structure.levels)} niveles de estructura")
    else:
        print("❌ Test falló")
