setup:
	python3 -m venv venv
	@echo "Installing python dependencies..."
	. venv/bin/activate && pip install -r requirements.txt
	@echo "Setup complete. Activate venv with: . venv/bin/activate"

run:
	@echo "Starting development server at http://127.0.0.1:8000/"
	@. venv/bin/activate && python3 manage.py runserver
