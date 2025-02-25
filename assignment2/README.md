# CPSC 526 Assignment 2: Client-Server File Transfer System

### **Collaborators**

-   **Name**: Abdelrahman Abbas
-   **Student ID**: 30110374

-   **Name**: Issam Akhtar
-   **Student ID**: 30131310

## Features Implemented

### 1. **Secure Handshake with SHA256**

-   **Server-Side Handshake Workflow**:
    -   Server generates a random 8-character alphanumeric challenge (e.g., `1234abcd`).
    -   Sends the challenge to the client.
    -   Client appends the shared secret (`SECRET526`) to the challenge and computes SHA256.
    -   Client sends the computed hash back to the server.
    -   Server compares the received hash with its own hash (challenge + secret). If they match, sends "OK"; otherwise, disconnects.
-   **Security Mechanism**: Prevents unauthorized access by verifying client authenticity without exposing the secret directly.

---

### 2. **Command Support**

#### **pwd**

-   **Usage**: `pwd`
-   **Client-Side**:
    -   Sends "pwd" command to the server.
-   **Server-Side**:
    -   Immediately responds with the server’s current working directory (e.g., `/home/issam/`).
    -   Handles errors (e.g., permissions) and returns appropriate messages.
-   **Example**:
    ```bash
    > pwd
    Output: /home/services/
    ```

#### **cd**

-   **Usage**: `cd <dirname>`
-   **Client-Side**:
    -   Sends the directory name (unusual names for directories are supported) to the server.
-   **Server-Side**:
    -   Attempts to change the working directory.
    -   Responds with the new directory path if successful, or an error message (e.g., `cd: No such file or directory`).
-   **Example**:
    ```bash
    > cd proj
    Output: /home/user/proj
    > cd nonexisting
    cd: No such file or directory
    ```

#### **ls**

-   **Usage**: `ls [options]`
-   **Client-Side**:
    -   Sends the command with optional arguments (e.g., `ls`).
-   **Server-Side**:
    -   Executes `ls` on the server’s filesystem with provided options.
    -   Sends each line of output followed by `---` to signify the end.
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

-   **Usage**: `cat <filename>`
-   **Client-Side**:
    -   Sends the filename to the server.
-   **Server-Side**:
    -   Reads the file content, Base64-encodes it, and sends lines until `#` is sent.
    -   Decodes on client-side and prints.
-   **Example**:
    `bash
    > cat weird2.txt
This file has filename that's tough to handle.
'weird2.txt
    `

#### **sha256**

-   **Usage**: `sha256 <filename>`
-   **Client-Side**:
    -   Sends filename to server.
-   **Server-Side**:
    -   Computes SHA256 hash of the file and returns it.
    -   If file not found, returns an error message.
-   **Example**:
    ```bash
    > sha256 code.cpp
    Output: c454f865fa2cf05252279887bfb68006f60d36677c5d11f0caa3311b2be59a51
    ```

#### **download**

-   **Usage**: `download <filename>`
-   **Client-Side**:
    -   Initiates download request.
    -   Supports unusual file names
    -   If local file exists and matches server hash, skips transfer.
-   **Server-Side**:
    -   Sends SHA256 hash of the file.
    -   If client accepts, sends Base64-encoded content, finalized with `#`.
-   **Example**:
    ```bash
    > download penguin.jpg
    Output: downloaded 21345 bytes
    > download penguin.jpg  # Second time
    Output: download skipped - local file matches remote file
    ```

#### **upload**

-   **Usage**: `upload <filename>`
-   **Client-Side**:
    -   Sends SHA256 hash of the local file to server.
    -   Supports unusual file names
    -   If server’s hash differs, sends Base64-encoded content.
-   **Server-Side**:
    -   Checks if existing file matches hash.
    -   Writes new content if necessary and sends "OK" or error.
-   **Example**:
    ```bash
    > upload penguin.jpg
    Output: uploaded 123 bytes
    > upload penguin.jpg  # Duplicate file
    Output: upload skipped - local file matches remote file
    ```

---

### 3. **Smart File Transfer Mechanism**

-   **Hash Comparison**:
    -   Both download and upload commands compare file hashes before transferring data.
    -   Reduces unnecessary transfers, enhancing efficiency.
-   **Binary Support**:
    -   Files with binary content (e.g., images, PDFs) are transferred intact using Base64 encoding.

---

### 4. **Protocol Design**

-   **Text-Based Communication**:
    -   Uses line-based protocol with clear delimiters (`---`, `#`).
    -   Example server response after `ls`:
        ```
        -rw------- ...
        drwxr-xr-x ...
        ---
        ```
-   **Error Handling**:
    -   Server sends error messages (e.g., `ERROR: File not found`).
    -   Client formats and displays errors to the user.

---

### 5. **Security and Environment Variables**

-   **Secret Management**:
    -   Secret is sourced from `SECRET526` environment variable, a file `.secret526`, or hardcoded when running the command.
    -   Example configuration:
        ```bash
        export SECRET526=mySecureSecret123
        SECRET526=111111 ../server.py -d 2222
        ```
-   **Hidden Authentication**:
    -   Environment variable approach prevents command-line snooping, increasing security.

---

### 6. **Testing Unusual Filenames**

-   **Examples Tested**:
    -   `weird .txt` (with space)
    -   ` weird 3. txt"` (leading whitespace)
    -   `weird~!@#.file` (special characters)
-   **Handling**: Filenames are sanitized by stripping backslashes and spaces are preserved.

---

### 7. **Error Scenarios Handled**

1. **File/Directory Not Found**:
    - `"cd /invalid" → "No such file or directory"`.
2. **Permission Errors**:
    - `"cat /private" → "Permission denied"`.
3. **Client Disconnects Mid-Transfer**:
    - Server closes connection gracefully and resumes listening.

---

### 8. **Usage Examples**

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
> exit
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
