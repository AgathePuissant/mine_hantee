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
        else:
            retour.append("Vous ne pouvez pas aller dans cette direction")
            
        retour.append(cartes_accessibles)
        #print(retour)

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
    print(plateau.position)
    chemins_possibles_total = [] #Liste des listes de chemins possibles pour chaque insertion possible, donc liste de liste de liste
    
    #On recueille les données des adversaires i.e. leurs fantomes target
    target_adversaires = [] 
    for i in plateau.dico_joueurs.keys():
        if i != id_joueur : 
            for j in plateau.dico_joueurs[i].fantome_target :
                target_adversaires.append(j)
        
        
    #Pour toutes les insertions possibles, on stocke tous les chemins possibles
    #Pour le joueur donné
    for i in plateau.insertions_possibles: 
        plateau.deplace_carte(i)
        print(plateau.position,"plateau")
        print(plateau_en_cours.position,"plateau-en-cours")
        chemins_possibles = plateau.chemins_possibles(plateau.dico_joueurs[id_joueur].carte_position)
        chemins_possibles_total.append(chemins_possibles)
        #On réinitialise les emplacements des cartes à celles du plateau en cours
        plateau = copy.deepcopy(plateau_en_cours)


    dico_heuristique = {} #dico avec le rang (couple) d'un chemin dans chemin_possibles_total en clé et son heuristique en valeur
    

    for k in range(len(chemins_possibles_total)): #Ensembles de chemins possibles
        for i in range(len(chemins_possibles_total[k])) : #chemin possible parmi cet ensemble
            
            heuristique = 0
            #On examine chaque case
            for j in chemins_possibles_total[k][i]:
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
                    
            dico_heuristique[(k,i)] = heuristique
    
    #On trouve l'heuristique maximale
    max_heur = max(dico_heuristique.values())
    print(max_heur)
    
    chemins_opti = []
    inser_opti = []
    
    #On trouve le/les chemin(s) correspondant à l'heuristique maximale
    for couple in dico_heuristique.keys():
        if dico_heuristique[couple] == max_heur :
            chemins_opti.append(chemins_possibles_total[couple[0]][couple[1]])
            #On trouve les coordonnées de l'insertion correspondant au chemin optimal trouvé
            inser_opti.append(plateau.insertions_possibles[couple[0]])
    

    #Si il n'y a qu'un seul chemin optimal, on le choisit
    if len(chemins_opti) == 1:
        return (inser_opti[0],chemins_opti[0])
    
    #Sinon on prend au hasard parmi les chemins optimaux
    #On pourrait aussi faire le choix de prendre celui qui inclu la capture d'un fantôme par ex
    else:
        rang = rd.randint(0,len(chemins_opti))
        return (inser_opti[rang], chemins_opti[rang])
        
    


#plat = plateau(3,["Antoine","Christine","Michel"],[],7)
#print(IA_simple(1,plat))


 
    
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
    
def affiche_plateau(plat,fenetre):
    #Chargement et collage du fond
    
    fenetre.blit(fond_ext,(0,0))
    fenetre.blit(fond, (0,0))
    
    
    for i in range(len(plat.position)) :
        for j in range(len(plat.position)) :
            x=plat.dico_cartes[plat.position[i,j]].coord[0]*100
            y=plat.dico_cartes[plat.position[i,j]].coord[1]*100
            
            for k in range(len(plat.dico_cartes[plat.position[i,j]].orientation)) :
               if plat.dico_cartes[plat.position[i,j]].orientation[k]==1 :
                   if k==0 :
                       fenetre.blit(mur1,(y,x))
                   elif k==1 :
                       fenetre.blit(mur4,(y,x))
                   elif k==2 :
                       fenetre.blit(mur2,(y,x))
                   elif k==3 :
                       fenetre.blit(mur3,(y,x))
                       
# Si on veut ajouter un graphisme pour les cartes déplaçables et indéplaçables
                       
            if plat.dico_cartes[plat.position[i,j]].deplacable==False :
                fenetre.blit(indeplacable,(y,x))
                
                       
            if plat.dico_cartes[plat.position[i,j]].presence_pepite==True:
                fenetre.blit(pepite,(y,x))
            if plat.dico_cartes[plat.position[i,j]].id_fantome!=0 :
                fenetre.blit(fantome,(y,x))
                fenetre.blit(police.render(str(plat.dico_cartes[plat.position[i,j]].id_fantome),True,pygame.Color("#FFFFFF")),(y+10,x+40))
                       
    for i in range(len(plat.dico_joueurs)) :
        x=plat.dico_joueurs[i].carte_position.coord[0]*100
        y=plat.dico_joueurs[i].carte_position.coord[1]*100
        fenetre.blit(liste_im_joueur[i],(y,x))
        
    
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
      

