#IMPORTATION
import os
import csv
from datetime import datetime
import pandas as pd
import sys

if("/" in sys.argv[0]):
    path=sys.argv[0].split("ChickenCoopSystem/")[0]+"ChickenCoopSystem"
else:
    path=os.getcwd()


#FUNCTIONS
def retrieveComponentByName(name,actuatorOrSensor): 
    nameFile=path+"/components.csv"
    if(os.path.isfile(nameFile)): 
        with open(nameFile,newline='') as file: 
            reader=csv.reader(file,delimiter=',') 
            data=list(reader) 
        for i in range(1,len(data)): 
            if(data[i][-1]==actuatorOrSensor and data[i][2]==name): 
                return data[i]
    return "" 


def addSensorsValues(*args): 
    nameFile=path+"/sensorsValues.csv"
    automatic=args[-2] 
    use=args[0].split("/") 
    name=args[1]
    if(os.path.isfile(nameFile)): 
        df=pd.read_csv(nameFile) 
        if(args[-1] and df.iloc[len(df)-1]["Time"]!="None"): 
            df.at[len(df),"Time"]=datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
            df.at[len(df)-1,"Auto/Man"]="Automatic" if automatic else "Manual" 
            for i in range(len(use)): 
                df.at[len(df)-1,use[i]+" "+name]=args[2+i]
        else: 
            df.at[len(df)-1,"Time"]=datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
            df.at[len(df)-1,"Auto/Man"]="Automatic" if automatic else "Manual"
            for i in range(len(use)):
                df.at[len(df)-1,use[i]+" "+name]=args[2+i]
        df.to_csv(nameFile,index=False) 
            
    return True

def updateActuatorsStates(actuatorName,actuatorState): 
    nameFile=path+"/actuatorsStates.csv"
    if(os.path.isfile(nameFile)):
        df=pd.read_csv(nameFile) 
        df[actuatorName.capitalize()]=actuatorState 
        df.to_csv(nameFile,index=False) 
                
    return True

def addNewComponent(use,typ,name,pin,isPwm,actOrSens):
    nameFile=path+"/components.csv"
    if(os.path.isfile(nameFile)):
        with open(nameFile,newline='') as file: 
            reader=csv.reader(file,delimiter=',')
            data=list(reader)
        for i in range(1,len(data)):
            if(name == data[i][2]): 
                return False
        with open(nameFile, 'a',newline='') as file:
            writer = csv.writer(file, delimiter=',') 
            writer.writerow([use,typ,name,pin,isPwm,actOrSens]) 
            
    return True

def retrieveComponents(ActuatorOrSensor): 
    nameFile=path+"/components.csv"
    components=[] 
    if(os.path.isfile(nameFile)):
        with open(nameFile,newline='') as file:
            reader=csv.reader(file,delimiter=',')
            data=list(reader)
        for i in range(1,len(data)):
            if(data[i][-1]==ActuatorOrSensor): 
                components.append(data[i])
    return components 


def retrieveComponentsUse(ActuatorOrSensor): 
    nameFile=path+"/components.csv"
    components=[] 
    if(os.path.isfile(nameFile)):
        with open(nameFile,newline='') as file:
            reader=csv.reader(file,delimiter=',')
            data=list(reader)
        for i in range(1,len(data)):
            if(data[i][-1]==ActuatorOrSensor and data[i][0] not in components):
                components.append(data[i][0])
    return components 


def addState(use,name): 
    df=pd.read_csv(path+"/actuatorsStates.csv") 
    if(use=="Door"): 
        df[name]="Closed"
    elif(use=="Lights"):
        df[name]="Off"
    df.to_csv(path+"/actuatorsStates.csv",index=False)

def addSensorValueColumn(*args): 
    #d'un nouveau capteur
    df=pd.read_csv(path+"/sensorsValues.csv")
    use=args[0].split("/") 
    name=args[1]
    for i in range(len(use)):
        df[use[i]+" "+name]="None"
    df.to_csv(path+"/sensorsValues.csv",index=False)
    
