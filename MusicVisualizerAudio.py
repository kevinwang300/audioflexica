"""
This creates a 3D mesh with perlin noise to simulate
a terrain. The mesh is animated by shifting the noise
to give a "fly-over" effect.
If you don't have pyOpenGL or opensimplex, then:
    - conda install -c anaconda pyopengl
    - pip install opensimplex
"""

import numpy as np
from opensimplex import OpenSimplex
import pyqtgraph.opengl as gl
from pyqtgraph.Qt import QtCore, QtGui
import struct
import pyaudio
import sys
import wave


class Terrain(object):
    def __init__(self):
        """
        Initialize the graphics window and mesh surface
        """

        # setup the view window
        self.app = QtGui.QApplication(sys.argv)
        self.window = gl.GLViewWidget()
        self.window.show()
        self.window.setWindowTitle('Terrain')
        self.window.setCameraPosition(pos=(0,0,0), distance=200, elevation=30)
        self.window.setGeometry(0, 0, 1280, 800)
        self.window.pan(-70, -15, 0)
        self.window.opts['viewport'] =  (0, 0, 2560, 1600)

        # constants and arrays
        self.nsteps = 1.3
        self.offset = 0
        self.ypoints = np.arange(-20, 20 + self.nsteps, self.nsteps)
        self.xpoints = np.arange(-20, 20 + self.nsteps, self.nsteps)
        self.nfaces = len(self.ypoints)

        self.RATE = 44100 # 44100
        self.CHUNK = len(self.xpoints) * len(self.ypoints)

        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.RATE,
            input=True,
            output=True,
            frames_per_buffer=self.CHUNK,
        )

        # perlin noise object
        self.noise = OpenSimplex()

        # create the veritices array
        verts, faces, colors = self.mesh()

        self.mesh1 = gl.GLMeshItem(
            faces=faces,
            vertexes=verts,
            faceColors=colors,
            drawEdges=True,
            smooth=False,
        )
        self.mesh1.setGLOptions('additive')
        self.window.addItem(self.mesh1)

    def mesh(self, offset=0, height=2.5, wf_data=None):
        if wf_data is not None:
            wf_data = struct.unpack(str(2 * self.CHUNK) + 'B', wf_data)
            wf_data = np.array(wf_data, dtype='b')[::2] + 128
            wf_data = np.array(wf_data, dtype='int32') - 128
            wf_data = wf_data * 0.04
            wf_data = wf_data.reshape((len(self.xpoints), len(self.ypoints)))
        else:
            wf_data = np.array([1] * 1024)
            wf_data = wf_data.reshape((len(self.xpoints), len(self.ypoints)))

        faces = []
        colors = []
        verts = np.array([
            [
                x, y, wf_data[xid][yid] * self.noise.noise2d(x=xid / 10000 + offset, y=yid / 10000 + offset)
            ] for xid, x in enumerate(self.xpoints) for yid, y in enumerate(self.ypoints)
        ], dtype=np.float32)

        for yid in range(self.nfaces - 1):
            yoff = yid * self.nfaces
            for xid in range(self.nfaces - 1):
                faces.append([
                    xid + yoff,
                    xid + yoff + self.nfaces,
                    xid + yoff + self.nfaces + 1,
                ])
                faces.append([
                    xid + yoff,
                    xid + yoff + 1,
                    xid + yoff + self.nfaces + 1,
                ])
                colors.append([
                    float(xid) / float(self.nfaces), float(1 - xid) / float(self.nfaces), float(yid) / float(self.nfaces), 0.7
                ])
                colors.append([
                    float(1 - xid) / float(self.nfaces), float(xid) / float(self.nfaces), float(1 - yid) / float(self.nfaces), 0.7
                ])

        faces = np.array(faces, dtype=np.uint32)
        colors = np.array(colors, dtype=np.float32)

        return verts, faces, colors

    def update(self):
        """
        update the mesh and shift the noise each time
        """

        wf_data = self.stream.read(self.CHUNK, exception_on_overflow = False)
        print(len(wf_data))
        verts, faces, colors = self.mesh(offset=self.offset, wf_data=wf_data)
        self.mesh1.setMeshData(vertexes=verts, faces=faces, faceColors=colors)
        self.offset -= 0.05

    def start(self):
        """
        get the graphics window open and setup
        """
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtGui.QApplication.instance().exec_()

    def animation(self, frametime=10):
        """
        calls the update method to run in a loop
        """
        timer = QtCore.QTimer()
        timer.timeout.connect(self.update)
        timer.start(frametime)
        self.start()


if __name__ == '__main__':
    t = Terrain()
    
    # CHUNK_SIZE = 1024
    # FORMAT = pyaudio.paInt16
    # RATE = 80000
    # 
    # p = pyaudio.PyAudio()
    # output = p.open(format=FORMAT,
    #                         channels=1,
    #                         rate=RATE,
    #                         input=True,
    #                         output=True,
    #                         frames_per_buffer=CHUNK_SIZE)
    # 
    # with open('Redbone.wav', 'rb') as fh:
    #     while fh.tell() != 50000: # get the file-size from the os module
    #         AUDIO_FRAME = fh.read(CHUNK_SIZE)
    #         print(len(AUDIO_FRAME))
    #         # verts, faces, colors = t.mesh(offset=t.offset, wf_data=AUDIO_FRAME)
    #         # self.mesh1.setMeshData(vertexes=verts, faces=faces, faceColors=colors)
    #         # self.offset -= 0.05
    # 
    #         output.write(AUDIO_FRAME)
    t.animation()
