---
layout: page
title: Exploring the Google AJAX Search API
---

# Exploring the Google AJAX Search API

## Authors

* [postmodern](mailto:postmodern at sophsec.com)
* [cd](mailto:cd at sophsec.com)

## Introduction

The [Google AJAX Search API](http://code.google.com/apis/ajaxsearch/)
is a Javascript library that allows web-developers to embed Google Search
dialogues into web-pages. The API utilizes a publically exposed RESTful
web-service which returns the search results in
[JSON (Javascript Serialization Object Notation)][http://www.json.org/]
format. This fact makes the API particularly easy to interface with in
non-Javascript environments. 

The API provides the ability for performing Search queries against a number
of Google services. Such services currently include
[Web Search](http://www.google.com/),
[Local Search](http://maps.google.com/),
[Video Search](http://video.google.com/),
[Blog Search](http://blogsearch.google.com/),
[News Search](http://news.google.com/),
[Book Search](http://books.google.com/) and
[Image Search](http://images.google.com/).

In this document we will be focusing only on the
[Web Search](http://code.google.com/apis/ajaxsearch/web.html)
functionality of the API.

## Disecting the RESTful URLs

We can begin by disecting the
[Web Search](http://code.google.com/apis/ajaxsearch/web.html)
functionality of the API. We will be specifically looking at the RESTful
URLs the API is using and howto construct our own. The example we will begin
disecting is the
[Simple Search Box](http://www.google.com/uds/samples/apidocs/helloworld.html).

Immediately we can see that the Simple Search Box returns results from
Local, Web, Video, Blog, News, Image and Book Search Services. But where
are these results being requested from, we will use
[Tamper Data](https://addons.mozilla.org/en-US/firefox/addon/966)
to find which URLs are actually being requested. Tamper Data shows that the following seven AJAX requests are being made which return text/javascript.

* [http://www.google.com/uds/GlocalSearch?callback=google.search.LocalSearch.RawCompletion&context=0&lstkp=0&rsz=small&hl=en&gss=.com&sig=c8b58b9f22a4c2eca4342449dba29b6f&q=ruby&sll=40.71453,-74.00713&sspn=0.23791,0.30675&gll=40682767,-74038892,40746292,-73975367&llsep=500,500&key=notsupplied&v=1.0](http://www.google.com/uds/GlocalSearch?callback=google.search.LocalSearch.RawCompletion&context=0&lstkp=0&rsz=small&hl=en&gss=.com&sig=c8b58b9f22a4c2eca4342449dba29b6f&q=ruby&sll=40.71453,-74.00713&sspn=0.23791,0.30675&gll=40682767,-74038892,40746292,-73975367&llsep=500,500&key=notsupplied&v=1.0)
* [http://www.google.com/uds/GwebSearch?callback=google.search.WebSearch.RawCompletion&context=0&lstkp=0&rsz=small&hl=en&gss=.com&sig=c8b58b9f22a4c2eca4342449dba29b6f&q=ruby&key=notsupplied&v=1.0](http://www.google.com/uds/GwebSearch?callback=google.search.WebSearch.RawCompletion&context=0&lstkp=0&rsz=small&hl=en&gss=.com&sig=c8b58b9f22a4c2eca4342449dba29b6f&q=ruby&key=notsupplied&v=1.0)
* [http://www.google.com/uds/GvideoSearch?callback=google.search.VideoSearch.RawCompletion&context=0&lstkp=0&rsz=small&hl=en&gss=.com&sig=c8b58b9f22a4c2eca4342449dba29b6f&q=ruby&key=notsupplied&v=1.0](http://www.google.com/uds/GvideoSearch?callback=google.search.VideoSearch.RawCompletion&context=0&lstkp=0&rsz=small&hl=en&gss=.com&sig=c8b58b9f22a4c2eca4342449dba29b6f&q=ruby&key=notsupplied&v=1.0)
* [http://www.google.com/uds/GblogSearch?callback=google.search.BlogSearch.RawCompletion&context=0&lstkp=0&rsz=small&hl=en&gss=.com&sig=c8b58b9f22a4c2eca4342449dba29b6f&q=ruby&key=notsupplied&v=1.0](http://www.google.com/uds/GblogSearch?callback=google.search.BlogSearch.RawCompletion&context=0&lstkp=0&rsz=small&hl=en&gss=.com&sig=c8b58b9f22a4c2eca4342449dba29b6f&q=ruby&key=notsupplied&v=1.0)
* [http://www.google.com/uds/GnewsSearch?callback=google.search.NewsSearch.RawCompletion&context=0&lstkp=0&rsz=small&hl=en&gss=.com&sig=c8b58b9f22a4c2eca4342449dba29b6f&q=ruby&key=notsupplied&v=1.0](http://www.google.com/uds/GnewsSearch?callback=google.search.NewsSearch.RawCompletion&context=0&lstkp=0&rsz=small&hl=en&gss=.com&sig=c8b58b9f22a4c2eca4342449dba29b6f&q=ruby&key=notsupplied&v=1.0)
* [http://www.google.com/uds/GimageSearch?callback=google.search.ImageSearch.RawCompletion&context=0&lstkp=0&rsz=small&hl=en&gss=.com&sig=c8b58b9f22a4c2eca4342449dba29b6f&q=ruby&key=notsupplied&v=1.0](http://www.google.com/uds/GimageSearch?callback=google.search.ImageSearch.RawCompletion&context=0&lstkp=0&rsz=small&hl=en&gss=.com&sig=c8b58b9f22a4c2eca4342449dba29b6f&q=ruby&key=notsupplied&v=1.0).
* [http://www.google.com/uds/GbookSearch?callback=google.search.BookSearch.RawCompletion&context=0&lstkp=0&rsz=small&hl=en&gss=.com&sig=c8b58b9f22a4c2eca4342449dba29b6f&q=ruby&key=notsupplied&v=1.0](http://www.google.com/uds/GbookSearch?callback=google.search.BookSearch.RawCompletion&context=0&lstkp=0&rsz=small&hl=en&gss=.com&sig=c8b58b9f22a4c2eca4342449dba29b6f&q=ruby&key=notsupplied&v=1.0)

Judging from the paths of the URLs the second URL is the one which returns
the Web Search results.

    http://www.google.com/uds/GwebSearch?callback=google.search.WebSearch.RawCompletion&context=0&lstkp=0&rsz=small&hl=en&gss=.com&sig=c8b58b9f22a4c2eca4342449dba29b6f&q=ruby&key=notsupplied&v=1.0

First lets inspect the URL query parameters that are being passed to `http://www.google.com/uds/GwebSearch`:

* `v=1.0`: The desired version of functionality.
* `lstkp=0`: The offset of the returned Search results.
* `rsz=small`: The amount of search results to return. The value of small
  returns four results per request, and the value of large returns eight
  results per request.
* `hl=en`: The language to return results in.
* `callback=google.search.WebSearch.RawCompletion`: Used in the returned
  Javascript.
* `q=ruby`: The Search query.
* `sig=c8b58b9f22a4c2eca4342449dba29b6f`.
* `gss=.com`.
* `context=0`: Used in constructing the callback Javascript.
* `key=notsupplied`: An optional API key.

## Analyzing the JSON

Now that we have some understanding of the structure of the RESTful URL, we
can begin constructing our own URLs and analyzing the resulting JSON they
return. For this task we will write a small Ruby method and test it in
[irb (Interactive Ruby Shell)](http://en.wikipedia.org/wiki/Interactive_Ruby_Shell).

    require 'uri'
    require 'net/http'
    
    module SophSec
      def SophSec.get_ajax_search(options={})
        options[:callback] ||= 'google.search.WebSearch.RawCompletion'
        options[:context] ||= 0
        options[:lstkp] ||= 0
        options[:rsz] ||= 'large'
        options[:hl] ||= 'en'
        options[:gss] ||= '.com'
        options[:start] ||= 0
        options[:sig] ||= '582c1116317355adf613a6a843f19ece'
        options[:key] ||= 'notsupplied'
        options[:v] ||= '1.0'
    
        url = URI("http://www.google.com/uds/GwebSearch?" + options.map { |key,value|
          "#{key}=#{value}"
        }.join('&'))
    
        return Net::HTTP.get(url)
      end
    end

The `SophSec.get_ajax_search` method will build the RESTful URL and request
the results from the Web Search API.

    irb(main):024:0> SophSec.get_ajax_search(:q => 'ruby', :rsz => 'small')
    => "google.search.WebSearch.RawCompletion('0',{\"results\":[{\"GsearchResultClas
    s\":\"GwebSearch\",\"unescapedUrl\":\"http://www.ruby-lang.org/\",\"url\":\"http
    ://www.ruby-lang.org/\",\"visibleUrl\":\"www.ruby-lang.org\",\"cacheUrl\":\"http
    ://www.google.com/search?q\\u003dcache:U0idxbaGKSwJ:www.ruby-lang.org\",\"title\
    ":\"\\u003cb\\u003eRuby\\u003c/b\\u003e Programming Language\",\"titleNoFormatti
    ng\":\"Ruby Programming Language\",\"content\":\"A dynamic, interpreted, open so
    urce programming language with a focus on simplicity   and productivity. Site in
    cludes news, downloads, documentation, \\u003cb\\u003e...\\u003c/b\\u003e\"},{\"
    GsearchResultClass\":\"GwebSearch\",\"unescapedUrl\":\"http://en.wikipedia.org/w
    iki/Ruby_programming_language\",\"url\":\"http://en.wikipedia.org/wiki/Ruby_prog
    ramming_language\",\"visibleUrl\":\"en.wikipedia.org\",\"cacheUrl\":\"http://www
    .google.com/search?q\\u003dcache:ctgTVVq1VwEJ:en.wikipedia.org\",\"title\":\"\\u
    003cb\\u003eRuby\\u003c/b\\u003e (programming language) - Wikipedia, the free en
    cyclopedia\",\"titleNoFormatting\":\"Ruby (programming language) - Wikipedia, th
    e free encyclopedia\",\"content\":\"Growing article, with links to many related 
    topics. [Wikipedia]\"},{\"GsearchResultClass\":\"GwebSearch\",\"unescapedUrl\":\
    "http://en.wikipedia.org/wiki/Rubies\",\"url\":\"http://en.wikipedia.org/wiki/Ru
    bies\",\"visibleUrl\":\"en.wikipedia.org\",\"cacheUrl\":\"http://www.google.com/
    search?q\\u003dcache:gtP3_-Y-jd0J:en.wikipedia.org\",\"title\":\"\\u003cb\\u003e
    Ruby\\u003c/b\\u003e - Wikipedia, the free encyclopedia\",\"titleNoFormatting\":
    \"Ruby - Wikipedia, the free encyclopedia\",\"content\":\"\\u003cb\\u003eRuby\\u
    003c/b\\u003e is a pink to blood red gemstone, a variety of the mineral corundum
    (aluminium   oxide). The common red color is caused mainly by the element chromi
    um. \\u003cb\\u003e...\\u003c/b\\u003e\"},{\"GsearchResultClass\":\"GwebSearch\"
    ,\"unescapedUrl\":\"http://www.rubyonrails.org/\",\"url\":\"http://www.rubyonrai
    ls.org/\",\"visibleUrl\":\"www.rubyonrails.org\",\"cacheUrl\":\"http://www.googl
    e.com/search?q\\u003dcache:kEJNFfIPffoJ:www.rubyonrails.org\",\"title\":\"\\u003
    cb\\u003eRuby\\u003c/b\\u003e on Rails\",\"titleNoFormatting\":\"Ruby on Rails\"
    ,\"content\":\"RoR home; full stack, Web application framework optimized for sus
    tainable   programming productivity, allows writing sound code by favoring conve
    ntion over \\u003cb\\u003e...\\u003c/b\\u003e\"}],\"cursor\":{\"pages\":[{\"star
    t\":\"0\",\"label\":1},{\"start\":\"4\",\"label\":2},{\"start\":\"8\",\"label\":
    3},{\"start\":\"12\",\"label\":4}],\"estimatedResultCount\":\"10900000\",\"curre
    ntPageIndex\":0,\"moreResultsUrl\":\"http://www.google.com/search?oe\\u003dutf8\
    \u0026ie\\u003dutf8\\u0026source\\u003duds\\u0026start\\u003d0\\u0026hl\\u003den
    \\u0026q\\u003druby\"}}, 200, null, 205)"

Wow, that's a huge chunk of Javascript. Clearly this is a Javascript
callback to update the Search dialogue with the JSON Hash containing the
results Array. To make this giant Javascript String useful we will have to
write another method to strip off the callback method and parse the JSON
Hash.

    require 'json'
    
    module SophSec
      def SophSec.ajax_search(options={})
        hash = JSON.parse(SophSec.get_ajax_search(options).scan(/\{.*\}/).first)
    
        if (hash.kind_of?(Hash) && hash['results'])
          return hash['results']
        end
    
        return []
      end
    end

The `SophSec.ajax_search` method will extract the first JSON Hash it
recognizes from `SophSec.get_ajax_search` and parse it using Ruby's
[JSON.parse](http://json.rubyforge.org/doc/classes/JSON.html#M000084)
method. Well test out `SophSec.ajax_search` in irb using the Ruby
[pp](http://www.ruby-doc.org/stdlib/libdoc/pp/rdoc/index.html)
method to pretty print the Array of Search results.

    irb(main):014:0> require 'pp'
    irb(main):015:0> pp SophSec.ajax_search(:q => 'ruby', :rsz => 'small')
    [{"GsearchResultClass"=>"GwebSearch",
      "title"=>"<b>Ruby</b> Programming Language",
      "url"=>"http://www.ruby-lang.org/",
      "cacheUrl"=>
       "http://www.google.com/search?q=cache:U0idxbaGKSwJ:www.ruby-lang.org",
      "content"=>
        "A dynamic, interpreted, open source programming language with a focus on simplicity \
        and productivity. Site includes news, downloads, documentation, <b>...</b>",
      "visibleUrl"=>"www.ruby-lang.org",
      "titleNoFormatting"=>"Ruby Programming Language",
      "unescapedUrl"=>"http://www.ruby-lang.org/"},
     {"GsearchResultClass"=>"GwebSearch",
      "title"=>
       "<b>Ruby</b> (programming language) - Wikipedia, the free encyclopedia",
      "url"=>"http://en.wikipedia.org/wiki/Ruby_programming_language",
      "cacheUrl"=>
       "http://www.google.com/search?q=cache:ctgTVVq1VwEJ:en.wikipedia.org",
      "content"=>"Growing article, with links to many related topics. [Wikipedia]",
      "visibleUrl"=>"en.wikipedia.org",
      "titleNoFormatting"=>
       "Ruby (programming language) - Wikipedia, the free encyclopedia",
      "unescapedUrl"=>"http://en.wikipedia.org/wiki/Ruby_programming_language"},
     {"GsearchResultClass"=>"GwebSearch",
      "title"=>"<b>Ruby</b> - Wikipedia, the free encyclopedia",
      "url"=>"http://en.wikipedia.org/wiki/Rubies",
      "cacheUrl"=>
       "http://www.google.com/search?q=cache:gtP3_-Y-jd0J:en.wikipedia.org",
      "content"=>
        "<b>Ruby</b> is a pink to blood red gemstone, a variety of the mineral \
        corundum (aluminium   oxide). The common red color is caused mainly by the element \
        chromium. <b>...</b>",
      "visibleUrl"=>"en.wikipedia.org",
      "titleNoFormatting"=>"Ruby - Wikipedia, the free encyclopedia",
      "unescapedUrl"=>"http://en.wikipedia.org/wiki/Rubies"},
     {"GsearchResultClass"=>"GwebSearch",
      "title"=>"<b>Ruby</b> on Rails",
      "url"=>"http://www.rubyonrails.org/",
      "cacheUrl"=>
       "http://www.google.com/search?q=cache:kEJNFfIPffoJ:www.rubyonrails.org",
      "content"=>
        "RoR home; full stack, Web application framework optimized for sustainable \
        programming productivity, allows writing sound code by favoring convention over \
        <b>...</b>",
      "visibleUrl"=>"www.rubyonrails.org",
      "titleNoFormatting"=>"Ruby on Rails",
      "unescapedUrl"=>"http://www.rubyonrails.org/"}]
    => nil

Awesome, `SophSec.ajax_search` returns a native Array of Search Results,
ripe for the data-mining.

## Conclusion

As one can see it takes a surprisingly small amount of code to create a
non-Javascript interface to the Google AJAX Search API. The full source
code to the `SophSec.get_ajax_search` and `SophSec.ajax_search`
methods can be found
[here](http://github.com/sophsec/shards/blob/master/ruby/ajax_search.rb).

An interesting side-note, while testing the `SophSec.ajax_search` method it
was discovered that the Search API does not perform query filtering against
bots or other interesting Search queries. This discovery indicates that the
Google AJAX Search API could be leveraged for automated web application
vulnerability finger-printing.
