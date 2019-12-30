# -*- coding: utf-8 -*-
"""
FICHIER DEFINISSANT LES INTELLIGENCES ARTIFICIELLES
"""

import copy
import random as rd

def IA_simple(id_joueur,plateau_en_cours):
    """
    Fonction permettant pour un joueur automatique de niveau débutant de savoir 
    quel coup jouer à un moment donné du jeu.
    
    Prend en entrée :
         - id_joueur : identifiant de joueur automatique (entier)
         - plateau_en_cours : état du plateau lors du tour du joueur automatique
         (entité de classe plateau)
    
    A partir d'une copie de l'entité de plateau, génère tous les chemins possibles
    à partir de l'emplacement du joueur en utilisant la méthode chemins_possibles
    de plateau et en prenant en compte toutes les orientations de la carte extérieure
    et toutes les insertions possibles.
    
    Calcule pour chacun de ces chemins une valeur d'heuristique en prenant en compte
    le nombre de pépites sur le chemin, si le joueur capture un fantôme, si ce 
    fantôme est sur son ordre de mission ou sur l'ordre de mission d'un autre joueur.
    
    Choisit le chemin qui maximise l'heuristique (ou si plusieurs chemins la
    maximise, en choisit un au hasard parmi ceux-ci).
    
    Renvoie les coordonnées d'insertion de la carte extérieure (liste), son orientation 
    (entier correspondant au nombre de fois qu'il faut tourner la carte) et le 
    chemin optimal (liste d'entités de carte).
    """
    
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
        for i in range(len(chemins_possibles_total[k])) : #i: rang du sous-sous ensemble correspondant à l'orientation de la carte
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
    #print(max_heur)
    
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
            
    #Les instances de cartes stockées dans les chemins possibles correspondent
    #aux instances du plateau dupliqué, il faut donc retrouver les instances qui
    #correspondent au vrai plateau utilisé
    chemin_plateau = []
    #Si il n'y a qu'un seul chemin optimal, on le choisit
    if len(chemins_opti) == 1:
        #On ne prend pas la première carte du chemin, qui correspond à la carte
        #où on se trouve actuellement
        for j in range(1,len(chemins_opti[0])):
            chemin_plateau.append(plateau_en_cours.dico_cartes[chemins_opti[0][j].id])
        return (inser_opti[0],orientation_opti[0],chemin_plateau)
    
    #Sinon on prend au hasard parmi les chemins optimaux
    #On pourrait aussi faire le choix de prendre celui qui inclu la capture d'un fantôme par ex
    else:
        rang = rd.randint(0,len(chemins_opti)-1)
        for j in range(1,len(chemins_opti[rang])):
            chemin_plateau.append(plateau_en_cours.dico_cartes[chemins_opti[rang][j].id])
        return (inser_opti[rang], orientation_opti[rang],chemin_plateau)
        

#plat = plateau(3,["Antoine","Christine","Michel"],[],7)
#print(IA_simple(2,plat))
#print(plat.position)
#print(plat.dico_joueurs[0].carte_position.coord,plat.dico_joueurs[1].carte_position.coord,plat.dico_joueurs[2].carte_position.coord)

