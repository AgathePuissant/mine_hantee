# -*- coding: utf-8 -*-
"""
Created on Wed Nov 13 14:35:26 2019
@author: agaca
"""

import pygame
from pygame.locals import *
import numpy as np
import random as rd
import pickle
import glob
import copy
import math
from moviepy.editor import *

from moteur import *
from objets_graphiques import *
from parametrisation import *
from IA import *
    
#---------------------------------------Défintion des instructions graphiques------------------------------
    
def menu():
    global fenetre,liste_sauv,num_partie,nouvelle,dico_stop
    
    
    #en cours de modification
    if 'dico_stop' not in globals() :
        dico_stop={"intro" : True}
    elif any(value == True for value in dico_stop.values()):
        dico_stop["intro"]=True
    else :
        dico_stop = dict.fromkeys(dico_stop, False)

    nouvelle_partie_button=Bouton(500,350,200,50,"Nouvelle partie")
    charger_partie_button=Bouton(500,450,200,50,"Charger une partie")
    
    nouvelle=False
    

    while dico_stop["intro"]==True: #Boucle infinie
                
        pygame.display.flip() #Update l'écran
        fenetre.blit(fond_menu,(0,0))  #On colle le fond du menu
        
        liste_sauv=glob.glob("sauvegarde*")
        liste_sauv=[int(liste_sauv[i][-1]) for i in range(len(liste_sauv))]
        nouvelle_partie_button.draw(fenetre)
        charger_partie_button.draw(fenetre)
        
        for event in pygame.event.get(): #Instructions de sortie
            
            nouvelle_partie_button.handle_event(event,nouvelle_partie)
            charger_partie_button.handle_event(event,charger_partie)
            
            if event.type == pygame.QUIT:
                dico_stop = dict.fromkeys(dico_stop, False)
                pygame.display.quit()
                pygame.quit()
                
                
        
                
        
    
        

