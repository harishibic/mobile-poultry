import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import datetime
import os
import sys

if("/" in sys.argv[0]):
    path=sys.argv[0].split("ChickenCoopSystem/")[0]+"ChickenCoopSystem"
else:
    path=os.getcwd()
    
csv_file = path+"/sensorsValues.csv"

if not os.path.exists(path+"/Graphs"):
    os.makedirs(path+"/Graphs")
    
def hour(use,name,unit):
    #Graph displaying humidity for the last 60 minutes
    #How to extract values for last 60 minutes
    #Take all values between current time and current time - 1h

    def dataManipulate(x, y):
        for i in range(x, y):
            if(automatic[i] == 'Automatic'):
                if(lastHour < pd.to_datetime(times[i])):
                    a = times[i].split()
                    a = a[1].split('.')
                    a = a[0].split(':')
                    timesIn60.append(a[0] + ':' + a[1])
                    if(dat[i]=="None" or int(dat[i]) > topDat or int(dat[i]) < lowDat):
                        dat[i] = np.nan
                        tempsIn60.append(dat[i])
                    else: tempsIn60.append(dat[i])
                    ticks.append(a[0] + ':' + a[1])
    #Reading the data from file (working folder)
    data = pd.read_csv(csv_file)

    #Extracting column data into lists
    times = list(data["Time"])
    dat = list(data[use+' '+name])
    automatic = list(data["Auto/Man"])
    #Humidity threshold on DHT11
    #Good for 20-80% humidity readings ±2°C accuracy
    if(use=="Humidity"):
        lowDat = 20
        topDat = 80
    elif(use=="Temperature"):
        lowDat = 0
        topDat = 50


    #Extracting plotting data for last 60 minutes
    lastHour = pd.Timestamp.now() - pd.Timedelta('1 hours')

    #lastHour = pd.to_datetime('2021-03-29 22:50:00.0')


    #n is maximum 24 hour amount of entries 60 times (1 per min) for 24 hours
    ticks = []
    timesIn60 = []
    tempsIn60 = []
    #60 because it's "maximum" amount of records per hour 
    if(len(times)>60):
        dataManipulate(len(times)-60, len(times))
    else: dataManipulate(0,len(times))
    fig = plt.figure(figsize=(14,5))
    ax = fig.add_axes([0.1, 0.15, 0.8, 0.8])
    ax.plot(timesIn60, tempsIn60)

    ax.xaxis.set_major_locator(matplotlib.ticker.FixedLocator(np.linspace(0, len(timesIn60)-1, len(ticks))))
    ax.set_xticklabels(ticks)
    #ax.axes.set_ylim(lowHumidity,topHumidity)
    ax.axes.set_xlim(-1, len(timesIn60))

    plt.xlabel('Time')
    plt.ylabel(use+' '+unit)
    plt.title(use+' for the last 60 minutes ')
    plt.grid()
    plt.savefig(path+"/Graphs/hour"+use+name+"Graph.png")
    os.system("sudo chmod 777 "+path+"/Graphs/hour"+use+name+"Graph.png") 

#daily graph management
def day(use,name,unit):
    
    def dataManipulate(x, y):
        for i in range(x, y):
            if(automatic[i] == 'Automatic'):
                if(lastDay < pd.to_datetime(times[i])):
                    
                    a = times[i].split()
                    a = a[1].split('.')
                    a = a[0].split(':')
                    timesIn24.append(a[0] + ':' + a[1])
                    
                    if(dat[i] > topDat or dat[i] < lowDat):
                        dat[i] = np.nan
                        tempsIn24.append(dat[i])
                    else: tempsIn24.append(dat[i])
                
                    if(i%6 == 0):
                        ticks.append(a[0] + ':' + a[1])
                    else: ticks.append('')



    #Reading the data from file (working folder)
    data = pd.read_csv(csv_file)

    #Extracting column data into lists
    times = list(data["Time"])
    dat = list(data[use+' '+name])
    automatic = list(data["Auto/Man"])



    #Humidity threshold on DHT11
    #Good for 20-80% humidity readings ±2°C accuracy
    if(use=="Humidity"):
        lowDat = 20
        topDat = 80
    elif(use=="Temperature"):
        lowDat = 0
        topDat = 50

    #Extracting plotting data for last 60 minutes
    lastDay = pd.Timestamp.now() - pd.Timedelta('24 hours')

    #lastHour = pd.to_datetime('2021-03-29 00:00:00.0')

    #n is maximum 24 hour amount of entries 60 times (1 per min) for 24 hours
    ticks = []
    timesIn24 = []
    tempsIn24 = []

    #1440 because it's sensors value every 3 minutes (3 * 60 * 24) for 24 hours (the max)
    if(len(times)>1440):
        dataManipulate(len(times)-1440, len(times))
    else: dataManipulate(0,len(times))
        



    fig = plt.figure(figsize=(14,5))
    ax = fig.add_axes([0.1, 0.15, 0.8, 0.8])
    ax.plot(timesIn24, tempsIn24)
    ax.xaxis.set_major_locator(matplotlib.ticker.FixedLocator(np.linspace(0, len(timesIn24)-1, len(ticks))))
    ax.set_xticklabels(ticks)
    #ax.axes.set_ylim(lowHumidity,topHumidity)
    #ax.axes.set_xlim(0,len(timesIn24))
    plt.xlabel('Time')
    plt.ylabel(use+' '+unit)
    plt.title(use+' for the last 24 hours ')
    plt.grid()
    plt.savefig(path+"/Graphs/day"+use+name+"Graph.png")
    os.system("sudo chmod 777 "+path+"/Graphs/day"+use+name+"Graph.png")
    return True

