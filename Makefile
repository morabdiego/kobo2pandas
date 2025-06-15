.PHONY: clean uninstall build install all

PACKAGE_NAME=kobo2pandas

clean:
	echo "🧹 Limpiando dist/, egg-info, __pycache__, pytest_cache y smoke output..."
	rm -rf dist/ *.egg-info
	find . -type d -name "__pycache__" -exec rm -r {} + || true

uninstall:
	echo "❌ Desinstalando paquete si está instalado..."
	pip uninstall -y $(PACKAGE_NAME) || true

build: clean
	echo "📦 Construyendo paquete..."
	python -m build

install: uninstall build
	echo "📥 Instalando paquete desde dist/*.whl..."
	pip install dist/*.whl

all: clean uninstall build install
	echo "🏁 Proceso completo (build, install, test, smoke) terminado."
