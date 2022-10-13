ui:
	python cli.py ui


ref:
	flake8 . --exclude=docs,scripts --max-line-length=100 && black -S .

# fixme: ui build in docker
dui:
	docker-compose up --build app