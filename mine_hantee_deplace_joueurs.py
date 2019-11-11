# -*- coding: utf-8 -*-
"""
Éditeur de Spyder

Ceci est un script temporaire.
"""

import numpy as np

class carte(object):
    
    def __init__(self, ID, orientation, coord, deplacable=False, id_fantome = 0):
        
        self.id = ID
        self.orientation = orientation
        self.deplacable = deplacable
        self.id_fantome = id_fantome
        self.presence_pepite = True
        self.coord = coord
        
        
class joueur(object):
    
    def __init__(self, ID, nom, niveau = 0, fantome_target, carte_position):
        self.id = ID
        self.nom = nom
        self.niveau = niveau
        self.fantome_target = fantome_target
        self.carte_position = carte_position
        self.points = 0
        self.cartes_explorees = []
        self.capture_fantome = False



def deplace_joueur(self,id_joueur,input):
    
    entite_joueur = self.dico_joueurs[id_joueur]
    entite_carte = entite_joueur.position
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
                entite_joueur.position = nv_carte #On déplace le joueur
                entite_joueur.cartes_explorees.append(nv_carte)
                
                #Si il y a une pépite sur la nouvelle carte, le joueur la ramasse
                if nv_carte.presence_pepite == True : 
                    entite_joueur.points += 1
                    nv_carte.presence_pepite = False
                    retour.append("nouvelle pépite")
                
                #Si il y a un fantôme sur la nouvelle carte, le joueur le capture si c'est possible
                #i.e. si c'est le fantôme à capturer et s'il n'a pas encore capturé de fantôme pendant ce tour
                if nv_carte.id_fantome == id_dernier_fantome+1 and entite_joueur.capture_fantome == False :
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
                    id_dernier_fantome += 1
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
                
        
        
        
    
    
    
    
        
