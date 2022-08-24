import struct

class symbol(type):
	def __new__(cls, name):
		return super().__new__(cls, name, (), {})

	def __repr__(self):
		return self.__name__

DEFAULT = symbol('DEFAULT')
PENDING = symbol('PENDING')
NOT_AVAILABLE = symbol('N/A')

class protocol_consumer:
	stream = None

class protocol_producer:
	stream = None

	def dispatch_sentinel(self):
		self.dispatch_frame((None, None))


class command_option:
	def __init__(self, type, default, description, url_query_tag, command_line_option, name=None):
		self.type = type
		self.default = default
		self.description = description
		self.url_query_tag = url_query_tag
		self.command_line_option = command_line_option
		self.name = name

	def __set_name__(self, target, name):
		self.name = name

	def parse(self, value=DEFAULT):
		if value is DEFAULT:
			return self.default
		else:
			return self.type(value)


class structure:
	__slots__ = ()
	def __init_subclass__(cls):
		cls._structure = struct.Struct(cls._format)

	def __init__(self, *values):
		for slot, value in zip(self.__slots__, values):
			setattr(self, slot, value)

	def __repr__(self):
		inner = (self.__class__.__qualname__, *(f'{slot}={getattr(self, slot, NOT_AVAILABLE)!r}' for slot in self.__slots__))
		return f'<{" ".join(inner)}>'

	def __hash__(self):
		value = 0
		for slot in self.__slots__:
			value ^= hash(getattr(self, slot) )
		return value

	def __eq__(self, other):
		if self.__class__ is not other.__class__:
			return False

		for slot in self.__slots__:
			if getattr(self, slot) != getattr(other, slot):
				return False

		return True



	@classmethod
	def _read(cls, stream):
		size = cls._structure.size
		data = stream.read(size)

		if len(data) < size:
			raise EOFError()

		return cls(*cls._structure.unpack(data))

	def _write(self, stream):
		data = self._structure.pack(*(getattr(self, slot) for slot in self.__slots__))
		stream.write(data)


class semantic_version(structure):
	_format = '<BBH'
	__slots__ = 'major', 'minor', 'revision'

