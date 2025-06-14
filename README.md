# Kobo2Pandas - Extractor de Datos de KoboToolbox

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-2.0.0-orange.svg)](https://github.com/your-repo/kobo2pandas)

Una librería Python minimalista y eficiente para extraer y procesar datos de KoboToolbox, aplicando principios SOLID y DRY para un código limpio y mantenible.

## 🚀 Características

- **API Simplificada**: Una sola clase `KoboAPI` con interfaz clara y concisa
- **Procesamiento Automático**: Convierte datos JSON anidados en DataFrames relacionados
- **Exportación a Excel**: Genera archivos Excel con múltiples hojas automáticamente
- **Configuración Flexible**: Personaliza el comportamiento mediante `ProcessingConfig`
- **Arquitectura Limpia**: Implementa principios SOLID para máxima mantenibilidad
- **Mínimas Dependencias**: Solo las librerías esenciales

## 📦 Instalación

```bash
pip install kobo2pandas
```

## 🔧 Uso Básico

```python
from kobo2pandas import KoboAPI

# Inicializar cliente
kobo = KoboAPI(token="tu_token_aqui", debug=True)

# Obtener lista de assets
assets = kobo.list_assets()
print(f"Assets disponibles: {len(assets)}")

# Procesar datos a DataFrames
asset_uid = "tu_asset_uid"
dataframes = kobo.get_dataframes(asset_uid)

# Exportar a Excel
kobo.export_excel(asset_uid, "mi_encuesta.xlsx")
```

## 📚 Referencia de API

### Clase Principal: `KoboAPI`

#### Constructor

```python
KoboAPI(token: str, endpoint: str = 'default', debug: bool = False)
```

**Parámetros:**
- `token` (str): Token de autenticación de KoboToolbox
- `endpoint` (str): Endpoint del servidor ('default', 'humanitarian', o URL personalizada)
- `debug` (bool): Habilita modo debug para logging detallado

### Métodos Públicos

#### 1. `list_assets() -> List[Dict[str, Any]]`
Lista todos los assets (formularios) disponibles en tu cuenta.

```python
assets = kobo.list_assets()
for asset in assets:
    print(f"Nombre: {asset['name']}, UID: {asset['uid']}")
```

#### 2. `list_uid() -> Dict[str, str]`
Retorna un mapeo de nombres de assets a sus UIDs.

```python
uid_mapping = kobo.list_uid()
asset_uid = uid_mapping['Mi Formulario']
```

#### 3. `get_asset(asset_uid: str) -> Dict[str, Any]`
Obtiene información detallada de un asset específico.

```python
asset = kobo.get_asset(asset_uid)
print(f"Creado: {asset['date_created']}")
print(f"Respuestas: {asset['deployment__submission_count']}")
```

#### 4. `get_data(asset_uid: str, **filters) -> Dict[str, Any]`
Obtiene los datos brutos de una encuesta con filtros opcionales.

```python
# Sin filtros
data = kobo.get_data(asset_uid)

# Con filtros
data = kobo.get_data(
    asset_uid,
    limit=100,
    start=0,
    submitted_after="2023-01-01"
)

# Con query personalizada
data = kobo.get_data(
    asset_uid,
    query='{"_submission_time": {"$gt": "2023-01-01"}}'
)
```

**Filtros disponibles:**
- `limit` (int): Número máximo de registros
- `start` (int): Índice de inicio para paginación
- `submitted_after` (str): Fecha en formato ISO (YYYY-MM-DD)
- `query` (str): Query MongoDB personalizada

#### 5. `get_dataframes(asset_uid: str, **kwargs) -> Optional[Dict[str, DataFrame]]`
Convierte los datos de la encuesta en DataFrames de pandas organizados por tabla.

```python
dataframes = kobo.get_dataframes(asset_uid, limit=50)

if dataframes:
    # Tabla principal
    main_data = dataframes['root']
    print(f"Registros principales: {len(main_data)}")

    # Tablas anidadas (si existen)
    for table_name, df in dataframes.items():
        if table_name != 'root':
            print(f"Tabla {table_name}: {len(df)} registros")
```

#### 6. `export_excel(asset_uid: str, filename: Optional[str] = None, **kwargs) -> bool`
Exporta los datos directamente a un archivo Excel con múltiples hojas.

```python
# Con nombre automático
success = kobo.export_excel(asset_uid)

# Con nombre personalizado
success = kobo.export_excel(asset_uid, "mi_archivo.xlsx")

# Con filtros
success = kobo.export_excel(
    asset_uid,
    "datos_filtrados.xlsx",
    limit=100,
    submitted_after="2023-01-01"
)
```

#### 7. `get_choices(asset: Dict[str, Any]) -> Dict[str, Dict[str, Any]]`
Extrae las opciones de selección múltiple de un formulario.

```python
asset = kobo.get_asset(asset_uid)
choices = kobo.get_choices(asset)

for list_name, options in choices.items():
    print(f"Lista: {list_name}")
    for value, info in options.items():
        print(f"  {value}: {info['label']}")
```

#### 8. `get_questions(asset: Dict[str, Any]) -> List[Dict[str, Any]]`
Extrae las preguntas del formulario.

```python
asset = kobo.get_asset(asset_uid)
questions = kobo.get_questions(asset)

for question in questions:
    print(f"Tipo: {question.get('type')}")
    print(f"Nombre: {question.get('name')}")
    print(f"Etiqueta: {question.get('label')}")
```

## 🎯 Ejemplos Avanzados

### Procesamiento Completo con Análisis

```python
from kobo2pandas import KoboAPI
import pandas as pd

# Configurar cliente
kobo = KoboAPI(token="tu_token", debug=True)

# Obtener mapeo de assets
assets = kobo.list_uid()
print("Assets disponibles:")
for name, uid in assets.items():
    print(f"  - {name}: {uid}")

# Procesar asset específico
asset_uid = assets['Mi Encuesta']
dataframes = kobo.get_dataframes(asset_uid)

if dataframes:
    # Análisis de la tabla principal
    main_df = dataframes['root']
    print(f"\n📊 Análisis de datos:")
    print(f"Total respuestas: {len(main_df)}")
    print(f"Columnas: {list(main_df.columns)}")

    # Análisis de tablas relacionadas
    for table_name, df in dataframes.items():
        if table_name != 'root':
            print(f"\n📋 Tabla {table_name}:")
            print(f"  Registros: {len(df)}")
            print(f"  Columnas: {list(df.columns)}")

    # Exportar todo a Excel
    success = kobo.export_excel(asset_uid, "analisis_completo.xlsx")
    if success:
        print("✅ Datos exportados exitosamente")
```

### Filtrado y Procesamiento por Fechas

```python
from datetime import datetime, timedelta

# Obtener datos de los últimos 30 días
fecha_limite = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

dataframes = kobo.get_dataframes(
    asset_uid,
    submitted_after=fecha_limite,
    limit=1000
)

if dataframes:
    main_df = dataframes['root']
    print(f"Respuestas últimos 30 días: {len(main_df)}")

    # Exportar con nombre descriptivo
    filename = f"datos_{fecha_limite}_a_hoy.xlsx"
    kobo.export_excel(asset_uid, filename, submitted_after=fecha_limite)
```

## 🛠️ Estructura de Datos

### DataFrames Generados

La librería convierte automáticamente datos JSON anidados en múltiples DataFrames relacionados:

- **Tabla `root`**: Contiene los campos principales de cada respuesta
- **Tablas anidadas**: Una por cada grupo repetible (ej: `root_miembros_familia`)
- **Columnas de relación**: `_index`, `_parent_index`, `_parent_table` para mantener trazabilidad

### Archivos Excel

Los archivos Excel generados contienen:
- Una hoja por cada DataFrame
- Nombres de hojas sanitizados (máximo 31 caracteres)
- Tabla principal en la primera hoja
- Orden lógico de las hojas relacionadas

## 🔍 Debugging

Habilita el modo debug para ver el proceso detalladamente:

```python
kobo = KoboAPI(token="tu_token", debug=True)

# Verás logs como:
# 🔄 Petición HTTP: https://kf.kobotoolbox.org/api/v2/assets.json
# 📊 Procesando 150 registros
# ✅ Generados 3 DataFrames:
#    📋 root: (150, 25)
#    📋 root_miembros: (380, 8)
#    📋 root_gastos: (520, 6)
```

## 📋 Requisitos

- Python 3.8+
- pandas
- requests
- openpyxl

## 🤝 Contribución

Las contribuciones son bienvenidas. Por favor:

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/amazing-feature`)
3. Commit tus cambios (`git commit -m 'Add amazing feature'`)
4. Push a la rama (`git push origin feature/amazing-feature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 🙏 Agradecimientos

- Equipo de KoboToolbox por su API
- [heiko-r/koboextractor](https://github.com/heiko-r/koboextractor) por la inspiración inicial y conceptos de extracción de datos de Kobo
