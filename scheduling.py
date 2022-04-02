from dataclasses import dataclass
import re
from tkinter import N
import numpy as np


class Process:
    """process class to hold proces info"""

    def __init__(self, pid: int,
                 arrival_time: int = 0,
                 burst_time: int = None,
                 priority: int = None,
                 waiting_time: int = 0,
                 turnaround_time: int = 0) -> None:
        self.pid = pid
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.rem_burst_time = burst_time
        self.priority = priority
        self.waiting_time = waiting_time
        self.turnaround_time = turnaround_time

    def __str__(self) -> str:
        return f"P{self.pid}\t{self.arrival_time}\t\t{self.burst_time}\t\
            {self.priority}\t{self.waiting_time}\t\t{self.turnaround_time}"


class SortedQue:
    def __init__(self) -> None:
        self.que = []

    def enque(self, p: Process):
        for i in range(len(self.que)):
            if p.rem_burst_time < self.que[i].rem_burst_time:
                self.que.insert(i, p)
                return
        self.que.append(p)

    def deque(self, p):
        self.que.remove(p)

    def pop(self, idx):
        return self.que.pop(idx)

    def increment_waiting_time(self):
        for p in self.que:
            p.waiting_time += 1

    def __str__(self):
        pids = [str(p.pid) for p in self.que]
        return "[" + " ".join(pids) + "]"


class Scheduler:
    """base class for all schedulers, provides schedule, get_stats and print_stats 
    methods and stores processes and their number"""

    def __init__(self, processes: list[Process]) -> None:
        self.processes = processes
        self.n_processes = len(processes)
        self.que = None  # que of sorted processes according to scheduler algorithm
        self.stats = None  # calculated stats after scheduling, waiting times, turnaround times

    def schedule(self):
        """assumes non-preemtive scheduling"""
        time_elapsed = self.que[0].arrival_time
        for p in self.que:
            p.waiting_time = time_elapsed - p.arrival_time
            time_elapsed += p.burst_time
            p.turnaround_time = time_elapsed - p.arrival_time

    def get_stats(self):
        """return waiting times, and turnaround times for each process"""
        waiting_times = [p.waiting_time for p in self.processes]
        turnaround_times = [p.turnaround_time for p in self.processes]
        return waiting_times, turnaround_times

    def print_stats(self):
        waiting_times, turnaround_times = self.stats
        print("Process\tArrival Time\tBurst Time\tPriority\tWaiting Time\tTurnaround Time")
        for p in self.processes:
            print(p)
        print()
        print(f"Average Waiting Time: {np.mean(waiting_times)}")
        print(f"Average Turnaround Time: {np.mean(turnaround_times)}")


class FCFS(Scheduler):
    """first-come-first-served scheduling"""

    def __init__(self, processes: list[Process], verbose: bool = False) -> None:
        super(FCFS, self).__init__(processes)
        self.que = sorted(processes, key=lambda p: p.arrival_time)
        self.schedule()
        self.stats = self.get_stats()
        if verbose:
            self.print_stats()


class SJF(Scheduler):
    """shortest-job-first scheduling"""

    def __init__(self, processes: list[Process], verbose: bool = False) -> None:
        super(SJF, self).__init__(processes)
        self.que = sorted(processes, key=lambda p: (
            p.arrival_time, p.burst_time))
        self.schedule()
        self.stats = self.get_stats()
        if verbose:
            self.print_stats()


class Priority(Scheduler):
    """priority scheduling"""

    def __init__(self, processes: list[Process], verbose: bool = False) -> None:
        super(Priority, self).__init__(processes)
        self.que = sorted(processes, key=lambda p: (
            p.arrival_time, p.priority))
        self.schedule()
        self.stats = self.get_stats()
        if verbose:
            self.print_stats()


class STCF(Scheduler):
    def __init__(self, processes: list[Process], verbose: bool = False) -> None:
        super().__init__(processes)
        self.que = SortedQue()
        self.schedule()
        self.stats = self.get_stats()
        if verbose:
            self.print_stats()

    def burst(self, p: Process):
        """simulate bursting process p, return true when done"""
        p.rem_burst_time -= 1
        return p.rem_burst_time == 0

    def schedule(self):
        """
        1- enque the earliest process(es)
        2- while que:
            2a- p = pop(0)
            2b- while process not done and no new processes arrived:
                2ba- burst p
                2bb- increment que waiting time
                2bc- increment t
            2c- if done:
                    store p turnaround time
                    update t to new arrival time
                else:
                    return p to que
                enque new arrivals
        """
        arrival_times = sorted(set([p.arrival_time for p in self.processes]))
        while True:
            if arrival_times:
                t = arrival_times.pop(0)
                self.enque_t(t)

            p = self.que.pop(0)
            while True:
                done = self.burst(p)
                self.que.increment_waiting_time()
                t += 1
                if done:
                    p.turnaround_time = t - p.arrival_time
                    if not self.que.que:
                        return
                    break

                if arrival_times and t == arrival_times[0]:
                    self.que.enque(p)
                    break

    def enque_t(self, t):
        """enque the processes which arrive at time t"""
        for p in self.processes:
            if p.arrival_time == t:
                self.que.enque(p)


def main(args):
    assert(len(args.burst_times) == len(args.arrival_times))

    priorities = args.priorities
    if args.priorities == (0,):
        priorities *= len(args.burst_times)

    processes = [Process(pid=i,
                         arrival_time=args.arrival_times[i],
                         burst_time=args.burst_times[i],
                         priority=priorities[i])
                 for i in range(len(args.burst_times))]

    schedulers = [FCFS, SJF, Priority, STCF]
    scheduler = schedulers[args.scheduler]
    scheduler(processes, verbose=True)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--scheduler', type=int,
                        help="0: FCFS, 1: SJF, 2: Priority, 3: STCF")
    parser.add_argument('--burst_times', type=int, nargs="+",
                        help="expected cpu-burst times of each process")
    parser.add_argument('--arrival_times', type=int, nargs="+",
                        help="arrival times of each process")
    parser.add_argument('--priorities', type=int, nargs="+",
                        default=(0,), help="priority of each process")
    args = parser.parse_args()

    main(args)