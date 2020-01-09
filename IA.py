# -*- coding: utf-8 -*-
"""
FICHIER DEFINISSANT LES INTELLIGENCES ARTIFICIELLES
"""
import time as time
import copy as copy
import random as rd
import numpy as np
import pygame

def IA_monte_carlo(plateau_en_cours,joueur_id, reps, liste_coups=[], profondeur="fin"):
    """
    evalue les coups possibles d'un joueur et renvoie le meilleur coup à une profondeur de donnée,
    à partir d'une frequence de victoire calculée sur un nombre de repetitions reps.
    Les coups testés peuvent ou bien être tous les coups possibles, ou bien 
    """
    #recuperer la liste des coups possibles
    if liste_coups==[]:
        liste_coups=plateau_en_cours.coups_possibles(joueur_id)
    liste_coups_copy=copy.deepcopy(liste_coups)
    liste_scores=[]
    progression=0
    start=time.time()
    #pour chaque coup, on le joue et on fait [reps] parties aleatoires
    for coup in liste_coups_copy:
        score=0
        progression+=1
        print("progression :"+str(progression/len(liste_coups_copy)*100)+"%")
        for essai in range(reps):
            pygame.event.pump()
            copie=0
            copie=copy.deepcopy(plateau_en_cours)
            copie.joue_coup(coup, joueur_id)
            copie.partie_aleatoire(profondeur)
            score+=copie.dico_joueurs[joueur_id].points
        score=score/reps
        liste_scores.append(score)
    #Recuperer le coup correspondant à la meilleure heuristique
    index_max=liste_scores.index(max(liste_scores))
    coup_optimal=liste_coups[index_max]
    end=time.time()
    print("temps de calcul : "+ str(end-start))
    return(coup_optimal)



