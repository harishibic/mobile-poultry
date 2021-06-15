#IMPORTATION
import RPi.GPIO as GPIO
from csvManager import *
from time import sleep
import Adafruit_DHT

#CLASS DECLARATION

class Routine: #Routine class
    def __init__(self,iD,actuator,sensor,sensorUseName,operator,sensorValue,*args): #this method is the method called at the instantiation of the class, it's the constructor of
        #the class, so we initialize every variable
        self.__id=iD #self.__id is the id class variable, the "__" after the "." means that this variable has the private visibility, so it's directly reachable from this class only
        self.__actuator=actuator
        self.__sensor=sensor
        self.__operator=operator
        self.__sensorValue=sensorValue
        self.__sensorUseName=sensorUseName
        self.__actuatorValue=int(args[0]) if args[0]!="None" else "None" #if the actuator needs a value to be used (like the servomotor which needs an angle value for example)
        #then we take this value, and we cast it into and integer, because in this csv, those values are string type
        #if the actuator doesn't need a value to be used, we juste write "None" and so this variable is also equal to "None" (string type)
        
    #here are the getters and setters of the class : as we put the visiblity of each variable in private, we need them to get their values and to change them from another class
    def getID(self):
        return self.__id
    def getActuator(self):
        return self.__actuator
    def getSensor(self):
        return self.__sensor
    def getOperator(self):
        return self.__operator
    def getSensorValue(self):
        return self.__sensorValue
    def getSensorUseName(self):
        return self.__sensorUseName
    def getActuatorValue(self):
        return self.__actuatorValue
    
    def setID(self,iD):
        self.__id=iD
    def setActuator(self,actuator):
        self.__actuator=actuator
    def setSensor(self,sensor):
        self.__sensor=sensor
    def setOperator(self,operator):
        self.__operator=operator
    def setSensorValue(self,sensorValue):
        self.__sensorValue=sensorValue
    def setSensorUseName(self,sensorUseName):
        self.__sensorUseName=sensorUseName
    def setActuatorValue(self,actuatorValue):
        self.__actuatorValue=actuatorValue
    
    def testRoutine(self): #this is the method called by every routine to use the actuator
        if(self.__actuator[1]=="Servomotor"): #we check the type of the actuator associated to the current routine and according to it, instantiate the correct class
            act=Servomotor(self.__actuator[2])
        else:
            act=LED(self.__actuator[2])
        num=0 #this is for the the sensors which are used for different kinds of values (for example the DHT11 : it's used to measure temperature and humidity)
        use=self.__sensorUseName.split()[0] #sensorUseName is a string with sensor use as first word, and its name as second word, so thanks to the split (which converts the string
        #into an array, according to the specified separator into the parenthesis, the default one is a space) we retrieve the use
        values=self.__sensor.getValues() #values contains the use of the sensor with its associated value (for example "(Humidity, 53%)"
        if(not "None" in values): #if the sensor is well pluged and works well (so it doesn't send back a "None"), then we can execute the action
            for i in range(len(values)): #here is for the sensors which are used for different kinds of values, because if we want to use for example a DHT11 but only for temperature,
                #then we have to check only this value, so we retrieve the index of "values" which corresponds to the correct uses 
                if(values[i][0]==use):
                    num=i
            if(self.__operator=="<=" and values[num][1]<=self.__sensorValue): #from here, we check the operator and if the value of the data verify the condition on the threshold
                #then we check if an actuator value is specified or not, in order to give parameters or not to the "do" method
                if(self.__actuatorValue=="None"):
                    act.do(True) #the True is to know if the "do" method is called from a routine or not, because if not, then we just check the state of the actuator (light state
                    #for example) and we switch to the other state, else we check if the condition about the threshold is verified
                else:
                    act.do(self.__actuatorValue)
            elif(self.__operator==">=" and values[num][1]>=self.__sensorValue):
                if(self.__actuatorValue=="None"):
                    act.do(True)
                else:
                    act.do(self.__actuatorValue)
            elif(self.__operator=="=" and values[num][1]==self.__sensorValue):
                if(self.__actuatorValue=="None"):
                    act.do(True)
                else:
                    act.do(self.__actuatorValue)
            elif(self.__operator=="<" and values[num][1]<self.__sensorValue):
                if(self.__actuatorValue=="None"):
                    act.do(True)
                else:
                    act.do(self.__actuatorValue)
            elif(self.__operator==">" and values[num][1]>self.__sensorValue):
                if(self.__actuatorValue=="None"):
                    act.do(True)
                else:
                    act.do(self.__actuatorValue)
            else:
                """if(self.__actuatorValue=="None"):
                    act.do(False)"""
                if(self.__actuatorValue!="None"):
                    act.do(self.__actuatorValue)


class Component: #this class is a class from which actuators and sensors will inherit, because they have some variables which are the same
    
    def __init__(self,use,typ,name,pins,pwm):
        self.__name=name
        self.__pins=pins
        self.__pwm=pwm
        self.__typ=typ #servomotor/led/motor...
        self.__use=use  #door/window/light...
        GPIO.setmode(GPIO.BCM) #this is to tell to the program that we want to number the pins according to BCM mode (there is another mode which is BOARD mode)

    # all the getters and setters
    def getName(self):
        return self.__name
    def getPins(self):
        return self.__pins
    def getIsPWM(self):
        return self.__pwm
    def getType(self):
        return self.__typ
    def getUse(self):
        return self.__use

    def setName(self,name):
        self.__name=name
    def setPins(self,pins):
        self.__pins=pins
    def setIsPWM(self,pwm):
        self.__pwm=pwm
    def setType(self,typ):
        self.__typ=typ
    def setUse(self,use):
        self.__use=use


