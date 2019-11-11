# -*- coding: utf-8 -*-
"""
Éditeur de Spyder

Ceci est un script temporaire.
"""

import numpy as np
import random as rd

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
    
    
    def deplace_joueur(self,id_joueur,input):
        
        entite_joueur = self.dico_joueurs[id_joueur]
        entite_carte = entite_joueur.carte_position
        carte_coord = entite_carte.coord
        retour = [] #Stocke les informations nécessaires à renvoyer au joueur dans l'interface graphique
        
        #On stocke les coordonnées de la carte où on veut aller
        if input == "DOWN":  
            nv_coord = [carte_coord[0],carte_coord[1]+1]
            direction = 0 #rang du côté concerné dans l'attribut orientation de la nouvelle carte
        
        elif input == "LEFT":
            nv_coord = [carte_coord[0]-1,carte_coord[1]]
            direction = 1
        
        elif input == "UP":
            nv_coord = [carte_coord[0],carte_coord[1]-1]
            direction = 2
        
        elif input == "RIGHT":
            nv_coord = [carte_coord[0]+1,carte_coord[1]]
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
                if nv_carte in entite_joueur.cartes_explorees:
                    retour.append("Vous avez déjà exploré cette carte")
                
                else:
                    entite_joueur.carte_position = nv_carte #On déplace le joueur
                    entite_joueur.cartes_explorees.append(nv_carte)
                    
                    #Si il y a une pépite sur la nouvelle carte, le joueur la ramasse
                    if nv_carte.presence_pepite == True : 
                        entite_joueur.points += 1
                        nv_carte.presence_pepite = False
                        retour.append("nouvelle pépite")
                    
                    #Si il y a un fantôme sur la nouvelle carte, le joueur le capture si c'est possible
                    #i.e. si c'est le fantôme à capturer et s'il n'a pas encore capturé de fantôme pendant ce tour
                    if nv_carte.id_fantome == self.id_dernier_fantome+1 and entite_joueur.capture_fantome == False :
                        #Si le fantôme est sur l'ordre de mission, le joueur gagne 20 points
                        if nv_carte.id_fantome in entite_joueur.fantome_target : 
                            entite_joueur.points += 20
                            entite_joueur.fantome_target.remove(nv_carte.id_fantome)
                            retour.append("fantome sur l'ordre de mission capturé")
                            #Si l'ordre de mission est totalement rempli, le joueur gagne 40 points
                            if entite_joueur.fantome_target==[]:
                                entite_joueur.points += 40
                                retour.append("ordre de mission rempli")
                        #Si le fantôme n'est pas sur l'ordre de mission, le joueur gagne 5 points
                        else:
                            entite_joueur.points += 5
                            retour.append("fantome capturé")
                        
                        entite_joueur.capture_fantome = True
                        self.id_dernier_fantome += 1
                        nv_carte.id_fantome = 0
                        
                    
                    #On trouve les cartes accessibles à partir de la nouvelle carte
                    cartes_accessibles=[] #liste des entités des cartes accessibles
                    
                    if (nv_coord[0]-1)>=0: #Si on est pas sur l'extrêmité gauche du plateau
                        #On trouve l'entité de la carte à notre gauche
                        for i in self.dico_cartes.values():
                            if i.coord == [nv_coord[0]-1,nv_coord[1]]:
                                carte_access = i
                        if carte_access.orientation[1] == 0: #Si aucun mur ne barre le passage
                            cartes_accessibles.append(carte_access)
                        
                    if (nv_coord[0]+1)<self.N: #Si on est pas sur l'extrêmité droite du plateau
                        for i in self.dico_cartes.values():
                            if i.coord == [nv_coord[0]+1,nv_coord[1]]:
                                carte_access = i
                        if carte_access.orientation[3] == 0:
                            cartes_accessibles.append(carte_access)
                    
                    if (nv_coord[1]-1)>=0: #Si on est pas sur l'extrêmité haute du plateau
                        for i in self.dico_cartes.values():
                            if i.coord == [nv_coord[0],nv_coord[1]-1]:
                                carte_access = i
                        if carte_access.orientation[2] == 0:
                            cartes_accessibles.append(carte_access)
                    
                    if (nv_coord[1]+1)<self.N: #Si on est pas sur l'extrêmité basse du plateau
                        for i in self.dico_cartes.values():
                            if i.coord == [nv_coord[0],nv_coord[1]+1]:
                                carte_access = i
                        if carte_access.orientation[0] == 0:
                            cartes_accessibles.append(carte_access)
                    
            
                    retour.append(cartes_accessibles)
        
        print(retour)
                    
            
            
            
    
test=plateau(3,["Antoine","Christine","Michel"],[],7)
    
    
        
