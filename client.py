import os
import socket
import time
import csv
import numpy as np
import pandas as pd
import tqdm


SIZE = 1024
FORMAT = "utf-8"
SERVER_DATA_PATH = "server_data"
connected = False

def connect(IP, PORT):
    ADDR = (IP, PORT)
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    connected = True
    return client, connected

def recieve(client):
    connected = True
    data = client.recv(SIZE).decode(FORMAT)
    #print(f"Received: {data}") #########
    cmd, msg = data.split("@")
    if cmd == "OK":
        print(f"{msg}")
    elif cmd == "DISCONNECTED":
        print(f"{msg}")
        connected = False
        client.close()
    return connected

def upload(client, filename):
    client.send("UPLOAD".encode(FORMAT))
    filesize = os.path.getsize(filename)
    timeArray = [] # for data
    dataRate = []    # for data
    client.send(f"{filename} {filesize}".encode(FORMAT))
    timeArray.append(time.time()) # time 0 for download
    dataRate.append(0) # to line up arrays
    i = 0 # for time
    progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024) # Progress bar
    with open(filename, "rb") as file:
        while True:
            bytes_read = file.read(SIZE)
            timeArray.append(time.time()) # time array appended
            i += 1 # i iterated
            elapsed = timeArray[i] - timeArray[i-1] # time elapsed between this round and last
            dataRate.append(len(bytes_read)/elapsed) # dataRate calculatd and added to array
            progress.update(len(bytes_read))
            if not bytes_read:
                break
            client.sendall(bytes_read)
        file.close()
    timeArray0 = timeArray[0]
    for i in range(len(timeArray)):
        timeArray[i] -= timeArray0
    dataRate = np.array(dataRate)
    dataRate = pd.Series(dataRate)
    dataRate = dataRate.rolling(60).mean()
    with open('uploadData.csv', 'w', newline='') as file:
        mywriter = csv.writer(file, delimiter=',')
        for i in range(len(timeArray)):
            mywriter.writerow([timeArray[i], dataRate[i]])


        


def download(client, filename):
    client.send(f"DOWNLOAD {filename}".encode(FORMAT))
    status = client.recv(SIZE).decode(FORMAT)
    #print(f"status: {status}") #########
    if status == "download":
        timeArray = [] # for data
        dataRate = []    # for data
        filesize = int(client.recv(SIZE).decode(FORMAT))
        #print(f"filesize: {filesize}")
        filename = os.path.basename(filename)
        sizeDownloaded = 0
        timeArray.append(time.time()) # time 0 for download
        dataRate.append(0) # line up arrays
        i = 0 # for time
        #progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024) # Progress bar
        with open(filename, "wb") as file:
            sizeUploaded = 0
            while sizeUploaded < filesize:
                timeArray.append(time.time())
                bytes_read = client.recv(SIZE)
                sizeUploaded += len(bytes_read)
                i += 1
                elapsed = timeArray[i] - timeArray[i-1] # time elapsed between this round and last
                dataRate.append(len(bytes_read)/elapsed) # dataRate calculatd and added to array
                if not bytes_read:
                    break
                file.write(bytes_read)
                print(int(sizeUploaded)/int(filesize))
                #progress.update(len(bytes_read))
            file.close()
        client.send("complete".encode(FORMAT))
        timeArray0 = timeArray[0]
        for i in range(len(timeArray)):
            timeArray[i] -= timeArray0
        dataRate = np.array(dataRate)
        dataRate = pd.Series(dataRate)
        dataRate = dataRate.rolling(60).mean()
        with open('downloadData.csv', 'w', newline='') as file:
            mywriter = csv.writer(file, delimiter=',')
            for i in range(len(timeArray)):
                mywriter.writerow([timeArray[i], dataRate[i]])
        return
    elif status == "OK":
        #print("The status was OK") #########
        return
    
while True:   
    data = input("> ")
    if data != "":
        dataCopy = data
        dataCopy = dataCopy.split(" ")

        if dataCopy[0] == "CONNECT":
            if connected == False:
                client, connected = connect(dataCopy[1], int(dataCopy[2]))
                connected = recieve(client)
            elif connected == True:
                print("Disconnected from current server before connecting to new server.")
        elif dataCopy[0] == "UPLOAD":
            if connected == True:
                try:
                    filesize = os.path.getsize(dataCopy[1])
                    upload(client, dataCopy[1])
                    connected = recieve(client)
                except:
                    print(f"{dataCopy[1]} does not exist")
            elif connected == False:
                print("Not connected to a server")
        elif dataCopy[0] == "DOWNLOAD":
            if connected:
                download(client, dataCopy[1])
                connected = recieve(client)
            if not connected:
                print("Not connected to a server")
        elif dataCopy[0] == "EXIT":
            if connected:
                print("Please disconnect from the server first")
            elif not connected:
                exit()
        else:
            if connected:
                client.send(data.encode(FORMAT))
                connected = recieve(client)
            elif not connected:
                print("unknown command or not connected to a server")
        

