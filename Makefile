
# PREREQUISITES


# ------------------------------------------------
# Variables – can be overridden on the command line
# ------------------------------------------------

APP_MODE ?= dev
export APP_MODE

COMPOSE_FILE ?= docker-compose.yml

# Conditionally set environment variables based on APP_MODE
ifeq ($(APP_MODE), dev)
    # export DB_HOST=db
endif

COMPOSE = \
	DB_HOST=$(DB_HOST) \
	docker-compose -f $(COMPOSE_FILE)

# ------------------------------------------------
# ------------------------------------------------

.PHONY: build
build: ## Builds services
	@echo "Building services in $(APP_MODE) mode..."
	$(COMPOSE) build

.PHONY: up run
up run: ## Starts db and app services
	@echo "Starting services in $(APP_MODE) mode..."
	$(COMPOSE) up 

.PHONY: stop
stop: ## Stops services
	@echo "Stopping services..."
	$(COMPOSE) down 
	@rmdir -v app/tests/

.PHONY: clean-up
clean-up: ## Cleans up Docker containers and volumes
	@echo "Cleaning up..."
	$(COMPOSE) down -v

.PHONY: restart
restart: stop run   ## Restart the stack

.PHONY: test-logs
show-logs: 
	@echo "Getting logs for the test service"
	$(COMPOSE) logs test

.PHONY: test
test: ## Run tests
	@echo "Running pytest (in a container)..."
	@docker-compose exec test pytest tests/ -v

.PHONY: test-with-html-report
test-with-html-report:
  @docker-compose exec test pip install pytest-html
	@docker-compose exec test pytest tests --no-cov  --disable-warnings --html=report.html --self-contained-html

.PHONY: copy-report-to-local-machine
copy-report-to-local-machine:
	@docker cp $(docker-compose ps -q test):/app/report.html ./report.html

# ---

# Start SonarQube container
.PHONY: sonar-up
sonar-up:
	# @docker network create sonarqube_network || true
	# @docker run --name postgres_for_sonarqube  \
	# 	-d  \
	# 	-e POSTGRES_USER=sonar  \
	# 	-e POSTGRES_DB=sonar \
	# 	-e POSTGRES_PASSWORD=Test12345  \
	# 	-p 5432:5432  \
	# 	-v postgres_data:/var/lib/postgresql/data  \
	# 	--network sonarqube_network  \
	# 	postgres:alpine

	# @sleep 20

	@docker run --name sonarqube \
		-d \
		-p 9000:9000  \
		-e sonar.jdbc.url=jdbc:postgresql://postgres_for_sonarqube/sonar  \
		-e sonar.jdbc.username=sonar  \
		-e sonar.jdbc.password=Test12345  \
		--network sonarqube_network \
		-v sonarqube_data:/opt/sonarqube/data \
		sonarqube


.PHONY: sonar-clean-all
sonar-clean-all:
	@echo "Stopping and removing SonarQube container..."
	@docker stop sonarqube && docker rm sonarqube || true

	@echo "Stopping and removing PostgreSQL container..."
	@docker stop postgres_for_sonarqube && docker rm postgres_for_sonarqube


.PHONY: sonar-scan
sonar-scan:
	@pysonar \
		--sonar-host-url=http://localhost:9000 \
		--sonar-token=sqp_250a5ce48b29dd6caade31a5c318b9fe87170fc4 \
		--sonar-project-key=testing_part_11
