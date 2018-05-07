# MersennePrime_Python_CPP_GMP_BenchMark
A Mersenne Prime finder Python app that wraps a C++ solver that uses ultra-extended precision arithmetic from libgmp library and implements the Lucas-Lehmer algo.  The Python block breaks the job into tasks over a user specified number of threads.

Mersenne Primes have the format: MP = 2^p - 1, where p is a standard prime number.  Not all p result in a Mersenne.  Lucas/Lehmer discovered an efficient test for MP-ness.  The MP's grow quickly to have huge numbers of digits.  

The largest prime number discoveries have been Mersenne's.  There are 50 known to date.  The latest: On Dec. 26, 2017, Jonathon Pace published his discovery of a 50th Mersenne prime, 2^77,232,917 − 1, having 23,249,425 digits.  He used the globally available GIMP network to perform his searches.  More about them here: https://en.wikipedia.org/wiki/Mersenne_prime.

Python by default can handle arbitrary integer size.  C/C++'s std lib can't nominally handle larger than quad precision, but the Gnu Multi-Precision library is designed to handle arbritrary precision arithmetic.  Clever algorithms allow realizable performance for what would otherwise be order-polynomial complexity.  For example, sqr(N) performance for multiplications.  An example of the cleverness: FFT's are used above a user configurable threshold of digits to perform a multiplication.

Mine is a simple design that was started with Python in an exploration of "perfect numbers" - associated with Mersenne's as described in the provided reference's references.  Performance enhancement with replacement of the MP-test using the GMP lib allowed the Mersenne search in this case to grow from testing p's in the range of the first 10,000 whole numbers with Python, in reasonable time, to a range of the first 200,000 in reasonable time on my 12 core linux server.  I now use this framework to do a quick and dirty personal benchmark with a known multiprocessing algorithm when evaluating a new machine.  The work could relatively quickly be extended to an arbitrary number of servers - but the infrastructure and the fact that without special configuration, a single Mersenne test needs to be contained entirely within one thread - finally limits the performance.  

As a side note: The GIMP network has been tweaked for many years to yield the fastest performance.  I've considered what could be gained with the use of FPGA's - I think that's been considered elsewhere, too.  I think significant gains could be made - again, using some clever fast algorithms to perform the test.

I chose PyBindGen as my wrapper interface API for the C extension instead of Boost Python.  BP doesn't allow arbitrary precision arithmetic - or didn't, as of 2013, when I was deciding.  PyBindGen is simple and met the needs and it led to a quick decision without evaluating any of the other candidate interfaces that could potentially do the same thing.

