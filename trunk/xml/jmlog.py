from numpy import arange
from matplotlib.dates import MinuteLocator, DateFormatter
from csv import reader, writer
from xml.etree import ElementTree
from pylab import *
from datetime import datetime
from time import time
rcParams['font.size'] = 8

class jmlog:
    def __init__(self,path):
        self.data=list()
        self.data.append(("timeStamp","elapsed","Latency","bytes","label","success","allThreads","secFromStart","type"))

        tree = ElementTree.parse(path)
        first = True
        
        for sample in tree.findall("sample"):
            row = list()
            row.append(long(sample.get("ts")))
            row.append(long(sample.get("t")))
            row.append(long(sample.get("lt")))
            row.append(long(sample.get("by")))
            row.append(sample.get("lb"))
            row.append(sample.get("s"))
            row.append(int(sample.get("na")))
            if first:
                start_time = row[0]
                first = False
            row.append(int((row[0]-start_time)/1000))
            row.append("sample")
            elapsedTime=0
            latency=0
            for httpSample in sample.getchildren():                
                subRow = list()
                subRow.append(long(httpSample.get("ts")))
                subRow.append(long(httpSample.get("t")))
                subRow.append(long(httpSample.get("lt")))
                subRow.append(long(httpSample.get("by")))
                subRow.append(httpSample.get("lb"))
                subRow.append(httpSample.get("s"))
                subRow.append(int(httpSample.get("na")))
                subRow.append(int((subRow[0]-start_time)/1000))
                subRow.append("httpSample")
                elapsedTime+=subRow[1]
                latency+=subRow[2]
                self.data.append(subRow)
            row[1]=elapsedTime
            row[2]=latency
            self.data.append(row)

        self.sec_index  =   self.index("secFromStart")
        self.ts_index   =   self.index("timeStamp")
        self.et_index   =   self.index("elapsed")
        self.lt_index   =   self.index("Latency")
        self.b_index    =   self.index("bytes")
        self.lbl_index  =   self.index("label")
        self.err_index  =   self.index("success")
        self.vu_index   =   self.index("allThreads")
        self.type_index =   self.index("type")

        self.labels = list()
        self.transactions = list()
        self.start_time = 0
        self.start = 0
        self.end_time = 0
        for row in range(1,len(self.data)):
            if self.end_time < self.data[row][self.sec_index]:
                self.end_time = self.data[row][self.sec_index]
            if self.data[row][self.type_index] == "httpSample":
                if not self.data[row][self.lbl_index] in self.labels:
                    self.labels.append(self.data[row][self.lbl_index])
            else:
                if not self.data[row][self.lbl_index] in self.transactions:
                    self.transactions.append(self.data[row][self.lbl_index])
               
        self.end = self.end_time
        
    def index(self,column):
        for i in range(len(self.data[0])):
            if self.data[0][i] == column:
                return i

    def log_agg(self, time_int, label, mode):
        prev_step = self.start
        next_step = prev_step+time_int
        points = dict()
        points[prev_step]=0
        
        for i in range(1,len(self.data)):
            if self.data[i][self.sec_index] >= prev_step:
                row = i
                break
        count = 0
        while prev_step < self.end and row < len(self.data):
            if self.data[row][self.sec_index] < next_step:
                if self.data[row][self.lbl_index] == label:
                    if mode == 'bpt':
                        points[prev_step] += self.data[row][self.b_index]
                    elif mode == 'art':
                        points[prev_step] += self.data[row][self.et_index]
                        count += 1
                    elif mode == 'lat':
                        points[prev_step] += self.data[row][self.lt_index]
                        count += 1
                    elif mode == 'rpt':
                        points[prev_step] += 1
                    elif mode == 'err' or mode == 'errc':
                        if self.data[row][self.err_index] == 'false':
                            points[prev_step] += 1
                elif mode == 'vusers':
                    points[prev_step] = self.data[row][self.vu_index]
                elif self.data[row][self.lbl_index] in self.labels:
                    if mode == 'err_total' or mode == 'errc_total':
                        if self.data[row][self.err_index] == 'false':
                            points[prev_step] += 1
                    elif mode == 'bpt_total':
                        points[prev_step] += self.data[row][self.b_index]
                    elif mode == 'rpt_total':
                        points[prev_step] += 1
                
                row += 1
            else:
                if mode == 'errc' or mode == 'errc_total':
                    points[next_step] = points[prev_step]
                elif mode == 'vusers':
                    None
                elif mode == 'art' or mode == 'lat':
                    if count:
                        points[prev_step] /= count
                        count = 0
                    if next_step < self.end:
                        points[next_step] = 0
                else:                            
                    points[prev_step] /= (time_int*1.0)
                    if next_step < self.end:
                        points[next_step] = 0
                prev_step = next_step
                next_step += time_int
        return points

    def trend(self,array = list()):
        ma = list()
        for i in range(5):
            ma.append(array[i])
        for i in range(5,len(array)-5):
            smoothed = 0
            for j in range(i-5,i+5):
                smoothed+=array[j]/10
            ma.append(smoothed)
        for i in range(len(array)-5,len(array)):
            ma.append(array[i])
        return ma

    def save(self,path):
        log_file = open(path,"wb")
        output = writer(log_file)        
        for row in range(len(self.data)):
            current_cow=(self.data[row][self.ts_index],self.data[row][self.et_index],
                self.data[row][self.lbl_index],self.data[row][self.err_index],
                self.data[row][self.b_index],self.data[row][self.lt_index])            
            output.writerow(current_cow)
        log_file.close()
   
    def plot(self, graph = 'bpt_total',time_int = 30, label = None, l_opt = False,ttl=None,trend = False, pnts=False):
        if l_opt:
            ax=subplot(2,1,1)
        else:
            ax=subplot(1,1,1)

        title(ttl)
        points = self.log_agg(time_int, label, graph)

        if graph == 'bpt_total'     : label = 'Total Throughput'
        elif graph == 'rpt_total'   : label = 'Total Hits'
        elif graph == 'err_total'   : label = 'Total Error Rate'
        elif graph == 'errc_total'  : label = 'Total Error Count'

        x=list()
        y=list()
        for key in sorted(points.keys()):
            days = key/86400
            hours = (key-86400*days)/3600
            minutes = (key - 86400*days-3600*hours)/60
            seconds = key - 86400*days-3600*hours-60*minutes
            days+=1
            x.append(datetime(1970, 1, days, hours, minutes, seconds))
            y.append(points[key])
        if pnts:
            plot(x,y,linestyle='solid',marker='.',markersize=5,label = label, linewidth=0.5)
        else:
            plot(x,y,label = label, linewidth=0.5)
        if trend:
            plot(x,self.trend(y),label = label+' (Trend)', linewidth=1)

        grid(True)
        max_min = self.end/60
        min_min = self.start/60
        
        time_int = (int((max_min-min_min)/10.0))/10*10
        if not time_int:
            if max_min>75:
                time_int=10
            else:
                time_int=5
        if time_int > 30:
            time_int = 60

        if time_int<=60:
            xlabel('Elapsed time (hh:mm)')
            ax.xaxis.set_major_locator( MinuteLocator(arange(0,max_min,time_int)))
            ax.xaxis.set_minor_locator( MinuteLocator(arange(0,max_min,time_int/5)))
            ax.xaxis.set_major_formatter( DateFormatter('%H:%M') )
        else:
            xlabel('Elapsed time (dd;hh:mm)')
            labels = ax.get_xticklabels()
            ax.xaxis.set_major_formatter( DateFormatter('%d;%H:%M') )
            setp(labels, rotation=0, fontsize=8)
        if l_opt:
            legend(bbox_to_anchor=(0, -0.2),loc=2,ncol=1)
