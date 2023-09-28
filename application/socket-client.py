import socket

PORT = 5000

def main():
    host = socket.gethostname()

    client_socket = socket.socket()
    client_socket.connect((host, PORT))

    message = input('--> ')
    while message.lower().strip() != 'exit':
        client_socket.send(message.encode())
        msg = client_socket.recv(1024).decode()
        print(f'Recieved message {msg}')
        message = input('--> ')
    
    client_socket.close()



if __name__ == '__main__':
    main()