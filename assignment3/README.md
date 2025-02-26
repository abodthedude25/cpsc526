## WARNING
Do not upload any files in this repository to public websites. If you clone this repository, keep it private.



# a3-dekrypt

Starter code for CPSC 526 Assignment 3.

## enkrypt.py

`enkrypt.py` accepts password on command line, and then encrypts all data on standard input using AES-128-CTR. It writes output to stdout. THe program uses PBKDF2 with the password and a random salt to create AES key. It also uses a random IV for the CTR mode.

Example - encrypt a file with password `pwd`, using random salt and IV:
```shell
$ ./enkrypt pwd < file1 > file2
```

The salt and IV (both 16-byte values) are written in the first 32 bytes of the output:
```shell
$ xxd -l 32 < file2
00000000: 0d55 7da9 85bb c6f8 ad51 194e 30a0 3c3a  .U}......Q.N0.<:
00000010: 2669 34ab 6a5f d2e5 3283 6a65 6c8c 3271  &i4.j_..2.jel.2q
```

Example - encrypting a file with non-random nonces:
```shell
$ ./enkrypt -nonce 1234 pwd < file1 > file2
```

## other files

`dekrypt1.py`, `dekrypt2.py` and `dekrypt3.py`
* If you like, you can use these files as starting points for tasks 1-3.

`inp/` directory
* sample input files

`out/` directory
* sample encrypted files


