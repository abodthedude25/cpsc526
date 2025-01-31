.PHONY: all

all: fixedSecretServer 

fixedSecretServer: fixedSecretServer.c Makefile
	gcc -Wall -Wextra -DBUFFSIZE=32 fixedSecretServer.c -o fixedSecretServer


clean:
	/bin/rm -f *~
	/bin/rm -f fixedSecretServer
