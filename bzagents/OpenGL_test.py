#!/usr/bin/env python

import time
import numpy
from grid import Grid
import OpenGL
OpenGL.ERROR_CHECKING = False
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from numpy import zeros

grid = None

grid = Grid(int(800),
    int(800),
    float(0.97),
    float(0.9))

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


def main():
    init_window(int(800),int(800))
    # print 'init complete'
    prev_time = time.time()

    # Run the agent
    try:
        global tic
        tic = 0
        while True:
            if(tic == 10):
                update_grid(numpy.array(zip(*grid)))
                draw_grid()
                tic = 0
            tic+=1
    except KeyboardInterrupt:
        print "Exiting due to keyboard interrupt."


if __name__ == '__main__':
    main()

# vim: et sw=4 sts=4