Potential Improvements:

 - I believe I could make my own version faster on my server - I spent only a low to moderate amount of time optimizing it using /usr/bin/perf.  The bottleneck is in the the Lucas-Lehmer calculation - specifically the multiplication (~35% of the time is spent in this on GMP API call doing the squaring in the equation: s = (sqr(s) - 2) % M, where M = 2^p -1.  This is executed p - 2 times for each tested p value.  There's no good way to memoize or pre-calculate general (independent of M) values to be used in the equation - the growth of s without the mod M portion is extreme - beyond the realm of storage bitwise in any earth-bound compute system and quickly far surpassing the huge value of M - thus requiring M for the calculation.  Note that the newest largest M is found with p = 77,232,917.  My server can't approach the reproduction of this one, or anything reasonably above p = 5 million or so.

- Due to the need so far to perform the LL loop single-threaded, I could also achieve significant performance gains by using one of the newest Xeon processors with relatively huge last-level cache operating overclocked.  A sea of such things would probably enable my algorithm to make a realistic attempt to tackle a new record.  A sea of such entities would require a flood of money, too (I prefer to avoid the reputed ease of using GIMP - I haven't tried it).
 
 - I could also use matplotlib to explore potential correlations between the resulting prime numbers and most importantly, the p - 2 intermediate steps in the lucas-lehmer algorithm.  I'm certain that has been beaten to death over the years in order to find some way to narrow the search and the numerical processing, but I'd like to see it for myself.
 
 - I could convert the python2.7 to python3, but that is non-trivial and isn't just as simple as running 2to3.  The C-api conversions in this case will require a moderate and fully manual effort.

Required:

	o Linux OS - tested on Ubuntu 13.10 and up - latest: Fedora 27

	o g++: tested with 4.9 and up - latest: 7.3.1

	o libgmpxx.so: tested with libgmpxx.so.4.5.0, can be gotten at: https://gmplib.org

	o Python2.7

	o PyBindGen: tested with 0.15.0 and up, can be gotten at: https://pypi.python.org/pypi/PyBindGen

PerfNumMultiCLL.py -h gives:

        usage: PerfNumMultiCLL.py [-h] [-t THREADS]
                                  [-r PRIME_RANGE | -p PRIME_VALUE | -l PRIME_LIST [PRIME_LIST ...]
                                  | -n RETURN_NUM_PRIMES_IN_RANGE]

        optional arguments:
          -h, --help            show this help message and exit
          -t THREADS, --threads THREADS
                                Number of threads
          -r PRIME_RANGE, --prime_range PRIME_RANGE
                                Range of primes to search starting with 1 to this
                                number
          -p PRIME_VALUE, --prime_value PRIME_VALUE
                                A specific prime value to test
          -l PRIME_LIST [PRIME_LIST ...], --prime_list PRIME_LIST [PRIME_LIST ...]
                                A space separated list of specific primes to test
          -n RETURN_NUM_PRIMES_IN_RANGE, --return_num_primes_in_range RETURN_NUM_PRIMES_IN_RANGE
                                Return the number of standard primes from 2 to the
                                given value
			
1) To build and test on 10 worker threads over the primes found in the first 10,001 whole numbers on a single command line:

$  bash -p -c "gmake clean && gmake" && bash -c 'PerfNumMultiCLL.py -t 10 -r 10001'

rm -f lucaslehmerpy_bind.cpp liblucaslehmerpy.so lucaslehmerpy.o lucaslehmerpy_bind.o lucaslehmer.so

Clean done

PYTHONPATH=:./ python lucaslehmerBind.py > lucaslehmerpy_bind.cpp

g++ -g -O3 -w -fPIC -frecord-gcc-switches -I/usr/include/python2.7 -std=c++14 -c -o lucaslehmerpy.o lucaslehmerpy.cpp

g++ -shared -fPIC -g -O3 -rdynamic -Wl,-rpath -Wl,/home/wade/Dev/Python/MersennePrime_Python_CPP_GMP_BenchMark -Wl,-rpath -Wl,/usr/lib/x86_64-linux-gnu -lgmpxx -lgmp -o liblucaslehmerpy.so lucaslehmerpy.o

g++ -g -O3 -w -fPIC -frecord-gcc-switches -I/usr/include/python2.7 -std=c++14 -c -o lucaslehmerpy_bind.o lucaslehmerpy_bind.cpp

g++ -o lucaslehmer.so lucaslehmerpy_bind.o -shared -fPIC -g -O3 -rdynamic -Wl,-rpath -Wl,/home/wade/Dev/Python/MersennePrime_Python_CPP_GMP_BenchMark -Wl,-rpath -Wl,/usr/lib/x86_64-linux-gnu -L. -llucaslehmerpy -lgmpxx -lgmp

Build done
  
Total number of primes in set: 1229

  		----------------------------------------------------------------------------------------------
  		|         Tested Value         |      Time From App Start     |     Elapsed Time To Calc     |
  		----------------------------------------------------------------------------------------------
  		|                        3     |                 0.077552     |                 0.000394     |
		----------------------------------------------------------------------------------------------
  		|                        5     |                 0.081690     |                 0.000554     |
		----------------------------------------------------------------------------------------------
  		|                        7     |                 0.085645     |                 0.000324     |
		----------------------------------------------------------------------------------------------
  		|                       13     |                 0.093307     |                 0.000679     |
		----------------------------------------------------------------------------------------------
  		|                       17     |                 0.098780     |                 0.000438     |
		----------------------------------------------------------------------------------------------
  		|                       19     |                 0.105030     |                 0.000565     |
		----------------------------------------------------------------------------------------------
  		|                       31     |                 0.124716     |                 0.000709     |
		----------------------------------------------------------------------------------------------
  		|                       61     |                 0.173454     |                 0.000433     |
		----------------------------------------------------------------------------------------------
  		|                       89     |                 0.236665     |                 0.000402     |
		----------------------------------------------------------------------------------------------
  		|                      107     |                 0.275323     |                 0.000272     |
		----------------------------------------------------------------------------------------------
  		|                      127     |                 0.308952     |                 0.000434     |
		----------------------------------------------------------------------------------------------
  		|                      521     |                 0.727131     |                 0.000722     |
		----------------------------------------------------------------------------------------------
  		|                      607     |                 0.792134     |                 0.000773     |
		----------------------------------------------------------------------------------------------
  		|                     1279     |                 1.259954     |                 0.002469     |
		----------------------------------------------------------------------------------------------
  		|                     2203     |                 1.790522     |                 0.009780     |
		----------------------------------------------------------------------------------------------
  		|                     2281     |                 1.889030     |                 0.006947     |
		----------------------------------------------------------------------------------------------
  		|                     3217     |                 2.648756     |                 0.021875     |
		----------------------------------------------------------------------------------------------
  		|                     4253     |                 4.200098     |                 0.035039     |
		----------------------------------------------------------------------------------------------
  		|                     4423     |                12.537035     |                 0.059899     |
		----------------------------------------------------------------------------------------------
  		|                     9689     |                20.587355     |                 0.462537     |
		----------------------------------------------------------------------------------------------
  		|                     9941     |                22.196429     |                 0.497361     |
		----------------------------------------------------------------------------------------------



2) To then run the case of reproducing as many of the 50 known Mersenne Primes in 2 mins, you would do the following and get the subsequent result:

