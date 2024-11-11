import socket, time
import sys# noqa: F401
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from argparse import ArgumentParser
map = {}
expiry_dictionary = {}
args = None
# Create a CommandParse object
class CommandParser:
    def respSimpleString(message):
        return f"+{message}\r\n"
    def respBulkString(message):
        if message == None:
            return f"$-1\r\n"
        return f"${len(message)}\r\n{message}\r\n"

def handle_request(client_socket, addr):
    global map, expiry_dictionary, args
    with client_socket:
        print(f"Accecpted connection from {addr}\n")
        while True:
            data: bytes = client_socket.recv(1024)
            if not data:
                break
            decoded_data = data.decode().lower()
            if "ping" in decoded_data:
                pong: str = "+PONG\r\n"
                client_socket.sendall(pong.encode())
            if "echo" in decoded_data:
                res_data = decoded_data.split("\r\n")[-2]
                content_len = len(res_data)
                response = f"${content_len}\r\n{res_data}\r\n"
                client_socket.send(response.encode())
            if "get" in decoded_data:
                command = decoded_data.split("\r\n")
                key = command[4]
                value = map.get(key)
                # Check if the key has expired
                if key in expiry_dictionary:
                    if time.time() * 1000 - expiry_dictionary[key] > 0:
                        value = None

                client_socket.send(CommandParser.respBulkString(value).encode())
            if "set" in decoded_data:
                command = decoded_data.split("\r\n")
                key = command[4]
                value = command[6]
                map[key] = value
                if len(command) > 8:
                    expiry = command[10]
                    expiry_dictionary[key] = time.time() * 1000 + int(expiry)
                client_socket.send(CommandParser.respSimpleString("OK").encode())

            if "info" in decoded_data:
                if "replication" in decoded_data:
                    command = decoded_data.split("\r\n")
                    print(command)
                    if args.replicaof:
                        client_socket.send(CommandParser.respBulkString("role:slave").encode())
                    else:
                        client_socket.send(CommandParser.respBulkString("role:master\nmaster_replid:3540kim3pknqq2qx3r4kwjvwu63sfsq5alaxpeuk\nmaster_repl_offset:0").encode())

def perform_handshake(host, port):
    master_socket = socket.create_connection((host, port))
    master_socket.sendall(str.encode("*1\r\n$4\r\nping\r\n"))


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")
    global args
    parser = ArgumentParser(description="Start a simple socket server.")
    parser.add_argument(
        "--port", type=int, default=6379, help="Port number to bind the server."
    )
    parser.add_argument(
        "--replicaof",
        nargs=1,
        help="Specify the host and port of the replica server.",
    )
    args = parser.parse_args()
    if args.replicaof:
        global role
        role = "slave"
        host, port = args.replicaof[0].split(" ")

        perform_handshake(host, port)
    server_socket = socket.create_server(("localhost",  args.port), reuse_port=False)
      # wait for client
    # server_socket.accept() # wait for client
    while True:
        try:
            client_socket, _ = server_socket.accept()
            client_thread = threading.Thread(
                target=handle_request, args=[client_socket, _]
            )
            client_thread.start()

        except Exception as e:
            print(e)







if __name__ == "__main__":
    main()
