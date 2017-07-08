# -*- coding: UTF-8 -*- 
import struct
import socket  
import time
class MyUdp(object):
    commands=dict(helm_motor='\xAA\xBB\x55\x01\x04\x00\x66',
                  stop='\xAA\xBB\x55\x01\x04\x00\x00',
                  start='\xAA\xBB\x55\x01\x04\x00\x77',
                  speed_up='\xAA\xBB\x55\x01\x04\x00\x88',
                  guidance='\xAA\xBB\x55\x01\x04\x00\x11',
                  lost='\xAA\xBB\x55\x01\x04\x00\x22',
                  avoid='\xAA\xBB\x55\x01\x04\x00\x44',
                  test_pid='\xAA\xBB\x55\x01\x04\xAA',
                  listen_speed='\xaa\xbb\x01\x55\x04',
                  back_car='\xAA\xBB\x55\x01\x04\x00\xBB')

    def __init__(self):
        self.udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
        self.client_address=None
    
    def bind_host(self):
        self.address = (MyUdp.getlocalIP(), 8899)  
        self.udp.bind(self.address)    

    def send_message(self,order,val=(0,0)):
        #val=(val1,val2) val1:-128~127 val2:0~255
        if order in MyUdp.commands and self.client_address is not None:
            self.udp.sendto(MyUdp.getbyte(order,val),self.client_address)

    def recv_message(self):
        #return self.udp.recv(1024)
        return self.udp.recvfrom(1024)

    def close(self):
        self.udp.close
        del self

    @staticmethod
    def getbyte(order,val):
        data=struct.pack('bB',val[0],val[1])
        temp='%s%s' % (MyUdp.commands[order],data)
        c=MyUdp.check(temp)
        return '%s%s' % (temp,c)
    
    @staticmethod
    def check(beit):
        num=struct.unpack_from('BBBBBBB',beit,offset=2)
        c=num[0]
        for n in xrange(len(num)-1):
            c=c^num[n+1]
        return struct.pack('B',c)

    @staticmethod
    def getlocalIP():
        return socket.gethostbyname(socket.gethostname())

    @staticmethod
    def get_piIP(piname):
        try:
            raspberrypi=socket.getaddrinfo(piname,None)
            return raspberrypi[4][4][0]
        except:
            return 0

    @staticmethod
    def getdata(datum):
        cmd=None
        if MyUdp.check(datum)==datum[-1:]:
            for key,value in MyUdp.commands.items():
                if value==datum[:7]:
                    cmd=key
        if cmd is not None:
            return (cmd,struct.unpack('b',datum[-3])[0],struct.unpack('B',datum[-2])[0])
        else:
            return None

if __name__=='__ain__':
    mdp=MyUdp()
    mdp.bind_host()
    mdp.client_address=('192.168.56.31',8899)
    while True:
        input = raw_input()  
        if not input:  
            break  
        try:
            input=input.split(',')
            #两位数据位分开使用
            o,i1,i2=input
            i=(eval(i1),eval(i2))
            mdp.send_message(o,i)
        except:
            print 'no such a order\norderlist:'
            for o in MyUdp.commands:
                print o
            break
        #data, addr = mdp.recv_message()
        #data=MyUdp.getdata(data)
        #if data:
        #    print "received:", data, "from", addr
    mdp.close() 


if __name__=='__ain__':
    mdp=MyUdp()
    mdp.bind_host()
    mdp.client_address=('192.168.56.31',8899)
    angle=100
    while True: 
        try:
            #两位数据位分开使用
            time.sleep(0.5)
            angle=angle*-1
            o,i1,i2=('guidance',angle,abs(angle))
            i=(i1,i2)
            mdp.send_message(o,i)
            ##o,i1,i2=('guidance',angle,abs(angle))
            ##i=(i1,i2)
            ##mdp.send_message(o,i)
            ##o,i1,i2=('guidance',angle,abs(angle))
            ##i=(i1,i2)
            #mdp.send_message(o,i)
        except:
            print 'no such a order\norderlist:'
            for o in MyUdp.commands:
                print o
            break
        #data, addr = mdp.recv_message()
        #data=MyUdp.getdata(data)
        #if data:
        #    print "received:", data, "from", addr
    mdp.close() 

if __name__=='__main__':
    mdp=MyUdp()
    #mdp.bind_host()
    mdp.client_address=('192.168.56.31',8899)
    while True:
        input = raw_input()  
        if not input:  
            break  
        #try:
        input=input.split(',')
        p=input[0]
        data=struct.pack('>H',int(p))
        temp='%s%s' % (MyUdp.commands['helm_motor'], data)   
        num=struct.unpack_from('BBBBBBB',temp,offset=2)
        c=num[0]
        for n in xrange(len(num)-1):
            c=c^num[n+1]
        ck=struct.pack('B',c)
        mes='%s%s' % (temp,ck)
        mdp.udp.sendto(mes,mdp.client_address)

    mdp.close() 

if __name__=='__ain__':
    mdp=MyUdp()
    mdp.bind_host()
    mdp.client_address=('192.168.56.31',8899)
    while True:
        input = raw_input()  
        if not input:  
            break  
        #try:
        input=input.split(',')
        p,i,d=input
        data=struct.pack('BBB',int(p),int(i),int(d))
        temp='%s%s' % (commands['test_pid'], data)
        
       
        num=struct.unpack_from('BBBBBBB',temp,offset=2)
        c=num[0]
        for n in xrange(len(num)-1):
            c=c^num[n+1]
        ck=struct.pack('B',c)
        mes='%s%s' % (temp,c)
        mdp.udp.sendto(mes,mdp.client_address)

    mdp.close() 

if __name__=='__ain__':
    #import numpy as np
    #from matplotlib import pyplot as plt
    mdp=MyUdp()
    mdp.bind_host()
    #graph=np.ones((1024,1),dtype=np.int)
    
    current=0
    while True: 
        data, addr = mdp.recv_message()
        try:        
            index=data.find(MyUdp.commands['listen_speed'])
            data=data[index+5:index+9]
        except:
            pass

        if not index==-1 and len(data)==4  :            
            speed=struct.unpack('>I',data)
            print "received:", speed[0], "from", addr 
            #graph[current]=speed
            #current=current+1
            #plt.draw()
     
    mdp.close()     
