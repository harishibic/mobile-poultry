
from tkinter import *
import RPi.GPIO as GPIO 
from time import sleep
from csvManager import *
from actuatorsManager import useAct
from sensorsManager import listSensors
from programManager import *
from graphsManager import *
from components import *

import subprocess
import shutil
import psutil
from PIL import Image as Img,ImageTk as ImgTk
import os
from export import *

#FUNCTIONS    
def changeFrame(frame,layerNum):
    if(layerNum==1): 
        L=[frame2,frame3,frame4,frame5,frame6,frame7,frame8,frame9,frame10,frame11,frame12,frame13,frame14,frame15,frame16,frame17]
        for i in L: 
            if(i!=frame):
                i.grid_forget()
                window.update()
        for widget in frame.winfo_children(): 
            if(widget.winfo_name()=="doneLabel"):
                widget.grid_forget()
        updateFrames()
        frame.grid(row=1,column=2,padx=5,pady=5) 
    elif(layerNum==2): 
        L=[frame6,frame7,frame9,frame10,frame11,frame15,frame17]
        for i in L:
            if(i!=frame):
                i.grid_forget()
                window.update()
        for widget in frame.winfo_children():
            if(widget.winfo_name()=="doneLabel" or widget.winfo_name()=="failedLabel"):
                widget.grid_forget()
        updateFrames()
        frame.grid(row=1,column=3,padx=5,pady=5)
        
    window.update()

def updateValues(): 
    new=True
    for sens in sensors:
        if(type(sens)==TemperatureHumidity):
            values=sens.getValues()
            humidity=values[0][1]
            temperature=values[1][1]
            if humidity is None:
                humidity="None"
            if temperature is None:
                temperature="None"
            for index in range(len(frame3.winfo_children())): 
                if(frame3.winfo_children()[index].winfo_name()==sens.getUse().split("/")[1].lower()+" "+sens.getName().lower()): 
                    frame3.winfo_children()[index].config(text=str(humidity)+" %")
                elif(frame3.winfo_children()[index].winfo_name()==(sens.getUse().split("/")[0].lower()+" "+sens.getName().lower())):
                    frame3.winfo_children()[index].config(text=str(temperature)+" °C")
            addSensorsValues(sens.getUse(),sens.getName(),str(temperature),str(humidity),False,new) 
            sens.newValues(("Temperature",temperature," °C")) 
            sens.addValues(("Humidity",humidity," %"))
            new=False
    updateFrames() 
    
def saveChanges(frame,openingHours,openingMinutes,closingHours,closingMinutes,act): 
    updateCron(openingHours,openingMinutes,closingHours,closingMinutes,act) 
    doneLabel=Label(frame,text='Data well saved',fg='green',name="doneLabel",width=15,font=("Courier", 20)).grid(row=len(actuators)*5,column=3) 

    window.update()
def export(): 
    changeFrame(frame4,1) 
    devices=retrieveDevicesList() 
    for i in range(len(devices)): 
        Button(frame4,text=devices[i],command=lambda:exportFilesIntoSelectedDevice(devices[i]),background="#51c4d3",relief="groove",highlightbackground="#51c4d3",width=15,font=("Courier", 20)).grid(row=i+1,column=2,pady=5)
        
def retrieveDevicesList():
    user = str(subprocess.check_output('whoami')).split("'")[1].split("\\")[0] 
    partitions=psutil.disk_partitions() 
    names=[]
    rootName="/media/"+user+"/" 
    for disk in partitions: 
        if(disk.mountpoint.find(rootName)!=-1): 
            names.append(disk.mountpoint.split(rootName)[1]) 
    return names 
    
    
    
