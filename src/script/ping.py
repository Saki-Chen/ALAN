import os
import time
print('for reboot')
server_ip='172.27.35.1'
server_id='9'

while True:
    res=os.system('ping -w 1 %s' % server_ip)
    if res:
        print('network is down,rebooting...')
        os.system('sudo wpa_cli disable_network %s\nsudo wpa_cli enable_network %s' % (server_id,server_id))
        while True:
            if os.popen('ping -w 1 %s' % server_ip).read():
                print('success')
                break
            else:
                print('wait...')
                time.sleep(1)