class Actuator(Component): #this class inherits from "Component" class, and all the actuator classes will inherit from this one (like LED, servomotor...)

    def __init__(self,name):
        act=retrieveComponentByName(name,"Actuator") #we get all the information about the corresponding actuator from the CSV
        super().__init__(act[0],act[1],act[2],int(act[3]),bool(act[4])) #the "super" method call the parent class constructor, we put all the needed arguments thanks to what we
        #retrieve before
        self.__state=retrieveActuatorsStates()[name][0] #we retrieve the last state of the actuator
        self.__pwm=None #this corresponds to the pwm "signal" of the current actuator, we initialize it to none because it's only for actuators which use pwm 
        GPIO.setup(self.getPins(),GPIO.OUT) #we initialize the setup of the actuator pin, we have to specify that the actuator is an output
        

    #getters and setters
    def getState(self):
        return self.__state

    def getPWM(self):
        return self.__pwm
    
    
    def setPWM(self,pwm):
        self.__pwm=pwm


    def setState(self,state):
        self.__state=state
    
    def do(self,*args): #this method contains only "pass" which does nothing, but it's overrided in the child classes, because every actuator get this method in order to allow
        #the user to use it, override a method means that we "re-write" a parent class method to adapt it to the current clas
        pass


class Sensor(Component): #this class inherits from "Component" class, and all the sensor classes will inherit from this one (like TemperatureHumidity)
    
    def __init__(self,name):
        sens=self.getSensor(name) #we get all the information about the corresponding sensor from the CSV
        super().__init__(sens[0],sens[1],sens[2],int(sens[3]),bool(sens[4])) #same as the actuator class
        self.__values=[] #values is an empty array because it can contains several type of values, indeed some sensors can measure several type of values
        
    #getters
    def getSensor(self,name):
        return retrieveComponentByName(name,"Sensor")
    
    def getValues(self):
        return self.__values
    
    def newValues(self,*args): #this method is called to add new values into the values array
        self.__values.clear()
        for i in range(len(args)): #we add all the values given in argument of the function
            self.__values.append(args[i])
            
    def addValues(self,*args): #this is the same method than before except we don't clear the array. This method is called when we want to add values to the existing values array
        # we call this one when we are in the loop from the second iteration, at the first iteration we call the previous method ("newValues")
        for i in range(len(args)):
                self.__values.append(args[i])


class Servomotor(Actuator): 
        
    def __init__(self,name): 
        super().__init__(name)
        self.setPWM(self.initializeServo(50)) 
        

    def initializeServo(self,frequence): 
        p=GPIO.PWM(self.getPins(),frequence) 
        if(self.getState()=="Closed"): 
            p.start(self.angle_to_percent(0))
        else:
            p.start(self.angle_to_percent(180))
        return p 

    def do(self,angle): 
        self.moveServo(angle) 
        sleep(0.8) 
        self.getPWM().stop()

    def moveServo(self,angle): 
        self.getPWM().ChangeDutyCycle(self.angle_to_percent(angle)) 
        self.setState("Opened" if angle==180 else "Closed")
        updateActuatorsStates(self.getName(),self.getState())
        
    def angle_to_percent(self,angle) : 
        if angle > 180 or angle < 0 :
            return False
        
        #0° = 0.5-1ms and 180° = 2-2.5 ms; for 20ms period time (50 Hz), we compute the duty cycle (time during which we will "send a signal" to the servomotor)
        #by doing 0.5/20 (for 0°) which is equal to 2.5%, but it's theorical so we take 4; we do the same for 180°
        start = 4
        end = 12.5
        ratio = (end - start)/180 #Calcul ratio from angle to percent

        angle_as_percent = angle * ratio
        return start + angle_as_percent


class LED(Actuator): 
    
    def __init__(self,name):
        super().__init__(name)

    def do(self,*args): 
        if(len(args)>0 and args[0]==True): 
            self.digitalOnOffRout()
        elif(len(args)>0 and args[0]=="Auto"): 
            self.digitalOnOff(args[1]) 
        else:
            self.digitalOnOff()
        
    def digitalOnOff(self,*args): 
        if(len(args)>0):
            if(args[0]=="On"):
                GPIO.output(self.getPins(), GPIO.HIGH) 
                self.setState("On")
            else:
                GPIO.output(self.getPins(), GPIO.LOW)
                self.setState("Off")
        else:
            if(GPIO.input(self.getPins())): 
                #LED)
                GPIO.output(self.getPins(), GPIO.LOW) 
                self.setState("Off")
            else:
                GPIO.output(self.getPins(), GPIO.HIGH)
                self.setState("On")
        updateActuatorsStates(self.getName(),self.getState()) 
    
    def digitalOnOffRout(self): 
        if(not GPIO.input(self.getPins())): 
            GPIO.output(self.getPins(),GPIO.HIGH)
            self.setState("On")
            updateActuatorsStates(self.getName(),"On")


class TemperatureHumidity(Sensor): 
    
    def __init__(self,name):
        super().__init__(name)
        sens=self.getSensor(name) 
        uses=sens[0].split("/")
        i=0 
        for use in uses: 
            if(i==0): 
                self.newValues((use,retrieveSensorsValues()[use+' '+sens[2]],"°C" if use=="Temperature" else "%")) 
            else: 
                self.addValues((use,retrieveSensorsValues()[use+' '+sens[2]],"°C" if use=="Temperature" else "%")) 
            i+=1 
    
    def readValues(self): 
        return super().getValues()
    
    def getValues(self): 
        DHT11=Adafruit_DHT.DHT11
        humidity,temperature=Adafruit_DHT.read_retry(DHT11, self.getPins()) 
        
        return (("Humidity",humidity),("Temperature",temperature)) 