import PodSixNet.Channel
import PodSixNet.Server
from time import sleep


class ClientChannel(PodSixNet.Channel.Channel):
    def Network(self, data):
        print(data)
        
    def Network_myaction(self, data):
        print("myaction:", data)
 
class MineServer(PodSixNet.Server.Server):
 
    channelClass = ClientChannel
 
    def Connected(self, channel, addr):
        print('new connection:', channel)
 
print("STARTING SERVER ON LOCALHOST")
MineServe=MineServer()
while True:
    MineServe.Pump()
    sleep(0.01)