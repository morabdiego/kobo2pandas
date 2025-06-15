# kobo2pandas - Extractor de Datos de KoboToolbox

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Un paquete de python para acceder a la API de KoboToolbox y transformar las respuestas de las encuestas directamente a dataframes, recursivamente.

## 🚀 Características

- **Cliente de la API**: Acceso a principales características de la API oficial.
- **Procesamiento Automático**: Convierte datos JSON anidados en DataFrames relacionados
- **Exportación a Excel**: Genera archivos Excel con múltiples hojas automáticamente

## 📦 Instalación

```bash
pip install kobo2pandas
```

## 🔧 Uso Básico

```python
from kobo2pandas import KoboAPI

# Inicializar cliente
kobo = KoboAPI(token="TU_API_KEY", debug=True)

asset_uid = kobo.list_uid()['nombre_de_tu_encuesta']

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


#### 2. `list_uid() -> Dict[str, str]`
Retorna un mapeo de nombres de assets a sus UIDs.

```python
uid_mapping = kobo.list_uid()
asset_uid = uid_mapping['Mi Formulario']
```

#### 3. `get_asset(asset_uid: str) -> Dict[str, Any]`
Obtiene información detallada de un asset específico.


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

#### 5. `get_dataframes(asset_uid: str, **kwargs) -> Optional[List[DataFrame]]`
Convierte los datos de la encuesta en una lista de DataFrames de pandas organizados por tabla según niveles de anidación.

```python
dataframes = kobo.get_dataframes(asset_uid)
# Ahora devuelve una lista de DataFrames en lugar de un diccionario
for i, df in enumerate(dataframes):
    print(f"DataFrame {i}: {df.shape}")
```

#### 6. `export_excel(asset_uid: str, filename: Optional[str] = None, **kwargs) -> bool`
Exporta los datos directamente a un archivo Excel con tantas sheets commo niveles de anidación.

```python
# Con nombre automático
kobo.export_excel(asset_uid)

# Con nombre personalizado
kobo.export_excel(asset_uid, "mi_archivo.xlsx")
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

## 🛠️ Estructura de Datos

Los datos descargados desde la API convierten el JSON en pandas.DataFrame según nivel de anidación.
En el caso que existan más de un nivel de anidación, el return principal es una lista de los dataframes generados.
La relación entre los dataframes son idénticos a los generados por la herramienta de exportación de Kobo: _index, _parent_index y _parent_table para mantener las relaciones presentes en el JSON.

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
