# **CPSC 526 Winter 2025**

## **Assignment 1 Readme**

### **Collaborators**

-   **Name**: Abdelrahman Abbas
-   **Student ID**: 30110374

-   **Name**: Issam Akhtar
-   **Student ID**: 30131310

### **Task 1 – Exploit the Vulnerability in 2 Connections**

In the first connection we sent an input exceeding the buffer size (`BUFFSIZE=32`) to cause buffer overlow of the global.buffer and overwrite the server's stored password (global.password ) with a new desired password (`NewPass`). This was achieved by sending a payload structured as `'NewPass'` prepended by padding and the new password. In the second connection, we simply sent the new password (`NewPass`) to successfully retrieve the secret without knowing the original password. We verfied this by adding print statements and checking the memory addresses of the buffer and password arrays:
Memory increasing downwards <br>
Buffers Memory Address: 4040c4 <br>
Password's Memory Address: 4040e4 <br>
Exploit: <br>
`'printf '................................secret' | nc localhost 1235'` <br>
`'printf 'secret' | nc localhost 1235'`

### **Task 2 – Exploit the Vulnerability in a Single Connection**

Created a single payload that simultaneously overwrote the stored password and set the buffer content to the new password. By inserting a null byte (`\x00`) after the new password and padding the remaining buffer space with filler characters (`.`), the server interprets the new password correctly within a single connection. The payload format was `'secret\0.........................secret\n'`, which effectively tricked the server into revealing the secret by recognizing the manipulated password.
Here we are overriting the input buffer array into the password array , the \0 is used to end the input buffer as a string. This means that when we do a string comparison or read the buffer as a string, it will stop at \0 but we still have the leftover characters in the buffer. Since we are wriiting these chars into the buffer, we are doing overflow. we fill the rest of the buffer array with '.' and when we overflow, we overflow with the passowrd we stored in the beginning of the input bufffer
Memory increasing downwards
Buffers Memory Address: 4040c4 Written by first instance of secret and overflowed with '.'
Password's Memory Address: 4040e4 Overwritten by second instance of secret after 32 chars
Exploit: <br>
`'printf 'secret\0.........................secret' | nc localhost 1235'`

### **Task 3 – Write a Python Code to Automatically Run the Exploit**

The script iterates through possible `BUFFSIZE` values (ranging from 8 to 128) to determine the correct buffer size dynamically. For each iteration, it constructs the appropriate payload with the new password, null byte, and padding, as shown in Task 2, then sends this payload to the server. Upon successful exploitation, the script captures and displays the secret.

### **Task 4 – Fix the Vulnerability**

Implementing proper bounds checking and using safer string handling functions. Specifically, we modified the `read_line_from_fd` function to limit the number of characters read into the buffer, ensuring it does not exceed `BUFFSIZE - 1` to accommodate the null terminator. Additionally, we replaced `strncpy` with safer alternatives and ensured that all string operations enforce null-termination. These changes effectively prevent buffer overflows by restricting input lengths and maintaining memory integrity.