def retrieveActuatorsStatesByName(name): 
    nameFile=path+"/actuatorsStates.csv"
    if(os.path.isfile(nameFile)):
        return pd.read_csv(nameFile)[name][0]
    
def retrieveAllComponents(): 
    return pd.read_csv(path+"/components.csv")
    
def retrieveActuatorsStates():
    nameFile=path+"/actuatorsStates.csv"
    if(os.path.isfile(nameFile)):
        return pd.read_csv(nameFile)
    else:
        return False

def retrieveSensorsValues(): 
    nameFile=path+"/sensorsValues.csv"
    if(os.path.isfile(nameFile)):
        return pd.read_csv(nameFile).iloc[-1]
    
def retrieveAllSensorsValues(): 
    nameFile=path+"/sensorsValues.csv"
    if(os.path.isfile(nameFile)):
        return pd.read_csv(nameFile)
    
def retrieveUsedPins(): 
    nameFile=path+"/components.csv"
    usedPins=[] 
    if(os.path.isfile(nameFile)):
        with open(nameFile,newline='') as file:
            reader=csv.reader(file,delimiter=',')
            data=list(reader)
        for i in range(1,len(data)):
            usedPins.append(int(data[i][3])) 
    return usedPins

def retrieveRoutines(): 
    nameFile=path+"/routines.csv"
    if(os.path.isfile(nameFile)):
        return pd.read_csv(nameFile)

def updateRoutine(routine,threshold,op,actValue,doneLabel): 
    #à l'actionneur
    nameFile=path+"/routines.csv"
    try: 
        int(threshold)
        if(os.path.isfile(nameFile)):
            df=pd.read_csv(nameFile)
            for i in range(len(df)): 
                if(df.iloc[i]["ID"]==routine["ID"]): 
                    df.at[i,"SensorValue"]=threshold 
                    df.at[i,"Operator"]=op
                    if(actValue!=""): 
                        df.at[i,"ActuatorValue"]=actValue
            doneLabel.config(text="Routine well updated",fg="green")
            df.to_csv(nameFile,index=False)
    except:
        doneLabel.config(text="Wrong value",fg="red")
    doneLabel.grid(row=8,column=2) 

def addRoutine(actuator,sensor,sensorUse,threshold,operator,actValue,done): 
    nameFile=path+"/routines.csv"
    if(os.path.exists(nameFile)):
        df=pd.read_csv(nameFile) 
        iD=[actuator[2],sensorUse,sensor.getName(),str(int(df.iloc[len(df)-1]["ID"].split("_")[-1])+1) if(len(df)>0) else str(0)] 
        df.loc[len(df)]=["_".join(iD),actuator[1],actuator[2],sensorUse+' '+sensor.getName(),threshold,operator,actValue if actValue!= "" else "None"] 
        df.to_csv(nameFile,index=False)
        done.grid(row=8,column=2) 
 


def deleteRoutine(routine): 
    nameFile=path+"/routines.csv"
    if(os.path.isfile(nameFile)):
        df=pd.read_csv(nameFile)
        for i in range(len(df)): 
            df.drop(df.loc[df["ID"]==routine["ID"]].index,inplace=True)
        df.to_csv(nameFile,index=False)
                      
pins=[17,27,22,5,6,26,23,24,25,16]
pwmPins=[12,13]


if(not os.path.isfile(path+"/components.csv")):
    with open(path+"/components.csv",'w',newline='') as file:
            c=csv.writer(file,delimiter=',')
            c.writerow(["Use","Type","Name","Pin","PWM","Actuator/Sensor"])
            c.writerow(["Door","SG90","Door1",13,True,"Actuator"])
            c.writerow(["Lights","LED","Light1",17,False,"Actuator"])
            c.writerow(["Temperature/Humidity","DHT11","Inside",23,False,"Sensor"])
