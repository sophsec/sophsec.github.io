#!/usr/bin/env ruby

require 'digest/sha1'
require 'digest/sha2'
require 'digest/md5'
require 'openssl'

module SophSec
  #
  # aes_pipe v0.2 by Postmodern (postmodern at sophsec.com)
  #
  # A Ruby implementation of the aespipe utility. Handy if you don't have
  # aespipe installed.
  #
  class AESPipe

    class InvalidHash < RuntimeError
    end

    class InvalidMode < RuntimeError
    end

    # Mode of the cipher
    attr_reader :mode

    # Block-size of the cipher
    attr_reader :block_size

    # Key-size to use with the cipher
    attr_reader :key_size

    # Initial Vector (IV) to use with the cipher
    attr_reader :iv

    # Hash for encoding any passwords
    attr_reader :hash

    # Key to use with the cipher
    attr_reader :key

    # Default block-size
    DEFAULT_BLOCK_SIZE = 4096

    # Default key-size
    DEFAULT_KEY_SIZE = 256

    # Default Initial Vector (IV)
    DEFAULT_IV = '19070547872603305'

    # Default hash
    DEFAULT_HASH = :sha256

    #
    # Creates a new AESPipe object with the given _options_. If a _block_
    # is given, it will be passed the newly created AESPipe object.
    #
    # _options_ may contain the following keys:
    # <tt>:mode</tt>:: The mode of the cipher, either <tt>:encrypt</tt>
    #                  or <tt>:decrypt</tt>. Defaults to <tt>:encrypt</tt>.
    # <tt>:block_size</tt>:: The block-size to use with the cipher.
    #                        Defaults to 4096.
    # <tt>:key_size</tt>:: The key-size of the cipher. Defaults to 256.
    # <tt>:iv</tt>:: The Initial Vector (IV) to use with the cipher.
    #                Defaults to 19070547872603305.
    # <tt>:hash</tt>:: The hash to use with the cipher. Defaults to SHA256.
    # <tt>:key</tt>:: The key to use with the cipher.
    # <tt>:password</tt>:: If <tt>:key</tt> is not given, <tt>:password</tt>
    #                      can be given. The password will be hashed and
    #                      used as the key.
    #
    #   AESPipe.new(:mode => :encrypt, :password => 'pants') do |aes|
    #     aes.cipher do |cipher|
    #       aes.process_output(output_file) do |output|
    #         aes.process_input(input_file) do |text|
    #           output << cipher.update(text)
    #         end
    #
    #         output << cipher.final
    #       end
    #     end
    #   end
    #
    def initialize(options={},&block)
      @mode = (options[:mode] || :encrypt).to_sym
      @block_size = (options[:block_size] || DEFAULT_BLOCK_SIZE).to_i
      @key_size = (options[:key_size] || DEFAULT_KEY_SIZE).to_i
      @iv = (options[:iv] || DEFAULT_IV).to_s
      @hash = (options[:hash] || DEFAULT_HASH).to_s.downcase
      @key = options[:key]

      if options[:key]
        @key = options[:key].to_s
      elsif (password = options[:password])
        begin
          @key = Digest.const_get(@hash.upcase).hexdigest(password)
        rescue RuntimeError => e
          raise(InvalidHash,"invalid hash name #{@hash.dump}",caller)
        end
      end

      block.call(self) if block
    end

    #
    # Returns a new AES cipher object. If a _block_ is given it will be
    # passed the newly created cipher.
    #
    def cipher(&block)
      aes = OpenSSL::Cipher::Cipher.new("aes-#{@key_size}-cbc")

      case @mode
      when :encrypt
        aes.encrypt
      when :decrypt
        aes.decrypt
      else
        raise(InvalidMode,"invalid mode #{@mode}",caller)
      end

      aes.key = @key
      aes.iv = @iv

      block.call(aes) if block
      return aes
    end

    #
    # Processes an input stream of the given _file_ and the specified
    # _block_. If _file_ is not given +STDIN+ will be used instead. The
    # specified _block_ will be passed each block of data from the stream.
    # Once the _block_ has returned the input stream will be closed.
    #
    def process_input(file=nil,&block)
      if @file
        input = File.new(file.to_s)
      else
        input = STDIN
      end

      loop do
        text = input.read(@block_size)
        break unless text

        block.call(text)
      end

      input.close
      return nil
    end

    #
    # Opens an output stream of the given _file_ and the specified
    # _block_. If _file_ is not given +STDOUT+ will be used instead.
    # The specified _block_ will be passed the newly opened output stream.
    # Once the _block_ has returned the output stream will be flushed and
    # closed.
    #
    def process_output(file=nil,&block)
      if @file
        output = File.new(file.to_s,'w')
      else
        output = STDOUT
      end

      block.call(output) if block

      output.flush
      output.close
      return nil
    end

  end
end

if File.basename($0)=='aes_pipe.rb'
  require 'optparse'

  include SophSec

  options = {}
  input_file = nil
  output_file = nil

  opts = OptionParser.new do |opts|
    opts.banner = 'usage: aes_pipe.rb [options]'

    opts.on('-e','--encrypt','encrypt input') do
      options[:mode] = :encrypt
    end

    opts.on('-d','--decrypt','decrypt input') do
      options[:mode] = :decrypt
    end

    opts.on('-i','--input FILE','input file (default: stdin)') do |i|
      input_file = i
    end

    opts.on('-o','--output FILE','output file (default: stdout)') do |o|
      output_file = o
    end

    opts.on('-b','--blocksize BYTES',"block-size used to process input (default: #{AESPipe::DEFAULT_BLOCK_SIZE})") do |b|
      options[:block_size] = b
    end

    opts.on('-s','--keysize BYTES',"key size in bits (default: #{AESPipe::DEFAULT_KEY_SIZE})") do |s|
      options[:key_size] = s
    end

    opts.on('-k','--key KEY','key to use') do |k|
      options[:key] = k
    end

    opts.on('-p','--password PASS','password to use') do |p|
      options[:password] = p
    end

    opts.on('-H','--hash NAME',"hash algorithm to use for the password (default: #{AESPipe::DEFAULT_HASH})") do |h|
      options[:hash] = h
    end

    opts.on('-h','--help','this cruft') do
      puts opts
      exit
    end
  end

  opts.parse!

  begin
    AESPipe.new(options) do |aes|
      aes.cipher do |cipher|
        aes.process_output(output_file) do |output|
          aes.process_input(input_file) do |text|
            output << cipher.update(text)
          end

          output << cipher.final
        end
      end
    end
  rescue RuntimeError => e
    STDERR.puts(e)
    exit -1
  end
end
