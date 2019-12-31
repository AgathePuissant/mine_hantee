
"""
FICHIER DE DEFINITION LES OBJETS ET FONCTIONS GRAPHIQUES
"""

import pygame

pygame.init()

#définition de la police du jeu
police = pygame.font.SysFont("calibri", 20, bold=True) #Load font object.
police_small = pygame.font.SysFont("calibri", 17, bold=True) #Load font object.

#définition des couleurs
COLOR_INACTIVE = pygame.Color('lightskyblue3')
COLOR_ACTIVE = pygame.Color('dodgerblue2')
COLOR_ERROR = pygame.Color('tomato2')

#définition des polices
police1=pygame.font.SysFont('calibri', 15)
police2=pygame.font.SysFont('calibri', 25)
police3=pygame.font.SysFont('calibri', 35)

def text_objects(text, font):
    textSurface = font.render(text, True, pygame.Color("#000000"))
    return textSurface, textSurface.get_rect()

class Bouton:
    """
    Classe d'objets graphiques définissant les boutons d'action dans pyGame. 
    Si l'utilisateur clique sur un bouton, alors l'action associée à ce bouton est déclenchée. 
    
    Comprend les méthodes :
        - initialisation : permet d'attribuer aux boutons de la classe leurs 
        caractéristiques graphiques.
        - handle_event : prend en entrée un évènement pyGame, une action et son éventuel paramètre.
        Traite l'évènement donné en entrée, actualise les caractéristiques graphiques du bouton,
        et déclenche l'action si nécessaire.
        - draw : prend en entrée la fenêtre pyGame et dessine le bouton dans la fenêtre. 
    """
    
    def __init__(self, x, y, w, h, text=''):
        """
        Prend en entrée : 
            - x : abscisse du coin en haut à gauche du rectangle du bouton (float).
            - y : ordonnée du coin en haut à gauche du rectangle du bouton (float).
            - w : largeur du rectangle du bouton (float).
            - h : hauteur du rectangle du bouton (float).
            - text : texte du bouton (string). 
        
        Initialise les attributs suivants :
            - rect : rectangle du bouton (rectangle, objet graphique pyGame).
            - color : couleur (color, objet graphique pyGame). 
            - text : texte du bouton (string).
            - txt_surface : surface graphique du texte du bouton (surface, objet graphique pyGame).
            - active : état d'activité du bouton (booléen).
        """
        
        self.rect = pygame.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.text = text
        self.txt_surface = police2.render(text, True, pygame.Color("#000000"))
        self.active = False
    
    def handle_event(self, event, action, parametre_action=None):
        """
        Méthode permettant de gérer, pour le bouton, les évenements pyGame 
        lors de l'utilisation de l'ordinateur par l'utilisateur. 
        
        Prend en entrée : 
            - event : 
            - action : 
            - parametre_action : 
        
        Renvoie :
        
        """
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        #si la souris se trouve au dessous du bouton, on l'active et on change la couleur
        if self.rect.x+self.rect.w > mouse[0] > self.rect.x and self.rect.y+self.rect.h > mouse[1] > self.rect.y:
            self.active=True
            if click[0] == 1:
                # L'action est lancée, avec ou sans paramètre
                if parametre_action==None:
                    action()
                else:
                    action(parametre_action)
        else:
            self.active=False
            
        #actualisation de la couleur du bouton
        if self.active==True:
            self.color=COLOR_ACTIVE
        else:
            self.color=COLOR_INACTIVE
    
    def draw(self, fenetre):
        # Blit le rectangle. 
        pygame.draw.rect(fenetre, self.color, self.rect)
        # Blit le texte.
        text_rect=self.txt_surface.get_rect()
        text_rect.center=(self.rect.x+((self.rect.w)/2), self.rect.y+((self.rect.h)/2))
        fenetre.blit(self.txt_surface, text_rect)
    
#definition des Inputboxs
    
class InputBox:

    def __init__(self, x, y, w, h, text='', max_caract=10, contenu='texte'):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.text = text
        self.txt_surface = police2.render(text, True, self.color)
        self.active = False
        self.max_caract=max_caract
        self.contenu=contenu

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
                        
            # si l'utilisateur clique sur le rectangle de inputbox.
            if self.rect.collidepoint(event.pos):
                # Activation de l'inputbox.
                self.active = not self.active
            else:
                self.active = False
            # On change la couleur de l'inputbox pour montrer qu'elle est active
            self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                elif self.contenu=='num' and (event.key in [pygame.K_0,pygame.K_1,pygame.K_2,pygame.K_3,pygame.K_4,pygame.K_5,pygame.K_6,pygame.K_7,pygame.K_8,pygame.K_9,pygame.K_KP0,pygame.K_KP1,pygame.K_KP2,pygame.K_KP3,pygame.K_KP4,pygame.K_KP5,pygame.K_KP6,pygame.K_KP7,pygame.K_KP8,pygame.K_KP9]) and len(self.text)<self.max_caract:
                    self.text += event.unicode
                elif self.contenu=='texte' and len(self.text)<self.max_caract:
                    self.text += event.unicode
                # Re-render le texte. 
                self.txt_surface = police2.render(self.text, True, self.color)

    def draw(self, fenetre):
        # Blit le rectangle. 
        pygame.draw.rect(fenetre, self.color, self.rect, 2)
        # Blit le texte. 
        fenetre.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))