def IA_simple(id_joueur,plateau_en_cours, output_type="single"):
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
    
    Calcule pour chacun de ces chemins une valeur d'heuristique prenant en compte
    le nombre de pépites sur le chemin, si le joueur capture un fantôme, si ce 
    fantôme est sur son ordre de mission ou sur l'ordre de mission d'un autre joueur.
    
    En fonction du type de output_type, la fonction renvoie :
        - si output_type = single (par défaut), la fonction renvoie le coup correspondant
        à la meilleure heuristique, ou bien à une heuristique au hasard parmi les meilleures
        en cas d'égalité, sous la forme :
        [coordonnees, orientation, deplacement]
        - si output_type = alea, la fonction renvoie un coup au hasard parmi les 5 meilleurs,
        sous la même forme que pour single
        - si output_type = liste, la fonction renvoie une liste des 5 meilleurs coups, sous la forme :
            liste ([orientation, coordonnées, deplacement])
    
    Où coordonneés = coordonnées d'insertion de la carte extérieure (liste), 
    orientation = entier correspondant au nombre de fois qu'il faut tourner la carte et
    deplacement = liste d'entités de carte.
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
                #On examine chaque carte
                for carte in chemins_possibles_total[k][i][m]:
                    #Si il y a une pépite sur la carte
                    if carte.presence_pepite == True : 
                        heuristique +=1
                    #Si il y a un de nos fantomes target attrapable
                    if carte.id_fantome == plateau.id_dernier_fantome+1 and carte.id_fantome in plateau.dico_joueurs[id_joueur].fantome_target:
                        heuristique += 20
                    #Si il y a un des fantomes target d'un adversaire attrapable
                    elif carte.id_fantome == plateau.id_dernier_fantome+1 and carte.id_fantome in target_adversaires:
                        heuristique += 10
                    #Si il y a un fantome attrapable qui n'est le target de personne
                    elif carte.id_fantome == plateau.id_dernier_fantome+1:
                        heuristique += 5
                        
                dico_heuristique[(k,i,m)] = heuristique
    
    chemins_opti = []
    inser_opti = []
    orientation_opti = []

    if output_type == "single":
        
        max_heur = max(dico_heuristique.values())
        
        for triplet in dico_heuristique.keys():
            if dico_heuristique[triplet] == max_heur :
                chemins_opti.append(chemins_possibles_total[triplet[0]][triplet[1]][triplet[2]])
                #On trouve les coordonnées de l'insertion correspondant au chemin optimal trouvé
                inser_opti.append(plateau.insertions_possibles[triplet[0]])
                orientation_opti.append(triplet[1])
        
        

        chemin_plateau = []
        #Si il n'y a qu'un seul chemin optimal, on le choisit
        if len(chemins_opti) == 1:
            #On ne prend pas la première carte du chemin, qui correspond à la carte
            #où on se trouve actuellement
            for j in range(1,len(chemins_opti[0])):
                chemin_plateau.append(plateau_en_cours.dico_cartes[chemins_opti[0][j].id])
            out = [inser_opti[0],orientation_opti[0],chemin_plateau]
        
        #Sinon on prend au hasard parmi les coups d'heuristique maximale
        #On pourrait aussi faire le choix de prendre celui qui inclu la capture d'un fantôme par ex
        else:
            rang = rd.randint(0,len(chemins_opti)-1)
            for j in range(1,len(chemins_opti[rang])):
                chemin_plateau.append(plateau_en_cours.dico_cartes[chemins_opti[rang][j].id])
            out = [inser_opti[rang], orientation_opti[rang],chemin_plateau]
            
    else :
        
        #On créé une liste des heuristiques triée
        heur_triees = [v for k, v in sorted(dico_heuristique.items(), key=lambda item: item[1])]
        
        
        #On cherche les 2 valeurs d'heuristiques maximales si il y a au moins 2 valeurs
        #différentes
        max_heur = []
        j=0
        while j<len(heur_triees) and len(max_heur)<3:
            if heur_triees[len(heur_triees)-j-1] not in max_heur :
                max_heur.append(heur_triees[len(heur_triees)-j-1])
            j += 1
        
        
        #On trouve le/les chemin(s) correspondant aux 2 heuristiques maximales
        for triplet in dico_heuristique.keys():
            if dico_heuristique[triplet] in max_heur :
                chemins_opti.append(chemins_possibles_total[triplet[0]][triplet[1]][triplet[2]])
                #On trouve les coordonnées de l'insertion correspondant au chemin optimal trouvé
                inser_opti.append(plateau.insertions_possibles[triplet[0]])
                orientation_opti.append(triplet[1])
                
            
        #Retourner un coup parmi les 2 ayant les meilleures heuristiques
        if output_type=="alea":
            #Les instances de cartes stockées dans les chemins possibles correspondent
            #aux instances du plateau dupliqué, il faut donc retrouver les instances qui
            #correspondent au vrai plateau utilisé
            chemin_plateau = []
        
            rang = rd.randint(0,len(chemins_opti)-1)
            for j in range(1,len(chemins_opti[rang])):
                chemin_plateau.append(plateau_en_cours.dico_cartes[chemins_opti[rang][j].id])
                
            out=[inser_opti[rang], orientation_opti[rang],chemin_plateau]
    
    
        #Ou retourne une liste contenant les coups de meilleures heuristiques
        elif output_type=="liste" :
            #On recupere une liste de triplets inser_opti, orientation_opti, chemin_plateau
            meilleurs_chemins=[]
            
            for rang in range(len(chemins_opti)):
                chemin_plateau=[]
                for j in range(1,len(chemins_opti[rang])):
                    chemin_plateau.append(plateau_en_cours.dico_cartes[chemins_opti[rang][j].id])
                meilleurs_chemins.append([orientation_opti[rang],inser_opti[rang],chemin_plateau])
            out=meilleurs_chemins
            #reduire le nombre de coups testes
            if len(out)>10:
                out=rd.sample(out, 10)
        

    #Ou bien retourner le coup correspondant à la meilleure heuristique
    return(out)
    
