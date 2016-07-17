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

sys.path.append("/home/wade/Dev/Python/Tools")
sys.path.append("/home/wade/Dev/Python/PerfNum")

import lucaslehmer

import pdbAttach

sys.setrecursionlimit(100000)

today = date.today()
appstart = time.time()
enabled = True
queue = deque()
jobs = {}
main_pid = 0
sleep_time = 0.1
e = multiprocessing.Event()

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
    Clucaslehmer = lucaslehmer.LucasLehmer()
    return Clucaslehmer.sa_lucaslehmer(X);

def doNothing(sig,frame):
    print 'Received SIGINT: letting parent handle it, disabling'
    time.sleep(1)
    process.shutdown()

def worker(s, pool, X):
    signal.signal(signal.SIGINT, doNothing)
    name = multiprocessing.current_process().name

    with s:
        pool.makeActive(name)
        timestart = time.time()
        v = 0
        l = doLucasLehmer(X)
        timestop = time.time()
        time_elapsed = timestop - timestart
        from_start = timestop - appstart
        pstr = '%d: ' % X
        if l:
            timestamp = datetime.datetime(today.year, today.month, today.day).utcnow()
            pstr += 'prime is mersenne -- time: from start: %f -- elapsed: %f' % (from_start, time_elapsed)
            ActivePool.addResult(X, pstr)
            print '\t\t%d ... time: from start %f -- elapsed: %f' % (X, from_start, time_elapsed)

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

def checkTheory(s, numlimit, numproc, ct, print_primes):
    signal.signal(signal.SIGINT, terminateAll)

    pool = ActivePool()

    global g_ct
    if not ct:
        primes = []
        try:
            Clucaslehmer = lucaslehmer.LucasLehmer()
            Clucaslehmer.sa_getListOfPrimes(primes, numlimit)
        except:
            print 'Exception getting primes'
            sys.exit(1)
        if print_primes:
            print primes
        print 'Total number of primes in set: ', len(primes)

        for g_ct in primes:
            name = 'job' + str(g_ct)
            queue.append(name)
            jobs[name] = multiprocessing.Process(target=worker, name=name, args=(s, pool, g_ct))

        start_set = set()
        fin_set = set()

        j_list = jobs.keys()

        for j in j_list:
            if e.is_set():
                print 'Terminated by signal: number of remaining jobs = ', len(queue)
                break

            while len(start_set) < numproc and len(queue):
                p = jobs[queue.popleft()]
                pool.monVal(int(p.name[3:]))
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
    else:
        name = 'job' + str(ct)
        queue.append(name)
        worker(s, pool, ct)
        printResults()

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
                print 'Monitor: mon_val = %d, value now = %d' % (self.mon_val, val)
                self.mon_val += self.mon_incr

def printResults():
    print 'Results:'
    results = ActivePool.getResults()
    for key in sorted(results.keys()):
        print str(key) + '\t' + results[key]

def terminateAll(sig,frame):
    print 'Received SIGINT: terminating all jobs'
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
        print 'You exited!'

    def shutdown(self):
        print 'Shutdown initiated'
        self.exit.set()

def addArgs(p):
    p.add_argument("-t", "--threads", type=int, required=False, default=10,
                   help="Number of threads")
    p.add_argument("-r", "--prime_range", type=int, required=False, default=20001,
                   help="Range of primes to search starting with 1 to this number")
    
def main():
    """ the main process - starts off checkTheory()"""

    parser = argparse.ArgumentParser()
    addArgs(parser)

    args = parser.parse_args()

    process = MyProcess()
    process.start()

    numthreads = args.threads
    numprimes = args.prime_range

    print_primes = False

    ct = 0

    if numthreads > MAX_THREADS:
        print 'Limit # of threads is %d' % MAX_THREADS
        sys.exit(1)

    s = multiprocessing.Semaphore(numthreads)

    pdbAttach.listen()

    checkTheory(s, numprimes, numthreads, ct, print_primes)
    #printResults()

    process.shutdown()


if __name__ == '__main__':
    sys.exit(main())
