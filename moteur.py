
"""
FICHIER DE DEFINITION DES CLASSES DU MOTEUR DU JEU
"""

import numpy as np
import random as rd
import copy as copy

class carte(object):
    """
    Classe décrivant une carte du plateau.
    Comprend uniquement la méthode d'initialisation, permettant d'attribuer aux
    attributs de la classe leurs valeurs.
    """
    
    def __init__(self, ID, orientation, coord, deplacable=False, id_fantome = 0):
        """
        Prend en entrée :
            - ID : identifiant de la carte (entier)
            - orientation : description du type de carte et de son orientation, i.e.
            liste de longueur 4 dont chaque élément correspond à un côté de la carte
            et vaut 1 si un mur est présent, 0 sinon. Le premier élément correspond
            au côté du haut, le deuxième au côté à droite et ainsi de suite (liste)
            - coord : coordonnées de la carte sur le plateau, i.e. liste de 2
            entiers correspondant à la ligne et la colonne de la carte (liste)
            - deplacable : carte pouvant être déplacée (True) ou non (False) (booleen)
            - id_fantome : identifiant du fantôme présent sur la carte. Vaut 0
            si il n'y a pas de fantôme (entier)
        
        Initialise les attributs correspondant à ces éléments d'entrées ainsi que 
        l'attribut :
            - presence_pepite : présence d'une pépite sur la carte (True) ou 
            non (False). L'attribut est initialisé à True, chaque carte
            comportant une pépite en début de jeu (booleen).
        """
        
        self.id = ID
        self.orientation = orientation
        self.deplacable = deplacable
        self.id_fantome = id_fantome
        self.presence_pepite = True
        self.coord = coord
        
        
class joueur(object):
    """
    Classe décrivant un joueur du jeu.
    Comprend uniquement la méthode d'initialisation, permettant d'attribuer aux
    attributs de la classe leurs valeurs.
    """
    
    def __init__(self, ID, nom, niveau, fantome_target, carte_position, nb_joker):
        """
        Prend en entrée : 
             - ID : identifiant du joueur (entier)
             - nom : pseudo du joueur, valant automatiquement Ordinateur{num de l'id}
             si le joueur est un joueur automatique (chaîne de caractères)
             - niveau : niveau du joueur automatique, 1 pour débutant, 2 pour
             intermédiaire et 3 pour confirmé. Vaut 0 si le joueur est réel (entier)
             - fantome_target : liste des id des fantômes présents sur l'ordre
             de mission du joueur (liste)
             - carte_position : carte sur laquelle le joueur est positionné sur 
             le plateau (entité de la classe carte)
             - nb_joker : nombre de jokers utilisables par le joueur (entier)
        
        Initialise les attributs correspondant à ces éléments d'entrées ainsi que 
        les attributs :
            - points : nombre de points gagnés par le joueur (entier)
            - capture_fantome : vaut True si le joueur a déjà capturé un fantôme
            pendant un tour donné, False sinon. Cet attribut est réinitialisé 
            à False à chaque début de tour (booleen).
            - cartes_explorées : liste des cartes déjà explorées par le joueur
            pendant un tour donné. Cet attribut est réinitialisé à une liste
            d'un élément comprenant la carte sur laquelle se trouve le joueur
            à chaque début de tour (liste).    
        """
        
        self.id = ID
        self.nom = nom
        self.niveau = niveau
        self.fantome_target = fantome_target
        self.carte_position = carte_position
        self.nb_joker=nb_joker
        self.points = 0
        self.cartes_explorees = [carte_position]
        self.capture_fantome = False


