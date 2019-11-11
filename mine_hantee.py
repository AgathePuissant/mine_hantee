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
        self.
