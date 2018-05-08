import sys
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
from wx.lib.mixins.listctrl import TextEditMixin

CANVAS_WIDTH = 300
CANVAS_HEIGHT = 300

MAX_INT = 1000000

COMPARE_FILE = 1
PHOTAL_FILE = 2
INVALID_FILE = 0

FRAME_WIDTH = 1500
FRAME_HEIGHT = 700 #550

xlim00 = 0
xlim01 = 3
ylim00 = 0
ylim01 = 1

legend_positions = ['best','upper right', 'upper left', 'lower left',
                    'lower right', 'right', 'center left', 'center right',
                    'lower center', 'upper center', 'center']

class EditListCtrl(wx.ListCtrl, TextEditMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self,parent,-1,style=wx.LC_REPORT,size=wx.Size(750,-1))
        TextEditMixin.__init__(self)
        self.Bind(wx.EVT_LIST_BEGIN_LABEL_EDIT, self.OnBeginLabelEdit)

    def OnBeginLabelEdit(self,event):
        if event.GetColumn() == 0:
            event.Veto()
        else:
            event.Skip()

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

class PlotDatum:
    def __init__(self,name,data,status,label):
        self.name   = name
        self.data   = data
        self.status = status
        self.label  = label

class PlotData:
    def __init__(self,names,data):
        status = [True for d in data]
        #self.plotData = [PlotDatum(*a) for a in zip(names,data,status,names)]
        self.plotData = [list(a) for a in zip(names,data,status,names)]

    def getNames(self):
        return zip(*self.plotData)[0]
        #return [d.name for d in self.plotData]

    def getData(self):
        return zip(*self.plotData)[1]
        #return [d.data for d in self.plotData]
        
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


class LabelDialog(wx.Dialog):
    def __init__(self,parent,id,title):
        wx.Dialog.__init__(self, parent, id, title,
                           wx.DefaultPosition,size=wx.Size(800,-1))
        self.parent = parent
        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        
        panel = wx.Panel(self,-1)
        button_panel = wx.Panel(self,-1)

        self.list = EditListCtrl(panel)
        self.list.InsertColumn(0,'File Name',width=300)
        self.list.InsertColumn(1,'Label',width=300)

        for n in range(len(parent.labels)):
            index = self.list.InsertItem(MAX_INT,parent.names[n])
            self.list.SetItem(index,1,parent.labels[n])

        ok_btn = wx.Button(button_panel,-1,'OK')
        cancel_btn = wx.Button(button_panel,-1,'Cancel')

        ok_btn.Bind(wx.EVT_BUTTON,self.okPress)
        cancel_btn.Bind(wx.EVT_BUTTON,self.cancelPress)

        hbox.Add(ok_btn)
        hbox.Add(cancel_btn)

        
        vbox.Add(panel,1,wx.EXPAND | wx.GROW,0)
        vbox.Add(button_panel,1,wx.EXPAND)

        button_panel.SetSizer(hbox)
        self.SetSizer(vbox)
        self.Centre()
    
    def okPress(self,event):
        newLabels = []
        count = self.list.GetItemCount()
        for row in range(count):
            label = self.list.GetItem(itemIdx=row, col=1).GetText()
            newLabels.append(label)
        self.parent.labels = newLabels

        self.parent.plot()
        
        self.Close()
            
    def cancelPress(self,event):
        self.Close()