def game() :
    global fenetre,num_partie,nouvelle,plateau_test,dico_stop
    #Initialisation d'une nouvelle partie ou chargement d'une ancienne partie
    if nouvelle==False :
        plateau_test=pickle.load(open("sauvegarde "+str(num_partie),"rb"))
        dico_stop["charger"]=False
    elif nouvelle==True :
        #Création d'un nouveau plateau
        #Lecture du fichier de paramétrage et initialisation des paramètres
        dico_parametres=lecture(fichier)
        nb_joueurs=int(dico_parametres['nb_joueurs'])
        dimensions_plateau=int(dico_parametres['dimensions_plateau'])
        liste_noms=[dico_parametres['pseudo_joueur_1'],dico_parametres['pseudo_joueur_2'],dico_parametres['pseudo_joueur_3'],dico_parametres['pseudo_joueur_4']]
        
        #liste des niveaux
        liste_niveaux=[]
        for joueur in range(1,nb_joueurs+1):
            mode='mode_joueur_'+str(joueur)
            #si c'est un joueur normal, alors le niveau est de 0. 
            if dico_parametres[mode]=='manuel':
                liste_niveaux=liste_niveaux+[0]
            #sinon on prend le niveau rentré par l'utilisateur
            else:
                niveau='niveau_ia_'+str(joueur)
                liste_niveaux=liste_niveaux+[int(dico_parametres[niveau])]
                
        plateau_test=plateau(nb_joueurs,liste_noms,liste_niveaux,dimensions_plateau,dico_parametres)
        
    else :
        pass
    
    afficher_commandes(debut=True)
    
    afficher_commandes_button=Bouton(725,5,150,40,"Commandes")

    N = plateau_test.N
    
    
    dico_stop["rester_jeu"]=True
    #in charge l'animation en cas de capture de fantome
    clip = VideoFileClip('animation.mp4')
    
    
    #Boucle du jeu. On joue tant qu'il reste des fantômes à attraper
    while plateau_test.id_dernier_fantome!=plateau_test.nbre_fantomes and dico_stop["rester_jeu"]==True:

        #Tours de jeu
        #on parcours chaque joueur à chaque tours.
        for j in plateau_test.dico_joueurs :
            
            information="" #Initialisation du texte d'erreur
            etape=""
            
            joueur=plateau_test.dico_joueurs[j]

            actualise_fenetre(plateau_test,fenetre,joueur,information,afficher_commandes_button,etape)

            if joueur.niveau == 0 :
                #premiere etape : rotation et insertion de la carte
                #On parcours la liste de tous les événements reçus tant qu'une carte n'a pas été insérée
                dico_stop["test_carte"]=True
                dico_stop["test_entree"]=True
                
                
                while dico_stop["test_carte"]!=False:
                    
                    etape="Tourner la carte avec R, cliquer pour insérer"
                    
                    for event in pygame.event.get():   
                        
                        afficher_commandes_button.handle_event(event,afficher_commandes)
                        
                        #Si on appuie sur R, rotation de la carte à jouer
                        if event.type == KEYDOWN and event.key == K_r: 
                            plateau_test.carte_a_jouer.orientation[0],plateau_test.carte_a_jouer.orientation[1],plateau_test.carte_a_jouer.orientation[2],plateau_test.carte_a_jouer.orientation[3]=plateau_test.carte_a_jouer.orientation[3],plateau_test.carte_a_jouer.orientation[0],plateau_test.carte_a_jouer.orientation[1],plateau_test.carte_a_jouer.orientation[2]
                        
                        #ajouter la carte lorsque l'utilisateur clique dans le plateau
                        
                        elif event.type == MOUSEBUTTONDOWN : 
                            #clic gauche : insertion de la carte à jouer
                            if event.button==1: 
    
                                coord=[int(math.floor(event.pos[1]/700*plateau_test.N)),int(math.floor(event.pos[0]/700*plateau_test.N))]
                                
                                test_inser=plateau_test.deplace_carte(coord)
                               
                                if test_inser==False :
                                    information=["Insertion impossible"]
                                #Sinon, on finit cette section du tour
    
                                else :
                                    information=""
                                   
                                    dico_stop["test_carte"]=False
                                    
    
                        elif event.type == KEYDOWN and event.key == K_SPACE :
                            pause()
                        
                        elif event.type == QUIT:
                            dico_stop = dict.fromkeys(dico_stop, False)
                            
                    actualise_fenetre(plateau_test,fenetre,joueur,information,afficher_commandes_button,etape)
                   
                                        
                                        
                #2e etape : On parcours les évènements tant que le joueur n'a pas appuyé sur entrée ou tant qu'il peut encore se déplacer
                #initialisation à la position du joueur
                
                carte_actuelle=joueur.carte_position
                
                cartes_accessibles=plateau_test.cartes_accessibles1(carte_actuelle)
                
                information=""
                
                #parcours des evenements
                while dico_stop["test_entree"]==True and len(cartes_accessibles)>0:#La 2e condition deconne a cause de cartes_accessibles
                    
                    etape="Déplacer avec les flèches, entrée pour finir"
                    
                    for event in pygame.event.get():
                        
                        afficher_commandes_button.handle_event(event,afficher_commandes)
                        
                        #deplacement
                        if event.type == KEYDOWN and (event.key == K_UP or event.key == K_LEFT or event.key == K_DOWN or event.key == K_RIGHT) : #touches directionnelles : déplacement du joueur
                            deplace = plateau_test.deplace_joueur(j,event.key)
                            if isinstance(deplace, carte) == True: #Si le déplacement était possible, on affiche ce que le joueur a potentiellement gagné
                                information=plateau_test.compte_points(j,deplace)
                                #si le joueur capture un fantome, on lance l'animation de capture
                                if joueur.capture_fantome == True :
                                    clip.preview()
                            else: #Sinon on affiche la raison pour laquelle le déplacement n'était pas possible
                                information=deplace
                            carte_actuelle=joueur.carte_position
                            cartes_accessibles=plateau_test.cartes_accessibles1(carte_actuelle)
                            
                            
                        #fin de tour
                        if event.type == KEYDOWN and (event.key== K_RETURN):
                            dico_stop["test_entree"]=False
                            information=""
                        
                            
                            
                        elif event.type == KEYDOWN and event.key == K_SPACE :
                            pause()
                            
                        elif event.type == QUIT:
                            dico_stop = dict.fromkeys(dico_stop, False)
                            
                    #Update l'écran                                                                
                    actualise_fenetre(plateau_test,fenetre,joueur,information,afficher_commandes_button,etape)
    
                        
                #Fin du tour du joueur : On ré-initialise cartes_explorees et capture_fantome
                joueur.cartes_explorees = [carte_actuelle]
                joueur.capture_fantome = False
                
                if dico_stop["test_carte"]==False and dico_stop["test_entree"]==False and dico_stop["rester_jeu"]==False:
                    break
            
            else:
                if joueur.niveau == 1:
                    IA = IA_debutant(j,plateau_test)
                elif joueur.niveau == 2:
                    IA = IA_simple(j,plateau_test)
                coord_inser, orientation, chemin = IA[0],IA[1],IA[2]

                #On tourne la carte
                for i in range(orientation):
                    plateau_test.carte_a_jouer.orientation[0],plateau_test.carte_a_jouer.orientation[1],plateau_test.carte_a_jouer.orientation[2],plateau_test.carte_a_jouer.orientation[3]=plateau_test.carte_a_jouer.orientation[3],plateau_test.carte_a_jouer.orientation[0],plateau_test.carte_a_jouer.orientation[1],plateau_test.carte_a_jouer.orientation[2]
                    pygame.time.wait(200)
                    actualise_fenetre(plateau_test,fenetre,joueur,information,afficher_commandes_button,etape)
                 
                plateau_test.deplace_carte(coord_inser) #On l'insère
                pygame.time.wait(200)
                actualise_fenetre(plateau_test,fenetre,joueur,information,afficher_commandes_button,etape)
                

                information=""
                for i in chemin :
                    joueur.carte_position = i
                    information=plateau_test.compte_points(j,i)

                    pygame.time.wait(200)
                    actualise_fenetre(plateau_test,fenetre,joueur,information,afficher_commandes_button,etape)
                

            

