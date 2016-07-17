# MersennePrime_Python_CPP_GMP_BenchMark
A Mersenne Prime finder Python app that wraps a C++ solver that uses ultra-extended precision arithmetic from libgmp library and implements the Lucas-Lehmer algo.  The Python block breaks the job into tasks over a user specified number of threads.

Mersenne Primes have the format: MP = 2^p - 1, where p is a standard prime number.  Not all p result in a Mersenne.  Lucas/Lehmer discovered an efficient test for MP-ness.  The MP's grow quickly to have huge numbers of digits.  

The largest prime number discoveries have been Mersenne's.  There are 49 known to date.  The latest: On January 19, 2016, Curtis Cooper published his discovery of a 49th Mersenne prime, 2^74,207,281 − 1, having 22,338,618 digits.  He has discovered the last 4 largest primes.  He uses the globally available GIMP network to perform his searches.  More about them here: https://en.wikipedia.org/wiki/Mersenne_prime.

Python by default can handle arbitrary integer size.  C/C++'s std lib can't nominally handle larger than quad precision, but the Gnu Multi-Precision library is designed to handle arbritrary precision arithmetic.  Clever algorithms allow realizable performance for what would otherwise be order-polynomial complexity.  For example, sqr(N) performance for multiplications.  An example of the cleverness: FFT's are used above a user configurable threshold of digits to perform a multiplication.

This is a simple design that was started with Python in an exploration of "perfect numbers" - associated with Mersenne's as described in the provided reference.  The performance enhancement with the GMP lib allowed the Mersenne search in this case to grow from about 10,000 primes (values of p) with Python, in reasonable time, to about 30,000 in reasonable time on my 12 core linux server.  I now use this to do a quick and dirty personal benchmark with a known multiprocessing algorithm when evaluating a new machine.  The work could relatively quickly be extended to an arbitrary number of servers - but the infrastructure and the fact that without special configuration, a single Mersenne test needs to be contained entirely within one thread - finally limits the performance.  The GIMP network has been tweaked for many years to yield the fastest performance.  I've considered would could be gained with FPGA's - I think that's been considered elsewhere, too.  I think significant gains could be made - again, using some clever fast algorithms to perform the test.

I chose PyBindGen as my wrapper interface API instead of Boost Python.  BP doesn't allow arbitrary precision arithmetic - or didn't, as of 2013, when I was deciding.  PyBindGen is simple and met the needs and it led to a quick decision without evaluating any of the other candidate frameworks that could potentially do the same thing.

Potential Improvements:

I believe I could make my own version faster on my server - I spent only a low to moderate amount of time optimizing it using /usr/bin/perf.  The bottleneck is in the the Lucas-Lehmer calculation - specifically the multiplication.  NUMA plus careful attention to memory allocation will be required to make it faster.  The last portion of the test is the pickle transmission from the multiple threads back to the consolidation function for sorting annd printing the resulting primes.  This could easily be streamlined, or in fact ignored if desired, since the unsorted results and elapsed times have already been printed before that begins.  It more than doubles the processing time above about 20,000 standard primes.  I could also clean up the resulting printout's and use matplotlib to explore potential correlations between the resulting prime numbers.  I'm certain that has been beaten to death over the years in order to find some way to narrow the search and the numerical processing, but I'd like to see it for myself.

Required:

o Linux OS - tested on Ubuntu 13.10 and up

o g++: tested with 4.9 and up

o libgmpxx.so: tested with libgmpxx.so.4.5.0, can be gotten at: https://gmplib.org

o Python2.7

o PyBindGen: tested with 0.15.0 and up, can be gotten at: https://pypi.python.org/pypi/PyBindGen

PerfNumMultiCLL.py -h gives:
     
     usage: PerfNumMultiCLL.py [-h] [-t THREADS] [-r PRIME_RANGE]

     optional arguments:
     
     	      -h, --help            show this help message and exit
	      
  	      -t THREADS, --threads THREADS
                        Number of threads
			
  	      -r PRIME_RANGE, --prime_range PRIME_RANGE
                        Range of primes to search starting with 1 to this
                        number
			
