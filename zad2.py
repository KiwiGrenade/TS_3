import random
import os
from time import sleep
from copy import deepcopy
from functools import reduce


class Antenna:
    def __init__(self, name, pos, start, to_send):
        self.name = str(name)
        self.position = pos
        self.suspend = False
        self.collision_count = 0
        self.broadcasting = False
        self.frames_to_wait = start
        self.packages_to_send = to_send

        # Stats
        self.total_collisions = 0
        self.total_waiting_time = 0

    def state(self) -> str:
        if self.broadcasting:
            if self.suspend:
                return "Collided"
            else:
                return "Active"
        else:
            if self.packages_to_send == 0:
                return "Idle"
            else:
                return "Waiting"

    def wait_random_t(self):
        self.collision_count += 1
        self.frames_to_wait = random.randrange(0, 2 ** min((self.collision_count, 10)))
        self.total_waiting_time += self.frames_to_wait


class Signal:
    def __init__(self, antenna, direction):
        self.antenna = antenna
        self.direction = direction
        self.is_jam = antenna.suspend

    def __repr__(self):
        if self.is_jam:
            return self.antenna.name[0] + "*"
        return self.antenna.name[0]

    def __str__(self):
        return repr(self)


class Env:
    def __init__(self, size):
        self.antenna_list = {i: None for i in range(size)}
        self.active_antenna_list = []
        self.cable = [[] for _ in range(size)]
        self.empty_cable = deepcopy(self.cable)
        self.size = size

        self.names = ["" for _ in range(self.size)]
        self.width = 10

    def add_antenna(self, name, position, start=0, frames_to_send=0):
        antenna = Antenna(name, position, start, frames_to_send)
        # create an antenna if the position it's supposed to be is within a cable
        if position in self.antenna_list:
            self.antenna_list[position] = antenna
            self.names[position] = name
            if frames_to_send > 0:
                self.active_antenna_list.append(antenna)

    def next_frame(self):
        # Propagate signals present in the cable
        next_cable = deepcopy(self.empty_cable)
        # i - direction of signal
        for i, segment in enumerate(self.cable):
            for signal in segment:
                # broadcast to left
                if signal.direction == -1:
                    if i > 0:
                        next_cable[i - 1].append(signal)
                # broadcast to right
                elif signal.direction == 1:
                    if i < self.size - 1:
                        next_cable[i + 1].append(signal)
                # broadcast to left and right
                else:
                    if i > 0:
                        next_cable[i - 1].append(Signal(signal.antenna, -1))
                    if i < self.size - 1:
                        next_cable[i + 1].append(Signal(signal.antenna, 1))

        self.cable = next_cable

        # Antenna behaviour
        for antenna in self.active_antenna_list:
            if antenna.broadcasting:
                # End broadcasting
                if antenna.frames_to_wait == 0:
                    antenna.broadcasting = False
                    # collision detected - wait random time
                    if antenna.suspend:
                        antenna.suspend = False
                        antenna.wait_random_t()
                    # package was sent successfully
                    else:
                        antenna.packages_to_send -= 1
                        antenna.total_collisions += antenna.collision_count
                        antenna.collision_count = 0
                        # all packages were sent - stop sending
                        if antenna.packages_to_send == 0:
                            self.active_antenna_list.remove(antenna)

                # Proceed to broadcast
                else:
                    # Collision detected
                    if not antenna.suspend and len(self.cable[antenna.position]) > 0:
                        antenna.suspend = True
                        antenna.frames_to_wait = 2 * self.size - 2
                    self.cable[antenna.position].append(Signal(antenna, 0))
                    antenna.frames_to_wait -= 1
            # not broadcasting
            else:
                # waiting
                if antenna.frames_to_wait > 0:
                    antenna.frames_to_wait -= 1
                else:
                    # receiving signal
                    if self.cable[antenna.position]:
                        antenna.total_waiting_time += 1
                    # sending signal
                    else:
                        self.cable[antenna.position].append(Signal(antenna, 0))
                        antenna.broadcasting = True
                        # how long to send signal
                        antenna.frames_to_wait = random.randrange(0, self.size * 2)

    # UI methods
    def show_nodes(self):
        times = ["" for _ in range(self.size)]
        flags = ["" for _ in range(self.size)]
        for antenna in self.antenna_list.values():
            if antenna:
                p = antenna.position
                times[p] = antenna.frames_to_wait
                flags[p] = antenna.state()

        w = self.width
        print(("+" + "-" * 6) + ("+" + "-" * w) * self.size + "+")
        print(
            "|{:^6}|".format("Name")
            + reduce(lambda a, b: "{:^{w}}|{:^{w}}".format(a, b, w=w), self.names)
            + "|"
        )
        print(("+" + "=" * 6) + ("+" + "=" * w) * self.size + "+")

    def print_frame(self, frame):
        w = self.width
        signals = [" ".join(sorted(str(s) for s in frag)) for frag in self.cable]
        print(
            "{}".format("t={}".format(frame))
            + reduce(lambda a, b: "{:^{w}}|{:^{w}}".format(a, b, w=w), signals)
            + "|"
        )
        print(("-" * 7) + ("-" * (w + 1)) * self.size)

    def run(self):
        self.width = max((4 * (len(self.active_antenna_list)) - 2, 10))
        self.show_nodes()
        i = -1
        while self.active_antenna_list or self.cable != self.empty_cable:
            i += 1
            self.next_frame()
            self.print_frame(i)
        print("\n{} iterations total. antenna statistics:\n".format(i))
        for antenna in self.antenna_list.values():
            if antenna:
                print(antenna.name)
                print("collisions: {}".format(antenna.total_collisions))
                print("total waiting time: {}\n".format(antenna.total_waiting_time))


if __name__ == "__main__":
    sim = Env(13)
    sim.add_antenna("A", 0, 0, 4)
    sim.add_antenna("B", 8, 0, 5)
    sim.add_antenna("C", 12, 3, 2)
    sim.run()
