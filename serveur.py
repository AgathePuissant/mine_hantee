# -*- coding: utf-8 -*-
"""
Created on Fri Jan  3 09:12:18 2020

@author: eloda
"""

import PodSixNet.Channel
import PodSixNet.Server
from time import sleep

from moteur import *
from objets_graphiques import *
from parametrisation import *
from IA import *

#Each time a client connects, a new Channel based class will be created
class ClientChannel(PodSixNet.Channel.Channel):
    def Network(self, data):
        print(data)
    
        
    def Network_rotation(self, data):
        num = data["num"]
        self.gameid = data["gameid"]
        
        self._server.rotation(data,self.gameid, num)
 
    def Network_insertion(self, data):
        num = data["num"]
        coord = data["coord"]
        self.gameid = data["gameid"]
        
        self._server.insertion(data,self.gameid, num,coord)
        
    def Network_deplacement(self, data):
        num = data["num"]
        event = data["event"]
        self.gameid = data["gameid"]
        
        self._server.deplacement(data,self.gameid, num, event)
        
    def Network_changejoueur(self, data):
        num = data["num"]
        self.gameid = data["gameid"]
        
        self._server.changejoueur(data,self.gameid, num)
        
        
    def Close(self):
        self._server.close(self.gameid)
        
    
    
class MineServer(PodSixNet.Server.Server):
 
    channelClass = ClientChannel
    
    def __init__(self, *args, **kwargs):
        
        PodSixNet.Server.Server.__init__(self, *args, **kwargs)
        self.games = []
        self.queue = None
        self.currentIndex=0
    
    #called whenever a new client connects to your server.
    def Connected(self, channel, addr):
        print('new connection:', channel)
        if self.queue==None:
            self.currentIndex+=1
            channel.gameid=self.currentIndex
            self.queue=Game(channel, self.currentIndex)
        else:
            channel.gameid=self.currentIndex
            self.queue.player1=channel
            self.queue.player0.Send({"action": "startgame","joueur_id":0, "gameid": self.queue.gameid})
            self.queue.player1.Send({"action": "startgame","joueur_id":1, "gameid": self.queue.gameid})
            self.games.append(self.queue)
            self.queue=None
    
    
    def rotation(self, data, gameid, num):
        game = [a for a in self.games if a.gameid==gameid]
        if len(game)==1:
            game[0].rotation(data, num)
    
    def insertion(self, data, gameid, num, coord):
        game = [a for a in self.games if a.gameid==gameid]
        if len(game)==1:
            game[0].insertion(data, num, coord)
            
    def deplacement(self, data, gameid, num, event):
        game = [a for a in self.games if a.gameid==gameid]
        if len(game)==1:
            game[0].deplacement(data, num, event)
            
    def changejoueur(self, data, gameid, num):
        game = [a for a in self.games if a.gameid==gameid]
        if len(game)==1:
            game[0].changejoueur(data, num)
    

class Game:
    
    def __init__(self, player0, currentIndex):
        # whose turn 
        self.turn = 0
        #owner map
        dico_parametres = {'dimensions_plateau': '7', 'nb_fantomes': '21', 'nb_joueurs': '2', 'mode_joueur_1': 'manuel', 'mode_joueur_2': 'manuel', 'mode_joueur_3': 'manuel', 'mode_joueur_4': 'manuel', 'niveau_ia_1': '1', 'niveau_ia_2': '1', 'niveau_ia_3': '1', 'niveau_ia_4': '1', 'pseudo_joueur_1': player0, 'pseudo_joueur_2': '', 'pseudo_joueur_3': '', 'pseudo_joueur_4': '', 'nb_fantomes_mission': '3', 'nb_joker': '1', 'points_pepite': '1', 'points_fantome': '5', 'points_fantome_mission': '20', 'bonus_mission': '40'}
        self.plateau_jeu=plateau(2,[player0,''],[0,0],7,dico_parametres)
        #initialize the players including the one who started the game
        self.player0=player0
        self.player1=None
        #gameid of game
        self.gameid=currentIndex
        
    
    def rotation(self,data,num):
        if num==self.turn:
            self.plateau_jeu.carte_a_jouer.orientation[0],self.plateau_jeu.carte_a_jouer.orientation[1],self.plateau_jeu.carte_a_jouer.orientation[2],self.plateau_jeu.carte_a_jouer.orientation[3]=self.plateau_jeu.carte_a_jouer.orientation[3],self.plateau_jeu.carte_a_jouer.orientation[0],self.plateau_jeu.carte_a_jouer.orientation[1],self.plateau_jeu.carte_a_jouer.orientation[2]
            
            self.player0.Send(data)
            self.player1.Send(data)
        
        
    def insertion(self,data, num, coord):
        if num==self.turn:
            self.plateau_jeu.deplace_carte(coord)
            
            self.player0.Send(data)
            self.player1.Send(data)
    
    def deplacement(self,data, num, event):
        
        if num==self.turn:
            deplace = self.plateau_jeu.deplace_joueur(num,event)
            self.plateau_jeu.compte_points(num,deplace)
            
            self.player0.Send(data)
            self.player1.Send(data)
            
            
    def changejoueur(self,data, num):
        
        if num==self.turn:
            self.turn = 0 if self.turn else 1
            self.player1.Send({"action":"yourturn", "tour":True if self.turn==1 else False})
            self.player0.Send({"action":"yourturn", "tour":True if self.turn==0 else False})

            self.player0.Send(data)
            self.player1.Send(data)
    
    
print("STARTING SERVER ON LOCALHOST")

address=input("Host:Port (localhost:8000): ")
if not address:
    host, port="localhost", 8000
else:
    host,port=address.split(":")

MineServe=MineServer(localaddr=(host, int(port)))
#MineServe=MineServer()
while True:
    MineServe.Pump()
    sleep(0.01)
    
    
    