#Definition des choiceboxs (boutons de sélection de valeurs prédéfinies)

class ChoiceBox:
    
    def __init__(self, x, y, w, h, text, active=False):
        self.rect = pygame.Rect(x, y, w, h)
        if active==False:
            self.color = COLOR_INACTIVE
        else:
            self.color = COLOR_ACTIVE
        self.text = text
        self.txt_surface = police2.render(text, True, self.color)
        self.active=active
    
    def handle_event(self, event, ChoiceBox_associees=[]):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # si l'utilisateur clique sur le rectangle de inputbox.
            if self.rect.collidepoint(event.pos):
                # Activation de l'inputbox.
                self.active = True
                #si l'un des boutons associé est activé, alors on l'inactive (un seul choix possible)
                for box in ChoiceBox_associees:
                    if self.rect!=box:
                        if box.active:
                            box.active = False
                            box.color=COLOR_INACTIVE
            self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE
    
    def draw(self,fenetre):
        # Blit le rectangle. 
        pygame.draw.rect(fenetre, self.color, self.rect, 2)
        # Blit le texte. 
        fenetre.blit(self.txt_surface, (self.rect.x+20, self.rect.y+5))
        
    
def affiche_plateau(plat,fenetre):
    
    #Création des images nécesssaires au plateau
    #fond = pygame.image.load("fond.jpg").convert()
    fond_ext = pygame.image.load("fond_ext.png").convert()
    mur1 = pygame.image.load("mur1.png").convert_alpha()
    mur2 = pygame.image.load("mur2.png").convert_alpha()
    mur3 = pygame.image.load("mur3.png").convert_alpha()
    mur4 = pygame.image.load("mur4.png").convert_alpha()
    liste_im_joueur = [pygame.image.load("joueur"+str(i)+".png").convert_alpha() for i in range(1,5)]
    fond_a_jouer = pygame.image.load("fond_carte_a_jouer.jpg").convert()
    fantome = pygame.image.load("fantome.png").convert_alpha()
    pepite = pygame.image.load("pepite.png").convert_alpha()
    indeplacable = pygame.image.load("indeplacable.png").convert_alpha()

    
    #Chargement du fond dans la fenetre 
    fenetre.blit(fond_ext,(0,0))
    #fenetre.blit(fond, (0,0))
    N = plat.N #on récupère la taille du plateau
     
    #Mise  à jour de la taille des images en fonction du nombre de cartes du plateau
    x_mur1 = 100
    y_mur1 = 100
    mur1 = pygame.transform.scale(mur1, (int(x_mur1*(7/N)),int(y_mur1*(7/N))))
    x_mur2 = 100
    y_mur2 = 100
    mur2 = pygame.transform.scale(mur2, (int(x_mur2*(7/N)),int(y_mur2*(7/N))))
    x_mur3 = 100
    y_mur3 = 100
    mur3 = pygame.transform.scale(mur3, (int(x_mur3*(7/N)),int(y_mur3*(7/N))))
    x_mur4 = 100
    y_mur4 = 100
    mur4 = pygame.transform.scale(mur4, (int(x_mur4*(7/N)),int(y_mur4*(7/N))))
    x_fond_a_jouer = 100
    y_fond_a_jouer = 100
    fond_a_jouer = pygame.transform.scale(fond_a_jouer,(int(x_fond_a_jouer*(7/N)),int(y_fond_a_jouer*(7/N))))
    x_fantome = fantome.get_width()
    y_fantome = fantome.get_height()
    fantome = pygame.transform.scale(fantome, (int(x_fantome*(7/N)),int(y_fantome*(7/N))))
    x_pepite = pepite.get_width()
    y_pepite = pepite.get_height()
    pepite  = pygame.transform.scale(pepite, (int(x_pepite *(7/N)),int(y_pepite*(7/N))))
    x_indeplacable = indeplacable.get_width()
    y_indeplacable = indeplacable.get_height()
    indeplacable  = pygame.transform.scale(indeplacable, (int(x_indeplacable*(7/N)),int(y_indeplacable*(7/N))))
    for i in range (4) :
        x_joueur = 60
        y_joueur = 60
        liste_im_joueur[i] = pygame.transform.scale(liste_im_joueur[i], (int(x_joueur*(7/N)),int(y_joueur*(7/N))))
    
    #Création de la police du jeu
    police = pygame.font.SysFont("calibri", int(20*7/N), bold=True) #Load font object.
    
    for i in range(len(plat.position)) :
        for j in range(len(plat.position)) :
            x=plat.dico_cartes[plat.position[i,j]].coord[0]*int(100*7/N)
            y=plat.dico_cartes[plat.position[i,j]].coord[1]*int(100*7/N)
            fenetre.blit(fond_a_jouer,(y,x))

