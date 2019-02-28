# -*- coding: UTF-8 -*-
"""
Query CPU and MEMORY usages of the containers in a openshift project.
Like promethues monitoring.
Test on OpenShift 3.11 on Docker 1.13 on CentOS 7.5.
"""
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
# get docker ID's and NAME's mapping
CMD = 'docker ps --format "{{.ID}}\t{{.Names}}"'
DOCKERS = os.popen(CMD).read()
DICT_ID = {}
for ID in StringIO.StringIO(DOCKERS):
    items = ID.split()
    Key, Value = items[0], items[1]
    DICT_ID[Key] = Value
print("Dokcer ID and Name of all")
print(json.dumps(DICT_ID))
print("*"*20)
DICT_POD_IN_PROJECT = {}
for ID, Name in DICT_ID.items():
    for Pod in List_pod:
        if Pod in Name:
            DICT_POD_IN_PROJECT[ID] = Name
print("POD ID & Name in project" )
print(json.dumps(DICT_POD_IN_PROJECT))
print("*"*20)
# get docker stats for pods in the project
Test_times = int(Script_Duration / Interval)
for count in range(0, Test_times, 1):
    CMD = 'docker  stats --all --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"'
    DOCKERS = os.popen(CMD).read()
    Date = str(time.strftime("%Y-%m-%d-%H%M%S", time.localtime()))
    OC_GET_POD_CMD = os.popen(OC_GET_POD_IN_PROJECT).read()
    for Line in StringIO.StringIO(OC_GET_POD_CMD):
        Output = Date+" "+Line
        with open(OC_GET_POD_LOG, "a") as f:    
            f.write(Output)
        print(Output)
    f.close()
    Text= "Date    Container    ID      CPUPerc      MemUsage \n"
    with open(LOG,"a") as f:
        f.write(Text)
    print("Dokkers status in the project: ", Project)
    with open(LOG, "a") as f:
        for Docker in StringIO.StringIO(DOCKERS):
            ID = Docker.split()[0]
            if ID in DICT_POD_IN_PROJECT.keys():
                Text = Date+" "+DICT_POD_IN_PROJECT[ID]+" "+Docker
                print(Text)
                f.write(Text)
        f.close()
    print("*"*20)
    time.sleep(Interval*60)
print("Monitor done. log file is: ", LOG, OC_GET_POD_LOG)
print("\n")

