# -*- coding: utf-8 -*-
"""
Éditeur de Spyder

Ceci est un script temporaire.
"""

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
        
    def deplace_carte(self,orientation,coord) :
        
        self.carte_a_jouer.orientation=orientation
        
        N=len(self.position)
        
        x=coord[0]
        y=coord[1]
        
        #Traite tous les cas possible : carte insérée de chaque côté
        
        if x==0 : #carte insérée en haut
            
            carte_sauvegardee=self.dico_cartes[self.position[N-1,y]] #on sauvegarde la carte qui va sortir du plateau
            
            for i in range(1,N):
                
                #en partant du bas, on change la carte pour la carte d'avant jusqu'à la première carte
                self.position[N-i,y]=self.position[N-i-1,y]
            
            #la première carte est changée par la carte à jouer
            self.position[x,y]=self.carte_a_jouer.id
            
            if carte_sauvegardee.id_fantome!=0 : #si il y'a un fantome sur la carte sortie
                
                self.dico_cartes[self.position[0,y]].id_fantome=carte_sauvegardee.id_fantome #on déplace ce fantôme à l'autre bout du plateau
                
                carte_sauvegardee.id_fantome=0 #on supprime le fantôme de la carte sortie
            
        elif x==N-1: #carte insérée en bas
            
            carte_sauvegardee=self.dico_cartes[self.position[0,y]] #on sauvegarde la carte qui va sortir du plateau
            
            for i in range(1,N):
                #en partant du haut, on change la carte pour la carte d'après jusqu'à la dernière carte
                self.position[i,y]=self.position[i-1,y]
            
            #la dernière carte est changée par la carte à jouer
            self.position[x,y]=self.carte_a_jouer.id
            
            if carte_sauvegardee.id_fantome!=0 : #si il y'a un fantome sur la carte sortie
                
                self.dico_cartes[self.position[N-1,y]].id_fantome=carte_sauvegardee.id_fantome #on déplace ce fantôme à l'autre bout du plateau
                
                carte_sauvegardee.id_fantome=0 #on supprime le fantôme de la carte sortie
            
        elif y==0: #carte insérée sur le côté gauche
            
            carte_sauvegardee=self.dico_cartes[self.position[x,N-1]] #on sauvegarde la carte qui va sortir du plateau
            
            for i in range(1,N):
                #en partant de la droite, on change la carte pour la carte d'avant jusqu'à la première carte
                self.position[x,N-i]=self.position[x,N-i-1]
            
            #la première carte est changée par la carte à jouer
            self.position[x,y]=self.carte_a_jouer.id
            
            if carte_sauvegardee.id_fantome!=0 : #si il y'a un fantome sur la carte sortie
                
                self.dico_cartes[self.position[x,0]].id_fantome=carte_sauvegardee.id_fantome #on déplace ce fantôme à l'autre bout du plateau
                
                carte_sauvegardee.id_fantome=0 #on supprime le fantôme de la carte sortie
            
        elif y==N-1: #carte insérée sur le côté droit
            
            carte_sauvegardee=self.dico_cartes[self.position[x,0]] #on sauvegarde la carte qui va sortir du plateau
            
            for i in range(1,N):
                #en partant de la gauche, on change la carte pour la carte d'après jusqu'à la dernière carte
                self.position[x,i]=self.position[x,i-1]
            
            #la dernière carte est changée par la carte à jouer
            self.position[x,y]=self.carte_a_jouer.id
            
            if carte_sauvegardee.id_fantome!=0 : #si il y'a un fantome sur la carte sortie
                
                self.dico_cartes[self.position[x,N-1]].id_fantome=carte_sauvegardee.id_fantome #on déplace ce fantôme à l'autre bout du plateau
                
                carte_sauvegardee.id_fantome=0 #on supprime le fantôme de la carte sortie
            
        self.carte_a_jouer=carte_sauvegardee #update la carte à jouer
        
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
    
    
def affiche_plateau(plateau):
    N=plateau.N
    array_image=[]
    for i in range(N):
        for j in range(N):
            array_image.append(plateau.dico_cartes[plateau.position[i,j]].orientation)
    array_image=np.array(array_image).reshape(N,N,4)
    
    
    grid=np.zeros((50*N,50*N,3), 'uint8')
    for ligne in range(len(array_image)):
        for colonne in range(len(array_image)):
            
            subgrid=np.zeros((50,50,3), 'uint8')
            subgrid[..., 0] = np.array([0 for i in range(50*50)]).reshape(50,50)
            subgrid[..., 1] = np.array([150 for i in range(50*50)]).reshape(50,50)
            subgrid[..., 2] = np.array([0 for i in range(50*50)]).reshape(50,50)
            orientation=array_image[ligne,colonne]
            
            for mur in range(4):
                if orientation[mur]==1 and mur==0:
                    subgrid[:5,:,1]=np.array([256 for i in range(5*50)]).reshape(5,50)
                elif orientation[mur]==1 and mur==1:
                    subgrid[:,45:,1]=np.array([256 for i in range(5*50)]).reshape(50,5)
                elif orientation[mur]==1 and mur==2:
                    subgrid[45:,:,1]=np.array([256 for i in range(5*50)]).reshape(5,50)
                elif orientation[mur]==1 and mur==3:
                    subgrid[:,:5,1]=np.array([256 for i in range(5*50)]).reshape(50,5)
                    
            grid[50*ligne:50*(ligne+1),50*colonne:50*(colonne+1),]=subgrid
    
    img = Image.fromarray(grid)
    plt.imshow(img)
    
test=plateau(3,["Antoine","Christine","Michel"],[],7)
affiche_plateau(test)