def week(use,name,unit):
    
    def getUnique(list_in, list_out):
        for x in list_in:
            if x not in list_out:
                list_out.append(x)


    def dataManipulate(x, y):
        for i in range(x, y):
            if(lastWeek < pd.to_datetime(times[i])):
                a = times[i].split()
                allDays.append(a[0])
                a = a[1].split('.')
                a = a[0].split(':')
                timesIn7.append(times[i])
                
                
                if(dat[i] > topDat or dat[i] < lowDat):
                    dat[i] = np.nan
                    datIn7.append(dat[i])
                else: datIn7.append(dat[i])
            
                if(i%50 == 0):
                    ticks.append(a[0] + ':' + a[1])
                else: ticks.append('')



    #Reading the data from file (working folder)
    data = pd.read_csv(csv_file)

    #Extracting column data into lists
    times = list(data["Time"])
    dat = list(data[use+' '+name])

    #Humidity threshold on DHT11
    #Good for 20-80% humidity readings ±2°C accuracy
    if(use=="Humidity"):
        lowDat = 20
        topDat = 80
    elif(use=="Temperature"):
        lowDat = 0
        topDat = 50


    #Extracting plotting data for last 7 days
    lastWeek = pd.Timestamp.now() - pd.Timedelta('7 days')

    #lastWeek = pd.to_datetime('2021-03-23 00:00:00.0')

    ticks = []
    timesIn7 = []
    datIn7 = []
    allDays = []
    distinctDays = []

    #10080 because it's sensors value every minute (60 * 24 * 7) for 7 days maximum
    if(len(times)>10800):
        dataManipulate(len(times)-10080, len(times))
        getUnique(allDays, distinctDays)
    else: 
        dataManipulate(0,len(times))
        getUnique(allDays, distinctDays)
        
    #Adding day to the date
    dateToDay = pd.DataFrame({'inputDates': distinctDays})
    dateToDay['inputDates'] = pd.to_datetime(dateToDay['inputDates'])
    dateToDay['dayOfWeek'] = dateToDay['inputDates'].dt.day_name()

    #Converting the date from YYYY-MM-DD format to MM DD, YYYY
    theDate = []
    holder = []
    for i in range(0, len(distinctDays)):
        holder = datetime.datetime.strptime(distinctDays[i], '%Y-%m-%d')
        holder = holder.strftime('%b %d, %Y')
        theDate.append(holder)


    fig = plt.figure(figsize=(14,5))
    ax = fig.add_axes([0.1, 0.15, 0.8, 0.8])
    ax.plot(timesIn7, datIn7)
    ax.xaxis.set_major_locator(matplotlib.ticker.FixedLocator(np.linspace(0, len(timesIn7)-1, len(distinctDays))))
    ax.set_xticklabels(dateToDay['dayOfWeek'] + "\n" + theDate)
    #ax.axes.set_ylim(lowHumidity,topHumidity)

    plt.xlabel('Time')
    plt.ylabel(use+' '+unit)
    plt.title(use+' for the last 7 days')
    plt.grid(axis = 'y')
    plt.savefig(path+"/Graphs/week"+use+name+"Graph.png")
    os.system("sudo chmod 777 "+path+"/Graphs/week"+use+name+"Graph.png")
    return True