def actualise_fenetre(plateau,fenetre,joueur):
    """
    fonction pour actualiser l'affichage dans la fonction jeu
    """
    affiche_plateau(plateau,fenetre)
    for i in range(len(plateau.dico_joueurs)) :
                fenetre.blit(police.render("Score joueur "+str(i+1)+" : "+str(plateau.dico_joueurs[i].points),True,pygame.Color("#FFFFFF")),(760,300+i*100))
                #test texte pour afficher le joueur qui joue
    fenetre.blit(police.render("C'est a "+str(joueur.nom)+" de jouer",False,pygame.Color(0,0,0)),(760,250))
    pygame.display.flip()
      

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
    
    erreur_deplacement="" #Initialisation du texte d'erreur ???
    
    
    
    #Boucle du jeu. On joue tant qu'il reste des fantômes à attraper
    while plateau_test.id_dernier_fantome!=21:
        #collage du plateau
        affiche_plateau(plateau_test,fenetre) 
        
        #affichage des scores
        for i in range(len(plateau_test.dico_joueurs)) :
                fenetre.blit(police.render("Score joueur "+str(i+1)+" : "+str(plateau_test.dico_joueurs[i].points),True,pygame.Color("#FFFFFF")),(760,300+i*100))
        
        #affichage du message d'erreur ?                       
        fenetre.blit(police.render(erreur_deplacement,True,pygame.Color("#000000")),(750,250)) 
        #Update l'écran                                                                
        pygame.display.flip() 
        

        #Tours de jeu
        #on parcours chaque joueur à chaque tours.
        for j in plateau_test.dico_joueurs :
            
            joueur=plateau_test.dico_joueurs[j]
            actualise_fenetre(plateau_test,fenetre,joueur)
            
            
            #premiere etape : rotation et insertion de la carte
            #On parcours la liste de tous les événements reçus tant qu'une carte n'a pas été insérée
            test_carte="en cours"
            while test_carte!="fin":
                
                for event in pygame.event.get():   
                    
                    #Si on appuie sur R, rotation de la carte à jouer
                    if event.type == KEYDOWN and event.key == K_r: 
                        plateau_test.carte_a_jouer.orientation[0],plateau_test.carte_a_jouer.orientation[1],plateau_test.carte_a_jouer.orientation[2],plateau_test.carte_a_jouer.orientation[3]=plateau_test.carte_a_jouer.orientation[3],plateau_test.carte_a_jouer.orientation[0],plateau_test.carte_a_jouer.orientation[1],plateau_test.carte_a_jouer.orientation[2]
                        #Update l'écran                                                                
                        actualise_fenetre(plateau_test,fenetre,joueur)
                    
                    #ajouter la carte lorsque l'utilisateur clique dans le plateau
                    elif event.type == MOUSEBUTTONDOWN : 
                        #clic gauche : insertion de la carte à jouer
                        if event.button==1: 
                            coord=[event.pos[1]//100,event.pos[0]//100]
                            #Si les coordonnées sont hors du plateau
                            if coord[0]>plateau_test.N-1 :
                                erreur_deplacement="Cliquez dans le plateau"
                            #Sinon, on vérifie que la case cliquée est déplaçable
                            else :
                                test_inser=plateau_test.deplace_carte(coord)
                                #Update l'écran                                                                
                                actualise_fenetre(plateau_test,fenetre,joueur)
                                #Si ce n'est pas le cas:
                                if test_inser==False :
                                    erreur_deplacement="Insertion impossible"
                                #Sinon, on finit cette section du tours
                                else :
                                    erreur_deplacement=""
                                    test_carte="fin"

                    

                    elif event.type == QUIT:
                        pygame.display.quit()
                        pygame.quit()
               
                                    
                                    
            #2e etape : On parcours les évènements tant que le joueur n'a pas appuyé sur entrée ou tant qu'il peut encore se déplacer
            #initialisation à la position du joueur
            test_entree=False
            carte_actuelle=joueur.carte_position
            cartes_accessibles=plateau_test.cartes_accessibles1(carte_actuelle)
            #parcours des evenements
            while test_entree==False and len(cartes_accessibles)>0:#La 2e condition deconne a cause de cartes_accessibles
                for event in pygame.event.get():
                    #deplacement
                    if event.type == KEYDOWN and (event.key == K_UP or event.key == K_LEFT or event.key == K_DOWN or event.key == K_RIGHT) : #touches directionnelles : déplacement du joueur
                        plateau_test.deplace_joueur(j,event.key)
                        carte_actuelle=joueur.carte_position
                        cartes_accessibles=plateau_test.cartes_accessibles1(carte_actuelle)
                        
                        #Update l'écran                                                                
                        actualise_fenetre(plateau_test,fenetre,joueur)
                        
                    #fin de tour
                    if event.type == KEYDOWN and (event.key== K_RETURN):
                        test_entree=True
                        #Update l'écran                                                                
                        actualise_fenetre(plateau_test,fenetre,joueur)
                        
                    elif event.type == QUIT:
                        pygame.display.quit()
                        pygame.quit()

                    
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
    global fenetre,liste_sauv,num_partie,nouvelle
    
    if liste_sauv!=[]:
        num_partie=np.max(liste_sauv)+1
    else :
        num_partie=1
        
    nouvelle=True
        
    game()
    


#-----------------------------------------Affichage graphique et début du jeu------------------------------

pygame.init()

#Ouverture de la fenêtre Pygame
fenetre = pygame.display.set_mode((1200, 700),pygame.RESIZABLE)



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
fond_uni = pygame.image.load("fond_uni.png").convert()
indeplacable = pygame.image.load("indeplacable.png").convert_alpha()
#Création de la police du jeu
police = pygame.font.Font("SuperMario256.ttf", 20) #Load font object.


#Lancement du menu
menu()
pygame.quit()
