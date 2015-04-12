#!/usr/bin/env python
import paramiko

class Ssh():
    """Ssh Class for ssh host"""

    def __init__(self):
        self.ip   = None
        self.port = 22
        self.user = None
        self.password = None

        # sftp
        self.t    = None
        self.sftp = None
        
        # ssh
        self.ssh  = None

    def initSsh(self, ip, user, passwd, port=22):
        self.ip   = ip
        self.port = port
        self.user = user
        self.password = passwd

    def sshConnect(self):        
        self.ssh  = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        self.ssh.connect(self.ip, self.port, self.user, self.password)
        print "# Already connected host %s" % self.ip

    def sshExecute(self, cmd):
        print "ssh2 execute command: %s" %cmd
        stdin, stdout, stderr = self.ssh.exec_command(cmd)
        stdin.close()
        for l in stdout.read().splitlines():
            print '# To excute result : ', l
        for l in stderr.read().splitlines():
            print '# To excute error  : ', l

    def sshExecuteInteract(self):
        print "ssh2 execute interactive command"
        while True:
            cmd = raw_input("Please Input Command to run in server %s : " %(self.ip))
            if cmd == "":
                break
            print "# To run '%s'" % cmd
            channel = self.ssh.get_transport().open_session()
            channel.exec_command(cmd)
            print "# To exit status: %s" % channel.recv(1000)

    def sshClose(self):
        self.ssh.close()

if __name__ == '__main__':
    s = Ssh()
    s.initSsh('192.168.7.1', 'netdata', 'nd!@#$%^')
    s.sshConnect()
    s.sshExecute('ls /home/netdata/data/qzj/20141111')
    s.sshClose()
