import socket
import select
import sys


def server(log_buffer=sys.stderr):
    # set an address for our server
    address = ('127.0.0.1', 10000)
    # create an IPv4 socket
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
    # allow the socket address to be reused immediately
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # log that we are building a server
    print >>log_buffer, "making a server on {0}:{1}".format(*address)

    # bind the server socket to the address above 
    server_sock.bind(address)

    # Set the max number of queued socket connection requests to Linux maximum.
    server_sock.listen(128)

    # Create a list of sockets for reading,
    # initialized with the server's connection request socket.
    read_list = [server_sock]

    try:
        # The outer loop controls the creation of new connection sockets. 
        while True:
            print >>log_buffer, 'waiting for a connection'

            # Check for sockets ready for reading
            read_sockets, write_sockets, excp_sockets = select.select(read_list, [], [])

            # Process those sockets ready for reading
            for sock in read_sockets:

                if sock == server_sock:
                    # If this is the server socket, then it's a connection request.
                    client_sock, addr = server_sock.accept()
                    print >>log_buffer, 'connection - {0}:{1}'.format(*addr)

                    # Add the client's ephemeral socket to the list of sockets 
                    # to be listened to.
                    read_list.append(client_sock)
                    
                else:
                    # Else it must be a client socket; a client is ready to talk.
                    try:
                        while True:
                            # Retreive the client's data in 16 byte chunks.
                            data = sock.recv(16)
                            print >>log_buffer, 'received "{0}"'.format(data)

                            # What we receive from the client gets sent back.
                            if data:
                                sock.sendall(data)
                            else:
                                break

                    except socket.error as e:
                        # Ignoring client socket errors for now
                        pass

                    finally:
                        # Close the socket when we have read all of the client's message.
                        sock.close()
                        read_list.remove(sock)

    except KeyboardInterrupt:
        # Use the python KeyboardIntterupt exception as a signal to
        # close the server socket and exit from the server function.
        server_sock.close()


if __name__ == '__main__':
    server()
    sys.exit(0)
