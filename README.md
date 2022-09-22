Abstract
In this report I discuss the background of the project, what my server and client code are able to
do, the project design and implementation, and the evaluation of the rate of bytes sent during the upload
and download of files.
Introduction And Motivation
The purpose of this project is to create a server that can be accessed by a client to store and
manage files, similarly to a cloud server. This will be accomplished using sockets and threads in the
Python 3 programming language. These cloud servers usually require user authentication, a GUI, and the
ability to edit files simultaneously. Not all of this was accomplished so this will be a more simplistic
version of that idea. This code will follow the client server model. A server listens on an IP address and a
port, and then waits for clients to connect. After this connection, messages can be exchanged between the
two parties. This will use the TCP protocol which is a connection-oriented, reliable service. That means
that a connection is set up for the communication, and then torn down after the communication is done,
and it means that if there are errors in the communication the messages will be resent.
Project Design and Implementation
My software supports all of the essential commands specified in the specifications, plus the
subfolders extension:
1. CONNECT server_IP_address server_port: This function opens a connection with the
server on the specified port.
2. UPLOAD filename: the client uploads on the server the prespecified file.
3. DOWNLOAD filename: the client downloads the specified file on a local folder. If the
file does not exist or the file is uploading or deleting, the server returns an error.
4. DELETE filename: the specified file name is deleted.
5. DIR: returns the content of the shared folder.
6. MKDIR directory: the specified directory is created.
7. CHDIR directory: the current directory is changed.
8. RMDIR directory: the directory is deleted.
9. MOVE filename directory: file is moved to specified directory.
10. DISCONNECT: The client disconnects from the server.
11. EXIT: The client is closed.
Pseudocode:
This section will contain the server pseudocode and the client pseudocode along with the pseudocode for
each function that the server and client execute.
Server pseudocode:
Address, size of bytes sent, encoding format, and server path are defined.
A socket that runs the TCP protocol and uses IPv4 addresses is defined as the server.
The server is binded to the address
The server starts listening.
The server accepts a connection.
For each client that connects the following happens in a new thread:
Server sends “OK@Welcome to the server”
Then a loop starts that terminates when the client disconnects:
The server receives a message from the client.
The data is split into tokens.
Token[0] is defined as the command to be executed.
If Token[0] is a command with a function, the server executes it.
Else if Token[0] is “DISCONNECT” the server breaks the loop and closes the connection
Else if Token[0] is not a known command, the server sends “OK@Unknown command”
to the client.
Server Functions:
handle_upload(conn, send_data)
The filename and file size are received from the client
If the path is part of the filename the path is removed
sizeUploaded is set to 0
A file is created
while sizeUploaded is less than the file size received from the client this loop runs:
Bytes_read are received from the client
sizeUploaded is updated with the length of the bytes_read
The file is closed
The server sends “OK@File uploaded” to the client
handle_download(conn, send_data, filename)
The file size is sent to the client
The file is opened
Loop runs until broken:
1024 bytes are read from the file
If there were no more bytes in the file the loop is broken
The bytes are sent to the client
If “complete” is received from the client the server sends “OK@Download complete” to the client
handle_delete(conn, file)
If the file exists:
The file is deleted
Server sends “OK@File deleted” to client
Else if the file does not exist:
The server sends “OK@File does not exist” to client
handle_dir(conn)
If the directory is not empty:
The server sends a string with all items in the directory separated by a newline character
Else if the directory is empty:
The server sends “OK@Directory empty” to client
handle_CHDIR(conn, path)
The directory is changed to path
The server sends “OK@Directory changed to {current directory}” to client
handle_MKDIR(conn, DIR)
DIR is created
The server sends “OK@{DIR} file created” to client
handle_RMDIR(conn, DIR)
The server tries this:
DIR is deleted
The server sends “OK@{DIR} file deleted” to the client
If that fails:
The server sends “OK@Either {DIR} does not exist or {DIR} is not empty”
handle_MOVE(conn, source, dest)
The server tries to move source file to destination directory and then sends “OK@{source} moved to
{dest}” to the client
If this fails the server sends “OK@Error occurred” to the client
Client Pseudocode:
Size of bytes sent, encoding format, server data path are defined.
connected is set to False
This loop is executed until “EXIT” command:
data = input from user.
If data is not an empty string:
A copy of data is made called dataCopy
dataCopy is split into tokens
If dataCopy[0] is “CONNECT”:
If the client is not connected:
client is defined as a socket that uses TCP and IPv4
client connects to ADDR defined by dataCopy[1] and dataCopy[2] which
are IP address and port
Else if client is connected:
“Disconnect from current server before connecting to new server” is
printed.
Else if dataCopy[0] is “UPLOAD” or “DOWNLOAD” that function is executed and then
serve waits for a response from the server.
Else if dataCopy[0] is “EXIT”:
If client is connected to a server:
“Please disconnect from server first” is printed.
Else if client is not connected to a server:
exit() is called and python closes.
If dataCopy[0] is anything else, data is sent to the server and then the client waits for a
response.
Client functions:
Connect(IP, PORT)
ADDR = (IP, PORT)
Client is defined as a socket that uses TCP and IPv4 addresses.
Client connects to ADDR
Connected is set to True
Return client, connected
Receive(client):
Connected is set to True (just so connected variable is in the function)
Data is received from the server and decoded using the chosen format
Message is split using “@” into cmd, and msg
If cmd is “OK”:
Msg is printed
Else if cmd is “DISCONNECTED”:
Msg is printed
Connected is set to False
Client is closed
Connected status is returned
Upload(client, filename):
Client sends “UPLOAD” to the server
timeArray and dataRate arrays are initialized for storing the rate of data transmission for the file upload
Client sends filename and file size to the server
timeArray is appended by the current time
dataRate is appended with 0 so the arrays are lined up
i = 0
The file is opened to be read from
Loop until broken:
bytes_read is set to 1024 bytes read from the file
The new time value is appended to timeArray
i is iterated by 1
The data rate is calculated using the elapsed time and number of bytes sent and then appended to
dataRate
If there aren’t any more bytes in the file to read the loop is broken
Client sends the bytes_read to the server
The file is closed
timeArray is normalized so the timeArray[0] is 0, and the rest are offsets from this.
Rolling average over 60 points is taken on the dataRate array
These arrays are written to a file
Download(client, filename):
Client sends “DOWNLOAD {filename}”
The client awaits for the server to verify that filename is a real file.
If the file is real:
timeArray and dataArray are initialized
The client receives the file size from the server
sizeDownloaded is set to 0
timeArray is appended with current time
dataRate is appended with 0 to line up the arrays
i = 0
A new file is created
While the number of bytes received are less than the file size the server sent:
timeArray is appended with the current time
bytes_read is set equal to whatever the server has sent
Length of bytes_read is added to the number of bytes received from the server
i is iterated by 1
dataRate is calculated using elapsed time between receiving data from the server
The bytes_read is added to the new file
The file is closed
The client sends “complete” to the server
timeArray is normalized
Rolling average of dataRate using 60 points is completed
timeArray and dataRate are written to a file
