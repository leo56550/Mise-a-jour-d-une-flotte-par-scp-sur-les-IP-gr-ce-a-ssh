
from ping3 import ping
from threading import Thread
from paramiko import SSHClient
from scp import SCPClient
import paramiko
import time
import filecmp

def compareandcpy(ip) : 
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip,username='root',key_filename='name')
    scp = SCPClient(ssh.get_transport())
    stdin, stdout, stderr = ssh.exec_command('ls')
    scp.get('start.sh','startsh.remote')

    if filecmp.cmp('start.sh', 'startsh.remote') == False : 
        print("Files aren't equal")
        scp.put('start.sh')
    else : 
        print("Files are equal, nothing to do")
    print(stdout.readlines())
    ssh.close()

class Ip_thread(Thread):
    def __init__(self, ip):
        super().__init__()
        self.ip = ip 

    def run(self):
        
        print("Thread started for ip = "+ self.ip)
        while True : 
            print("Pinging ip : " + self.ip)
            resp = ping(self.ip)
            if resp == False:
                    print("Non")
                    time.sleep(1)
                    continue 
            print("Oui") 
            compareandcpy(self.ip)
                
threads = []

def create_thread(ip) : 
    t = Ip_thread(ip)
    threads.append(t)
    t.start()

#lecture fichier
file = open('ip-batch-1.txt','r')
listeurl = file.readlines()
listeip =[]

for ip in listeurl:
    #print("Ip = " + ip )
    index  = ip.find(':')
    new_ip = ip[0:index]
    listeip.append(new_ip)
    print("Nouvelle ip : " + new_ip)

for ip in listeip : 
    create_thread(ip)

for thread in threads:
    thread.join()

print("end ")

  
file.close()