def exportFilesIntoSelectedDevice(device): 
    changeFrame(frame11,2) 
    Label(frame11,text="Select the days of the current month you want to export : ",background="#d8e3e7",highlightbackground="#d8e3e7",width=15,font=("Courier", 20)).grid(row=1,column=1)
    Label(frame11,text="From ",background="#d8e3e7",highlightbackground="#d8e3e7",width=15,font=("Courier", 20)).grid(row=1,column=2)
    fromDate=Entry(frame11,width=3,background="#d8e3e7",highlightbackground="#d8e3e7",font=("Courier", 20)) 
    fromDate.grid(row=1,column=3)
    Label(frame11,text="To ",background="#d8e3e7",highlightbackground="#d8e3e7",width=15,font=("Courier", 20)).grid(row=1,column=4)
    toDate=Entry(frame11,width=2,background="#d8e3e7",highlightbackground="#d8e3e7",font=("Courier", 20)) 
    toDate.grid(row=1,column=5)
    Button(frame11,text="Last month",command=lambda:exportLastMonth(device),background="#51c4d3",relief="groove",highlightbackground="#51c4d3",width=15,font=("Courier", 20)).grid(row=2,column=1,pady=5) 
    Button(frame11,text="Export",command=lambda:exportThisMonth(device,fromDate.get(),toDate.get(),frame11),background="#51c4d3",relief="groove",highlightbackground="#51c4d3",width=15,font=("Courier", 20)).grid(row=3,column=1,pady=5) 

    
def submitAdd(win,use,inputType,inputName,isPwm,actOrSens): 
    win.destroy() 
    availablePins=[] 
    usedPins=retrieveUsedPins() 
    if(not isPwm): 
        for pin in pins: 
            if(pin not in usedPins and pin not in pwmPins): 
                availablePins.append(pin) 
    else: 
        for pin in pwmPins: 
            if(pin not in usedPins): 
                availablePins.append(pin) 
    if(len(availablePins)>0): 
        chosenPin=availablePins[0]
    else: 
        chosenPin=""
    if(chosenPin==""): 
        messagebox.showinfo("Selected Pin","No pin available")
        return

    isNew=use not in retrieveComponentsUse("Sensor") 
    isCreated=addNewComponent(use,inputType,inputName.capitalize(),chosenPin,isPwm,actOrSens)
    if(isCreated):
        messagebox.showinfo("Selected Pin","Your pin is : "+str(chosenPin)) 
        if(actOrSens=="Actuator"): 
            addState(use,inputName.capitalize()) 
            global actuators 
            actuators=retrieveComponents("Actuator") 
        else: 
            addSensorValueColumn(use,inputName.capitalize()) 
            if(use=="Temperature/Humidity"):
                sensors.append(TemperatureHumidity(inputName))
        updateFrames() 
        addCron(inputName.capitalize(),actOrSens,inputType,use,chosenPin,isNew) 
    else:
        messagebox.showinfo("Erreur","Nom déjà utilisé")
        
def updateFrames(): 
    global comp 
    frames=[frame2,frame3,frame6,frame7,frame9,frame10,frame12,frame13,frame14,frame15,frame16] 
    comp=retrieveAllComponents() 
    for frame in frames: 
        for wid in frame.winfo_children(): 
            wid.destroy()
        frameContent(frame) 
    window.update()
    
        
    
def newWindow(actOrSens,use): 
    inputWin=Toplevel() 
    inputWin.config(background="#d8e3e7")
    #frameWin=Frame(inputWin,background="#d8e3e7",relief="groove").pack()
    isChecked=BooleanVar() 
    Label(inputWin,text="Type",background="#d8e3e7",highlightbackground="#d8e3e7",width=15,font=("Courier", 20)).grid(row=1,column=1) 
    inputType=Entry(inputWin,background="#d8e3e7",highlightbackground="#d8e3e7",width=15,font=("Courier", 20)) 
    inputType.grid(row=1,column=2,pady=5) 
    Label(inputWin,text="Name",background="#d8e3e7",highlightbackground="#d8e3e7",width=15,font=("Courier", 20)).grid(row=2,column=1)
    inputName=Entry(inputWin,background="#d8e3e7",highlightbackground="#d8e3e7",width=15,font=("Courier", 20))
    inputName.grid(row=2,column=2,pady=5)
    Label(inputWin,text="PWM",background="#d8e3e7",highlightbackground="#d8e3e7",width=15,font=("Courier", 20)).grid(row=3,column=1)
    pwmButton=Checkbutton(inputWin,text="Yes",variable=isChecked,background="#d8e3e7",highlightbackground="#d8e3e7",pady=5,width=15,font=("Courier", 20)) 
    pwmButton.grid(row=3,column=2)
    Button(inputWin,text="Submit",command=lambda:submitAdd(inputWin,use,inputType.get(),inputName.get(),isChecked.get(),actOrSens),background="#51c4d3",relief="groove",highlightbackground="#51c4d3",width=15,font=("Courier", 20)).grid(row=4,column=2,pady=5) 
    

