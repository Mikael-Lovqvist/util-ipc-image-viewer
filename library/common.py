from urllib.parse import urlparse, parse_qsl
import argparse
from . import transport_managers, producers, consumers, testing
from pathlib import Path

transport_manager_table = None
scheme_map = dict()
method_map = dict()
url_help_schemes = tuple()
method_help = tuple()
argument_parser = None

def iter_options(cls):
	for key in cls.__dict__:
		if not key.startswith('_'):
			yield getattr(cls, key)



def load_transport_managers():
	global transport_manager_table, scheme_map, method_map, url_help_schemes, method_help

	transport_manager_table = (
		('tcp',		'tcp',		transport_managers.tcp),
		('sock',	'socket',	transport_managers.unix),
		('fifo',	'fifo',		transport_managers.fifo),
	)


	for scheme, method, tm in transport_manager_table:
		scheme_map[scheme] = tm
		method_map[method] = tm

		url_help_schemes += (
			'',
			f'{scheme}://host:[address][?options]',
			'',
			'  Valid options:',
			*(f'    {option.url_query_tag:<18} {option.description}' for option in iter_options(tm.options)),
		)

		method_help += (
			'',
			method,
			'',
			'  Valid options:',
			*(f'    {option.command_line_option:<25} {option.description}' for option in iter_options(tm.options)),
		)


def load_argument_parser():
	global argument_parser
	argument_parser = argparse.ArgumentParser(description='Image data test util', formatter_class=argparse.RawTextHelpFormatter)
	seen_options = set()

	for scheme, method, tm in transport_manager_table:
		for option in iter_options(tm.options):
			if option.type is bool:

				if option.command_line_option not in seen_options:
					#We will assume that any colissions are on purpose
					argument_parser.add_argument(option.command_line_option, action='store_true', help='Depends on METHOD, see --method', dest=option.command_line_option)
					seen_options.add(option.command_line_option)
			else:
				raise NotImplementedError('only supports bool for now')

	argument_parser.add_argument('URL', nargs='?',
		help = '\n'.join((
			'Specify connection using a URL',
			'The following schemes are supported:',
			*url_help_schemes,
		))
	)

	argument_parser.add_argument('--method',
		help = '\n'.join((
			'Specify transport when not using URL.',
			'The following transports are supported:',
			*method_help
		))
	)




def get_producer_by_url(url):

	url = urlparse(url)


	transport = scheme_map[url.scheme]

	#NOTE - maybe we should have the transport parsing the url for us?
	if transport is transport_managers.tcp:
		t_host, t_port = url.netloc.split(':')
		target = (t_host, int(t_port))
	else:
		target = str(Path(url.netloc, url.path))

	transport_arguments = dict()
	option_by_query = dict()
	for option in iter_options(transport.options):
		transport_arguments[option.name] = option.default
		option_by_query[option.url_query_tag] = option

	for key, value in parse_qsl(url.query, keep_blank_values=True):
		option = option_by_query[key]
		transport_arguments[option.name] = True


	return transport.pending_connection(target, **transport_arguments)


def example():

	load_transport_managers()
	#load_argument_parser()

	pending = get_producer_by_url('sock://viewstuff.sock')
	producer = producers.raw_pillow_producer()
	sender = pending.connect_as_thread(producer)


	import time
	for v in range(10):
		[image] = testing.generate_random_images(1)
		producer.transport(image)
		time.sleep(0.01)

	producer.dispatch_sentinel()