def afficher_commandes(debut=False) :
    global dico_stop

    dico_stop["comm"]=True
    
    while dico_stop["comm"]==True :
    
        fenetre.blit(fond_uni,(0,0))
        
        fenetre.blit(police3.render("Commandes",True,pygame.Color("#000000")),(100,100))
        
        fenetre.blit(police2.render("R : tourner la carte.",False,pygame.Color("#000000")),(100,200))
        fenetre.blit(police2.render("Clic sur une carte déplaçable en périphérie du plateau : insérer la carte extérieure.",False,pygame.Color("#000000")),(100,250))
        fenetre.blit(police2.render("Flèches directionnelles : déplacer le joueur.",False,pygame.Color("#000000")),(100,300))
        fenetre.blit(police2.render("Entrée : finir le tour.",False,pygame.Color("#000000")),(100,350))
        fenetre.blit(police2.render("Espace : mettre en pause/Retour au jeu.",False,pygame.Color("#000000")),(100,400))
        
        if debut==False:                                                                                         
            fenetre.blit(police2.render("Appuyez sur espace pour revenir au jeu.",False,pygame.Color("#000000")),(100,500))
        else:
            fenetre.blit(police2.render("Appuyez sur espace pour commencer le jeu.",False,pygame.Color("#000000")),(100,500))                                                                                             
        
        pygame.display.flip() 
                                                        
        for event in pygame.event.get() :
            
            if event.type == KEYDOWN and event.key == K_SPACE :
                dico_stop["comm"]=False
                
            if event.type == pygame.QUIT :
                dico_stop = dict.fromkeys(dico_stop, False)
            
def pause() :
    global fenetre,texte_sauv,nouvelle,dico_stop
    
    nouvelle="jeu en pause"
    
    dico_stop["pause"]=True
    
    texte_sauv=""
    
    sauvegarder_button=Bouton(550,350,200,50,"Sauvegarder")
    retour_menu_button=Bouton(550,450,200,50,"Retour au menu")
    
    while dico_stop["pause"]==True :
                
        fenetre.blit(fond_uni,(0,0))
    
        fenetre.blit(police.render("Pause",True,pygame.Color("#000000")),(600,200))
                                                             
        sauvegarder_button.draw(fenetre)
        retour_menu_button.draw(fenetre)
                                  
        fenetre.blit(police.render(texte_sauv,True,pygame.Color("#000000")),(550,550))
                                                                
        pygame.display.flip() #Update l'écran
        
        for event in pygame.event.get():   #On parcours la liste de tous les événements reçus
            
            sauvegarder_button.handle_event(event,sauvegarder)
            retour_menu_button.handle_event(event,menu)
                
            if event.type == KEYDOWN and event.key == K_SPACE :
                dico_stop["pause"]=False
                
            if event.type == QUIT:     #Si un de ces événements est de type QUIT
                dico_stop = dict.fromkeys(dico_stop, False)
                

                
def sauvegarder():
    global texte_sauv,num_partie,plateau_test
    
    pickle.dump(plateau_test,open("sauvegarde "+str(num_partie),"wb"))
    texte_sauv="Partie sauvegardée"

    