def displayGraph(use,name,nameGraph,*args): 
    img.clear() 
    unit="%" if use=="Humidity" else "°C" 
    if(nameGraph=="hour"): 
        hour(use,name,unit)
    elif(nameGraph=="day"):
        day(use,name,unit)
    elif(nameGraph=="week"):
        week(use,name,unit)
    image=Img.open(os.getcwd()+"/Graphs/"+nameGraph+use+name+"Graph.png") 
    if(len(args)==0): 
        winTest=Toplevel(window) 
        frameImg=Frame(winTest,background="#d8e3e7",relief="groove") 
    else:
        frameImg=args[0] 
        for widget in frameImg.winfo_children(): 
            widget.destroy()
    photo=ImgTk.PhotoImage(image) 
    img.append(photo) 
    frameImg.grid(row=1,column=2,pady=1) 
    canvas = Canvas(frameImg, width = image.size[0], height =image.size[1]) 
    canvas.create_image(0,0, anchor = NW, image=photo) 
    canvas.grid(row=1,column=1,columnspan=3,pady=1)
    Button(frameImg,text="Last hour",command=lambda:displayGraph(use,name,"hour",frameImg),background="#51c4d3",relief="groove",highlightbackground="#51c4d3",width=15,font=("Courier", 20)).grid(row=2,column=1,pady=5) 
    Button(frameImg,text="Last 24 hours",command=lambda:displayGraph(use,name,"day",frameImg),background="#51c4d3",relief="groove",highlightbackground="#51c4d3",width=15,font=("Courier", 20)).grid(row=2,column=2,pady=5)
    Button(frameImg,text="Last week ",command=lambda:displayGraph(use,name,"week",frameImg),background="#51c4d3",relief="groove",highlightbackground="#51c4d3",width=15,font=("Courier", 20)).grid(row=2,column=3,pady=5)
    window.update()


def decorator(function): 
    function 
    updateFrames()

