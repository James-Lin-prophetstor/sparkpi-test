import json
import os
import time


# Log files are pod_restart.log & pod_restart_resources.log
# default SPARK namespace used spark-cluster,
# replace namespace by BASH command sed -i 's/-n spark-cluster/-n <namespace>/g' apply_recommendation.py

Script_Duration = int(input("How long to run the script(min) : "))
Interval = int(input("Set test interval(min) : "))
Date = str(time.strftime("%Y-%m-%d-%H%M%S", time.localtime()))
pod_restart_log = "/root/pod_restart-" + \
                  str(Interval) + "M" + \
                  str(Script_Duration) + "M" + \
                  Date+".log"
pod_restart_resources_log = "/root/pod_restart_resources-" + \
                            str(Interval) + "M" + \
                            str(Script_Duration) + "M" + \
                            Date+".log"
# read sparkpi config into a JSON file
# check the resources in the config
# read alameda recommendation into a JSON file
# apply new resources of memory limits and requests 
def alameda_test():
    print("#"*30)
    global Log_time
    Log_time = str(time.strftime("%Y-%m-%d-%H%M%S", time.localtime()))
    with open('/root/sparkpi-dc.json', 'r') as file:
        spark_dc_json = json.load(file)
    print("Read spark deploymentconfig in JSON format.\n\n")
    sparkpi_dc_resources = spark_dc_json["spec"]["template"]["spec"]["containers"][0]["resources"]
    print(Log_time + " " + "Set sparkpi containers deploymentconfig.\n\n")
    print(Log_time + " " + "sparkpi resources:\n" + json.dumps(sparkpi_dc_resources, indent=2) + "\n\n")

    get_running_sparkpi_pod = "oc get pod -n spark-cluster -o=name|grep sparkpi |grep -v build"
    get_running_sparkpi_pod_cmd = os.popen(get_running_sparkpi_pod).read()
    pod_name = str(get_running_sparkpi_pod_cmd).split("/")[1].rstrip()
    alamedarecommendation = "oc get alamedarecommendation "+pod_name+" -n spark-cluster -o json"
    output = os.popen(alamedarecommendation).read()
    predict_resources = json.loads(output)["spec"]["containers"][0]["resources"]
    print(Log_time + " " + "sparkpi alameda recommendations: \n" + json.dumps(predict_resources, indent=2) + "\n\n")
    log = open(pod_restart_resources_log, "a")
    log.write(Log_time + " " + str(predict_resources) + "\n")
    log.close()
    if predict_resources:
        spark_dc_json["spec"]["template"]["spec"]["containers"][0]["resources"] = predict_resources
        print(Log_time + " " + "Set recommendation containers resources.\n\n")
        with open('/root/sparkpi-dc.json', 'w') as file:
            json.dump(spark_dc_json, file, indent=2)
        print(Log_time + " " + "deploymentconfig in JSON format.\n\n")
        get_pods = "oc get pods -n spark-cluster"
        get_pods_cmd = os.popen(get_pods).read()
        f = open(pod_restart_log, "a")
        f.write(Log_time + " " + str(get_pods_cmd) + "\n")
        f.close()
        apply_dc = "oc apply -f /root/sparkpi-dc.json "
        apply_dc_cmd = os.popen(apply_dc).read()
        print(Log_time + " " + apply_dc_cmd + "Apply sparkpi deploymentconfig.\n\n")


Test_times = int(Script_Duration / int(Interval))
for count in range(0, Test_times, 1):
    alameda_test()
    get_pods = "oc get pods -n spark-cluster"
    get_pods_cmd = os.popen(get_pods).read()
    print(Log_time + " " + get_pods_cmd + "\n\n")
    if "Terminating":
        if "ContainerCreating" in get_pods_cmd:
            print(Log_time + " " + "pods Terminating.\n\n")
            f = open(pod_restart_log, "a")
            f.write(Log_time + " " + "pods reset \n")
            f.close()
        elif "Running" in get_pods_cmd:
            print(Log_time + " " + "do nothing on pods.\n\n")
            f = open(pod_restart_log, "a")
            f.write(Log_time + " " + "pods NOT reset \n")
            f.close()
    Interval_sec = int(Interval) * 60
    time.sleep(Interval_sec)
    while "Running" not in get_pods_cmd:
        time.sleep(10)
        print(Log_time + " " + "Waiting for pods up.\n\n")
        get_pods_cmd = os.popen(get_pods).read()
        if "OOMKilled" in get_pods_cmd:
            alameda_test()
    get_running_sparkpi_pod = "oc get pod -n spark-cluster -o=name|grep sparkpi |grep -v build"
    get_running_sparkpi_pod_cmd = os.popen(get_running_sparkpi_pod).read()
    pod_name = str(get_running_sparkpi_pod_cmd).split("/")[1].rstrip()
    check_recommendation = "oc get alamedarecommendation -n spark-cluster"
    check_recommendation_cmd = os.popen(check_recommendation).read()
    while pod_name not in check_recommendation_cmd:
        time.sleep(10)
        print(Log_time + " " + "Waiting for recommendation up.\n\n")
        check_recommendation_cmd = os.popen(check_recommendation).read()

