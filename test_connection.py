import transport_managers
from protocols import binary_protocol_0_1
from application_types import TRANSPORT_ROLE

transport_managers.fifo.connect('local_fifo', binary_protocol_0_1, TRANSPORT_ROLE.PRODUCER)

#import socket
#socket.socket(socket.AF_UNIX).bind('test_socket')
#os.unlink('test_socket')