def frameContent(frame,*args): 
    if(frame.winfo_name()=="actuatorsFrame"): 
        for u in range(len(actuators)): 
            Label(frame,text=actuators[u][2]+' : ',background="#d8e3e7",highlightbackground="#d8e3e7",font=("Courier", 20)).grid(row=u,column=1) 
            if(actuators[u][1]=="Servomotor"): 
                Button(frame,text="Open/Close",command=lambda u=u: decorator(useAct(actuators[u][2],actuators[u][1],180 if retrieveActuatorsStatesByName(actuators[u][2])=="Closed" else 0)),background="#51c4d3",relief="groove",highlightbackground="#51c4d3",width=15,font=("Courier", 20)).grid(row=u,column=2,padx=5,pady=5)
                Label(frame,text="State : "+retrieveActuatorsStatesByName(actuators[u][2]),name=actuators[u][2].lower(),background="#d8e3e7",highlightbackground="#d8e3e7",font=("Courier", 20)).grid(row=u,column=3,pady=5) 
            elif(actuators[u][1]=="LED"): 
                Button(frame,text="On/Off",command=lambda u=u:decorator(useAct(actuators[u][2],actuators[u][1])),background="#51c4d3",relief="groove",highlightbackground="#51c4d3",width=15,font=("Courier", 20)).grid(row=u,column=2,padx=5,pady=5)
                Label(frame,text="State : "+retrieveActuatorsStatesByName(actuators[u][2]),name=actuators[u][2].lower(),background="#d8e3e7",highlightbackground="#d8e3e7",font=("Courier", 20)).grid(row=u,column=3,pady=5)
                
    elif(frame.winfo_name()=="sensorsFrame"): 
        for h in range(len(sensors)):
            for j in range(len(sensors[h].readValues())): 
                Label(frame,text=sensors[h].readValues()[j][0]+" "+sensors[h].getName()+" : ",background="#d8e3e7",highlightbackground="#d8e3e7",font=("Courier", 20)).grid(row=j+h*len(sensors[h].readValues()),column=1) 
                Label(frame,text=str(sensors[h].readValues()[j][1])+" "+sensors[h].readValues()[j][2],background="#d8e3e7",highlightbackground="#d8e3e7",font=("Courier", 20)).grid(row=j+h*len(sensors[h].readValues()),column=2) 
                Button(frame,text="Display graph",command=lambda h=h,j=j:displayGraph(sensors[h].readValues()[j][0],sensors[h].getName(),"hour"),background="#51c4d3",relief="groove",highlightbackground="#51c4d3",width=15,font=("Courier", 20)).grid(row=j+h*len(sensors[h].readValues()),column=3,padx=5,pady=5)
                
            updateButton=Button(frame,command=updateValues,text="Update",background="#51c4d3",relief="groove",highlightbackground="#51c4d3",width=15,font=("Courier", 20)).grid(row=+len(sensors)*2,column=1,columnspan=2,pady=5) 
            
    elif(frame.winfo_name()=="deleteComponentFrame"): 
        Label(frame12,text='What do you want to delete ?',background="#d8e3e7",highlightbackground="#d8e3e7",font=("Courier", 20)).grid(row=1,column=2)
        for i in range(len(comp)): 
            Button(frame12,text=comp.loc[i]["Use"]+' '+comp.loc[i]["Name"],command=lambda i=i:deleteComponent(comp.loc[i]["Name"],comp.loc[i]["Actuator/Sensor"],comp.loc[i]["Use"]),background="#51c4d3",relief="groove",highlightbackground="#51c4d3",width=len(comp.loc[i]["Use"]+' '+comp.loc[i]["Name"]),font=("Courier", 20)).grid(row=2+i,column=2,pady=5)
    elif(frame.winfo_name()=="actuatorsUse"): 
        for i in range(len(retrieveComponentsUse("Actuator"))): 
            Button(frame9,text=retrieveComponentsUse("Actuator")[i],command=lambda i=i:newWindow("Actuator",retrieveComponentsUse("Actuator")[i]),background="#51c4d3",relief="groove",highlightbackground="#51c4d3",width=len(retrieveComponentsUse("Actuator")[i]),font=("Courier", 20)).grid(row=i,column=1,pady=5)
    elif(frame.winfo_name()=="sensorsUse"): 
        for i in range(len(retrieveComponentsUse("Sensor"))):
            Button(frame10,text=retrieveComponentsUse("Sensor")[i],command=lambda i=i :newWindow("Sensor",retrieveComponentsUse("Sensor")[i]),background="#51c4d3",relief="groove",highlightbackground="#51c4d3",width=len(retrieveComponentsUse("Sensor")[i]),font=("Courier", 20)).grid(row=i,column=1,pady=5)
    elif(frame.winfo_name()=="addRout"): 
        Label(frame,text="Select the actuator you want to add routine for",background="#d8e3e7",highlightbackground="#d8e3e7",font=("Courier", 20)).grid(row=1,column=2,pady=5)
        for i in range(len(actuators)): 
             Button(frame,text=actuators[i][2],command=lambda i=i: selAct(actuators[i]),background="#51c4d3",relief="groove",highlightbackground="#51c4d3",width=len(actuators[i][2]),font=("Courier", 20)).grid(row=i+2,column=2,pady=5)
    elif(frame.winfo_name()=="updateRoutines"): 
        Label(frame,text="Select the routine you want to update",background="#d8e3e7",highlightbackground="#d8e3e7",font=("Courier", 20)).grid(row=1,column=2,pady=5)
        for i in range(len(retrieveRoutines())): 
            Button(frame,text=retrieveRoutines().iloc[i]["ID"],command=lambda i=i:updateRoutMenu(retrieveRoutines().iloc[i]),background="#51c4d3",relief="groove",highlightbackground="#51c4d3",width=len(retrieveRoutines().iloc[i]["ID"]),font=("Courier", 20)).grid(row=i+2,column=2,pady=5)
    elif(frame.winfo_name()=="deleteRout"): 
        Label(frame,text="Select the routine you want to delete",background="#d8e3e7",highlightbackground="#d8e3e7",font=("Courier", 20)).grid(row=1,column=2,pady=5)
        for i in range(len(retrieveRoutines())):
            Button(frame,text=retrieveRoutines().iloc[i]["ID"],command=lambda i=i:delOldRoutine(retrieveRoutines().iloc[i]),background="#51c4d3",relief="groove",highlightbackground="#51c4d3",width=len(retrieveRoutines().iloc[i]["ID"]),font=("Courier", 20)).grid(row=i+2,column=2,pady=5)
    elif(frame.winfo_name()=="programDoorFrame"):
        for ind in range(len(actuators)): 
            if(actuators[ind][0]=="Door"): 
                Label(frame6,text=actuators[ind][2]+' program',background="#d8e3e7",highlightbackground="#d8e3e7",font=("Courier", 20)).grid(row=3*ind,column=2,columnspan=2,pady=5)
                Label(frame6,text='Opening time : ',background="#d8e3e7",highlightbackground="#d8e3e7",font=("Courier", 20)).grid(row=3*ind+1,column=1,pady=5)
                openingHours=Entry(frame6,width=2,background="#d8e3e7",highlightbackground="#d8e3e7",font=("Courier", 20)) 
                openingHours.grid(row=3*ind+1,column=3)
                Label(frame6,text=':',background="#d8e3e7",highlightbackground="#d8e3e7",font=("Courier", 20)).grid(row=3*ind+1,column=4,pady=5)
                openingMinutes=Entry(frame6,width=2,background="#d8e3e7",highlightbackground="#d8e3e7",font=("Courier", 20)) 
                openingMinutes.grid(row=3*ind+1,column=5)

                Label(frame6,text='Closing time : ',background="#d8e3e7",highlightbackground="#d8e3e7",font=("Courier", 20)).grid(row=3*ind+2,column=1,pady=5) 
                closingHours=Entry(frame6,width=2,background="#d8e3e7",highlightbackground="#d8e3e7",font=("Courier", 20))
                closingHours.grid(row=3*ind+2,column=3)
                Label(frame6,text=':',background="#d8e3e7",highlightbackground="#d8e3e7",font=("Courier", 20)).grid(row=3*ind+2,column=4,pady=5)
                closingMinutes=Entry(frame6,width=2,background="#d8e3e7",highlightbackground="#d8e3e7",font=("Courier", 20))
                closingMinutes.grid(row=3*ind+2,column=5)
                Button(frame6,text='Save',command=lambda ind=ind:saveChanges(frame6,openingHours.get(),openingMinutes.get(),closingHours.get(),closingMinutes.get(),actuators[ind]),background="#51c4d3",relief="groove",highlightbackground="#51c4d3",width=15,font=("Courier", 20)).grid(row=len(actuators)*3,column=2,columnspan=3,pady=5)
                
    elif(frame.winfo_name()=="programLightFrame"): 
        for ind in range(len(actuators)):
            if(actuators[ind][0]=="Lights"):
                Label(frame7,text=actuators[ind][2]+' program',background="#d8e3e7",highlightbackground="#d8e3e7",font=("Courier", 20)).grid(row=3*ind,column=2,columnspan=2,pady=5)
                Label(frame7,text='Switching ON time : ',background="#d8e3e7",highlightbackground="#d8e3e7",font=("Courier", 20)).grid(row=3*ind+1,column=1,pady=5)
                switchingOnHours=Entry(frame7,width=2,background="#d8e3e7",highlightbackground="#d8e3e7",font=("Courier", 20))
                switchingOnHours.grid(row=3*ind+1,column=3,pady=5)
                Label(frame7,text=':',background="#d8e3e7",highlightbackground="#d8e3e7",font=("Courier", 20)).grid(row=3*ind+1,column=4,pady=5)
                switchingOnMinutes=Entry(frame7,width=2,background="#d8e3e7",highlightbackground="#d8e3e7",font=("Courier", 20))
                switchingOnMinutes.grid(row=3*ind+1,column=5,pady=5)

                Label(frame7,text='Switching OFF time : ',background="#d8e3e7",highlightbackground="#d8e3e7",font=("Courier", 20)).grid(row=3*ind+2,column=1,pady=5)
                switchingOffHours=Entry(frame7,width=2,background="#d8e3e7",highlightbackground="#d8e3e7",font=("Courier", 20))
                switchingOffHours.grid(row=3*ind+2,column=3,pady=5)
                Label(frame7,text=':',background="#d8e3e7",highlightbackground="#d8e3e7",font=("Courier", 20)).grid(row=3*ind+2,column=4,pady=5)
                switchingOffMinutes=Entry(frame7,width=2,background="#d8e3e7",highlightbackground="#d8e3e7",font=("Courier", 20))
                switchingOffMinutes.grid(row=3*ind+2,column=5,pady=5)
                Button(frame7,text='Save',command=lambda ind=ind:saveChanges(frame7,switchingOnHours.get(),switchingOnMinutes.get(),switchingOffHours.get(),switchingOffMinutes.get(),actuators[ind]),background="#51c4d3",relief="groove",highlightbackground="#51c4d3",width=15,font=("Courier", 20)).grid(row=len(actuators)*3,column=2,columnspan=3,pady=5)
    

