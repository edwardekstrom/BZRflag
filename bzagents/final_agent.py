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
from mapping_agent_final import MAgent
from shooter_agent_final import KAgent
from pf_agent_final import PFAgent


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

	tanks_per_team = len(bzrc.get_mytanks())

	tank_agents = [0] * tanks_per_team

	# currently this section is hard coded for 10 tanks
	# ******************************
	for i in range(3):
		#print i
		tank_agents[i] = KAgent(bzrc, i)
	for i in range(3,10):
		tank_agents[i] = PFAgent(bzrc, i)
	for i in range(10,10):
		tank_agents[i] = MAgent(bzrc, i)
	# ******************************
		
	#agent = PFAgent(bzrc)
	prev_time = time.time()

	# Run the agent
	try:
		while True:
			time_diff = time.time() - prev_time
			for agent in tank_agents:
				agent.tick(time_diff)
	except KeyboardInterrupt:
		print "Exiting due to keyboard interrupt."
		bzrc.close()


if __name__ == '__main__':
	main()


