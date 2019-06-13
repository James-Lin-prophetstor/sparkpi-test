class OC():
    def __init__(self, user, password, ip, port='8443'):
        import os
        import sys
        import subprocess
        self.user = user
        self.password = password
        self.ip = ip
        self.port = port
        self.process = subprocess

    def login(self):
        cmd = "oc login https://%s:%s -u %s -p %s" %\
             (self.ip, self.port, self.user, self.password)
        return self.process.getoutput(cmd)

    def logout(self):
        cmd = 'oc logout'
        return self.process.getoutput(cmd)

    def project(self, namespace="default"):
        self.namespace = namespace
        cmd = "oc project %s" % self.namespace
        return self.process.getoutput(cmd)

    def get(self, item, name=None, form=None):
        self.item = item
        self.name = name
        self.form = form
        if self.name:
            cmd = 'oc -n %s get %s %s' %\
                 (self.namespace, self.item, self.name)
            if self.form:
                cmd = 'oc -n %s get %s %s -o %s' %\
                 (self.namespace, self.item, self.name, self.form)
        else:
            cmd = 'oc -n %s get %s' %\
                 (self.namespace, self.item)
        return self.process.getoutput(cmd)

    def describe(self, item, name):
        self.item = item
        self.name = name
        cmd = 'oc -n %s describe %s %s' %\
            (self.namespace, self.item, self.name) 
        return self.process.getoutput(cmd)

    def delete(self, item, name, f=None):
        self.item = item
        self.name = name
        self.f = f
        if self.f:
            cmd = 'oc -n %s delete -f %s' %\
            (self.namespace, self.f)
        else: 
            cmd = 'oc -n %s delete %s %s' %\
                (self.namespace, self.item, self.name)
        return self.process.getoutput(cmd)

    def apply(self, f):
        self.f = f
        import os
        test = os.path.isfile(self.f)
        if not test:
            raise RuntimeError(
                'NO FILE TO APPLY.'
            )
        cmd = 'oc apply -f %s' %\
            self.f
        return self.process.getoutput(cmd)