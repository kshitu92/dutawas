# Variables
DOCKER_IMAGE = jekyll-site
DOCKER_TAG = latest
DOCKER_CONTAINER = jekyll-container
PORT = 4000

# Default target
.PHONY: all
all: build

# Build the Jekyll site locally
.PHONY: build
build:
	bundle install
	bundle exec jekyll build

# Test the site
.PHONY: test
test: build
	bundle exec ruby test/test_site.rb

# Serve the Jekyll site locally
.PHONY: serve
serve:
	bundle exec jekyll serve

# Clean the Jekyll build
.PHONY: clean
clean:
	bundle exec jekyll clean
	rm -rf _site
	rm -rf .jekyll-cache

# Docker commands
.PHONY: docker-build
docker-build:
	docker build -t $(DOCKER_IMAGE):$(DOCKER_TAG) .

.PHONY: docker-run
docker-run:
	docker run -p $(PORT):$(PORT) --name $(DOCKER_CONTAINER) $(DOCKER_IMAGE):$(DOCKER_TAG)

.PHONY: docker-stop
docker-stop:
	docker stop $(DOCKER_CONTAINER)
	docker rm $(DOCKER_CONTAINER)

# Development setup
.PHONY: setup
setup:
	gem install bundler
	bundle install

# CI checks
.PHONY: ci-local
ci-local:
	docker run --rm -v "$(PWD):/app" -w /app ruby:3.3 bash -c "rm -f Gemfile.lock && bundle install && bundle exec jekyll build && bundle exec ruby test/test_site.rb"

# Help target
.PHONY: help
help:
	@echo "Available targets:"
	@echo "  build         - Build the Jekyll site locally"
	@echo "  serve         - Serve the Jekyll site locally"
	@echo "  clean         - Clean the Jekyll build"
	@echo "  test          - Run tests"
	@echo "  docker-build  - Build Docker image"
	@echo "  docker-run    - Run Docker container"
	@echo "  docker-stop   - Stop and remove Docker container"
	@echo "  setup         - Install dependencies"
	@echo "  ci-local      - Run CI checks locally"