setup:
	python3 -m venv venv
	@echo "Installing python dependencies..."
	. venv/bin/activate && pip install -r requirements.txt
	@echo "Installing npm dependencies..."
	npm install
	@echo "Copying .env.example to .env..."
	cp .env.example .env
	@echo "Setup complete."
	. venv/bin/activate
	@echo "Building frontend assets..."
	npm run build

run:
	@echo "Starting development server at http://127.0.0.1:8000/"
	@. venv/bin/activate && python3 manage.py runserver