#!/usr/bin/python -tt

# An incredibly simple agent.  All we do is find the closest enemy tank, drive
# towards it, and shoot.  Note that if friendly fire is allowed, you will very
# often kill your own tanks with this code.

#################################################################
# NOTE TO STUDENTS
# This is a starting point for you.  You will need to greatly
# modify this code if you want to do anything useful.  But this
# should help you to know how to interact with BZRC in order to
# get the information you need.
#
# After starting the bzrflag server, this is one way to start
# this code:
# python agent0.py [hostname] [port]
#
# Often this translates to something like the following (with the
# port name being printed out by the bzrflag server):
# python agent0.py localhost 49857
#################################################################

import sys
import math
import time
import random

from bzrc import BZRC, Command

class Agent(object):
    """Class handles all command and control logic for a teams tanks."""

    def __init__(self, bzrc):
        self.bzrc = bzrc
        self.constants = self.bzrc.get_constants()
        self.commands = []
        self.stuck_ticks = 0
        self.prev_x = 0.0
        self.prev_y = 0.0

        # tuning parameters
        self.goal = self.select_new_goal()
        self.goal_sphere = 20
        self.shot_sphere = 100
        self.stuck_tolerance = 30

    def tick(self, time_diff):
        """Some time has passed; decide what to do next."""
        mytanks, othertanks, flags, shots = self.bzrc.get_lots_o_stuff()
        self.mytanks = mytanks
        self.othertanks = othertanks
        self.shots = shots

        self.commands = []

        for tank in mytanks:
            speed = 1.0
            angle_mod = 0.0

            # if(tank.status == 'dead'):
            #     print "dead"

            # find new goal if stuck
            if(tank.status != 'dead' and self.prev_x == tank.x and self.prev_y == tank.y):
                self.stuck_ticks += 1
                # print "stuck %d" % self.stuck_ticks
                if(self.stuck_ticks > self.stuck_tolerance):
                    self.stuck_ticks = 0
                    self.goal = self.select_new_goal()
            else:
                self.stuck_ticks = 0

            self.prev_x = tank.x
            self.prev_y = tank.y

            # when a goal is reached request a new goal
            if(self.dist(tank.x, tank.y, self.goal[0], self.goal[1]) <= self.goal_sphere):
                self.goal[2] = True


            if(self.goal[2] == False):
                if(len(self.shots) > 0):
                    shot_dist = self.dist(tank.x, tank.y, shots[0].x, shots[0].y)
                    if(shot_dist <= self.shot_sphere):
                        angle_mod = float(random.randint(-90,90)) * ((2 * math.pi) / 180.0)
                        #speed = float(random.randint(0,1))
                self.move_to_position(tank, self.goal[0], self.goal[1], angle_mod, speed)
            else:
                self.goal = self.select_new_goal()

        results = self.bzrc.do_commands(self.commands)

    def move_to_position(self, tank, target_x, target_y, angle_mod, speed):
        """Set command to move to given coordinates."""
        target_angle = math.atan2(target_y - tank.y,
                                  target_x - tank.x)
        relative_angle = self.normalize_angle(target_angle - tank.angle)
        command = Command(tank.index, speed, 2 * relative_angle + angle_mod, False)
        self.commands.append(command)

    def select_new_goal(self):
        goal = [float(random.randint(-200, 200)), float(random.randint(-200, 200)), False]
        # print goal
        return goal

    def dist(self, x1, y1, x2, y2):
        dist_result = math.sqrt((float(x1) - float(x2))**2 + (float(y1) - float(y2))**2)
        return dist_result

    def normalize_angle(self, angle):
        """Make any angle be between +/- pi."""
        angle -= 2 * math.pi * int (angle / (2 * math.pi))
        if angle <= -math.pi:
            angle += 2 * math.pi
        elif angle > math.pi:
            angle -= 2 * math.pi
        return angle


def main():
    # Process CLI arguments.
    try:
        execname, host, port = sys.argv
    except ValueError:
        execname = sys.argv[0]
        print >>sys.stderr, '%s: incorrect number of arguments' % execname
        print >>sys.stderr, 'usage: %s hostname port' % sys.argv[0]
        sys.exit(-1)

    # Connect.
    #bzrc = BZRC(host, int(port), debug=True)
    bzrc = BZRC(host, int(port))

    agent = Agent(bzrc)

    prev_time = time.time()

    # Run the agent
    try:
        while True:
            time_diff = time.time() - prev_time
            agent.tick(time_diff)
    except KeyboardInterrupt:
        print "Exiting due to keyboard interrupt."
        bzrc.close()


if __name__ == '__main__':
    main()

# vim: et sw=4 sts=4