def updateRoutMenu(routine): 
    op=["<=",">=","=","<",">"] 
    choice=StringVar() 
    frame17.grid(row=1,column=3)
    Label(frame17,text="Actual routine : ",background="#d8e3e7",highlightbackground="#d8e3e7",font=("Courier", 20)).grid(row=1,column=1,pady=5) 
    Label(frame17,text=routine["Operator"]+' '+str(routine["SensorValue"]),background="#d8e3e7",highlightbackground="#d8e3e7",width=15,font=("Courier", 20)).grid(row=1,column=2,pady=5)
    Label(frame17,text="Write the threshold",background="#d8e3e7",highlightbackground="#d8e3e7",font=("Courier", 20)).grid(row=2,column=1,pady=5)
    threshold=Entry(frame17,width=3,font=("Courier", 20)) 
    threshold.grid(row=3,column=1,pady=5)
    actValue=Entry(frame17,width=3,font=("Courier", 20)) 
    Label(frame17,text="Write the value for the actuator (write nothing if you don't need it)",background="#d8e3e7",highlightbackground="#d8e3e7",font=("Courier", 20)).grid(row=4,column=1,pady=5)
    actValue.grid(row=5,column=1,pady=5)
    done=Label(frame17,text="Routine well updated",name="doneLabel",fg="green",background="#d8e3e7",highlightbackground="#d8e3e7",font=("Courier", 20)) 
    for i in range(len(op)): 
         Checkbutton(frame17,text=op[i],variable=choice,onvalue=op[i]).grid(row=6,column=i+1,pady=5)
    Button(frame17,text="Submit",command=lambda:updateRoutine(routine,threshold.get(),choice.get(),actValue.get(),done),background="#51c4d3",relief="groove",highlightbackground="#51c4d3",width=15,font=("Courier", 20)).grid(row=7,column=1,pady=5) 


    
