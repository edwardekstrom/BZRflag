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
from grid import Grid

import numpy
from numpy import *
from numpy.linalg import *
import OpenGL
OpenGL.ERROR_CHECKING = False
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from numpy import zeros


grid = None

def draw_grid():
    # This assumes you are using a numpy array for your grid
    width, height = grid.shape
    glRasterPos2f(-1, -1)
    glDrawPixels(width, height, GL_LUMINANCE, GL_FLOAT, grid)
    glFlush()
    glutSwapBuffers()

def update_grid(new_grid):
    global grid
    grid = new_grid



def init_window(width, height):
    global window
    global grid
    grid = zeros((width, height))
    glutInit(())
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_ALPHA | GLUT_DEPTH)
    glutInitWindowSize(width, height)
    glutInitWindowPosition(0, 0)
    window = glutCreateWindow("Grid filter")
    glutDisplayFunc(draw_grid)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    #glutMainLoop()

class Agent(object):
    """Class handles all command and control logic for a teams tanks."""
    initialGridConstant = 0

    def __init__(self, bzrc):
        self.resetArrays()
        self.bzrc = bzrc
        self.constants = self.bzrc.get_constants()
        # print self.constants
        self.commands = []
        self.potentialFields = []
        self.updates = []
        self.flag_sphere = 400
        self.obstacle_sphere = 1000
        self.enemy_sphere = 100
        self.explore_sphere = 50

        self.prev_x = {}
        self.prev_y = {}
        self.stuck_ticks = {}
        for x in xrange(20):
            self.prev_x[x] = 0
            self.prev_y[x] = 0
            self.stuck_ticks[x] = 0

        self.path_fields = []
        # self.bzrc.ini


        # print 'hello'
        # pos,grid = self.bzrc.get_occgrid(0)
        # x,y = pos
        # print x
        # print y
        self.grid = Grid(int(self.constants['worldsize']),
            int(self.constants['worldsize']),
            self.initialGridConstant,
            self.initialGridConstant)
        # self.grid.init_window(int(self.constants['worldsize']),int(self.constants['worldsize']))
        # for g in grid:
        #     print g
        # print pos
        # print grid
        # print 'world'
        # pf1 = PField(-350, 350, 0, self.flag_sphere, 'attract')
        # pf2 = PField(-350, -350, 0, self.flag_sphere, 'attract')
        # pf3 = PField(350, -350, 0, self.flag_sphere, 'attract')
        # pf4 = PField(350, 350, 0, self.flag_sphere, 'attract')
        # self.path_fields.append(pf1)
        # self.path_fields.append(pf2)
        # self.path_fields.append(pf3)
        # self.path_fields.append(pf4)
        
        self.row_step = 400
        self.col_step = 100
        start_x = -350
        start_y = 200
        end_x = 350
        end_y = -200
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

    def resetArrays(self):
            # mean of the other tanks initial start position
        self.mu = array([[0],
                         [0],
                         [0],
                         [200],
                         [0],
                         [0]])

        self.sigmaT = array([[90,0,0  ,0 ,0,0  ],
                             [0 ,1,0  ,0 ,0,0  ],
                             [0 ,0,0.1,0 ,0,0  ],
                             [0 ,0,0  ,90,0,0  ],
                             [0 ,0,0  ,0 ,1,0  ],
                             [0 ,0,0  ,0 ,0,0.1]])

        self.H = array([[1,0,0,0,0,0],
                        [0,0,0,1,0,0]])

        self.sigmaZ = array([[25,0],
                             [0,25]])

        deltaT = .25
        self.F = array([[1,deltaT,deltaT**2/2,0,0     ,0          ],
                        [0,1     ,deltaT     ,0,0     ,0          ],
                        [0,0     ,1          ,0,0     ,0          ],
                        [0,0     ,0          ,1,deltaT,deltaT**2/2],
                        [0,0     ,0          ,0,1     ,deltaT     ],
                        [0,0     ,0          ,0,0     ,1          ]])

        self.sigmaX = array([[0.1,0  ,0 ,0  ,0  ,0 ],
                             [0  ,0.1,0 ,0  ,0  ,0 ],
                             [0  ,0  ,10,0  ,0  ,0 ],
                             [0  ,0  ,0 ,0.1,0  ,0 ],
                             [0  ,0  ,0 ,0  ,0.1,0 ],
                             [0  ,0  ,0 ,0  ,0  ,10]])

    def my_range(self, start, end, step):
        while start <= end:
            yield start
            start += step


    def tick(self, time_diff):
        """Some time has passed; decide what to do next."""
        # don't need to know where the flags or shots are when exploring.  Enemies are included in the 'othertanks' call
        # pos,partialGrid = self.bzrc.get_occgrid()
        # self.grid.updateGrid(pos,partialGrid)
        self.F[0][1] = time_diff
        self.F[0][3] = time_diff**2/2
        self.F[1][2] = time_diff
        self.F[3][4] = time_diff
        self.F[3][5] = time_diff**2/2
        self.F[4][5] = time_diff
        self.mytanks = self.bzrc.get_mytanks()
        # self.othertanks = self.bzrc.get_othertanks()
        targetTank = self.bzrc.get_othertanks()[0]
        self.commands = []
        if targetTank.status == 'alive':
            agentTank = self.mytanks[0]
            z_tPlus1 = array([[targetTank.x],
                              [targetTank.y]])
            self.updateKalmanFilter(z_tPlus1)

            est = self.H.dot(self.mu)

            self.updates.append(((int(est[0][0]), int(est[1][0])),self.sigmaT))
            aimAngle,distance = self.take_aim((agentTank.x,agentTank.y), agentTank.angle)
            command = Command(0,0,aimAngle*2,True)
            if aimAngle < 1 and aimAngle > -1:
                if distance < 350:
                    command = Command(0,0,aimAngle*2,True)
                else:
                    command = Command(0,0,aimAngle*2,False)
            else:
                command = Command(0,0,aimAngle*2,False)
            self.commands.append(command)
            self.bzrc.do_commands(self.commands)
        else:
            resetArrays()





        # self.doTank(self.mytanks[0])
        # self.doTank(self.mytanks[1])
        
        # in the rare case that a tank runs into its own bullet, don't do anything while it is dead

    def take_aim(self, tankPosition, tankAngle):
        xPos = self.mu[0][0]
        xVel = self.mu[1][0]
        xAcc = self.mu[2][0]
        yPos = self.mu[3][0]
        yVel = self.mu[4][0]
        yAcc = self.mu[5][0]

        tankX, tankY = tankPosition

        velocity = math.sqrt(xVel**2 + yVel**2)
        acceleration = math.sqrt(xAcc**2 + yAcc**2)

        distance = math.sqrt((tankX - xPos)**2 + (tankY - yPos)**2)

        timeToEnemy = 0
        if acceleration!=0:
            r = (100-velocity)**2 - 4*(acceleration/2)*distance*-1
            if r>0:
                plusRoot = (-(100-velocity) + math.sqrt(r)) / acceleration
                minusRoot = (-(100-velocity) - math.sqrt(r)) / acceleration
                if plusRoot > minusRoot:
                    timeToEnemy = plusRoot
                else:
                    timeToEnemy = minusRoot
            else:
                timeToEnemy = 0
        else:
            timeToEnemy = distance/(100-velocity)

        projectedX = xPos + xVel*timeToEnemy + xAcc*timeToEnemy**2/2
        projectedY = yPos + yVel*timeToEnemy + yAcc*timeToEnemy**2/2
        # print 'projX = ' + str(projectedX) + ', projY = ' + str(projectedY)

        distance = math.sqrt((tankX - projectedX)**2 + (tankY - projectedY)**2)
        angel = math.atan2(projectedY - tankY, projectedX - tankX)
        return (self.normalize_angle(angel - tankAngle), distance)
        


    def updateKalmanFilter(self, z_tPlus1):
        fTranspose = self.F.transpose()
        hTranspose = self.H.transpose()
        k0 = self.F.dot(self.sigmaT).dot(fTranspose)+self.sigmaX
        k1 = self.H.dot(k0).dot(hTranspose)+self.sigmaZ
        k2 = inv(k1)
        k_tPlus1 = k0.dot(hTranspose).dot(k2)

        mu0 = z_tPlus1-self.H.dot(self.F).dot(self.mu)
        mu_tPlus1 = self.F.dot(self.mu) + k_tPlus1.dot(mu0)

        sigmaT_tPlus1 = (identity(6)-k_tPlus1.dot(self.H)).dot(k0)

        self.sigmaT = sigmaT_tPlus1
        self.mu = mu_tPlus1


    def doTank(self, tank):        
        exp_tank = tank
        if(exp_tank.status == 'dead'):
            return
        if tic % 4 == 0:
            pos,partialGrid = self.bzrc.get_occgrid(tank.index)
            self.updates.append((pos,partialGrid))
        # self.grid.updateGrid(pos,partialGrid)

        # if the tank has no change in position, it is stuck. Try turning and shooting whatever it is is next to (usually a tank)
        travel_d = self.dist(exp_tank.x, exp_tank.y, self.prev_x[exp_tank.index], self.prev_y[exp_tank.index])
        pfe = None
        # print travel_d
        if travel_d == 0.0:
            self.stuck_ticks[exp_tank.index] = self.stuck_ticks[exp_tank.index] + 1
            # # print "I'm stuck %d" % self.stuck_ticks
            # enemy_x, enemy_y, enemy_dist = self.closest_tank(exp_tank)
            # # a temp sphere of 10 for enemies prevents the explorer tank from tracking down tanks that aren't next to it
            # tempPFEsphere = 10
            # if enemy_dist < tempPFEsphere:
            #     pfe = PField(enemy_x, enemy_y, 1, tempPFEsphere, 'attract')
        else:
            self.stuck_ticks[exp_tank.index] = 0

        # move the tank to the next pField (explore spot or shoot tank)
        # for tank in self.mytanks:
        #     if tank.status == 'dead':
        #         return
        #     else:
        #         self.pf_move(tank, self.cur_path, pfe)
        #         pos,partialGrid = self.bzrc.get_occgrid(tank.index)
        #         self.grid.updateGrid(pos,partialGrid)
        self.pf_move(exp_tank, self.cur_path, pfe)    
        tolerance = 20
        if(abs(exp_tank.x - self.cur_path.x) <= tolerance and abs(exp_tank.y - self.cur_path.y) <= tolerance):
            # print "nailed it!"
            if self.path_fields:
                self.cur_path = self.path_fields.pop(0)

        
        # if the tank is stuck longer than the really stuck tollerance, shift the pField down or up depending on the quadrant
        really_stuck_tolerance = 40
        if self.stuck_ticks[exp_tank.index] > really_stuck_tolerance:
            print "I'm REALLY stuck"
            direction = 1
            if(exp_tank.y <= 0):
                direction = -1

            self.cur_path = PField(self.cur_path.x, self.cur_path.y + (self.row_step * direction), 0, self.explore_sphere, 'attract')
            print "%f, %f" % (self.cur_path.x, self.cur_path.y)
            self.stuck_ticks[exp_tank.index] = 0


        self.prev_x[exp_tank.index] = exp_tank.x
        self.prev_y[exp_tank.index] = exp_tank.y
        results = self.bzrc.do_commands(self.commands)

    def doUpdate(self):
        # print len(self.updates)
        for update in self.updates:
            pos,partialGrid = update
            self.grid.updateGrid(pos,partialGrid)
        self.updates = []

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

    init_window(int(agent.constants['worldsize']),int(agent.constants['worldsize']))
    # print 'init complete'
    prev_time = time.time()

    # Run the agent
    try:
        global tic
        tic = 0
        while True:
            t = time.time()
            time_diff = t - prev_time
            prev_time = t
            agent.tick(time_diff)
            agent.doUpdate()
            if(tic == 10):
                update_grid(numpy.array(zip(*agent.grid.grid)))
                draw_grid()
                tic = 0
            tic+=1
    except KeyboardInterrupt:
        print "Exiting due to keyboard interrupt."
        bzrc.close()


if __name__ == '__main__':
    main()

# vim: et sw=4 sts=4
