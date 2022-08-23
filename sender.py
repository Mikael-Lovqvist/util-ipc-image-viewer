from testing import generate_random_images	  # todo  - add support for using the tool for generating test images as well
from producers import raw_pillow_producer
from urllib.parse import urlparse, parse_qsl
import threading, time, signal, os
import transport_managers


import argparse

def iter_options(cls):
	for key in cls.__dict__:
		if not key.startswith('_'):
			yield getattr(cls, key)


#TODO - add options for non URL for hostname and port and such

parser = argparse.ArgumentParser(description='Image data test util', formatter_class=argparse.RawTextHelpFormatter)

transport_manager_table = (
	('tcp',		'tcp',		transport_managers.tcp),
	('sock',	'socket',	transport_managers.unix),
	('fifo',	'fifo',		transport_managers.fifo),
)

scheme_map = dict()
method_map = dict()


url_help_schemes = tuple()
method_help = tuple()
seen_options = set()

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

	for option in iter_options(tm.options):
		if option.type is bool:

			if option.command_line_option not in seen_options:
				#We will assume that any colissions are on purpose
				parser.add_argument(option.command_line_option, action='store_true', help='Depends on METHOD, see --method', dest=option.command_line_option)
				seen_options.add(option.command_line_option)
		else:
			raise NotImplementedError('only supports bool for now')




parser.add_argument('URL', nargs='?',
	help = '\n'.join((
		'Specify connection using a URL',
		'The following schemes are supported:',
		*url_help_schemes,
	))
)

parser.add_argument('--method',
	help = '\n'.join((
		'Specify transport when not using URL.',
		'The following transports are supported:',
		*method_help
	))
)


invocation = parser.parse_args()

if invocation.URL:
	url = urlparse(invocation.URL)

	transport = scheme_map[url.scheme]
	t_host, t_port = url.netloc.split(':')
	target = (t_host, int(t_port))

	transport_arguments = dict()
	option_by_query = dict()
	for option in iter_options(transport.options):
		#transport_arguments[option.name] = getattr(invocation, option.command_line_option)
		transport_arguments[option.name] = option.default
		option_by_query[option.url_query_tag] = option

	for key, value in parse_qsl(url.query, keep_blank_values=True):
		option = option_by_query[key]
		transport_arguments[option.name] = True


else:
	raise NotImplementedError()


signal.signal(signal.SIGINT, signal.SIG_DFL)


producer = raw_pillow_producer(one_shot = True)
[image] = generate_random_images(1)
producer.transport(image)
transport.connect(target, producer, **transport_arguments)
