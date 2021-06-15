import os
import sys
from csvManager import *
from components import *

if("/" in sys.argv[0]):
    path=sys.argv[0].split("ChickenCoopSystem/")[0]+"ChickenCoopSystem"
else:
    path=os.getcwd()
    

def listSensors(): 
    sens=[] 
    for i in range(len(retrieveComponents("Sensor"))): 
        if(retrieveComponents("Sensor")[i][0]=="Temperature/Humidity"): 
            sens.append(TemperatureHumidity(retrieveComponents("Sensor")[i][2])) 
    return sens

def updateBluetooth(): 
    sensors=listSensors() 
    new=True 
    for sens in sensors: 
        values=sens.getValues() 
        if(isinstance(sens,TemperatureHumidity)):
            humidity=values[0][1] 
            temperature=values[1][1] 
            if humidity is None: 
                humidity="None"
            if temperature is None:
                temperature="None"
            addSensorsValues(sens.getUse(),sens.getName(),str(temperature),str(humidity),False,new) 
            sens.newValues(("Temperature",temperature," °C")) 
            sens.addValues(("Humidity",humidity," %"))
        new=False 
        
        
if(not os.path.isfile(path+"/sensorsValues.csv")): 
    df=pd.DataFrame([["None","None"]],columns=["Time","Auto/Man"])
    for sens in retrieveComponents("Sensor"): 
        for splitted in sens[0].split("/"):
            df[splitted+" "+sens[2]]="None" 
    df.to_csv(path+"/sensorsValues.csv",index=False) 
           
    
    
if(len(sys.argv)==2): 
    new=True
    use=sys.argv[1] 
    for sens in retrieveComponents("Sensor"): 
        if(sens[0]==use): 
            if(use=="Temperature/Humidity"):
                sensor=TemperatureHumidity(sens[2])
                values=sensor.getValues()
                humidity=values[0][1]
                temperature=values[1][1]
                if humidity is None:
                    humidity="None"
                if temperature is None:
                    temperature="None"
                addSensorsValues(sensor.getUse(),sensor.getName(),str(temperature),str(humidity),True,new)
                new=False


