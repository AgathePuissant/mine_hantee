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
    
    def Network_fin(self, data):
        self.gameid = data["gameid"]
        
        self._server.fin(data,self.gameid)
        
        
    def Close(self):
        self._server.close(self.gameid)
        
    
    
class MineServer(PodSixNet.Server.Server):
 
    channelClass = ClientChannel
    
    def __init__(self, *args, **kwargs):
        
        PodSixNet.Server.Server.__init__(self, *args, **kwargs)
        self.games = []
        self.queue = []
        self.currentIndex=0
    
    #called whenever a new client connects to your server.
    def Connected(self, channel, addr):
        print('nouvelle connexion:', channel)
        if self.queue==[]:
            print("en attente d'un autre joueur...")
            self.currentIndex+=1
            channel.gameid=self.currentIndex
            self.queue.append(channel)
        else:
            channel.gameid=self.currentIndex
            self.queue.append(channel)
            self.queue[0].Send({"action": "startgame","joueur_id":0, "gameid": self.currentIndex})
            self.queue[1].Send({"action": "startgame","joueur_id":1, "gameid": self.currentIndex})
            print("La partie peut commencer !")
            self.games.append(self.queue)
            Game(self.queue, self.currentIndex)
            self.queue= []

        
    
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
            
    def fin(self, data, gameid):
        game = [a for a in self.games if a.gameid==gameid]
        if len(game)==1:
            game[0].fin(data) 
            
    def close(self, gameid):
        try:
            game = [a for a in self.games if a.gameid==gameid][0]
            game.player0.Send({"action":"close"})
            game.player1.Send({"action":"close"})
        except:
            pass
    

class Game:
    
    def __init__(self, queue, currentIndex):

        # whose turn 
        self.turn = 0
        #owner map
        dico_parametres = {'dimensions_plateau': '7', 'nb_fantomes': '21', 'nb_joueurs': '2', 'mode_joueur_1': 'manuel', 'mode_joueur_2': 'manuel', 'mode_joueur_3': 'manuel', 'mode_joueur_4': 'manuel', 'niveau_ia_1': '1', 'niveau_ia_2': '1', 'niveau_ia_3': '1', 'niveau_ia_4': '1', 'pseudo_joueur_1': 0, 'pseudo_joueur_2': 1, 'pseudo_joueur_3': '', 'pseudo_joueur_4': '', 'nb_fantomes_mission': '3', 'nb_joker': '1', 'points_pepite': '1', 'points_fantome': '5', 'points_fantome_mission': '20', 'bonus_mission': '40'}
        self.plateau_jeu=plateau(2,[0,1],[0,0],7,dico_parametres)
        #initialize the players including the one who started the game
        self.joueur_0= queue[0]
        self.joueur_1=queue[1]
        #gameid of game
        self.gameid=currentIndex
        
    
    def rotation(self,data,num):
        if num==self.turn:
            self.plateau_jeu.carte_a_jouer.orientation[0],self.plateau_jeu.carte_a_jouer.orientation[1],self.plateau_jeu.carte_a_jouer.orientation[2],self.plateau_jeu.carte_a_jouer.orientation[3]=self.plateau_jeu.carte_a_jouer.orientation[3],self.plateau_jeu.carte_a_jouer.orientation[0],self.plateau_jeu.carte_a_jouer.orientation[1],self.plateau_jeu.carte_a_jouer.orientation[2]
            
            self.joueur_0.Send(data)
            self.joueur_1.Send(data)
        
        
    def insertion(self,data, num, coord):
        if num==self.turn:
            self.plateau_jeu.deplace_carte(coord)
            
            self.joueur_0.Send(data)
            self.joueur_1.Send(data)
    
    def deplacement(self,data, num, event):
        
        if num==self.turn:
            deplace = self.plateau_jeu.deplace_joueur(num,event)
            self.plateau_jeu.compte_points(num,deplace)
            
            self.joueur_0.Send(data)
            self.joueur_1.Send(data)
            
            
    def changejoueur(self,data, num):
        
        if num==self.turn:
            self.turn = 0 if self.turn else 1
            self.joueur_0.Send({"action":"yourturn", "tour":True if self.turn==1 else False})
            self.joueur_1.Send({"action":"yourturn", "tour":True if self.turn==0 else False})

            
    def fin(self,data):
        
        if self.plateau_jeu.dico_joueurs[0].points > self.plateau_jeu.dico_joueurs[1].points :
            self.joueur_0.Send({"action":"victoire"})
            self.joueur_1.Send({"action":"echec"})
        
        elif self.plateau_jeu.dico_joueurs[0].points < self.plateau_jeu.dico_joueurs[1].points :
            self.joueur_1.Send({"action":"victoire"})
            self.joueur_0.Send({"action":"echec"})
        
    
    
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
    
    
    
