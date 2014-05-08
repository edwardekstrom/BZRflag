from __future__ import division
from itertools import cycle
import time
import sys
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
		self.OBSTACLES = [ ((0, 0), (-150, 0), (-150, -50), (0, -50)),
              ((200, 100), (200, 330), (300, 330), (300, 100))]

		self.BZRC = bzrc
		print 'got here'
		time.sleep(2)
		print 'done sleeping'
		self.FLAG_INT = 0
		mytanks, othertanks, flags, shots = self.BZRC.get_lots_o_stuff()
		for f in flags:
		    if f.color == flagColor:
		        self.FLAG_INT += 1
		        break
		self.f = flags[self.FLAG_INT]
		print f.color
		print 'flag x = ' + str(f.x)
		print 'flag y = ' + str(f.y)



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
		for scale in anim_points:
		    # time.sleep(.3)
		    # print scale
		    mytanks, othertanks, flags, shots = self.BZRC.get_lots_o_stuff()
		    self.f = flags[self.FLAG_INT]
		    field_function = self.generate_field_function(scale)
		    gp.write(self.plot_field(field_function))

	# def thread_start(self):
	# 	threading.Thread(target=self._thread_start).start()

# vim: et sw=4 sts=4

	def generate_field_function(self, scale):
	    def function(x, y):
	        '''User-defined field function.'''
	        sqnorm = (x**2 + y**2)
	        if sqnorm == 0.0:
	            return 0, 0
	        else:
	            # print str(f.x)
	            return self.f.x - x, self.f.y - y
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