$  timeout -s SIGINT 120s PerfNumMultiCLL.py -t 10 -l $(cat known_mp_list.txt | tr '\n' ' ')
  
Total number of values to test in set: 47

  		----------------------------------------------------------------------------------------------
  		|         Tested Value         |      Time From App Start     |     Elapsed Time To Calc     |
  		----------------------------------------------------------------------------------------------
  		|                        3     |                 0.025677     |                 0.000355     |
		----------------------------------------------------------------------------------------------
  		|                        5     |                 0.030043     |                 0.000197     |
		----------------------------------------------------------------------------------------------
  		|                        7     |                 0.043573     |                 0.000457     |
		----------------------------------------------------------------------------------------------
  		|                       13     |                 0.055922     |                 0.000327     |
		----------------------------------------------------------------------------------------------
  		|                       17     |                 0.061132     |                 0.000504     |
		----------------------------------------------------------------------------------------------
  		|                       19     |                 0.066268     |                 0.000432     |
		----------------------------------------------------------------------------------------------
  		|                       61     |                 0.073579     |                 0.000591     |
		----------------------------------------------------------------------------------------------
  		|                      107     |                 0.079775     |                 0.000450     |
		----------------------------------------------------------------------------------------------
  		|                       89     |                 0.084976     |                 0.000305     |
		----------------------------------------------------------------------------------------------
  		|                      127     |                 0.094240     |                 0.000773     |
		----------------------------------------------------------------------------------------------
  		|                      521     |                 0.102225     |                 0.001041     |
		----------------------------------------------------------------------------------------------
  		|                      607     |                 0.107375     |                 0.000567     |
		----------------------------------------------------------------------------------------------
  		|                     1279     |                 0.114181     |                 0.002030     |
		----------------------------------------------------------------------------------------------
  		|                       31     |                 0.119691     |                 0.000408     |
		----------------------------------------------------------------------------------------------
  		|                     2203     |                 0.123170     |                 0.006910     |
		----------------------------------------------------------------------------------------------
  		|                     2281     |                 0.131885     |                 0.008673     |
		----------------------------------------------------------------------------------------------
  		|                     3217     |                 0.147968     |                 0.020942     |
		----------------------------------------------------------------------------------------------
  		|                     4423     |                 0.175509     |                 0.041126     |
		----------------------------------------------------------------------------------------------
  		|                     4253     |                 0.184482     |                 0.051553     |
		----------------------------------------------------------------------------------------------
  		|                     9941     |                 0.635446     |                 0.495023     |
		----------------------------------------------------------------------------------------------
  		|                    11213     |                 0.882603     |                 0.741126     |
		----------------------------------------------------------------------------------------------
  		|                    19937     |                 3.273970     |                 3.125011     |
		----------------------------------------------------------------------------------------------
  		|                    21701     |                 3.917314     |                 3.766983     |
		----------------------------------------------------------------------------------------------
  		|                    23209     |                 4.573598     |                 4.401419     |
		----------------------------------------------------------------------------------------------
  		|                    44497     |                23.559502     |                23.370437     |
		----------------------------------------------------------------------------------------------
  Killed by ctrl-C

3) To explore and test a particular value of p, you could run:

$  PerfNumMultiCLL.py -t 10 -p 44497

  		----------------------------------------------------------------------------------------------
  		|         Tested Value         |      Time From App Start     |     Elapsed Time To Calc     |
  		----------------------------------------------------------------------------------------------
  		|                    44497     |                14.221298     |                14.198381     |
		----------------------------------------------------------------------------------------------
