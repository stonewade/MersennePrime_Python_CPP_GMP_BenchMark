#!/usr/bin/python

import sys
import os
import math
import random
import fractions
import multiprocessing
import pdb
import signal
import datetime
from datetime import date
import time
import copy
import argparse

from collections import deque

from pybindgen import *

import lucaslehmer

sys.setrecursionlimit(100000)

def addArgs(p):
    p.add_argument("-t", "--threads", type=int, required=False, default=10,
                   help="Number of threads")
    mutex = p.add_mutually_exclusive_group()
    mutex.add_argument("-r", "--prime_range", type=int, required=False, default=0,
                   help="Range of primes to search starting with 1 to this number")
    mutex.add_argument("-p", "--prime_value", type=int, required=False, default=0,
                   help="A specific prime value to test")
    mutex.add_argument("-l", "--prime_list", required=False, nargs="+", default=[],
                   help="A space separated list of specific primes to test")
    
today = date.today()
appstart = time.time()
enabled = True
queue = deque()
jobs = {}
main_pid = 0
sleep_time = 0.1
e = multiprocessing.Event()
spacer = " " * 5
box_top_bottom = '-' * (4 + 6 * len(spacer) + 3 *20)

def writeFlush(str_, stderr_=False, func_=''):
    tz_info = "" if "TZ" not in os.environ.keys() else ' ' + os.environ["TZ"] + ' '
    t_str = '' if not func_ else time.strftime("%Y%m%d %H:%M:%S", time.localtime(time.time())) + tz_info
    func = '' if not func_ else func_ + ": "
    if not stderr_:
        sys.stdout.write(t_str + ' ' + func + ' ' + str_ + "\n")
        sys.stdout.flush()
    else:
        sys.stderr.write(t_str + ' ' + func + ' ' + str_ + "\n")
        sys.stderr.flush()

def lucasLehmer(N):
    if N % 2 == 0:
        return 2
    s = 4
    M = pow(2, N) - 1
    for i in xrange(N - 2):
        if enabled:
            s = ((s * s) - 2) % M
        else:
            return False
    if s:
        return False
    return True

def doLucasLehmer(X):
    if not (X % 2):
        return False
    Clucaslehmer = lucaslehmer.LucasLehmer()
    return Clucaslehmer.sa_lucaslehmer(X);

def doNothing(sig,frame):
    writeFlush("Received SIGINT: letting parent handle it, disabling", True)
    time.sleep(1)
    process.shutdown()

def worker(s, pool, X, force_print=False):
    signal.signal(signal.SIGINT, doNothing)
    name = multiprocessing.current_process().name

    with s:
        pool.makeActive(name)
        timestart = time.time()
        l = doLucasLehmer(X)
        timestop = time.time()
        time_elapsed = timestop - timestart
        from_start = timestop - appstart
        if l or force_print:
            print_str = "\t\t"
            print_str += "|" + spacer + "{0:20d}".format(X) + spacer
            print_str += "|" + spacer + "{0:20.6f}".format(from_start) + spacer
            print_str += "|" + spacer + "{0:20.6f}".format(time_elapsed) + spacer
            print_str += "|"
            print_str += "\n\t\t" + box_top_bottom
            writeFlush(print_str)
        else:
            print_str = "\t\t"
            print_str += "|" + spacer + "{0:20d}".format(X) + spacer
            print_str += "|" + spacer + "{0:20s}".format("    Not Mersenne    ") + spacer
            print_str += "|" + spacer + "{0:20s}".format(' ' * 20) + spacer
            print_str += "|"
            print_str += "\n\t\t" + box_top_bottom
        pool.makeInactive(name)

def primeFact(limit):
    numbers = [ _ for _ in range (2, limit + 1) ]
    primes = []

    while numbers:
        candidate = numbers[0]
        primes.append(candidate)
        for i in range(candidate, limit + 1, candidate):
            if i in numbers: 
                numbers.remove(i)
    return primes

def doPass(sig, frame):
    enabled = False

