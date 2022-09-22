import os
import socket
import threading
import time
import shutil

#IP =  "10.47.16.122"
IP = "localhost"
PORT = 4450
ADDR = (IP,PORT)
SIZE = 1024
FORMAT = "utf-8"
SERVER_PATH = "server"

def handle_upload(conn, send_data):
    fileInfo = conn.recv(SIZE).decode()
    filename, filesize = fileInfo.split()
    filename = os.path.basename(filename)
    filesize = int(filesize)
    sizeUploaded = 0
    
    with open(filename, "wb") as file:
        while sizeUploaded < filesize:
            bytes_read = conn.recv(SIZE)
            sizeUploaded += len(bytes_read)
            if not bytes_read:
                break
            file.write(bytes_read)
        file.close()
    conn.send("OK@File uploaded".encode(FORMAT))

def handle_download(conn, send_data, filename):
    filesize = os.path.getsize(filename)
    conn.send(f"{filesize}".encode(FORMAT))
    with open(filename, "rb") as file:
        while True:
            bytes_read = file.read(SIZE)
            if not bytes_read:
                break
            conn.send(bytes_read)
        if conn.recv(SIZE).decode(FORMAT) == "complete":
            #print("complete")
            conn.send("OK@Download complete".encode(FORMAT))
            #print("OK@Download complete sent")#########


def handle_delete(conn, send_data, file):
    try:
        os.remove(file)
        send_data += "File Deleted"
        conn.send(send_data.encode(FORMAT))
    except:
        send_data += "File does not exist"
        conn.send(send_data.encode(FORMAT))
def handle_dir(conn, send_data):
        if len(os.listdir()) > 0:
            for i in os.listdir():
                send_data+= i + "\n"
            send_data = send_data[:-1]
            conn.send(send_data.encode(FORMAT))
        else:
            send_data += "Directory empy"
            conn.send(send_data.encode(FORMAT))

def handle_CHDIR(conn, send_data, path):
    os.chdir(path)
    send_data += f"Directory changed to {os.getcwd()}"
    conn.send(send_data.encode(FORMAT))

def handle_MKDIR(conn, send_data, DIR):
    os.mkdir(DIR)
    send_data += f"{DIR} file created"
    conn.send(send_data.encode(FORMAT))

def handle_RMDIR(conn, send_data, DIR):
    DIR_DEL = os.getcwd() + "/" + DIR
    try:
        os.rmdir(DIR_DEL)
        send_data += f"{DIR} file deleted"
        conn.send(send_data.encode(FORMAT))
    except:
        send_data += f"Either {DIR} does not exist or {DIR} is not empty"
        conn.send(send_data.encode(FORMAT))
def handle_MOVE(conn, send_data, source, dest):
    sourceCopy = os.getcwd() + "/" + source
    destCopy = os.getcwd() + "/" + dest + "/" + source
    print(sourceCopy)
    print(destCopy)
    try:
        shutil.move(sourceCopy, destCopy)
        send_data += f"{source} moved to {dest}"
        conn.send(send_data.encode(FORMAT))
    except:
        conn.send("Error occured".encode(FORMAT))
        

### to handle the clients
def handle_client (conn,addr):

    print(f"[NEW CONNECTION] {addr} connected.")
    conn.send("OK@Welcome to the server".encode(FORMAT))
    while True:
        data =  conn.recv(SIZE).decode(FORMAT)
        #print(f"data: {data}")
        data = data.split()
        cmd = data[0]
        send_data = "OK@"

        if cmd == "UPLOAD":
            handle_upload(conn, send_data)
        elif cmd == "DOWNLOAD":
            try:
                filesize = os.path.getsize(data[1])
                conn.send("download".encode(FORMAT))
                handle_download(conn, send_data, data[1])
            except:
                send_data += f"{data[1]} does not exist"
                #print(send_data)
                conn.send("OK".encode(FORMAT))
                conn.send(send_data.encode(FORMAT))
        elif cmd == "DELETE" and len(data) == 2:
            handle_delete(conn, send_data, data[1])
        elif cmd == "DIR" and len(data) == 1:
            handle_dir(conn, send_data)
        elif cmd == "CHDIR" and len(data) == 2:
            handle_CHDIR(conn, send_data, data[1])
        elif cmd == "MKDIR" and len(data) == 2:
            handle_MKDIR(conn, send_data, data[1])
        elif cmd == "RMDIR" and len(data) == 2:
            handle_RMDIR(conn, send_data, data[1])
        elif cmd == "MOVE" and len(data) == 3:
            handle_MOVE(conn, send_data, data[1], data[2])
        elif cmd == "DISCONNECT":
            conn.send("DISCONNECTED@Disconnected".encode(FORMAT))
            break
        else:
            send_data += "Unknown command"
            conn.send(send_data.encode(FORMAT))

    print(f"{addr} disconnected")
    conn.close()


def main():
    print("Starting the server")
    server = socket.socket(socket.AF_INET,socket.SOCK_STREAM) ## used IPV4 and TCP connection
    server.bind(ADDR) # bind the address
    server.listen() ## start listening
    print(f"server is listening on {IP}: {PORT}")
    while True:
        conn, addr = server.accept() ### accept a connection from a client
        thread = threading.Thread(target = handle_client, args = (conn, addr)) ## assigning a thread for each client
        thread.start()


if __name__ == "__main__":
    main()


