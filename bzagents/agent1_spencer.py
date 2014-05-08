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
        self.flag_sphere = 20
        self.obstacle_sphere = 0
        self.enemy_sphere = 10

        print ""
        for o in self.bzrc.get_obstacles():
            print o
        print ""


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



        for tank in mytanks:
            pfo = None
            # obstacle_x, obstacle_y, d = self.closest_obstacle(tank)
            # if d < self.obstacle_sphere:
            #     pfo = PField(obstacle_x, obstacle_y, 0, self.obstacle_sphere, 'tangent')
            

            pfe = None
            enemy_x, enemy_y, enemy_dist = self.closest_enemy(tank, self.enemies)
            if enemy_dist < self.enemy_sphere:
                pfe = PField(enemy_x, enemy_y, 0, self.enemy_sphere, 'repel')

            # if flag possession, then put a pf on the home_base
            if(tank.flag == '-'):
                best_flag = self.choose_best_flag(tank)
                pf = PField(best_flag.x, best_flag.y, 0, self.flag_sphere, 'attract')
            # if not possessed, then put a pf on a flag
            else:
                home_base_x, home_base_y = self.find_home_base(tank)
                pf = PField(home_base_x, home_base_y, 0, self.flag_sphere, 'attract')
            self.pf_move(tank, pf, pfo, pfe)

        #for tank in mytanks:
            #self.attack_enemies(tank)

        #for tank in mytanks:
            #self.run_to_flag(tank)

        results = self.bzrc.do_commands(self.commands)

    def pf_move(self, tank, pf, pfo, pfe):
        final_angle = 0

        if pfo == None and pfe == None:
            speedmod, angle = pf.calc_vector(tank.x, tank.y)
        elif pfe == None:
            speedmod, angle = pfo.calc_vector(tank.x, tank.y)
        else:
            speedmod, angle = pfe.calc_vector(tank.x, tank.y)
        

        angle = self.normalize_angle(angle - tank.angle)

        if final_angle == 0:
            final_angle = angle
        else:
            final_angle = (float(final_angle) + float(angle)) / 2.0

        
        # current_tank_speed = math.sqrt(float(tank.vx**2) + float(tank.vy**2))
        # print current_tank_speed

        #command = Command(tank.index, speedmod * current_tank_speed, 2 * final_angle, True)
        command = Command(tank.index, speedmod, 2 * final_angle, True)
        self.commands.append(command)
    
    def closest_obstacle(self, tank):
        closest_x = 2 * float(self.constants['worldsize'])
        closest_y = 2 * float(self.constants['worldsize'])
        best_d = 2 * float(self.constants['worldsize'])

        obstacles = self.bzrc.get_obstacles()
        for o in obstacles:
            for corner in o:
                d = self.dist(corner[0], corner[1], tank.x, tank.y)
                if d < best_d:
                    best_d = d
                    closest_x = corner[0]
                    closest_y = corner[1]

        return (closest_x, closest_y, best_d)

    def closest_enemy(self, tank, enemies):
        closest_x = 2 * float(self.constants['worldsize'])
        closest_y = 2 * float(self.constants['worldsize'])
        best_d = 2 * float(self.constants['worldsize'])

        for e in enemies:
            d = self.dist(e.x, e.y, tank.x, tank.y)
            if d < best_d:
                best_d = d
                closest_x = e.x
                closest_y = e.y

        return (closest_x, closest_y, best_d)

    def dist(self, x1, y1, x2, y2):
        return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

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