# = plateau(3,['Elodie', 'Joueur2', 'Ordinateur3', 'zodj'],[0, 0, 1],7,{'dimensions_plateau': '7', 'nb_fantomes': '21', 'nb_joueurs': '3', 'mode_joueur_1': 'manuel', 'mode_joueur_2': 'manuel', 'mode_joueur_3': 'automatique', 'mode_joueur_4': 'manuel', 'niveau_ia_1': '3', 'niveau_ia_2': '1', 'niveau_ia_3': '1', 'niveau_ia_4': '1', 'pseudo_joueur_1': 'Elodie', 'pseudo_joueur_2': 'Joueur2', 'pseudo_joueur_3': 'Ordinateur3', 'pseudo_joueur_4': 'zodj', 'nb_fantomes_mission': '3', 'nb_joker': '1', 'points_pepite': '1', 'points_fantome': '5', 'points_fantome_mission': '20', 'bonus_mission': '40'})
#print(IA_simple(2,plat,"liste"))

###IA MINMAX
def joueur_tour(plateau_en_cours,joueur_id):
    '''
    Fonction permettant de déterminer l'id du prochain joueur à joueur. Utilisee pour l'algorithme
    minmax
    Entrees :
         - joueur_id : identifiant de joueur automatique (entier)
         - plateau_en_cours : état du plateau lors du tour du joueur automatique
         (entité de classe plateau)
    Sortie :
        identifiant du joueur suivant 
    '''
    
    #recuperer le tour et l'etape de jeu
    if plateau_en_cours.etape_jeu!="":
        nom_joueur=plateau_en_cours.etape_jeu.split('_')[0]
    liste_noms=[truc.nom for truc in plateau_en_cours.dico_joueurs.values()]
    compteur=liste_noms.index(nom_joueur)
    
    #Si l'indice du joueur n'est pas le dernier de la liste
    if int(compteur)+1 <= len(liste_noms)-1:
        joueur_suivant=plateau_en_cours.dico_joueurs[int(compteur)+1]
        joueur_suivant_id = joueur_suivant.id
        
    #Si le joueur est le dernier, on retourne au début
    else :
        joueur_suivant = plateau_en_cours.dico_joueurs[0]
        joueur_suivant_id = joueur_suivant.id
    return(joueur_suivant_id)
    
#        
#def jouer_minmax(plateau_en_cours,joueur_id,profondeur):
#    '''
#    Fonction generale de l'algorithme minmax. Elle permet de déterminer le coup optimal
#    à jouer.
#    On simule un certains nombres de tours de jeu. On suppose que quand ce n'est pas à
#    joueur_id de jouer, les joueurs "ennemis" choisissent le coup qui va minimiser le 
#    gain de joueur_id. (C'est un postulat fort)
#    Joueur_id lui choisit le maximum
#    Entrees :
#         - joueur_id : identifiant de joueur automatique (entier)
#         - plateau_en_cours : état du plateau lors du tour du joueur automatique
#         (entité de classe plateau)
#         - profondeur : nombre de tour de jeu effectués par l'algorithme. 
#         Ici un tour de jeu correspond à un joueur qui joue, pas tous les joueurs
#    Sortie :
#        coup optimal à jouer pour l'IA pour maximiser son score
#    '''
#    max_score = -10000                
#    start=time.time()
#    progression = 0
#    #recuperer la liste des coups possibles
#    liste_coups=plateau_en_cours.coups_possibles(joueur_id)
#    #print(len(liste_coups))
#    liste_coups_copy=copy.deepcopy(liste_coups)
#    joueur_initial = joueur_id
#    #print(joueur_initial)
#
#    for coup in liste_coups_copy:
#        progression+=1
#        print("progression :"+str(progression/len(liste_coups_copy)*100)+"%")
#        #print("WESH",coup)
#        copie=0
#        copie=copy.deepcopy(plateau_en_cours)
#        copie.joue_coup(coup,joueur_id)
#        #print(copie.etape_jeu)
#        #score =copie.dico_joueurs[joueur_id].points
#        joueur_suivant = joueur_tour(copie,joueur_id)
#        #print("joeur suivant1",joueur_suivant)
#        score = Min_IA(copie,joueur_suivant, profondeur - 1,joueur_initial)
#        #print(score)
#        if score > max_score :
#            max_score = score 
#            index_coup_optimal = liste_coups_copy.index(coup)
#    end=time.time()
#    print("temps de calcul : "+ str(end-start))
#    coup_optimal = liste_coups[index_coup_optimal]
#    print(coup_optimal)
#    return coup_optimal

