# -*- coding: utf-8 -*-
"""
Created on Fri Jan  3 09:12:18 2020

@author: eloda
"""

import PodSixNet.Channel
import PodSixNet.Server
from time import sleep
import copy as copy


from moteur import *
from objets_graphiques import *


class ClientChannel(PodSixNet.Channel.Channel):
    """
    Classe représentant un client. 
    Composée des méthodes permettant de recevoir les actions envoyées par les clients.
    Chaque méthode prend en entrée data : le dictionnaire des données envoyées 
    par le client.
    """
    
    def Network(self, data):
        print(data)
    
    def Network_myaction(self, data):
        print("myaction:", data)
        
        
    def Network_rotation(self, data):
        """.
        Méthode activée quand un client effectue une rotation de carte.
        Appelle la méthode rotation de la classe server en lui passant les infos
        d'entrées.
        """
        num = data["num"]
        self.gameid = data["gameid"]
        
        self._server.rotation(data,self.gameid, num)
 
    def Network_insertion(self, data):
        """
        Méthode activée quand un client effectue une insertion de carte dans
        le plateau.
        Appelle la méthode insertion de la classe server en lui passant les infos
        d'entrées.
        """
        num = data["num"]
        coord = data["coord"]
        self.gameid = data["gameid"]
        
        self._server.insertion(data,self.gameid, num,coord)
        
    def Network_deplacement(self, data):
        """
        Méthode activée quand un client effectue un déplacement sur le plateau.
        Appelle la méthode deplacement de la classe server en lui passant les infos
        d'entrées.
        """
        num = data["num"]
        event = data["event"]
        self.gameid = data["gameid"]
        
        self._server.deplacement(data,self.gameid, num, event)
        
    def Network_changejoueur(self, data):
        """
        Méthode activée quand lors du changement de joueur.
        Appelle la méthode changejoueur de la classe server en lui passant les infos
        d'entrées.
        """

        num = data["num"]
        self.gameid = data["gameid"]
        self._server.changejoueur(data,self.gameid, num)
    
    def Network_fin(self, data):
        """
        Méthode activée lorsque le jeu est terminé.
        Appelle la méthode fin de la classe server en lui passant les infos
        d'entrées.
        """
        self.gameid = data["gameid"]
        
        self._server.fin(data,self.gameid)
        
    def Network_quitter(self, data):
        """
        Méthode activée quand un client quitte le jeu.
        Appelle la méthode quitter de la classe server en lui passant les infos
        d'entrées.
        """

        self.gameid = data["gameid"]
        num = data["num"]
        
        self._server.quitter(data,self.gameid,num)
        
        
    def Close(self):
        """
        Méthode activée quand le serveur est fermé.
        Appelle la méthode close de la classe server en lui passant les infos
        d'entrées.
        """
        self._server.close(self.gameid)
        
    
    
