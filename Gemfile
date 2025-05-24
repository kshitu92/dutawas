source 'https://rubygems.org'

gem "jekyll", "~> 4.4.1" # installed by `gem jekyll`
# gem "webrick"        # required when using Ruby >= 3 and Jekyll <= 4.2.2

gem "just-the-docs", "0.10.1" # pinned to the current release
# gem "just-the-docs"        # always download the latest release

group :test do
  gem 'minitest'
  gem 'html-proofer'
end

# Platform specific dependencies
platforms :ruby, :mswin, :mingw, :x64_mingw do
  gem 'ffi'
  gem 'sassc'
end
