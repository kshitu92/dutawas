# Use Ruby as base image
FROM ruby:3.3-slim

# Install required dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy Gemfile and Gemfile.lock
COPY Gemfile* ./

# Install bundler and gems
RUN gem install bundler && \
    bundle install

# Copy the rest of the application
COPY . .

# Build the site
RUN bundle exec jekyll build

# Expose port 4000 for Jekyll server
EXPOSE 4000

# Start Jekyll server
CMD ["bundle", "exec", "jekyll", "serve", "--host", "0.0.0.0"]