class MineServer(PodSixNet.Server.Server):
    """
    Classe représentant le serveur.
    Gère les connections des clients et les différentes parties simultanées.
    """
 
    channelClass = ClientChannel
    
    def __init__(self, *args, **kwargs):
        """
        Appelle l'initialisation du serveur PodSixNet .
        Initialise :
            games : la liste des parties en train d'être jouées 
            queue : la liste des joueurs 
            currentIndex : l'index de la partie
        """
        
        PodSixNet.Server.Server.__init__(self, *args, **kwargs)
        self.games = []
        self.queue = []
        self.currentIndex=0
        
    
    def Connected(self, channel, addr):
        """
        Méthode appelée lorsqu'un client se connecte au serveur.
        Si un seul client est connecté, le stocke dans la queue et attend un autre client.
        Si un deuxième client se connecte, créé une instance de Game pour créer 
        le jeu et l'ajoute à la liste games.
        Envoie toutes les informations nécessaires à la création d'un plateau
        identique à celui créé ici aux clients (car une partie des paramètres 
        d'un plateau lors de sa création sont aléatoires), ainsi que les infos identifiant
        la partie et chaque joueur.
        """
        
        print('nouvelle connexion:', channel)
        if self.queue==[]:
            print("en attente d'un autre joueur...")
            self.currentIndex+=1
            channel.gameid=self.currentIndex
            self.queue.append(channel)
            print(self.queue)
        else:
            channel.gameid=self.currentIndex
            self.queue.append(channel)
            print(self.queue)
            jeu = Game(self.queue, self.currentIndex)
            plat = jeu.plateau_jeu
            self.games.append(jeu)
            data0 = {"action": "startgame", "gameid": self.currentIndex}
            
            fant_target0 = plat.dico_joueurs[0].fantome_target
            fant_target1 = plat.dico_joueurs[1].fantome_target
            for j in range(len(fant_target0)):
                fant_target0[j] = int(fant_target0[j])
                fant_target1[j] = int(fant_target1[j])
            data0["fant_target0"] = fant_target0
            data0["fant_target1"] = fant_target1
            
            ori_carte_ext = list(plat.carte_a_jouer.orientation)
            for j in range(len(ori_carte_ext)):
                ori_carte_ext[j] = int(ori_carte_ext[j])
            data0["carte_a_jouer_or"] = ori_carte_ext
            
            for i in range((plat.N)**2):
                orientation = list(plat.dico_cartes[i].orientation)
                for j in range(len(orientation)):
                    orientation[j] = int(orientation[j])
                fantome = int(plat.dico_cartes[i].id_fantome)
                data0[str(i)+"_carteor"] = orientation
                data0[str(i)+"_cartefant"] = fantome
                
            data1 = copy.deepcopy(data0)
            data0["joueur_id"] = 0
            data1["joueur_id"] = 1
            
            #print(data0)
            self.queue[0].Send(data0)
            self.queue[1].Send(data1)
            print("La partie peut commencer !")
            self.queue= []

        
    
    def rotation(self, data, gameid, num):
        """
        Méthode permettant de trouver la partie à laquelle se réfère l'action
        envoyée par le client, puis appelle la méthode adéquate dans Game.
        """
        game = [a for a in self.games if a.gameid==gameid]
        if len(game)==1:
            game[0].rotation(data, num)
        
    
    def insertion(self, data, gameid, num, coord):
        """
        Méthode permettant de trouver la partie à laquelle se réfère l'action
        envoyée par le client, puis appelle la méthode adéquate dans Game.
        """
        game = [a for a in self.games if a.gameid==gameid]
        if len(game)==1:
            game[0].insertion(data, num, coord)
            
    def deplacement(self, data, gameid, num, event):
        """
        Méthode permettant de trouver la partie à laquelle se réfère l'action
        envoyée par le client, puis appelle la méthode adéquate dans Game.
        """
        game = [a for a in self.games if a.gameid==gameid]
        if len(game)==1:
            game[0].deplacement(data, num, event)
            
    def changejoueur(self, data, gameid, num):
        """
        Méthode permettant de trouver la partie à laquelle se réfère l'action
        envoyée par le client, puis appelle la méthode adéquate dans Game.
        """
        game = [a for a in self.games if a.gameid==gameid]
        if len(game)==1:
            game[0].changejoueur(data, num)
            
    def fin(self, data, gameid):
        """
        Méthode permettant de trouver la partie à laquelle se réfère l'action
        envoyée par le client, puis appelle la méthode adéquate dans Game.
        """
        game = [a for a in self.games if a.gameid==gameid]
        if len(game)==1:
            game[0].fin(data) 
            
    def quitter(self,data,gameid,num):
        """
        Méthode permettant de trouver la partie à laquelle se réfère l'action
        envoyée par le client, puis appelle la méthode adéquate dans Game.
        """
        game = [a for a in self.games if a.gameid==gameid]
        if len(game)==1:
            game[0].quitter(data, num)
        
            
    def close(self, gameid):
        """
        Méthode permettant de trouver la partie à laquelle se réfère la fermeture
        du serveur et d'appeler les méthodes close chez les 2 joueurs.
        """
        try:
            game = [a for a in self.games if a.gameid==gameid][0]
            game.player0.Send({"action":"close"})
            game.player1.Send({"action":"close"})
        except:
            pass
    