def deleteComponent(name,actOrSens,use): 
    comp.drop(comp.loc[comp["Name"]==name].index,inplace=True) 
    comp.to_csv("components.csv",index=False)
    if(actOrSens=="Actuator"): 
        act=retrieveActuatorsStates() 
        act.drop(name,inplace=True,axis=1) 
        act.to_csv("actuatorsStates.csv",index=False)  
        for i in range(len(actuators)): 
            if(actuators[i][2]==name):
                del actuators[i]
    elif(actOrSens=="Sensor"): 
        allSensors=retrieveAllSensorsValues()
        uses=use.split("/")
        for u in uses:
            allSensors.drop(u+' '+name,inplace=True,axis=1)
            allSensors.to_csv("sensorsValues.csv")
        for i in range(len(sensors)):
            if(sensors[i].getName()==name):
                del sensors[i]
    deleteCron(name,actOrSens,use) 
    updateFrames() 

def selAct(act): 
    frame15.grid(row=1,column=3)
    Label(frame15,text="Select the data according which you want to program routine",background="#d8e3e7",highlightbackground="#d8e3e7",font=("Courier", 20)).grid(row=1,column=1,pady=5)
    for j in range(len(sensors)): 
        for h in range(len(sensors[j].readValues())): 
            Button(frame15,text=sensors[j].readValues()[h][0]+' '+sensors[j].getName(),command=lambda j=j,h=h:rout(act,sensors[j].readValues()[h][0]+' '+sensors[j].getName()),background="#51c4d3",relief="groove",highlightbackground="#51c4d3",width=15,font=("Courier", 20)).grid(row=3+h+j*len(sensors),column=1,pady=5)
            
            
