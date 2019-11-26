



def simulation(plateau):
    resultats=[]
    while plateau.id_dernier_fantome!=24:
        #on parcours chaque joueur à chaque tours.
        for j in plateau.dico_joueurs:
                #premiere etape : rotation et insertion de la carte
                #1 à 4 rotations, pour couvrir toutes les actions de rotations potentielles
                nb_rotations=rd.randint(1,4)
                for ro in nb_rotations:
                        #rotation de la carte à jouer
                        plateau.carte_a_jouer.orientation[0],plateau.carte_a_jouer.orientation[1],plateau.carte_a_jouer.orientation[2],plateau.carte_a_jouer.orientation[3]=plateau.carte_a_jouer.orientation[3],plateau.carte_a_jouer.orientation[0],plateau.carte_a_jouer.orientation[1],plateau.carte_a_jouer.orientation[2]


                #ajouter la carte dans l'une des positions possibles:
                coord=rd.choice(plateau.insertions_possibles)[0]
                test_inser=plateau.deplace_carte(coord)


            #2e etape : On parcours les évènements tant que le joueur n'a pas appuyé sur entrée ou tant qu'il peut encore se déplacer
            #initialisation à la position du joueur
            joueur=plateau.dico_joueurs[j]
            carte_actuelle=joueur.carte_position
            chemins = plateau.chemins_possibles(carte_actuelle)
            chemin=chemins[rd.randint(0,len(chemins)-1)]
            #On reprend la fonction deplace_joueurs
            for carte in chemin:
                nv_carte=i

                #on déplace le joueur sur cette carte
                self.dico_joueurs[id_joueur].carte_position = nv_carte 
                self.dico_joueurs[id_joueur].cartes_explorees.append(nv_carte)
                
                #Si il y a une pépite sur la nouvelle carte, le joueur la ramasse
                if nv_carte.presence_pepite == True : 
                    self.dico_joueurs[id_joueur].points += 1
                    nv_carte.presence_pepite = False
                    retour.append("nouvelle pépite")
                
                #Si il y a un fantôme sur la nouvelle carte, le joueur le capture si c'est possible
                #i.e. si c'est le fantôme à capturer et s'il n'a pas encore capturé de fantôme pendant ce tour
                if nv_carte.id_fantome == self.id_dernier_fantome+1 and self.dico_joueurs[id_joueur].capture_fantome == False :
                    #Si le fantôme est sur l'ordre de mission, le joueur gagne 20 points
                    if nv_carte.id_fantome in self.dico_joueurs[id_joueur].fantome_target : 
                        self.dico_joueurs[id_joueur].points += 20
                        self.dico_joueurs[id_joueur].fantome_target.remove(nv_carte.id_fantome)
                        retour.append("fantome sur l'ordre de mission capturé")
                        #Si l'ordre de mission est totalement rempli, le joueur gagne 40 points
                        if self.dico_joueurs[id_joueur].fantome_target==[]:
                            self.dico_joueurs[id_joueur].points += 40
                            retour.append("ordre de mission rempli")
                    #Si le fantôme n'est pas sur l'ordre de mission, le joueur gagne 5 points
                    else:
                        self.dico_joueurs[id_joueur].points += 5
                        retour.append("fantome capturé")
                    
                    self.dico_joueurs[id_joueur].capture_fantome = True
                    self.id_dernier_fantome += 1
                    nv_carte.id_fantome = 0

            #Fin du tour du joueur : On ré-initialise cartes_explorees et capture_fantome
            joueur.cartes_explorees = [carte_actuelle]
            joueur.capture_fantome = False


