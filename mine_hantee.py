from numpy import *

class carte(object):
    
    def __init__(self, ID, orientation, deplacable=False, id_fantome = 0):
        
        self.id = ID
        self.orientation = orientation
        self.deplacable = deplacable
        self.id_fantome = id_fantome
        self.presence_pepite = True
        
        
class joueur(object):
    
    def __init__(self, ID, nom, niveau = 0, fantome_target, position):
        self.id = ID
        self.nom = nom
        self.niveau = niveau
        self.fantome_target = fantome_target
        self.position = position
        self.points = 0  

class plateau(object):
    def __init__(self, nb_joueurs, liste_noms, liste_niveaux, N=7):
        pass
    def deplace_carte(self,orientation,coord) :
        
        N=len(self.position)
        
        x=coord[0]
        y=coord[1]
        
        #Traite tous les cas possible : carte insérée de chaque côté
        
        if x==0 : #carte insérée en haut
            
            for i in range(N):                
                self.position[N-i,y]=self.position[N-i-1,y] #en partant du bas, on change la carte pour la carte d'avant jusqu'à la première carte
           
            self.position[x,y]=self.carte_a_jouer #la première carte est changée par la carte à jouer
            
        elif x==N: #carte insérée en bas
            
            for i in range(N):
                self.position[i,y]=self.position[i-1,y] #en partant du haut, on change la carte pour la carte d'après jusqu'à la dernière carte
            
            self.position[x,y]=self.carte_a_jouer #la dernière carte est changée par la carte à jouer
            
        elif y==0: #carte insérée sur le côté gauche
            
            for i in range(N):
                self.position[x,N-i]=self.position[x,N-i-1] #en partant de la droite, on change la carte pour la carte d'avant jusqu'à la première carte
            
            self.position[x,y]=self.carte_a_jouer #la première carte est changée par la carte à jouer
            
        elif y==N: #carte insérée sur le côté droit
            
            for i in range(N):
                self.position[i,y]=self.position[i-1,y] #en partant de la gauche, on change la carte pour la carte d'après jusqu'à la dernière carte
            
            self.position[x,y]=self.carte_a_jouer #la dernière carte est changée par la carte à jouer
