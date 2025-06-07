# Variables
VENV_DIR = .venv
PYTHON = python3
PIP = $(VENV_DIR)/bin/pip
PYTHON_VENV = $(VENV_DIR)/bin/python

# Crear entorno virtual
env:
	$(PYTHON) -m venv $(VENV_DIR)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "Entorno virtual creado en $(VENV_DIR)"
	@echo "Para activar: source $(VENV_DIR)/bin/activate"

# Limpiar archivos generados
clean:
	find . -name "*.json" -type f -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +
	@echo "Archivos JSON y directorios __pycache__ eliminados"

# Limpiar entorno virtual
clean-env:
	rm -rf $(VENV_DIR)
	@echo "Entorno virtual eliminado"

# Reinstalar entorno
reinstall: clean-env env

# Activar entorno (helper)
activate:
	@echo "Para activar el entorno virtual ejecuta:"
	@echo "source $(VENV_DIR)/bin/activate"

.PHONY: env clean clean-env reinstall activate