#    
#def Min_IA(plateau_en_cours,joueur_id, profondeur, joueur_initial):
#     '''
#    Fonction min de minmax. Elle permet de determiner le score minimum et se relance
#    recursivement si le prochain joueur n'est pas le joueur initial ou lance maximum si
#    c'est le joueur initial
#    Entrees :
#         - joueur_id : identifiant de joueur dont c'est le tour (entier)
#         - plateau_en_cours : état du plateau lors du tour du joueur 
#         (entité de classe plateau)
#         - profondeur : nombre de tour de jeu effectués par l'algorithme. 
#         Ici un tour de jeu correspond à un joueur qui joue, pas tous les joueurs
#         -joueur_initial :identifiant de joueur automatique (entier)
#    Sortie :
#        - score du joueur automatique
#    '''
#    
#    min_score = 10000
#    #Si on est arrivé à la profondeur seuil, on remonte les points du joueur automatique
#    if profondeur == 0:
#        return plateau_en_cours.dico_joueurs[joueur_initial].points
#
#    #Sinon
#    else :
#        liste_coups=plateau_en_cours.coups_possibles(joueur_id)
#        liste_coups_copy=copy.deepcopy(liste_coups)
#
#        for coup in liste_coups_copy:
#            copie=0
#            copie=copy.deepcopy(plateau_en_cours)
#            copie.joue_coup(coup, joueur_id)
#            joueur_suivant = joueur_tour(copie,joueur_id)
#
#            #Si le joueur est le joueur automatique on cherche à obtenir le maximum
#            if int(joueur_suivant) == int(joueur_initial) :
#                score = Max_IA(copie,joueur_suivant, profondeur - 1,joueur_initial)
#                if score < min_score :
#                    min_score = score
#            else : 
#                score = Min_IA(copie,joueur_suivant, profondeur - 1,joueur_initial)            
#                
#    return min_score
#
#def Max_IA(plateau_en_cours,joueur_id, profondeur, joueur_initial):
#    '''
#    Fonction max de minmax. Elle permet de determiner le score maximum du joueur automatique
#    et se relance
#    recursivement si le prochain joueur n'est pas le joueur initial ou lance maximum si
#    c'est le joueur initial
#    Entrees :
#         - joueur_id : identifiant de joueur dont c'est le tour (entier)
#         - plateau_en_cours : état du plateau lors du tour du joueur 
#         (entité de classe plateau)
#         - profondeur : nombre de tour de jeu effectués par l'algorithme. 
#         Ici un tour de jeu correspond à un joueur qui joue, pas tous les joueurs
#         -joueur_initial :identifiant de joueur automatique (entier)
#    Sortie :
#        - score du joueur automatique
#    '''
#    
#    max_score = -10000
#    
#    #Si on est arrivé à la profondeur seuil, on remonte les points du joueur automatique
#
#    if profondeur == 0:
#        return plateau_en_cours.dico_joueurs[joueur_initial].points
#    #Sinon
#    else :
#        liste_coups=plateau_en_cours.coups_possibles(joueur_id)
#        liste_coups_copy=copy.deepcopy(liste_coups)
#
#        for coup in liste_coups_copy:
#            copie=0
#            copie=copy.deepcopy(plateau_en_cours)
#            copie.joue_coup(coup,joueur_id)
#            joueur_suivant = joueur_tour(copie,joueur_id)
#            
#            #au tour suivant on lance min car le joueur qui joue n'est plus le joueur initial
#            score = Min_IA(copie,joueur_suivant, profondeur - 1,joueur_initial)
#            if score > max_score :
#                max_score = score
#            
#    return max_score
