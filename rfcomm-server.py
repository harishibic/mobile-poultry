# file: rfcomm-server.py
# auth: Albert Huang <albert@csail.mit.edu>
# desc: simple demonstration of a server application that uses RFCOMM sockets
#
# $Id: rfcomm-server.py 518 2007-08-10 07:20:07Z albert $

from bluetooth import *

from csvManager import *
from actuatorsManager import useActWithBluetooth
from sensorsManager import updateBluetooth,listSensors
import os
from graphsManager import *
from components import *
from time import sleep
os.system("sudo hciconfig hci0 piscan")

actuators=retrieveComponents("Actuator")
sensors=listSensors()

while True:
  server_sock=BluetoothSocket( RFCOMM )
  server_sock.bind(("",PORT_ANY))
  server_sock.listen(1)

  port = server_sock.getsockname()[1]

  uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

  advertise_service( server_sock, "SampleServer",
                     service_id = uuid,
                     service_classes = [ uuid, SERIAL_PORT_CLASS ],
                     profiles = [ SERIAL_PORT_PROFILE ], 
#                     protocols = [ OBEX_UUID ] 
                   )

  print("Waiting for connection on RFCOMM channel %d" % port)

  client_sock, client_info = server_sock.accept()
  print("Accepted connection from ", client_info)

  def sendActuators(actuators): 
    for act in actuators:
      client_sock.send(act[2]+" "+retrieveActuatorsStatesByName(act[2])+'\n')
    client_sock.send(b'Done\n')

  def sendSensors(sensors): 
    for sens in sensors:
      uses=sens.getUse().split("/")
      for i in range(len(uses)):
        client_sock.send(uses[i]+"_"+sens.getName()+" "+str(sens.readValues()[i][1])+" "+sens.readValues()[i][2]+'\n')
    client_sock.send(b'Done\n')

  isAct=True

  try:
      while True:
          data = client_sock.recv(1024)
          if len(data) == 0: break
          print("received [%s]" % data)
          if (str(data).split("'")[1].split("\\")[0]=="Actuator"): 
            isAct=True 
            sendActuators(actuators) 
          elif(str(data).split("'")[1].split("\\")[0]=="Sensor"): 
            isAct=False
            sendSensors(sensors)
          elif("Last" in str(data).split("'")[1]): 
            nameUse=str(data).split("'")[1].split(" ")[0]
            use=nameUse.split("_")[0]
            name=nameUse.split("_")[1]
            graphName=str(data).split("'")[1].split(" ")[1].split("_")[1].split("\\")[0]
            for sens in sensors:
                for i in range(len(sens.readValues())):
                    if(sens.readValues()[i][0]==use):
                        unit=sens.readValues()[i][2] 
            if(graphName=="hour"):  
             hour(use,name,unit)
            elif(graphName=="day"):
             day(use,name,unit)
            else:
              week(use,name,unit)
            os.system("bt-obex -p "+client_info[0]+" "+os.getcwd()+"/Graphs/"+graphName+use+name+"Graph.png") 
          else: 
            if(isAct):
              useActWithBluetooth(data) 
              actuators=retrieveComponents("Actuator") 
              sendActuators(actuators) 
            elif(str(data).split("'")[1].split("\\")[0]=="Refresh"): 
              try:
                updateBluetooth()
                sensors=listSensors()
                sendSensors(sensors)
              except:
                pass
  except IOError:
      pass

  print("disconnected")

  client_sock.close()
  server_sock.close()
  print("all done")