def charger_partie():
    global fenetre,liste_sauv,num_partie,retour_partie,dico_stop
    
    dico_stop["charger"]=True
    retour_partie=False
    lancer_partie_button=Bouton(800,300,200,50,"Lancer la partie")
    retour_menu_button=Bouton(500,300,200,50,"Retour au menu")
        
    while dico_stop["charger"] ==True:
                
                
        if liste_sauv!=[] :
            
            fenetre.blit(fond_uni,(0,0))  #On colle le fond du menu
            
            for i in range(len(liste_sauv)) :
                button_charger_partie(fenetre,"Partie "+str(liste_sauv[i]),500,100+i*100,200,50,pygame.Color("#b46503"),pygame.Color("#d09954"),liste_sauv[i])
            
            if retour_partie==True :
                fenetre.blit(police.render("Partie "+str(num_partie)+" sélectionnée",True,pygame.Color("#000000")),(800,100))
                lancer_partie_button.draw(fenetre)                                                    
        else :
            
            fenetre.blit(fond_uni,(0,0))  #On colle le fond du menu
            fenetre.blit(police.render("Aucune partie sauvegardee",True,pygame.Color("#000000")),(450,100))
            retour_menu_button.draw(fenetre)
            
        pygame.display.flip() #Update l'écran
        
        for event in pygame.event.get():   #On parcours la liste de tous les événements reçus
            
            if retour_partie==True :
                lancer_partie_button.handle_event(event,game)
            else :
                retour_menu_button.handle_event(event,menu)
            
            if event.type == QUIT:     #Si un de ces événements est de type QUIT
                dico_stop = dict.fromkeys(dico_stop, False)
                

                
def nouvelle_partie():
    '''
    Fonction de paramétrisation simple 1
    demande le nombre de joueurs pour la partie (entre 2,3 et 4) 
    '''
    global fenetre,liste_sauv,num_partie,nouvelle,dico_stop
    
    nouvelle=True
    #attribution du numéro de la partie
    if liste_sauv!=[]:
        num_partie=np.max(liste_sauv)+1
    else :
        num_partie=1
    
    dico_stop["intro"]=False
    dico_stop["nouvellepartie"]=True
    
    #initialisation des boutons valider et retour
    valider=Bouton(500,450,200,50,"Valider")
    retour=Bouton(500,550,200,50,"Retour")
    
    #initialisation des boxs pour le choix du nombre de joueurs
    choix_nb_joueur_2=ChoiceBox(475, 300, 50, 30, '2')
    choix_nb_joueur_3=ChoiceBox(575, 300, 50, 30, '3')
    choix_nb_joueur_4=ChoiceBox(675, 300, 50, 30, '4')
    choix_nb_joueurs=[choix_nb_joueur_2, choix_nb_joueur_3, choix_nb_joueur_4]
    
    #lecture du fichier de paramétrisation
    dico_parametres=lecture(fichier)
    #on stoque le choix entre les boutons dans le dictionnaire choix_final
    choix_final={}
    choix_final["fonction"]=parametrisation_1
    choix_final["nb_joueurs"]=dico_parametres['nb_joueurs'] 
    choix_final['test_null']=False
    choix_final['test_max']=False          
    #initialisation du nombre de joueurs à la valeur renseignée dans le fichier
    for choix in choix_nb_joueurs:
            if choix.text==choix_final["nb_joueurs"]:
                choix.active=True
                choix.color=COLOR_ACTIVE
    
    while dico_stop["nouvellepartie"]==True :
                
        fenetre.blit(fond_uni,(0,0))
        
        #choix du nombre de joueurs 
        fenetre.blit(police3.render("Nouvelle partie!",True,pygame.Color("#000000")),(485,100))
        fenetre.blit(police3.render("Nombre de joueurs",True,pygame.Color("#000000")),(465,200))
        
        #dessin des boutons
        valider.draw(fenetre)  
        retour.draw(fenetre)
        
        #choix du nombre de joueurs
        for choix in choix_nb_joueurs:
            choix.draw(fenetre)
            if choix.active==True:
                choix_final["nb_joueurs"]=choix.text
                                                            
        #actualisation de l'écran
        pygame.display.flip()
        
        for event in pygame.event.get():
            
            #gestion des boutons
            valider.handle_event(event,action=enregistrement_inputs, parametre_action=choix_final)
            retour.handle_event(event,action=menu)
            
            #actualisation du choix du nombre de joueurs
            for choix in choix_nb_joueurs:
                choix.handle_event(event, choix_nb_joueurs)
            
            #arrêt du jeu
            if event.type == QUIT:   
                dico_stop = dict.fromkeys(dico_stop, False)
        

