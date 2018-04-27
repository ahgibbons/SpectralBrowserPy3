from numpy import arange, sin, pi
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('WXAgg')
import matplotlib.pyplot as plt
import parseSpectral as ps

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.figure import Figure

import wx

CANVAS_WIDTH = 300
CANVAS_HEIGHT = 300

COMPARE_FILE = 1
PHOTAL_FILE = 2
INVALID_FILE = 0

FRAME_WIDTH = 1500
FRAME_HEIGHT = 700 #550

xlim00 = 0
xlim01 = 3
ylim00 = 0
ylim01 = 1

def validate_file(fpath):
    f = open(fpath,'r')
    firstline = f.readline()
    if firstline.startswith('R'):
        return COMPARE_FILE
    elif firstline.startswith('ListNo.'):
        return PHOTAL_FILE
    else:
        return INVALID_FILE

def open_compare_file(fpath):
    df_file = pd.read_csv(fpath,header=1)
    names = df_file.columns.values[1:]
    wavelength = np.array(df_file['Wavelength'])
    plotData = [[wavelength,np.array(df_file[col])] for col in names]
    return PlotData(names,plotData)

def open_photal_file(fpath):
    with open(fpath,'r') as ffile:
        ftext = ffile.read()
    fdata = ps.genSpecData(ftext)
    names = [a.name for a in fdata]
    plotData = [[a.wavelength,a.rmeasured] for a in fdata]
    return PlotData(names,plotData)

class PlotData:
    def __init__(self,names,data):
        status = [True for d in data]
        self.plotData = [list(a) for a in zip(names,data,status)]

    def getNames(self):
        return zip(*self.plotData)[0]

    def getData(self):
        return zip(*self.plotData)[1]
        
class CanvasPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent,size=wx.Size(CANVAS_WIDTH,CANVAS_HEIGHT))
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


        self.plotData = None

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        vbox = wx.BoxSizer(wx.VERTICAL)
        canvas_sizer = wx.BoxSizer(wx.VERTICAL)
        control_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sample_selector_sizer = wx.BoxSizer(wx.VERTICAL)
        select_button_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.checkboxes = []
        
        filectrl_panel = wx.Panel(self, -1)
        canvas_panel = wx.Panel(self, -1)
        sample_panel = wx.Panel(self,-1)
        select_button_panel = wx.Panel(sample_panel,-1)
        self.samples_select_panel = wx.ScrolledWindow(self, -1)
        self.samples_select_panel.SetScrollbars(20,20,50,50)
        button_panel = wx.Panel(canvas_panel,-1)
        self.filectrl = wx.FileCtrl(filectrl_panel,wx.ID_ANY,'.',)
        load_button_panel = wx.Panel(filectrl_panel,-1)
        self.canvas = CanvasPanel(canvas_panel)
        
        self.btn_load_file = wx.Button(load_button_panel,-1,"Load File")
        self.btn_save_plot = wx.Button(button_panel,-1,"Save Image")
        self.text1 = wx.StaticText(button_panel,-1,"xLim (Lower): ",
                                   style=wx.ALIGN_RIGHT,size=wx.Size(50,-1))
        self.xlim1 = wx.TextCtrl(button_panel,-1)
        self.text2 = wx.StaticText(button_panel,-1,"xLim (Upper): ",
                                   style=wx.ALIGN_RIGHT)
        self.xlim2 = wx.TextCtrl(button_panel,-1)

        #-- Sample Select Panel --#
        self.select_all = wx.Button(select_button_panel,-1,"Select All")
        self.select_none = wx.Button(select_button_panel,-1,"Select All")
        
        
        self.doBinds()
        

        vbox.Add(self.filectrl,9,wx.EXPAND)
        vbox.Add(load_button_panel,1,wx.EXPAND)
        hbox.Add(filectrl_panel, 2, wx.EXPAND)
        hbox.Add(canvas_panel, 3, wx.EXPAND | wx.ALL)
        hbox.Add(self.samples_select_panel,1,wx.EXPAND)
        canvas_sizer.Add(self.canvas,6,wx.EXPAND)
        canvas_sizer.Add(button_panel,1,wx.EXPAND)
        control_sizer.Add(self.text1,1)
        control_sizer.Add(self.xlim1,1)
        control_sizer.Add(self.text2,1)
        control_sizer.Add(self.xlim2,1)
        control_sizer.Add(self.btn_save_plot,1)
        select_button_sizer.Add(self.select_all,0)
        select_button_sizer.Add(self.select_none,0)
        self.sample_selector_sizer.Add(select_button_panel,0)
        self.sample_selector_sizer.Add(sample_panel,0)
        
        button_panel.SetSizer(control_sizer)
        filectrl_panel.SetSizer(vbox)
        canvas_panel.SetSizer(canvas_sizer)
        #select_button_panel.SetSizer(select_button_sizer)
        self.samples_select_panel.SetSizer(self.sample_selector_sizer)
        self.SetSizer(hbox)
        self.Centre()
        
    def doBinds(self):
        self.filectrl.Bind(wx.EVT_FILECTRL_FILEACTIVATED,self.LoadFile)
        self.btn_load_file.Bind(wx.EVT_BUTTON, self.LoadFile)
        self.btn_save_plot.Bind(wx.EVT_BUTTON, self.SavePlot)
        return

    def choose_sample(self,event):
        name = event.EventObject.GetLabel()
        state = event.EventObject.GetValue()
        for d in self.plotData.plotData:
            if d[0] == name:
                d[2] = state
                self.plot()

    def plot(self):
        ax = self.canvas.axes
        ax.clear()
        ax.set_xlim((250,800))
        ax.set_ylim((0,1))
        for d in self.plotData.plotData:
            if d[2]:
                ax.plot(d[1][0],d[1][1])

        ax.set_xlabel('Wavelength, nm')
        ax.set_ylabel('Relative Intensity')
            
        self.canvas.canvas.draw()
    

    def LoadFile(self,event):
        fpath = self.filectrl.GetPath()
        fileValidate = validate_file(fpath)
        if fileValidate   == COMPARE_FILE:
            self.plotData = open_compare_file(fpath)
        elif fileValidate == PHOTAL_FILE:
            self.plotData = open_photal_file(fpath)
        else:
            wx.MessageBox("Invalid File")
            return

        self.plot()
        
        self.sample_selector_sizer.DeleteWindows()
        self.checkboxes = []

        for n,d in enumerate(self.plotData.plotData):
            chkbox = wx.CheckBox(self.samples_select_panel,-1,d[0])
            self.checkboxes.append(chkbox)
            self.sample_selector_sizer.Add(chkbox,0)
            chkbox.SetValue(True)
            chkbox.Bind(wx.EVT_CHECKBOX,self.choose_sample)
        self.samples_select_panel.SetScrollbars(20,20,50,50)
        self.samples_select_panel.Layout()
            
        
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

    def SaveCSV(self,event):
        pass

                
class MyApp(wx.App):
    def OnInit(self):
        frame = MyFrame(None, -1, 'Spectrum Browser')
        frame.Show(True)
        self.SetTopWindow(frame)
        return True

app = MyApp(0)
app.MainLoop()
