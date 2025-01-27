.PHONY: all

all: secretServer 

secretServer: secretServer.c Makefile
	gcc -Wall -Wextra -DBUFFSIZE=32 secretServer.c -o secretServer


clean:
	/bin/rm -f *~
	/bin/rm -f secretServer
