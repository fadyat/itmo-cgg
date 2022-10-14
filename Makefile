ui:
	python cli.py ui


ref:
	flake8 . --exclude=docs,scripts --max-line-length=100 && black -S .

tests:
	docker-compose up --build tests