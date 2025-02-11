## WARNING
Do not upload any files in this repository to public websites. If you clone this repository, keep it private.


# a2-file-transfer

This is skeleton code for CPSC526 Winter 2024 Assignment 2.

I suggest you start your server inside the testDir directory, to avoid accidentally overwriting your source code:
```
$ cd testDir
$ SECRET526=<your secret> ./server.py -d <port number>
```

Once the server is running, you can connect to it using either netcat:
```
# assuming you are running client & server on the same machine
$ nc localhost <port number>
```
 or use the python client:
 ```
# assuming you are running server on cxs1 server:
$ cd testDir
$ SECRET526=<your secret> ./client.py csx1 <port number>
 ```
