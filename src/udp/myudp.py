import struct
import socket  

class MyUdp(object):
    commands=dict(turn_right='\xAA\xBB\x55\x01\x04\x00\x66',
                  stop='\xAA\xBB\x55\x01\x04\x00\x00',
                  start='\xAA\xBB\x55\x01\x04\x00\x77',
                  speed_up='\xAA\xBB\x55\x01\x04\x00\x88')

    def __init__(self):
        #self.address = (host, port)  
        self.__udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
        #self.__udp.bind(self.address)      
    
    def send_message(self,order,val,address):
        if order in MyUdp.commands:
            self.__udp.sendto(MyUdp.getbyte(order,val),address)

    def recv_message(self):
        return self.__udp.recvfrom(1024)

    def close(self):
        self.__udp.close
        del self

    @staticmethod
    def getbyte(order,val):
        data=struct.pack('>H',val)
        temp='%s%s' % (MyUdp.commands[order],data)
        c=MyUdp.check(temp)
        return '%s%s' % (temp,c)
    
    @staticmethod
    def check(b):
        num=struct.unpack_from('BBBBBBB',b,offset=2)
        c=num[0]
        for n in xrange(len(num)-1):
            c=c^num[n+1]
        return struct.pack('B',c)


if __name__=='__main__':
    mdp=MyUdp()
    while True:
        input = raw_input()  
        if not input:  
            break  
        try:
            input=input.split(':',1)
            o,i=input
            i=eval(i)
            mdp.send_message(o,i,('192.168.40.31',8899))
        except:
            print 'no such a order\norderlist:'
            for o in MyUdp.commands:
                print o
    mdp.close() 

#if __name__=='__main__':
#    mdp=MyUdp('192.168.43.221',8899)
#    while True:
#        data, addr = mdp.recv_message()  
#        if not data:  
#            break  
#        print "received:", data, "from", addr  
#    s.close() 