class MyFrame(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, wx.DefaultPosition,
                          wx.Size(FRAME_WIDTH, FRAME_HEIGHT),style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)


        self.plotData = None
        self.legend = False
        self.legend_cur_loc = legend_positions[0]
        self.labels = []
        self.names = []
        

        main_sizer    = wx.BoxSizer(wx.HORIZONTAL)

        self.CreateBrowsePanel(main_sizer)
        self.CreatePlotPanel(main_sizer)
        self.CreateSamplePanel(main_sizer)

        self.checkboxes = []
        
        self.SetSizer(main_sizer)
        self.Centre()
        
    def CreateBrowsePanel(self,main_sizer):
        sizer = wx.BoxSizer(wx.VERTICAL)
        panel = wx.Panel(self,-1)
        self.filectrl = wx.FileCtrl(panel,wx.ID_ANY,'.')
        load_button_panel = wx.Panel(panel,-1)
        btn_load_file   = wx.Button(load_button_panel,-1,"Load File")
        
        
        sizer.Add(self.filectrl,9,wx.EXPAND)
        sizer.Add(load_button_panel,1,wx.EXPAND)
        
        panel.SetSizer(sizer)
        main_sizer.Add(panel, 2, wx.EXPAND)
        
        self.filectrl.Bind(wx.EVT_FILECTRL_FILEACTIVATED,self.LoadFile)
        btn_load_file.Bind(wx.EVT_BUTTON, self.LoadFile)
        
    def CreatePlotPanel(self,main_sizer):
        sizer = wx.BoxSizer(wx.VERTICAL)
        control_sizer = wx.BoxSizer(wx.HORIZONTAL)
        panel = wx.Panel(self,-1)
        button_panel = wx.Panel(panel,-1)
        self.canvas = CanvasPanel(panel)
        
        btn_save_plot   = wx.Button(button_panel,-1,"Export Image")
        btn_save_csv    = wx.Button(button_panel,-1,"Export CSV")
        legend_chk      = wx.CheckBox(button_panel,-1,"Legend")
        btn_edit_label  = wx.Button(button_panel,-1,"Edit Labels")
        legend_pos_text = wx.StaticText(button_panel,-1,"Location: ",style=wx.ALIGN_RIGHT)
        self.legend_pos      = wx.Choice(button_panel,-1,choices=legend_positions)
        self.legend_pos.SetSelection(0)
        
        btn_save_plot.Bind(wx.EVT_BUTTON, self.SavePlot)
        btn_save_csv.Bind(wx.EVT_BUTTON, self.SaveCSV)
        legend_chk.Bind(wx.EVT_CHECKBOX, self.toggleLegend)
        self.legend_pos.Bind(wx.EVT_CHOICE, self.set_legend_position)
        btn_edit_label.Bind(wx.EVT_BUTTON, self.open_label_dialog)
        
        main_sizer.Add(panel, 3, wx.EXPAND | wx.ALL)
        sizer.Add(self.canvas,6,wx.EXPAND)
        sizer.Add(button_panel,1,wx.EXPAND)
        
        control_sizer.Add(legend_chk,1)
        control_sizer.Add(btn_edit_label,1)
        control_sizer.Add(legend_pos_text,1,wx.ALIGN_RIGHT)
        control_sizer.Add(self.legend_pos,1,wx.ALIGN_LEFT)
        control_sizer.Add(btn_save_plot,1)
        control_sizer.Add(btn_save_csv,1)
        
        button_panel.SetSizer(control_sizer)
        panel.SetSizer(sizer)
        
    def CreateSamplePanel(self,main_sizer):
        sizer   = wx.BoxSizer(wx.VERTICAL)
        sample_selector_sizer = wx.BoxSizer(wx.VERTICAL)
        select_button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        panel = wx.Panel(self,-1)
        select_button_panel = wx.Panel(panel,-1)
        self.samples_select_panel = wx.ScrolledWindow(panel, -1)
        self.samples_select_panel.SetScrollbars(20,20,50,50)
        
        btn_select_all = wx.Button(select_button_panel,-1,"Select All")
        btn_select_none = wx.Button(select_button_panel,-1,"Select None")
        
        btn_select_all.Bind(wx.EVT_BUTTON, self.select_all)
        btn_select_none.Bind(wx.EVT_BUTTON, self.select_none)
        
        main_sizer.Add(panel,1,wx.EXPAND)
        sizer.Add(select_button_panel,0,wx.EXPAND)
        sizer.Add(self.samples_select_panel,1,wx.EXPAND)
        select_button_sizer.Add(btn_select_all,0)
        select_button_sizer.Add(btn_select_none,0)
        
        panel.SetSizer(sizer)
        select_button_panel.SetSizer(select_button_sizer)
        self.samples_select_panel.SetSizer(sample_selector_sizer)
        

    def set_legend_position(self,event):
        self.legend_cur_loc = self.legend_pos.GetSelection()
        self.plot()

    def open_label_dialog(self,event):
        dlg = LabelDialog(self,-1,"Edit Labels").Show()
        
    def choose_sample(self,event):
        name = event.EventObject.GetLabel()
        state = event.EventObject.GetValue()
        for d in self.plotData.plotData:
            if d[0] == name:
                d[2] = state
                self.plot()

    def setLabels(self):
        for d in self.plotData.plotData:
            pass
                
    def toggleLegend(self,event):
        self.legend = not self.legend
        self.plot()

    def plot(self):
        ax = self.canvas.axes
        fig = self.canvas.figure

        renderLabels = []
        for n,d in enumerate(self.plotData.plotData):
            if d[2]:
                renderLabels.append(self.labels[n])
                
        ax.clear()
        ax.set_xlim((250,800))
        ax.set_ylim((0,1))
        for d in self.plotData.plotData:
            if d[2]:
                ax.plot(d[1][0],d[1][1])
        if self.legend:
            ax.legend(renderLabels,prop={'size':12},loc=self.legend_cur_loc)
        ax.set_xlabel('Wavelength, nm')
        ax.set_ylabel('Relative Intensity')

        fig.tight_layout()
        
        self.canvas.canvas.draw()

    

    def select_none(self,event):
        names = []
        for chkbox in self.checkboxes:
            chkbox.SetValue(False)
            name = chkbox.GetLabel()
            names.append(name)
        for d in self.plotData.plotData:
            if d[0] in names:
                d[2] = False
        self.plot()

    def select_all(self,event):
        names = []
        for chkbox in self.checkboxes:
            chkbox.SetValue(True)
            name = chkbox.GetLabel()
            names.append(name)
        for d in self.plotData.plotData:
            if d[0] in names:
                d[2] = True
        self.plot()
    

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

        self.labels = []
        self.names = []
        for d in self.plotData.plotData:
            self.labels.append(d[3])
            self.names.append(d[0])

        
        self.plot()
        
        self.samples_select_panel.DestroyChildren()
        sample_selector_sizer = wx.BoxSizer(wx.VERTICAL)
        self.checkboxes = []

        for n,d in enumerate(self.plotData.plotData):
            chkbox = wx.CheckBox(self.samples_select_panel,-1,d[0])
            self.checkboxes.append(chkbox)
            sample_selector_sizer.Add(chkbox,0)
            chkbox.SetValue(True)
            chkbox.Bind(wx.EVT_CHECKBOX,self.choose_sample)
        self.samples_select_panel.SetSizer(sample_selector_sizer)
        self.Layout()
            
        
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

        savedata = [d for d in self.plotData.plotData if d[2]]
        df = pd.DataFrame()
        for s in savedata:
            name  = s[0]
            names = ["Wavelength: {:s}".format(name),name]
            data  = s[1]
            df1   = pd.DataFrame({names[0]:data[0], names[1]:data[1]})
            df  = pd.concat([df, df1], ignore_index=True,axis=1)

        with wx.FileDialog(self,"Choose Location to Save CSV",
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fdialog:
            if fdialog.ShowModal() == wx.ID_CANCEL:
                return
            pathname = fdialog.GetPath()
            if not pathname.endswith('.csv'):
                pathname += '.csv'
            try:
                print("saving to {:s}.".format(pathname))
                df.to_csv(pathname)
                print("Saved")
                
            except IOError:
                wx.LogError("Cannot save in file {:s}.".format(pathname))
            
        return

                
class MyApp(wx.App):
    def OnInit(self):
        frame = MyFrame(None, -1, 'Spectrum Browser')
        frame.Show(True)
        self.SetTopWindow(frame)
        return True

app = MyApp(0)
app.MainLoop()
