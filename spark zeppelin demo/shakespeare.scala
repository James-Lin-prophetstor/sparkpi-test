%pyspark # use python on apache zeppelin web IDE. 
"""
count total number of words in the files. 
this demo count total words on 3 files.
get file 1 from url
get file 2 and file 3 from local PV.
"""

import os
import urllib2
hamlet = urllib2.urlopen('https://raw.githubusercontent.com/eformat/kubernetes-spark/master/data/shakespeare/hamlet.txt').read()
file = open("/aaa/1.txt", "r").read()
dante = open("/aaa/Dante\'s_Inferno.txt", "r").read()
rdd = sc.parallelize([hamlet,file,dante])
print rdd.map(lambda s: len(s.split())).sum()