from crontab import CronTab
import subprocess
import sys
import os

user = str(subprocess.check_output('whoami')).split("'")[1].split("\\")[0] 
python="/usr/bin/python3"
if("/" in sys.argv[0]):
    path=sys.argv[0].split("ChickenCoopSystem/")[0]+"ChickenCoopSystem"
else:
    path=os.getcwd()
    

cron=CronTab(user=user)

cron.new(command=python+' '+path+'/actuatorsManager.py LED Light1 On',comment="Light1").hours.on(7)
cron.new(command=python+' '+path+'/actuatorsManager.py LED Light1 Off',comment="Light1").hours.on(19)
cron.new(command=python+' '+path+'/actuatorsManager.py Servomotor Door1 Opened',comment="Door1").hours.on(7)
cron.new(command=python+' '+path+'/actuatorsManager.py Servomotor Door1 Closed',comment="Door1").hours.on(19)
cron.new(command=python+' '+path+'/sensorsManager.py Temperature/Humidity',comment="Temperature/Humidity").minutes.every(5)

cron.new(command= python+' '+path+'/routines.py').every_reboot()
cron.new(command= 'sudo '+python+' '+path+'/rfcomm-server.py').every_reboot()


cron.write()

#installation of libraries (pandas, psutil ?, PIL ?)