# -*- coding: utf-8 -*-
"""
Created on Fri Nov  8 10:35:50 2019

@author: eloda
"""

#Mine hantée

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