class Game:
    """
    Classe représentant une partie. 
    Initialise le plateau et contient les méthodes permettant de répercuter
    les actions faites par un client sur le plateau du serveur et envoyer les infos
    de ces actions à l'autre client.
    """
    
    def __init__(self, queue, currentIndex):
        """
        Initalise un plateau.
        Prend en entrée :
            - queue : la liste des 2 instances de channel correspondant aux 2 joueurs
            - currentIndex : l'identifiant de la partie (int)
        
        Initialise les attributs :
            - turn : 0 si c'est le tour du joueur 0, 1 si c'est le tour du joueur 1
            - plateau_jeu : instance de plateau
            - joueur_0 : instance de channel correspondant au joueur 0
            - joueurè1 : instance de channel correspondant au joueur 1
            - gameid : identifiant de la partie (int)
        """
        
        self.turn = 0
        dico_parametres = {'dimensions_plateau': '7', 'nb_fantomes': '21', 'nb_joueurs': '2', 'mode_joueur_1': 'manuel', 'mode_joueur_2': 'manuel', 'mode_joueur_3': 'manuel', 'mode_joueur_4': 'manuel', 'niveau_ia_1': '1', 'niveau_ia_2': '1', 'niveau_ia_3': '1', 'niveau_ia_4': '1', 'pseudo_joueur_1': 0, 'pseudo_joueur_2': 1, 'pseudo_joueur_3': '', 'pseudo_joueur_4': '', 'nb_fantomes_mission': '3', 'nb_joker': '1', 'points_pepite': '1', 'points_fantome': '5', 'points_fantome_mission': '20', 'bonus_mission': '40'}
        self.plateau_jeu=plateau(2,[0,1],[0,0],7,dico_parametres)

        self.joueur_0=queue[0]
        self.joueur_1=queue[1]

        self.gameid=currentIndex
        
    
    def rotation(self,data,num):
        """
        Méthode permettant de répercuter une rotation de carte sur le plateau du
        serveur et d'envoyer l'information au joueur qui ne joue pas.
        """

        if num==self.turn:
            self.plateau_jeu.carte_a_jouer.orientation[0],self.plateau_jeu.carte_a_jouer.orientation[1],self.plateau_jeu.carte_a_jouer.orientation[2],self.plateau_jeu.carte_a_jouer.orientation[3]=self.plateau_jeu.carte_a_jouer.orientation[3],self.plateau_jeu.carte_a_jouer.orientation[0],self.plateau_jeu.carte_a_jouer.orientation[1],self.plateau_jeu.carte_a_jouer.orientation[2]
            if self.turn == 0:
                self.joueur_1.Send(data)
            else:
                self.joueur_0.Send(data)
            
        
        
    def insertion(self,data, num, coord):
        """
        Méthode permettant de répercuter une insertion de carte sur le plateau du
        serveur et d'envoyer l'information au joueur qui ne joue pas.
        """
        if num==self.turn:
            self.plateau_jeu.deplace_carte(coord)
            
            if self.turn == 0:
                self.joueur_1.Send(data)
            else:
                self.joueur_0.Send(data)
            
    
    def deplacement(self,data, num, event):
        """
        Méthode permettant de répercuter un déplacement du joueur dont c'est le tour
        sur le plateau du serveur ainsi que les points gagnés grâce à ce 
        déplacement et d'envoyer l'information au joueur qui ne joue pas.
        """
        
        if num==self.turn:
            deplace = self.plateau_jeu.deplace_joueur(num,event)
            self.plateau_jeu.compte_points(num,deplace)
            
            if self.turn == 0:
                self.joueur_1.Send(data)
            else:
                self.joueur_0.Send(data)
            
            
            
    def changejoueur(self,data, num):
        """
        Méthode permettant de changer de joueur en modifiant l'attribut turn
        du serveur et des 2 joueurs.
        """
        
        print(self.joueur_1,self.joueur_0)
        if num==self.turn:
            if self.turn == 0:
                self.turn = 1
                self.joueur_1.Send({"action":"changejoueur", "tour":True})
                self.joueur_0.Send({"action":"changejoueur", "tour":False})
                
            else:
                self.turn = 0
                self.joueur_0.Send({"action":"changejoueur", "tour":True})
                self.joueur_1.Send({"action":"changejoueur", "tour":False})
            

            
    def fin(self,data):
        """
        Méthode activée à la fin du jeu. Active la méthode victoire chez le joueur
        victorieux et la méthode echec chez le joueur perdant.
        """
        
        if self.plateau_jeu.dico_joueurs[0].points > self.plateau_jeu.dico_joueurs[1].points :
            self.joueur_0.Send({"action":"victoire"})
            self.joueur_1.Send({"action":"echec"})
        
        elif self.plateau_jeu.dico_joueurs[0].points < self.plateau_jeu.dico_joueurs[1].points :
            self.joueur_1.Send({"action":"victoire"})
            self.joueur_0.Send({"action":"echec"})
            
    
    def quitter(self, data, num):
        """
        Méthode activée quand un joueur ferme le jeu. Envoie l'information à l'autre
        joueur. 
        """

        if num == 0:
            self.joueur_1.Send({"action":"abandonadversaire"})
        else:
            print("envoie joueur 0")
            self.joueur_0.Send({"action":"abandonadversaire"})
                
            
        
    
    
    
print("Serveur ouvert")


#En appuyant sur entrée sans préciser d'adresse, le serveur se connecte automatiquement
#au localhost.
address=input("Entrer une adresse de type Host:Port (entrée : adresse automatique localhost:8000): ")
if not address:
    host, port="localhost", 8000
    print("localhost, 8000")
    print("en attente de connexions...")
else:
    host,port=address.split(":")
    print("en attente de connexions...")

MineServe=MineServer(localaddr=(host, int(port)))

while True:
    MineServe.Pump()
    sleep(0.01)
    
    