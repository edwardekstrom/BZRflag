from __future__ import division
from itertools import cycle
import time
import sys
import math
import threading
try:
    from numpy import linspace
except ImportError:
    # This is stolen from numpy.  If numpy is installed, you don't
    # need this:
    def linspace(start, stop, num=50, endpoint=True, retstep=False):
        """Return evenly spaced numbers.

        Return num evenly spaced self.samples from start to stop.  If
        endpoint is True, the last sample is stop. If retstep is
        True then return the step value used.
        """
        num = int(num)
        if num <= 0:
            return []
        if endpoint:
            if num == 1:
                return [float(start)]
            step = (stop-start)/float((num-1))
            y = [x * step + start for x in xrange(0, num - 1)]
            y.append(stop)
        else:
            step = (stop-start)/float(num)
            y = [x * step + start for x in xrange(0, num)]
        if retstep:
            return y, step
        else:
            return y


try:
    from bzrc import BZRC, Command
except ImportError:
    print "could not find bzrc."
    import sys
    sys.exit(-1)

try:
    from pFields import PField
except ImportError:
    print "could not find pFields."
    import sys
    sys.exit(-1)
try:
    from Gnuplot import GnuplotProcess
except ImportError:
    print "Sorry.  You don't have the Gnuplot module installed."
    import sys
    sys.exit(-1)

########################################################################
# Constants
class Visualizer:

    def __init__(self,bzrc, flagColor):
                # Output file:
        self.FILENAME = 'fields.gpi'
        # Size of the world (one of the "constants" in bzflag):
        self.WORLDSIZE = 800
        # How many self.samples to take along each dimension:
        self.SAMPLES = 25
        # Change spacing by changing the relative length of the vectors.  It looks
        # like scaling by 0.75 is pretty good, but this is adjustable:
        self.VEC_LEN = 0.75 * self.WORLDSIZE / self.SAMPLES
        # Animation parameters:
        self.ANIMATION_MIN = 0
        self.ANIMATION_MAX = 500
        self.ANIMATION_FRAMES = 50

        self.BZRC = bzrc
        self.constants = self.BZRC.get_constants()
        self.flag_sphere = 400
        self.obstacle_sphere = 1000
        self.enemy_sphere = 100
        self.OBSTACLES = self.BZRC.get_obstacles()
        self.obstacle_centers = []
        for ob in self.OBSTACLES:
            totalX = 0
            totalY = 0
            for corner in ob:
                totalX += corner[0]
                totalY += corner[1]
            averageX = totalX / len(ob)
            averageY = totalY / len(ob)
            for corner in ob:
                if self.dist(averageX,averageY,corner[0],corner[1]) > self.obstacle_sphere:
                    self.obstacle_sphere = self.dist(averageX,averageY,corner[0],corner[1])
                    # print self.obstacle_sphere
            tup = (averageX,averageY)
            self.obstacle_centers.append(tup)

        self.mytanks, self.othertanks, self.flags, shots = self.BZRC.get_lots_o_stuff()
        outfile = open(self.FILENAME, 'w')
        print >>outfile, self.gnuplot_header(-self.WORLDSIZE / 2, self.WORLDSIZE / 2)
        print >>outfile, self.draw_obstacles(self.OBSTACLES)
        field_function = self.generate_field_function(150)
        print >>outfile, self.plot_field(field_function)

    def visualize(self):
        time.sleep(10)
        forward_list = list(linspace(self.ANIMATION_MIN, self.ANIMATION_MAX, self.ANIMATION_FRAMES/2))
        backward_list = list(linspace(self.ANIMATION_MAX, self.ANIMATION_MIN, self.ANIMATION_FRAMES/2))
        anim_points = forward_list + backward_list
        lastTime = time.time()
        gp = GnuplotProcess(persist=False)
        gp.write(self.gnuplot_header(-self.WORLDSIZE / 2, self.WORLDSIZE / 2))
        gp.write(self.draw_obstacles(self.OBSTACLES))
        for scale in cycle(anim_points):
                # time.sleep(.3)
                # print scale
            self.mytanks, self.othertanks, self.flags, shots = self.BZRC.get_lots_o_stuff()
            # self.f = flags[self.FLAG_INT]
            field_function = self.generate_field_function(scale)
            gp.write(self.plot_field(field_function))

    # def thread_start(self):
    #       threading.Thread(target=self._thread_start).start()

