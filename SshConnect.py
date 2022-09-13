#python_paramiko.py

import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('ec2-34-226-124-76.compute-1.amazonaws.com', port='22', username='ec2-user', key_filename='./MOMO.pem')

stdin, stdout, stderr = ssh.exec_command('df -h')
print(''.join(stdout.readlines()))

ssh.close()