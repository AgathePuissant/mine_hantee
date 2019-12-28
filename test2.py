# -*- coding: utf-8 -*-
"""
Created on Wed Nov 13 14:35:26 2019
@author: agaca
"""

import pygame
from pygame.locals import *
import numpy as np
import random as rd
import pickle
import glob
import copy
import math


class carte(object):
    
    def __init__(self, ID, orientation, coord, deplacable=False, id_fantome = 0):
        
        self.id = ID
        self.orientation = orientation
        self.deplacable = deplacable
        self.id_fantome = id_fantome
        self.presence_pepite = True
        self.coord = coord
        
        
class joueur(object):
    
    def __init__(self, ID, nom, niveau, fantome_target, carte_position, nb_joker):
        self.id = ID
        self.nom = nom
        self.niveau = niveau
        self.fantome_target = fantome_target
        self.carte_position = carte_position
        self.points = 0
        self.cartes_explorees = [carte_position]
        self.capture_fantome = False
        self.nb_joker=nb_joker


class plateau(object):
    """
    - seuls les N impairs sont acceptés
    """
    def __init__(self, nb_joueurs, liste_noms, liste_niveaux, N, dico_parametres):
        
        self.N = N
        self.position=np.zeros([N,N])
        self.id_dernier_fantome=0
        self.dico_cartes={}
        self.dico_joueurs = {}
        self.insertions_possibles=[] #liste des coordonnees des insertiones possible des cartes sur le plateau. 
        #attributs plateau liés aux points
        self.points_pepite=int(dico_parametres['points_pepite'])
        self.points_fantome=int(dico_parametres['points_fantome'])
        self.points_fantome_mission=int(dico_parametres['points_fantome_mission'])
        self.bonus_mission=int(dico_parametres['bonus_mission'])
        
        positions_initiales = [] #cartes du milieu où se placent les joueurs en début de partie
        
        compte_id=0
        compte_deplacable=0
        compte_fantomes = 0
        #créer une combinaison des types de cartes
        nb_deplacable=N//2*(N//2+1+N)+1
        #orientations et types de murs de chaque carte
        pool1=[rd.choice([[1,0,1,0],[0,1,0,1]]) for i in range(int(nb_deplacable*13/34))]
        pool2=[rd.choice([[1,1,0,0],[0,1,1,0],[0,0,1,1],[1,0,0,1]]) for i in range(int(nb_deplacable*15/34))]
        pool3=[rd.choice([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]) for i in range(int(nb_deplacable*6/34))]
        pool=pool1+pool2+pool3
        
        #Pool du placement des fantomes 
        self.nbre_fantomes = int(dico_parametres['nb_fantomes'])
        nb_max_fant=(N-2)*(N//2)+(N//2)*(N//2-1)
        pos_fant=range(nb_max_fant)
        pool_pos_fant=rd.sample(pos_fant,self.nbre_fantomes)
        compt=0
        
        #Pool des id des fantômes à placer sur le plateau
        pool_fantomes = [i for i in range(1,self.nbre_fantomes+1)]
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
                    elif ligne<colonne and N-ligne-1>colonne:
                        orientation=[1,0,0,0]
                    elif ligne<colonne and N-ligne-1<colonne:
                        orientation=[0,1,0,0]
                    elif ligne>colonne and N-ligne-1<colonne:
                        orientation=[0,0,1,0]
                    elif ligne>colonne and N-ligne-1>colonne:
                        orientation=[0,0,0,1]

               #cases déplaçables
                else:
                    orientation=pool[compte_deplacable]
                    compte_deplacable+=1
                    deplacable=True
                    #Si la carte déplaçable ne fait pas partie de la couronne extérieure
                    #Elle accueille un fantome
                    if ligne>0 and ligne<N-1 and colonne>0 and colonne<N-1:
                        if compte_fantomes<self.nbre_fantomes:
                            if compt in pool_pos_fant:
                                id_fantome=pool_fantomes[compte_fantomes]
                                compte_fantomes += 1
                            compt += 1
                    #si la carte fait partie de la couronne extérieure et qu'elle est déplaçable, 
                    #on ajoute ses coordonnées aux coordonnées à la liste des insertions possibles. 
                    elif ligne==0 or ligne==N-1 or colonne==0 or colonne==N-1:
                        self.insertions_possibles=self.insertions_possibles+[[ligne,colonne]]
                    
                self.dico_cartes[compte_id]=carte(compte_id, orientation, [ligne,colonne], deplacable,id_fantome)
                    
                #Si la carte en question fait partie des 4 cartes de positionnement initial, on l'ajoute à la liste
                if carte_initiale == True:
                    positions_initiales.append(self.dico_cartes[compte_id])
                compte_id+=1
        
        
        #La carte qui reste dans pool est la carte à l'exterieur du plateau
        self.carte_a_jouer=carte(compte_id,pool[compte_deplacable],["",""],True)
        self.dico_cartes[compte_id] = self.carte_a_jouer
        
        #Initialisation des joueurs
        #Création des entités de joueurs
        pool_fantomes = np.random.permutation(pool_fantomes)   #On remélange les fantômes
        
        nb_fantomes_mission=int(dico_parametres['nb_fantomes_mission'])
        nb_joker=int(dico_parametres['nb_joker'])
        compte_fantomes = 0
        for i in range(nb_joueurs):
            
            fantomes_target = []
            for j in range(nb_fantomes_mission):
                fantomes_target.append(pool_fantomes[compte_fantomes])
                compte_fantomes += 1
                
            position = positions_initiales[i]
            self.dico_joueurs[i] = joueur(i,liste_noms[i],liste_niveaux[i],fantomes_target,position,nb_joker)
    
    
        
    def deplace_carte(self,coord) :
        
        x=coord[0]
        y=coord[1]
        
        if [x,y] not in self.insertions_possibles:
            out=False
        
        else:
            
            out=True
        
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
                    
            for i in range(len(self.dico_joueurs)) : 
                if carte_sauvegardee.id==self.dico_joueurs[i].carte_position.id :
                    self.dico_joueurs[i].carte_position=self.dico_cartes[self.position[x,y]]
                        
                
            self.carte_a_jouer=carte_sauvegardee #update la carte à jouer
            self.carte_a_jouer.coord=['','']
            
        return out
        
        
    def cartes_accessibles1(self,carte):
        """
        carte=carte de la position pour laquelle on veut trouver les cartes accessibles
        """
        cartes_accessibles=[] #liste des entitÃ©s des cartes accessibles
        coord=carte.coord
                    
        if ((coord[1]-1)>=0 and carte.orientation[3]==0): 
            #Si on est pas sur l'extrÃªmitÃ© gauche du plateau
            #et si aucun mur de la carte position ne barre le passage
            #On trouve l'entitÃ© de la carte Ã  notre gauche
            for i in self.dico_cartes.values():
                if i.coord == [coord[0],coord[1]-1]:
                    carte_access = i
            if carte_access.orientation[1] == 0: #Si aucun mur de la carte accessible ne barre le passage
                cartes_accessibles.append(carte_access)
            
        if ((coord[1]+1)<self.N and carte.orientation[1]==0):
            #Si on est pas sur l'extrÃªmitÃ© droite du plateau
            for i in self.dico_cartes.values():
                if i.coord == [coord[0],coord[1]+1]:
                    carte_access = i
            if carte_access.orientation[3] == 0:
                cartes_accessibles.append(carte_access)
        
        if ((coord[0]-1)>=0 and carte.orientation[0]==0): #Si on est pas sur l'extrÃªmitÃ© haute du plateau
            for i in self.dico_cartes.values():
                if i.coord == [coord[0]-1,coord[1]]:
                    carte_access = i
            if carte_access.orientation[2] == 0:
                cartes_accessibles.append(carte_access)
        
        if ((coord[0]+1)<self.N and carte.orientation[2]==0): #Si on est pas sur l'extrÃªmitÃ© basse du plateau
            for i in self.dico_cartes.values():
                if i.coord == [coord[0]+1,coord[1]]:
                    carte_access = i
            if carte_access.orientation[0] == 0:
                cartes_accessibles.append(carte_access)
        
        return cartes_accessibles
    
    
    
    def deplace_joueur(self,id_joueur,key):

        carte_depart=self.dico_joueurs[id_joueur].carte_position
            
        #On stocke les coordonnées de la carte où on veut aller
        if key == 274: #bas
            nv_coord = [self.dico_joueurs[id_joueur].carte_position.coord[0]+1,self.dico_joueurs[id_joueur].carte_position.coord[1]]
        
        elif key == 276: #gauche
            nv_coord = [self.dico_joueurs[id_joueur].carte_position.coord[0],self.dico_joueurs[id_joueur].carte_position.coord[1]-1]
        
        elif key == 273: #haut
            nv_coord = [self.dico_joueurs[id_joueur].carte_position.coord[0]-1,self.dico_joueurs[id_joueur].carte_position.coord[1]]
        
        elif key == 275: #droite
            nv_coord = [self.dico_joueurs[id_joueur].carte_position.coord[0],self.dico_joueurs[id_joueur].carte_position.coord[1]+1]
        
        #On vérifie qu'on ne fonce pas dans une extrêmité du plateau
        if nv_coord[0]<0 or nv_coord[1]<0 or nv_coord[0]>=self.N or nv_coord[1]>=self.N :
            retour = "Ce déplacement est impossible."
        else :
            #On retrouve la carte associée aux nouvelles coordonnées
            for i in self.dico_cartes.values():
                if i.coord == nv_coord :
                    nv_carte = i

            #On trouve les cartes accessibles à partir de la nouvelle carte
            cartes_accessibles = self.cartes_accessibles1(carte_depart)
            #SI l'entrée du joueur correspond à une carte accessible
            if nv_carte in cartes_accessibles:
                #On vérifie que le joueur n'est pas déjà passé par cette carte pendant ce tour
                if nv_carte in self.dico_joueurs[id_joueur].cartes_explorees:
                    retour = "Cette case a déjà été explorée."
                
                else:
                    self.dico_joueurs[id_joueur].carte_position = nv_carte #On déplace le joueur
                    self.dico_joueurs[id_joueur].cartes_explorees.append(nv_carte)
                    retour = nv_carte
            else:
                retour = "Ce déplacement est impossible."
                

        return [retour]
    
    
    def compte_points(self,id_joueur,nv_carte):
        
        retour = []
        #Si il y a une pépite sur la nouvelle carte, le joueur la ramasse
        if nv_carte.presence_pepite == True : 
            self.dico_joueurs[id_joueur].points += self.points_pepite
            nv_carte.presence_pepite = False
            retour.append("Vous avez trouvé une pépite !")
        
        #Si il y a un fantôme sur la nouvelle carte, le joueur le capture si c'est possible
        #i.e. si c'est le fantôme à capturer et s'il n'a pas encore capturé de fantôme pendant ce tour
        if nv_carte.id_fantome == self.id_dernier_fantome+1 and self.dico_joueurs[id_joueur].capture_fantome == False :
            #Si le fantôme est sur l'ordre de mission, le joueur gagne 20 points
            if nv_carte.id_fantome in self.dico_joueurs[id_joueur].fantome_target : 
                self.dico_joueurs[id_joueur].points += self.points_fantome_mission
                self.dico_joueurs[id_joueur].fantome_target.remove(nv_carte.id_fantome)
                retour.append("Vous avez capturé un fantôme sur votre ordre de mission !")
                #Si l'ordre de mission est totalement rempli, le joueur gagne 40 points
                if self.dico_joueurs[id_joueur].fantome_target==[]:
                    self.dico_joueurs[id_joueur].points += self.bonus_mission
                    retour.append("Vous avez rempli votre ordre de mission !")
            #Si le fantôme n'est pas sur l'ordre de mission, le joueur gagne 5 points
            else:
                self.dico_joueurs[id_joueur].points += self.points_fantome
                retour.append("Vous avez capturé un fantôme !")
            
            self.dico_joueurs[id_joueur].capture_fantome = True
            self.id_dernier_fantome += 1
            nv_carte.id_fantome = 0

        return retour
        

    def chemins_possibles(self, carte_depart=0, chemin_en_cours=[]):
        """
        fonction récursive qui donne tous les chemins possibles à partir d'une carte sur le plateau. 
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


#------------------------------------IA---------------------------------------

def IA_simple(id_joueur,plateau_en_cours):
    
    #On duplique l'entité du plateau en cours pour faire des simulations de déplacement
    #de cartes sans impacter le vrai plateau
    plateau = copy.deepcopy(plateau_en_cours)
    chemins_possibles_total = [] #Liste des listes de chemins possibles pour chaque insertion possible, donc liste de liste de liste
    
    #On recueille les données des adversaires i.e. leurs fantomes target
    target_adversaires = [] 
    for i in plateau.dico_joueurs.keys():
        if i != id_joueur : 
            for j in plateau.dico_joueurs[i].fantome_target :
                target_adversaires.append(j)
        
        
    #Pour toutes les insertions possibles et toutes les rotations de carte possibles,
    #on stocke tous les chemins possibles pour le joueur donné
    orientation = plateau.carte_a_jouer.orientation
    #On teste pour chaque emplacement où la carte est insérable
    for i in plateau.insertions_possibles: 
        
        j=0
        chemins_possibles_carte = [] 
        
        for j in range(4):
            plateau.carte_a_jouer.orientation = orientation
            plateau.deplace_carte(i)
            chemins_possibles = plateau.chemins_possibles(plateau.dico_joueurs[id_joueur].carte_position)
            chemins_possibles_carte.append(chemins_possibles)
            #On réinitialise les emplacements des cartes à celles du plateau en cours
            plateau = copy.deepcopy(plateau_en_cours)
            orientation[0],orientation[1],orientation[2],orientation[3]=orientation[3],orientation[0],orientation[1],orientation[2]
        
        chemins_possibles_total.append(chemins_possibles_carte)
    dico_heuristique = {} #dico avec le rang (couple) d'un chemin dans chemin_possibles_total en clé et son heuristique en valeur
    

    for k in range(len(chemins_possibles_total)): #k : rang du sous-ensemble correspondant à un endroit d'insertion possible
        for i in range(len(chemins_possibles_total[k])) : #i: rang du sous-sous ensemble correspondant à l'orientation de la carte
            for m in range(len(chemins_possibles_total[k][i])):#m: rang du chemin possible parmi le sous-sous-ensemble
                heuristique = 0
                #On examine chaque case
                for j in chemins_possibles_total[k][i][m]:
                    #Si il y a une pépite sur la case
                    if j.presence_pepite == True : 
                        heuristique +=1
                    #Si il y a un de nos fantomes target attrapable
                    if j.id_fantome == plateau.id_dernier_fantome+1 and j.id_fantome in plateau.dico_joueurs[id_joueur].fantome_target:
                        heuristique += 20
                    #Si il y a un des fantomes target d'un adversaire attrapable
                    elif j.id_fantome == plateau.id_dernier_fantome+1 and j.id_fantome in target_adversaires:
                        heuristique += 10
                    #Si il y a un fantome attrapable qui n'est le target de personne
                    elif j.id_fantome == plateau.id_dernier_fantome+1:
                        heuristique += 5
                        
                dico_heuristique[(k,i,m)] = heuristique
    
    #On trouve l'heuristique maximale
    max_heur = max(dico_heuristique.values())
    #print(max_heur)
    
    chemins_opti = []
    inser_opti = []
    orientation_opti = []
    
    #On trouve le/les chemin(s) correspondant à l'heuristique maximale
    for triplet in dico_heuristique.keys():
        if dico_heuristique[triplet] == max_heur :
            chemins_opti.append(chemins_possibles_total[triplet[0]][triplet[1]][triplet[2]])
            #On trouve les coordonnées de l'insertion correspondant au chemin optimal trouvé
            inser_opti.append(plateau.insertions_possibles[triplet[0]])
            orientation_opti.append(triplet[1])
            
    #Les instances de cartes stockées dans les chemins possibles correspondent
    #aux instances du plateau dupliqué, il faut donc retrouver les instances qui
    #correspondent au vrai plateau utilisé
    chemin_plateau = []
    #Si il n'y a qu'un seul chemin optimal, on le choisit
    if len(chemins_opti) == 1:
        #On ne prend pas la première carte du chemin, qui correspond à la carte
        #où on se trouve actuellement
        for j in range(1,len(chemins_opti[0])):
            chemin_plateau.append(plateau_en_cours.dico_cartes[chemins_opti[0][j].id])
        return (inser_opti[0],orientation_opti[0],chemin_plateau)
    
    #Sinon on prend au hasard parmi les chemins optimaux
    #On pourrait aussi faire le choix de prendre celui qui inclu la capture d'un fantôme par ex
    else:
        rang = rd.randint(0,len(chemins_opti)-1)
        for j in range(1,len(chemins_opti[rang])):
            chemin_plateau.append(plateau_en_cours.dico_cartes[chemins_opti[rang][j].id])
        return (inser_opti[rang], orientation_opti[rang],chemin_plateau)
        

#plat = plateau(3,["Antoine","Christine","Michel"],[],7)
#print(IA_simple(2,plat))
#print(plat.position)
#print(plat.dico_joueurs[0].carte_position.coord,plat.dico_joueurs[1].carte_position.coord,plat.dico_joueurs[2].carte_position.coord)





    
#---------------------------------------Définition des objets graphiques---------------------------------
 
#code nécessaire pour créer des boutons associés à une action
def text_objects(text, font):
    textSurface = font.render(text, True, pygame.Color("#000000"))
    return textSurface, textSurface.get_rect()
    
def button_charger_partie(fenetre,msg,x,y,w,h,ic,ac,i):
    global num_partie,retour_partie
    
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    
    if x+w > mouse[0] > x and y+h > mouse[1] > y:
        pygame.draw.rect(fenetre, ac,(x,y,w,h))

        if click[0] == 1 and i != None:
            num_partie=i
            retour_partie=True
            
    else:
        pygame.draw.rect(fenetre, ic,(x,y,w,h))   

    smallText = pygame.font.SysFont("comicsansms",20)
    textSurf, textRect = text_objects(msg, smallText)
    textRect.center = ( (x+(w/2)), (y+(h/2)) )
    fenetre.blit(textSurf, textRect)
    
#definition des Boutons

class Bouton:
    
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.text = text
        self.txt_surface = police2.render(text, True, pygame.Color("#000000"))
        self.active = False
    
    def handle_event(self, event, action, parametre_action=None):
        
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        #si la souris se trouve au dessous du bouton, on l'active et on change la couleur
        if self.rect.x+self.rect.w > mouse[0] > self.rect.x and self.rect.y+self.rect.h > mouse[1] > self.rect.y:
            self.active=True
            if click[0] == 1:
                # L'action est lancée, avec ou sans paramètre
                if parametre_action==None:
                    action()
                else:
                    action(parametre_action)
        else:
            self.active=False
            
        #actualisation de la couleur du bouton
        if self.active==True:
            self.color=COLOR_ACTIVE
        else:
            self.color=COLOR_INACTIVE
    
    def draw(self, fenetre):
        # Blit le rectangle. 
        pygame.draw.rect(fenetre, self.color, self.rect)
        # Blit le texte.
        text_rect=self.txt_surface.get_rect()
        text_rect.center=(self.rect.x+((self.rect.w)/2), self.rect.y+((self.rect.h)/2))
        fenetre.blit(self.txt_surface, text_rect)
    
#definition des Inputboxs
    
class InputBox:

    def __init__(self, x, y, w, h, text='', max_caract=10, contenu='texte'):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.text = text
        self.txt_surface = police2.render(text, True, self.color)
        self.active = False
        self.max_caract=max_caract
        self.contenu=contenu

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
                        
            # si l'utilisateur clique sur le rectangle de inputbox.
            if self.rect.collidepoint(event.pos):
                # Activation de l'inputbox.
                self.active = not self.active
            else:
                self.active = False
            # On change la couleur de l'inputbox pour montrer qu'elle est active
            self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                elif self.contenu=='num' and (event.key in [pygame.K_0,pygame.K_1,pygame.K_2,pygame.K_3,pygame.K_4,pygame.K_5,pygame.K_6,pygame.K_7,pygame.K_8,pygame.K_9,pygame.K_KP0,pygame.K_KP1,pygame.K_KP2,pygame.K_KP3,pygame.K_KP4,pygame.K_KP5,pygame.K_KP6,pygame.K_KP7,pygame.K_KP8,pygame.K_KP9]) and len(self.text)<self.max_caract:
                    self.text += event.unicode
                elif self.contenu=='texte' and len(self.text)<self.max_caract:
                    self.text += event.unicode
                # Re-render le texte. 
                self.txt_surface = police2.render(self.text, True, self.color)

    def draw(self, fenetre):
        # Blit le rectangle. 
        pygame.draw.rect(fenetre, self.color, self.rect, 2)
        # Blit le texte. 
        fenetre.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))

#Definition des choiceboxs (boutons de sélection de valeurs prédéfinies)

class ChoiceBox:
    
    def __init__(self, x, y, w, h, text, active=False):
        self.rect = pygame.Rect(x, y, w, h)
        if active==False:
            self.color = COLOR_INACTIVE
        else:
            self.color = COLOR_ACTIVE
        self.text = text
        self.txt_surface = police2.render(text, True, self.color)
        self.active=active
    
    def handle_event(self, event, ChoiceBox_associees=[]):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # si l'utilisateur clique sur le rectangle de inputbox.
            if self.rect.collidepoint(event.pos):
                # Activation de l'inputbox.
                self.active = True
                #si l'un des boutons associé est activé, alors on l'inactive (un seul choix possible)
                for box in ChoiceBox_associees:
                    if self.rect!=box:
                        if box.active:
                            box.active = False
                            box.color=COLOR_INACTIVE
            self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE
    
    def draw(self,fenetre):
        # Blit le rectangle. 
        pygame.draw.rect(fenetre, self.color, self.rect, 2)
        # Blit le texte. 
        fenetre.blit(self.txt_surface, (self.rect.x+20, self.rect.y+5))

#lecture du fichier de paramétrage

def lecture(fichier):
    """
    fonction qui lit le fichier de paramètres
    et retourne le dictionnaire des paramètres
    (si l'utilisateur modifie directement le fichier des paramètres)
    """
    f=open(fichier,"r")
    lignes=f.readlines()
    dico_parametres={}
    for ligne in lignes:
        if ligne[0]!='#' and len(ligne)!=0 and ligne[0]!='\n':
            ligne=ligne[:-1]
            ligne_coupe = ligne.split("=")
            dico_parametres[ligne_coupe[0]]=ligne_coupe[1]
    return dico_parametres

#écriture du fichier de paramétrage

def ecriture(fichier, dico_parametres):
    """
    fonction qui remplit le fichier de paramètres à partir du dictionnaire des nouveaux paramètres 
    donnée en entrée dans dico_parametres. 
    (si l'utilisateur modifie les paramètres vie l'interface de jeu (avancée ou non))
    """
    f=open(fichier,"r")
    lignes=f.readlines()
    f.close()
    f_new=open(fichier,"w")
    for ligne in lignes:
        if ligne[0]!='#' and len(ligne)!=0 and ligne[0]!='\n':
            #récupération des anciens paramètres
            parametres=ligne[:-1]
            parametres=parametres.split("=")
            if parametres[0] in dico_parametres.keys():
                #comparaison avec les nouveaux paramètres
                #si le paramètre a été changé, on met le nouveau paramètre
                if dico_parametres[parametres[0]]!=parametres[1]:
                    parametres[1]=dico_parametres[parametres[0]]
                    #écriture de la ligne modifiée
                    f_new.write(parametres[0]+"="+str(parametres[1])+"\n")
                else:
                    f_new.write(ligne)
            else:
                f_new.write(ligne)
        else:
            f_new.write(ligne)
    f_new.close()  
    
    
    
    
def affiche_plateau(plat,fenetre):
    
    #Création des images nécesssaires au plateau
    #fond = pygame.image.load("fond.jpg").convert()
    fond_ext = pygame.image.load("fond_ext.png").convert()
    mur1 = pygame.image.load("mur1.png").convert_alpha()
    mur2 = pygame.image.load("mur2.png").convert_alpha()
    mur3 = pygame.image.load("mur3.png").convert_alpha()
    mur4 = pygame.image.load("mur4.png").convert_alpha()
    liste_im_joueur = [pygame.image.load("joueur"+str(i)+".png").convert_alpha() for i in range(1,5)]
    fond_a_jouer = pygame.image.load("fond_carte_a_jouer.png").convert()
    fantome = pygame.image.load("fantome.png").convert_alpha()
    pepite = pygame.image.load("pepite.png").convert_alpha()
    indeplacable = pygame.image.load("indeplacable.png").convert_alpha()

    
    #Chargement du fond dans la fenetre 
    fenetre.blit(fond_ext,(0,0))
    #fenetre.blit(fond, (0,0))
    N = plat.N #on récupère la taille du plateau
     
    #Mise  à jour de la taille des images en fonction du nombre de cartes du plateau
    x_mur1 = mur1.get_width()
    y_mur1 = mur1.get_height()
    mur1 = pygame.transform.scale(mur1, (int(x_mur1*(7/N)),int(y_mur1*(7/N))))
    x_mur2 = mur2.get_width()
    y_mur2 = mur2.get_height()
    mur2 = pygame.transform.scale(mur2, (int(x_mur2*(7/N)),int(y_mur2*(7/N))))
    x_mur3 = mur3.get_width()
    y_mur3 = mur3.get_height()
    mur3 = pygame.transform.scale(mur3, (int(x_mur3*(7/N)),int(y_mur3*(7/N))))
    x_mur4 = mur4.get_width()
    y_mur4 = mur4.get_height()
    mur4 = pygame.transform.scale(mur4, (int(x_mur4*(7/N)),int(y_mur4*(7/N))))
    x_fond_a_jouer = fond_a_jouer.get_width()
    y_fond_a_jouer = fond_a_jouer.get_height()
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
        x_joueur = liste_im_joueur[i].get_width()
        y_joueur = liste_im_joueur[i].get_height()
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
    affiche_plateau(plateau,fenetre)
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
                
            
    
    
#---------------------------------------Défintion des instructions graphiques------------------------------
    
def menu():
    global fenetre,liste_sauv,num_partie,nouvelle,dico_stop
    
    
    #en cours de modification
    if 'dico_stop' not in globals() :
        dico_stop={"intro" : True}
    elif any(value == True for value in dico_stop.values()):
        dico_stop["intro"]=True
    else :
        dico_stop = dict.fromkeys(dico_stop, False)

    nouvelle_partie_button=Bouton(500,350,200,50,"Nouvelle partie")
    charger_partie_button=Bouton(500,450,200,50,"Charger une partie")
    
    nouvelle=False
    

    while dico_stop["intro"]==True: #Boucle infinie
                
        pygame.display.flip() #Update l'écran
        fenetre.blit(fond_menu,(0,0))  #On colle le fond du menu
        
        liste_sauv=glob.glob("sauvegarde*")
        liste_sauv=[int(liste_sauv[i][-1]) for i in range(len(liste_sauv))]
        nouvelle_partie_button.draw(fenetre)
        charger_partie_button.draw(fenetre)
        
        for event in pygame.event.get(): #Instructions de sortie
            
            nouvelle_partie_button.handle_event(event,nouvelle_partie)
            charger_partie_button.handle_event(event,charger_partie)
            
            if event.type == pygame.QUIT:
                dico_stop = dict.fromkeys(dico_stop, False)
                pygame.display.quit()
                pygame.quit()
                
                
        
                
        
    
        

def game() :
    global fenetre,num_partie,nouvelle,plateau_test,dico_stop
    #Initialisation d'une nouvelle partie ou chargement d'une ancienne partie
    if nouvelle==False :
        plateau_test=pickle.load(open("sauvegarde "+str(num_partie),"rb"))
        dico_stop["charger"]=False
    elif nouvelle==True :
        #Création d'un nouveau plateau
        #Lecture du fichier de paramétrage et initialisation des paramètres
        dico_parametres=lecture(fichier)
        nb_joueurs=int(dico_parametres['nb_joueurs'])
        dimensions_plateau=int(dico_parametres['dimensions_plateau'])
        liste_noms=[dico_parametres['pseudo_joueur_1'],dico_parametres['pseudo_joueur_2'],dico_parametres['pseudo_joueur_3'],dico_parametres['pseudo_joueur_4']]
        
        #liste des niveaux
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
                
        plateau_test=plateau(nb_joueurs,liste_noms,liste_niveaux,dimensions_plateau,dico_parametres)
        
    else :
        pass
    
    
    afficher_commandes_button=Bouton(725,5,150,40,"Commandes")

    N = plateau_test.N
    
    
    dico_stop["rester_jeu"]=True
    
    
    #Boucle du jeu. On joue tant qu'il reste des fantômes à attraper
    while plateau_test.id_dernier_fantome!=plateau_test.nbre_fantomes and dico_stop["rester_jeu"]==True:

        #Tours de jeu
        #on parcours chaque joueur à chaque tours.
        for j in plateau_test.dico_joueurs :
            
            information="" #Initialisation du texte d'erreur
            etape=""
            
            joueur=plateau_test.dico_joueurs[j]

            actualise_fenetre(plateau_test,fenetre,joueur,information,afficher_commandes_button,etape)

            if joueur.niveau == 0 :
                #premiere etape : rotation et insertion de la carte
                #On parcours la liste de tous les événements reçus tant qu'une carte n'a pas été insérée
                dico_stop["test_carte"]=True
                dico_stop["test_entree"]=True
                
                
                while dico_stop["test_carte"]!=False:
                    
                    etape="Tourner la carte avec R, cliquer pour insérer"
                    
                    for event in pygame.event.get():   
                        
                        afficher_commandes_button.handle_event(event,afficher_commandes)
                        
                        #Si on appuie sur R, rotation de la carte à jouer
                        if event.type == KEYDOWN and event.key == K_r: 
                            plateau_test.carte_a_jouer.orientation[0],plateau_test.carte_a_jouer.orientation[1],plateau_test.carte_a_jouer.orientation[2],plateau_test.carte_a_jouer.orientation[3]=plateau_test.carte_a_jouer.orientation[3],plateau_test.carte_a_jouer.orientation[0],plateau_test.carte_a_jouer.orientation[1],plateau_test.carte_a_jouer.orientation[2]
                        
                        #ajouter la carte lorsque l'utilisateur clique dans le plateau
                        
                        elif event.type == MOUSEBUTTONDOWN : 
                            #clic gauche : insertion de la carte à jouer
                            if event.button==1: 
    
                                coord=[int(math.floor(event.pos[1]/700*plateau_test.N)),int(math.floor(event.pos[0]/700*plateau_test.N))]
                                
                                test_inser=plateau_test.deplace_carte(coord)
                               
                                if test_inser==False :
                                    information="Insertion impossible"
                                #Sinon, on finit cette section du tour
    
                                else :
                                    information=""
                                   
                                    dico_stop["test_carte"]=False
                                    
    
                        elif event.type == KEYDOWN and event.key == K_SPACE :
                            pause()
                        
                        elif event.type == QUIT:
                            dico_stop = dict.fromkeys(dico_stop, False)
                            
                    actualise_fenetre(plateau_test,fenetre,joueur,information,afficher_commandes_button,etape)
                   
                                        
                                        
                #2e etape : On parcours les évènements tant que le joueur n'a pas appuyé sur entrée ou tant qu'il peut encore se déplacer
                #initialisation à la position du joueur
                
                carte_actuelle=joueur.carte_position
                
                cartes_accessibles=plateau_test.cartes_accessibles1(carte_actuelle)
                
                information=""
                
                #parcours des evenements
                while dico_stop["test_entree"]==True and len(cartes_accessibles)>0:#La 2e condition deconne a cause de cartes_accessibles
                    
                    etape="Déplacer avec les flèches, entrée pour finir"
                    
                    for event in pygame.event.get():
                        
                        afficher_commandes_button.handle_event(event,afficher_commandes)
                        
                        #deplacement
                        if event.type == KEYDOWN and (event.key == K_UP or event.key == K_LEFT or event.key == K_DOWN or event.key == K_RIGHT) : #touches directionnelles : déplacement du joueur
                            deplace = plateau_test.deplace_joueur(j,event.key)
                            if isinstance(deplace, carte) == True: #Si le déplacement était possible, on affiche ce que le joueur a potentiellement gagné
                                information=plateau_test.compte_points(j,deplace)
                            else: #Sinon on affiche la raison pour laquelle le déplacement n'était pas possible
                                information=deplace
                            carte_actuelle=joueur.carte_position
                            cartes_accessibles=plateau_test.cartes_accessibles1(carte_actuelle)
                            
                            
                        #fin de tour
                        if event.type == KEYDOWN and (event.key== K_RETURN):
                            dico_stop["test_entree"]=False
                            information=""
                        
                            
                            
                        elif event.type == KEYDOWN and event.key == K_SPACE :
                            pause()
                            
                        elif event.type == QUIT:
                            dico_stop = dict.fromkeys(dico_stop, False)
                            
                    #Update l'écran                                                                
                    actualise_fenetre(plateau_test,fenetre,joueur,information,afficher_commandes_button,etape)
    
                        
                #Fin du tour du joueur : On ré-initialise cartes_explorees et capture_fantome
                joueur.cartes_explorees = [carte_actuelle]
                joueur.capture_fantome = False
                
                if dico_stop["test_carte"]==False and dico_stop["test_entree"]==False and dico_stop["rester_jeu"]==False:
                    break
            
            else:
                IA = IA_simple(j,plateau_test)
                coord_inser, orientation, chemin = IA[0],IA[1],IA[2]

                #On tourne la carte
                for i in range(orientation):
                    plateau_test.carte_a_jouer.orientation[0],plateau_test.carte_a_jouer.orientation[1],plateau_test.carte_a_jouer.orientation[2],plateau_test.carte_a_jouer.orientation[3]=plateau_test.carte_a_jouer.orientation[3],plateau_test.carte_a_jouer.orientation[0],plateau_test.carte_a_jouer.orientation[1],plateau_test.carte_a_jouer.orientation[2]
                    pygame.time.wait(200)
                    actualise_fenetre(plateau_test,fenetre,joueur,information,afficher_commandes_button,etape)
                 
                plateau_test.deplace_carte(coord_inser) #On l'insère
                pygame.time.wait(200)
                actualise_fenetre(plateau_test,fenetre,joueur,information,afficher_commandes_button,etape)
                

                information=""
                for i in chemin :
                    joueur.carte_position = i
                    information=plateau_test.compte_points(j,i)

                    pygame.time.wait(200)
                    actualise_fenetre(plateau_test,fenetre,joueur,information,afficher_commandes_button,etape)
                

            

def afficher_commandes() :
    global dico_stop

    dico_stop["comm"]=True
    
    while dico_stop["comm"]==True :
    
        fenetre.blit(fond_uni,(0,0))
        
        fenetre.blit(police.render("R : tourner la carte",False,pygame.Color("#000000")),(100,100))
        fenetre.blit(police.render("Clic sur une carte déplaçable en périphérie du plateau : insère la carte extérieure",False,pygame.Color("#000000")),(100,150))
        fenetre.blit(police.render("Flèches directionnelles : déplacer le joueur",False,pygame.Color("#000000")),(100,200))
        fenetre.blit(police.render("Entrée : finir le tour",False,pygame.Color("#000000")),(100,250))
        fenetre.blit(police.render("Espace : mettre en pause/Retour au jeu",False,pygame.Color("#000000")),(100,300))
        fenetre.blit(police.render("Appuyez sur espace pour revenir au jeu",False,pygame.Color("#000000")),(100,500))
                                                                                                     
                                                                                                    
                                                                      
        pygame.display.flip() 
                                                        
        for event in pygame.event.get() :
            
            if event.type == KEYDOWN and event.key == K_SPACE :
                dico_stop["comm"]=False
                
            if event.type == pygame.QUIT :
                dico_stop = dict.fromkeys(dico_stop, False)
            
def pause() :
    global fenetre,texte_sauv,nouvelle,dico_stop
    
    nouvelle="jeu en pause"
    
    dico_stop["pause"]=True
    
    texte_sauv=""
    
    sauvegarder_button=Bouton(550,350,200,50,"Sauvegarder")
    retour_menu_button=Bouton(550,450,200,50,"Retour au menu")
    
    while dico_stop["pause"]==True :
                
        fenetre.blit(fond_uni,(0,0))
    
        fenetre.blit(police.render("Pause",True,pygame.Color("#000000")),(600,200))
                                                             
        sauvegarder_button.draw(fenetre)
        retour_menu_button.draw(fenetre)
                                  
        fenetre.blit(police.render(texte_sauv,True,pygame.Color("#000000")),(550,550))
                                                                
        pygame.display.flip() #Update l'écran
        
        for event in pygame.event.get():   #On parcours la liste de tous les événements reçus
            
            sauvegarder_button.handle_event(event,sauvegarder)
            retour_menu_button.handle_event(event,menu)
                
            if event.type == KEYDOWN and event.key == K_SPACE :
                dico_stop["pause"]=False
                
            if event.type == QUIT:     #Si un de ces événements est de type QUIT
                dico_stop = dict.fromkeys(dico_stop, False)
                

                
def sauvegarder():
    global texte_sauv,num_partie,plateau_test
    
    pickle.dump(plateau_test,open("sauvegarde "+str(num_partie),"wb"))
    texte_sauv="Partie sauvegardée"

    
def charger_partie():
    global fenetre,liste_sauv,num_partie,retour_partie,dico_stop
    
    dico_stop["charger"]=True
    retour_partie=False
    lancer_partie_button=Bouton(800,300,200,50,"Lancer la partie")
    retour_menu_button=Bouton(500,300,200,50,"Retour au menu")
        
    while dico_stop["charger"] ==True:
                
                
        if liste_sauv!=[] :
            
            fenetre.blit(fond_uni,(0,0))  #On colle le fond du menu
            
            for i in range(len(liste_sauv)) :
                button_charger_partie(fenetre,"Partie "+str(liste_sauv[i]),500,100+i*100,200,50,pygame.Color("#b46503"),pygame.Color("#d09954"),liste_sauv[i])
            
            if retour_partie==True :
                fenetre.blit(police.render("Partie "+str(num_partie)+" sélectionnée",True,pygame.Color("#000000")),(800,100))
                lancer_partie_button.draw(fenetre)                                                    
        else :
            
            fenetre.blit(fond_uni,(0,0))  #On colle le fond du menu
            fenetre.blit(police.render("Aucune partie sauvegardee",True,pygame.Color("#000000")),(450,100))
            retour_menu_button.draw(fenetre)
            
        pygame.display.flip() #Update l'écran
        
        for event in pygame.event.get():   #On parcours la liste de tous les événements reçus
            
            if retour_partie==True :
                lancer_partie_button.handle_event(event,game)
            else :
                retour_menu_button.handle_event(event,menu)
            
            if event.type == QUIT:     #Si un de ces événements est de type QUIT
                dico_stop = dict.fromkeys(dico_stop, False)
                

                
def nouvelle_partie():
    '''
    Fonction de paramétrisation simple 1
    demande le nombre de joueurs pour la partie (entre 2,3 et 4) 
    '''
    global fenetre,liste_sauv,num_partie,nouvelle,dico_stop
    
    nouvelle=True
    #attribution du numéro de la partie
    if liste_sauv!=[]:
        num_partie=np.max(liste_sauv)+1
    else :
        num_partie=1
    
    dico_stop["intro"]=False
    dico_stop["nouvellepartie"]=True
    
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
    #on stoque le choix entre les boutons dans le dictionnaire choix_final
    choix_final={}
    choix_final["fonction"]=parametrisation_1
    choix_final["nb_joueurs"]=dico_parametres['nb_joueurs'] 
    choix_final['test_null']=False
    choix_final['test_max']=False          
    #initialisation du nombre de joueurs à la valeur renseignée dans le fichier
    for choix in choix_nb_joueurs:
            if choix.text==choix_final["nb_joueurs"]:
                choix.active=True
                choix.color=COLOR_ACTIVE
    
    while dico_stop["nouvellepartie"]==True :
                
        fenetre.blit(fond_uni,(0,0))
        
        #choix du nombre de joueurs 
        fenetre.blit(police3.render("Nouvelle partie!",True,pygame.Color("#000000")),(485,100))
        fenetre.blit(police3.render("Nombre de joueurs",True,pygame.Color("#000000")),(465,200))
        
        #dessin des boutons
        valider.draw(fenetre)  
        retour.draw(fenetre)
        
        #choix du nombre de joueurs
        for choix in choix_nb_joueurs:
            choix.draw(fenetre)
            if choix.active==True:
                choix_final["nb_joueurs"]=choix.text
                                                            
        #actualisation de l'écran
        pygame.display.flip()
        
        for event in pygame.event.get():
            
            #gestion des boutons
            valider.handle_event(event,action=enregistrement_inputs, parametre_action=choix_final)
            retour.handle_event(event,action=menu)
            
            #actualisation du choix du nombre de joueurs
            for choix in choix_nb_joueurs:
                choix.handle_event(event, choix_nb_joueurs)
            
            #arrêt du jeu
            if event.type == QUIT:   
                dico_stop = dict.fromkeys(dico_stop, False)
        

def parametrisation_1(dico_erreurs={}):
    """
    Fonction qui lance la paramétrisation des joueurs
    """
    global fenetre, dico_stop
    
    dico_stop['nouvellepartie']=False
    dico_stop['parametrisation1']=True
    
    #stockage des paramètres choisis qui seront enregistrés
    dico_choix={}
    dico_choix['fonction']=parametrisation_2
    dico_choix['fonction_prec']=parametrisation_1
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
                input_boxes[k].color=COLOR_ERROR
    
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
                choix.color=COLOR_ACTIVE 
    for k in range(0,len(choix_lvl_joueurs)):
        for choix in choix_lvl_joueurs[k]:
            if choix.text==dico_choix[L_lvl[k]]:
                choix.active=True
                choix.color=COLOR_ACTIVE
    
    while dico_stop['parametrisation1']==True :
        
        #actualisation de l'écran
        pygame.display.flip()
        
        fenetre.blit(fond_uni,(0,0))
        
        #paramètres des joueurs
        fenetre.blit(police3.render("Paramètres des joueurs",True,pygame.Color("#000000")),(100,50))
        
        if len(dico_erreurs)!=0:
            fenetre.blit(police2.render("ERREUR : Renseignez tous les champs!",True,COLOR_ERROR),(550,50))
        
        for k in range(1,int(nb_joueurs)+1):

            fenetre.blit(police2.render("Joueur "+str(k)+": ",True,pygame.Color("#000000")),(100,(k*100)))
            fenetre.blit(police2.render("Pseudo",True,pygame.Color("#000000")),(250,(k*100)))
            fenetre.blit(police2.render("Mode",True,pygame.Color("#000000")),(550,(k*100)))
                
            box=input_boxes[k-1]
            box.draw(fenetre)
            choix_manuel=choix_modes_joueurs[k-1][0]
            choix_automatique=choix_modes_joueurs[k-1][1]
            choix_manuel.draw(fenetre)
            choix_automatique.draw(fenetre)
            #si le mode automatique est activé, l'utilisateur peut choisir le niveau de l'ia. 
            #mais il ne peut pas choisir son nom
            if choix_automatique.active:
                fenetre.blit(police2.render("Niveau",True,pygame.Color("#000000")),(900,45+(k*100)))
                choix_lvl1=choix_lvl_joueurs[k-1][0]
                choix_lvl2=choix_lvl_joueurs[k-1][1]
                choix_lvl3=choix_lvl_joueurs[k-1][2]
                choix_lvl1.draw(fenetre)
                choix_lvl2.draw(fenetre)
                choix_lvl3.draw(fenetre)
        
        #dessin des boutons
        valider.draw(fenetre)  
        retour.draw(fenetre)
                                          
        #actualisation de l'écran
        pygame.display.flip()
        
        for event in pygame.event.get():
            
            #gestion des boutons
            valider.handle_event(event,action=enregistrement_inputs, parametre_action=dico_choix)
            retour.handle_event(event,action=nouvelle_partie)
            
            #remplissage des inputboxs    
            for k in range(1,int(nb_joueurs)+1):
                choix_manuel=choix_modes_joueurs[k-1][0]
                choix_automatique=choix_modes_joueurs[k-1][1]
                choix_manuel.handle_event(event,choix_modes_joueurs[k-1])
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
                    input_boxes[k-1].txt_surface=police2.render(input_boxes[k-1].text, True, input_boxes[k-1].color)
                    dico_choix[L_pseudos[k-1]]=input_boxes[k-1].text
                    dico_choix[L_modes[k-1]]="automatique"
                else:
                    box=input_boxes[k-1]
                    box.handle_event(event)
                    dico_choix[L_pseudos[k-1]]=input_boxes[k-1].text
                    dico_choix[L_modes[k-1]]="manuel"
                    if input_boxes[k-1].text=="Ordinateur"+str(k):
                        input_boxes[k-1].text="Joueur"+str(k)
                        input_boxes[k-1].txt_surface=police2.render(input_boxes[k-1].text, True, input_boxes[k-1].color)
            
            #arrêt du jeu
            if event.type == QUIT:   
                dico_stop = dict.fromkeys(dico_stop, False)

def parametrisation_2(dico_erreurs={}):
    '''
    Fonction qui lance la paramétrisation des paramètres avancés de la partie
    '''    
    
    global fenetre, dico_stop
    
    dico_stop['parametrisation1']=False
    dico_stop['parametrisation2']=True
    
    #lecture du fichier de paramétrisation 
    dico_parametres=lecture(fichier)
    
    #stockage des choix
    dico_choix={}
    dico_choix['fonction']=game
    dico_choix['fonction_prec']=parametrisation_2
    dico_choix['nb_joueurs']=dico_parametres['nb_joueurs']
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
            choix.color=COLOR_ACTIVE 
    
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
                input_boxes[k].color=COLOR_ERROR

    while dico_stop['parametrisation2']==True :
                
        fenetre.blit(fond_uni,(0,0))
        
        #titre de la fenêtre
        fenetre.blit(police3.render("Paramètres avancés",True,pygame.Color("#000000")),(100,50))
        
        #affichage de l'éventuel message d'erreur 
        if len(dico_erreurs)!=0:
            if dico_erreurs['type']=='null':
                fenetre.blit(police2.render("ERREUR : Renseignez tous les champs!",True,COLOR_ERROR),(550,50))
            elif dico_erreurs['type']=='max':
                fenetre.blit(police2.render("ERREUR : Renseignez une valeur plus petite",True,COLOR_ERROR),(550,50))
        
        #dessin des boutons
        valider.draw(fenetre)  
        retour.draw(fenetre)
        
        #dessin des choicebox
        for choicebox in choix_taille:
            choicebox.draw(fenetre)
        
        #dessin des inputboxs
        for box in input_boxes:
            box.draw(fenetre)
            
        #Ecriture des textes associés aux boxes
        fenetre.blit(police2.render("Dimensions du plateau: ",True,pygame.Color("#000000")),(100,110))
        fenetre.blit(police2.render("Nombre de fantômes: ",True,pygame.Color("#000000")),(100,180))
        n=int(dico_choix['dimensions_plateau'])
        nb_fant=(n-2)*(n//2)+(n//2)*(n//2-1)
        fenetre.blit(police1.render("Entier positif / Maximum:"+str(nb_fant),True,pygame.Color("#000000")),(100,210))
        fenetre.blit(police1.render("Configuration standard : "+str(nb_fant)+" fantômes pour un plateau de taille "+str(dico_choix['dimensions_plateau'])+"x"+str(dico_choix['dimensions_plateau'])+".",True,pygame.Color("#000000")),(100,230))
        fenetre.blit(police2.render("Nombre de fantômes par ordre de mission: ",True,pygame.Color("#000000")),(100,250))
        fenetre.blit(police1.render("Entier positif / Configuration standard : 3 fantômes.",True,pygame.Color("#000000")),(100,280))
        fenetre.blit(police2.render("Joker(s) par joueur: ",True,pygame.Color("#000000")),(100,320))
        fenetre.blit(police1.render("Entier positif / Configuration standard : 1 joker.",True,pygame.Color("#000000")),(100,350))
        fenetre.blit(police2.render("Points gagnés par pépite ramassée: ",True,pygame.Color("#000000")),(100,390))    
        fenetre.blit(police1.render("Entier positif / Configuration standard : 1 point.",True,pygame.Color("#000000")),(100,420))                                                                                                                                                                                                                                                                                                
        fenetre.blit(police2.render("Points gagnés par fantôme capturé: ",True,pygame.Color("#000000")),(100,460))
        fenetre.blit(police1.render("Entier positif / Configuration standard : 5 points.",True,pygame.Color("#000000")),(100,490))
        fenetre.blit(police2.render("Points gagnés par fantôme capturé: ",True,pygame.Color("#000000")),(100,530))  
        fenetre.blit(police2.render("si le fantôme figure sur l'ordre de mission",True,pygame.Color("#000000")),(100,560))
        fenetre.blit(police1.render("Entier positif / Configuration standard : 20 points.",True,pygame.Color("#000000")),(100,590))
        fenetre.blit(police2.render("Bonus lors du remplissage d'une mission: ",True,pygame.Color("#000000")),(100,630))
        fenetre.blit(police1.render("Entier positif / Configuration standard : 40 points.",True,pygame.Color("#000000")),(100,660)) 
                                                                               
        #actualisation de l'écran
        pygame.display.flip()
        
        #gestion des évènements
        for event in pygame.event.get():
            
            #gestion des boutons
            valider.handle_event(event,action=enregistrement_inputs, parametre_action=dico_choix)
            retour.handle_event(event,action=parametrisation_1)
            
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
                dico_stop = dict.fromkeys(dico_stop, False)
    

def enregistrement_inputs(dico):
    global fichier
    """
    fonction d'enregistrement des paramètres inputs
    dico : dictionnaire avec les paramètres, 
    dont un paramètre (fonction) correspond à la fonction suivante appelée. 
    """
    
    ecriture(fichier, dico)
    
    if dico['test_null']==True:
        tests_null_inputs(dico)
    elif dico['test_max']==True:
        tests_max_inputs(dico)
    else:
        fonction_suivante=dico['fonction']
        fonction_suivante()

def tests_max_inputs(dico):
    """
    fonction qui teste la conformité des paramètres  renseignés par les joueurs. 
    dico : dictionnaire avec les paramètres, 
    dont un paramètre (fonction) correspond à la fonction suivante appelée.
    dont un paramètre (fonction_prec) correspond à la fonction d'origine. 
    Les types ne sont pas testés car ils sont forcés lors de l'entrée de l'utilisateur.
    La fonction vérifie si les valeurs maximale ne sont pas dépassées. 
    """
    
    #dictionnaire des maximums autorisés pour chaque paramètre (s'il y en a).
    n=int(dico['dimensions_plateau'])
    nb_fant=(n-2)*(n//2)+(n//2)*(n//2-1)
    dico_max={'nb_fantomes': nb_fant, 'nb_fantomes_mission': nb_fant//int(dico['nb_joueurs']), 
                'nb_joker': 10, 'points_pepite': 50, 'points_fantome': 200, 
                'points_fantome_mission': 200, 'bonus_mission': 500}
    
    dico_erreurs={}
    
    for cle_input in dico.keys():
        
        #on vérifie si les valeurs renseignées ne dépassent pas le maximum autorisé
        for cle_max in dico_max:
            if cle_input==cle_max:
                if int(dico[cle_input])>dico_max[cle_max]:
                    dico_erreurs[cle_input]='max'
                    
    if len(dico_erreurs)==0:
        dico['test_max']=False
        fonction_suivante=dico['fonction']
        if fonction_suivante==game:
            fonction_suivante()
        else:
            fonction_suivante(dico)
    else:
        dico_erreurs['type']='max'
        fonction_prec=dico['fonction_prec']
        fonction_prec(dico_erreurs)
                        
def tests_null_inputs(dico):
    """
    fonction qui teste la conformité des paramètres  renseignés par les joueurs. 
    dico : dictionnaire avec les paramètres, 
    dont un paramètre (fonction) correspond à la fonction suivante appelée.
    dont un paramètre (fonction_prec) correspond à la fonction d'origine. 
    Les types ne sont pas testés car ils sont forcés lors de l'entrée de l'utilisateur.
    La fonction vérifie que les inputsboxs ne sont pas vide et renvoie un message d'erreur si c'est le cas. 
    """
    
    #liste qui renseigne les paramètres ne pouvant être nulls. 
    #(seulement ceux pour lesquels il est possible que l'utilisateur entre une valeur nulle).
    L_null=['pseudo_joueur_1', 'pseudo_joueur_2','pseudo_joueur_3','pseudo_joueur_4',
            'nb_fantomes', 'nb_fantomes_mission','nb_joker', 'points_pepite', 
            'points_fantome', 'points_fantome_mission', 'bonus_mission']
    
    dico_erreurs={}
    
    for cle_input in dico.keys():
        
        #on vérifie que l'utilisateur a bien renseigné les valeurs
        for cle_null in L_null:
            if cle_null==cle_input:
                if len(dico[cle_input])==0:
                    dico_erreurs[cle_null]='null'
                    
    if len(dico_erreurs)==0:
        dico['test_null']=False
        if dico['test_max']==True:
            fonction_suite=tests_max_inputs
            fonction_suite(dico)
        else:
            fonction_suite=dico['fonction']
            fonction_suite()
    else:
        dico_erreurs['type']='null'
        fonction_prec=dico['fonction_prec']
        fonction_prec(dico_erreurs)

#-----------------------------------------Affichage graphique et début du jeu------------------------------

pygame.init()

#Ouverture de la fenêtre Pygame
fenetre = pygame.display.set_mode((1200, 700),pygame.RESIZABLE)



#Creation des images du menu
fond_menu = pygame.image.load("fond_menu.png").convert()
fond_uni = pygame.image.load("fond_uni.png").convert()
#Création de la police du jeu
police = pygame.font.SysFont("calibri", 20, bold=True) #Load font object.
police_small = pygame.font.SysFont("calibri", 17, bold=True) #Load font object.

COLOR_INACTIVE = pygame.Color('lightskyblue3')
COLOR_ACTIVE = pygame.Color('dodgerblue2')
COLOR_ERROR = pygame.Color('tomato2')
police1=pygame.font.SysFont('calibri', 15)
police2=pygame.font.SysFont('calibri', 25)
police3=pygame.font.SysFont('calibri', 35)
fichier="mine_hantee_config.txt" 

#Lancement du menu
menu()
pygame.quit()