def parametrisation_1(dico_erreurs={}):
    """
    Fonction qui lance la paramétrisation des joueurs
    """
    global fenetre, dico_stop
    
    dico_stop['nouvellepartie']=False
    dico_stop['parametrisation1']=True
    
    #stockage des paramètres choisis qui seront enregistrés
    dico_choix={}
    dico_choix['fonction']=parametrisation_2
    dico_choix['fonction_prec']=parametrisation_1
    #pour cette fonction, on testera la nullité des paramètres entrés. 
    dico_choix['test_null']=True
    #pour cette fonction, on ne testera pas le maximum des paramètres entrés. 
    dico_choix['test_max']=False
    
    #lecture du fichier de paramétrisation 
    dico_parametres=lecture(fichier)
    nb_joueurs=dico_parametres['nb_joueurs']
    
    #initialisation des boutons valider et retour
    valider=Bouton(850,600,200,50,"Valider")
    retour=Bouton(500,600,200,50,"Retour")
    
    #initialisation des inputbox (on en définit 4 même si les 4 ne sont pas forcément utilisées)
    input_box1=InputBox(350, 100, 150, 30, text=dico_parametres['pseudo_joueur_1'])
    input_box2=InputBox(350, 200, 150, 30, text=dico_parametres['pseudo_joueur_2'])
    input_box3=InputBox(350, 300, 150, 30, text=dico_parametres['pseudo_joueur_3'])
    input_box4=InputBox(350, 400, 150, 30, text=dico_parametres['pseudo_joueur_4'])
    input_boxes=[input_box1,input_box2,input_box3,input_box4]
    L_pseudos=['pseudo_joueur_1','pseudo_joueur_2','pseudo_joueur_3','pseudo_joueur_4']
    for k in range(0,len(input_boxes)):
        #remplissage du dictionnaire des choix
        dico_choix[L_pseudos[k]]=input_boxes[k].text
        #vérification des erreurs
        for erreur in dico_erreurs.keys():
            if L_pseudos[k]==erreur:
                input_boxes[k].color=COLOR_ERROR
    
    #initialisation des boxs pour le choix des modes de jeu des joueurs
    choix_manuel_joueur_1=ChoiceBox(650, 100, 175, 30, 'manuel')
    choix_automatique_joueur_1=ChoiceBox(650, 140, 175, 30, 'automatique')
    choix_manuel_joueur_2=ChoiceBox(650, 200, 175, 30, 'manuel')
    choix_automatique_joueur_2=ChoiceBox(650, 240, 175, 30, 'automatique')
    choix_manuel_joueur_3=ChoiceBox(650, 300, 175, 30, 'manuel')
    choix_automatique_joueur_3=ChoiceBox(650, 340, 175, 30, 'automatique')
    choix_manuel_joueur_4=ChoiceBox(650, 400, 175, 30, 'manuel')
    choix_automatique_joueur_4=ChoiceBox(650, 440, 175, 30, 'automatique')
    choix_modes_joueurs=[[choix_manuel_joueur_1,choix_automatique_joueur_1],[choix_manuel_joueur_2,choix_automatique_joueur_2],[choix_manuel_joueur_3,choix_automatique_joueur_3],[choix_manuel_joueur_4,choix_automatique_joueur_4]]
    L_modes=['mode_joueur_1','mode_joueur_2','mode_joueur_3','mode_joueur_4']
    for k in range(0,len(L_modes)):
        dico_choix[L_modes[k]]=dico_parametres[L_modes[k]]
    
    #initialisation des boxs pour le choix des niveaux des joueurs
    choix_lvl_j1_1=ChoiceBox(1000, 140, 50, 30, '1')
    choix_lvl_j1_2=ChoiceBox(1050, 140, 50, 30, '2')
    choix_lvl_j1_3=ChoiceBox(1100, 140, 50, 30, '3')
    choix_lvl_j2_1=ChoiceBox(1000, 240, 50, 30, '1')
    choix_lvl_j2_2=ChoiceBox(1050, 240, 50, 30, '2')
    choix_lvl_j2_3=ChoiceBox(1100, 240, 50, 30, '3')
    choix_lvl_j3_1=ChoiceBox(1000, 340, 50, 30, '1')
    choix_lvl_j3_2=ChoiceBox(1050, 340, 50, 30, '2')
    choix_lvl_j3_3=ChoiceBox(1100, 340, 50, 30, '3')
    choix_lvl_j4_1=ChoiceBox(1000, 440, 50, 30, '1')
    choix_lvl_j4_2=ChoiceBox(1050, 440, 50, 30, '2')
    choix_lvl_j4_3=ChoiceBox(1100, 440, 50, 30, '3')
    choix_lvl_joueurs=[[choix_lvl_j1_1,choix_lvl_j1_2,choix_lvl_j1_3],[choix_lvl_j2_1,choix_lvl_j2_2,choix_lvl_j2_3],[choix_lvl_j3_1,choix_lvl_j3_2,choix_lvl_j3_3],[choix_lvl_j4_1,choix_lvl_j4_2,choix_lvl_j4_3]]
    L_lvl=['niveau_ia_1','niveau_ia_2','niveau_ia_3','niveau_ia_4']
    for k in range(0,len(L_lvl)):
        dico_choix[L_lvl[k]]=dico_parametres[L_lvl[k]]
    
    #initialisation des boutons sélectionnés en fonction des valeurs renseignées dans le fichier 
    #de configuration
    for k in range(0,len(choix_modes_joueurs)):
        for choix in choix_modes_joueurs[k]:
            if choix.text==dico_choix[L_modes[k]]:
                choix.active=True
                choix.color=COLOR_ACTIVE 
    for k in range(0,len(choix_lvl_joueurs)):
        for choix in choix_lvl_joueurs[k]:
            if choix.text==dico_choix[L_lvl[k]]:
                choix.active=True
                choix.color=COLOR_ACTIVE
    
    while dico_stop['parametrisation1']==True :
        
        #actualisation de l'écran
        pygame.display.flip()
        
        fenetre.blit(fond_uni,(0,0))
        
        #paramètres des joueurs
        fenetre.blit(police3.render("Paramètres des joueurs",True,pygame.Color("#000000")),(100,50))
        
        if len(dico_erreurs)!=0:
            fenetre.blit(police2.render("ERREUR : Renseignez tous les champs!",True,COLOR_ERROR),(550,50))
        
        for k in range(1,int(nb_joueurs)+1):

            fenetre.blit(police2.render("Joueur "+str(k)+": ",True,pygame.Color("#000000")),(100,(k*100)))
            fenetre.blit(police2.render("Pseudo",True,pygame.Color("#000000")),(250,(k*100)))
            fenetre.blit(police2.render("Mode",True,pygame.Color("#000000")),(550,(k*100)))
                
            box=input_boxes[k-1]
            box.draw(fenetre)
            choix_manuel=choix_modes_joueurs[k-1][0]
            choix_automatique=choix_modes_joueurs[k-1][1]
            choix_manuel.draw(fenetre)
            choix_automatique.draw(fenetre)
            #si le mode automatique est activé, l'utilisateur peut choisir le niveau de l'ia. 
            #mais il ne peut pas choisir son nom
            if choix_automatique.active:
                fenetre.blit(police2.render("Niveau",True,pygame.Color("#000000")),(900,45+(k*100)))
                choix_lvl1=choix_lvl_joueurs[k-1][0]
                choix_lvl2=choix_lvl_joueurs[k-1][1]
                choix_lvl3=choix_lvl_joueurs[k-1][2]
                choix_lvl1.draw(fenetre)
                choix_lvl2.draw(fenetre)
                choix_lvl3.draw(fenetre)
        
        #dessin des boutons
        valider.draw(fenetre)  
        retour.draw(fenetre)
                                          
        #actualisation de l'écran
        pygame.display.flip()
        
        for event in pygame.event.get():
            
            #gestion des boutons
            valider.handle_event(event,action=enregistrement_inputs, parametre_action=dico_choix)
            retour.handle_event(event,action=nouvelle_partie)
            
            #remplissage des inputboxs    
            for k in range(1,int(nb_joueurs)+1):
                choix_manuel=choix_modes_joueurs[k-1][0]
                choix_automatique=choix_modes_joueurs[k-1][1]
                choix_manuel.handle_event(event,choix_modes_joueurs[k-1])
                choix_automatique.handle_event(event,choix_modes_joueurs[k-1])
                if choix_automatique.active:
                    choix_lvl_joueurs[k-1][0].handle_event(event,choix_lvl_joueurs[k-1])
                    choix_lvl_joueurs[k-1][1].handle_event(event,choix_lvl_joueurs[k-1])
                    choix_lvl_joueurs[k-1][2].handle_event(event,choix_lvl_joueurs[k-1])
                    choix_lvl1=choix_lvl_joueurs[k-1][0]
                    choix_lvl2=choix_lvl_joueurs[k-1][1]
                    choix_lvl3=choix_lvl_joueurs[k-1][2]
                    if choix_lvl1.active:
                        dico_choix[L_lvl[k-1]]=choix_lvl1.text
                    elif choix_lvl2.active:
                        dico_choix[L_lvl[k-1]]=choix_lvl2.text
                    elif choix_lvl3.active:
                        dico_choix[L_lvl[k-1]]=choix_lvl3.text
                    input_boxes[k-1].text="Ordinateur"+str(k)
                    input_boxes[k-1].txt_surface=police2.render(input_boxes[k-1].text, True, input_boxes[k-1].color)
                    dico_choix[L_pseudos[k-1]]=input_boxes[k-1].text
                    dico_choix[L_modes[k-1]]="automatique"
                else:
                    box=input_boxes[k-1]
                    box.handle_event(event)
                    dico_choix[L_pseudos[k-1]]=input_boxes[k-1].text
                    dico_choix[L_modes[k-1]]="manuel"
                    if input_boxes[k-1].text=="Ordinateur"+str(k):
                        input_boxes[k-1].text="Joueur"+str(k)
                        input_boxes[k-1].txt_surface=police2.render(input_boxes[k-1].text, True, input_boxes[k-1].color)
            
            #arrêt du jeu
            if event.type == QUIT:   
                dico_stop = dict.fromkeys(dico_stop, False)

