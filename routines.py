
from components import *
from csvManager import retrieveRoutines,retrieveComponents
from sensorsManager import listSensors


def getRoutinesList(actuators,sensors): 
    localRoutines=[] 
    routines=retrieveRoutines() 
    for i in range(len(routines)): 
        rout=routines.iloc[i] 
        for act in actuators: 
            if(act[2]==rout["ActuatorName"]):
                actuator=act
        for sens in sensors: 
            if(sens.getName()==rout["SensorUseName"].split()[1]):
                sensor=sens
        localRoutines.append(Routine(rout["ID"],actuator,sensor,rout["SensorUseName"],rout["Operator"],rout["SensorValue"],
                                     rout["ActuatorValue"] if rout["ActuatorValue"]!="None" else "None")) 
    return localRoutines 

if __name__=="__main__": 
    while(True): 
        sensors=listSensors() 
        actuators=retrieveComponents("Actuator") 
        routines=getRoutinesList(actuators,sensors) 
        for rout in routines: 
            rout.testRoutine()

