#!/usr/bin/python

def StringAdjust(word):
    if len(word) < 24:
        word = word.ljust(24)
    else:
        word = word
    return word

def fcinfo():
    import glob
    Sys = '/sys/class/fc_host/'
    glob.glob(Sys)
    hosts = glob.glob(Sys+'*')
    
    dic_hosts_name = {}
    for x in hosts:
        host_name = open(x+"/port_name","r").read()
        host_name = host_name.replace("0x","")
        host_name = host_name.replace("\n","")
        host_name = ":".join(a+b for a,b in zip(host_name[::2], host_name[1::2]))
        dic_hosts_name[x] = host_name

    dic_hosts_speed = {}
    for x in hosts:
        host_speed = open(x+"/speed","r").read()
        host_speed = host_speed.replace("\n","")
        dic_hosts_speed[x] = host_speed

    dic_hosts_state = {}
    for x in hosts:
        host_state = open(x+"/port_state","r").read()
        host_state = host_state.replace("\n","")
        dic_hosts_state[x] = host_state

    dic_hosts_support = {}
    for x in hosts:
        host_support = open(x+"/supported_speeds","r").read()
        host_support = host_support.replace("\n","")
        dic_hosts_support[x] = host_support

    dic_hosts_model = {}
    for x in hosts:
        host_model = open(x+"/symbolic_name","r").read()
        host_model = host_model.split(" ")[0]
        dic_hosts_model[x] = host_model

    dic_hosts = {}
    for host in hosts:
        short_hostname = host.split("/")[-1]
        dic_hosts[short_hostname] = dict()
        dic_hosts[short_hostname]["wwpn"] = dic_hosts_name[host]
        dic_hosts[short_hostname]["model"] = dic_hosts_model[host] 
        dic_hosts[short_hostname]["speed"] = dic_hosts_speed[host]
        dic_hosts[short_hostname]["state"] = dic_hosts_state[host]
        dic_hosts[short_hostname]["supported"] = dic_hosts_support[host]
    return dic_hosts

if __name__ == "__main__":
    dic_hosts = fcinfo()
    for x in dic_hosts:
        print (x, dic_hosts[x])
