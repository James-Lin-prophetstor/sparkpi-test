#!/bin/bash
#Check sparkpi running
export OC=/usr/local/bin/oc
read -p "Spark project name on openshift: " PROJECT

# login oc cluster as user=admin and password=password
login_oc()
{
    read -p "Openshift cluster user: " USER
    read -p "Openshift cluster user password: " PASSWORD
    $OC login -u $USER -p $PASSWORD 2>&1 > /dev/null
    USE_NAMESPACE=`$OC project $PROJECT `
    echo $USE_NAMESPACE
}
    
TEST_LOGIN_OC=$(login_oc)
echo $TEST_LOGIN_OC

# go into project spark-cluster and check running state
STAT()
{
    POD=`$OC get pod -n $PROJECT | grep 'sparkpi-'|grep -v build|cut -d ' ' -f1`
    STAT=`$OC describe pod $POD  -n $PROJECT |grep 'State'`
    echo $STAT
}

Stat=$(STAT)
if [[ ${Stat} != *'Running'* ]]; then
    echo "Sparkpi is not Running on $PROJECT ."
    exit 0
else
    echo "Sparkpi is Running on $PROJECT."
fi

DATE=`date +%Y%m%d-%H%M%S-%Z`
# Check sparkpi expose port 
NODEPORT=`$OC get service sparkpi -n $PROJECT -oyaml |grep -i 'nodeport:' |awk '{print $2}' `
if test $[NODEPORT] -gt 30000 ;then NODEPORT=":${NODEPORT}";else NODEPORT="" ; fi

# Configure SPARKPI url
export HOST_SERVICE=`$OC get routes/sparkpi -n $PROJECT --template='{{.spec.host}}'`
URL="http://`echo ${HOST_SERVICE}${NODEPORT}`/sparkpi?scale=1000"


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

# Create log files under script work folder
LOG_FILE="${INITIAL}_${DATE}_${INTERVAL}S_${LOG_INTERVAL}M_${TERM}M.log"
touch ./$LOG_FILE
SPARKPI_LOG="${INITIAL}_${DATE}_${INTERVAL}S_${LOG_INTERVAL}M_${TERM}M_Sparkpi_Stats_${LIMIT}.log"
touch ./$SPARKPI_LOG
PROMETHEUS_LOG="${INITIAL}_${DATE}_${INTERVAL}S_${LOG_INTERVAL}M_${TERM}M_Prometheus_Stats_${LIMIT}.log"
touch ./$PROMETHEUS_LOG
INFLUXDB_LOG="${INITIAL}_${DATE}_${INTERVAL}S_${LOG_INTERVAL}M_${TERM}M_Influxdb_Stats_${LIMIT}.log"
touch ./$INFLUXDB_LOG
ALAMEDA_AI_LOG="${INITIAL}_${DATE}_${INTERVAL}S_${LOG_INTERVAL}M_${TERM}M_Alameda_ai_Stats_${LIMIT}.log"
touch ./$ALAMEDA_AI_LOG
ALAMEDA_OPERATOR_LOG="${INITIAL}_${DATE}_${INTERVAL}S_${LOG_INTERVAL}M_${TERM}M_Alameda_operator_Stats_${LIMIT}.log"
touch ./$ALAMEDA_OPERATOR_LOG
ALAMEDA_DATAHUB_LOG="${INITIAL}_${DATE}_${INTERVAL}S_${LOG_INTERVAL}M_${TERM}M_Alameda_datahub_Stats_${LIMIT}.log"
touch ./$ALAMEDA_DATAHUB_LOG

DOCKER_STATS='docker stats --no-stream'
HEAD_LINE=$($DOCKER_STATS | head -n 1 | awk '{print $1" "$2"\t"$3"\t"$4" "$5 "\t"$6" "$7" "$8" "$9 }')
Date=$(date +%Y-%m-%d-%H:%M:%S)
echo "$Date  $HEAD_LINE " > $SPARKPI_LOG
echo "$Date  $HEAD_LINE " > $PROMETHEUS_LOG
echo "$Date  $HEAD_LINE " > $INFLUXDB_LOG
echo "$Date  $HEAD_LINE " > $ALAMEDA_AI_LOG
echo "$Date  $HEAD_LINE " > $ALAMEDA_OPERATOR_LOG
echo "$Date  $HEAD_LINE " > $ALAMEDA_DATAHUB_LOG

export INTERVAL LOG_INTERVAL TERM SPARKPI_LOG PROMETHEUS_LOG INFLUXDB_LOG ALAMEDA_LOG

COUNT=$((${TERM}*60/${INTERVAL}))

Check_sparkpi_stat()
{
    Stat=$(STAT)
    until [[ $Stat == *'Running'* ]] ; do
        Stat=$(STAT)
        sleep 1
   done
}


# Write docker stats and test results to logs
LOGGER()
{
    LOGCOUNT=$((${TERM}/${LOG_INTERVAL}))
    echo "log times $LOGCOUNT"
    for LOGTEST in `seq 0 1 ${LOGCOUNT}` ; do
        Check_sparkpi_stat
        RESTARTS=`oc get pods | grep sparkpi- |grep -v build |awk '{print $4}'`
        DETAILS=`oc get pods -n $PROJECT `
        echo "$(date +%Y-%m-%d-%H:%M:%S) SPARkPI OOM RESTARTS TIME: $RESTARTS" >> ${LOG_FILE}
        echo "$DETAILS " >> ${LOG_FILE}
        Sparkpi_Stat=$($DOCKER_STATS | awk '{print $1" "$2"\t"$3"\t"$4" "$5" "$6}' | grep 'sparkpi' | grep $PROJECT |grep -v 'POD')
        Prometheus_Stat=$($DOCKER_STATS | awk '{print $1" "$2"\t"$3"\t"$4" "$5" "$6}' | grep 'prometheus' | grep -v 'POD')
        Influxdb_Stat=$($DOCKER_STATS | awk '{print $1" "$2"\t"$3"\t"$4" "$5" "$6}' | grep 'influxdb' | grep -v 'POD')
        Alameda_ai_Stat=$($DOCKER_STATS | awk '{print $1" "$2"\t"$3"\t"$4" "$5" "$6}' | grep 'alameda-ai'| grep -v 'POD')
        Alameda_operator_Stat=$($DOCKER_STATS | awk '{print $1" "$2"\t"$3"\t"$4" "$5" "$6}' | grep 'alameda_operator' | grep -v 'POD')
        Alameda_datahub_Stat=$($DOCKER_STATS | awk '{print $1" "$2"\t"$3"\t"$4" "$5" "$6}' | grep 'datahub'| grep -v 'POD')
        Date=$(date +%Y-%m-%d-%H:%M:%S)
        echo "$Date  $Sparkpi_Stat " >> $SPARKPI_LOG
        echo "$Date  $Prometheus_Stat " >> $PROMETHEUS_LOG
        echo "$Date  $Influxdb_Stat " >> $INFLUXDB_LOG
        echo "$Date  $Alameda_ai_Stat " >> $ALAMEDA_AI_LOG
        echo "$Date  $Alameda_operator_Stat " >> $ALAMEDA_OPERATOR_LOG
        echo "$Date  $Alameda_datahub_Stat " >> $ALAMEDA_DATAHUB_LOG
        LOG_INTERVAL_SEC=$(($LOG_INTERVAL*60))
        sleep $LOG_INTERVAL_SEC
    done
    echo "Findished LOGGER"
    echo
}

TEST_OOM()
{
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
TEST_OOM &
wait