To build and test on a single command line:

   bash -p -c "gmake clean && gmake" && taskset -c 0-10 bash -c 'PerfNumMultiCLL.py -t 10 -r 10001'

Here, taskset is used to choose 11 cores on a platform.

The result should look something like: 

$ bash -p -c "gmake clean && gmake" && taskset -c 0-10 bash -c 'PerfNumMultiCLL.py -t 10 -r 10001'
rm -f lucaslehmerpy_bind.cpp liblucaslehmerpy.so lucaslehmerpy.o lucaslehmerpy_bind.o lucaslehmer.so
Clean done
PYTHONPATH=:./ python lucaslehmerBind.py > lucaslehmerpy_bind.cpp
g++  -O3 -fPIC -frecord-gcc-switches -I/usr/include/python2.7 -c -o lucaslehmerpy.o lucaslehmerpy.cpp
g++ -shared -fPIC  -O3 -rdynamic -Wl,-rpath -Wl,/home/wade/Dev/Python/MersennePrime_Python_CPP_GMP_BenchMark -Wl,-rpath -Wl,/usr/lib/x86_64-linux-gnu -lgmpxx -lgmp -o liblucaslehmerpy.so lucaslehmerpy.o
g++  -O3 -fPIC -frecord-gcc-switches -I/usr/include/python2.7 -c -o lucaslehmerpy_bind.o lucaslehmerpy_bind.cpp
g++ -o lucaslehmer.so lucaslehmerpy_bind.o -shared -fPIC  -O3 -rdynamic -Wl,-rpath -Wl,/home/wade/Dev/Python/MersennePrime_Python_CPP_GMP_BenchMark -Wl,-rpath -Wl,/usr/lib/x86_64-linux-gnu -L. -llucaslehmerpy -lgmpxx -lgmp
Build done
Total number of primes in set:  1229
                2 ... time: from start 0.051437 -- elapsed: 0.000041
                5 ... time: from start 0.054208 -- elapsed: 0.000036
                7 ... time: from start 0.053408 -- elapsed: 0.000046
                3 ... time: from start 0.057826 -- elapsed: 0.000050
                19 ... time: from start 0.054790 -- elapsed: 0.000046
                13 ... time: from start 0.055211 -- elapsed: 0.000036
                17 ... time: from start 0.055658 -- elapsed: 0.000047
                31 ... time: from start 0.154257 -- elapsed: 0.000056
                61 ... time: from start 0.159354 -- elapsed: 0.000058
                107 ... time: from start 0.263329 -- elapsed: 0.000064
                89 ... time: from start 0.264786 -- elapsed: 0.000044
                127 ... time: from start 0.370253 -- elapsed: 0.000047
                521 ... time: from start 1.003569 -- elapsed: 0.000351
                607 ... time: from start 1.205115 -- elapsed: 0.000289
Monitor: mon_val = 1000, value now = 1009
                1279 ... time: from start 2.157965 -- elapsed: 0.001700
Monitor: mon_val = 2000, value now = 2003
                2203 ... time: from start 3.442381 -- elapsed: 0.006397
                2281 ... time: from start 3.559078 -- elapsed: 0.009585
Monitor: mon_val = 3000, value now = 3001
                3217 ... time: from start 4.819234 -- elapsed: 0.026981
Monitor: mon_val = 4000, value now = 4001
                4253 ... time: from start 6.226845 -- elapsed: 0.064278
                4423 ... time: from start 6.427267 -- elapsed: 0.054439
Monitor: mon_val = 5000, value now = 5003
Monitor: mon_val = 6000, value now = 6007
Monitor: mon_val = 7000, value now = 7001
Monitor: mon_val = 8000, value now = 8009
Monitor: mon_val = 9000, value now = 9001
                9689 ... time: from start 23.469367 -- elapsed: 0.449409
                9941 ... time: from start 25.214372 -- elapsed: 0.453314
Shutdown initiated
You exited!

