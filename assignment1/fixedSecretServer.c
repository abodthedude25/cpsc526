/// =========================================================================
/// Copyright (C) 2024 Pavol Federl (pfederl@ucalgary.ca)
/// All Rights Reserved. Do not distribute this file.
/// =========================================================================

#include <arpa/inet.h>
#include <ctype.h>
#include <errno.h>
#include <error.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>

#if ! defined(BUFFSIZE)
#error BUFFSIZE not defined
#endif

// global variables, grouped in struct
struct {
    int port;                // listening port
    char buffer[BUFFSIZE];   // temporary buffer for input
    char password[BUFFSIZE]; // required password
    char secret[1024];       // the secret to reveal
} globals;

// read a line of text from file descriptor fd into provided buffer
void read_line_from_fd(int fd, char * buff)
{
    size_t i = 0;
    char c;
    while (i < BUFFSIZE - 1) {  // Leave space for null terminator
        ssize_t bytes_read = read(fd, &c, 1);
        if (bytes_read < 1) {
            break; // EOF or error
        }
        if (c == '\n') {
            break; // End of line
        }
        buff[i++] = c;
    }
    buff[i] = '\0'; // Null-terminate the string

    // Optionally, read and discard the remaining characters to prevent further overflow
    if (i >= BUFFSIZE - 1) {
        while (1) {
            ssize_t bytes_read = read(fd, &c, 1);
            if (bytes_read < 1 || c == '\n') {
                break;
            }
        }
    }
}
// write a string to file descriptor
void write_str_to_fd(int fd, const char * str)
{
    size_t remain = strlen(str);
    const char * ptr = str;
    while (remain > 0) {
        ssize_t written = write(fd, ptr, remain);
        if (written < 0) {
            error(-1, errno, "write() failed");
        }
        ptr += written;
        remain -= written;
    }
}

int main(int argc, char ** argv)
{
    // parse command line arguments
    if (argc != 4) {
        error(-1, 0, "Usage: %s port password secret", argv[0]);
    }
    char * end = NULL;
    globals.port = strtol(argv[1], &end, 10);
    if (*end != 0) {
        error(-1, 0, "bad port '%s'", argv[1]);
    }
    strncpy(globals.password, argv[2], sizeof(globals.password));
    strncpy(globals.secret, argv[3], sizeof(globals.secret));

    // create a listenning socket on a given port
    struct sockaddr_in srv_addr;
    int listen_sock_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (listen_sock_fd < 0) {
        error(-1, errno, "socket() failed");
    }
    bzero((char *) &srv_addr, sizeof(srv_addr));
    srv_addr.sin_family = AF_INET;
    srv_addr.sin_addr.s_addr = htons(INADDR_ANY);
    srv_addr.sin_port = htons(globals.port);
    if (bind(listen_sock_fd, (struct sockaddr *) &srv_addr, sizeof(srv_addr))
        < 0) {
        error(-1, errno, "could not bind() listening socket");
    }

    // start listening for connections
    if (listen(listen_sock_fd, 3) != 0) {
        error(-1, errno, "listen() failed");
    }

    while (1) {
        printf("Waiting for a new connection...\n");
        // wait for a connection
        int conn_sock_fd = accept(listen_sock_fd, NULL, NULL);
        if (conn_sock_fd < 0) {
            error(-1, errno, "accept() failed");
        }
        printf("Talking to client.\n");
        // sey hello to the other side
        write_str_to_fd(conn_sock_fd, "Secret Server 1.0\n");
        write_str_to_fd(conn_sock_fd, "Password:");
        // read response from socket (password)
        read_line_from_fd(conn_sock_fd, globals.buffer);
        // check if it was a correct password
        if (strcmp(globals.buffer, globals.password) == 0) {
            // password was correct, reveal the secret
            printf("Client entered correct password.\n");
            write_str_to_fd(conn_sock_fd, "The secret is: ");
            write_str_to_fd(conn_sock_fd, globals.secret);
            write_str_to_fd(conn_sock_fd, "\n");
        }
        else {
            // password was incorrect, don't reveal the secret
            printf("Client entered incorrect password.\n");
            write_str_to_fd(conn_sock_fd, "Wrong password.\n");
        }
        // close the connection
        shutdown(conn_sock_fd, SHUT_RDWR);
        close(conn_sock_fd);
    }
    // this will never be called
    close(listen_sock_fd);
    return 0;
}
