ui:
	python cli.py ui


ref:
	black -S .

# fixme: ui build in docker
dui:
	docker-compose up --build app