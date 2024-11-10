import socket, time
import sys# noqa: F401
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
map = {}
expiry_dictionary = {}

# Create a CommandParse object
class CommandParser:
    def respSimpleString(message):
        return f"+{message}\r\n"
    def respBulkString(message):
        if message == None:
            return f"$-1\r\n"
        return f"${len(message)}\r\n{message}\r\n"

def handle_request(client_socket, addr):
    global map, expiry_dictionary
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
def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage
    #
    server_socket = socket.create_server(("localhost", 6379), reuse_port=False)
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
