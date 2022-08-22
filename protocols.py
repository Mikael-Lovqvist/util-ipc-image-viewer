from application_types import semantic_version, structure, protocol_consumer, protocol_producer

class binary_protocol_0_1_base:
	class frame_info(structure):
		_format = '<IHHHHHIII'
		__slots__ = 'frame_size', 'frame_format', 'width', 'height', 'pixel_format', 'pixel_stride', 'row_stride', 'ts_epoch', 'ts_epoch_ns'


class binary_protocol_0_1_consumer(protocol_consumer, binary_protocol_0_1_base):

	def consume_from_stream(self, stream):
		#We store this so that we could close it
		self.stream = stream
		version = semantic_version._read(stream)
		assert version.major == 0 and version.minor == 1

		#TODO - check if stream.read may return early for any of the transports

		while True:
			try:
				frame = self.frame_info._read(stream)
			except EOFError:
				stream.close()
				return

			#TODO - sanity check frame size

			frame_data = stream.read(frame.frame_size)
			self.dispatch_frame(frame, frame_data)

class binary_protocol_0_1_producer(protocol_producer, binary_protocol_0_1_base):
	def produce_into_stream(self, stream):
		#We store this so that we could close it
		self.stream = stream
		semantic_version(0, 1, 0)._write(stream)


		while True:
			frame, frame_data = self.produce_frame()
			if not frame:
				stream.close()
				return
			frame._write(stream)
			stream.write(frame_data)
