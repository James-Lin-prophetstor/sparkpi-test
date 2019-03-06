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
LOG = NAME+'docker_stats'+'.log'
OC_GET_POD = "oc get pod -n "
OC_GET_POD_IN_PROJECT = OC_GET_POD + Project
OC_GET_POD_LOG = NAME+'oc_get_pod'+'.log'

# Test to login oc into the project
CMD = 'oc login -u '+User+' -p '+Password
subprocess.check_call([CMD],shell=True)
CMD = 'oc project '+Project
subprocess.call([CMD],shell=True)
print("*"*20)

# get pods NAME in an oc project 
CMD = 'oc get pod -n '+Project+' -o=NAME'
OC_pods = subprocess.Popen([CMD], stdout=subprocess.PIPE,
    shell=True).communicate()[0].splitlines()
List_pod = []
for Pod in OC_pods:
    List_pod.append(Pod.split("/")[1])
print("pod in project")
print(List_pod)
print("*"*20)

#get alameda scaler 
CMD = "oc get alamedascaler --all-namespaces -o json"
AlamedaScaler = os.popen(CMD).read()
print(AlamedaScaler)

print("*"*20)
# get alameda recommendation list
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

# get recommendation values in pods
for LINE in LIST:
        CMD = "oc get alamedarecommendation -n "+Project
        CMD = CMD+" "+LINE+" -o json"
        CMD = os.popen(CMD).read()
        CMD = json.load(CMD)
        print(json.dumps(CMD)
        
        
