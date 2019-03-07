import os
import StringIO
import subprocess
import time
import json

User = raw_input("Project user: ")
Password = raw_input("User password: ")

# Test to login oc into the project
CMD = 'oc login -u '+User+' -p '+Password
subprocess.check_call([CMD],shell=True)
Project = raw_input("Project Name: ")
CMD = 'oc project '+Project
subprocess.check_call([CMD],shell=True)

# Set parameters
Interval = int(input("Set interval for logger (minutes): "))
Script_Duration = int(input("Set how long will in monitoring (miutes): "))
Date = time.strftime("%Y-%m-%d-%H%M%S", time.localtime())
NAME = './pod_in_'+Project+'-'+\
        str(Interval)+'M-'+\
        str(Script_Duration)+'M-'+\
        str(Date)+"-"
LOG = NAME+'alamedarecommendation'+'.log'
OC_GET_POD = "oc get pod -n "
OC_GET_POD_IN_PROJECT = OC_GET_POD + Project
OC_GET_POD_LOG = NAME+'oc_get_pod'+'.log'

# Test to login oc into the project
CMD = 'oc login -u '+User+' -p '+Password
subprocess.check_call([CMD],shell=True)
CMD = 'oc project '+Project
subprocess.check_call([CMD],shell=True)
print("*"*20)

# Get pods NAME in an oc project 
CMD = 'oc get pod -n '+Project+' -o=NAME'
OC_pods = subprocess.Popen([CMD], stdout=subprocess.PIPE,
    shell=True).communicate()[0].splitlines()
List_pod = []
for Pod in OC_pods:
    List_pod.append(Pod.split("/")[1])
print("pod in project")
print(List_pod)
print("*"*20)

# Get alameda scaler 
CMD = "oc get alamedascaler --all-namespaces -o json"
AlamedaScaler = os.popen(CMD).read()

print("*"*20)
# Get alameda recommendation list
CMD = "oc get alamedarecommendation -n "+Project
RES = os.popen(CMD).read()
LIST = []
for LINE in StringIO.StringIO(RES):
    LINE = LINE.split()[0]
    LIST.append(LINE)
if "NAME" in LIST:
    LIST.remove("NAME")
print("Name in alameda recommendation on project:", Project)
print(LIST)

print("*"*20)
# Get recommendation values in pods
Test_times = int(Script_Duration / int(Interval))
Interval_sec = int(Interval) * 60
for count in range(0, Test_times, 1):
    Date = time.strftime("%Y-%m-%d-%H%M%S", time.localtime())
    print("recommendation on POD:")
    with open(LOG, 'a') as file:
        for LINE in LIST:
            CMD = "oc get alamedarecommendation -n "+Project
            CMD = CMD+" "+LINE+" -o json"
            CMD = os.popen(CMD).read()
            CMD = json.loads(CMD)
            CMD = CMD["spec"]["containers"][0]["resources"]
            RES = (Date, LINE, CMD)
            print(RES)
            file.write(str(RES)+"\n")
    file.close()
    print("\n"*5)
    time.sleep(Interval_sec)
print("Monitor done. log file: ", LOG)
print("\n")