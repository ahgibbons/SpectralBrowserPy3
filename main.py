from numpy import arange, sin, pi
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('WXAgg')
import matplotlib.pyplot as plt

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.figure import Figure

import wx

CANVAS_WIDTH = 300
CANVAS_HEIGHT = 300

FRAME_WIDTH = 1500
FRAME_HEIGHT = 700 #550

xlim00 = 0
xlim01 = 3
ylim00 = 0
ylim01 = 1

def validate_file(fpath):
    f = open(fpath,'r')
    firstline = f.readline()
    return firstline.startswith('R')

def open_compare_file(fpath):
    df_file = pd.read_csv(fpath,header=1)
    return df_file
    
class CanvasPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent,size=wx.Size(CANVAS_WIDTH,CANVAS_HEIGHT))
        #wx.Panel.__init__(self, parent)
        self.figure = Figure()
        self.axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self, -1, self.figure)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        self.SetSizer(self.sizer)
        self.Fit()

    def draw(self):
        t = arange(0.0, 3.0, 0.01)
        s = sin(2 * pi * t)
        self.axes.plot(t, s)

class MyFrame(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, wx.DefaultPosition,
                          wx.Size(FRAME_WIDTH, FRAME_HEIGHT),style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)
        #wx.Frame.__init__(self, parent, id, title, wx.DefaultPosition)


        hbox = wx.BoxSizer(wx.HORIZONTAL)
        vbox = wx.BoxSizer(wx.VERTICAL)
        canvas_sizer = wx.BoxSizer(wx.VERTICAL)
        control_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        filectrl_panel = wx.Panel(self, -1)
        canvas_panel = wx.Panel(self, -1)
        options_panel = wx.Panel(self, -1)
        button_panel = wx.Panel(canvas_panel,-1)
        self.filectrl = wx.FileCtrl(filectrl_panel,wx.ID_ANY,'.',)
        load_button_panel = wx.Panel(filectrl_panel,-1)
        self.canvas = CanvasPanel(canvas_panel)
        self.canvas.draw()
        self.btn_load_file = wx.Button(load_button_panel,-1,"Load File")
        self.btn_save_plot = wx.Button(button_panel,-1,"Save Image")
        self.text1 = wx.StaticText(button_panel,-1,"xLim (Lower): ",style=wx.ALIGN_RIGHT,size=wx.Size(50,-1))
        self.xlim1 = wx.TextCtrl(button_panel,-1)
        self.text2 = wx.StaticText(button_panel,-1,"xLim (Upper): ",style=wx.ALIGN_RIGHT)
        self.xlim2 = wx.TextCtrl(button_panel,-1)
        
        self.doBinds()
        
        self.display = wx.StaticText(options_panel, -1, '',(10,10), style=wx.ALIGN_CENTRE)

        vbox.Add(self.filectrl,9,wx.EXPAND)
        vbox.Add(load_button_panel,1,wx.EXPAND)
        hbox.Add(filectrl_panel, 2, wx.EXPAND)
        hbox.Add(canvas_panel, 3, wx.EXPAND | wx.ALL)
        hbox.Add(options_panel,1,wx.EXPAND)
        canvas_sizer.Add(self.canvas,6,wx.EXPAND)
        canvas_sizer.Add(button_panel,1,wx.EXPAND)
        control_sizer.Add(self.text1,1)
        control_sizer.Add(self.xlim1,1)
        control_sizer.Add(self.text2,1)
        control_sizer.Add(self.xlim2,1)
        control_sizer.Add(self.btn_save_plot,1)
        button_panel.SetSizer(control_sizer)
        filectrl_panel.SetSizer(vbox)
        canvas_panel.SetSizer(canvas_sizer)
        self.SetSizer(hbox)
        self.Centre()
        
    def doBinds(self):
        self.filectrl.Bind(wx.EVT_FILECTRL_FILEACTIVATED,self.LoadFile)
        self.btn_load_file.Bind(wx.EVT_BUTTON, self.LoadFile)
        self.btn_save_plot.Bind(wx.EVT_BUTTON, self.SavePlot)
        return

    def LoadFile(self,event):
        fpath = self.filectrl.GetPath()
        if not validate_file(fpath):
            wx.MessageBox("Invalid File")
            return

        plot_df = open_compare_file(fpath)
        ax = self.canvas.axes
        ax.clear()
        ax.set_xlim((200,800))
        ax.set_ylim((0,1))
        plot_df.plot(x=0,ax=ax,legend=False)

        self.canvas.canvas.draw()

    def SavePlot(self,event):
        with wx.FileDialog(self,"Choose Location to Save Plot",
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fdialog:
            if fdialog.ShowModal() == wx.ID_CANCEL:
                return
            pathname = fdialog.GetPath()
            if not pathname.endswith('.png'):
                pathname += '.png'
            try:
                print("saving to {:s}.".format(pathname))
                self.canvas.figure.savefig(pathname)
                print("Saved")
                
            except IOError:
                wx.LogError("Cannot save in file {:s}.".format(pathname))

        

class MyApp(wx.App):
    def OnInit(self):
        frame = MyFrame(None, -1, 'Spectrum Browser')
        frame.Show(True)
        self.SetTopWindow(frame)
        return True

app = MyApp(0)
app.MainLoop()
