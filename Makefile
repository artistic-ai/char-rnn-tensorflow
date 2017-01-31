.PHONY: all

PROJECT_DIR = $(CURDIR)


setup: download-datasets setup-server

setup-server:
	@./run.py setup_server

download-datasets:
	@./main.py --datasets-all

nginx:
	@nginx -c $(PROJECT_DIR)/server/nginx.conf

redis:
	@redis-server $(PROJECT_DIR)/server/redis.conf

app:
	@./run.py app --reverse_samples

samples-server:
	@./run.py samples_server --reverse_samples
