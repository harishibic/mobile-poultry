import pandas as pd
import datetime
import os
import sys
from dateutil.relativedelta import relativedelta
from tkinter import *

if("/" in sys.argv[0]):
    path=sys.argv[0].split("ChickenCoopSystem/")[0]+"ChickenCoopSystem"
else:
    path=os.getcwd()
#from csvManager import *
#csv_file="path+"/sensorsValues.csv"
csv_file = 'try_again2.csv'
data = pd.read_csv(csv_file)


#CleanData function serves as a 'cleanup' function which deletes all records older than 2 months
def cleanData():
    #Getting current and last month to delete everything that's different than them
    #Pandas library is used to retrieve current time and dt.month to get the month as integer
    currentMonth = pd.Series(pd.Timestamp.now()).dt.month[0]
    #Relativedelta is used so we can subtract months from January and get December (January -1 = 12)
    lastMonth = pd.Series(pd.Timestamp.now() - relativedelta(months=1)).dt.month[0]
    for i in range(0, len(data['Time'])):
        #current month is 2 and last is current -1
        #this checks if the month is different than last 2 months and drops the value if it is
        if(pd.Series(pd.to_datetime(data['Time'][i])).dt.month[0] != currentMonth and pd.Series(pd.to_datetime(data['Time'][i])).dt.month[0] != lastMonth):
            data.drop([i],axis=0,inplace=True)
        else:
            break
    #We reset the indexes here and save the csv    
    data.reset_index(drop=True, inplace=True)
    data.to_csv('new.csv',index=False)
    #put "csv_file" instead of "new.csv" 
    

#getUnique function returns unique items from list
def getUnique(list_in, list_out):
   for x in list_in:
      if x not in list_out:
         list_out.append(x)
         
#exportLastMonth exports all the values from last month in a folder into each separate file
def exportLastMonth(device):
    #We take current timestamp and go back one month to use as threshold
    lastMonth = pd.Series(pd.Timestamp.now() - relativedelta(months=1)).dt.month[0]

    #Here we drop all the data that's different than lastMonth
    for i in range(0, len(data['Time'])):
        if(pd.Series(pd.to_datetime(data['Time'][i])).dt.month[0] != lastMonth):
            data.drop([i], axis=0, inplace = True)
    data.reset_index(drop=True, inplace=True)

    #Here we check if there is any data in lastMonth matching month data
    #If there's not we just print there's not enough data
    if(len(data) > 0):
        #Convert data datetimes to days with '.dt.day'
        allDays = pd.Series(pd.to_datetime(data['Time'])).dt.day
        uniqueDays = []
        #Then using getUnique retrieve all unique days
        getUnique(allDays, uniqueDays)

        #This is used for naming the files, we split to retrieve date
        a = data['Time'][0].split()
        b = a[0][:8]
        
        rootName="/media/pi/"+str(device)+"/"
        myDirectory = rootName+a[0][:7]
        #Check if the folder with same name exists, delete it if it does and then create a new one
        if os.path.exists(myDirectory):
            shutil.rmtree(myDirectory)
        os.makedirs(myDirectory)
        print(f"Starting the export for {b}")
        #Takes all matching values day by day and exports them to a single .csv
        for x in uniqueDays:
            holder = pd.DataFrame()
            for i in range (0, len(data)):
                if(int(pd.Series(pd.to_datetime(data['Time'][i])).dt.day) == x):
                    holder = holder.append(data[i:i+1], ignore_index = True)
            print(f"Exporting  {b}{str(x)}")
            holder.to_csv(f'{myDirectory}/{b}{str(x)}.csv', index = False)
        print("Export successful!")
    else: print("Insufficient data")


#exportThisMonth function allows us to export one or more days from current month day-by-day into separate csvs
def exportThisMonth(device,startDate, endDate,frame):
    #get current month so you can export last month (integer April = 4)
    #we do relativedelta -2 bc last data is in February
    
    #currentMonth = pd.Series(pd.Timestamp.now()).dt.month[0] #final use
    currentMonth = pd.Series(pd.Timestamp.now() - relativedelta(months=2)).dt.month[0]
    try:
        startDate=int(startDate)
        endDate=int(endDate)
        #Check if dates are valid and if endDate is smaller/equal to today's date
        if(startDate <= endDate and startDate > 0 and endDate <= pd.Series(pd.Timestamp.now()).dt.day[0]):
            for i in range(0, len(data)):
                if(pd.Series(pd.to_datetime(data['Time'][i])).dt.month[0] != currentMonth):
                    data.drop([i], axis=0, inplace = True)
            data.reset_index(drop=True, inplace=True)
    
            #Similar to before, we repeat the same step for the days in current month
            if(len(data) > 0):
                allDays = pd.Series(pd.to_datetime(data['Time'])).dt.day
                uniqueDays = []
                getUnique(allDays, uniqueDays)

                a = data['Time'][0].split()
                b = a[0][:8]
                rootName="/media/pi/"+str(device)+"/"
                myDirectory = rootName+a[0][:7]
                #shutil.copy("sensorsValues.csv",rootName+device)
                if os.path.exists(myDirectory):
                    shutil.rmtree(myDirectory)
                os.makedirs(myDirectory)
                print(f"Starting the export from {b}{startDate} to {b}{endDate}")
                for x in range(startDate, endDate + 1):
                    holder = pd.DataFrame()
                    for i in range (0, len(data)):
                        if(int(pd.Series(pd.to_datetime(data['Time'][i])).dt.day) == x):
                            holder = holder.append(data[i:i+1], ignore_index = True)
                    print(f"Exporting  {b}{str(x)}")
                    holder.to_csv(f'{myDirectory}/{b}{str(x)}.csv', index=False)
                print("Export successful!")
            else: print("Insufficient data")
        else:
            Label(frame,text="Enter correct values for days",fg="red",name="failedLabel").grid(row=4,column=1)
    except:
        Label(frame,text="Enter integer",fg="red",name="failedLabel").grid(row=4,column=1)




"""startDate = 3
endDate = 6"""
"""if(startDate <= endDate and startDate > 0 and endDate <= pd.Series(pd.Timestamp.now()).dt.day[0]):
    exportThisMonth(startDate, endDate)"""
#cleanData()
#exportLastMonth()

"""if(len(sys.argv)>1): #crontab to add
    cleanData()"""


