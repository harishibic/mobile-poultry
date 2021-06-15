#IMPORTATION
from crontab import CronTab
import subprocess
from csvManager import retrieveActuatorsStatesByName,retrieveActuatorsStates,retrieveComponentsUse
import os
import pandas as pd
from components import *

#FUNCTIONS

user = str(subprocess.check_output('whoami')).split("'")[1].split("\\")[0] 
if("/" in sys.argv[0]):
    path=sys.argv[0].split("ChickenCoopSystem/")[0]+"ChickenCoopSystem"
else:
    path=os.getcwd()

    
def updateCron(openHours,openMinutes,closeHours,closeMinutes,act): 
    cron=CronTab(user=user) 
    if(retrieveActuatorsStatesByName(act[2]) in ("Opened","Closed")): 
        for job in cron: 
            if(job.command.split()[-1]=="Opened"): 
                openJob=job 
            elif (job.command.split()[-1]=="Closed"): 
                closeJob=job

        if(openMinutes != '' and openHours != ''): 
            openJob.minute.on(openMinutes) 
            openJob.hour.on(openHours) 
        if(closeMinutes != '' and closeHours != ''):
            closeJob.minute.on(closeMinutes)
            closeJob.hour.on(closeHours)
        cron.write() 
        
    if(retrieveActuatorsStatesByName(act[2]) in ("On","Off")): 
            for job in cron:
                if(job.command.split()[-1]=="On"):
                    openJob=job
                elif (job.command.split()[-1]=="Off"):
                    closeJob=job

            if(openMinutes != '' and openHours != ''):
                openJob.minute.on(openMinutes)
                openJob.hour.on(openHours)
            if(closeMinutes != '' and closeHours != ''):
                closeJob.minute.on(closeMinutes)
                closeJob.hour.on(closeHours)
            cron.write()

def addCron(name,actOrSens,typ,use,pin,isNew): 
    cron=CronTab(user=user)
    sens=False 
    if(actOrSens=="Actuator"): 
        state=retrieveActuatorsStates()[name][0] 
        if(state in ("Off","On")): 
            onJob=cron.new(command='python3 '+path+'/actuatorsManager.py '+typ+' '+name+' '+"On"+' ',comment=name) 
            offJob=cron.new(command='python3 '+path+'/actuatorsManager.py '+typ+' '+name+' '+"Off"+' ',comment=name) 
        elif(state in ("Opened","Closed")): 
            onJob=cron.new(command='python3 '+path+'/actuatorsManager.py '+typ+' '+name+' '+"Opened"+' ',comment=name)
            offJob=cron.new(command='python3 '+path+'/actuatorsManager.py '+typ+' '+name+' '+"Closed"+' ',comment=name)
    
    elif(actOrSens=="Sensor"): 
        sens=True
        if(isNew): 
            sensJob=cron.new(command='python3 '+path+'/sensorsManager.py '+use,comment=name)

    if(not sens): 
        onJob.hours.on(7)
        offJob.hours.on(19)
    else:
        if(isNew): 
            sensJob.minutes.every(5)
        
    cron.write()

def deleteCron(name,actOrSens,use): 
    cron=CronTab(user=user)
    if(actOrSens=="Actuator"):
        for job in cron:
            if(job.comment==name): 
                cron.remove(job) 
    elif(actOrSens=="Sensor"):
        if(use not in retrieveComponentsUse("Sensor")): 
            for job in cron:
                if(job.comment==use):
                    cron.remove(job)
    cron.write()


    
if(not os.path.exists(path+"/routines.csv")): 
    df=pd.DataFrame(columns=["ID","ActuatorType","ActuatorName","SensorUseName","SensorValue","Operator","ActuatorValue"])
    df.to_csv(path+"/routines.csv",index=False)

        
