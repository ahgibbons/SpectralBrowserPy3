# -*- coding: utf-8 -*-
"""
Created on Wed Jun 04 16:03:02 2014

Module parses data from Photal data produced by spectrometer

@author: andrew
"""

import matplotlib.pyplot as plt
import numpy as np
import csv


def splitData(text):
    sections = text.split("ListNo.")
    sections = sections[1:]
    tables = [sec[sec.index("Wavelength,RMeasured data"):] for sec in sections]
    readers = [csv.reader(tableo.split('\n'),delimiter=",") for tableo in tables]
    csvd = [[i for i in reader] for reader in readers]
    
    return csvd



    
def plotSpectraData2():
    ifile = open("PS_PQ_F127_2.csv",'r')
    itext = ifile.read()
    ifile.close()
    sdata = genSpecData(itext)
    
    names = np.unique([s.name for s in sdata])
    for name in names:
        c=0
        fig = plt.figure()
        ax = fig.add_subplot(111)
        for s in sdata:
            if s.name == name:
                ax.plot(s.wavelength,s.rmeasured,label=str(c))
                c+=1
        ax.set_xlabel("Wavelength, nm")
        ax.set_ylabel("Reflectance")
        ax.set_title(name)
        ax.legend()
        plt.savefig(name+".png")
        plt.close()
        print("Finished {:s}".format(name))
        
toPlotA = [("340nm_PS_PQ_35kda_F127",8,340,150),
           ("385nm_PS_PQ_35kda_F127",3,385,105),
           ("395nm_PS_PQ_35kda_F127",8,395,180),
           ("405nm_PS_PQ_35kda_F127",4,405,150)
           ]

toPlotOld = [("340_PS_PQ_2hr_5min",0,340,135),
             ("385_1hr_45min",1,385,105),
             ("395_3hr_mid",3,395,180),
             ("405_2hr_45min_mid",1,405,165)]



def plotActual2():
  
    fig = plt.figure(figsize=(10,4))
    ax = fig.add_subplot(111)
    
    for name,n,w,t in toPlotA:
        c=0
        for s in sdata:
            if s.name == name:
                if c==n:
                    ax.plot(s.wavelength,s.rmeasured,label="{:d} nm, {:d} min".format(w,t))
                c+=1
    ax.set_xlabel("Wavelength, nm")
    ax.set_ylabel("Reflectance")
    ax.set_title("PS-PQ-F127 COS Spectra")
    ax.legend(loc="upper right")
    ax.set_ylim((0,1.2))
    plt.savefig("peak_plot3.png",bbox_inches='tight')
    plt.close()
    #print("Finished {:s}".format(name))
    
def plotActualOld():

    fig = plt.figure(figsize=(10,4))
    ax = fig.add_subplot(111)
    
    for name,n,w,t in toPlotOld:
        c=0
        for s in sdata_old:
            if s.name == name:
                if c==n:
                    ax.plot(s.wavelength,s.rmeasured,label="{:d} nm, {:d} min".format(w,t))
                c+=1
    ax.set_xlabel("Wavelength, nm")
    ax.set_ylabel("Reflectance")
    ax.set_title("PS-PQ COS Spectra")
    ax.legend(loc="upper right")
    ax.set_ylim((0,1.2))
    plt.savefig("peak_plot3_old.png",bbox_inches='tight')
    plt.close()
    
def load_data():
    ifile = open("used_samples.csv",'r')
    itext = ifile.read()
    ifile.close()
    sdata = genSpecData(itext)
    
    ifile2 = open("340_2hr_15min.csv",'r')
    itext2 = ifile2.read()
    ifile2.close()
    sdata2 = genSpecData(itext2)[0]
    sdata.append(sdata2)
    return sdata    

def used_data():
    sdata = load_data()
    new_data = []
    for name,n,w,_ in toPlotA:
        c=0
        for s in sdata:
            if s.name == name:
                if c==n:
                    s.irwavelength = w
                    new_data.append(s)
                c+=1
    return new_data

def expansionFactor(sdata):
    peaks = findPeaks(sdata)
    ws,_ = zip(*peaks)
    ws = np.array(ws,dtype='float64')
    iws = [s.irwavelength for s in sdata]
    wavelengthExpansion = ws/iws
    return wavelengthExpansion

def findPeaks(sdata):
    return [(s.wavelength[s.rmeasured==max(s.rmeasured)][0],max(s.rmeasured)) for s in sdata]
    
def peaksPlot(sdata,peaks):
    for s in sdata:
        plt.plot(s.wavelength,s.rmeasured)
    xs,ys = zip(*peaks)
    plt.scatter(xs,ys)
        
    
def plotSpectraData3():
    ifile = open("used_samples.csv",'r')
    itext = ifile.read()
    ifile.close()
    sdata = genSpecData(itext)
    
    names = np.unique([s.name for s in sdata])
    for name in names:
        c=0
        fig = plt.figure()
        ax = fig.add_subplot(111)
        for s in sdata:
            if s.name == name:
                ax.plot(s.wavelength,s.rmeasured,label=str(c))
                c+=1
        ax.set_xlabel("Wavelength, nm")
        ax.set_ylabel("Reflectance")
        ax.set_title(name)
        ax.legend()
        plt.savefig("used_samples/"+name+".png")
        plt.close()
        print("Finished {:s}".format(name))
                   

def dataNames(text):
    sections = text.split("ListNo.")[1:]
    names = []
    for section in sections:
        lines = section.split('\n')
        name=''
        for line in lines:
            listno = lines[0]
            if line.startswith('Sample name,'):
                name = line.split(',')[1]
                names.append((name+"(ListNo.{:s})".format(listno)).replace('\r',''))
    return names
    
def genSpecData(text):
    data = splitData(text)
    names = dataNames(text)
    sdata = [SpectralData(d) for d in data]
    for n,s in enumerate(sdata):
        s.rmeasured = np.array(s.rmeasured,dtype='float64')
        s.wavelength = np.array(s.wavelength,dtype='float64')
        s.name = names[n]
    return sdata

    
class SpectralData:
    def __init__(self,data,name=""):
        tdata = list(zip(*data[1:-2]))
        self.wavelength = tdata[0]
        self.rmeasured = tdata[1]
        self.rreferenceDark = tdata[2]
        self.rreferenceSignal = tdata[3]
        self.rsampleDark = tdata[4]
        self.rsamplesignal=tdata[5]
 
