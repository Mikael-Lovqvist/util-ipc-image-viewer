from .application_types import command_option, DEFAULT, PENDING, protocol_consumer, protocol_producer
import os, socket, errno, threading	#TODO - figure out how to deal with EADDR on non posix platforms
from pathlib import Path

#TODO - maybe make path to be an option as well? Or not?

class abstract_transport:
	pass

class tcp(abstract_transport):
	class options:
		listen = command_option(bool, False, 'Listen', url_query_tag='listen', command_line_option='--listen')
		reuse_address = command_option(bool, False, 'Reuse address', url_query_tag='reuse_address', command_line_option='--reuse-address')


	@classmethod
	def pending_connection(cls, address=PENDING, protocol_handler=PENDING, listen=DEFAULT, reuse_address=DEFAULT):
		return pending_connection(cls, address, protocol_handler, listen, reuse_address)

	@classmethod
	def connect(cls, address, protocol_handler, listen=DEFAULT, reuse_address=DEFAULT):

		option_listen = cls.options.listen.parse(listen)
		option_reuse_address = cls.options.reuse_address.parse(reuse_address)

		def handle_transport_socket(transport_socket):

			if isinstance(protocol_handler, protocol_producer):
				with transport_socket.makefile('wb') as stream:
					protocol_handler.produce_into_stream(stream)

			elif isinstance(protocol_handler, protocol_consumer):
				with transport_socket.makefile('rb') as stream:
					protocol_handler.consume_from_stream(stream)
			else:
				raise TypeError(protocol_handler)


		if option_listen:
			#The reason we use try here is that if we check p.exists() we can still get an error since some other process could create it just after we checked.
			with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listening_socket:
				if option_reuse_address:
					listening_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

				listening_socket.bind(address)
				listening_socket.listen()
				while True:
					transport_socket = listening_socket.accept()[0]
					handle_transport_socket(transport_socket)
		else:
			with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as transport_socket:
				transport_socket.connect(address)
				handle_transport_socket(transport_socket)


class unix(abstract_transport):
	class options:
		listen = command_option(bool, False, 'Listen', url_query_tag='listen', command_line_option='--listen')
		delete_existing = command_option(bool, False, 'Delete existing socket', url_query_tag='delete_existing', command_line_option='--delete-existing')


	@classmethod
	def pending_connection(cls, path=PENDING, protocol_handler=PENDING, listen=DEFAULT, delete_existing=DEFAULT):
		return pending_connection(cls, path, protocol_handler, listen, delete_existing)

	@classmethod
	def connect(cls, path, protocol_handler, listen=DEFAULT, delete_existing=DEFAULT):

		option_listen = cls.options.listen.parse(listen)
		option_delete_existing = cls.options.delete_existing.parse(delete_existing)

		p = Path(path)

		def handle_transport_socket(transport_socket):

			if isinstance(protocol_handler, protocol_producer):
				with transport_socket.makefile('wb') as stream:
					protocol_handler.produce_into_stream(stream)

			elif isinstance(protocol_handler, protocol_consumer):
				with transport_socket.makefile('rb') as stream:
					protocol_handler.consume_from_stream(stream)
			else:
				raise TypeError(protocol_handler)


		if option_listen:
			#The reason we use try here is that if we check p.exists() we can still get an error since some other process could create it just after we checked.
			with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as listening_socket:
				try:
					listening_socket.bind(path)
				except OSError as e:
					if e.errno == errno.EADDRINUSE and option_delete_existing:
						p.unlink()
						#Retrying one more time
						listening_socket.bind(path)
					else:
						raise

				listening_socket.listen()
				while True:
					transport_socket = listening_socket.accept()[0]
					handle_transport_socket(transport_socket)

		else:
			with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as transport_socket:
				transport_socket.connect(path)
				handle_transport_socket(transport_socket)



class fifo(abstract_transport):
	class options:
		create = command_option(bool, False, 'Create fifo', url_query_tag='create', command_line_option='--create-fifo')
		strict = command_option(bool, False, 'Creating fifo must not fail', url_query_tag='strict', command_line_option='--create-fifo-strict')


	@classmethod
	def pending_connection(cls, path=PENDING, protocol_handler=PENDING, create=DEFAULT, strict=DEFAULT):
		return pending_connection(cls, path, protocol_handler, create, strict)

	@classmethod
	def connect(cls, path, protocol_handler, create=DEFAULT, strict=DEFAULT):

		option_create = cls.options.create.parse(create)
		option_strict = cls.options.strict.parse(strict)

		p = Path(path)

		if option_create:
			#The reason we use try here is that if we check p.exists() we can still get an error since some other process could create it just after we checked.
			try:
				os.mkfifo(p)
			except FileExistsError:
				if option_strict:
					raise	#We only raise the FileExistsError if we are also strict


		if isinstance(protocol_handler, protocol_producer):
			#Open will be blocking here until the other end of the fifo is connected
			with open(p, 'wb') as fifo:
				protocol_handler.produce_into_stream(fifo)
		elif isinstance(protocol_handler, protocol_consumer):
			#Open will be blocking here until the other end of the fifo is connected
			with open(p, 'rb') as fifo:
				protocol_handler.consume_from_stream(fifo)
		else:
			raise TypeError(protocol_handler)


class pending_connection:
	def __init__(self, transport, *positional, **named):
		self.transport = transport
		self.positional = positional
		self.named = named

	def connect(self, *positional, **named):
		ip = iter(positional)

		def get_pos(p):
			return next(ip) if p is PENDING else p

		#Get positionals, replace PENDING with positionals from positional
		pos = tuple(get_pos(p) for p in self.positional)
		kw = {n: get_pos(v) for n, v in self.named.items()}

		#If there are more positionals here add them
		pos += tuple(ip)
		kw.update(named)

		self.transport.connect(*pos, **kw)

	def connect_as_thread(self, *positional, **named):
		thread = threading.Thread(target=self.connect, args=positional, kwargs=named)
		thread.start()
		return thread