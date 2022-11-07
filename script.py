
from threading import Thread
from paramiko import SSHClient
from scp import SCPClient
import paramiko
import time
import filecmp


def patch(ssh, ip) :
    print("compare an copy on ", ip)
   
    scp = SCPClient(ssh.get_transport())

    scp.get('start.sh','startsh.remote')

    if filecmp.cmp('start.sh', 'startsh.remote') == False : 
        print(ip, ": Files are different, updating")
        scp.put('start.sh')
        stdin, stdout, stderr = ssh.exec_command('chmod +x start.sh')
    else : 
        print(ip + " Files are equal, nothing to do")

	# paranoia: do that every time
    stdin, stdout, stderr = ssh.exec_command("sysctl -w 'kernel.core_pattern=|/bin/false'")

    print(ip, ": DONE")
#    print(stdout.readlines())


class Ip_thread(Thread):
	def __init__(self, ip):
		super().__init__()
		self.ip = ip

	def patch(self):
		print("compare and copy on ", ip)
		self.remote = 'startsh.remote.'+self.ip
   
		scp = SCPClient(self.ssh.get_transport())
		scp.get('start.sh', self.remote)

		if filecmp.cmp('start.sh', self.remote ) == False : 
			print(self.ip, ": Files are different, updating")
			scp.put('start.sh')	
			stdin, stdout, stderr = self.ssh.exec_command('chmod +x start.sh')
		else : 
			print(ip + " Files are equal, nothing to do")

		# paranoia: do that every time
		stdin, stdout, stderr = self.ssh.exec_command("sysctl -w 'kernel.core_pattern=|/bin/false'")
		print(self.ip, ": DONE")

	def run(self):
        
		self.ssh = paramiko.SSHClient()
		self.key = paramiko.RSAKey.from_private_key_file("holotov")
		self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
		print("Thread started for ip = "+ self.ip)
		while True : 
			print("SSH connect to", self.ip)
			try:
				self.ssh.connect(self.ip, username='root',pkey=self.key, timeout=10)
			except TimeoutError:
				print("Connection timeout on ", self.ip, "retry...")
				continue
			except Exception as err:
				print("Connection failed on ", self.ip, "(" , type(err) , ") retry in 60s...")
				time.sleep(60)
				continue
            
			print("Connected to", self.ip)
			self.patch()
			self.ssh.close()
			break
                
threads = []

def create_thread(ip) : 
	t = Ip_thread(ip)
	threads.append(t)
	t.start()

#lecture fichier
file = open('ip-batch-1.txt','r')
listeurl = file.readlines()
file.close()

listeip =[]

for ip in listeurl:
	index  = ip.find(':')
	new_ip = ip[0:index]
	listeip.append(new_ip)

for ip in listeip : 
	create_thread(ip)

for thread in threads:
	thread.join()

print("Bye !")