# vim: et sw=4 sts=4

    def generate_field_function(self, scale):
        def function(x, y):
            '''User-defined field function.'''
            sqnorm = (x**2 + y**2)
            if sqnorm == 0.0:
                return 0, 0
            else:
                closest_flag = self.choose_best_flag(x,y)
                enemy_x, enemy_y, enemy_dist = self.closest_enemy(x,y)
                obstacle_x, obstacle_y, d = self.closest_obstacle(x,y)
                # if enemy_dist < self.enemy_sphere:
                #     return x - enemy_x, y - enemy_y
                # elif d < self.obstacle_sphere:
                #     return math.cos(y - obstacle_y), -math.sin(x - obstacle_x)
                # else:
                #     return closest_flag.x - x, closest_flag.y - y
                return closest_flag.x - x, closest_flag.y - y #attractive
                # return x - enemy_x, y - enemy_y #repulsive
                # return math.cos(y - obstacle_y), -math.sin(x - obstacle_x) #tangential
                
        return function




    ########################################################################
    # Helper Functions

    def gpi_point(self, x, y, vec_x, vec_y):
        '''Create the centered gpi data point (4-tuple) for a position and
        vector.  The vectors are expected to be less than 1 in magnitude,
        and larger values will be scaled down.'''
        r = (vec_x ** 2 + vec_y ** 2) ** 0.5
        if r > 1:
            vec_x /= r
            vec_y /= r
        return (x - vec_x * self.VEC_LEN / 2, y - vec_y * self.VEC_LEN / 2,
                vec_x * self.VEC_LEN, vec_y * self.VEC_LEN)

    def gnuplot_header(self, minimum, maximum):
        '''Return a string that has all of the gnuplot sets and unsets.'''
        s = ''
        s += 'set xrange [%s: %s]\n' % (minimum, maximum)
        s += 'set yrange [%s: %s]\n' % (minimum, maximum)
        # The key is just clutter.  Get rid of it:
        s += 'unset key\n'
        # Make sure the figure is square since the world is square:
        s += 'set size square\n'
        # Add a pretty title (optional):
        #s += "set title 'Potential Fields'\n"
        return s

    def draw_line(self, p1, p2):
        '''Return a string to tell Gnuplot to draw a line from point p1 to
        point p2 in the form of a set command.'''
        x1, y1 = p1
        x2, y2 = p2
        return 'set arrow from %s, %s to %s, %s nohead lt 3\n' % (x1, y1, x2, y2)

    def draw_obstacles(self, obstacles):
        '''Return a string which tells Gnuplot to draw all of the obstacles.'''
        s = 'unset arrow\n'

        for obs in obstacles:
            last_point = obs[0]
            for cur_point in obs[1:]:
                s += self.draw_line(last_point, cur_point)
                last_point = cur_point
            s += self.draw_line(last_point, obs[0])
        return s

    def plot_field(self, function):
        '''Return a Gnuplot command to plot a field.'''
        s = "plot '-' with vectors head\n"

        separation = self.WORLDSIZE / self.SAMPLES
        end = self.WORLDSIZE / 2 - separation / 2
        start = -end

        points = ((x, y) for x in linspace(start, end, self.SAMPLES)
                    for y in linspace(start, end, self.SAMPLES))

        for x, y in points:
            f_x, f_y = function(x, y)
            # if countG == 0:
            # print 'f(y) = f(' + str(y) + ") = " + str(f_y)
            # print 'f(x) = f(' + str(x) + ") = " + str(f_x)
            plotvalues = self.gpi_point(x, y, f_x, f_y)
            if plotvalues is not None:
                x1, y1, x2, y2 = plotvalues
                s += '%s %s %s %s\n' % (x1, y1, x2, y2)
        # countG += 1
        s += 'e\n'
        return s
    def closest_obstacle(self, xx, yy):
        closest_x = (2 * float(self.constants['worldsize']))**2
        closest_y = (2 * float(self.constants['worldsize']))**2
        best_d = (2 * float(self.constants['worldsize']))**2

        # obstacles = self.bzrc.get_obstacles()
        for o in self.obstacle_centers:
            x,y = o
            d = self.dist(x, y, xx, yy)
            if d < best_d:
                best_d = d
                closest_x = x
                closest_y = y

        return (closest_x, closest_y, best_d)

    def closest_enemy(self, xx, yy):
        closest_x = (2 * float(self.constants['worldsize']))**2
        closest_y = (2 * float(self.constants['worldsize']))**2
        best_d = (2 * float(self.constants['worldsize']))**2

        for e in self.othertanks:
            d = self.dist(e.x, e.y, xx, yy)
            if d < best_d:
                best_d = d
                closest_x = e.x
                closest_y = e.y

        return (closest_x, closest_y, best_d)

    def dist(self, x1, y1, x2, y2):
        return (x1 - x2)**2 + (y1 - y2)**2

    def find_home_base(self, tank):
        bases = self.bzrc.get_bases()
        for base in bases:
            if base.color == self.constants['team']:
                xdist = abs(base.corner1_x - base.corner3_x) / 2.0
                ydist = abs(base.corner1_y - base.corner3_y) / 2.0
                base_x = max(base.corner1_x, base.corner3_x) - (xdist/2.0)
                base_y = max(base.corner1_y, base.corner3_y) - (ydist/2.0)
                return (base_x, base_y)

    def choose_best_flag(self, x, y):
        best_flag = None
        best_flag_dist = 2 * float(self.constants['worldsize'])
        for f in self.flags:
	        # print str(len(self.flags))
	        if f.color != self.constants['team'] and f.poss_color != self.constants['team']:
	            dist = math.sqrt((f.x - x)**2 + (f.y - y)**2)
	            if dist < best_flag_dist:
	                best_flag_dist = dist
	                best_flag = f
	            if best_flag is None:
	                return self.flags[0]
	            else:
	                return best_flag
	                # return self.flags[2]

def main():
    # Process CLI arguments.
    try:
        execname, host, port, color = sys.argv
    except ValueError:
        execname = sys.argv[0]
        print >>sys.stderr, '%s: incorrect number of arguments' % execname
        print >>sys.stderr, 'usage: %s hostname port' % sys.argv[0]
        sys.exit(-1)

    bzrc = BZRC(host,int(port))
    v = Visualizer(bzrc, color)
    v.visualize()

if __name__ == '__main__':
    main()
