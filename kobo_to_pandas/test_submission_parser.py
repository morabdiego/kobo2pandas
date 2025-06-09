import os
import json
from dotenv import load_dotenv
from app import KoboAPI
import pandas as pd

load_dotenv()
API_KEY = os.getenv("API_KEY")

client = KoboAPI(token=API_KEY, debug=True)
uid = client.list_uid()['simple']

# Test using the new KoboAPI methods
def test_kobo_api_workflow():
    print("=" * 60)
    print("TESTING KoboAPI Workflow with new methods")
    print("=" * 60)

    try:
        print("🔍 Testing get_dataframes method...")

        # Test get_dataframes method
        dataframes = client.get_dataframes(uid)

        if not dataframes:
            print("❌ No DataFrames returned")
            return None

        print(f"✅ Datos procesados exitosamente")
        print(f"📊 Se generaron {len(dataframes)} DataFrames")
        print()

        # Mostrar información de cada DataFrame
        print("=== DATAFRAMES GENERADOS ===\n")
        for table_name, df in dataframes.items():
            print(f"📋 Tabla: {table_name}")
            print(f"   Dimensiones: {df.shape}")
            print(f"   Columnas ({len(df.columns)}):")
            for col in df.columns:
                print(f"     - {col}")
            print()

            # Mostrar primeras filas si hay datos
            if len(df) > 0:
                print(f"   Primeras {min(3, len(df))} filas:")
                print(df.head(3).to_string(index=False))
                print()

        # Análisis de trazabilidad
        print("=== ANÁLISIS DE TRAZABILIDAD ===\n")
        for table_name, df in dataframes.items():
            index_cols = [col for col in df.columns if col in ['_index', '_parent_index', '_parent_table']]
            if index_cols:
                print(f"🔗 {table_name}:")
                for col in index_cols:
                    if col == '_parent_table':
                        unique_values = df[col].unique().tolist() if col in df.columns else []
                        print(f"   - {col}: {unique_values}")
                    else:
                        unique_values = df[col].nunique() if col in df.columns else 0
                        print(f"   - {col}: {unique_values} valores únicos")
                print()

        return dataframes

    except Exception as e:
        print(f"❌ Error durante el procesamiento: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def test_excel_export():
    """Test the export_excel method"""
    print("=" * 60)
    print("TESTING export_excel method")
    print("=" * 60)

    try:
        # Test export with default filename
        print("🔄 Testing export with default filename...")
        success1 = client.export_excel(uid)

        if success1:
            print("✅ Export with default filename successful")
        else:
            print("❌ Export with default filename failed")

        # Test export with custom filename
        print("\n🔄 Testing export with custom filename...")
        custom_filename = "./data/custom_export.xlsx"
        success2 = client.export_excel(uid, custom_filename)

        if success2:
            print("✅ Export with custom filename successful")
        else:
            print("❌ Export with custom filename failed")

        return success1 and success2

    except Exception as e:
        print(f"❌ Error durante exportación: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🚀 Starting KoboAPI workflow tests...\n")

    # Test 1: Basic DataFrame generation
    dataframes = test_kobo_api_workflow()

    if dataframes:
        print("✅ Test 1 completado exitosamente!")
        print(f"📊 Total de DataFrames generados: {len(dataframes)}")

        # Mostrar resumen final
        total_records = sum(len(df) for df in dataframes.values())
        print(f"📈 Total de registros procesados: {total_records}")

        # Test 2: Excel export functionality
        print("\n")
        export_success = test_excel_export()

        if export_success:
            print("✅ Test 2 (Excel export) completado exitosamente!")
        else:
            print("❌ Test 2 (Excel export) falló")
