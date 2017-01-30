.PHONY: all

PROJECT_DIR = $(CURDIR)


setup-server:
	@./run.py setup_server

nginx: setup-server
	@nginx -c $(PROJECT_DIR)/server/nginx.conf