def rout(act,dat): 
    newWind=Toplevel(window)
    frameRout=Frame(newWind,name="frameRout",background="#d8e3e7",relief="groove",padx=10)
    frameRout.grid(row=1,column=4,pady=5)
    op=["<=",">=","=","<",">"] 
    choice=StringVar() 
    Label(frameRout,text="Write the threshold",background="#d8e3e7",highlightbackground="#d8e3e7",font=("Courier", 20)).grid(row=2,column=1,pady=5)
    threshold=Entry(frameRout,width=3,background="#d8e3e7",highlightbackground="#d8e3e7",font=("Courier", 20)) 
    threshold.grid(row=3,column=1,pady=5)
    actValue=Entry(frameRout,width=3,background="#d8e3e7",highlightbackground="#d8e3e7",font=("Courier", 20)) 
    Label(frameRout,text="Write the value for the actuator (write nothing if you don't need it)",background="#d8e3e7",highlightbackground="#d8e3e7",font=("Courier", 20)).grid(row=4,column=1,pady=5)
    actValue.grid(row=5,column=1,pady=5)
    done=Label(frameRout,text="Routine well added",name="doneLabel",fg="green",background="#d8e3e7",highlightbackground="#d8e3e7",font=("Courier", 20)) 
    for i in range(len(op)): 
         Checkbutton(frameRout,text=op[i],variable=choice,onvalue=op[i],background="#d8e3e7",highlightbackground="#d8e3e7",width=15,font=("Courier", 20)).grid(row=3,column=i+2,pady=5)
    for i in range(len(sensors)): 
        if(sensors[i].getName()==dat.split()[1]):
            sensor=sensors[i]
        else: 
            sensor=None
    Button(frameRout,text="Submit",command=lambda:addNewRoutine(act,sensor,dat.split()[0],threshold.get(),choice.get(),actValue.get(),done),background="#51c4d3",relief="groove",highlightbackground="#51c4d3",width=15,font=("Courier", 20)).grid(row=7,column=1,pady=5) 

def addNewRoutine(act,sensor,dat,threshold,choice,actValue,done): 
    addRoutine(act,sensor,dat,threshold,choice,actValue,done)
    updateFrames()
    
def delOldRoutine(routine): 
    deleteRoutine(routine)
    updateFrames()
    

actuators=retrieveComponents("Actuator") 

