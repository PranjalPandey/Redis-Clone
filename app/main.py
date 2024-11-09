import socket
import sys# noqa: F401
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

def handle_request(client_socket, addr):
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
def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage
    #
    server_socket = socket.create_server(("localhost", 6379), reuse_port=True)
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
