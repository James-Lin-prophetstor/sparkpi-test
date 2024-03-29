import json
import os
import time


Interval = int(input("Set interval for logger(minutes): "))
Script_Duration = int(input("Set how long will in test(miutes): "))
Project_Name = raw_input("Project name for sparkpi: ")
Date = str(time.strftime("%Y-%m-%d-%H%M%S", time.localtime()))
alameda_recommendation_log = "/root/alameda_recommendation-" + \
                            str(Interval) + "M" + \
                            str(Script_Duration) + "M" + \
                            Date+".log"

OC_GET_POD="oc get pod -n "+Project_Name
OC_GET_RECOMMENDATION="oc get alamedarecommendation "

def alameda_monitor():
    print("#"*30)
    global Log_time
    Log_time = str(time.strftime("%Y-%m-%d-%H%M%S", time.localtime()))
    with open('/root/sparkpi-dc.json', 'r') as file:
        spark_dc_json = json.load(file)
    print("Read spark deploymentconfig in JSON format.\n\n")
    sparkpi_dc_resources = spark_dc_json["spec"]["template"]["spec"]["containers"][0]["resources"]
    print(Log_time + " " + "Set sparkpi containers deploymentconfig.\n\n")
    print(Log_time + " " + "sparkpi resources:\n" + json.dumps(sparkpi_dc_resources, indent=2) + "\n\n")
    get_running_sparkpi_pod =OC_GET_POD+" -o=name|grep sparkpi |grep -v build"
    get_running_sparkpi_pod_cmd = os.popen(get_running_sparkpi_pod).read()
    pod_name = str(get_running_sparkpi_pod_cmd).split("/")[1].rstrip()
    recommendation = OC_GET_RECOMMENDATION+pod_name+" -n "+Project_Name+" -o json"
    output = os.popen(recommendation).read()
    predict_resources = json.loads(output)["spec"]["containers"][0]["resources"]
    print(Log_time + " " + "sparkpi alameda recommendations: \n" + json.dumps(predict_resources, indent=2) + "\n\n")
    log = open(alameda_recommendation_log, "a")
    log.write(Log_time + " " + str(predict_resources) + "\n")
    log.close()

    
Test_times = int(Script_Duration / int(Interval))
for count in range(0, Test_times, 1):
    alameda_monitor()
    Interval_sec = int(Interval) * 60
    time.sleep(Interval_sec)
    get_running_sparkpi_pod = OC_GET_POD+" -o=name|grep sparkpi |grep -v build"
    get_running_sparkpi_pod_cmd = os.popen(get_running_sparkpi_pod).read()
    pod_name = str(get_running_sparkpi_pod_cmd).split("/")[1].rstrip()
    check_recommendation = OC_GET_RECOMMENDATION+"-n "+Project_Name
    check_recommendation_cmd = os.popen(check_recommendation).read()
    while pod_name not in check_recommendation_cmd:
        time.sleep(10)
        print(Log_time + " " + "Waiting for recommendation up.\n\n")
        check_recommendation_cmd = os.popen(check_recommendation).read()


