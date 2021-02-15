.PHONY: run

ENV ?= venv_debian
PYTHON ?= $(ENV)/bin/python
FLASK ?= $(ENV)/bin/flask
FLASK_ENV ?= development
CELERY ?= $(ENV)/bin/celery
CELERY_APP ?= celery_app
PIP ?= $(ENV)/bin/pip
PROJECT_PATH ?= src
CELERY_PARAMS ?=
LOGS_PATH ?= /app/logs
WORKER_NAME ?= worker-celery

export LC_ALL=en_US.utf-8
export LANG=en_US.utf-8

run-server: install
	FLASK_APP=$(PROJECT_PATH)/server.py FLASK_ENV=$(FLASK_ENV) $(FLASK) run --host=0.0.0.0

install: .install
.install: requirements.txt
	$(PIP) install -r requirements.txt
	touch $@

run-worker: install
	PYTHONPATH=$(PROJECT_PATH) $(CELERY) -A $(CELERY_APP) worker -l info $(CELERY_PARAMS)

run-celery-beat: install
	PYTHONPATH=$(PROJECT_PATH) $(CELERY) -A $(CELERY_APP) beat -l info $(CELERY_PARAMS)

celery-command: install
	PYTHONPATH=$(PROJECT_PATH) $(CELERY) -A $(CELERY_APP) $(CELERY_PARAMS)

shell:
	PYTHONPATH=$(PROJECT_PATH) $(PYTHON)

celery-multi-start: install
	$(CELERY) multi start $(WORKER_NAME) $(CELERY_PARAMS) \
	-A $(CELERY_APP) --workdir=/app/$(PROJECT_PATH) --pidfile=$(LOGS_PATH)/celery-%n.pid --logfile=$(LOGS_PATH)/celery-%n.log

celery-multi-reload: install
	$(CELERY) multi restart $(WORKER_NAME) $(CELERY_PARAMS) \
	-A $(CELERY_APP) --workdir=/app/$(PROJECT_PATH) --pidfile=$(LOGS_PATH)/celery-%n.pid --logfile=$(LOGS_PATH)/celery-%n.log

celery-multi-stop: install
	$(CELERY) multi stopwait $(WORKER_NAME) $(CELERY_PARAMS) -A $(CELERY_APP) \
	--workdir=/app/$(PROJECT_PATH) --pidfile=$(LOGS_PATH)/celery-%n.pid --logfile=$(LOGS_PATH)/celery-%n.log

pip-freeze:
	$(PIP) freeze

run-real-time-monitor: install
	PYTHONPATH=$(PROJECT_PATH) $(PYTHON) $(PROJECT_PATH)/celery_real_time_monitor.py

run-camera-monitor: install
	PYTHONPATH=$(PROJECT_PATH) $(PYTHON) $(PROJECT_PATH)/celery_camera_monitor.py
