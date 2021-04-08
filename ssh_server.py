import socket
import paramiko
import sys
import threading

HOST_KEY = paramiko.RSAKey.from_private_key_file('mykey.pem')
USERNAME = 'root'
PASSWORD = 'toor'

class Server(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()
    
    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED
    
    def check_auth_password(self, username, password):
        if (username == USERNAME) and (password == PASSWORD):
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

def main():
    if not len(sys.argv[1:]):
        print('Usage: ssh_server.py <SERVER>  <PORT>')
        return
    # Create a socket object.
    server = sys.argv[1]
    ssh_port = int(sys.argv[2])
    try:
        sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((server, ssh_port))
        sock.listen(100)
        print('[+] Listening for connection ...')
        client, addr = sock.accept()
    except Exception as e:
        print(f'[-] Connection Failed: {str(e)}')
        return
    
    print('[+] Connection Established!')
    # Creating a paramiko object.
    try:
        Session = paramiko.Transport(client)
        Session.add_server_key(HOST_KEY)
        paramiko.util.log_to_file('custom_log.log')
        server = Server()
        try:
            Session.start_server(server=server)
        except paramiko.SSHException as x:
            print('[-] SSH negotiation failed.')
            return
        chan = Session.accept(100)
        print('[+] Authenticated!')
        chan.send("Welcome to Buffy's SSH")
        while True:
            try:
                command = input('Enter command: ').strip('\n')
                if command != 'exit':
                    chan.send(command)
                    print(chan.recv(4096) + '\n')
                else:
                    chan.send('exit')
                    print('[*] Exiting ...')
                    Session.close()
                    raise Exception('exit')
            except KeyboardInterrupt:
                Session.close()
    except Exception as e:
        print(f'[-] Caught exception: {str(e)}')
        try:
            Session.close()
        except:
            pass

if __name__ == '__main__':
    main()