def checkTheory(s, numlimit, numproc, ct, print_primes, args):
    signal.signal(signal.SIGINT, terminateAll)

    pool = ActivePool()

    global g_ct
    if not ct:
        if not len(args.prime_list):
            primes = []
            try:
                Clucaslehmer = lucaslehmer.LucasLehmer()
                Clucaslehmer.sa_getListOfPrimes(primes, numlimit)
            except:
                writeFlush("Exception getting primes", True)
                sys.exit(1)
            if print_primes:
                writeFlush(str(primes))
        else:
           primes = [int(a) for a in args.prime_list]
        writeFlush("\nTotal number of " + ("primes" if not len(args.prime_list) else "values to test") + " in set: {0}\n".format(len(primes)))
    else:
        primes = [ct]
    writeFlush("\t\t" + box_top_bottom)
    print_str = "\t\t"
    print_str += "|" + spacer + "{0:20s}".format("    Tested Value    ") + spacer
    print_str += "|" + spacer + "{0:20s}".format(" Time From App Start") + spacer
    print_str += "|" + spacer + "{0:20s}".format("Elapsed Time To Calc") + spacer
    print_str += "|"
    writeFlush(print_str)
    writeFlush("\t\t" + box_top_bottom)
    for g_ct in primes:
        name = 'job' + str(g_ct)
        queue.append(name)
        jobs[name] = multiprocessing.Process(target=worker, name=name, args=(s, pool, g_ct))

    start_set = set()
    fin_set = set()

    j_list = jobs.keys()

    for j in j_list:
        if e.is_set():
            writeFlush("Terminated by signal: number of remaining jobs = {0}".format(len(queue)))
            break

        while len(start_set) < numproc and len(queue):
            p = jobs[queue.popleft()]
            #pool.monVal(int(p.name[3:]))
            start_set.add(p.name)
            p.start()

        while True:
            testb = True
            fin_set.clear()
            for j in start_set:
                if not jobs[j].is_alive():
                    if jobs[j].name in start_set:
                        fin_set.add(jobs[j].name)

            for i in fin_set:
                start_set.remove(jobs[i].name)
                jobs[i].join()

            if len(fin_set):
                break

            time.sleep(sleep_time)

            if not len(queue) and not len(start_set) and not len(fin_set):
                break

    for j in jobs:
        if pool.inList(name):
            pool.makeInactive(jobs[j].name)
    '''
    else:
        name = 'job' + str(ct)
        queue.append(name)
        worker(s, pool, ct)
        printResults()
    '''

MAX_THREADS = 30
g_ct = 2

class ActivePool(object):
    mgr = multiprocessing.Manager()
    results = mgr.dict()
    active = mgr.list()
    lock = multiprocessing.Lock()
    @staticmethod
    def getResults():
        with ActivePool.lock:
            return ActivePool.results
            #return copy.deepcopy(ActivePool.results)
    @staticmethod
    def addResult(N, res):
        with ActivePool.lock:
            ActivePool.results[int(N)] = res
    @staticmethod
    def makeActive(name):
        with ActivePool.lock:
            ActivePool.active.append(name)
    @staticmethod
    def makeInactive(name):
        with ActivePool.lock:
            ActivePool.active.remove(name)
    @staticmethod
    def inList(name):
        with ActivePool.lock:
            if name in ActivePool.active:
                return True
            else:
                return False
    def __init__(self):
        super(ActivePool, self).__init__()
        self.pid = os.getpid()
        self.mon_incr = 1000
        self.mon_val = self.mon_incr
    def __str__(self):
        with ActivePool.lock:
            return str(ActivePool.active)
    def monVal(self, val):
        with ActivePool.lock:
            if val > self.mon_val:
                writeFlush("Monitor: mon_val = {0}, value now = {1}".format(self.mon_val, val))
                self.mon_val += self.mon_incr

def printResults():
    writeFlush("Results")
    results = ActivePool.getResults()
    for key in sorted(results.keys()):
        writeFlush(str(key) + '\t' + results[key])

def terminateAll(sig,frame):
    writeFlush("Received SIGINT: terminating all jobs", True)
    sleep_time = 0
    e.set()

class MyProcess(multiprocessing.Process):
    """ process class - handles exiting by signal"""
    def __init__(self, ):
        multiprocessing.Process.__init__(self)
        self.exit = multiprocessing.Event()

    def run(self):
        while not self.exit.is_set():
            time.sleep(1)
        writeFlush("You exited!", True)

    def shutdown(self):
        writeFlush("Shutdown initiated", True)
        self.exit.set()

def main():
    """ the main process - starts off checkTheory()"""

    parser = argparse.ArgumentParser()
    addArgs(parser)

    args = parser.parse_args()

    numthreads = args.threads
    numprimes = args.prime_range

    s = multiprocessing.Semaphore(numthreads)

    '''
    if args.prime_value:
        pool = ActivePool()
        name = "specific prime"
        queue.append(name)
        job = multiprocessing.Process(target=worker, name=name, args=(s, pool, args.prime_value, true))
        job.start()
        job.join()
        return 0
  
    process = MyProcess()
    process.start()
  '''

    print_primes = False

    ct = args.prime_value

    if numthreads > MAX_THREADS:
        writeFlush("Limit # of threads is {}".format(MAX_THREADS), True)
        sys.exit(1)

    checkTheory(s, numprimes, numthreads, ct, print_primes, args)

    #process.shutdown()


if __name__ == '__main__':
    sys.exit(main())
