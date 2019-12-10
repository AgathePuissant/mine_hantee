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
    
    def __init__(self, ID, nom, niveau, fantome_target, carte_position):
        self.id = ID
        self.nom = nom
        self.niveau = niveau
        self.fantome_target = fantome_target
        self.carte_position = carte_position
        self.points = 0
        self.cartes_explorees = [carte_position]
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
        self.insertions_possibles=[] #liste des coordonnees des insertiones possible des cartes sur le plateau. 
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
        self.nbre_fantomes = (N-2)*(N//2)+(N//2)*(N//2-1)
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
                    #print(["indéplaçable",ligne,colonne])
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
                    #print(orientation)
                
                #cases déplaçables
                else:
                    #print("deplaçable"+str(ligne)+str(colonne))
                    orientation=pool[compte_deplacable]
                    compte_deplacable+=1
                    deplacable=True
                    #Si la carte déplaçable ne fait pas partie de la couronne extérieure
                    #Elle accueille un fantome
                    if ligne>0 and ligne<N-1 and colonne>0 and colonne<N-1:
                        id_fantome=pool_fantomes[compte_fantomes]
                        compte_fantomes += 1
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
        retour = []
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
            retour.append(" Déplacement impossible")
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
                    retour.append("Case déjà explorée")
                
                else:
                    self.dico_joueurs[id_joueur].carte_position = nv_carte #On déplace le joueur
                    self.dico_joueurs[id_joueur].cartes_explorees.append(nv_carte)
                    
                    #Si il y a une pépite sur la nouvelle carte, le joueur la ramasse
                    if nv_carte.presence_pepite == True : 
                        self.dico_joueurs[id_joueur].points += 1
                        nv_carte.presence_pepite = False
                        retour.append("Pépite")
                    
                    #Si il y a un fantôme sur la nouvelle carte, le joueur le capture si c'est possible
                    #i.e. si c'est le fantôme à capturer et s'il n'a pas encore capturé de fantôme pendant ce tour
                    if nv_carte.id_fantome == self.id_dernier_fantome+1 and self.dico_joueurs[id_joueur].capture_fantome == False :
                        #Si le fantôme est sur l'ordre de mission, le joueur gagne 20 points
                        if nv_carte.id_fantome in self.dico_joueurs[id_joueur].fantome_target : 
                            self.dico_joueurs[id_joueur].points += 20
                            self.dico_joueurs[id_joueur].fantome_target.remove(nv_carte.id_fantome)
                            retour.append("Fantôme sur l'ordre de mission")
                            #Si l'ordre de mission est totalement rempli, le joueur gagne 40 points
                            if self.dico_joueurs[id_joueur].fantome_target==[]:
                                self.dico_joueurs[id_joueur].points += 40
                                retour.append("Ordre de mission rempli")
                        #Si le fantôme n'est pas sur l'ordre de mission, le joueur gagne 5 points
                        else:
                            self.dico_joueurs[id_joueur].points += 5
                            retour.append("Fantôme capturé")
                        
                        self.dico_joueurs[id_joueur].capture_fantome = True
                        self.id_dernier_fantome += 1
                        nv_carte.id_fantome = 0
            else:
                retour.append("Déplacement impossible")
                
        retour=' et '.join(retour)
                
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
        #On teste pour chaque orientation de la carte
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
        for i in range(len(chemins_possibles_total[k])) : #i: rang du sous-sous ensemble corrspondant à l'orientation de la carte
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
    print(max_heur)
    
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
    

    #Si il n'y a qu'un seul chemin optimal, on le choisit
    if len(chemins_opti) == 1:
        return (inser_opti[0],orientation_opti[0],chemins_opti[0])
    
    #Sinon on prend au hasard parmi les chemins optimaux
    #On pourrait aussi faire le choix de prendre celui qui inclu la capture d'un fantôme par ex
    else:
        rang = rd.randint(0,len(chemins_opti))
        return (inser_opti[rang], orientation_opti[rang],chemins_opti[rang])
        
    


plat = plateau(3,["Antoine","Christine","Michel"],[],7)
print(IA_simple(2,plat))
#print(plat.position)
#print(plat.dico_joueurs[0].carte_position.coord,plat.dico_joueurs[1].carte_position.coord,plat.dico_joueurs[2].carte_position.coord)


#---------------------------------------Définition des objets graphiques---------------------------------
 
#code nécessaire pour créer des boutons associés à une action
def text_objects(text, font):
    textSurface = font.render(text, True, pygame.Color("#000000"))
    return textSurface, textSurface.get_rect()
      
def button(fenetre,msg,x,y,w,h,ic,ac,action=None, parametre_action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    
    if x+w > mouse[0] > x and y+h > mouse[1] > y:
        pygame.draw.rect(fenetre, ac,(x,y,w,h))

        if click[0] == 1 and action != None:
            if parametre_action==None:
                action()    
            else:
                action(parametre_action)
    else:
        pygame.draw.rect(fenetre, ic,(x,y,w,h))

    textSurf, textRect = text_objects(msg, police2)
    textRect.center = ( (x+(w/2)), (y+(h/2)) )
    fenetre.blit(textSurf, textRect)
    
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
    

#definition des Inputboxs
    
class InputBox:

    def __init__(self, x, y, w, h, text='', max_caract=10):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.text = text
        self.txt_surface = police2.render(text, True, self.color)
        self.active = False
        self.max_caract=max_caract

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
                elif len(self.text)<self.max_caract:
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
    police = pygame.font.Font("coda.ttf", int(20*7/N)) #Load font object.
    
    for i in range(len(plat.position)) :
        for j in range(len(plat.position)) :
            x=plat.dico_cartes[plat.position[i,j]].coord[0]*int(100*7/N)
            #print(plat.dico_cartes[plat.position[i,j]].coord[0]*int(100*7/N))
            y=plat.dico_cartes[plat.position[i,j]].coord[1]*int(100*7/N)
            #print(plat.dico_cartes[plat.position[i,j]].coord[1]*int(100*7/N))
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
               
def actualise_fenetre(plateau,fenetre,joueur,info):

    affiche_plateau(plateau,fenetre)
    for i in range(len(plateau.dico_joueurs)) :
                fenetre.blit(police.render("Score joueur "+str(i+1)+" : "+str(plateau.dico_joueurs[i].points),False,pygame.Color("#000000")),(850,360+i*80))
                #test texte pour afficher le joueur qui joue
    fenetre.blit(police.render("C'est a "+str(joueur.nom)+" de jouer",False,pygame.Color(0,0,0)),(800,240))
    #affichage du message d'erreur ?                       
    fenetre.blit(police_small.render(info,False,pygame.Color("#000000")),(760,170))
                                                                        
    pygame.display.flip()

    
#---------------------------------------Défintion des instructions graphiques------------------------------
    
def menu():
    global fenetre,liste_sauv,num_partie,nouvelle
    
    intro = True

    while intro==True: #Boucle infinie
                
                
        fenetre.blit(fond_menu,(0,0))  #On colle le fond du menu
        
        liste_sauv=glob.glob("sauvegarde*")
        liste_sauv=[int(liste_sauv[i][-1]) for i in range(len(liste_sauv))]
        
        nouvelle=False
        
        #Création du bouton qui lance le jeu
        button(fenetre,"Nouvelle partie",500,350,200,50,pygame.Color("#b46503"),pygame.Color("#d09954"),nouvelle_partie)
        button(fenetre,"Charger une partie",500,450,200,50,pygame.Color("#b46503"),pygame.Color("#d09954"),charger_partie)
                                                                     
        pygame.display.flip() #Update l'écran
        
        for event in pygame.event.get(): #Instructions de sortie
            if event.type == pygame.QUIT:
                intro=False
                pygame.display.quit()
                pygame.quit()
      

def game() :
    global fenetre,num_partie,nouvelle,plateau_test
    #Initialisation d'une nouvelle partie ou chargement d'une ancienne partie
    if nouvelle==False :
        plateau_test=pickle.load(open("sauvegarde"+str(num_partie),"rb"))
    elif nouvelle==True:
        #Plateau de plateau_test
        plateau_test=plateau(3,["Antoine","Christine","Michel"],[],7)
    else :
        pass


    N = plateau_test.N
    information="" #Initialisation du texte d'erreur ???
    
    
    
    #Boucle du jeu. On joue tant qu'il reste des fantômes à attraper
    while plateau_test.id_dernier_fantome!=plateau_test.nbre_fantomes:
        

        #Tours de jeu
        #on parcours chaque joueur à chaque tours.
        for j in plateau_test.dico_joueurs :
            joueur=plateau_test.dico_joueurs[j]

            actualise_fenetre(plateau_test,fenetre,joueur,information)
            
            #premiere etape : rotation et insertion de la carte
            #On parcours la liste de tous les événements reçus tant qu'une carte n'a pas été insérée
            test_carte="en cours"
            
            while test_carte!="fin":
                
                for event in pygame.event.get():   
                    
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
                                test_carte="fin"

                    elif event.type == KEYDOWN and event.key == K_SPACE :
                        pause()
                    
                    elif event.type == QUIT:
                        pygame.display.quit()
                        pygame.quit()
                        
                actualise_fenetre(plateau_test,fenetre,joueur,information)
               
                                    
                                    
            #2e etape : On parcours les évènements tant que le joueur n'a pas appuyé sur entrée ou tant qu'il peut encore se déplacer
            #initialisation à la position du joueur
            test_entree=False
            
            carte_actuelle=joueur.carte_position
            
            cartes_accessibles=plateau_test.cartes_accessibles1(carte_actuelle)
            
            information=""
            
            #parcours des evenements
            while test_entree==False and len(cartes_accessibles)>0:#La 2e condition deconne a cause de cartes_accessibles
                for event in pygame.event.get():
                    #deplacement
                    if event.type == KEYDOWN and (event.key == K_UP or event.key == K_LEFT or event.key == K_DOWN or event.key == K_RIGHT) : #touches directionnelles : déplacement du joueur
                        information=plateau_test.deplace_joueur(j,event.key)
                        carte_actuelle=joueur.carte_position
                        cartes_accessibles=plateau_test.cartes_accessibles1(carte_actuelle)
                        
                        
                    #fin de tour
                    if event.type == KEYDOWN and (event.key== K_RETURN):
                        test_entree=True
                        information=""
                        
                        
                    elif event.type == KEYDOWN and event.key == K_SPACE :
                        pause()
                        
                    elif event.type == QUIT:
                        pygame.display.quit()
                        pygame.quit()
                        
                #Update l'écran                                                                
                actualise_fenetre(plateau_test,fenetre,joueur,information)

                    
            #Fin du tour du joueur : On ré-initialise cartes_explorees et capture_fantome
            joueur.cartes_explorees = [carte_actuelle]
            joueur.capture_fantome = False

                
def pause() :
    global fenetre,texte_sauv,nouvelle
    
    nouvelle="jeu en pause"
    
    pause=True
    
    texte_sauv=""
    
    while pause==True :
                
        fenetre.blit(fond_uni,(0,0))
    
        fenetre.blit(police.render("Pause",True,pygame.Color("#000000")),(600,200))
                                                             
        button(fenetre,"Sauvegarder",550,350,200,50,pygame.Color("#b46503"),pygame.Color("#d09954"),sauvegarder) 
                                                                 
        button(fenetre,"Retour au menu",550,450,200,50,pygame.Color("#b46503"),pygame.Color("#d09954"),menu)
                                  
        fenetre.blit(police.render(texte_sauv,True,pygame.Color("#000000")),(550,550))
                                                                
        pygame.display.flip() #Update l'écran
        
        for event in pygame.event.get():   #On parcours la liste de tous les événements reçus
                
            if event.type == KEYDOWN and event.key == K_SPACE :
                game()
                
            if event.type == QUIT:     #Si un de ces événements est de type QUIT
                pause = False      #On arrête la boucle
                pygame.display.quit()
                pygame.quit()
                

                
def sauvegarder():
    global texte_sauv,num_partie,plateau_test
    
    pickle.dump(plateau_test,open("sauvegarde"+str(num_partie),"wb"))
    texte_sauv="Partie sauvegardee"

    
def charger_partie():
    global fenetre,liste_sauv,num_partie,retour_partie
    
    charger=True
    retour_partie=False
        
    while charger ==True:
                
                
        if liste_sauv!=[] :
            
            fenetre.blit(fond_uni,(0,0))  #On colle le fond du menu
            
            for i in range(len(liste_sauv)) :
                button_charger_partie(fenetre,"Partie "+str(liste_sauv[i]),500,100+i*100,200,50,pygame.Color("#b46503"),pygame.Color("#d09954"),liste_sauv[i])
            
            if retour_partie==True :
                fenetre.blit(police.render("Partie "+str(num_partie)+" selectionnee",True,pygame.Color("#000000")),(800,100))
            
                button(fenetre,"Lancer la partie",800,300,200,50,pygame.Color("#b46503"),pygame.Color("#d09954"),game)
                                                                          
        else :
            
            fenetre.blit(fond_uni,(0,0))  #On colle le fond du menu
            fenetre.blit(police.render("Aucune partie sauvegardee",True,pygame.Color("#000000")),(450,100))
            button(fenetre,"Retour au menu",500,300,200,50,pygame.Color("#b46503"),pygame.Color("#d09954"),menu)
            
        pygame.display.flip() #Update l'écran
        
        for event in pygame.event.get():   #On parcours la liste de tous les événements reçus
            
            if event.type == QUIT:     #Si un de ces événements est de type QUIT
                charger = False      #On arrête la boucle
                pygame.display.quit()
                pygame.quit()
                
def nouvelle_partie():
    '''
    Fonction qui lance la paramétrisation d'une nouvelle partie
    demande le nombre de joueurs pour la partie (entre 2,3 et 4) 
    '''    
    global fenetre,liste_sauv,num_partie,nouvelle

    nouvelle=True
    #attribution du numéro de la partie
    if liste_sauv!=[]:
        num_partie=np.max(liste_sauv)+1
    else :
        num_partie=1
    
    parametrisation=True
    
    #initialisation des boxs pour le choix du nombre de joueurs
    choix_nb_joueur_2=ChoiceBox(475, 300, 50, 30, '2')
    choix_nb_joueur_3=ChoiceBox(575, 300, 50, 30, '3')
    choix_nb_joueur_4=ChoiceBox(675, 300, 50, 30, '4')
    choix_nb_joueurs=[choix_nb_joueur_2, choix_nb_joueur_3, choix_nb_joueur_4]
    
    #lecture du fichier de paramétrisation et initialisation du nombre de joueurs à la valeur renseignée dans le fichier
    dico_parametres=lecture(fichier)
    choix_final=dico_parametres['nb_joueurs']           #on stoque le choix entre les boutons dans choix_final
    for choix in choix_nb_joueurs:
            if choix.text==choix_final:
                choix.active=True
                choix.color=COLOR_ACTIVE
    
    while parametrisation==True :
                
        fenetre.blit(fond_uni,(0,0))
        
        #choix du nombre de joueurs 
        fenetre.blit(police3.render("Nouvelle partie!",True,pygame.Color("#000000")),(485,100))
        fenetre.blit(police3.render("Nombre de joueurs",True,pygame.Color("#000000")),(465,200))
        
        #Validation et passage à la page suivante
        button(fenetre,"Valider",500,450,200,50,COLOR_INACTIVE,COLOR_ACTIVE,parametrisation_1, choix_final)
        
        #retour au menu                                                       
        button(fenetre,"Retour",500,550,200,50,COLOR_INACTIVE,COLOR_ACTIVE,menu)
        
        #choix du nombre de joueurs
        for choix in choix_nb_joueurs:
            choix.draw(fenetre)
            if choix.active==True:
                choix_final=choix.text
                                                            
        #actualisation de l'écran
        pygame.display.flip()
        
        for event in pygame.event.get():
            
            #actualisation du choix du nombre de joueurs
            for choix in choix_nb_joueurs:
                choix.handle_event(event, choix_nb_joueurs)
            
            #arrêt du jeu
            if event.type == QUIT:   
                parametrisation = False      
                pygame.display.quit()
                pygame.quit()

def parametrisation_1(choix_final):
    """
    Fonction qui lance la paramétrisation des joueurs
    """
    
    global fenetre
    
    #actualisation du fichier de configuration en fonction du choix du nombre de joueurs qui a été réalisé
    dico_nb_joueurs={'nb_joueurs':choix_final}
    ecriture(fichier, dico_nb_joueurs)

    parametrisation1=True
    
    #lecture du fichier de paramétrisation 
    dico_parametres=lecture(fichier)
    
    #définition des inputbox (on en définit 4 même si les 4 ne sont pas forcément utilisées)
    input_box1=InputBox(350, 100, 150, 30, text=dico_parametres['pseudo_joueur_1'])
    input_box2=InputBox(350, 200, 150, 30, text=dico_parametres['pseudo_joueur_2'])
    input_box3=InputBox(350, 300, 150, 30, text=dico_parametres['pseudo_joueur_3'])
    input_box4=InputBox(350, 400, 150, 30, text=dico_parametres['pseudo_joueur_4'])
    input_boxes=[input_box1,input_box2,input_box3,input_box4]
    
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
    
    #initialisation des pseudos, des modes de jeu 
    #et des éventuels niveaux de ias en fonction des valeurs renseignées dans le fichier 
    #de configuration
    
    #on stoque le choix des pseudos des joueurs manuels dans choix_final_pseudos
    choix_final_pseudos=[input_box1.text,input_box2.text,input_box3.text,input_box4.text]
    
    #on stoque le choix des modes dans choix_final_modes
    choix_final_modes=[dico_parametres['mode_joueur_1'], dico_parametres['mode_joueur_2'], dico_parametres['mode_joueur_3'], dico_parametres['mode_joueur_4']]           
    for k in range(0,len(choix_modes_joueurs)):
        for choix in choix_modes_joueurs[k]:
            if choix.text==choix_final_modes[k]:
                choix.active=True
                choix.color=COLOR_ACTIVE
    
    #on stoque le choix des lvls des ias dans choix_lvl_joueurs
    choix_final_lvls=[dico_parametres['niveau_ia_1'], dico_parametres['niveau_ia_2'], dico_parametres['niveau_ia_3'], dico_parametres['niveau_ia_4']]           
    for k in range(0,len(choix_lvl_joueurs)):
        for choix in choix_lvl_joueurs[k]:
            if choix.text==choix_final_lvls[k]:
                choix.active=True
                choix.color=COLOR_ACTIVE
    
    while parametrisation1==True :
        
        fenetre.blit(fond_uni,(0,0))
        
        #paramètres des joueurs
        fenetre.blit(police3.render("Paramètres des joueurs",True,pygame.Color("#000000")),(100,50))
        
        for k in range(1,int(choix_final)+1):
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
                                                                 
        #retour au menu                                                       
        button(fenetre,"Retour",500,600,200,50,COLOR_INACTIVE,COLOR_ACTIVE,nouvelle_partie)
        
        #validation 
        #button(fenetre,"Valider",850,600,200,50,COLOR_INACTIVE,COLOR_ACTIVE,enregistrement_inputs,[1,choix_final,choix_final_pseudos,choix_final_modes,choix_final_lvls])                                                   
        button(fenetre,"Valider",850,600,200,50,COLOR_INACTIVE,COLOR_ACTIVE,parametrisation_2, [1,choix_final,choix_final_pseudos,choix_final_modes,choix_final_lvls])
                                                    
        #actualisation de l'écran
        pygame.display.flip()
        
        for event in pygame.event.get():
            
            #remplissage des inputboxs    
            for k in range(1,int(choix_final)+1):
                choix_manuel=choix_modes_joueurs[k-1][0]
                choix_automatique=choix_modes_joueurs[k-1][1]
                choix_manuel.handle_event(event,choix_modes_joueurs[k-1])
                choix_automatique.handle_event(event,choix_modes_joueurs[k-1])
                if choix_automatique.active:
                    choix_lvl1=choix_lvl_joueurs[k-1][0]
                    choix_lvl2=choix_lvl_joueurs[k-1][1]
                    choix_lvl3=choix_lvl_joueurs[k-1][2]
                    choix_lvl1.handle_event(event,choix_lvl_joueurs[k-1])
                    choix_lvl2.handle_event(event,choix_lvl_joueurs[k-1])
                    choix_lvl3.handle_event(event,choix_lvl_joueurs[k-1])
                    if choix_lvl1.active:
                        choix_final_lvls[k-1]=choix_lvl1.text
                    elif choix_lvl2.active:
                        choix_final_lvls[k-1]=choix_lvl2.text
                    elif choix_lvl2.active:
                        choix_final_lvls[k-1]=choix_lvl3.text
                    input_boxes[k-1].text="Ordinateur"+str(k)
                    input_boxes[k-1].txt_surface=police2.render(input_boxes[k-1].text, True, input_boxes[k-1].color)
                    choix_final_pseudos[k-1]=input_boxes[k-1].text
                    choix_final_modes[k-1]="automatique"
                else:
                    box=input_boxes[k-1]
                    box.handle_event(event)
                    choix_final_pseudos[k-1]=box.text
                    choix_final_modes[k-1]="manuel"
                    if input_boxes[k-1].text=="Ordinateur"+str(k):
                        input_boxes[k-1].text="Joueur"+str(k)
                        input_boxes[k-1].txt_surface=police2.render(input_boxes[k-1].text, True, input_boxes[k-1].color)
            
            #arrêt du jeu
            if event.type == QUIT:   
                parametrisation1 = False      
                pygame.display.quit()
                pygame.quit()

def parametrisation_2(L_inputs):
    '''
    Fonction qui lance la paramétrisation des paramètres avancés de la partie
    '''    
    global fenetre
    
    parametrisation2=True
    
    #lecture du fichier de paramétrisation 
    dico_parametres=lecture(fichier)
    
    #définition des inputboxs pour l'ensemble des paramètres restants
    #en initialisant les valeurs aux paramètres du fichier de paramétrisation. 
    ib_dimensions_plateau=InputBox(600, 110, 150, 30, text=dico_parametres['dimensions_plateau'])
    ib_nb_fantomes=InputBox(600, 180, 150, 30, text=dico_parametres['nb_fantomes'])
    ib_nb_fantomes_mission=InputBox(600, 250, 150, 30, text=dico_parametres['nb_fantomes_mission'])
    ib_nb_joker=InputBox(600, 320, 150, 30, text=dico_parametres['nb_joker'])
    ib_points_pepite=InputBox(600, 390, 150, 30, text=dico_parametres['points_pepite'])
    ib_points_fantome=InputBox(600, 460, 150, 30, text=dico_parametres['points_fantome'])
    ib_points_fantome_mission=InputBox(600, 530, 150, 30, text=dico_parametres['points_fantome_mission'])
    ib_bonus_mission=InputBox(600, 630, 150, 30, text=dico_parametres['bonus_mission'])
    input_boxes=[ib_dimensions_plateau,ib_nb_fantomes,ib_nb_fantomes_mission,ib_nb_joker,ib_points_pepite,ib_points_fantome,ib_points_fantome_mission,ib_bonus_mission]
    
    #Stockage des choix des inputs
    choix_final_inputs=[]
    for k in range(0,len(input_boxes)):
        choix_final_inputs=choix_final_inputs+[input_boxes[k].text]

    while parametrisation2==True :
                
        fenetre.blit(fond_uni,(0,0))
        
        #titre de la fenêtre
        fenetre.blit(police3.render("Paramètres avancés",True,pygame.Color("#000000")),(100,50))
        
        #Validation et passage à la page suivante
        button(fenetre,"Lancer la partie !",900,300,200,50,COLOR_INACTIVE,COLOR_ACTIVE,enregistrement_inputs,L_inputs)
        
        #retour au menu                                                       
        button(fenetre,"Retour",900,400,200,50,COLOR_INACTIVE,COLOR_ACTIVE,parametrisation_1, L_inputs[1])
        
        #dessin des inputboxs
        for box in input_boxes:
            box.draw(fenetre)
            
        #Ecriture des textes associés aux boxes
        fenetre.blit(police2.render("Dimensions du plateau: ",True,pygame.Color("#000000")),(100,110))
        fenetre.blit(police2.render("Nombre de fantômes: ",True,pygame.Color("#000000")),(100,180))
        fenetre.blit(police1.render("Entier positif / Maximum:"+str(input_boxes[0].text),True,pygame.Color("#000000")),(100,210))
        fenetre.blit(police1.render("Configuration standard : 21 fantômes pour un plateau de taille "+input_boxes[0].text+"x"+input_boxes[0].text+".",True,pygame.Color("#000000")),(100,230))
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
        fenetre.blit(police1.render("Entier positif / Configuration standard : 20 points pour la configuration.",True,pygame.Color("#000000")),(100,590))
        fenetre.blit(police2.render("Bonus lors du remplissage d'une mission: ",True,pygame.Color("#000000")),(100,630))
        fenetre.blit(police1.render("Entier positif / Configuration standard : 40 points.",True,pygame.Color("#000000")),(100,660)) 
                                                                                                  
        #actualisation de l'écran
        pygame.display.flip()
        
        #gestion des évènements
        for event in pygame.event.get():
            
            for k in range(0,len(input_boxes)):
                box=input_boxes[k]
                box.handle_event(event)
                choix_final_inputs[k]=box.text
            
            #arrêt du jeu
            if event.type == QUIT:   
                parametrisation2 = False      
                pygame.display.quit()
                pygame.quit()
    

def enregistrement_inputs(arg):

    dico={'nb_joueurs':arg[1], 
          'mode_joueur_1':arg[3][0],'mode_joueur_2':arg[3][1],'mode_joueur_3':arg[3][2],'mode_joueur_4':arg[3][3],
          'pseudo_joueur_1':arg[2][0],'pseudo_joueur_2':arg[2][1],'pseudo_joueur_3':arg[2][2],'pseudo_joueur_4':arg[2][3],
          'niveau_ia_1':arg[4][0],'niveau_ia_2':arg[4][1],'niveau_ia_3':arg[4][2],'niveau_ia_4':arg[4][3]}
    
    ecriture(fichier, dico)
    game()
    
    


#-----------------------------------------Affichage graphique et début du jeu------------------------------

pygame.init()

#Ouverture de la fenêtre Pygame
fenetre = pygame.display.set_mode((1200, 700),pygame.RESIZABLE)



#Creation des images du menu
fond_menu = pygame.image.load("fond_menu.png").convert()
fond_uni = pygame.image.load("fond_uni.png").convert()
#Création de la police du jeu
police = pygame.font.Font("coda.ttf", 20) #Load font object.
police_small = pygame.font.Font("coda.ttf", 17) #Load font object.

COLOR_INACTIVE = pygame.Color('lightskyblue3')
COLOR_ACTIVE = pygame.Color('dodgerblue2')
police1=pygame.font.SysFont('calibri', 15)
police2=pygame.font.SysFont('calibri', 25)
police3=pygame.font.SysFont('calibri', 35)
fichier="mine_hantee_config.txt" 

#Lancement du menu
menu()
pygame.quit()
