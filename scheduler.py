

READY = 0
RUNNING = 1
FINISHED = 2


class Process:
    def __init__(self, pid, ta, tb, p) -> None:
        self.pid = pid  # process id
        self.ta = ta  # arrival time
        self.tb = tb  # burst time
        self.p = p  # priority

        self.taub = tb  # remaining burst time
        self.tw = 0  # wait time
        self.tta = 0  # turnaround time
        self.status = READY

    def step(self):
        """increment times according to whether process is running, waiting, or finished"""
        self.tta += 1
        if self.status == RUNNING:
            self.taub -= 1
        elif self.status == READY:
            self.tw += 1
        return self.taub == 0

    def __str__(self):
        row = [self.pid, self.ta, self.tb, self.p,
               self.tw, self.tta, self.taub, self.status]
        row = [str(stat) for stat in row]
        return "\t".join(row)

    def __repr__(self):
        return f"{self.pid}"


class Que:
    """base class for scheduler que"""

    def __init__(self, rt: list[Process]) -> None:
        self.rt = sorted(rt, key=lambda x: x.ta)  # requests sorted by AT

        self.que = []
        self.idx = 0  # index into curernt serviced process
        self.t = 0

    def enque(self, r: Process):
        """enque a process request"""
        pass

    def enque_t(self):
        """enque the requests that arrive at time t"""
        try:
            while self.rt[0].ta <= self.t:
                r = self.rt.pop(0)
                self.enque(r)

        except IndexError:
            # request buffer is empty
            return

    def step(self):
        """step each process in que; if all are done return True;
        if current one is done increment que index
        enque requests_t if it's their time"""

        self.enque_t()  # requests arrive at t (if any) can only start at t+1

        done = True
        inc = False
        for i, p in enumerate(self.que):
            if p.status == FINISHED:
                # don't step finished processes
                continue

            if i == self.idx:
                p.status = RUNNING

            done_p = p.step()
            if done_p:
                p.status = FINISHED
                inc = True
            else:
                done = False

        if inc:
            self.idx += 1
        self.t += 1
        return done

    def print_stats(self):
        print(self)
        col_names = "\t".join(
            ["PID", "AT", "BT", "P", "WT", "TAT", "RBT", "STA"])
        print(col_names)
        for p in self.que:
            print(p)

    def __str__(self) -> str:
        return "[" + " ".join([str(p.pid) for p in self.que]) + "]"


class FCFS(Que):
    def __init__(self, rt) -> None:
        super(FCFS, self).__init__(rt)

    def enque(self, p: Process):
        self.que.append(p)

    def __str__(self) -> str:
        return "FCFS"


class SJF(Que):
    def __init__(self, rt) -> None:
        super(SJF, self).__init__(rt)

    def enque(self, r: Process):
        search_range = len(self.que) - self.idx
        for i in range(search_range):
            p = self.que[self.idx + i]
            if p.status == RUNNING:
                continue
            if r.tb < p.tb:
                self.que.insert(self.idx + i, r)
                return

        # if r is longer than all processes, or que is empty or all
        # processes are finished
        self.que.append(r)

    def __str__(self) -> str:
        return "SJF"


class STCF(Que):
    def __init__(self, rt) -> None:
        super(STCF, self).__init__(rt)

    def enque(self, r: Process):
        search_range = len(self.que) - self.idx
        for i in range(search_range):
            p = self.que[self.idx + i]
            if r.tb < p.tb:
                # print(f"P{r.pid} is taking the place of P{p.pid}")
                if p.status == RUNNING:
                    p.status = READY
                    # print(f"P{p.pid} changed from RUNNING to READY:")
                    # print(p.pid, p.status)
                self.que.insert(self.idx + i, r)
                return

        # if r is longer than all processes, or que is empty or all
        # processes are finished
        self.que.append(r)

    def __str__(self) -> str:
        return "STCF"


class Priority(Que):
    def __init__(self, rt: list[Process]) -> None:
        super(Priority, self).__init__(rt)

    def enque(self, r: Process):
        search_range = len(self.que) - self.idx
        for i in range(search_range):
            p = self.que[self.idx + i]
            if p.status == RUNNING:
                continue
            if r.p < p.p:
                self.que.insert(self.idx + i, r)
                return

        # if r is longer than all processes, or que is empty or all
        # processes are finished
        self.que.append(r)

    def __str__(self) -> str:
        return "PRIORITY"


class RoundRobin(FCFS):
    def __init__(self, rt: list[Process], quantum=1) -> None:
        super(RoundRobin, self).__init__(rt)
        self.quantum = quantum
        self.idx = -1

    def update_idx(self):
        """make sure the index is pointing to a ready process"""
        for _ in range(len(self.que)):
            if self.que[self.idx].status == READY:
                return True
            self.idx = (self.idx + 1) % len(self.que)
        return False

    def step(self):
        """step each process in que; if all are done return True;
        if current one is done increment que index
        enque requests_t if it's their time"""

        self.enque_t()  # requests arrive at t (if any) can only start at t+1
        self.idx = (self.idx + 1) % len(self.que)
        if not self.update_idx():
            return True

        done = True
        for i, p in enumerate(self.que):
            if p.status == FINISHED:
                # don't step finished processes
                continue

            if i == self.idx:
                p.status = RUNNING

            for burst_time in range(self.quantum):
                done_p = p.step()
                if done_p:
                    p.status = FINISHED
                    break
                else:
                    done = False
                    p.status = READY

        self.t += burst_time + 1
        return done

        return

    def __str__(self) -> str:
        return "ROUND ROBIN"


def main(args):
    assert(len(args.burst_times) == len(args.arrival_times))

    priorities = args.priorities
    if args.priorities == (0,):
        priorities *= len(args.burst_times)

    processes = [Process(pid=i,
                         ta=args.arrival_times[i],
                         tb=args.burst_times[i],
                         p=priorities[i])
                 for i in range(len(args.burst_times))]

    schedulers = [FCFS, SJF, Priority, STCF, RoundRobin]
    scheduler_class = schedulers[args.scheduler]
    scheduler = scheduler_class(processes)
    while True:
        done = scheduler.step()
        if done:
            break
    scheduler.print_stats()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--scheduler', type=int,
                        help="0: FCFS, 1: SJF, 2: Priority, 3: STCF, 4: Round Robin")
    parser.add_argument('--burst_times', type=int, nargs="+",
                        help="expected cpu-burst times of each process")
    parser.add_argument('--arrival_times', type=int, nargs="+",
                        help="arrival times of each process")
    parser.add_argument('--priorities', type=int, nargs="+",
                        default=(0,), help="priority of each process")
    args = parser.parse_args()

    main(args)
