# CPSC 526 Assignment 2: Client-Server File Transfer System

### **Collaborators**

-   **Name**: Abdelrahman Abbas
-   **Student ID**: 30110374

-   **Name**: Issam Akhtar
-   **Student ID**: 30131310

## Features Implemented

### 1. **Secure Handshake with SHA256**

The server and client establish a secure connection using a shared secret (SECRET526) verified via a SHA256 challenge-response protocol. When a client connects, the server generates an 8-character random challenge and sends it to the client. The client appends the shared secret to this challenge, computes its SHA256 hash, and returns it to the server. The server then compares this hash with its own computation of the challenge + secret. If they match, the handshake succeeds, and communication proceeds.

### 2. Supported Commands

#### **pwd**

The pwd command retrieves the server’s current working directory. When the client sends this command, the server immediately responds with its full path (e.g., /home/issam). This command is straightforward and serves as a basic test of server responsiveness.

-   **Usage**: `pwd`
-   **Example**:
    ```bash
    > pwd
    Output: /home/issam/
    ```

#### **cd**

The cd command changes the server’s working directory. The client sends the target directory name, and the server attempts to navigate to it. If successful, the server returns the new path; otherwise, it sends an error message (e.g., No such file or directory). This command also handles unusual directory names.

-   **Usage**: `cd <dirname>`
-   **Example**:
    ```bash
    > cd proj
    Output: /home/user/proj
    > cd nonexisting
    cd: No such file or directory
    ```

#### **ls**

The ls command lists the contents of the server’s current directory. The client can pass options (e.g., -l, -a) directly to the server, which executes the corresponding ls command on its filesystem. The server sends each line of output followed by a --- delimiter to signal completion.

-   **Usage**: `ls [options]`
-   **Example**:
    ```bash
    > ls -l
    Output:
    total 480
    -rw-r--r--@  1 issam  staff  216969 Feb 10 11:53 CPSC526W25-Assignment2-v1.pdf
    -rw-r--r--   1 issam  staff    6845 Feb 24 19:44 README.md
    -rwxr-xr-x@  1 issam  staff    6625 Feb 24 19:30 client.py
    -rw-r--r--@  1 issam  staff    3877 Feb 24 19:30 common.py
    -rwxr-xr-x@  1 issam  staff    6501 Feb 24 19:30 server.py
    drwxr-xr-x  10 issam  staff     320 Feb 24 19:30 testDir
    ---
    ```

#### **cat**

The cat command retrieves the contents of a file on the server. The server reads the file, Base64-encodes its contents, and sends it line-by-line to the client, ending with a # delimiter. The client decodes the content and displays it. If the file is binary, the client alerts the user instead of attempting to render it.

-   **Usage**: `cat <filename>`
-   **Example**:
    ```bash
    > cat weird2.txt
    This file has filename that's tough to handle.
    'weird2.txt
    ```

#### **sha256**

The sha256 command computes the SHA256 hash of a file on the server. The server reads the file, computes its hash, and returns it to the client. If the file does not exist, the server sends an error message.

-   **Usage**: `sha256 <filename>`
-   **Example**:
    ```bash
    > sha256 code.cpp
    Output: c454f865fa2cf05252279887bfb68006f60d36677c5d11f0caa3311b2be59a51
    ```

#### **download**

The download command implements smart file transfer by comparing hashes before downloading. The client requests the file, and the server responds with its SHA256 hash. The client checks if a local file with the same name exists and matches the hash. If they match, the client skips the download; otherwise, it requests the file content. The server sends the file encoded in Base64, which the client decodes and saves.

-   **Usage**: `download <filename>`
-   **Example**:
    ```bash
    > download penguin.jpg
    Output: downloaded 21345 bytes
    > download penguin.jpg  # Second time
    Output: download skipped - local file matches remote file
    ```

#### **upload**

The upload command mirrors the download process but in reverse. The client computes the SHA256 hash of the local file and sends it to the server. If the server’s file matches the hash, the upload is skipped. Otherwise, the client sends the file content encoded in Base64, which the server decodes and writes to disk

-   **Usage**: `upload <filename>`
-   **Example**:
    ```bash
    > upload penguin.jpg
    Output: uploaded 123 bytes
    > upload penguin.jpg  # Duplicate file
    Output: upload skipped - local file matches remote file
    ```

---

**Smart File Transfer Mechanism**

Both download and upload commands leverage SHA256 hashes to determine whether a file transfer is necessary. By comparing hashes, the system avoids transferring files that already exist and match on both ends. This optimization is particularly useful for large files or slow network connections. Additionally, all file transfers use Base64 encoding to preserve binary data integrity, ensuring that files like images, executables, and compressed archives are transferred without corruption.

---

**Protocol Design**

The client and server communicate using a hybrid text-based protocol with clear delimiters as well as base64 encoding for uploads and downloads. Commands and responses are sent line-by-line, with special markers like # and --- to signal the end of content. For example, when listing directory contents with ls, the server sends each line followed by --- to indicate completion. Similarly, file contents are sent in Base64-encoded chunks terminated by #. Error handling is integrated into the protocol. If a command fails (e.g., invalid directory, permission denied), the server sends an error message (e.g., ERROR: Permission denied), which the client displays to the user.

---

**Security and Environment Variables**

There are multiple options to source the secret to the code: - Secret is sourced from `SECRET526` environment variable, a file `.secret526`, or hardcoded when running the command. - Example configuration:
`bash
        export SECRET526=mySecureSecret123
        SECRET526=111111 ../server.py -d 2222
        `

---

**Testing Unusual Filenames**

-   **Examples Tested**:
    -   `weird .txt` (with space)
    -   `\ weird\ 3.\ txt` (leading whitespace with backslash)
    -   `weird~!@#.file` (special characters)
-   **Handling**: Filenames are sanitized by stripping backslashes and spaces are preserved.

---

**Usage Examples**

#### **Client Interaction**

```bash
$ SECRET526=secure ./client.py localhost 22222
Connected...
> pwd
/home/user
> upload empty.dat
uploaded 10240 bytes
> download empty.dat
downloaded 10240 bytes
> download empty.dat
download skipped - local file matches remote file
> sha256 empty.dat
1a79a4d60de6718e8e5b326e338ae533
```

#### **Server Log**

```bash
[dbg] client connected from 127.0.0.1:3456
[dbg] executing command: upload empty.dat
[dbg] received file: empty.dat saved successfully.
```

### How to Run

1. **Set the Environment Variable**:
    ```bash
    export SECRET526="abc123"
    ```
2. **Start the Server**:
    ```bash
    python3 server.py 22222 -d
    ```
3. **Start the Client**:
    ```bash
    python3 client.py localhost 22222
    ```

---