# Si on veut ajouter un graphisme pour les cartes déplaçables et indéplaçables
                       
            if plat.dico_cartes[plat.position[i,j]].deplacable==False :
                fenetre.blit(indeplacable,(y,x))
            
            for k in range(len(plat.dico_cartes[plat.position[i,j]].orientation)) :
                #fenetre.blit(fond_a_jouer,(y,x))
                if plat.dico_cartes[plat.position[i,j]].orientation[k]==1 :
                    if k==0 :
                        fenetre.blit(mur1,(y,x))
                    elif k==1 :
                        fenetre.blit(mur4,(y,x))
                    elif k==2 :
                        fenetre.blit(mur2,(y,x))
                    elif k==3 :
                        fenetre.blit(mur3,(y,x))
                       
                       
            if plat.dico_cartes[plat.position[i,j]].presence_pepite==True:
                fenetre.blit(pepite,(y,x))
            if plat.dico_cartes[plat.position[i,j]].id_fantome!=0 :
                fenetre.blit(fantome,(y,x))
                fenetre.blit(police.render(str(plat.dico_cartes[plat.position[i,j]].id_fantome),True,pygame.Color("#FFFFFF")),(y+10,x+30))
                       
    for i in range(len(plat.dico_joueurs)) :
        x=plat.dico_joueurs[i].carte_position.coord[0]*int(100*7/N)
        y=plat.dico_joueurs[i].carte_position.coord[1]*int(100*7/N)
        fenetre.blit(liste_im_joueur[i],(y,x))
        
#on place la carte à jouer dans le coin droite haut du plateau 
    x=750
    y=50
    fenetre.blit(fond_a_jouer,(x,y))
    for k in range(len(plat.carte_a_jouer.orientation)):
        if plat.carte_a_jouer.orientation[k]==1 :
            if k==0 :
               fenetre.blit(mur1,(x,y))
            elif k==1 :
               fenetre.blit(mur4,(x,y))
            elif k==2 :
               fenetre.blit(mur2,(x,y))
            elif k==3 :
               fenetre.blit(mur3,(x,y))
    
    if plat.carte_a_jouer.presence_pepite==True:
        fenetre.blit(pepite,(x,y))
               
               
def actualise_fenetre(plateau,fenetre,joueur,info,bouton,etape_texte):
    """
    fonction pour actualiser l'affichage dans la fonction jeu
    """
    affiche_plateau(plateau,fenetre)
    liste_im_joueur = [pygame.image.load("joueur"+str(i)+".png").convert_alpha() for i in range(1,5)]

    for i in range(len(plateau.dico_joueurs)) :
                fenetre.blit(liste_im_joueur[i],(1030,320+i*80))
                fenetre.blit(police.render(str(plateau.dico_joueurs[i].nom) + " : ",False,pygame.Color("#000000")),(800,340+i*80))
                fenetre.blit(police.render("Score : "+str(plateau.dico_joueurs[i].points),False,pygame.Color("#000000")),(800,340+i*80+20))
                fenetre.blit(police.render("Ordre de mission : "+str(sorted(plateau.dico_joueurs[i].fantome_target)),False,pygame.Color("#000000")),(800,340+i*80+40))

                #test texte pour afficher le joueur qui joue
    fenetre.blit(police.render("C'est a "+str(joueur.nom)+" de jouer",False,pygame.Color(0,0,0)),(800,240))
 
    #affichage du message d'erreur
    for i in range(len(info)) :                       
        fenetre.blit(police.render(info[i],False,pygame.Color("#000000")),(760,180+i*20))
                                   
    fenetre.blit(police.render(etape_texte,False,pygame.Color("#000000")),(760,160))
                                                             
                                                             
    bouton.draw(fenetre)
                                                             
    pygame.display.flip()
                
pygame.display.quit()
