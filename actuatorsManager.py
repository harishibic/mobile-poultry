#IMPORTATION
import RPi.GPIO as GPIO
from csvManager import *
import sys
import os
from components import *
    
#INIT GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False) #Disable warning

if("/" in sys.argv[0]):
    path=sys.argv[0].split("ChickenCoopSystem/")[0]+"ChickenCoopSystem"
else:
    path=os.getcwd()

#FUNCTIONS
def useAct(name,typ,*args): #This  function is called when we want to use the actuators
    #We check the type of the actuator, because the use can be different according to the type
    #To use the actuator, we instantiate the corresponding class and we call the "do" method
    #the "*args" means that we can have additionnal variable arguments
    if(typ=="Servomotor"):
        Servomotor(name).do(args[0])
    elif(typ=="LED"):
        if(len(args)>0): 
            LED(name).do("Auto",args[0])
        else:
            LED(name).do()

def useActWithBluetooth(name): #This function is quite the same than the previous one, but it is called for the bluetooth communication, so when the raspberry
    #receives the data sent by the mobile application, it sends only the name of the corresponding actuator
    #"name" parameter of this function is the data sent by the mobile app
    name=str(name).split("'")[1] #the data sent by bluetooth is byte type, to do processing after, we convert it to a string and split it to retrieve only the name 
    act=retrieveComponentByName(name,"Actuator") #we retrieve all the information of the actuator thanks to its name by calling this function
    typ=act[1] #we need the type of the actuators, which is the 2nd element of the list sent back by the previous function
    state=retrieveActuatorsStatesByName(name) #we also retrieve the state of the current actuator
    if(typ=="Servomotor"):#then it's the same code than before
        Servomotor(name).do(180 if state=="Closed" else 0)
    elif(typ=="LED"):
        LED(name).do()
        
if(not os.path.isfile(path+"/actuatorsStates.csv")): # we check if the actuatorsStates csv file already exists, if it doesn't, then we create it
    initStatesArray=[] #this list contains the states of all the actuators
    actuators=retrieveComponents("Actuator")
    for act in actuators: #we scan all the actuators and according to its use, we write the corresponding state
        if(act[0]=="Door"): #act is the current actuator (for the current iteration), and the first element (act[0]) is its use
            initStatesArray.append("Closed")
        elif(act[0]=="Lights"):
            initStatesArray.append("Off")
    pd.DataFrame(columns=[act[2] for act in actuators],data=[initStatesArray]).to_csv(path+"/actuatorsStates.csv",index=False) #we create the dataframe with all the values which will
    #be into the csv : the name of each actuator as column names, the corresponding state as value


#CRONTAB USES
if(len(sys.argv)==4): #we check the number of arguments when we call this script, this condition allows us to execute all the next code only if the script is run thanks to crontab
    #sys.argv is a list which contains those arguments, the 1st argument is always the name of the script
    actuatorType=sys.argv[1] #we retrieve the corresponding information, so the type, the name and the state of the actuator, from the arguments written in the crontab
    actuatorName=sys.argv[2]
    actuatorState=sys.argv[3]
    if(actuatorType=="Servomotor"): #we check the type of the corresponding actuator, and then we also check the state which is written in arguments
        #we call the function which allow to use the actuator, with the good values according its type
        if(actuatorState=="Opened"):
            useAct(actuatorName,actuatorType,180) #180 is the angle to give to the servomotor, here we consider 180° is opened door and 0° is closed door
        else:
            useAct(actuatorName,actuatorType,0)
    if(actuatorType=="LED"):
        useAct(actuatorName,actuatorType,actuatorState) #we call the useAct function to turn on/off the light according to the state
