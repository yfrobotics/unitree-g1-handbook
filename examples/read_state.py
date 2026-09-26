"""Read G1 LowState only. No command publisher or mode switch is created."""
import argparse
import math
import threading
import time


class Freshness:
    """Track arrival and advancing device ticks separately, using monotonic time."""
    def __init__(self, now):
        self.arrival = self.progress = now
        self.tick = None

    def update(self, tick, now):
        self.arrival = now
        if tick != self.tick:
            self.progress, self.tick = now, tick

    def status(self, now, timeout, check_tick=True):
        if self.tick is None:
            return "WAITING"
        if now - self.arrival > timeout:
            return "NO_MESSAGES"
        if check_tick and now - self.progress > timeout:
            return "FROZEN_TICK"
        return "OK"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--interface", required=True)
    parser.add_argument("--domain", required=True, type=int)
    parser.add_argument("--joint", type=int, default=0, help="Raw DDS slot, not model index")
    parser.add_argument("--seconds", type=float, default=10)
    parser.add_argument("--timeout", type=float, default=1)
    parser.add_argument("--freshness", choices=["tick", "arrival"], default="tick")
    args = parser.parse_args()
    if not 0 <= args.domain <= 232 or not 0 <= args.joint < 35:
        parser.error("domain must be 0..232 and joint must be 0..34")
    if not all(math.isfinite(v) and v > 0 for v in (args.seconds, args.timeout)):
        parser.error("seconds and timeout must be finite and positive")
    from unitree_sdk2py.core.channel import ChannelFactoryInitialize, ChannelSubscriber
    from unitree_sdk2py.idl.unitree_hg.msg.dds_ import LowState_

    lock = threading.Lock()
    start = time.monotonic()
    health = Freshness(start)
    latest, count = None, 0

    def receive(msg):
        nonlocal latest, count
        with lock:
            health.update(msg.tick, time.monotonic())
            latest, count = msg, count + 1

    ChannelFactoryInitialize(args.domain, args.interface)
    subscriber = ChannelSubscriber("rt/lowstate", LowState_)
    subscriber.Init(receive, 1)
    failed = False
    try:
        while time.monotonic() - start < args.seconds:
            time.sleep(0.25)
            with lock:
                now = time.monotonic()
                status = health.status(now, args.timeout, args.freshness == "tick")
                if status == "WAITING" and now - start > args.timeout:
                    status = "NO_MESSAGES"
                values = ""
                if latest is not None:
                    motor = latest.motor_state[args.joint]
                    quat = list(latest.imu_state.quaternion)
                    if not all(math.isfinite(v) for v in [motor.q, motor.dq, *quat]):
                        status = "NONFINITE"
                    values = f" tick={latest.tick} q={motor.q:.5f} dq={motor.dq:.5f} quat_wxyz={quat}"
                print(f"{status} received={count}{values}", flush=True)
                failed |= status not in ("OK", "WAITING")
    except KeyboardInterrupt:
        pass
    finally:
        subscriber.Close()
    return 2 if failed or count == 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
