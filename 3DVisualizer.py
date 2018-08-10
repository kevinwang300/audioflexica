import numpy as np
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.opengl as gl
import sys

class Terrain(object):
    def __init__(self):
        self.t = QtGui.QApplication(sys.argv)
        self.w = gl.GLViewWidget()
        self.w.setGeometry(0,0,1280,800)
        self.w.opts['viewport'] =  (0, 0, 2560, 1600)
        self.w.setCameraPosition(pos=(0,0,0), distance=10, elevation=30)
        self.w.show()
        # verts = np.array([[x, y] for x in range(20) for y in range(20)])
        # faces = []
        # for i in range(20):
        #     faces.append([1,1])
        # faces = np.array(faces)
        verts = np.array([
            [0, 0, 0],
            [0, 1, 0],
            [1, 0, 0],
            [1, 1, 0],
            [0, 0, 1],
            [0, 1, 1],
            [1, 0, 1],
            [1, 1, 1]
        ])
        faces = np.array([
            [0, 1, 2],
            [1, 2, 3],
            [0, 2, 4],
            [2, 4, 6],
            [4, 5, 6],
            [5, 6, 7],
            [1, 5, 3],
            [3, 5, 7],
            [2, 6, 3],
            [6, 3, 7],
            [0, 4, 1],
            [1, 4, 5]
        ])
        colors = np.array([
            [1, 0, 0, 0.3],
            [0, 1, 0, 0.3],
            [0, 0, 1, 0.3],
            [1, 1, 0, 0.3],
            [1, 0, 0, 0.3],
            [0, 1, 0, 0.3],
            [0, 0, 1, 0.3],
            [1, 1, 0, 0.3],
            [1, 0, 1, 0.3],
            [0, 1, 1, 0.3],
            [1, 0, 1, 0.3],
            [0, 1, 1, 0.3]
        ])
        self.mesh = gl.GLMeshItem(
            vertexes=verts,
            drawEdges=True, faces=faces,
            faceColors=colors
        )
        self.mesh.translate(0,-1,0)
        self.w.addItem(self.mesh)
        
    def start(self):
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtGui.QApplication.instance().exec_()
        
if __name__ == '__main__':
    t = Terrain()
    t.start()
        
