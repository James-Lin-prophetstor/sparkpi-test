#!/bin/bash
: ts=4 sw=4 et smarttab
#Check sparkpi running
if [ -x /usr/local/bin/oc ]; then 
    export OC=/usr/local/bin/oc
else
    echo "oc command was not found."
    exit 1
fi

echo "Test SparkPI on Openshift 3.11 with Alameda on CentOS 7.6 and later"
echo " "
echo "## Enter projects by space; like, project-1 project-2 project-3"
read -p "Spark projects on openshift: " PROJECT_LIST

# login oc cluster
login_oc()
{
    read -p "Openshift cluster user: " USER
    read -p "Openshift cluster user password: " PASSWORD
    LOGIN=`$OC login -u $USER -p $PASSWORD`
    echo $LOGIN
}
TEST_LOGIN_OC=$(login_oc)
echo $TEST_LOGIN_OC

# shift to project spark-cluster and check running state
stat()
{
    POD=`$OC get pod -n $PROJECT | grep 'sparkpi-'|grep -v build|cut -d ' ' -f1`
    STAT=`$OC describe pod $POD -n $PROJECT |grep 'State'`
    echo $STAT
}
for PROJECT in $PROJECT_LIST ; do
    STAT=$(stat)
    if [[ ${STAT} != *'Running'* ]]; then
        echo "Sparkpi is not Running on project: $PROJECT "
        exit 1
    else
        echo "Sparkpi is Running on project: $PROJECT "
    fi
done

DATE=`date +%Y%m%d-%H%M%S-%Z`
Date=$(date +%Y-%m-%d-%H:%M:%S)
read -p "Set interval(seconds) for sparkpi: " INTERVAL
read -p "Set interval(minutes) for logger: " LOG_INTERVAL
read -p "Set how long will in test(miutes): " TERM
read -p "Test with Alameda enabled(y/n)? " ALAMEDA_ENABLE
read -p "SPARKPI resources had limit (y/n)?" RESOURCE_LIMT
if [[ ${ALAMEDA_ENABLE} == 'y'* ]]; then
    INITIAL='sparkpi_alameda_enabled'
else
    INITIAL='sparkpi_alameda_disabled'
fi

if [[ ${RESOURCE_LIMT} == 'y'* ]]; then
    LIMIT='mem_limit_yes'
else
    LIMIT="mem_limit_no"
fi
export INTERVAL LOG_INTERVAL TERM

COUNT=$((${TERM}*60/${INTERVAL}))
export COUNT
Check_sparkpi_stat()
{
    STAT=$(stat)
    until [[ $Stat == *'Running'* ]] ; do
        STAT=$(stat)
        sleep 1
   done
}

# Write docker stats and test results to logs
LOGGER()
{
    # Create log files under script work folder
    Pod_list="prometheus-alertmanager-configmap-reload 
                prometheus-alertmanager_prometheus 
                prometheus-kube-state-metrics 
                prometheus-pushgateway_prometheus-pushgateway 
                prometheus-server-configmap-reload 
                prometheus-server_prometheus-server
                influxdb 
                alameda-ai 
                alameda_operator 
                datahub"
    Docker_Stats="docker stats --no-stream"
    Awk_Headline="awk '{print $1" "$2"\t"$3"\t"$4" "$5 "\t"$6" "$7" "$8" "$9 }')"
    Awk="awk '{print $1" "$2"\t"$3"\t"$4" "$5" "$6}'"
    HEAD_LINE=$($Docker_Stats | head -n 1 | $Awk_Headline )
    
    for Project in $PROJECT_LIST ; do
        Log_file="${INITIAL}_${DATE}_${INTERVAL}S_${LOG_INTERVAL}M_${TERM}M_${Project}.log"
        touch ./$Log_file
        Sparkpi_Log="${INITIAL}_${DATE}_${INTERVAL}S_${LOG_INTERVAL}M_${TERM}M_Sparkpi_Stats_${project}_${LIMIT}.log"
        touch ./$Sparkpi_Log
    done

    for Pod in $Pod_list ; do
        ${Pod}_LOG="${INITIAL}_${DATE}_${INTERVAL}S_${LOG_INTERVAL}M_${TERM}M_${Pod}_${LIMIT}.log"
        touch ./${${Pod}_LOG}
        echo "$Date  $HEAD_LINE " > ${${Pod}_LOG}
    done
    
    # trigger loggers 
    LOGCOUNT=$((${TERM}/${LOG_INTERVAL}))
    echo "log times $LOGCOUNT"
    for LOGTEST in `seq 0 1 ${LOGCOUNT}` ; do
        for PROJECT in $PROJECT_LIST ; do
            Check_sparkpi_stat
        done
        
        for PROJECT in $PROJECT_LIST ; do
            Restarts=`oc get pods | grep sparkpi- |grep -v build |awk '{print $4}'`
            Details=`oc get pods -n $PROJECT `
            echo "$Date SPARkPI OOM RESTARTS TIME: $Restarts" >> ${Log_file}
            echo "$Date $Details " >> ${Log_file}
            Sparkpi_Stat=$($Docker_Stats | $Awk | grep 'sparkpi' | grep -v 'POD')
            echo "$Date  $Sparkpi_Stat " >> $Sparkpi_Log
        done
        for Pod in $Pod_list ; do
                ${Pod}_Stat=$($Docker_Stats | $Awk | grep ${Pod} | grep -v 'POD')
                echo "$Date  ${${Pod}_Stat} " >> ${${Pod}_LOG}
        done
        LOG_INTERVAL_SEC=$(($LOG_INTERVAL*60))
        sleep $LOG_INTERVAL_SEC
    done
    echo "Findished LOGGER"
    echo
}

TEST_OOM()
{
    # Check sparkpi expose port 
    NODEPORT=`$OC get service sparkpi -n $PROJECT -oyaml |grep -i 'nodeport:' |awk '{print $2}' `
    if test $[NODEPORT] -gt 30000 ;then NODEPORT=":${NODEPORT}";else NODEPORT="" ; fi
    # Configure SPARKPI url
    export HOST_SERVICE=`$OC get routes/sparkpi -n $PROJECT --template='{{.spec.host}}'`
    URL="http://`echo ${HOST_SERVICE}${NODEPORT}`/sparkpi?scale=1000"
    Check_sparkpi_stat
    TEST=1
    while [ ${TEST} -le ${COUNT} ] ; do
        echo "Totla test ${COUNT} Times."
        echo "ROUND ${TEST} ." 
        curl ${URL} 2>&1 > /dev/null 
        sleep ${INTERVAL}
        Check_sparkpi_stat
        TEST=$((${TEST}+1))
    done
    echo "Finished TEST"
    echo 
}

LOGGER &
echo "subprocess ID: $! "
TEST_OOM &
echo "subprocesspr ID: $! "
wait
