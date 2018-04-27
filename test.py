import wx
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.figure as mplfig
import scipy.spatial.distance as dist
import matplotlib.backends.backend_wxagg as mwx

class Frame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, size = (800, 600))
        self.panel = wx.Panel(self)        
        self.fig = mplfig.Figure(figsize = (5, 4), dpi = 100)
        self.ax = self.fig.add_subplot(111)
        self.vbox = wx.BoxSizer(wx.VERTICAL)        
        self.canvas = mwx.FigureCanvasWxAgg(self.panel, wx.ID_ANY, self.fig)
        self.toolbar = mwx.NavigationToolbar2WxAgg(self.canvas)
        self.button = wx.Button(self.panel, wx.ID_ANY, "Quit")
        self.vbox.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        self.vbox.Add(self.toolbar, 0, wx.EXPAND)        
        self.vbox.Add(
            self.button, 0, border = 3,
            flag = wx.ALIGN_LEFT | wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.panel.SetSizer(self.vbox)
        self.vbox.Fit(self)
        self.toolbar.update()
        self.update = self.animate().next
        self.timer = wx.Timer(self)
        self.timer.Start(1)
        self.Bind(wx.EVT_BUTTON, self.OnCloseWindow, self.button)        
        self.Bind(wx.EVT_TIMER, lambda event: self.update())
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)

    def OnCloseWindow(self, evt):
        self.timer.Stop()
        del self.timer
        self.Destroy()

    def animate(self):
        N = 100                                             #Number of particles
        R = 10000                                           #Box width
        pR = 5                                               #Particle radius

        r = np.random.randint(0, R, (N, 2))                  #Position vector
        v = np.random.randint(-R/100, R/100, (N, 2))           #velocity vector
        a = np.array([0, -10])                               #Forces
        v_limit = R/2                                       #Speedlimit

        line, = self.ax.plot([], 'o')
        line2, = self.ax.plot([], 'o')                           #Track a particle
        self.ax.set_xlim(0, R+pR)
        self.ax.set_ylim(0, R+pR)        

        while True:
            v = v+a                                           #Advance
            r = r+v

            #Collision tests
            r_hit_x0 = np.where(r[:, 0]<0)                   #Hit floor?
            r_hit_x1 = np.where(r[:, 0]>R)                   #Hit roof?
            r_hit_LR = np.where(r[:, 1]<0)                   #Left wall?
            r_hit_RR = np.where(r[:, 1]>R)                   #Right wall?

            #Stop at walls
            r[r_hit_x0, 0] = 0
            r[r_hit_x1, 0] = R
            r[r_hit_LR, 1] = 0
            r[r_hit_RR, 1] = R

            #Reverse velocities
            v[r_hit_x0, 0] = -0.9*v[r_hit_x0, 0]
            v[r_hit_x1, 0] = -v[r_hit_x1, 0]
            v[r_hit_LR, 1] = -0.95*v[r_hit_LR, 1]
            v[r_hit_RR, 1] = -0.99*v[r_hit_RR, 1]

            #Collisions
            D = dist.squareform(dist.pdist(r))
            ind1, ind2 = np.where(D < pR)
            unique = (ind1 < ind2)
            ind1 = ind1[unique]
            ind2 = ind2[unique]

            for i1, i2 in zip(ind1, ind2):
                eps = np.random.rand()
                vtot = v[i1, :]+v[i2, :]
                v[i1, :] = -(1-eps)*vtot
                v[i2, :] = -eps*vtot

            line.set_ydata(r[:, 1])
            line.set_xdata(r[:, 0])
            line2.set_ydata(r[:N/5, 1])
            line2.set_xdata(r[:N/5, 0])
            self.canvas.draw()
            yield True

def main():
    app = wx.App(False)
    frame = Frame()
    frame.Show(True)
    app.MainLoop()

if __name__ == '__main__':
    main()
