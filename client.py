# -*- coding: utf-8 -*-
"""
Created on Fri Jan  3 09:16:52 2020

@author: eloda
"""

from PodSixNet.Connection import ConnectionListener, connection
from time import sleep

import pygame
from pygame.locals import *
import numpy as np
import random as rd
import pickle
import glob
import copy as copy
import math
from moviepy.editor import *

from moteur import *
from objets_graphiques import *
from parametrisation import *
from IA import *
    
#---------------------------------------Défintion des instructions graphiques------------------------------
    
class mine_hantee(ConnectionListener):
    
    
    def Network_startgame(self, data):
        self.running=True
        self.joueur_id=data["joueur_id"]
        self.gameid=data["gameid"]
    
    def __init__(self):
    
        pygame.init()
        
        #Ouverture de la fenêtre Pygame
        self.fenetre = pygame.display.set_mode((1200, 700),pygame.RESIZABLE)
        
        #Creation des images du menu
        self.fond_menu = pygame.image.load("fond_menu.png").convert()
        self.fond_uni = pygame.image.load("fond_uni.png").convert()
        
        #Création de la police du jeu
        self.police = pygame.font.Font("coda.ttf", 20) #Load font object.
        self.police_small = pygame.font.Font("coda.ttf", 17) #Load font object.
        
        #définition des couleurs
        self.COLOR_INACTIVE = pygame.Color('lightskyblue3')
        self.COLOR_ACTIVE = pygame.Color('dodgerblue2')
        self.COLOR_ERROR = pygame.Color('tomato2')
        
        #définition des polices
        self.police1=pygame.font.SysFont('calibri', 15)
        self.police2=pygame.font.SysFont('calibri', 25)
        self.police3=pygame.font.SysFont('calibri', 35)
        
        self.dico_stop={}
        
        self.Connect()
        address=input("Address of Server: ")
        try:
            if not address:
                host, port="localhost", 8000
            else:
                host,port=address.split(":")
            self.Connect((host, int(port)))
        except:
            print("Error Connecting to Server")
            print("Usage:", "host:port")
            print("e.g.", "localhost:31425")
            exit()
            
        print("Labyrinthe client started")
        
        self.running=False
        while not self.running:
            self.Pump()
            connection.Pump()
            sleep(0.01)
            
        if self.joueur_id==0:
            self.turn=True
            joueur_0 = "Moi"
            joueur_1 = "Adversaire"
            
        else:
            self.turn=False
            joueur_0 = "Adversaire"
            joueur_1 = "Moi"
            
        dico_parametres = {'dimensions_plateau': '7', 'nb_fantomes': '21', 'nb_joueurs': '2', 'mode_joueur_1': 'manuel', 'mode_joueur_2': 'manuel', 'mode_joueur_3': 'manuel', 'mode_joueur_4': 'manuel', 'niveau_ia_1': '1', 'niveau_ia_2': '1', 'niveau_ia_3': '1', 'niveau_ia_4': '1', 'pseudo_joueur_1': joueur_0, 'pseudo_joueur_2': joueur_1, 'pseudo_joueur_3': '', 'pseudo_joueur_4': '', 'nb_fantomes_mission': '3', 'nb_joker': '1', 'points_pepite': '1', 'points_fantome': '5', 'points_fantome_mission': '20', 'bonus_mission': '40'}
        self.plateau_jeu=plateau(2,[joueur_0,joueur_1],[0,0],7,dico_parametres)
        
    
        
        
    def Network_close(self, data):
        exit()
        
    def Network_yourturn(self, data):
        self.turn = data["tour"]
        
    def Network_rotation(self, data):
        if data["num"] != joueur_id:
            self.plateau_jeu.carte_a_jouer.orientation[0],self.plateau_jeu.carte_a_jouer.orientation[1],self.plateau_jeu.carte_a_jouer.orientation[2],self.plateau_jeu.carte_a_jouer.orientation[3]=self.plateau_jeu.carte_a_jouer.orientation[3],self.plateau_jeu.carte_a_jouer.orientation[0],self.plateau_jeu.carte_a_jouer.orientation[1],self.plateau_jeu.carte_a_jouer.orientation[2]
            
    def Network_insertion(self, data):
        if data["num"] != joueur_id:
            self.plateau_jeu.deplace_carte(data["coord"])
    
    def Network_deplacement(self, data):
        if data["num"] != joueur_id:
            deplace = self.plateau_jeu.deplace_joueur(data["num"],data["event"])
            self.plateau_jeu.compte_points(data["num"],deplace)



    def affiche_plateau(plat,fenetre):
    
        #Création des images nécesssaires au plateau
        #fond = pygame.image.load("fond.jpg").convert()
        fond_ext = pygame.image.load("fond_ext.png").convert()
        mur1 = pygame.image.load("mur1.png").convert_alpha()
        mur2 = pygame.image.load("mur2.png").convert_alpha()
        mur3 = pygame.image.load("mur3.png").convert_alpha()
        mur4 = pygame.image.load("mur4.png").convert_alpha()
        liste_im_joueur = [pygame.image.load("joueur"+str(i)+".png").convert_alpha() for i in range(1,5)]
        fond_a_jouer = pygame.image.load("fond_carte_a_jouer.jpg").convert()
        fantome = pygame.image.load("fantome.png").convert_alpha()
        pepite = pygame.image.load("pepite.png").convert_alpha()
        indeplacable = pygame.image.load("indeplacable.png").convert_alpha()
    
        
        #Chargement du fond dans la fenetre 
        fenetre.blit(fond_ext,(0,0))
        #fenetre.blit(fond, (0,0))
        N = plat.N #on récupère la taille du plateau
         
        #Mise  à jour de la taille des images en fonction du nombre de cartes du plateau
        x_mur1 = 100
        y_mur1 = 100
        mur1 = pygame.transform.scale(mur1, (int(x_mur1*(7/N)),int(y_mur1*(7/N))))
        x_mur2 = 100
        y_mur2 = 100
        mur2 = pygame.transform.scale(mur2, (int(x_mur2*(7/N)),int(y_mur2*(7/N))))
        x_mur3 = 100
        y_mur3 = 100
        mur3 = pygame.transform.scale(mur3, (int(x_mur3*(7/N)),int(y_mur3*(7/N))))
        x_mur4 = 100
        y_mur4 = 100
        mur4 = pygame.transform.scale(mur4, (int(x_mur4*(7/N)),int(y_mur4*(7/N))))
        x_fond_a_jouer = 100
        y_fond_a_jouer = 100
        fond_a_jouer = pygame.transform.scale(fond_a_jouer,(int(x_fond_a_jouer*(7/N)),int(y_fond_a_jouer*(7/N))))
        x_fantome = fantome.get_width()
        y_fantome = fantome.get_height()
        fantome = pygame.transform.scale(fantome, (int(x_fantome*(7/N)),int(y_fantome*(7/N))))
        x_pepite = pepite.get_width()
        y_pepite = pepite.get_height()
        pepite  = pygame.transform.scale(pepite, (int(x_pepite *(7/N)),int(y_pepite*(7/N))))
        x_indeplacable = indeplacable.get_width()
        y_indeplacable = indeplacable.get_height()
        indeplacable  = pygame.transform.scale(indeplacable, (int(x_indeplacable*(7/N)),int(y_indeplacable*(7/N))))
        for i in range (4) :
            x_joueur = 60
            y_joueur = 60
            liste_im_joueur[i] = pygame.transform.scale(liste_im_joueur[i], (int(x_joueur*(7/N)),int(y_joueur*(7/N))))
        
        #Création de la police du jeu
        police = pygame.font.SysFont("calibri", int(20*7/N), bold=True) #Load font object.
        
        for i in range(len(plat.position)) :
            for j in range(len(plat.position)) :
                x=plat.dico_cartes[plat.position[i,j]].coord[0]*int(100*7/N)
                y=plat.dico_cartes[plat.position[i,j]].coord[1]*int(100*7/N)
                fenetre.blit(fond_a_jouer,(y,x))
    
    # Si on veut ajouter un graphisme pour les cartes déplaçables et indéplaçables
                           
                if plat.dico_cartes[plat.position[i,j]].deplacable==False :
                    fenetre.blit(indeplacable,(y,x))
                
                for k in range(len(plat.dico_cartes[plat.position[i,j]].orientation)) :
                    #fenetre.blit(fond_a_jouer,(y,x))
                    if plat.dico_cartes[plat.position[i,j]].orientation[k]==1 :
                        if k==0 :
                            fenetre.blit(mur1,(y,x))
                        elif k==1 :
                            fenetre.blit(mur4,(y,x))
                        elif k==2 :
                            fenetre.blit(mur2,(y,x))
                        elif k==3 :
                            fenetre.blit(mur3,(y,x))
                           
                           
                if plat.dico_cartes[plat.position[i,j]].presence_pepite==True:
                    fenetre.blit(pepite,(y,x))
                if plat.dico_cartes[plat.position[i,j]].id_fantome!=0 :
                    fenetre.blit(fantome,(y,x))
                    fenetre.blit(police.render(str(plat.dico_cartes[plat.position[i,j]].id_fantome),True,pygame.Color("#FFFFFF")),(y+10,x+30))
                           
        for i in range(len(plat.dico_joueurs)) :
            x=plat.dico_joueurs[i].carte_position.coord[0]*int(100*7/N)
            y=plat.dico_joueurs[i].carte_position.coord[1]*int(100*7/N)
            fenetre.blit(liste_im_joueur[i],(y,x))
            
    #on place la carte à jouer dans le coin droite haut du plateau 
        x=750
        y=50
        fenetre.blit(fond_a_jouer,(x,y))
        for k in range(len(plat.carte_a_jouer.orientation)):
            if plat.carte_a_jouer.orientation[k]==1 :
                if k==0 :
                   fenetre.blit(mur1,(x,y))
                elif k==1 :
                   fenetre.blit(mur4,(x,y))
                elif k==2 :
                   fenetre.blit(mur2,(x,y))
                elif k==3 :
                   fenetre.blit(mur3,(x,y))
        
        if plat.carte_a_jouer.presence_pepite==True:
            fenetre.blit(pepite,(x,y))
               
                   
    def actualise_fenetre(plateau,fenetre,joueur,info,bouton,etape_texte):
        """
        fonction pour actualiser l'affichage dans la fonction jeu
        """
        self.affiche_plateau(plateau,fenetre)
        liste_im_joueur = [pygame.image.load("joueur"+str(i)+".png").convert_alpha() for i in range(1,5)]
    
        for i in range(len(plateau.dico_joueurs)) :
                    fenetre.blit(liste_im_joueur[i],(1030,320+i*80))
                    fenetre.blit(police.render(str(plateau.dico_joueurs[i].nom) + " : ",False,pygame.Color("#000000")),(800,340+i*80))
                    fenetre.blit(police.render("Score : "+str(plateau.dico_joueurs[i].points),False,pygame.Color("#000000")),(800,340+i*80+20))
                    fenetre.blit(police.render("Ordre de mission : "+str(sorted(plateau.dico_joueurs[i].fantome_target)),False,pygame.Color("#000000")),(800,340+i*80+40))
    
                    #test texte pour afficher le joueur qui joue
        fenetre.blit(police.render("C'est a "+str(joueur.nom)+" de jouer",False,pygame.Color(0,0,0)),(800,240))
     
        #affichage du message d'erreur
        for i in range(len(info)) :                       
            fenetre.blit(police.render(info[i],False,pygame.Color("#000000")),(760,180+i*20))
                                       
        fenetre.blit(police.render(etape_texte,False,pygame.Color("#000000")),(760,160))
                                                                 
                                                                 
        bouton.draw(fenetre)
                                                                 
        pygame.display.flip()
    

    def game(self):
                
        #On vérifie que c'est bien au tour de ce joueur

        information="" #Initialisation du texte d'erreur
        etape=""
        
        self.afficher_commandes(debut=True)
        afficher_commandes_button=Bouton(725,5,150,40,"Commandes")
        
        self.actualise_fenetre(self.plateau_jeu,self.fenetre,joueur,information,afficher_commandes_button,etape)

        #premiere etape : rotation et insertion de la carte
        #On parcours la liste de tous les événements reçus tant qu'une carte n'a pas été insérée
        self.dico_stop["test_carte"]=True
        self.dico_stop["test_entree"]=True
        
        
        while self.dico_stop["test_carte"]!=False:
            
            self.plateau_jeu.etape_jeu=joueur.nom+"_"+"inserer-carte"
            etape="Tourner la carte avec R, cliquer pour insérer"
            
            for event in pygame.event.get():   
                
                afficher_commandes_button.handle_event(event,self.afficher_commandes)
                
                #Si on appuie sur R, rotation de la carte à jouer
                if event.type == KEYDOWN and event.key == K_r: 
                    self.plateau_jeu.carte_a_jouer.orientation[0],self.plateau_jeu.carte_a_jouer.orientation[1],self.plateau_jeu.carte_a_jouer.orientation[2],self.plateau_jeu.carte_a_jouer.orientation[3]=self.plateau_jeu.carte_a_jouer.orientation[3],self.plateau_jeu.carte_a_jouer.orientation[0],self.plateau_jeu.carte_a_jouer.orientation[1],self.plateau_jeu.carte_a_jouer.orientation[2]
                    self.Send({"action": "rotation", "num": self.joueur_id, "gameid": self.gameid})

                #ajouter la carte lorsque l'utilisateur clique dans le plateau
                
                elif event.type == MOUSEBUTTONDOWN : 
                    #clic gauche : insertion de la carte à jouer
                    if event.button==1: 

                        coord=[int(math.floor(event.pos[1]/700*self.plateau_jeu.N)),int(math.floor(event.pos[0]/700*self.plateau_jeu.N))]
                        
                        test_inser=self.plateau_jeu.deplace_carte(coord)
                       
                        if test_inser==False :
                            information=["Insertion impossible"]
                        #Sinon, on finit cette section du tour

                        else :
                            information=""
                            self.Send({"action": "insertion", "coord":coord, "num": self.joueur_id, "gameid": self.gameid})

                            self.dico_stop["test_carte"]=False
                            

                elif event.type == KEYDOWN and event.key == K_SPACE :
                    self.pause()
                
                elif event.type == QUIT:
                    self.dico_stop = dict.fromkeys(self.dico_stop, False)
                    
            self.actualise_fenetre(self.plateau_jeu,self.fenetre,joueur,information,afficher_commandes_button,etape)
                                        
                                
        #2e etape : On parcours les évènements tant que le joueur n'a pas appuyé sur entrée ou tant qu'il peut encore se déplacer
        #initialisation à la position du joueur
        
        carte_actuelle=joueur.carte_position
        joueur.cartes_explorees=[carte_actuelle]
        cartes_accessibles=self.plateau_jeu.cartes_accessibles1(carte_actuelle)
        self.plateau_jeu.etape_jeu=joueur.nom+"_"+"deplacement"
        information=""
        
        #initialiser un marqueur pour l'animation de capture du fantôme
        premiere_capture=True
        #parcours des evenements
        #Tant que le joueur ne passe pas son tour et peut encore se deplacer
        while self.dico_stop["test_entree"]==True and len(cartes_accessibles)>0:
            
            etape="Déplacer avec les flèches, entrée pour finir"
            
            for event in pygame.event.get():
                
                #Correction pour supprimer les cartes explorees des cartes accessibles
                for carte_ex in joueur.cartes_explorees:
                    if carte_ex in cartes_accessibles:
                        cartes_accessibles.remove(carte_ex)
                        
                afficher_commandes_button.handle_event(event,self.afficher_commandes)
                
                #deplacement
                if event.type == KEYDOWN and (event.key == K_UP or event.key == K_LEFT or event.key == K_DOWN or event.key == K_RIGHT) : #touches directionnelles : déplacement du joueur
                    deplace = self.plateau_jeu.deplace_joueur(j,event.key)
                    if isinstance(deplace, carte) == True: #Si le déplacement était possible, on affiche ce que le joueur a potentiellement gagné
                        information=self.plateau_jeu.compte_points(j,deplace)
                        self.Send({"action": "deplacement", "event":event.key, "num": self.joueur_id, "gameid": self.gameid})
                        #si le joueur capture un fantome, on lance l'animation de capture
                        if joueur.capture_fantome == True and premiere_capture==True:
                            clip.preview()
                            premiere_capture=False
                    else: #Sinon on affiche la raison pour laquelle le déplacement n'était pas possible
                        information=deplace
                    
                    joueur.cartes_explorees.append(carte_actuelle)
                    carte_actuelle=joueur.carte_position
                    cartes_accessibles=self.plateau_jeu.cartes_accessibles1(carte_actuelle)
                    
            
                #fin de tour
                if event.type == KEYDOWN and (event.key== K_RETURN):
                    self.dico_stop["test_entree"]=False
                    self.Send({"action": "changejoueur", "num": self.joueur_id, "gameid": self.gameid})

                    information=""
                
                    
                elif event.type == KEYDOWN and event.key == K_SPACE :
                    pause()
                    
                elif event.type == QUIT:
                    self.dico_stop = dict.fromkeys(self.dico_stop, False)
                    
            #Update l'écran                                                                
            self.actualise_fenetre(self.plateau_jeu,self.fenetre,joueur,information,afficher_commandes_button,etape)


        #Fin du tour du joueur : On ré-initialise cartes_explorees et capture_fantome
        joueur.cartes_explorees = [carte_actuelle]
        joueur.capture_fantome = False
        

        if self.plateau_jeu.id_dernier_fantome==self.plateau_jeu.nbre_fantomes :
            
            self.fin_du_jeu([[j.nom,j.points] for j in self.plateau_jeu.dico_joueurs])
   

            
    def fin_du_jeu(self,scores) :
        
        self.dico_stop = dict.fromkeys(self.dico_stop, False)
        self.dico_stop["fin"]=True
        
        def getKey(elem):
            return elem[1]
        
        scores.sort(key=getKey,reverse=True)
        
        self.fenetre.blit(self.fond_uni,(0,0))
        
        self.fenetre.blit(self.police3.render(scores[0][0]+" a gagné!",False,pygame.Color("#000000")),(500,100))
        
        retour_menu_button=Bouton(500,600,200,50,"Retour au menu")
        
        retour_menu_button.draw(self.fenetre)
        
        for i in range(len(scores)) :
            self.fenetre.blit(self.police3.render("Score du joueur "+str(scores[i][0])+" : "+str(scores[i][1]),False,pygame.Color("#000000")),(500,200+i*100))
    
        pygame.display.flip()
        
        while self.dico_stop["fin"]==True :
            
            for event in pygame.event.get() :
                
                retour_menu_button.handle_event(event,self.menu)
                    
                if event.type == pygame.QUIT :
                    self.dico_stop = dict.fromkeys(self.dico_stop, False)
                
                
                
                    
    def afficher_commandes(self,debut=False) :
    
        self.dico_stop["comm"]=True
        
        while self.dico_stop["comm"]==True :
        
            self.fenetre.blit(self.fond_uni,(0,0))
            
            self.fenetre.blit(self.police3.render("Commandes",True,pygame.Color("#000000")),(100,100))
            
            self.fenetre.blit(self.police2.render("R : tourner la carte.",False,pygame.Color("#000000")),(100,200))
            self.fenetre.blit(self.police2.render("Clic sur une carte déplaçable en périphérie du plateau : insérer la carte extérieure.",False,pygame.Color("#000000")),(100,250))
            self.fenetre.blit(self.police2.render("Flèches directionnelles : déplacer le joueur.",False,pygame.Color("#000000")),(100,300))
            self.fenetre.blit(self.police2.render("Entrée : finir le tour.",False,pygame.Color("#000000")),(100,350))
            self.fenetre.blit(self.police2.render("Espace : mettre en pause/Retour au jeu.",False,pygame.Color("#000000")),(100,400))
            
            if debut==False:                                                                                         
                self.fenetre.blit(self.police2.render("Appuyez sur espace pour revenir au jeu.",False,pygame.Color("#000000")),(100,500))
            else:
                self.fenetre.blit(self.police2.render("Appuyez sur espace pour commencer le jeu.",False,pygame.Color("#000000")),(100,500))                                                                                             
            
            pygame.display.flip() 
                                                            
            for event in pygame.event.get() :
                
                if event.type == KEYDOWN and event.key == K_SPACE :
                    self.dico_stop["comm"]=False
                    
                if event.type == pygame.QUIT :
                    self.dico_stop = dict.fromkeys(self.dico_stop, False)
             
                
                
    def pause(self) :
        
        self.nouvelle="jeu en pause"
        
        self.dico_stop["pause"]=True
        
        texte_sauv=""
        
        sauvegarder_button=Bouton(550,350,200,50,"Sauvegarder")
        retour_menu_button=Bouton(550,450,200,50,"Retour au menu")
        
        while self.dico_stop["pause"]==True :
                    
            self.fenetre.blit(self.fond_uni,(0,0))
        
            self.fenetre.blit(self.police.render("Pause",True,pygame.Color("#000000")),(600,200))
                                                                 
            sauvegarder_button.draw(self.fenetre)
            retour_menu_button.draw(self.fenetre)
                                      
            self.fenetre.blit(self.police.render(texte_sauv,True,pygame.Color("#000000")),(550,550))
                                                                    
            pygame.display.flip() #Update l'écran
            
            for event in pygame.event.get():   #On parcours la liste de tous les événements reçus
                
                sauvegarder_button.handle_event(event,self.sauvegarder)
                retour_menu_button.handle_event(event,self.menu)
                    
                if event.type == KEYDOWN and event.key == K_SPACE :
                    self.dico_stop["pause"]=False
                    
                if event.type == QUIT:     #Si un de ces événements est de type QUIT
                    self.dico_stop = dict.fromkeys(self.dico_stop, False)
                    
  
    


mn = mine_hantee()
mn.game()
pygame.quit()