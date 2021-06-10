from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
from pyftpdlib.authorizers import DummyAuthorizer
import socket

usage_dir = "C:/Users/PERCY/projects/api/detections"
local_ip = socket.gethostbyname(socket.gethostname())
local_ip = "197.248.97.85"
PORT = 2121

class MyHandler(FTPHandler):

    def on_connect(self):
        print("[NEW SESSION] {}:{} connected".format(self.remote_ip, self.remote_port))

    def on_disconnect(self):
        # do something when client disconnects
        print("do something when client disconnects")

    def on_login(self, username):
        # do something when user login
        print("do something when user login")

    def on_logout(self, username):
        # do something when user logs out
        print("do something when user logs out")

    def on_file_sent(self, file):
        # do something when a file has been sent
        print("do something when a file has been sent")
        print(file)

    def on_file_received(self, file):
        # do something when a file has been received
        print("do something when a file has been received")
        print(f"Recieved file: {file}")

    def on_incomplete_file_sent(self, file):
        # do something when a file is partially sent
        print("do something when a file is partially sent")

    def on_incomplete_file_received(self, file):
        # remove partially uploaded files
        import os
        os.remove(file)
        
        print("remove partially uploaded files")


def main():
    
    print(f"Hosting FTP server at ftp://{local_ip}:{PORT}")
    
    authorizer = DummyAuthorizer()
    authorizer.add_user('user', '12345', homedir=usage_dir, perm='elradfmwMT')
    authorizer.add_anonymous(homedir=usage_dir)

    handler = MyHandler
    handler.authorizer = authorizer
    server = FTPServer(('0.0.0.0', PORT), handler)
    server.serve_forever()

if __name__ == "__main__":
    main()