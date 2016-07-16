# MersennePrime_Python_CPP_GMP_BenchMark
A Mersenne Prime finder Python app that wraps a C++ solver that uses ultra-extended precision arithmetic from libgmp library and implements the Lucas-Lehmer algo.  Breaks the job into tasks on user specified number of cores.

Required: 	o Linux OS - tested on Ubuntu 13.10 and up\n
			o g++: tested with 4.9 and up\n
			o libgmpxx.so: tested with libgmpxx.so.4.5.0\n
			o Python2.7\n
			o PyBindGen: tested with 0.15.0 and up, can be gotten at: https://pypi.python.org/pypi/PyBindGen\n

To build and test on a single command line:

	bash -p -c "gmake clean && gmake" && taskset -c 0-10 bash -c 'LD_PRELOAD="./liblucaslehmerpy.so ./lucaslehmer.so /usr/lib/x86_64-linux-gnu/libgmpxx.so" PerfNumMultiCLL.py 10 20001'	

Here, taskset is used to choose 11 cores on a platform.  The parameters 10 and 20001 mean: use 10 threads and find all the Mersenne Primes within the first 20001 primes starting at 1.
