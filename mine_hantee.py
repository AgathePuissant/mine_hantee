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
            
            carte_sauvegardee=self.position[N-1,y] #on sauvegarde la carte qui va sortir du plateau
            
            for i in range(N):
                self.position[N-i,y]=self.position[N-i-1,y] #en partant du bas, on change la carte pour la carte d'avant jusqu'à la première carte
           
            self.position[x,y]=self.carte_a_jouer #la première carte est changée par la carte à jouer
            
            if carte_sauvegardee.id_fantome!=0 : #si il y'a un fantome sur la carte sortie
                
                self.position[0,y].id_fantome=carte_sauvegardee.id_fantome #on déplace ce fantôme à l'autre bout du plateau
                
                carte_sauvegardee.id_fantome=0 #on supprime le fantôme de la carte sortie
            
        elif x==N: #carte insérée en bas
            
            carte_sauvegardee=self.position[0,y] #on sauvegarde la carte qui va sortir du plateau
            
            for i in range(N):
                self.position[i,y]=self.position[i-1,y] #en partant du haut, on change la carte pour la carte d'après jusqu'à la dernière carte
            
            self.position[x,y]=self.carte_a_jouer #la dernière carte est changée par la carte à jouer
            
            if carte_sauvegardee.id_fantome!=0 : #si il y'a un fantome sur la carte sortie
                
                self.position[N-1,y].id_fantome=carte_sauvegardee.id_fantome #on déplace ce fantôme à l'autre bout du plateau
                
                carte_sauvegardee.id_fantome=0 #on supprime le fantôme de la carte sortie
            
        elif y==0: #carte insérée sur le côté gauche
            
            carte_sauvegardee=self.position[x,N-1] #on sauvegarde la carte qui va sortir du plateau
            
            for i in range(N):
                self.position[x,N-i]=self.position[x,N-i-1] #en partant de la droite, on change la carte pour la carte d'avant jusqu'à la première carte
            
            self.position[x,y]=self.carte_a_jouer #la première carte est changée par la carte à jouer
            
            if carte_sauvegardee.id_fantome!=0 : #si il y'a un fantome sur la carte sortie
                
                self.position[x,0].id_fantome=carte_sauvegardee.id_fantome #on déplace ce fantôme à l'autre bout du plateau
                
                carte_sauvegardee.id_fantome=0 #on supprime le fantôme de la carte sortie
            
        elif y==N: #carte insérée sur le côté droit
            
            carte_sauvegardee=self.position[x,0] #on sauvegarde la carte qui va sortir du plateau
            
            for i in range(N):
                self.position[i,y]=self.position[i-1,y] #en partant de la gauche, on change la carte pour la carte d'après jusqu'à la dernière carte
            
            self.position[x,y]=self.carte_a_jouer #la dernière carte est changée par la carte à jouer
            
            if carte_sauvegardee.id_fantome!=0 : #si il y'a un fantome sur la carte sortie
                
                self.position[x,N-1].id_fantome=carte_sauvegardee.id_fantome #on déplace ce fantôme à l'autre bout du plateau
                
                carte_sauvegardee.id_fantome=0 #on supprime le fantôme de la carte sortie
            
        self.carte_a_jouer=carte_sauvegardee #update la carte à jouer
        
        
        
