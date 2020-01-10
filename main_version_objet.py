# -*- coding: utf-8 -*-
"""
Created on Mon Dec 30 18:02:06 2019

@author: eloda
"""

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
    
class mine_hantee():
    '''
    Classe qui contient les attributs et méthodes nécessaires à l'affichage 
    et à l'enchaînement des interfaces de jeu.
    Possède en attribut les objets pygame nécessaires au graphismes et les
    variables nécessaires au contrôle de l'enchaînement des méthodes.
    Chaque méthode correspond à une interface du jeu.
    '''
    
    def __init__(self):
        '''
        Méthode d'initialisation de la classe.
        Initialise les attributs servant aux graphismes du jeu (fenetre, les différents fonds,
        les différents polices, les couleurs nécessaires) selon des fichiers présents dans le 
        dossier racine ou des valeurs fixées.
        Initialise un dictionnaire vide à la variable qui contrôles l'activation des méthodes (dico_stop).
        '''
    
        #Initialisation de pygame
        pygame.init() 
    
        #Ouverture de la fenêtre Pygame
        self.fenetre = pygame.display.set_mode((1200, 700),pygame.RESIZABLE)
        
        #Creation des images du menu
        self.fond_menu = pygame.image.load("fond_menu.png").convert()
        self.fond_menu = pygame.transform.scale(self.fond_menu, (1200,700))
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
        
        #Initialisation du dictionnaire qui contrôle l'activation des méthodes
        self.dico_stop={}
    
    def menu(self):
        """
        Méthode permettant de créer et d'afficher le menu du jeu dans la fenêtre. 
        A partir de ce menu, l'utilisateur peut lancer une nouvelle partie
        ou charger une nouvelle partie par l'intermédiaire de boutons. 
        """
        #lancer la musique du menu
        pygame.mixer.music.load("musiqueretro.mp3")

        #Activation du menu par l'intermédiraire du dico_stop
        #Différente selon que l'on soit au début du jeu ou revenu au menu
        
        #Si c'est le début du jeu, on commence le dictionnaire par la clé intro
        if self.dico_stop=={} :
            self.dico_stop={"intro" : True}
            
        #Si c'est un retour au menu, on désactive toutes les méthodes
        #Sauf le menu via la clé intro
        elif any(value == True for value in self.dico_stop.values()):
            self.dico_stop = dict.fromkeys(self.dico_stop, False)
            self.dico_stop["intro"]=True
            
        #Sinon, fermeture des interfaces.
        else :
            self.dico_stop = dict.fromkeys(self.dico_stop, False)
        
        #définition des boutons pour lancer une nouvelle partie, ou en chrger une
        nouvelle_partie_button=Bouton(500,350,200,50,"Nouvelle partie")
        charger_partie_button=Bouton(500,450,200,50,"Charger une partie")
        
        #l'attribut qui indique si on est dans une nouvelle partie est remis à False
        #à chaque fois qu'on revient au menu
        self.nouvelle=False
        
        #l'attribut qui liste les parties sauvegardées est remis à jour
        #à chaque fois qu'on passe par le menu
        self.liste_sauv=glob.glob("sauvegarde*")
        self.liste_sauv=[int(self.liste_sauv[i][-1]) for i in range(len(self.liste_sauv))]
  
        #Tant que la méthode est activiée via la variable intro du dico_stop
        #on affiche le menu et les boutons du menu
        while self.dico_stop["intro"]==True:

            #actualisation de l'écran      
            pygame.display.flip()
            
            #fond du menu
            self.fenetre.blit(self.fond_menu,(0,0))
            #on lance la musique
            pygame.mixer.music.play()

            #dessin des boutons
            nouvelle_partie_button.draw(self.fenetre)
            charger_partie_button.draw(self.fenetre)
            
            #A tout moment, on récupère les interactions avec les opérateurs
            for event in pygame.event.get():
                
                #gestion des événements liés aux boutons
                nouvelle_partie_button.handle_event(event,self.nouvelle_partie)
                charger_partie_button.handle_event(event,self.charger_partie)
                
                #instructions de sortie
                if event.type == pygame.QUIT:
                    self.dico_stop = dict.fromkeys(self.dico_stop, False)
                    
        
            
    
    def game(self) :
        '''
        Méthode qui gère le déroulement du jeu.
        Cette méthode initialise le plateau ou le charge selon ce que l'opérateur a choisit.
        Elle passe ensuite les tours pour chaque joueur et gère les étapes de jeu grâce à dico_stop.
        En fonction du type de joueur, soit les actions de l'opérateur sont requises pour le tour de jeu,
        soit la méthode fait appel aux fonctions du fichier IA.
        Quand les conditions de fin de jeu sont réunies, la méthode fin_du_jeu est appelée.
        '''

        #Initialisation d'une nouvelle partie ou chargement d'une ancienne partie
        if self.nouvelle==False :
            self.plateau_jeu=pickle.load(open("sauvegarde "+str(self.num_partie),"rb"))
            #Désactivation de la méthode précédente
            self.dico_stop["aff_partie"]=False
            
        elif self.nouvelle==True :
            #Création d'un nouveau plateau
            
            #Lecture du fichier de paramétrage et initialisation des paramètres
            dico_parametres=lecture(fichier)
            nb_joueurs=int(dico_parametres['nb_joueurs'])
            dimensions_plateau=int(dico_parametres['dimensions_plateau'])
            liste_noms=[dico_parametres['pseudo_joueur_1'],dico_parametres['pseudo_joueur_2'],dico_parametres['pseudo_joueur_3'],dico_parametres['pseudo_joueur_4']]
            
            #création de la liste des niveaux pour pouvoir gérer différement les IA des joueurs réels
            liste_niveaux=[]
            for joueur in range(1,nb_joueurs+1):
                mode='mode_joueur_'+str(joueur)
                #si c'est un joueur normal, alors le niveau est de 0. 
                if dico_parametres[mode]=='manuel':
                    liste_niveaux=liste_niveaux+[0]
                #sinon on prend le niveau rentré par l'utilisateur
                else:
                    niveau='niveau_ia_'+str(joueur)
                    liste_niveaux=liste_niveaux+[int(dico_parametres[niveau])]
            
            self.plateau_jeu=plateau(nb_joueurs,liste_noms,liste_niveaux,dimensions_plateau,dico_parametres)

            #initialiser l'etape de jeu :
            self.plateau_jeu.etape_jeu=self.plateau_jeu.dico_joueurs[0].nom+"_"+"inserer-carte"
        #Si on retourne au jeu depuis la pause, rien n'est fait.
        else :
            pass
        
        
        
        #Au début du jeu, on affiche automatiquement les commandes.
        self.afficher_commandes(debut=True)
        pygame.mixer.music.stop()

        #Création du bouton qui permet d'afficher les commandes à tout moment.
        afficher_commandes_button=Bouton(725,5,150,40,"Commandes")
        N = self.plateau_jeu.N
        
        #tant que dico_stop["rester_jeu"] est True, on reste en jeu
        self.dico_stop["rester_jeu"]=True
        #Chargement de l'animation en cas de capture de fantome
        clip = VideoFileClip('animation.mp4')
        
        
        
        #Boucle du jeu. On joue tant qu'il reste des fantômes à attraper
        while self.plateau_jeu.id_dernier_fantome!=self.plateau_jeu.nbre_fantomes and self.dico_stop["rester_jeu"]==True:
    
            #Si on démarre le jeu depuis une sauvegarde, on récupère le joueur dont c'est le tour
            joueur_nom=self.plateau_jeu.etape_jeu.split("_")[0]
            joueur_index=[joueur.nom for joueur in self.plateau_jeu.dico_joueurs.values()].index(joueur_nom)
            joueur_actuel=self.plateau_jeu.dico_joueurs[joueur_index]
            
            #Tours de jeu
            #on parcourt chaque joueur à chaque tours.
            for j in self.plateau_jeu.dico_joueurs :
                
                #Si c'est le bon joueur, on joue son tour. Sinon, on on passe au joueur suivant
                if joueur_actuel==self.plateau_jeu.dico_joueurs[j]:
                    #Initialisation du texte d'information et du texte qui informe de l'étape
                    information=[""]
                    etape="" 
                    joueur=self.plateau_jeu.dico_joueurs[j]
                    #actualisation de la fenêtre à chaque début de tour
                    actualise_fenetre(self.plateau_jeu,self.fenetre,joueur,information,afficher_commandes_button,etape,joueur.nb_joker)
        
        
                    #Si le joueur est un joueur réel, il y'a 2 étapes dans le tour gérées par dico_stop
                    #et le plateau est modifié selon les actions de l'opérateur
                    if joueur.niveau == 0 :
                        #Première etape : rotation et insertion de la carte
                        #On parcourt la liste de tous les événements reçus tant qu'une carte n'a pas été insérée
                        self.dico_stop["test_carte"]=True
                        #On active aussi l'étape suivante qui se déroulera quand la carte aura été insérée
                        self.dico_stop["test_entree"]=True
                        
                        
                        while self.dico_stop["test_carte"]!=False:
                            #Mise à jour de l'étape du jeu et du message d'étape
                            self.plateau_jeu.etape_jeu=joueur.nom+"_"+"inserer-carte"
                            etape="Tourner la carte avec R, cliquer pour insérer"
                            
                            #Récupération des actions de l'opérateur
                            for event in pygame.event.get():   
                                #gestion des évènements liés au bouton 
                                afficher_commandes_button.handle_event(event,self.afficher_commandes)
                                #Si on appuie sur R, rotation de la carte à jouer
                                if event.type == KEYDOWN and event.key == K_r: 
                                    self.plateau_jeu.carte_a_jouer.orientation[0],self.plateau_jeu.carte_a_jouer.orientation[1],self.plateau_jeu.carte_a_jouer.orientation[2],self.plateau_jeu.carte_a_jouer.orientation[3]=self.plateau_jeu.carte_a_jouer.orientation[3],self.plateau_jeu.carte_a_jouer.orientation[0],self.plateau_jeu.carte_a_jouer.orientation[1],self.plateau_jeu.carte_a_jouer.orientation[2]
                                #Si on appuie sur J et qu'il reste un joker au joueur, déclenchement du joker
                                if event.type== KEYDOWN and event.key == K_j:
                                    if joueur.nb_joker==0:
                                        information=["Vous n'avez plus de joker"]
                                    #Si le joueur a un joker, on joue son tour avec une IA et on passe au joueur suivant
                                    else:
                                        self.tour_IA(joueur,information, afficher_commandes_button, etape, joker=True)
                                        self.dico_stop["test_carte"]=False
                                        self.dico_stop["test_entree"]=False
                                        joueur.nb_joker-=1
                                
                                #ajouter la carte lorsque l'utilisateur clique dans le plateau
                                elif event.type == MOUSEBUTTONDOWN : 
                                    
                                    #clic gauche : insertion de la carte à jouer
                                    if event.button==1: 
                                        
                                        #Test si le clic est dans le plateau ou en dehors et mise à jour du message d'erreur
                                        coord=[int(math.floor(event.pos[1]/700*self.plateau_jeu.N)),int(math.floor(event.pos[0]/700*self.plateau_jeu.N))]
                                        test_inser=self.plateau_jeu.deplace_carte(coord)
                                        
                                        if test_inser==False :
                                            information=["Insertion impossible"]
                                        
                                        #Sinon, on finit cette section du tour
                                        else :
                                            information=[""]
                                           
                                            self.dico_stop["test_carte"]=False
                                            
                                #Si la touche espace est enfoncée, lancement de la méthode de pause
                                elif event.type == KEYDOWN and event.key == K_SPACE :
                                    self.pause()
                                
                                #Instructions de sortie
                                elif event.type == QUIT:
                                    self.dico_stop = dict.fromkeys(self.dico_stop, False)
                            
                            #actualisation de la fenêtre
                            actualise_fenetre(self.plateau_jeu,self.fenetre,joueur,information,afficher_commandes_button,etape,joueur.nb_joker)
                           
    
                        #2e etape : On parcours les évènements tant que le joueur n'a pas appuyé sur entrée ou tant qu'il peut encore se déplacer
                        #initialisation à la position du joueur
                        
                        #On récupère la carte sur laquelle est le joueur, et on initialise les cartes explorées
                        carte_actuelle=joueur.carte_position
                        joueur.cartes_explorees=[carte_actuelle]
                        cartes_accessibles=self.plateau_jeu.cartes_accessibles1(carte_actuelle)
                        
                        #mise à jour de l'étape de jeu
                        self.plateau_jeu.etape_jeu=joueur.nom+"_"+"deplacement"
                        information=[""]
                        
                        #initialiser un marqueur pour l'animation de capture du fantôme
                        premiere_capture=True
                        #parcours des evenements
                        #Tant que le joueur ne passe pas son tour et peut encore se deplacer
                        while self.dico_stop["test_entree"]==True and len(cartes_accessibles)>0:
                            
                            #mise à jour de l'étape
                            etape="Déplacer avec les flèches, entrée pour finir"
                            
                            #parcours des entrées clavier/souris
                            for event in pygame.event.get():
                                
                                #Correction pour supprimer les cartes explorees des cartes accessibles
                                for carte_ex in joueur.cartes_explorees:
                                    if carte_ex in cartes_accessibles:
                                        cartes_accessibles.remove(carte_ex)
                                        
                                afficher_commandes_button.handle_event(event,self.afficher_commandes)
                                
                                #deplacement du joueur si il appuie sur une flèche directionnelle
                                if event.type == KEYDOWN and (event.key == K_UP or event.key == K_LEFT or event.key == K_DOWN or event.key == K_RIGHT) : #touches directionnelles : déplacement du joueur
                                    deplace = self.plateau_jeu.deplace_joueur(j,event.key)
                                    if isinstance(deplace, carte) == True: #Si le déplacement était possible, on affiche ce que le joueur a potentiellement gagné
                                        information=self.plateau_jeu.compte_points(j,deplace)
                                        #si le joueur capture un fantome, on lance l'animation de capture
                                        if joueur.capture_fantome == True and premiere_capture==True:
                                            clip.preview()
                                            premiere_capture=False
                                    #Sinon on affiche la raison pour laquelle le déplacement n'était pas possible
                                    else: 
                                        information=deplace
                                        
                                    #On met à jour les cartes explorées et la carte actuelle où se trouve le joueur
                                    joueur.cartes_explorees.append(carte_actuelle)
                                    carte_actuelle=joueur.carte_position
                                    cartes_accessibles=self.plateau_jeu.cartes_accessibles1(carte_actuelle)
                                    
                                
                                #fin de tour : "test_entree" est assigné à False, on sort de la boucle de deplacement
                                if event.type == KEYDOWN and (event.key== K_RETURN):
                                    self.dico_stop["test_entree"]=False
                                    information=[""]
                                
                                    
                                #Si la touche espace est enfoncée, lancement de la méthode de pause
                                elif event.type == KEYDOWN and event.key == K_SPACE :
                                    self.pause()
                                    
                                #Si on appuie sur quitter, fin du jeu   
                                elif event.type == QUIT:
                                    self.dico_stop = dict.fromkeys(self.dico_stop, False)
                                    
                            #Update l'écran                                                                
                            actualise_fenetre(self.plateau_jeu,self.fenetre,joueur,information,afficher_commandes_button,etape,joueur.nb_joker)
            
                    

                    ##Retour au test du niveau du joueur : si le joueur est une IA (joueur.niveau!=0)
                    else:
                        #on joue le tour de l'IA
                        self.tour_IA(joueur,information, afficher_commandes_button, etape, joker=False)
                        
                    #Fin du tour : On ré-initialise cartes_explorees et capture_fantome
                    joueur.cartes_explorees = [carte_actuelle]
                    joueur.capture_fantome = False
                    #On actualise etape_jeu pour passer au joueur suivant :
                    try :
                        joueur_suivant=self.plateau_jeu.dico_joueurs[joueur.id+1].nom
                    except :
                        joueur_suivant=self.plateau_jeu.dico_joueurs[0].nom
                    self.plateau_jeu.etape_jeu=str(joueur_suivant)+"_"+"inserer-carte"
    
                    #On remet test_carte et test_entrée à False pour la prochaine boucle
                    if self.dico_stop["test_carte"]==False and self.dico_stop["test_entree"]==False and self.dico_stop["rester_jeu"]==False:
                        break
            
                    #Si on a capturé tous les fantômes :
                    if self.plateau_jeu.id_dernier_fantome==self.plateau_jeu.nbre_fantomes :
                        #On récupère les scores, pour les afficher avec fin_du_jeu
                        scores=[]
                        for j in self.plateau_jeu.dico_joueurs:
                            joueur=self.plateau_jeu.dico_joueurs[j]
                            scores=scores+[[joueur.nom,joueur.points,joueur.fantome_target]]
                        self.fin_du_jeu(scores)

                #Fin du tour : On ré-initialise cartes_explorees et capture_fantome
                joueur.cartes_explorees = [joueur.carte_position]
                joueur.capture_fantome = False

                #On remet test_carte et test_entrée à False pour la prochaine boucle
                if self.dico_stop["test_carte"]==False and self.dico_stop["test_entree"]==False and self.dico_stop["rester_jeu"]==False:
                    break
        
                #Si on a capturé tous les fantômes :
                if self.plateau_jeu.id_dernier_fantome==self.plateau_jeu.nbre_fantomes :
                    #On récupère les scores, pour les afficher avec fin_du_jeu
                    scores=[]
                    for j in self.plateau_jeu.dico_joueurs:
                        joueur=self.plateau_jeu.dico_joueurs[j]
                        scores=scores+[[joueur.nom,joueur.points,joueur.fantome_target]]
                    self.dico_stop["rester_jeu"]==False
                    self.fin_du_jeu(scores)
                    break

            
            
            
            
            
    def tour_IA(self, joueur, information, afficher_commandes_button, etape, joker=False):
        """
        Méthode permettant à une IA de jouer son tour et d'afficher le tour de jeu de l'IA.
        Si Joker=True, cette méthode permet de jouer le Joker d'un joueur (en fait seuls les
        messages affichés changent..).
        Prend en entrée :
            - joueur une instance de type joueur
            - joker booléen True ou False
            - information, afficher_commandes_button et etape : inputs permettant le bon affichage
            des éléments déplacés par l'IA dans la fenêtre de jeu
        """
        #Mise à jour de l'étape du jeu 
        self.plateau_jeu.etape_jeu=joueur.nom+"_"+"inserer-carte"

        #Affichage de l'étape, suivant si le coup est une IA ou un joker
        if joker==True:
            etape = "Le Joker réfléchit !"
        else :
            etape = "L'"+joueur.nom+" réfléchit..."
        actualise_fenetre(self.plateau_jeu,self.fenetre,joueur,information,afficher_commandes_button,etape,joueur.nb_joker)
        
        #recuperer le coup à jouer en fonction du niveau de l'IA
        if joueur.niveau == 1:
            IA = IA_simple(joueur.id,self.plateau_jeu, output_type="alea")
        elif joueur.niveau == 2:
            IA = IA_simple(joueur.id,self.plateau_jeu, output_type="single")
        elif joueur.niveau == 3 or joker==True:
            coups=IA_simple(joueur.id,self.plateau_jeu, output_type="liste")
            IA=IA_monte_carlo(self.plateau_jeu, joueur.id, reps=100, liste_coups=coups, profondeur=3)
            IA=IA[1],IA[0],IA[2]
        #découpage du coup
        coord_inser, orientation, chemin = IA[0],IA[1],IA[2]
        
        #Mise à jour de l'affichage de etape
        if joker==True:
            etape = "Joker de "+str(joueur.nom)+"..."
        else :
            etape = "l'"+str(joueur.nom)+" joue.."
        actualise_fenetre(self.plateau_jeu,self.fenetre,joueur,information,afficher_commandes_button,etape,joueur.nb_joker)
        
        
        #Rotation de la carte
        for i in range(orientation):
            pygame.event.pump()
            self.plateau_jeu.carte_a_jouer.orientation[0],self.plateau_jeu.carte_a_jouer.orientation[1],self.plateau_jeu.carte_a_jouer.orientation[2],self.plateau_jeu.carte_a_jouer.orientation[3]=self.plateau_jeu.carte_a_jouer.orientation[3],self.plateau_jeu.carte_a_jouer.orientation[0],self.plateau_jeu.carte_a_jouer.orientation[1],self.plateau_jeu.carte_a_jouer.orientation[2]
            pygame.time.wait(200)
            pygame.event.pump()
            actualise_fenetre(self.plateau_jeu,self.fenetre,joueur,information,afficher_commandes_button,etape,joueur.nb_joker)
        
        #Insertion
        self.plateau_jeu.deplace_carte(coord_inser)
        pygame.time.wait(200)
        pygame.event.pump()
        actualise_fenetre(self.plateau_jeu,self.fenetre,joueur,information,afficher_commandes_button,etape,joueur.nb_joker)
        pygame.event.pump()

        #deplacement du joueur et decompte des points
        self.plateau_jeu.etape_jeu=joueur.nom+"_"+"deplacement"
        information=[""]
        for i in chemin :
            pygame.event.pump()
            joueur.carte_position = i
            information=self.plateau_jeu.compte_points(joueur.id,i)
            pygame.time.wait(200)
            pygame.event.pump()
            actualise_fenetre(self.plateau_jeu,self.fenetre,joueur,information,afficher_commandes_button,etape,joueur.nb_joker)

            
            
            
    def fin_du_jeu(self,scores) :
        """
        Méthode permettant d'afficher dans la fenêtre un message de fin de jeu contenant : 
        - le vainqueur de la partie.
        - le classement des joueurs.
        - les scores de chaque joueur.
        - les ordres de mission complétés.
        
        L'utilisateur peut alors choisir de quitter le jeu ou de revenir au menu de départ. 
        """

        #Toutes les méthodes sont désactivées sauf celle de fin du jeu.
        self.dico_stop = dict.fromkeys(self.dico_stop, False)
        self.dico_stop["fin"]=True

        #Fonction pour le tri par clé
        def getKey(elem):
            return elem[1]
        
        #tri des scores et des nom par ordre croissant de scores pour établir le classement
        scores.sort(key=getKey,reverse=True)
        
        #Affichage des scores et du gagnant
        self.fenetre.blit(self.fond_uni,(0,0))
        self.fenetre.blit(self.police3.render("Fin du jeu !",True,pygame.Color("#000000")),(500,50))
        self.fenetre.blit(self.police3.render(scores[0][0]+" a gagné!",False,pygame.Color("#000000")),(425,120))
        self.fenetre.blit(self.police3.render("Scores des joueurs : ",True,pygame.Color("#000000")),(200,200))
        
        #définition et dessin du bouton
        retour_menu_button=Bouton(500,600,200,50,"Retour au menu")
        retour_menu_button.draw(self.fenetre)
        
        #affichage des scores de joueurs
        for i in range(len(scores)) :
            self.fenetre.blit(self.police2.render(str(scores[i][0])+" : ",False,pygame.Color("#000000")),(200,275+i*100))
            self.fenetre.blit(self.police2.render("Score : "+str(scores[i][1]),False,pygame.Color("#000000")),(400,275+i*100))
            if len(scores[i][2])==0:
                self.fenetre.blit(self.police2.render("Ordre de mission complété",False,pygame.Color("#000000")),(600,275+i*100))
            else:
                self.fenetre.blit(self.police2.render("Ordre de mission non complété",False,pygame.Color("#000000")),(600,275+i*100))
        
        #actualisation de la fenêtre
        pygame.display.flip()

        while self.dico_stop["fin"]==True :
            for event in pygame.event.get() :
                #gestion des évènements liés au bouton
                retour_menu_button.handle_event(event,self.menu)
                #sortie du jeu
                if event.type == pygame.QUIT :
                    self.dico_stop = dict.fromkeys(self.dico_stop, False)
                    
                    
    def afficher_commandes(self,debut=False) :
        """
        Méthode permettant d'afficher dans la fenêtre les details des 
        commandes du jeu. 
        L'utilisateur peut revenir à la partie en appuyant sur 'Espace' 
        """
    
        #Activation de la méthode par le dico_stop
        self.dico_stop["comm"]=True
        
        while self.dico_stop["comm"]==True :
        
            #Affichage des commandes
            self.fenetre.blit(self.fond_uni,(0,0))
            self.fenetre.blit(self.police3.render("Commandes",True,pygame.Color("#000000")),(100,100))
            self.fenetre.blit(self.police2.render("R : tourner la carte.",False,pygame.Color("#000000")),(100,200))
            self.fenetre.blit(self.police2.render("Clic sur une carte déplaçable en périphérie du plateau : insérer la carte extérieure.",False,pygame.Color("#000000")),(100,250))
            self.fenetre.blit(self.police2.render("Flèches directionnelles : déplacer le joueur.",False,pygame.Color("#000000")),(100,300))
            self.fenetre.blit(self.police2.render("Entrée : finir le tour.",False,pygame.Color("#000000")),(100,350))
            self.fenetre.blit(self.police2.render("Espace : mettre en pause/Retour au jeu.",False,pygame.Color("#000000")),(100,400))
            self.fenetre.blit(self.police2.render("J : utiliser un joker.",False,pygame.Color("#000000")),(100,450))
            
            #Affichage différent si on est au début du jeu ou non
            if debut==False:                                                                                         
                self.fenetre.blit(self.police2.render("Appuyez sur espace pour revenir au jeu.",False,pygame.Color("#000000")),(100,500))
            else:
                #les commandes sont affichées en début de partie
                self.fenetre.blit(self.police2.render("Appuyez sur espace pour commencer le jeu.",False,pygame.Color("#000000")),(100,500))                                                                                             
            
            #actualisation de l'écran
            pygame.display.flip() 
                                                            
            for event in pygame.event.get() :
                #retour ou lancement de la partie
                if event.type == KEYDOWN and event.key == K_SPACE :
                    self.dico_stop["comm"]=False
                #sortie du jeu   
                if event.type == pygame.QUIT :
                    self.dico_stop = dict.fromkeys(self.dico_stop, False)
                
    def pause(self) :
        '''
        Méthode d'affichage qui permet de lancer les méthodes pour sauvegarder la partie en cours ou revenir au menu.
        Reste active tant que l'utilisateur n'a pas appuyé sur la touche espace, et quand elle est désactivée permet de revenir au jeu en cours à l'endroit précis 
        ou la méthode game en était.
        '''
        
        #Permet de ne pas changer le plateau quand on revient dans la méthode game
        self.nouvelle="jeu en pause"
        
        #Activation de la méthode
        self.dico_stop["pause"]=True
        
        #Création des boutons pour lancer la méthode sauvegarder et la méthode menu.
        sauvegarder_button=Bouton(550,350,200,50,"Sauvegarder")
        retour_menu_button=Bouton(550,450,200,50,"Retour au menu")
        
        while self.dico_stop["pause"]==True :
                    
            #Affichage de l'écran de pause
            self.fenetre.blit(self.fond_uni,(0,0))
        
            self.fenetre.blit(self.police.render("Pause",True,pygame.Color("#000000")),(600,200))
                                                                 
            sauvegarder_button.draw(self.fenetre)
            retour_menu_button.draw(self.fenetre)
                                      
                                                                    
            pygame.display.flip() #Update l'écran
            
            for event in pygame.event.get():   #On parcoure la liste de tous les événements reçus
                
                #Gestion des évènements liés aux boutons
                sauvegarder_button.handle_event(event,self.sauvegarder)
                retour_menu_button.handle_event(event,self.menu)
                    
                #Sortie de la pause
                if event.type == KEYDOWN and event.key == K_SPACE :
                    self.dico_stop["pause"]=False
                    
                #Instructions de sortie de jeu
                if event.type == QUIT:     
                    self.dico_stop = dict.fromkeys(self.dico_stop, False)
                    
                    
    def sauvegarder(self):
        '''
        Méthode qui permet de sauvegarder la partie en cours dans un fichier binaire grâce au module pickle.
        Affiche que la partie a été sauvegardée sur l'interface de pause.
        '''
        
        pickle.dump(self.plateau_jeu,open("sauvegarde "+str(self.num_partie),"wb"))
        
    def afficher_partie(self,num) :
        '''
        Méthode qui prend en argument le numéro de la partie qu'on veut charger, et attribue cette valeur à l'attribut num_partie de la classe ce qui permettra
        par la suite de charger le fichier correspondant pour initialiser le plateau.
        Cette méthode permet de lancer la méthode game ou bien de revenir en arrière pour choisir une autre partie à lancer.
        '''
        
        #Attribution du numéro de partie choisie à l'attribut permettant de charger le bon plateau
        self.num_partie=num
        
        #Désactivation de la méthode précédente et activation de cette méthode là
        self.dico_stop["charger"]=False
        self.dico_stop["aff_partie"]=True
        
        #Création des boutons permettant de lancer la méthode game, et permettant de revenir à la méthode précédente.
        lancer_partie_button=Bouton(800,300,200,50,"Lancer la partie")
        retour=Bouton(400,300,300,50,"Sélectionner autre partie")
        
        #Affichage de la partie sélectionnée
        self.fenetre.blit(police.render("Partie "+str(self.num_partie)+" sélectionnée",True,pygame.Color("#000000")),(800,100))
                                        
        while self.dico_stop["aff_partie"]==True :
            
            lancer_partie_button.draw(self.fenetre) 
            retour.draw(self.fenetre)
            
            #Actualisation de l'écran
            pygame.display.flip()    
            
            #On parcoure la liste de tous les événements reçus
            for event in pygame.event.get():   
                
                #Gestion des évènements liés aux boutons
                lancer_partie_button.handle_event(event,self.game)
                retour.handle_event(event,self.charger_partie)
                
                #Instruction de sortie du jeu
                if event.type == QUIT :
                    self.dico_stop = dict.fromkeys(self.dico_stop, False)

        
    def charger_partie(self):
        '''
        Méthode affichant la liste des parties sauvegardées sous forme de fichier binaire dans le dossier de base, et permettant de sélectionner la partie
        que l'on veut charger. Une fois qu'une des partie a été sélectionnée, lance la méthode suivante afficher_partie en lui passant en argument le numéro
        de la partie sélectionnée.
        '''
        
        #Activation de la méthode et désactivation de toute autre méthode
        self.dico_stop = dict.fromkeys(self.dico_stop, False)
        self.dico_stop["charger"]=True
        
        
        
        #Création des boutons permettant de sélectionner la partie voulue à partir de l'attribut contenant les numéros de partie
        if self.liste_sauv!=[] :
            boutons_charger_partie=[]
            for i in range(len(self.liste_sauv)) :
                boutons_charger_partie.append(Bouton(500,100+i*100,200,50,"Partie "+str(self.liste_sauv[i])))
                
        #Création du bouton de retour au menu
        retour_menu_button=Bouton(500,100+len(self.liste_sauv)*100,200,50,"Retour au menu")
            
        while self.dico_stop["charger"] ==True:
                    
            if self.liste_sauv!=[] :
                self.fenetre.blit(self.fond_uni,(0,0))  #On colle le fond du menu
                for i in range(len(self.liste_sauv)) :
                    boutons_charger_partie[i].draw(self.fenetre)
            #Si il n'y a pas de partie sauvegardée, on affiche pas les boutons mais un message                                                       
            else :
                self.fenetre.blit(self.fond_uni,(0,0))  #On colle le fond du menu
                self.fenetre.blit(police.render("Aucune partie sauvegardée",True,pygame.Color("#000000")),(450,100))
            
            retour_menu_button.draw(self.fenetre)
                
            #Actualisation de l'écran
            pygame.display.flip() 
            
            #On parcoure la liste de tous les événements reçus
            for event in pygame.event.get():  
                
                if self.liste_sauv!=[] :
                    for i in range(len(self.liste_sauv)) :
                        boutons_charger_partie[i].handle_event(event,self.afficher_partie,i+1)
                
                retour_menu_button.handle_event(event,self.menu)
                
                if event.type == QUIT:     #Si un de ces événements est de type QUIT
                    self.dico_stop = dict.fromkeys(self.dico_stop, False)
                    
    
                    
    def nouvelle_partie(self):
        """
        Méthode de paramétrisation d'une nouvelle partie : étape 1.
        Demande à l'utilisateur de choisir le nombre de joueurs.
        L'utilisateur peut valider son choix pour passer à la 
        deuxième étape de paramétrisation 
        ou revenir au menu principal. 
        """
        
        self.nouvelle=True
        
        #attribution du numéro de la partie
        if self.liste_sauv!=[]:
            self.num_partie=np.max(self.liste_sauv)+1
        else :
            self.num_partie=1
        
        self.dico_stop["intro"]=False
        self.dico_stop["nouvellepartie"]=True
        
        #initialisation des boutons valider et retour
        valider=Bouton(500,450,200,50,"Valider")
        retour=Bouton(500,550,200,50,"Retour")
        
        #initialisation des boxs pour le choix du nombre de joueurs
        choix_nb_joueur_2=ChoiceBox(475, 300, 50, 30, '2')
        choix_nb_joueur_3=ChoiceBox(575, 300, 50, 30, '3')
        choix_nb_joueur_4=ChoiceBox(675, 300, 50, 30, '4')
        choix_nb_joueurs=[choix_nb_joueur_2, choix_nb_joueur_3, choix_nb_joueur_4]
        
        #lecture du fichier de paramétrisation
        dico_parametres=lecture(fichier)
        #on stocke le choix entre les boutons dans le dictionnaire choix_final
        choix_final={}
        choix_final["fonction"]=self.parametrisation_1
        choix_final["nb_joueurs"]=dico_parametres['nb_joueurs'] 
        choix_final['test_null']=False
        choix_final['test_max']=False          
        #initialisation du nombre de joueurs à la valeur renseignée dans le fichier
        for choix in choix_nb_joueurs:
                if choix.text==choix_final["nb_joueurs"]:
                    choix.active=True
                    choix.color=self.COLOR_ACTIVE
        
        while self.dico_stop["nouvellepartie"]==True :
                    
            self.fenetre.blit(self.fond_uni,(0,0))
            
            #choix du nombre de joueurs 
            self.fenetre.blit(self.police3.render("Nouvelle partie!",True,pygame.Color("#000000")),(485,100))
            self.fenetre.blit(self.police3.render("Nombre de joueurs",True,pygame.Color("#000000")),(465,200))
            
            #dessin des boutons
            valider.draw(self.fenetre)  
            retour.draw(self.fenetre)
            
            #choix du nombre de joueurs
            for choix in choix_nb_joueurs:
                choix.draw(self.fenetre)
                if choix.active==True:
                    choix_final["nb_joueurs"]=choix.text
                                                                
            #actualisation de l'écran
            pygame.display.flip()
            
            for event in pygame.event.get():
                
                #gestion des boutons
                valider.handle_event(event,action=enregistrement_inputs, parametre_action=choix_final)
                retour.handle_event(event,action=self.menu)
                
                #actualisation du choix du nombre de joueurs
                for choix in choix_nb_joueurs:
                    choix.handle_event(event, choix_nb_joueurs)
                
                #arrêt du jeu
                if event.type == QUIT:   
                    self.dico_stop = dict.fromkeys(self.dico_stop, False)
            
    
    def parametrisation_1(self,dico_erreurs={}):
        """
        Méthode de paramétrisation d'une nouvelle partie : étape 2.
        Demande à l'utilisateur de renseigner les paramètres des 
        différents joueurs. 
        
        Prend en argument : 
            - dico_erreurs : dictionnaire contenant les paramètres 
            pour lesquels l'utilisateur a commis une erreur de saisie 
            ainsi que le type d'erreur (dictionnaire). Par défaut, 
            l'utilisateur n'a pas commis d'erreurs.
            
        L'utilisateur peut valider son choix pour passer à la 3ème étape 
        de paramétrisation ou revenir à l'étape précédente. 
        """
        
        self.dico_stop['nouvellepartie']=False
        self.dico_stop['parametrisation1']=True
        
        #stockage des paramètres choisis qui seront enregistrés
        dico_choix={}
        dico_choix['fonction']=self.parametrisation_2
        dico_choix['fonction_prec']=self.parametrisation_1
        #pour cette fonction, on testera la nullité des paramètres entrés. 
        dico_choix['test_null']=True
        #pour cette fonction, on ne testera pas le maximum des paramètres entrés. 
        dico_choix['test_max']=False
        
        #lecture du fichier de paramétrisation 
        dico_parametres=lecture(fichier)
        nb_joueurs=dico_parametres['nb_joueurs']
        
        #initialisation des boutons valider et retour
        valider=Bouton(850,600,200,50,"Valider")
        retour=Bouton(500,600,200,50,"Retour")
        
        #initialisation des inputbox (on en définit 4 même si les 4 ne sont pas forcément utilisées)
        input_box1=InputBox(350, 100, 150, 30, text=dico_parametres['pseudo_joueur_1'])
        input_box2=InputBox(350, 200, 150, 30, text=dico_parametres['pseudo_joueur_2'])
        input_box3=InputBox(350, 300, 150, 30, text=dico_parametres['pseudo_joueur_3'])
        input_box4=InputBox(350, 400, 150, 30, text=dico_parametres['pseudo_joueur_4'])
        input_boxes=[input_box1,input_box2,input_box3,input_box4]
        L_pseudos=['pseudo_joueur_1','pseudo_joueur_2','pseudo_joueur_3','pseudo_joueur_4']
        for k in range(0,len(input_boxes)):
            #remplissage du dictionnaire des choix
            dico_choix[L_pseudos[k]]=input_boxes[k].text
            #vérification des erreurs
            for erreur in dico_erreurs.keys():
                if L_pseudos[k]==erreur:
                    input_boxes[k].color=self.COLOR_ERROR
        
        #initialisation des boxs pour le choix des modes de jeu des joueurs
        choix_manuel_joueur_1=ChoiceBox(650, 100, 175, 30, 'manuel')
        choix_automatique_joueur_1=ChoiceBox(650, 140, 175, 30, 'automatique')
        choix_manuel_joueur_2=ChoiceBox(650, 200, 175, 30, 'manuel')
        choix_automatique_joueur_2=ChoiceBox(650, 240, 175, 30, 'automatique')
        choix_manuel_joueur_3=ChoiceBox(650, 300, 175, 30, 'manuel')
        choix_automatique_joueur_3=ChoiceBox(650, 340, 175, 30, 'automatique')
        choix_manuel_joueur_4=ChoiceBox(650, 400, 175, 30, 'manuel')
        choix_automatique_joueur_4=ChoiceBox(650, 440, 175, 30, 'automatique')
        choix_modes_joueurs=[[choix_manuel_joueur_1,choix_automatique_joueur_1],[choix_manuel_joueur_2,choix_automatique_joueur_2],[choix_manuel_joueur_3,choix_automatique_joueur_3],[choix_manuel_joueur_4,choix_automatique_joueur_4]]
        L_modes=['mode_joueur_1','mode_joueur_2','mode_joueur_3','mode_joueur_4']
        for k in range(0,len(L_modes)):
            dico_choix[L_modes[k]]=dico_parametres[L_modes[k]]
        
        #initialisation des boxs pour le choix des niveaux des joueurs
        choix_lvl_j1_1=ChoiceBox(1000, 140, 50, 30, '1')
        choix_lvl_j1_2=ChoiceBox(1050, 140, 50, 30, '2')
        choix_lvl_j1_3=ChoiceBox(1100, 140, 50, 30, '3')
        choix_lvl_j2_1=ChoiceBox(1000, 240, 50, 30, '1')
        choix_lvl_j2_2=ChoiceBox(1050, 240, 50, 30, '2')
        choix_lvl_j2_3=ChoiceBox(1100, 240, 50, 30, '3')
        choix_lvl_j3_1=ChoiceBox(1000, 340, 50, 30, '1')
        choix_lvl_j3_2=ChoiceBox(1050, 340, 50, 30, '2')
        choix_lvl_j3_3=ChoiceBox(1100, 340, 50, 30, '3')
        choix_lvl_j4_1=ChoiceBox(1000, 440, 50, 30, '1')
        choix_lvl_j4_2=ChoiceBox(1050, 440, 50, 30, '2')
        choix_lvl_j4_3=ChoiceBox(1100, 440, 50, 30, '3')
        choix_lvl_joueurs=[[choix_lvl_j1_1,choix_lvl_j1_2,choix_lvl_j1_3],[choix_lvl_j2_1,choix_lvl_j2_2,choix_lvl_j2_3],[choix_lvl_j3_1,choix_lvl_j3_2,choix_lvl_j3_3],[choix_lvl_j4_1,choix_lvl_j4_2,choix_lvl_j4_3]]
        L_lvl=['niveau_ia_1','niveau_ia_2','niveau_ia_3','niveau_ia_4']
        for k in range(0,len(L_lvl)):
            dico_choix[L_lvl[k]]=dico_parametres[L_lvl[k]]
        
        #initialisation des boutons sélectionnés en fonction des valeurs renseignées dans le fichier 
        #de configuration
        for k in range(0,len(choix_modes_joueurs)):
            for choix in choix_modes_joueurs[k]:
                if choix.text==dico_choix[L_modes[k]]:
                    choix.active=True
                    choix.color=self.COLOR_ACTIVE 
        for k in range(0,len(choix_lvl_joueurs)):
            for choix in choix_lvl_joueurs[k]:
                if choix.text==dico_choix[L_lvl[k]]:
                    choix.active=True
                    choix.color=self.COLOR_ACTIVE
        
        while self.dico_stop['parametrisation1']==True :
            
            #actualisation de l'écran
            pygame.display.flip()
            
            self.fenetre.blit(self.fond_uni,(0,0))
            
            #paramètres des joueurs
            self.fenetre.blit(self.police3.render("Paramètres des joueurs",True,pygame.Color("#000000")),(100,50))
            
            if len(dico_erreurs)!=0:
                self.fenetre.blit(self.police2.render("ERREUR : Renseignez tous les champs!",True,self.COLOR_ERROR),(550,50))
            
            for k in range(1,int(nb_joueurs)+1):
    
                self.fenetre.blit(self.police2.render("Joueur "+str(k)+": ",True,pygame.Color("#000000")),(100,(k*100)))
                self.fenetre.blit(self.police2.render("Pseudo",True,pygame.Color("#000000")),(250,(k*100)))
                self.fenetre.blit(self.police2.render("Mode",True,pygame.Color("#000000")),(550,(k*100)))
                    
                box=input_boxes[k-1]
                box.draw(self.fenetre)
                choix_manuel=choix_modes_joueurs[k-1][0]
                choix_automatique=choix_modes_joueurs[k-1][1]
                choix_manuel.draw(self.fenetre)
                #le joueur 1 est forcément manuel
                if k!=1:
                    choix_automatique.draw(self.fenetre)
                #si le mode automatique est activé, l'utilisateur peut choisir le niveau de l'ia. 
                #mais il ne peut pas choisir son nom
                if choix_automatique.active:
                    self.fenetre.blit(self.police2.render("Niveau",True,pygame.Color("#000000")),(900,45+(k*100)))
                    choix_lvl1=choix_lvl_joueurs[k-1][0]
                    choix_lvl2=choix_lvl_joueurs[k-1][1]
                    choix_lvl3=choix_lvl_joueurs[k-1][2]
                    choix_lvl1.draw(self.fenetre)
                    choix_lvl2.draw(self.fenetre)
                    choix_lvl3.draw(self.fenetre)
            
            #dessin des boutons
            valider.draw(self.fenetre)  
            retour.draw(self.fenetre)
                                              
            #actualisation de l'écran
            pygame.display.flip()
            
            for event in pygame.event.get():
                
                #gestion des boutons
                valider.handle_event(event,action=enregistrement_inputs, parametre_action=dico_choix)
                retour.handle_event(event,action=self.nouvelle_partie)
                
                #remplissage des inputboxs    
                for k in range(1,int(nb_joueurs)+1):
                    choix_manuel=choix_modes_joueurs[k-1][0]
                    choix_automatique=choix_modes_joueurs[k-1][1]
                    choix_manuel.handle_event(event,choix_modes_joueurs[k-1])
                    #le joueur 1 est forcément manuel
                    if k!=1:
                        choix_automatique.handle_event(event,choix_modes_joueurs[k-1])
                    if choix_automatique.active:
                        choix_lvl_joueurs[k-1][0].handle_event(event,choix_lvl_joueurs[k-1])
                        choix_lvl_joueurs[k-1][1].handle_event(event,choix_lvl_joueurs[k-1])
                        choix_lvl_joueurs[k-1][2].handle_event(event,choix_lvl_joueurs[k-1])
                        choix_lvl1=choix_lvl_joueurs[k-1][0]
                        choix_lvl2=choix_lvl_joueurs[k-1][1]
                        choix_lvl3=choix_lvl_joueurs[k-1][2]
                        if choix_lvl1.active:
                            dico_choix[L_lvl[k-1]]=choix_lvl1.text
                        elif choix_lvl2.active:
                            dico_choix[L_lvl[k-1]]=choix_lvl2.text
                        elif choix_lvl3.active:
                            dico_choix[L_lvl[k-1]]=choix_lvl3.text
                        input_boxes[k-1].text="Ordinateur"+str(k)
                        input_boxes[k-1].txt_surface=self.police2.render(input_boxes[k-1].text, True, input_boxes[k-1].color)
                        dico_choix[L_pseudos[k-1]]=input_boxes[k-1].text
                        dico_choix[L_modes[k-1]]="automatique"
                    else:
                        box=input_boxes[k-1]
                        box.handle_event(event)
                        dico_choix[L_pseudos[k-1]]=input_boxes[k-1].text
                        dico_choix[L_modes[k-1]]="manuel"
                        if input_boxes[k-1].text=="Ordinateur"+str(k):
                            input_boxes[k-1].text="Joueur"+str(k)
                            input_boxes[k-1].txt_surface=self.police2.render(input_boxes[k-1].text, True, input_boxes[k-1].color)
                
                #arrêt du jeu
                if event.type == QUIT:   
                    self.dico_stop = dict.fromkeys(self.dico_stop, False)
    
    def parametrisation_2(self,dico_erreurs={}):
        """
        Méthode de paramétrisation d'une nouvelle partie : étape 3.
        Demande à l'utilisateur de renseigner les paramètres avancés 
        de la partie. 
        
        Prend en argument : 
            - dico_erreurs : dictionnaire contenant les paramètres 
            pour lesquels l'utilisateur a commis une erreur de saisie 
            ainsi que le type d'erreur (dictionnaire). Par défaut, 
            l'utilisateur n'a pas commis d'erreurs.
            
        L'utilisateur peut valider son choix et lancer la partie 
        ou revenir à l'étape précédente. 
        """
       
        self.dico_stop['parametrisation1']=False
        self.dico_stop['parametrisation2']=True
        
        #lecture du fichier de paramétrisation 
        dico_parametres=lecture(fichier)
        
        #stockage des choix
        dico_choix={}
        dico_choix['fonction']=self.game
        dico_choix['fonction_prec']=self.parametrisation_2
        dico_choix['nb_joueurs']=dico_parametres['nb_joueurs']
        dico_choix['fonction_game']=self.game
        #pour cette fonction, on testera la nullité des paramètres entrés. 
        dico_choix['test_null']=True
        #pour cette fonction, on testera aussi le maximum des paramètres entrés. 
        dico_choix['test_max']=True
        
        #initialisation des boutons valider et retour
        valider=Bouton(900,300,200,50,"Lancer la partie !")
        retour=Bouton(900,400,200,50,"Retour")
        
        #définition des choicebox pour la taille du plateau
        taille_7=ChoiceBox(600, 110, 50, 30, '7')
        taille_11=ChoiceBox(650, 110, 50, 30, '11')
        taille_15=ChoiceBox(700, 110, 50, 30, '15')
        taille_19=ChoiceBox(750, 110, 50, 30, '19')
        taille_23=ChoiceBox(800, 110, 50, 30, '23')
        choix_taille=[taille_7, taille_11, taille_15, taille_19, taille_23]
        dico_choix['dimensions_plateau']=dico_parametres['dimensions_plateau']
        
        #initialisation des boutons sélectionnés en fonction des valeurs renseignées dans le fichier 
        #de configuration
        for choix in choix_taille:
            if choix.text==dico_choix['dimensions_plateau']:
                choix.active=True
                choix.color=self.COLOR_ACTIVE 
        
        #définition des inputboxs pour l'ensemble des paramètres restants
        #en initialisant les valeurs aux paramètres du fichier de paramétrisation. 
        ib_nb_fantomes=InputBox(600, 180, 150, 30, text=dico_parametres['nb_fantomes'], contenu='num')
        ib_nb_fantomes_mission=InputBox(600, 250, 150, 30, text=dico_parametres['nb_fantomes_mission'], contenu='num')
        ib_nb_joker=InputBox(600, 320, 150, 30, text=dico_parametres['nb_joker'], contenu='num')
        ib_points_pepite=InputBox(600, 390, 150, 30, text=dico_parametres['points_pepite'], contenu='num')
        ib_points_fantome=InputBox(600, 460, 150, 30, text=dico_parametres['points_fantome'], contenu='num')
        ib_points_fantome_mission=InputBox(600, 530, 150, 30, text=dico_parametres['points_fantome_mission'], contenu='num')
        ib_bonus_mission=InputBox(600, 630, 150, 30, text=dico_parametres['bonus_mission'], contenu='num')
        input_boxes=[ib_nb_fantomes,ib_nb_fantomes_mission,ib_nb_joker,ib_points_pepite,ib_points_fantome,ib_points_fantome_mission,ib_bonus_mission]
        
        #Stockage des choix des inputs
        L_parametres=['nb_fantomes','nb_fantomes_mission','nb_joker','points_pepite','points_fantome','points_fantome_mission','bonus_mission']
        for k in range(0,len(input_boxes)):
            dico_choix[L_parametres[k]]=input_boxes[k].text
            #vérification des erreurs
            for erreur in dico_erreurs.keys():
                if L_parametres[k]==erreur:
                    input_boxes[k].color=self.COLOR_ERROR
    
        while self.dico_stop['parametrisation2']==True :
                    
            self.fenetre.blit(self.fond_uni,(0,0))
            
            #titre de la fenêtre
            self.fenetre.blit(self.police3.render("Paramètres avancés",True,pygame.Color("#000000")),(100,50))
            
            #affichage de l'éventuel message d'erreur 
            if len(dico_erreurs)!=0:
                if dico_erreurs['type']=='null':
                    self.fenetre.blit(self.police2.render("ERREUR : Renseignez tous les champs!",True,self.COLOR_ERROR),(550,50))
                elif dico_erreurs['type']=='max':
                    self.fenetre.blit(self.police2.render("ERREUR : Renseignez une valeur plus petite",True,self.COLOR_ERROR),(550,50))
                elif dico_erreurs['type']=='min':
                    self.fenetre.blit(self.police2.render("ERREUR : Renseignez une valeur plus grande",True,self.COLOR_ERROR),(550,50))
            
            #dessin des boutons
            valider.draw(self.fenetre)  
            retour.draw(self.fenetre)
            
            #dessin des choicebox
            for choicebox in choix_taille:
                choicebox.draw(self.fenetre)
            
            #dessin des inputboxs
            for box in input_boxes:
                box.draw(self.fenetre)
                
            #Ecriture des textes associés aux boxes
            self.fenetre.blit(self.police2.render("Dimensions du plateau: ",True,pygame.Color("#000000")),(100,110))
            self.fenetre.blit(self.police2.render("Nombre de fantômes: ",True,pygame.Color("#000000")),(100,180))
            n=int(dico_choix['dimensions_plateau'])
            nb_fant=(n-2)*(n//2)+(n//2)*(n//2-1)
            self.fenetre.blit(self.police1.render("Entier positif / Maximum:"+str(nb_fant),True,pygame.Color("#000000")),(100,210))
            self.fenetre.blit(self.police1.render("Configuration standard : "+str(nb_fant)+" fantômes pour un plateau de taille "+str(dico_choix['dimensions_plateau'])+"x"+str(dico_choix['dimensions_plateau'])+".",True,pygame.Color("#000000")),(100,230))
            self.fenetre.blit(self.police2.render("Nombre de fantômes par ordre de mission: ",True,pygame.Color("#000000")),(100,250))
            self.fenetre.blit(self.police1.render("Entier positif / Configuration standard : 3 fantômes.",True,pygame.Color("#000000")),(100,280))
            self.fenetre.blit(self.police2.render("Joker(s) par joueur: ",True,pygame.Color("#000000")),(100,320))
            self.fenetre.blit(self.police1.render("Entier positif / Configuration standard : 1 joker.",True,pygame.Color("#000000")),(100,350))
            self.fenetre.blit(self.police2.render("Points gagnés par pépite ramassée: ",True,pygame.Color("#000000")),(100,390))    
            self.fenetre.blit(self.police1.render("Entier positif / Configuration standard : 1 point.",True,pygame.Color("#000000")),(100,420))                                                                                                                                                                                                                                                                                                
            self.fenetre.blit(self.police2.render("Points gagnés par fantôme capturé: ",True,pygame.Color("#000000")),(100,460))
            self.fenetre.blit(self.police1.render("Entier positif / Configuration standard : 5 points.",True,pygame.Color("#000000")),(100,490))
            self.fenetre.blit(self.police2.render("Points gagnés par fantôme capturé: ",True,pygame.Color("#000000")),(100,530))  
            self.fenetre.blit(self.police2.render("si le fantôme figure sur l'ordre de mission",True,pygame.Color("#000000")),(100,560))
            self.fenetre.blit(self.police1.render("Entier positif / Configuration standard : 20 points.",True,pygame.Color("#000000")),(100,590))
            self.fenetre.blit(self.police2.render("Bonus lors du remplissage d'une mission: ",True,pygame.Color("#000000")),(100,630))
            self.fenetre.blit(self.police1.render("Entier positif / Configuration standard : 40 points.",True,pygame.Color("#000000")),(100,660)) 
                                                                                   
            #actualisation de l'écran
            pygame.display.flip()
            
            #gestion des évènements
            for event in pygame.event.get():
                
                #gestion des boutons
                valider.handle_event(event,action=enregistrement_inputs, parametre_action=dico_choix)
                retour.handle_event(event,action=self.parametrisation_1)
                
                #gestion des inputboxs
                for k in range(0,len(input_boxes)):
                    box=input_boxes[k]
                    box.handle_event(event)
                    dico_choix[L_parametres[k]]=box.text
                
                #gestion des choiceboxs
                for choix in choix_taille:
                    choix.handle_event(event,choix_taille)
                    if choix.active:
                        dico_choix['dimensions_plateau']=choix.text
                
                #arrêt du jeu
                if event.type == QUIT:   
                    self.dico_stop = dict.fromkeys(self.dico_stop, False)
        


mn = mine_hantee()

mn.menu()

pygame.display.quit()
pygame.quit()
