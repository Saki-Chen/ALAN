import os
import time
print('for reboot')
server_ip='192.168.40.1'
server_id='11'

while True:
    res=os.system('ping -w 3 %s' % server_ip)
    if res:
        print('network is down,rebooting...')
        os.system('sudo wpa_cli disable_network all\nsudo wpa_cli enable_network %s' % server_id)
        while True:
            if os.popen('ping -w 1 %s' % server_ip).read():
                print('success')
                break
            else:
                print('wait...')
                time.sleep(1)



