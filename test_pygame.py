# -*- coding: utf-8 -*-
"""
Created on Wed Nov 13 14:35:26 2019

@author: agaca
"""

import pygame
from pygame.locals import *
import numpy as np
import random as rd
from PIL import Image
import matplotlib.pyplot as plt

class carte(object):
    
    def __init__(self, ID, orientation, coord, deplacable=False, id_fantome = 0):
        
        self.id = ID
        self.orientation = orientation
        self.deplacable = deplacable
        self.id_fantome = id_fantome
        self.presence_pepite = True
        self.coord = coord
        
        
class joueur(object):
    
    def __init__(self, ID, nom, niveau, fantome_target, carte_position):
        self.id = ID
        self.nom = nom
        self.niveau = niveau
        self.fantome_target = fantome_target
        self.carte_position = carte_position
        self.points = 0
        self.cartes_explorees = []
        self.capture_fantome = False



            
class plateau(object):
    """
    - seuls les N impairs sont acceptés
    """
    def __init__(self, nb_joueurs, liste_noms, liste_niveaux, N):
        
        self.N = N
        self.position=np.zeros([N,N])
        self.id_dernier_fantome=0
        self.dico_cartes={}
        self.dico_joueurs = {}
        positions_initiales = [] #cartes du milieu où se placent les joueurs en début de partie
        
        compte_id=0
        compte_deplacable=0
        compte_fantomes = 0
        #créer une combinaison des types de cartes
        nb_deplacable=N//2*(N//2+1+N)+1
        #orientations et types de murs de chaque carte
        pool1=[[[1,0,1,0],[0,1,0,1]][rd.randint(0,1)] for i in range(int(nb_deplacable*13/34))]
        pool2=[[[1,1,0,0],[0,1,1,0],[0,0,1,1],[1,0,0,1]][rd.randint(0,3)] for i in range(int(nb_deplacable*15/34))]
        pool3=[[[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]][rd.randint(0,3)] for i in range(int(nb_deplacable*6/34))]
        pool=pool1+pool2+pool3
        
        #Pool des id des fantômes à placer sur le plateau
        nbre_fantomes = (N-1)*(N//2)+(N//2)*(N//2-1)
        pool_fantomes = [i for i in range(1,nbre_fantomes+1)]
        pool_fantomes = np.random.permutation(pool_fantomes)
        
        while len(pool)<nb_deplacable:
            pool.append(rd.choice([rd.choice(pool1),rd.choice(pool2),rd.choice(pool3)]))
        pool=np.random.permutation(pool)
        
        for ligne in range(N):
            for colonne in range(N):
                
                carte_initiale = False #Faux par défaut, devient vraie si la carte en question est une des cartes de positionnement initial
                id_fantome = 0 #Pas de fantome sur la case par défaut
                
                self.position[ligne,colonne]=int(compte_id)
                #cases indéplaçables
                if ligne%2 ==0 and colonne%2==0:
                    print(["indéplaçable",ligne,colonne])
                    deplacable=False
                    #cases du milieu où les joueurs commencent la partie
                    if ligne==N//2-1 and colonne==N//2-1:
                        orientation=[0,0,0,1]
                        carte_initiale = True
                    elif ligne==N//2-1 and colonne==N//2+1:
                        orientation=[1,0,0,0]
                        carte_initiale = True
                    elif ligne==N//2+1 and colonne==N//2-1:
                        orientation=[0,0,1,0]
                        carte_initiale = True
                    elif ligne==N//2+1 and colonne==N//2+1:
                        orientation=[0,1,0,0]
                        carte_initiale = True
                    
                    #cases du coin et des diagonales
                    elif ligne==colonne or colonne==N-1-ligne:
                        if ligne<N//2 and colonne<N//2:
                            orientation=[1,0,0,1]
                        elif ligne<N//2 and colonne>N//2:
                            orientation=[1,1,0,0]
                        elif ligne>N//2 and colonne<N//2:
                            orientation=[0,0,1,1]
                        elif ligne>N//2 and colonne>N//2:
                            orientation=[0,1,1,0]
                    
                    #cases qui font les bords et les autres indéplaçables
                    elif ligne>colonne and N-ligne>N-colonne:
                        orientation=[1,0,0,0]
                    elif ligne>colonne:
                        orientation=[0,1,0,0]
                    elif N-ligne<N-colonne:
                        orientation=[0,0,1,0]
                    else:
                        orientation=[0,0,0,1]
                    print(orientation)
                
                #cases déplaçables
                else:
                    print("deplaçable"+str(ligne)+str(colonne))
                    orientation=pool[compte_deplacable]
                    compte_deplacable+=1
                    deplacable=True
                    #Si la carte déplaçable ne fait pas partie de la couronne extérieure
                    #Elle accueille un fantome
                    if ligne>0 and ligne<N-1 and colonne>0 and colonne<N-1:
                        id_fantome=pool_fantomes[compte_fantomes]
                        compte_fantomes += 1
                    
                self.dico_cartes[compte_id]=carte(compte_id, orientation, [ligne,colonne], deplacable,id_fantome)
                #Si la carte en question fait partie des 4 cartes de positionnement initial, on l'ajoute à la liste
                if carte_initiale == True:
                    positions_initiales.append(self.dico_cartes[compte_id])
                compte_id+=1
        
        
        #La carte qui reste dans pool est la carte à l'exterieur du plateau
        self.carte_a_jouer=carte(compte_id,pool[compte_deplacable],["",""],True)
        print(compte_id)
        self.dico_cartes[compte_id] = self.carte_a_jouer
        
        #Initialisation des joueurs
        #Création des entités de joueurs réels
        pool_fantomes = np.random.permutation(pool_fantomes)   #On remélange les fantômes
        compte_fantomes = 0
        for i in range(len(liste_noms)):
            
            fantomes_target = []
            for j in range(3):
                fantomes_target.append(pool_fantomes[compte_fantomes])
                compte_fantomes += 1
                
            position = positions_initiales[i]
            self.dico_joueurs[i] = joueur(i,liste_noms[i],0,fantomes_target,position)
        
        #Création des entités des joueurs IA
        compte = 0
        for i in range(len(liste_noms)+1,nb_joueurs+1):
            fantomes_target = []
            for j in range(3):
                fantomes_target.append(pool_fantomes[compte_fantomes])
                compte_fantomes += 1
                
            position = positions_initiales[i]
            nom = "IA"+str(compte+1)
            self.dico_joueurs[i] = joueur(i,nom,liste_niveaux[compte],fantomes_target,position)
            compte += 1
    
        
    def deplace_carte(self,coord) :
        
        x=coord[0]
        y=coord[1]
        
        if self.dico_cartes[self.position[x,y]].deplacable==False :
            return False
        
        self.dico_cartes[self.carte_a_jouer.id].coord=[x,y]
        
        #Traite tous les cas possible : carte insérée de chaque côté
        
        if x==0 : #carte insérée en haut
            
            carte_sauvegardee=self.dico_cartes[self.position[self.N-1,y]] #on sauvegarde la carte qui va sortir du plateau
            
            for i in range(1,self.N):
                
                self.dico_cartes[self.position[self.N-i-1,y]].coord[0]+=1
                #en partant du bas, on change la carte pour la carte d'avant jusqu'à la première carte
                self.position[self.N-i,y]=self.position[self.N-i-1,y]
                            
        elif x==self.N-1: #carte insérée en bas
            
            carte_sauvegardee=self.dico_cartes[self.position[0,y]] #on sauvegarde la carte qui va sortir du plateau
            
            for i in range(1,self.N):
                
                self.dico_cartes[self.position[i,y]].coord[0]-=1
                #en partant du haut, on change la carte pour la carte d'après jusqu'à la dernière carte
                self.position[i-1,y]=self.position[i,y]
            
        elif y==0: #carte insérée sur le côté gauche
            
            carte_sauvegardee=self.dico_cartes[self.position[x,self.N-1]] #on sauvegarde la carte qui va sortir du plateau
            
            for i in range(1,self.N):
                
                self.dico_cartes[self.position[x,self.N-i-1]].coord[1]+=1
                #en partant de la droite, on change la carte pour la carte d'avant jusqu'à la première carte
                self.position[x,self.N-i]=self.position[x,self.N-i-1]
            
        elif y==self.N-1: #carte insérée sur le côté droit
            
            carte_sauvegardee=self.dico_cartes[self.position[x,0]] #on sauvegarde la carte qui va sortir du plateau
            
            for i in range(1,self.N):
                
                self.dico_cartes[self.position[x,i]].coord[1]-=1
                #en partant de la gauche, on change la carte pour la carte d'après jusqu'à la dernière carte
                self.position[x,i-1]=self.position[x,i]
                
        else :
            return False
                
        self.position[x,y]=self.carte_a_jouer.id
                
        if carte_sauvegardee.id_fantome!=0 : #si il y'a un fantome sur la carte sortie
                
                self.dico_cartes[self.position[x,y]].id_fantome=carte_sauvegardee.id_fantome #on déplace ce fantôme à l'autre bout du plateau
                
                carte_sauvegardee.id_fantome=0 #on supprime le fantôme de la carte sortie
                
        for i in range(len(self.dico_joueurs)) : #copié collé de deplace_joueur -> faire une méthode dans la classe joueur?
            if carte_sauvegardee.id==self.dico_joueurs[i].carte_position.id :
                self.dico_joueurs[i].carte_position=self.dico_cartes[self.position[x,y]]
                
                if self.dico_joueurs[i].carte_position.id_fantome==self.id_dernier_fantome+1 and self.dico_joueurs[i].capture_fantome == False :
                    #Si le fantôme est sur l'ordre de mission, le joueur gagne 20 points
                        if self.dico_joueurs[i].carte_position.id_fantome in self.dico_joueurs[i].fantome_target : 
                            self.dico_joueurs[i].points += 20
                            self.dico_joueurs[i].fantome_target.remove(self.dico_joueurs[i].carte_position.id_fantome)
                            print("fantome sur l'ordre de mission capturé")
                            #Si l'ordre de mission est totalement rempli, le joueur gagne 40 points
                            if self.dico_joueurs[i].fantome_target==[]:
                                self.dico_joueurs[i].points += 40
                                print("ordre de mission rempli")
                        #Si le fantôme n'est pas sur l'ordre de mission, le joueur gagne 5 points
                        else:
                            self.dico_joueurs[i].points += 5
                            print("fantome capturé")
                        
                        self.dico_joueurs[i].capture_fantome = True
                        self.id_dernier_fantome += 1
                        self.dico_joueurs[i].carte_position.id_fantome = 0
                    
            
        self.carte_a_jouer=carte_sauvegardee #update la carte à jouer
        self.carte_a_jouer.coord=['','']
        
    def cartes_accessibles1(self,carte):
        """
        carte=carte de la position pour laquelle on veut trouver les cartes accessibles
        """
        cartes_accessibles=[] #liste des entités des cartes accessibles
        coord=carte.coord
                    
        if ((coord[0]-1)>=0 and carte.orientation[3]==0): 
            #Si on est pas sur l'extrêmité gauche du plateau
            #et si aucun mur de la carte position ne barre le passage
            #On trouve l'entité de la carte à notre gauche
            for i in self.dico_cartes.values():
                if i.coord == [coord[0]-1,coord[1]]:
                    carte_access = i
            if carte_access.orientation[1] == 0: #Si aucun mur de la carte accessible ne barre le passage
                cartes_accessibles.append(carte_access)
            
        if ((coord[0]+1)<self.N and carte.orientation[1]==0): 
            #Si on est pas sur l'extrêmité droite du plateau
            for i in self.dico_cartes.values():
                if i.coord == [coord[0]+1,coord[1]]:
                    carte_access = i
            if carte_access.orientation[3] == 0:
                cartes_accessibles.append(carte_access)
        
        if ((coord[1]-1)>=0 and carte.orientation[0]==0): #Si on est pas sur l'extrêmité haute du plateau
            for i in self.dico_cartes.values():
                if i.coord == [coord[0],coord[1]-1]:
                    carte_access = i
            if carte_access.orientation[2] == 0:
                cartes_accessibles.append(carte_access)
        
        if ((coord[1]+1)<self.N and carte.orientation[2]==0): #Si on est pas sur l'extrêmité basse du plateau
            for i in self.dico_cartes.values():
                if i.coord == [coord[0],coord[1]+1]:
                    carte_access = i
            if carte_access.orientation[0] == 0:
                cartes_accessibles.append(carte_access)
        
        return cartes_accessibles
    
    def deplace_joueur(self,id_joueur,key):
        
        retour = [] #Stocke les informations nécessaires à renvoyer au joueur dans l'interface graphique
        
        #On stocke les coordonnées de la carte où on veut aller
        if key == 274: #bas
            nv_coord = [self.dico_joueurs[id_joueur].carte_position.coord[0],self.dico_joueurs[id_joueur].carte_position.coord[1]+1]
            direction = 0 #rang du côté concerné dans l'attribut orientation de la nouvelle carte
        
        elif key == 276: #gauche
            nv_coord = [self.dico_joueurs[id_joueur].carte_position.coord[0]-1,self.dico_joueurs[id_joueur].carte_position.coord[1]]
            direction = 1
        
        elif key == 273: #haut
            nv_coord = [self.dico_joueurs[id_joueur].carte_position.coord[0],self.dico_joueurs[id_joueur].carte_position.coord[1]-1]
            direction = 2
        
        elif key == 275: #droite
            nv_coord = [self.dico_joueurs[id_joueur].carte_position.coord[0]+1,self.dico_joueurs[id_joueur].carte_position.coord[1]]
            direction = 3
        
        #On vérifie que les coordonnées de l'endroit où le joueur veut aller ne sont pas hors plateau
        #i.e. on vérifie que le joueur ne fonce pas dans une des limites du plateau
        if nv_coord[0]<0 or nv_coord[1]<0 or nv_coord[0]>=self.N or nv_coord[1]>=self.N:
            retour.append("Vous ne pouvez pas aller dans cette direction")
        else:
            #On retrouve la carte associée aux nouvelles coordonnées
            for i in self.dico_cartes.values():
                if i.coord == nv_coord :
                    nv_carte = i
            
            #On vérifie que le joueur ne fonce pas dans un mur
            if nv_carte.orientation[direction] == 1:
                retour.append("Vous ne pouvez pas aller dans cette direction")
            else:
                #On vérifie que le joueur n'est pas déjà passé par cette carte pendant ce tour
                if nv_carte in self.dico_joueurs[id_joueur].cartes_explorees:
                    retour.append("Vous avez déjà exploré cette carte")
                
                else:
                    self.dico_joueurs[id_joueur].carte_position = nv_carte #On déplace le joueur
                    self.dico_joueurs[id_joueur].cartes_explorees.append(nv_carte)
                    
                    #Si il y a une pépite sur la nouvelle carte, le joueur la ramasse
                    if nv_carte.presence_pepite == True : 
                        self.dico_joueurs[id_joueur].points += 1
                        nv_carte.presence_pepite = False
                        retour.append("nouvelle pépite")
                    
                    #Si il y a un fantôme sur la nouvelle carte, le joueur le capture si c'est possible
                    #i.e. si c'est le fantôme à capturer et s'il n'a pas encore capturé de fantôme pendant ce tour
                    if nv_carte.id_fantome == self.id_dernier_fantome+1 and self.dico_joueurs[id_joueur].capture_fantome == False :
                        #Si le fantôme est sur l'ordre de mission, le joueur gagne 20 points
                        if nv_carte.id_fantome in self.dico_joueurs[id_joueur].fantome_target : 
                            self.dico_joueurs[id_joueur].points += 20
                            self.dico_joueurs[id_joueur].fantome_target.remove(nv_carte.id_fantome)
                            retour.append("fantome sur l'ordre de mission capturé")
                            #Si l'ordre de mission est totalement rempli, le joueur gagne 40 points
                            if self.dico_joueurs[id_joueur].fantome_target==[]:
                                self.dico_joueurs[id_joueur].points += 40
                                retour.append("ordre de mission rempli")
                        #Si le fantôme n'est pas sur l'ordre de mission, le joueur gagne 5 points
                        else:
                            self.dico_joueurs[id_joueur].points += 5
                            retour.append("fantome capturé")
                        
                        self.dico_joueurs[id_joueur].capture_fantome = True
                        self.id_dernier_fantome += 1
                        nv_carte.id_fantome = 0
                        
                    
                    #On trouve les cartes accessibles à partir de la nouvelle carte
                    cartes_accessibles = self.cartes_accessibles1(nv_carte)
                    retour.append(cartes_accessibles)
        
        print(retour)

    def chemins_possibles(self, carte_depart=0, chemin_en_cours=[]):
        """
        fonction récursive
        un chemin correspond à une suite de cartes
        amélioration possible : soit on donne le chemin de départ, soit on donne le chemin en cours. 
        """
        L_chemin_possibles=[]
        #si on se trouve au niveau du point de départ
        if carte_depart!=0:
            #on initialise le chemin à la position de départ
            chemin=[carte_depart]
            #le joueur peut rester à sa place, donc le chemin ne contenant 
            #que la carte de départ fait partie des chemins possibles.
            L_chemin_possibles=L_chemin_possibles+[chemin]
            chemin_en_cours=chemin
        
        #on prend la dernière carte du chemin en cours.
        carte=chemin_en_cours[-1]
        options=self.cartes_accessibles1(carte)
        for i in options:
            #le joueur ne peut pas repasser sur une carte où il est déjà passé. 
            if i not in chemin_en_cours:
                chemin=chemin_en_cours+[i]
                L_chemin_possibles=L_chemin_possibles+[chemin]
                nouveaux_chemins=self.chemins_possibles(chemin_en_cours=chemin)
                if len(nouveaux_chemins)!=0:
                    L_chemin_possibles=L_chemin_possibles+nouveaux_chemins
            
        return L_chemin_possibles
    
    
    def affiche_plateau(self,fenetre):
        #Chargement et collage du fond
        
        fenetre.blit(fond_ext,(0,0))
        fenetre.blit(fond, (0,0))
        
        
        for i in range(len(self.position)) :
            for j in range(len(self.position)) :
                x=self.dico_cartes[self.position[i,j]].coord[0]*100
                y=self.dico_cartes[self.position[i,j]].coord[1]*100
                
                for k in range(len(self.dico_cartes[self.position[i,j]].orientation)) :
                   if self.dico_cartes[self.position[i,j]].orientation[k]==1 :
                       if k==0 :
                           fenetre.blit(mur1,(x,y))
                       elif k==1 :
                           fenetre.blit(mur4,(x,y))
                       elif k==2 :
                           fenetre.blit(mur2,(x,y))
                       elif k==3 :
                           fenetre.blit(mur3,(x,y))
                           
                if self.dico_cartes[self.position[i,j]].presence_pepite==True:
                    fenetre.blit(pepite,(x,y))
                if self.dico_cartes[self.position[i,j]].id_fantome!=0 :
                    fenetre.blit(fantome,(x,y))
                    fenetre.blit(police.render(str(self.dico_cartes[self.position[i,j]].id_fantome),True,pygame.Color("#FFFFFF")),(x+40,y+8))
                           
        for i in range(len(self.dico_joueurs)) :
            x=self.dico_joueurs[i].carte_position.coord[0]*100
            y=self.dico_joueurs[i].carte_position.coord[1]*100
            fenetre.blit(liste_im_joueur[i],(x,y))
            
        
        x=750
        y=50
        fenetre.blit(fond_a_jouer,(x,y))
        for k in range(len(self.carte_a_jouer.orientation)):
            if self.carte_a_jouer.orientation[k]==1 :
                if k==0 :
                   fenetre.blit(mur1,(x,y))
                elif k==1 :
                   fenetre.blit(mur4,(x,y))
                elif k==2 :
                   fenetre.blit(mur2,(x,y))
                elif k==3 :
                   fenetre.blit(mur3,(x,y))
                   
                   
#---------------------------------------Définition des objets graphiques---------------------------------
 
#code nécessaire pour créer des boutons associés à une action
def text_objects(text, font):
    textSurface = font.render(text, True, pygame.Color("#000000"))
    return textSurface, textSurface.get_rect()
      
def button(fenetre,msg,x,y,w,h,ic,ac,action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    
    if x+w > mouse[0] > x and y+h > mouse[1] > y:
        pygame.draw.rect(fenetre, ac,(x,y,w,h))

        if click[0] == 1 and action != None:
            action()         
    else:
        pygame.draw.rect(fenetre, ic,(x,y,w,h))

    smallText = pygame.font.SysFont("comicsansms",20)
    textSurf, textRect = text_objects(msg, smallText)
    textRect.center = ( (x+(w/2)), (y+(h/2)) )
    fenetre.blit(textSurf, textRect)
    
    
#---------------------------------------Défintion des instructions graphiques------------------------------
    
def menu():
    
    intro = True

    while intro: #Boucle infinie
        
        fenetre.blit(fond_menu,(0,0))  #On colle le fond du menu
        
        #Création du bouton qui lance le jeu
        button(fenetre,"Jouer",600,350,100,50,pygame.Color("#DC143C"),pygame.Color("#F08080"),game)
                                                           
        pygame.display.flip() #Update l'écran
        
        for event in pygame.event.get(): #Instructions de sortie
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

def game() :
    
    
    continuer = 1
    
    erreur_deplacement="" #Initialisation du texte d'erreur
    
    #Boucle infinie
    while continuer:
        
        test.affiche_plateau(fenetre) #on re-colle le plateau
        
        
        for i in range(len(test.dico_joueurs)) : #affichage des scores
                x=test.dico_joueurs[i].carte_position.coord[0]*100
                y=test.dico_joueurs[i].carte_position.coord[1]*100
                fenetre.blit(police.render("Score joueur "+str(i+1)+" : "+str(test.dico_joueurs[i].points),True,pygame.Color("#FFFFFF")),(760,300+i*100))
                                      
        fenetre.blit(police.render(erreur_deplacement,True,pygame.Color("#000000")),(750,250)) #affichage du message d'erreur
                                                                        
        pygame.display.flip() #Update l'écran
        
        for event in pygame.event.get():   #On parcours la liste de tous les événements reçus
            
            if event.type == QUIT:     #Si un de ces événements est de type QUIT
                pygame.display.quit()
                pygame.quit()
                continuer = 0      #On arrête la boucle
                
            if event.type == KEYDOWN and event.key == K_r: #Si on appuie sur R, rotation de la carte à jouer
                test.carte_a_jouer.orientation[0],test.carte_a_jouer.orientation[1],test.carte_a_jouer.orientation[2],test.carte_a_jouer.orientation[3]=test.carte_a_jouer.orientation[3],test.carte_a_jouer.orientation[0],test.carte_a_jouer.orientation[1],test.carte_a_jouer.orientation[2]
            
            if event.type == MOUSEBUTTONDOWN : 
                if event.button==1: #clic gauche : insertion de la carte à jouer
                    coord=[event.pos[0]//100,event.pos[1]//100]
                    if test.deplace_carte(coord)==False :
                        erreur_deplacement="Vous ne pouvez pas insérer la carte ici!"
                    else :
                        erreur_deplacement=""
                        
            if event.type == KEYDOWN and (event.key == K_UP or event.key == K_LEFT or event.key == K_DOWN or event.key == K_RIGHT) : #touches directionnelles : déplacement du joueur
                test.deplace_joueur(0,event.key)


#-----------------------------------------Affichage graphique et début du jeu------------------------------

pygame.init()

#Ouverture de la fenêtre Pygame
fenetre = pygame.display.set_mode((1200, 700))



#Création des images nécesssaires au jeu
fond = pygame.image.load("fond.jpg").convert()
fond_ext = pygame.image.load("fond_ext.png").convert()
mur1 = pygame.image.load("mur1.png").convert_alpha()
mur2 = pygame.image.load("mur2.png").convert_alpha()
mur3 = pygame.image.load("mur3.png").convert_alpha()
mur4 = pygame.image.load("mur4.png").convert_alpha()
liste_im_joueur = [pygame.image.load("joueur"+str(i)+".png").convert_alpha() for i in range(1,5)]
fond_a_jouer = pygame.image.load("fond_carte_a_jouer.png").convert()
fantome = pygame.image.load("fantome.png").convert_alpha()
pepite = pygame.image.load("pepite.png").convert_alpha()
fond_menu = pygame.image.load("fond_menu.png").convert()
#Création de la police du jeu
police = pygame.font.Font("SuperMario256.ttf", 20) #Load font object.

#Plateau de test
test=plateau(3,["Antoine","Christine","Michel"],[],7)

#Lancement du menu
menu()


                
                
                
                
                