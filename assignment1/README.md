# **CPSC 526 Winter 2025**
## **Assignment 1 Readme**


### **Collaborators**
- **Name**: Abdelrahman Abbas, Issam Akhtar
- **Student ID**: 30110374

- **Partner Name**: Issam Akhtar
- **Partner Student ID**: 


### **Task 1 – Exploit the Vulnerability in 2 Connections**

In the first connection we sent an input exceeding the buffer size (`BUFFSIZE=32`) to overwrite the server's stored password with a new desired password (`NewPass`). This was achieved by sending a payload structured as `'NewPass'` followed by padding and the new password. In the second connection, we simply sent the new password (`NewPass`) to successfully retrieve the secret without knowing the original password.

### **Task 2 – Exploit the Vulnerability in a Single Connection**

 Created a single payload that simultaneously overwrote the stored password and set the buffer content to the new password. By inserting a null byte (`\x00`) after the new password and padding the remaining buffer space with filler characters (`.`), the server interprets the new password correctly within a single connection. The payload format was `'secret\0.........................secret\n'`, which effectively tricked the server into revealing the secret by recognizing the manipulated password.


### **Task 3 – Write a Python Code to Automatically Run the Exploit**

 The script iterates through possible `BUFFSIZE` values (ranging from 8 to 128) to determine the correct buffer size dynamically. For each iteration, it constructs the appropriate payload with the new password, null byte, and padding, then sends this payload to the server. Upon successful exploitation, the script captures and displays the secret. This automation ensures that the exploit works across different buffer sizes without manual adjustments.

### **Task 4 – Fix the Vulnerability**

 Implementing proper bounds checking and using safer string handling functions. Specifically, we modified the `read_line_from_fd` function to limit the number of characters read into the buffer, ensuring it does not exceed `BUFFSIZE - 1` to accommodate the null terminator. Additionally, we replaced `strncpy` with safer alternatives and ensured that all string operations enforce null-termination. These changes effectively prevent buffer overflows by restricting input lengths and maintaining memory integrity.