class plateau(object):
    """
    Classe décrivant le plateau de jeu et permettant de le modifier.
    
    Comprend les méthodes :
        - initialisation : permet d'attribuer aux attributs de la classe leurs 
        valeurs et de créer les entités de carte et joueur nécessaires 
        pour le jeu.
        - deplace_carte : prend en entrée des coordonnées d'insertion, modifie
        les positions des cartes sur le plateau selon ces coordonnées et la 
        carte insérée, et actualise la carte hors du plateau.
        - carte_accessibles : prend en entrée une carte du plateau et renvoie
        la liste des cartes accessibles à partir de la carte d'entrée.
        - deplace_joueur : prend en entrée l'identifiant d'un joueur et un input
        directionnel et déplace le joueur sur le plateau selon l'input si c'est 
        possible
        - compte_points : prend en entrée l'identifiant d'un joueur et la nouvelle
        carte sur laquelle il se trouve, actualise les points du joueur selon
        ce qui se trouve sur la nouvelle carte, et actualise la carte.
        - chemins_possibles : prend en entrée une carte du plateau et renvoie 
        tous les chemins possibles à partir de cette carte pour une configuration
        du plateau donnée. 
    """
    
    def __init__(self, nb_joueurs, liste_noms, liste_niveaux, N, dico_parametres):
        """
        Prend en entrée : 
            - nb_joueurs : nombre de joueurs total de la partie (entier)
            - liste_noms : liste des pseudos choisis par les joueurs réels (entier)
            - liste_niveaux : liste des niveaux choisis pour les joueurs 
            automatiques (entier)
            - N : dimension du plateau (le plateau fait NXN cases). Ne peut prendre
            que les valeurs 7+n*5 avec n entier positif (entier).
            - dico_parametres : dictionnaire des paramètres choisis par l'utilisateur
            au début de la partie. Contient notamment le nombre de points qu'une 
            pépite ou qu'un fantôme (sur l'ordre de mission ou non) rapporte,
            le nombre de points que rapporte un ordre de mission complet, le 
            nombre de fantômes présents sur le plateau (dictionnaire).
        
        Initialise les attributs correspondant à ces éléments d'entrées ainsi que 
        les attributs :
            - position : matrice symbolisant le plateau et dont la valeur pour
            chaque coordonnées (ligne, colonne) correspond à l'identifiant de la 
            carte présente à ces coordonnées sur le plateau (array).
            - dico_cartes : dictionnaire des cartes de jeu dont les clés sont 
            les identifiants des cartes et les valeurs l'entité de classe carte
            correspondante (dictionnaire)
            - dico_joueurs : dictionnaire des joueurs de jeu dont les clés sont 
            les identifiants des joueurs et les valeurs l'entité de classe joueur
            correspondante (dictionnaire)
            - insertions_possibles : ensemble des coordonnées où les cartes 
            peuvent être insérées sur le plateau (liste).
        
        Crée les entités de classe carte, leur nombre dépendant de la dimension 
        du plateau. 
        On attribut aux cartes fixes leur localisation, leur type et leur orientation,
        et on place les cartes déplaçables aléatoirement sur le reste du plateau. 
        Une certaine proportion de chaque type de cartes déplaçables est créé 
        (selon les proportions données dans l'énoncé pour N=7) et leur orientation 
        est également assignée aléatoirement. 
        
        Place aléatoirement les fantômes sur le plateau. 
        
        Créé les entités de classe joueur en fonction des paramètres d'entrée.
        """
    
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
        self.etape_jeu=""
        
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
        """
        Méthode permettant de modifier les positions des cartes sur le plateau 
        lors de l'insertion d'une carte et d'actualiser la carte hors du plateau.
        
        Prend en entrée :
            - coord : coordonnées où la carte est insérée (liste).
            
        Renvoie True si la carte a pu être insérée, False sinon.
        """
        
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
        Méthode permettant de trouver les cartes accessibles à partir d'une 
        carte donnée.
        
        Prend en entrée :
            - carte : carte de laquelle on évalue les cartes accessibles (entité
            de classe carte)
            
        Renvoie la liste des entités de carte qui sont accessibles à partir de 
        la carte d'entrée.
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
        """
        Méthode qui permet de déplacer un joueur sur le plateau.
        
        Prend en entrée :
             - id_joueur : identifiant du joueur à déplacer (entier)
             - key : input directionnel informant sur le déplacement à effectuer
        
        Renvoie l'entité de la nouvelle carte sur laquelle se trouve le joueur
        si le déplacement a été effectué, l'explication de pourquoi le déplacement
        n'a pas pu être fait sous forme de string sinon (liste)
        
        """

        carte_depart=self.dico_joueurs[id_joueur].carte_position
        retour=[]
            
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
            retour.append("Ce déplacement est impossible.")
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
                    retour.append("Cette case a déjà été explorée.")
                
                else:
                    self.dico_joueurs[id_joueur].carte_position = nv_carte #On déplace le joueur
                    self.dico_joueurs[id_joueur].cartes_explorees.append(nv_carte)
                    retour = nv_carte
            else:
                retour.append("Ce déplacement est impossible.")
                

        return retour
    
    
    def compte_points(self,id_joueur,nv_carte):
        """
        Méthode qui permet d'actualiser les points d'un joueur selon la carte
        sur laquelle il se trouve et les objets présents sur cette carte.
        
        Prend en entrée :
             - id_joueur : identifiant du joueur considéré (entier)
             - nv_carte : nouvelle carte sur laquelle il se trouve (entité de
             classe carte)
             
        Renvoie une liste de chaînes de caractère décrivant quel(s) objet(s) le 
        joueur a trouvé sur la carte, s'il a trouvé quelque chose. 
        """
        
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
        Méthode récursive qui permet de trouver tous les chemins possibles à
        partir d'une carte sur le plateau (un chemin correspond à une suite de cartes).
        
        Prend en entrée :
            - carte_depart : la carte de laquelle on commence les chemins (entité
            de classe carte)
            - chemin_en_cours : chemin en train d'être construit récursivement (liste)
            
        Retourne la liste des chemins possibles à partir de la carte d'entrée,
        soit une liste de listes d'entités de carte.
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
    
    
    
    
    def partie_aleatoire(self, profondeur="fin"):
        """"
        Termine la partie du plateau ou l'avance de [profondeur] tours avec des coups aleatoires

        """
        #recuperer le tour et l'etape de jeu
        if self.etape_jeu!="":
            etape_jeu=self.etape_jeu
            nom_joueur, etape=etape_jeu.split("_")
        liste_noms=[truc.nom for truc in self.dico_joueurs.values()]
        compteur=liste_noms.index(nom_joueur)
        
        #decompte des tours
        tours=0
        #Boucle du jeu. On joue tant qu'il reste des fantômes à attraper ou jusqu'a atteindre la profondeur cible
        while self.id_dernier_fantome!=self.nbre_fantomes and tours<profondeur:
            tours+=1       
            #Tours de jeu
            #on parcours chaque joueur à chaque tours.
            while compteur<len(self.dico_joueurs):
                joueur=self.dico_joueurs[compteur]
                
                #On teste l'etape de jeu :
                if etape=="inserer-carte":                
                    #rotation de la carte : On tourne la carte 0 à 3 fois, aléatoirement
                    rotations=rd.randint(0,3)
                    for rot in range(rotations):
                        self.carte_a_jouer.orientation[0],self.carte_a_jouer.orientation[1],self.carte_a_jouer.orientation[2],self.carte_a_jouer.orientation[3]=self.carte_a_jouer.orientation[3],self.carte_a_jouer.orientation[0],self.carte_a_jouer.orientation[1],self.carte_a_jouer.orientation[2]
                            
                    #ajouter la carte
                    coord=rd.choice(self.insertions_possibles)
                    self.deplace_carte(coord)
                    etape="deplacement"                                                         
                    

                if etape=="deplacement":
                    #2e etape : Deplacement du joueur
                    #initialisation à la position du joueur
                    
                    carte_actuelle=joueur.carte_position
                    chemins=self.chemins_possibles(carte_actuelle)
                    chemin=rd.choice(chemins)
                    chemin.remove(carte_actuelle)
                    

                    for nv_carte in chemin:
                        #deplacement
                        joueur.carte_position = nv_carte 
                        joueur.cartes_explorees.append(nv_carte)
        
                        #Si il y a une pépite sur la nouvelle carte, le joueur la ramasse
                        if nv_carte.presence_pepite == True : 
                            joueur.points += 1
                            nv_carte.presence_pepite = False
            
                        #Si il y a un fantôme sur la nouvelle carte, le joueur le capture si c'est possible
                        #i.e. si c'est le fantôme à capturer et s'il n'a pas encore capturé de fantôme pendant ce tour
                        if nv_carte.id_fantome == self.id_dernier_fantome+1 and joueur.capture_fantome == False :
                            #Si le fantôme est sur l'ordre de mission, le joueur gagne 20 points
                            if nv_carte.id_fantome in joueur.fantome_target : 
                                joueur.points += 20
                                joueur.fantome_target.remove(nv_carte.id_fantome)
                                #Si l'ordre de mission est totalement rempli, le joueur gagne 40 points
                                if joueur.fantome_target==[]:
                                    joueur.points += 40
                            #Si le fantôme n'est pas sur l'ordre de mission, le joueur gagne 5 points
                            else:
                                joueur.points += 5
                
                            joueur.capture_fantome = True
                            self.id_dernier_fantome += 1
                            nv_carte.id_fantome = 0
                    etape="inserer-carte"
                            
                #Fin du tour du joueur : On ré-initialise cartes_explorees et capture_fantome
                joueur.cartes_explorees = [carte_actuelle]
                joueur.capture_fantome = False
                compteur+=1
            compteur=0
            
            
            
    def coups_possibles(self, joueur_id):
        """
        renvoie une liste des coups possibles pour un joueur, sous la forme :
            list([nb_rotations, [coordonnees], chemin])
        avec :
            - nb_rotations le nombre de rotations de la carte à inserer (entier de 0 à 3)
            - [coordonnees] un doublon donnant les coordonnees d'insertion de la carte
            - chemin une liste de cartes correspondant à un deplacement possible
        """
        #copie du plateau pour pouvoir evaluer les coups possibles apres insertion de la carte
        copie=copy.deepcopy(self)
        liste_coups=[]
        rotations=list(range(4))
        coord_insertions=copie.insertions_possibles
        #on boucle sur les rotations possibles, puis sur les coordonnees d'insertion possible
        for rota in rotations:
            liste1=[rota]
            
            for coord in coord_insertions:
                #pour chaque rotation, on re-copie le plateau pour prendre en compte l'insertion de la carte
                sub_copie=copy.deepcopy(copie)
                liste2=liste1+[coord]
                sub_copie.deplace_carte(coord)
                joueur=sub_copie.dico_joueurs[joueur_id]
                carte_actuelle=joueur.carte_position
                chemins=sub_copie.chemins_possibles(carte_actuelle)
                #finalement on recupere les deplacements possibles
                for chemin in chemins:
                    chemin.remove(carte_actuelle)
                    liste3=liste2+[chemin]
                    liste_coups.append(liste3)
        return(liste_coups)
        
    
    def joue_coup(self, coup, id_joueur):
        """
        joue un coup sous forme [orientation, coordonnées, deplacement] avec :
            - orientation entier correspondant à l'orientation de la carte à inserer
            - coordonnées les coordonnées d'insertion de la carte : list(int,int)
            - deplacement une liste d'objets cartes non séparés par un mur
        """
        #recuperer les inputs
        rotations, coord, chemin=coup
        joueur=self.dico_joueurs[id_joueur]
        
        #tourner la carte
        for rot in range(int(rotations)):
            self.carte_a_jouer.orientation[0],self.carte_a_jouer.orientation[1],self.carte_a_jouer.orientation[2],self.carte_a_jouer.orientation[3]=self.carte_a_jouer.orientation[3],self.carte_a_jouer.orientation[0],self.carte_a_jouer.orientation[1],self.carte_a_jouer.orientation[2]
        #inserer la carte
        self.deplace_carte(coord)
        
        
        #deplacer le joueur
        for nv_carte in chemin:
                joueur.carte_position = nv_carte 
                joueur.cartes_explorees.append(nv_carte)
    
                #Si il y a une pépite sur la nouvelle carte, le joueur la ramasse
                if nv_carte.presence_pepite == True : 
                    joueur.points += 1
                    nv_carte.presence_pepite = False
    
                #Si il y a un fantôme sur la nouvelle carte, le joueur le capture si c'est possible
                #i.e. si c'est le fantôme à capturer et s'il n'a pas encore capturé de fantôme pendant ce tour
                if nv_carte.id_fantome == self.id_dernier_fantome+1 and joueur.capture_fantome == False :
                    #Si le fantôme est sur l'ordre de mission, le joueur gagne 20 points
                    if nv_carte.id_fantome in joueur.fantome_target : 
                        joueur.points += 20
                        joueur.fantome_target.remove(nv_carte.id_fantome)
                        #Si l'ordre de mission est totalement rempli, le joueur gagne 40 points
                        if joueur.fantome_target==[]:
                            joueur.points += 40
                    #Si le fantôme n'est pas sur l'ordre de mission, le joueur gagne 5 points
                    else:
                        joueur.points += 5
        
                    joueur.capture_fantome = True
                    self.id_dernier_fantome += 1
                    nv_carte.id_fantome = 0