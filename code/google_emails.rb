#!/usr/bin/env ruby
#
# google_email.rb v0.2 by Postmodern (postmodern at sophsec.com)
#

gem 'gscraper', '>=0.1.7'
require 'gscraper/search'

module SophSec
  module Google
    include GScraper

    #
    # Scrapes Google Search for email addresses ending in the specified
    # _domain_ and the given _options_. If a _block_ is given it will be
    # passed each scraped email.
    #
    # _options_ may contain the following keys:
    # <tt>:page</tt>:: The page to scrape, defaults to 1.
    #
    # _options_ may also contain keys used for GScraper::Search::Query.new.
    #
    def self.emails(domain,options={},&block)
      index = (options[:page] || 1)

      all_emails = []

      sanitize = lambda { |email|
        # de-obfusticate email addresses
        email.gsub(/(\s+|\[\s*)at((\s+|-)?sign)?(\s*\]|\s+)/i,'@').gsub(/(\s+|\[\s*)dot(\s*\]|\s+)/i,'.')
      }

      Search.query(options.merge(:query => "@#{domain}")).each_on_page(index) do |result|
        page = result.page

        # xpath to find hrefs that begin with mailto: and ends with the _domain_
        links = page.search("a[@href ^= \"mailto:\"][@href $= \"#{domain}\"]")

        # xpath to get bold tags ending with the _domain_
        bolds = page.search("b[text() $= \"#{domain}\"]")

        emails = (links.map { |a|
          sanitize.call(a['href']).sub('mailto:','')
        } + bolds.map { |b|
          sanitize.call(b.inner_text)
        })

        emails.each(&block) if block
        all_emails += emails
      end

      return all_emails
    end
  end
end

if File.basename($0)=='google_emails.rb'
  require 'optparse'

  index = 1

  opts = OptionParser.new do |opts|
    opts.banner = 'usage: google_emails.rb [options] DOMAIN'

    opts.on('-p','--page [NUM]','page index') do |page|
      index = page
    end

    opts.on('-h','--help','this cruft') do
      puts opts
      exit
    end
  end

  unless (domain = (opts.parse!).first)
    STDERR.puts(opts)
    exit -1
  end

  SophSec::Google.emails(domain,:page => index).each { |email| puts email }
end
