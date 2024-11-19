APP_NAME = CS437FinalProject
VENV_DIR = venv

# Default target
.PHONY: all
all: run

# Create virtual environment and install dependencies
.PHONY: setup
setup:
	python3 -m venv venv
	. venv/bin/activate && pip install --upgrade pip
	. venv/bin/activate && pip install -r requirements.txt

# Initialize the database
.PHONY: init-db
init-db:
	python -c "from app import create_app, db; app = create_app(); with app.app_context(): db.create_all()"

# Run the Flask development server
.PHONY: run
run:
	. venv/bin/activate && python run.py

# Clean up generated files
.PHONY: clean
clean:
	rm -rf $(VENV_DIR)
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete
	rm -f *.db

# Export data to CSV
.PHONY: export-data
export-data:
	$(PYTHON) -c "from app import create_app, db; app = create_app(); with app.app_context(): print('Exporting...')"

# Help target
.PHONY: help
help:
	@echo "Usage:"
	@echo "  make setup       - Set up the virtual environment and install dependencies"
	@echo "  make init-db     - Initialize the database"
	@echo "  make run         - Run the Flask development server"
	@echo "  make clean       - Remove generated files and clean the project"
	@echo "  make export-data - Export data to CSV"
