Abstract:

In this report I discuss the background of the project, what my server and client code are able to
do, the project design and implementation, and the evaluation of the rate of bytes sent during the upload 
and download of files.

Introduction And Motivation:

The purpose of this project is to create a server that can be accessed by a client to store and
manage files, similarly to a cloud server. This will be accomplished using sockets and threads in the
Python 3 programming language. These cloud servers usually require user authentication, a GUI, and the
ability to edit files simultaneously. Not all of this was accomplished so this will be a more simplistic
version of that idea. This code will follow the client server model. A server listens on an IP address and a
port, and then waits for clients to connect. After this connection, messages can be exchanged between the
two parties. This will use the TCP protocol which is a connection-oriented, reliable service. That means
that a connection is set up for the communication, and then torn down after the communication is done,
and it means that if there are errors in the communication the messages will be resent.

Project Design and Implementation:

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
