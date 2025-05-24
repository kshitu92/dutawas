require 'minitest/autorun'
require 'jekyll'
require 'html-proofer'

class SiteTest < Minitest::Test
  def setup
    @site_dir = File.expand_path('../_site', __dir__)
  end

  def test_site_builds
    assert(File.directory?(@site_dir), "_site directory should exist")
    assert(File.exist?(File.join(@site_dir, 'index.html')), "index.html should exist")
  end

  def test_consulate_pages_exist
    required_pages = ['washington-state.html', 'boston.html', 'new-york.html']
    required_pages.each do |page|
      assert(File.exist?(File.join(@site_dir, 'consulates', page)), "#{page} should exist")
    end
  end

  def test_html_proofer
    options = { 
      :assume_extension => true,
      :check_html => true,
      :disable_external => true
    }
    HTMLProofer.check_directory(@site_dir, options).run
  end
end
