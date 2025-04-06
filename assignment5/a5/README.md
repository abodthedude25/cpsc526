## WARNING
Do not upload any files in this repository to public websites. If you clone this repository, keep the repository private.

# fw-sim
Starter code for CPSC 526 Assignment 5.

## running the simulator
To run the simulator, give it two filenames: rules and packets. Example:
```shell
$ ./fw.py rules0.txt packets0.txt
accept(2)    in  136.159.5.22    22    1
accept(2)    in  10.0.0.44       80    0
accept(5)    out 10.0.1.1        80    0
```
The only file you should modify and submit for grading is `fwsim.py`.
