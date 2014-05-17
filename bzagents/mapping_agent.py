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
from pFields import PField

class Agent(object):
    """Class handles all command and control logic for a teams tanks."""

    def __init__(self, bzrc):
        self.bzrc = bzrc
        self.constants = self.bzrc.get_constants()
        self.commands = []
        self.potentialFields = []
        self.flag_sphere = 400
        self.obstacle_sphere = 1000
        self.enemy_sphere = 100
        self.explore_sphere = 50

        self.prev_x = 0
        self.prev_y = 0
        self.stuck_ticks = 0

        self.path_fields = []
        # pf1 = PField(-350, 350, 0, self.flag_sphere, 'attract')
        # pf2 = PField(-350, -350, 0, self.flag_sphere, 'attract')
        # pf3 = PField(350, -350, 0, self.flag_sphere, 'attract')
        # pf4 = PField(350, 350, 0, self.flag_sphere, 'attract')
        # self.path_fields.append(pf1)
        # self.path_fields.append(pf2)
        # self.path_fields.append(pf3)
        # self.path_fields.append(pf4)
        
        self.row_step = 50
        self.col_step = 100
        start_x = -350
        start_y = 350
        end_x = 350
        end_y = -350
        odd = False
        for row in self.my_range(-start_y, -end_y, self.row_step):
            # print ""
            for col in self.my_range(start_x, end_x, self.col_step):
                r = -row
                c = col
                if odd:
                    c *= -1
                #print "%f, %f" % (r, c)
                newpf = PField(c, r, 0, self.explore_sphere, 'attract')
                self.path_fields.append(newpf)
            odd = not odd

        # odd = False
        # for row in self.my_range(-350, 350, 50):
        #     # print ""
        #     for col in self.my_range(-350, 350, 100):
        #         r = -row
        #         c = col
        #         if odd:
        #             c *= -1
        #         #print "%f, %f" % (r, c)
        #         newpf = PField(c, r, 0, self.flag_sphere, 'attract')
        #         self.path_fields.append(newpf)
        #     odd = not odd


        self.cur_path = self.path_fields.pop(0)

    def my_range(self, start, end, step):
        while start <= end:
            yield start
            start += step


    def tick(self, time_diff):
        """Some time has passed; decide what to do next."""
        # don't need to know where the flags or shots are when exploring.  Enemies are included in the 'othertanks' call

        self.bzrc.sendline('mytanks')
        self.bzrc.sendline('othertanks')
        self.bzrc.read_ack()
        self.mytanks = self.bzrc.read_mytanks()
        self.bzrc.read_ack()
        self.othertanks = self.bzrc.read_othertanks()

        self.commands = []
        
        # in the rare case that a tank runs into its own bullet, don't do anything while it is dead
        exp_tank = self.mytanks[0]
        if(exp_tank.status == 'dead'):
            return

        # if the tank has no change in position, it is stuck. Try turning and shooting whatever it is is next to (usually a tank)
        travel_d = self.dist(exp_tank.x, exp_tank.y, self.prev_x, self.prev_y)
        pfe = None
        if travel_d == 0.0:
            self.stuck_ticks += 1
            print "I'm stuck %d" % self.stuck_ticks
            enemy_x, enemy_y, enemy_dist = self.closest_tank(exp_tank)
            # a temp sphere of 10 for enemies prevents the explorer tank from tracking down tanks that aren't next to it
            tempPFEsphere = 10
            if enemy_dist < tempPFEsphere:
                pfe = PField(enemy_x, enemy_y, 0, tempPFEsphere, 'attract')
        else:
            self.stuck_ticks = 0

        # move the tank to the next pField (explore spot or shoot tank)
        self.pf_move(exp_tank, self.cur_path, pfe)
        tolerance = 20
        if(abs(exp_tank.x - self.cur_path.x) <= tolerance and abs(exp_tank.y - self.cur_path.y) <= tolerance):
            print "nailed it!"
            if self.path_fields:
                self.cur_path = self.path_fields.pop(0)

        
        # if the tank is stuck longer than the really stuck tollerance, shift the pField down or up depending on the quadrant
        really_stuck_tolerance = 40
        if self.stuck_ticks >= really_stuck_tolerance:
            print "I'm REALLY stuck"
            direction = 1
            if(exp_tank.y <= 0):
                direction = -1

            self.cur_path = PField(self.cur_path.x, self.cur_path.y + (self.row_step * direction), 0, self.explore_sphere, 'attract')
            print "%f, %f" % (self.cur_path.x, self.cur_path.y)
            self.stuck_ticks = 0


        self.prev_x = exp_tank.x
        self.prev_y = exp_tank.y
        results = self.bzrc.do_commands(self.commands)

    def flip_a_coin(self):
        res = random.randint(0,1)
        if(res):
            return res
        else:
            return -1

    def pf_move(self, tank, pf, pfe):
        final_angle = 0

        if pfe != None:
            #print self.constants['team'] + " tank: %d = pfe" % tank.index
            speedmod, angle = pfe.calc_vector(tank.x, tank.y)
        elif pf != None:
            #print self.constants['team'] + " tank: %d = pf" % tank.index
            speedmod, angle = pf.calc_vector(tank.x, tank.y)
        else:
            speedmod = -0.5
            angle = (math.pi / 2.0)
        

        angle = self.normalize_angle(angle - tank.angle)

        if final_angle == 0:
            final_angle = angle
        else:
            final_angle = (float(final_angle) + float(angle)) / 2.0

        command = Command(tank.index, speedmod, 2 * final_angle, True)
        self.commands.append(command)

    def closest_tank(self, tank):
        closest_x = (2 * float(self.constants['worldsize']))**2
        closest_y = (2 * float(self.constants['worldsize']))**2
        best_d = (2 * float(self.constants['worldsize']))**2

        for otank in self.othertanks:
            if(otank.status != 'dead'):
                d = self.dist(otank.x, otank.y, tank.x, tank.y)
                if d < best_d:
                    best_d = d
                    closest_x = otank.x
                    closest_y = otank.y

        for myt in self.mytanks:
            if myt.index != 0 and myt.status != 'dead':
                d = self.dist(myt.x, myt.y, tank.x, tank.y)
                if d < best_d:
                    best_d = d
                    closest_x = myt.x
                    closest_y = myt.y

        return (closest_x, closest_y, best_d)

    def dist(self, x1, y1, x2, y2):
        dist_result = math.sqrt((float(x1) - float(x2))**2 + (float(y1) - float(y2))**2)
        #print dist_result
        return dist_result

    def find_home_base(self, tank):
        bases = self.bzrc.get_bases()
        for base in bases:
            if base.color == self.constants['team']:
                xdist = abs(base.corner1_x - base.corner3_x) / 2.0
                ydist = abs(base.corner1_y - base.corner3_y) / 2.0
                base_x = max(base.corner1_x, base.corner3_x) - (xdist/2.0)
                base_y = max(base.corner1_y, base.corner3_y) - (ydist/2.0)
                return (base_x, base_y)

    def choose_best_flag(self, tank):
        best_flag = None
        best_flag_dist = 2 * float(self.constants['worldsize'])
        for f in self.flags:
            # print str(len(self.flags))
            if f.color != self.constants['team'] and f.poss_color != self.constants['team']:
                dist = math.sqrt((f.x - tank.x)**2 + (f.y - tank.y)**2)
                if dist < best_flag_dist:
                    best_flag_dist = dist
                    best_flag = f
        if best_flag is None:
            return self.flags[0]
        else:
            return best_flag

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
