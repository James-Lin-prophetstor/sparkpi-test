# -*- coding: UTF-8 -*-
import os
import StringIO
import subprocess
import time
import json

Project = raw_input("Project Name: ")
User = raw_input("Project user: ")
Password = raw_input("User password: ")
Interval = int(input("Set interval for logger (minutes): "))
Script_Duration = int(input("Set how long will in monitoring (miutes): "))
Date = time.strftime("%Y-%m-%d-%H%M%S", time.localtime())
LOG = './pod_in_'+Project+'-'+\
        str(Interval)+'M-'+\
        str(Script_Duration)+'M-'+\
        str(Date)+'.log'

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
    
# get docker ID's and NAME's mapping
CMD = 'docker ps --format "{{.ID}}\t{{.Names}}"'
DOCKERS = os.popen(CMD).read()
DICT_ID = {}
for ID in StringIO.StringIO(DOCKERS):
    items = ID.split()
    Key, Value = items[0], items[1]
    DICT_ID[Key] = Value

DICT_POD_IN_PROJECT = {}
for ID, Name in DICT_ID.items():
    for Pod in List_pod:
        if Pod in Name:
            DICT_POD_IN_PROJECT[ID] = Name
print DICT_POD_IN_PROJECT.keys()

# get docker stats for pods in the project
Test_times = int(Script_Duration / Interval)
for count in range(0, Test_times, 1):
    CMD = 'docker  stats --all --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"'
    DOCKERS = os.popen(CMD).read()
    Date = str(time.strftime("%Y-%m-%d-%H%M%S", time.localtime()))
    Text = {}
    Text[Date] = "Container      CPUPerc      MemUsage"
    for Docker in StringIO.StringIO(DOCKERS):
        ID = Docker.split()[0]
        if ID in DICT_POD_IN_PROJECT.keys():
            Text[ID] = Date +" " + DICT_POD_IN_PROJECT[ID] + " " + Docker        
    print "="*20
    for Key in Text.keys():
        print(Key, Text[Key])
        log = open(LOG, "a")
        log.write(str(Key), str(Text[Key])
        log.close()
    time.sleep(Interval*60)
