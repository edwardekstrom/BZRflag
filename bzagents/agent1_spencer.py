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

from bzrc import BZRC, Command
from pFields import PField

class Agent(object):
    """Class handles all command and control logic for a teams tanks."""

    def __init__(self, bzrc):
        self.bzrc = bzrc
        self.constants = self.bzrc.get_constants()
        self.commands = []
        self.potentialFields = []
        


    def tick(self, time_diff):
        """Some time has passed; decide what to do next."""
        mytanks, othertanks, flags, shots = self.bzrc.get_lots_o_stuff()
        self.mytanks = mytanks
        self.othertanks = othertanks
        self.flags = flags
        self.shots = shots
        self.enemies = [tank for tank in othertanks if tank.color !=
                        self.constants['team']]

        self.commands = []

        # for every flag create a potential field and add it to a list
        #for flg in flags:
            #if flg.color != self.constants['team']:
                #pf = PField(flg.x, flg.y, 0, 50, 'attract')
                #self.potentialFields.append(pf)



        obstacles = self.bzrc.get_obstacles()
        for o in obstacles:
            #pfo = PField(o.x, o.y, 0, 75, 'repel')
            #self.potentialFields.append(pfo)
            #print o
            pass

        pfo = PField(0, 0, 0, 75, 'repel')
        #self.potentialFields.append(pfo)

        for tank in mytanks:
            best_flag = self.choose_best_flag(tank)
            if ((best_flag.x == tank.x) and (best_flag.y == tank.y)):
                for f in self.flags:
                    if f.color == self.constants['team']:
                        print 'I have the' + f.color + ' flag.'
                        best_flag = f
            pf = PField(best_flag.x, best_flag.y, 0, 50, 'attract')
            self.potentialFields.append(pf)
            self.pf_move(tank)

        #for tank in mytanks:
            #self.attack_enemies(tank)

        #for tank in mytanks:
            #self.run_to_flag(tank)

        results = self.bzrc.do_commands(self.commands)

    def pf_move(self, tank):
        final_angle = 0
        final_speed = 0

        for pf in self.potentialFields:
            speed, angle = pf.calc_vector(tank.x, tank.y)
            angle = self.normalize_angle(angle - tank.angle)

            if final_angle == 0:
                final_angle = angle
            else:
                final_angle = (float(final_angle) + float(angle)) / 2.0

            if final_speed == 0:
                final_speed = speed / 2.0
            else:
                final_speed = (float(final_speed) + float(speed))
        # final_angle = final_angle/float(len(self.potentialFields))

        #print "%f\t%f" % (final_angle, final_speed)

        command = Command(tank.index, final_speed, 2 * final_angle, True)
        self.commands.append(command)
        

    def choose_best_flag(self, tank):
        best_flag = None
        best_flag_dist = 2 * float(self.constants['worldsize'])
        for f in self.flags:
            # print str(len(self.flags))
            if f.color != self.constants['team']:
                dist = math.sqrt((f.x - tank.x)**2 + (f.y - tank.y)**2)
                if dist < best_flag_dist:
                    best_flag_dist = dist
                    best_flag = f
        if best_flag is None:
            return self.flags[0]
        else:
            return best_flag


    def run_to_flag(self, tank):
        best_flag = None
        best_flag_dist = 2 * float(self.constants['worldsize'])
        for f in self.flags:
            if f.color != self.constants['team']:
                dist = math.sqrt((f.x - tank.x)**2 + (f.y - tank.y)**2)
                if dist < best_flag_dist:
                    best_flag_dist = dist
                    best_flag = f
        if best_flag is None:
            command = Command(tank.index, 0, 0, False)
            self.commands.append(command)
        else:
            self.move_to_position(tank, best_flag.x, best_flag.y)

    def attack_enemies(self, tank):
        """Find the closest enemy and chase it, shooting as you go."""
        best_enemy = None
        best_dist = 2 * float(self.constants['worldsize'])
        for enemy in self.enemies:
            if enemy.status != 'alive':
                continue
            dist = math.sqrt((enemy.x - tank.x)**2 + (enemy.y - tank.y)**2)
            if dist < best_dist:
                best_dist = dist
                best_enemy = enemy
        if best_enemy is None:
            command = Command(tank.index, 0, 0, False)
            self.commands.append(command)
        else:
            self.move_to_position(tank, best_enemy.x, best_enemy.y)

    def move_to_position(self, tank, target_x, target_y):
        """Set command to move to given coordinates."""
        target_angle = math.atan2(target_y - tank.y,
                                  target_x - tank.x)
        relative_angle = self.normalize_angle(target_angle - tank.angle)
        # index, speed, angvel, shoot
        command = Command(tank.index, 1, 2 * relative_angle, False)
        self.commands.append(command)

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
