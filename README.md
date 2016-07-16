# MersennePrime_Python_CPP_GMP_BenchMark
A Mersenne Prime finder Python app that wraps a C++ solver that uses ultra-extended precision arithmetic from libgmp library and implements the Lucas-Lehmer algo.  The Python block breaks the job into tasks over a user specified number of threads.

Mersenne Primes have the format: MP = 2^p - 1, where p is a standard prime number.  Not all p result in a Mersenne.  Lucas/Lehmer discovered an efficient test for MP-ness.  The MP's grow quickly to have huge numbers of digits.  

The largest prime number discoveries have been Mersenne's.  There are 49 known to date.  The latest: On January 19, 2016, Curtis Cooper published his discovery of a 49th Mersenne prime, 274,207,281 − 1 (a number with 22,338,618 digits).  He has discovered the last 4 largest primes.  He uses the globally available GIMP network to perform his searches.  More about them here: https://en.wikipedia.org/wiki/Mersenne_prime.

Python by default can handle arbitrary integer size.  C/C++'s std lib can't nominally handle larger than quad precision, but the Gnu Multi-Precision library is designed to handle arbritrary precision arithmetic.  Clever algorithms allow realizable performance for what would otherwise be order-polynomial complexity.  For example, sqr(N) performance for multiplications.  An example of the cleverness: FFT's are used above a user configurable threshold of digits to perform a multiplication.

This is a simple design that was started with Python in an exploration of "perfect numbers" - associated with Mersenne's as described in the provided reference.  The performance enhancement with the GMP lib allowed the Mersenne search in this case to grow from about 10,000 primes (values of p) with Python, in reasonable time, to about 30,000 in reasonable time on my 12 core linux server.  I now use this to do a quick and dirty personal benchmark with a known multiprocessing algorithm when evaluating a new machine.  The work could relatively quickly be extended to an arbitrary number of servers - but the infrastructure and the fact that without special configuration, a single Mersenne test needs to be contained entirely within one thread - finally limits the performance.  The GIMP network has been tweaked for many years to yield the fastest performance.  I've considered would could be gained with FPGA's - I think that's been considered elsewhere, too.  I think significant gains could be made - again, using some clever fast algorithms to perform the test.

Potential Improvements:

I believe I could make my own version faster on my server - I spent only a low to moderate amount of time optimizing it using /usr/bin/perf.  The bottleneck is in the the Lucas-Lehmer calculation - specifically the multiplication.  NUMA plus careful attention to memory allocation will be required to make it faster.  The last portion of the test is the pickle transmission from the 10 used cores back to the consolidation function for the resulting primes.  This could easily be streamlined, or in fact ignored if desired, since the results and elapsed times have already been printed before that begins.  It more than doubles the processing time above about 20,000 standard primes.  I could also improve the build process to make it cleaner, with rpaths, for example, to avoid LD_PRELOADs.  I could also clean up the resulting printout's and use matplotlib to explore potential correlations between the resulting prime numbers.  I'm certain that has been beaten to death over the years in order to find some way to narrow the search and the numerical processing, but I'd like to see it for myself.

Required:

o Linux OS - tested on Ubuntu 13.10 and up

o g++: tested with 4.9 and up

o libgmpxx.so: tested with libgmpxx.so.4.5.0, can be gotten at: https://gmplib.org

o Python2.7

o PyBindGen: tested with 0.15.0 and up, can be gotten at: https://pypi.python.org/pypi/PyBindGen

To build and test on a single command line:

	bash -p -c "gmake clean && gmake" && taskset -c 0-10 bash -c 'LD_PRELOAD="./liblucaslehmerpy.so ./lucaslehmer.so /usr/lib/x86_64-linux-gnu/libgmpxx.so" PerfNumMultiCLL.py 10 20001'	

Here, taskset is used to choose 11 cores on a platform.  The parameters 10 and 20001 mean: use 10 threads and find all the Mersenne Primes using the first 20001 standard primes starting at 1.
