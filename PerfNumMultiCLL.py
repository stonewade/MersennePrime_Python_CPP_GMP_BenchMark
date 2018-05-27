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

from collections import OrderedDict

from pybindgen import *

import lucaslehmer

sys.setrecursionlimit(100000)

DEFAULT_PRIME_RANGE = [2, 10001]

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
    mutex.add_argument("-n", "--return_num_primes_in_range", required=False, nargs=2, default=DEFAULT_PRIME_RANGE,
                   help="Return the number of standard primes over the given range")
    
today = date.today()
appstart = time.time()
enabled = True
jobs = OrderedDict()
main_pid = 0
sleep_time = 0.1
e = multiprocessing.Event()
spacer = " " * 5
box_top_bottom = '-' * (4 + 6 * len(spacer) + 3 *20)
MAX_THREADS = 30
g_ct = 2
pool = None
l_pids = list()

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

def runShellCommand(cmd_, dry_run_=False, shell_=True):
    s_output = ""
    if dry_run_:
        writeFlush("Dry run - would run:\n\n\t" + cmd_ + '\n')
        return s_output
    try:
        pid = subprocess.Popen(cmd_, stdout=subprocess.PIPE, shell=shell_)
        s_output, s_err = pid.communicate()
        if not s_output and not s_err:
            return ""
    except:
        writeFlush("Exception during call: " + cmd_, True, "")
        return ""
    finally:
        pass
    if s_err:
        writeFlush("Error during call: " + cmd_ + ": " + s_err, True, "")
    s_out = "" 
    t = type(s_output) if s_output else int
    if t != str:
        if str(t).find("bytes") > -1:
             s_out = s_output.decode( "unicode-escape" ).replace("\r\n", "\n")
    elif str(t).find("str"):
        s_out = s_output.decode( "ascii" ).replace("\r\n", "\n")
    return s_out

def doLucasLehmer(X, Clucaslehmer_, S_):
    if not (X % 2):
        return False
    return Clucaslehmer_.sa_lucaslehmer(X, S_);

def worker(X_, args_, slot_, force_print_=False):
    global enabled
    global pool
    global s
    global l_pids
    l_pids.append(os.getpid())
    name = multiprocessing.current_process().name
    if not enabled:
        return
    with s:
        pool.makeActive(name)
        timestart = time.time()
        l = doLucasLehmer(X_, pool.LLI[slot_], pool.l_s[slot_])
        if l or not args_.prime_range:
            timestop = time.time()
            time_elapsed = timestop - timestart
            from_start = timestop - appstart
            print_str = "\t\t"
            print_str += "|" + spacer + "{0:20d}".format(X_) + spacer
            if l or force_print_:
                print_str += "|" + spacer + "{0:20.6f}".format(from_start) + spacer
                print_str += "|" + spacer + "{0:20.6f}".format(time_elapsed) + spacer
            else:
                print_str += "|" + spacer + "{0:20s}".format("    Not Mersenne    ") + spacer
                print_str += "|" + spacer + "{0:20s}".format(' ' * 20) + spacer
            print_str += "|"
            print_str += "\n\t\t" + box_top_bottom
            writeFlush(print_str)
        pool.makeInactive(name)

def checkTheory(numlimit, ct, print_primes, args):
    global s
    s = multiprocessing.Semaphore(args.threads)
    global pool
    pool = ActivePool(args.threads)
    global g_ct
    if not ct:
        if not len(args.prime_list):
            primes = []
            try:
                Clucaslehmer = lucaslehmer.LucasLehmer()
                range_low, range_high = args.return_num_primes_in_range[0], args.return_num_primes_in_range[1]
                print("{0}:{1}".format(range_low, range_high))
                Clucaslehmer.sa_getListOfPrimes(primes, range_low, range_high)
            except:
                writeFlush("Exception getting primes", True)
                sys.exit(1)
            if print_primes:
                writeFlush(str(primes))
        else:
           primes = [int(a) for a in args.prime_list]
        writeFlush("\nTotal number of " + ("primes" if not len(args.prime_list) else "values to test") + " in set: {0}\n".format(len(primes)))
        if args.return_num_primes_in_range != DEFAULT_PRIME_RANGE:
            sys.exit(0)
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
    for i, g_ct in enumerate(primes):
        name = i
        slot = i % args.threads
        if slot not in pool.LLI.keys():
            pool.LLI[slot] = lucaslehmer.LucasLehmer()
            pool.l_s[slot] = 4
        jobs[name] = multiprocessing.Process(target=worker, name=name, args=(g_ct, args, slot))
    j_list = jobs.keys()
    for j in j_list:
        jobs[j].start()
        time.sleep(0.001)
    for j in j_list:
        if jobs[j]:
            jobs[j].join()

class ActivePool(object):
    def __init__(self, num_procs_):
        super(ActivePool, self).__init__()
        self.pid = os.getpid()
        self.mon_incr = 1000
        self.mon_val = self.mon_incr
        self.mgr = multiprocessing.Manager()
        self.results = self.mgr.dict()
        self.active = self.mgr.list()
        self.lock = multiprocessing.Lock()
        self.l_s = self.mgr.dict()
        self.LLI = self.mgr.dict()
    def getResults(self):
        with self.lock:
            return self.results
    def addResult(self, N, res):
        with self.lock:
            self.results[int(N)] = res
    def makeActive(self, name):
        with self.lock:
            self.active.append(name)
    def makeInactive(self, name):
        with self.lock:
            self.active.remove(name)
    def inList(self, name):
        with self.lock:
            if name in self.active:
                return True
            else:
                return False
    def __str__(self):
        with self.lock:
            return str(self.active)
    def monVal(self, val):
        with self.lock:
            if val > self.mon_val:
                writeFlush("Monitor: mon_val = {0}, value now = {1}".format(self.mon_val, val))
                self.mon_val += self.mon_incr

def signalHandler(signal_, frame_):
    e.set()
    global enabled
    global pool
    global l_pids
    global jobs
    enabled = False
    for j in jobs.keys():
        if jobs[j]:
            jobs[j].terminate()
            jobs[j].join()
        if j == jobs.keys()[-1]:
            writeFlush("Killed by ctrl-C\n")
    time.sleep(0.5)
    for pid in l_pids:
        cmd = r"kill 2>/dev/null" + str(pid)
        runShellCommand(cmd)
    sys.exit(1)

def main():
    """ the main process - starts off checkTheory()"""
    signal.signal(signal.SIGINT, signalHandler)

    parser = argparse.ArgumentParser()
    addArgs(parser)

    args = parser.parse_args()

    numprimes = args.prime_range

    print_primes = False

    ct = args.prime_value

    if args.threads > MAX_THREADS:
        writeFlush("Limit # of threads is {}".format(MAX_THREADS), True)
        sys.exit(1)

    checkTheory(numprimes, ct, print_primes, args)

if __name__ == '__main__':
    sys.exit(main())