def parametrisation_2(dico_erreurs={}):
    '''
    Fonction qui lance la paramétrisation des paramètres avancés de la partie
    '''    
    
    global fenetre, dico_stop
    
    dico_stop['parametrisation1']=False
    dico_stop['parametrisation2']=True
    
    #lecture du fichier de paramétrisation 
    dico_parametres=lecture(fichier)
    
    #stockage des choix
    dico_choix={}
    dico_choix['fonction']=game
    dico_choix['fonction_prec']=parametrisation_2
    dico_choix['nb_joueurs']=dico_parametres['nb_joueurs']
    dico_choix['fonction_game']=game
    #pour cette fonction, on testera la nullité des paramètres entrés. 
    dico_choix['test_null']=True
    #pour cette fonction, on testera aussi le maximum des paramètres entrés. 
    dico_choix['test_max']=True
    
    #initialisation des boutons valider et retour
    valider=Bouton(900,300,200,50,"Lancer la partie !")
    retour=Bouton(900,400,200,50,"Retour")
    
    #définition des choicebox pour la taille du plateau
    taille_7=ChoiceBox(600, 110, 50, 30, '7')
    taille_11=ChoiceBox(650, 110, 50, 30, '11')
    taille_15=ChoiceBox(700, 110, 50, 30, '15')
    taille_19=ChoiceBox(750, 110, 50, 30, '19')
    taille_23=ChoiceBox(800, 110, 50, 30, '23')
    choix_taille=[taille_7, taille_11, taille_15, taille_19, taille_23]
    dico_choix['dimensions_plateau']=dico_parametres['dimensions_plateau']
    
    #initialisation des boutons sélectionnés en fonction des valeurs renseignées dans le fichier 
    #de configuration
    for choix in choix_taille:
        if choix.text==dico_choix['dimensions_plateau']:
            choix.active=True
            choix.color=COLOR_ACTIVE 
    
    #définition des inputboxs pour l'ensemble des paramètres restants
    #en initialisant les valeurs aux paramètres du fichier de paramétrisation. 
    ib_nb_fantomes=InputBox(600, 180, 150, 30, text=dico_parametres['nb_fantomes'], contenu='num')
    ib_nb_fantomes_mission=InputBox(600, 250, 150, 30, text=dico_parametres['nb_fantomes_mission'], contenu='num')
    ib_nb_joker=InputBox(600, 320, 150, 30, text=dico_parametres['nb_joker'], contenu='num')
    ib_points_pepite=InputBox(600, 390, 150, 30, text=dico_parametres['points_pepite'], contenu='num')
    ib_points_fantome=InputBox(600, 460, 150, 30, text=dico_parametres['points_fantome'], contenu='num')
    ib_points_fantome_mission=InputBox(600, 530, 150, 30, text=dico_parametres['points_fantome_mission'], contenu='num')
    ib_bonus_mission=InputBox(600, 630, 150, 30, text=dico_parametres['bonus_mission'], contenu='num')
    input_boxes=[ib_nb_fantomes,ib_nb_fantomes_mission,ib_nb_joker,ib_points_pepite,ib_points_fantome,ib_points_fantome_mission,ib_bonus_mission]
    
    #Stockage des choix des inputs
    L_parametres=['nb_fantomes','nb_fantomes_mission','nb_joker','points_pepite','points_fantome','points_fantome_mission','bonus_mission']
    for k in range(0,len(input_boxes)):
        dico_choix[L_parametres[k]]=input_boxes[k].text
        #vérification des erreurs
        for erreur in dico_erreurs.keys():
            if L_parametres[k]==erreur:
                input_boxes[k].color=COLOR_ERROR

    while dico_stop['parametrisation2']==True :
                
        fenetre.blit(fond_uni,(0,0))
        
        #titre de la fenêtre
        fenetre.blit(police3.render("Paramètres avancés",True,pygame.Color("#000000")),(100,50))
        
        #affichage de l'éventuel message d'erreur 
        if len(dico_erreurs)!=0:
            if dico_erreurs['type']=='null':
                fenetre.blit(police2.render("ERREUR : Renseignez tous les champs!",True,COLOR_ERROR),(550,50))
            elif dico_erreurs['type']=='max':
                fenetre.blit(police2.render("ERREUR : Renseignez une valeur plus petite",True,COLOR_ERROR),(550,50))
        
        #dessin des boutons
        valider.draw(fenetre)  
        retour.draw(fenetre)
        
        #dessin des choicebox
        for choicebox in choix_taille:
            choicebox.draw(fenetre)
        
        #dessin des inputboxs
        for box in input_boxes:
            box.draw(fenetre)
            
        #Ecriture des textes associés aux boxes
        fenetre.blit(police2.render("Dimensions du plateau: ",True,pygame.Color("#000000")),(100,110))
        fenetre.blit(police2.render("Nombre de fantômes: ",True,pygame.Color("#000000")),(100,180))
        n=int(dico_choix['dimensions_plateau'])
        nb_fant=(n-2)*(n//2)+(n//2)*(n//2-1)
        fenetre.blit(police1.render("Entier positif / Maximum:"+str(nb_fant),True,pygame.Color("#000000")),(100,210))
        fenetre.blit(police1.render("Configuration standard : "+str(nb_fant)+" fantômes pour un plateau de taille "+str(dico_choix['dimensions_plateau'])+"x"+str(dico_choix['dimensions_plateau'])+".",True,pygame.Color("#000000")),(100,230))
        fenetre.blit(police2.render("Nombre de fantômes par ordre de mission: ",True,pygame.Color("#000000")),(100,250))
        fenetre.blit(police1.render("Entier positif / Configuration standard : 3 fantômes.",True,pygame.Color("#000000")),(100,280))
        fenetre.blit(police2.render("Joker(s) par joueur: ",True,pygame.Color("#000000")),(100,320))
        fenetre.blit(police1.render("Entier positif / Configuration standard : 1 joker.",True,pygame.Color("#000000")),(100,350))
        fenetre.blit(police2.render("Points gagnés par pépite ramassée: ",True,pygame.Color("#000000")),(100,390))    
        fenetre.blit(police1.render("Entier positif / Configuration standard : 1 point.",True,pygame.Color("#000000")),(100,420))                                                                                                                                                                                                                                                                                                
        fenetre.blit(police2.render("Points gagnés par fantôme capturé: ",True,pygame.Color("#000000")),(100,460))
        fenetre.blit(police1.render("Entier positif / Configuration standard : 5 points.",True,pygame.Color("#000000")),(100,490))
        fenetre.blit(police2.render("Points gagnés par fantôme capturé: ",True,pygame.Color("#000000")),(100,530))  
        fenetre.blit(police2.render("si le fantôme figure sur l'ordre de mission",True,pygame.Color("#000000")),(100,560))
        fenetre.blit(police1.render("Entier positif / Configuration standard : 20 points.",True,pygame.Color("#000000")),(100,590))
        fenetre.blit(police2.render("Bonus lors du remplissage d'une mission: ",True,pygame.Color("#000000")),(100,630))
        fenetre.blit(police1.render("Entier positif / Configuration standard : 40 points.",True,pygame.Color("#000000")),(100,660)) 
                                                                               
        #actualisation de l'écran
        pygame.display.flip()
        
        #gestion des évènements
        for event in pygame.event.get():
            
            #gestion des boutons
            valider.handle_event(event,action=enregistrement_inputs, parametre_action=dico_choix)
            retour.handle_event(event,action=parametrisation_1)
            
            #gestion des inputboxs
            for k in range(0,len(input_boxes)):
                box=input_boxes[k]
                box.handle_event(event)
                dico_choix[L_parametres[k]]=box.text
            
            #gestion des choiceboxs
            for choix in choix_taille:
                choix.handle_event(event,choix_taille)
                if choix.active:
                    dico_choix['dimensions_plateau']=choix.text
            
            #arrêt du jeu
            if event.type == QUIT:   
                dico_stop = dict.fromkeys(dico_stop, False)
    

#-----------------------------------------Affichage graphique et début du jeu------------------------------

pygame.init()

#Ouverture de la fenêtre Pygame
fenetre = pygame.display.set_mode((1200, 700),pygame.RESIZABLE)

#Creation des images du menu
fond_menu = pygame.image.load("fond_menu.png").convert()
fond_uni = pygame.image.load("fond_uni.png").convert()

#Création de la police du jeu
police = pygame.font.Font("coda.ttf", 20) #Load font object.
police_small = pygame.font.Font("coda.ttf", 17) #Load font object.

#définition des couleurs
COLOR_INACTIVE = pygame.Color('lightskyblue3')
COLOR_ACTIVE = pygame.Color('dodgerblue2')
COLOR_ERROR = pygame.Color('tomato2')

#définition des polices
police1=pygame.font.SysFont('calibri', 15)
police2=pygame.font.SysFont('calibri', 25)
police3=pygame.font.SysFont('calibri', 35)

#Lancement du menu
menu()
pygame.quit()
