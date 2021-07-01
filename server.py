import socket
import typing

# spacing
class Request(typing.NamedTuple):
	method: str
	path: str
	headers: typing.Mapping[str, str]

def iter_lines(socket: socket.socket, bufsize: int=16_384) -> typing.Generator[bytes, None, bytes]:
	# read CRLF line by line until empty line, then return remainder
	buff = b""
	while True:
		data = socket.recv(bufsize)
		if not data:
			return b""

		buff += data
		while True:
			try:
				i = buff.index(b"\r\n")
				line, buff = buff[:i], buff[i+2:]
				if not line: # empty line then return remainder
					return buff

				yield line

			except IndexError:
				break

HOST = "127.0.0.1"
PORT = 9000

RESPONSE = b"""\
HTTP/1.1 200 OK
Content-type: text/html
Content-length: 15

<h1>Hello!</h1>""".replace(b"\n", b"\r\n")

# one dendpoint of a two-way communication link between two sources
with socket.socket() as server_socket:
	# tell kernel to reuse sockets that are in TIME_WAIT state
	server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	server_socket.bind((HOST, PORT))

	# hold 0 pending connections -> 1 connection at a time
	server_socket.listen(0)
	print(f"Listening on {HOST}:{PORT}...")

	while True:
		client_socket, client_addr = server_socket.accept()
		print(f"New connection from {client_addr}")
		with client_socket:
			for request_line in iter_lines(client_socket):
				print(request_line)

			client_socket.sendall(RESPONSE)