if __name__=="__main__": 
    GPIO.setmode(GPIO.BCM) 
    GPIO.setwarnings(False)
    window = Tk() 
    window.title("Chicken Coop") 

    #window.geometry("1000x800")
    window.attributes("-fullscreen",1) 
    window.config(background="#d8e3e7") 

    img=[] 
    sensors=listSensors() 
    bouboule=False
    # FRAME Menu
    frame1 = Frame(window,background="#d8e3e7",relief="groove")
    Label(frame1,text="My chicken coop",background="#d8e3e7",width=15,font=("Courier", 36,'bold')).grid(row=0,column=1,columnspan=5,pady=30)
    Label(frame1,text="Actions :",background="#d8e3e7",width=15,font=("Courier", 20)).grid(row=1,column=1,pady=20) 
    Button(frame1,text="Actuators",command=lambda : changeFrame(frame2,1),background="#51c4d3",relief="groove",highlightbackground="#51c4d3",width=15,font=("Courier", 20)).grid(row=2,column=1,pady=5) 
    Button(frame1,text="Sensors",command= lambda: changeFrame(frame3,1),background="#51c4d3",relief="groove",highlightbackground="#51c4d3",width=15,font=("Courier", 20)).grid(row=3,column=1,pady=5)
    Button(frame1,text="Export",command=export,background="#51c4d3",relief="groove",highlightbackground="#51c4d3",width=15,font=("Courier", 20)).grid(row=4,column=1,pady=5)
    Button(frame1,text="Program",command=lambda: changeFrame(frame5,1),background="#51c4d3",relief="groove",highlightbackground="#51c4d3",width=15,font=("Courier", 20)).grid(row=5,column=1,pady=5)
    Button(frame1,text="Add component",command=lambda:changeFrame(frame8,1),background="#51c4d3",relief="groove",highlightbackground="#51c4d3",width=15,font=("Courier", 20)).grid(row=6,column=1,pady=5)
    Button(frame1,text="Delete component",command=lambda:changeFrame(frame12,1),background="#51c4d3",relief="groove",highlightbackground="#51c4d3",width=15,font=("Courier", 20)).grid(row=7,column=1,pady=5)
    Button(frame1,text="Add routine",command=lambda:changeFrame(frame13,1),background="#51c4d3",relief="groove",highlightbackground="#51c4d3",width=15,font=("Courier", 20)).grid(row=8,column=1,pady=5)
    Button(frame1,text="Delete routine",command=lambda:changeFrame(frame14,1),background="#51c4d3",relief="groove",highlightbackground="#51c4d3",width=15,font=("Courier", 20)).grid(row=9,column=1,pady=5)
    Button(frame1,text="Update routine",command=lambda:changeFrame(frame16,1),background="#51c4d3",relief="groove",highlightbackground="#51c4d3",width=15,font=("Courier", 20)).grid(row=10,column=1,pady=5)
    Button(frame1,text="Exit",command=window.destroy,background="#51c4d3",relief="groove",highlightbackground="#51c4d3",width=15,font=("Courier", 20)).grid(row=11,column=1,pady=5)


    frame1.grid(row=1,column=1,padx=20,pady=5)

    frame2=Frame(window,name="actuatorsFrame",background="#d8e3e7",relief="groove",padx=5)
    #FRAME Sensors        
        
    frame3 = Frame(window,name="sensorsFrame",background="#d8e3e7",relief="groove")

    frame6=Frame(window,name="programDoorFrame",background="#d8e3e7",relief="groove",padx=5)
    frame7=Frame(window,name="programLightFrame",background="#d8e3e7",relief="groove",padx=5)
    comp=retrieveAllComponents() 
        
    frame8=Frame(window,background="#d8e3e7",relief="groove",padx=5)
    Label(frame8,text='What do you want to add ?',background="#d8e3e7",highlightbackground="#d8e3e7",font=("Courier",20)).grid(row=1,column=2)
    Button(frame8,text='Actuators',command=lambda:changeFrame(frame9,2),background="#51c4d3",relief="groove",highlightbackground="#51c4d3",width=15,font=("Courier", 20)).grid(row=2,column=2,pady=5)
    Button(frame8,text='Sensors',command=lambda:changeFrame(frame10,2),background="#51c4d3",relief="groove",highlightbackground="#51c4d3",width=15,font=("Courier", 20)).grid(row=3,column=2,pady=5)


    frame9=Frame(window,name="actuatorsUse",background="#d8e3e7",relief="groove",padx=5)


    frame10=Frame(window,name="sensorsUse",background="#d8e3e7",relief="groove",padx=5)

    frame12=Frame(window,name="deleteComponentFrame",background="#d8e3e7",relief="groove",padx=5)

    frame13=Frame(window,name="addRout",background="#d8e3e7",relief="groove",padx=5)


    frame14=Frame(window,name="deleteRout",background="#d8e3e7",relief="groove",padx=5)

    frame15=Frame(window,name="selAct",background="#d8e3e7",relief="groove",padx=5)
    frame16=Frame(window,name="updateRoutines",background="#d8e3e7",relief="groove",padx=5)
    frame17=Frame(window,background="#d8e3e7",relief="groove",padx=5)

    frameContent(frame2) 
    frameContent(frame3)
    frameContent(frame6)
    frameContent(frame7)
    frameContent(frame9)
    frameContent(frame10)
    frameContent(frame12)
    frameContent(frame13)
    frameContent(frame14)
    frameContent(frame16)

    #FRAME Program

    frame4 = Frame(window,background="#d8e3e7",relief="groove",padx=10)
                   
    Label(frame4,text='Select your device',background="#d8e3e7",highlightbackground="#d8e3e7",font=("Courier", 20)).grid(row=0,column=2)


    frame5 = Frame(window,background="#d8e3e7",relief="groove",padx=10)

    Button(frame5,text="Door",command=lambda:changeFrame(frame6,2),background="#51c4d3",relief="groove",highlightbackground="#51c4d3",width=15,font=("Courier", 20)).grid(row=1,column=1,pady=5)
    Button(frame5,text="Lights",command=lambda:changeFrame(frame7,2),background="#51c4d3",relief="groove",highlightbackground="#51c4d3",width=15,font=("Courier", 20)).grid(row=2,column=1,pady=5)



    frame11=Frame(window,background="#d8e3e7",relief="groove",padx=10)


    window.mainloop() 
    exit() 