# -*- coding: utf-8 -*-
"""
FICHIER DEFINISSANT LES INTELLIGENCES ARTIFICIELLES
"""
import time as time
import copy as copy
import random as rd

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
        #On cherche les 5 valeurs d'heuristiques maximales si il y a au moins 5 valeurs
        #différentes
        max_heur = []
        j=0
        while j<len(heur_triees) and len(max_heur)<5:
            if heur_triees[len(heur_triees)-j-1] not in max_heur :
                max_heur.append(heur_triees[len(heur_triees)-j-1])
            j += 1
    
        
        #On trouve le/les chemin(s) correspondant aux 5 heuristiques maximales
        for triplet in dico_heuristique.keys():
            if dico_heuristique[triplet] in max_heur :
                chemins_opti.append(chemins_possibles_total[triplet[0]][triplet[1]][triplet[2]])
                #On trouve les coordonnées de l'insertion correspondant au chemin optimal trouvé
                inser_opti.append(plateau.insertions_possibles[triplet[0]])
                orientation_opti.append(triplet[1])
                
            
        #Retourner un coup parmi les 5 ayant les meilleures heuristiques
        if output_type=="alea":
            #Les instances de cartes stockées dans les chemins possibles correspondent
            #aux instances du plateau dupliqué, il faut donc retrouver les instances qui
            #correspondent au vrai plateau utilisé
            chemin_plateau = []
        
            rang = rd.randint(0,len(chemins_opti)-1)
            for j in range(1,len(chemins_opti[rang])):
                chemin_plateau.append(plateau_en_cours.dico_cartes[chemins_opti[rang][j].id])
                
            out=[inser_opti[rang], orientation_opti[rang],chemin_plateau]
    
    
        #Ou retourner une liste contenant les coups des 5 meilleures heuristiques
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