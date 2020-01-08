
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
    """
    Fonction renvoyant, pour un texte et une police donnés, les objets graphiques pyGame correspondants. 
    Ces objets graphiques peuvent ensuite être utilisés pour dessiner le texte dans une fenêtre. 
    
    Prend en entrée :
        - text : texte à dessiner dans une fenêtre (string).
        - font : police du texte (police, objet graphique pyGame). 
    
    Renvoie : 
        - textSurface : surface graphique du texte (surface, objet graphique pyGame).
        - textSurface.get_rect() : rectangle délimitant la surface graphique du texte (rectangle, objet graphique pyGame). 
    """
    
    textSurface = font.render(text, True, pygame.Color("#000000"))
    return textSurface, textSurface.get_rect()

class Bouton:
    """
    Classe d'objets graphiques définissant les boutons d'action dans pyGame. 
    Si l'utilisateur clique sur un bouton, alors l'action associée à ce bouton est déclenchée. 
    
    Comprend les méthodes :
        - initialisation : permet d'attribuer aux boutons de la classe leurs 
        caractéristiques (graphiques ou non).
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
            - active : état d'activité du bouton, non-actif par défaut (booléen).
        """
        
        self.rect = pygame.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.text = text
        self.txt_surface = police2.render(text, True, pygame.Color("#000000"))
        self.active = False
    
    def handle_event(self, event, action, parametre_action=None):
        """
        Méthode permettant de gérer, pour le bouton, les évenements pyGame 
        associés à l'utilisation de l'ordinateur par l'utilisateur. 
        
        Prend en entrée : 
            - event : évènement pyGame (event).
            - action : action à exécuter lorsque l'utilisateur clique sur le bouton (fonction). 
            - parametre_action : paramètre de l'action à exécuter (int, float ou booléen). 
        
        Actualise, en fonction de l'évènement d'entrée, l'état d'activité du bouton et sa couleur. 
        Lorsque que la souris de l'utilisateur se trouve au-dessus du bouton, celui-ci est actif et change de couleur.
        
        Délenche l'action si l'utilisateur clique sur le bouton. 
        """
        
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        #si la souris se trouve au dessous du bouton, on l'active.
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
        """
        Méthode permettant de dessiner le bouton dans la fenêtre. 
        
        Prend en entrée : 
            - fenetre : fenetre dans laquelle le bouton est dessiné (fenetre pyGame).
        
        Dessine le rectangle associé au bouton ainsi que son texte dans la fenêtre. 
        """
        
        # Blit le rectangle. 
        pygame.draw.rect(fenetre, self.color, self.rect)
        # Blit le texte.
        text_rect=self.txt_surface.get_rect()
        text_rect.center=(self.rect.x+((self.rect.w)/2), self.rect.y+((self.rect.h)/2))
        fenetre.blit(self.txt_surface, text_rect)
    
    
class InputBox:
    """
    Classe d'objets graphiques définissant les inputboxs dans pyGame. 
    Permet à l'utilisateur de saisir des textes ou des chiffres dans des cases dédiées.  
    
    Comprend les méthodes :
        - initialisation : permet d'attribuer aux inputsboxs de la classe leurs 
        différentes caractéristiques (graphiques ou non).
        - handle_event : prend en entrée un évènement pyGame, traite cet évènement et 
        actualise les caractéristiques de l'inputbox.
        - draw : prend en entrée la fenêtre pyGame et dessine l'inputbox dans la fenêtre. 
    """
    
    def __init__(self, x, y, w, h, text='', max_caract=10, contenu='texte'):
        """
        Prend en entrée : 
            - x : abscisse du coin en haut à gauche du rectangle de l'inputbox (float).
            - y : ordonnée du coin en haut à gauche du rectangle de l'inputbox (float).
            - w : largeur du rectangle de l'inputbox (float).
            - h : hauteur du rectangle de l'inputbox (float).
            - text : texte de l'inputbox lors de sa création (string). 
            - max_caract : nombre maximal de caractères pouvant être contenus dans l'inputbox (entier). 
            - contenu : type de contenu dans l'inputbox (string, 
            'texte' par défaut, correspondant à tout type de texte entré à l'aide du clavier
            'num' si l'utilisateur ne peut rentrer que des caractères numériques dans l'inputbox).
        
        Initialise les attributs correspondant à ces éléments d'entrées ainsi que 
        les attributs :
            - rect : rectangle de l'inputbox (rectangle, objet graphique pyGame).
            - color : couleur (color, objet graphique pyGame). 
            - txt_surface : surface graphique du texte de l'inputbox (surface, objet graphique pyGame).
            - active : état d'activité de l'inputbox, non-actif par défaut (booléen). 
        """
        
        self.rect = pygame.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.text = text
        self.txt_surface = police2.render(text, True, self.color)
        self.active = False
        self.max_caract=max_caract
        self.contenu=contenu

    def handle_event(self, event):
        """
        Méthode permettant de gérer, pour l'inputbox, les évenements pyGame 
        associés à l'utilisation de l'ordinateur par l'utilisateur. 
        
        Prend en entrée : 
            - event : évènement pyGame (event).
        
        Actualise, en fonction de l'évènement d'entrée, l'état d'activité du bouton, sa couleur et son texte.
        
        Lorsque que la souris de l'utilisateur se trouve au-dessus du bouton
        et que l'utilisateur clique sur le rectangle, l'inputbox est actif et son cadre change de couleur.
        Lorsque l'inputbox est actif et que l'utilisateur utilise le clavier, le texte de l'inputbox est actualisé
        en fonction des entrées de l'utilisateur. 
        """
        
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
        """
        Méthode permettant de dessiner l'inputbox dans la fenêtre. 
        
        Prend en entrée : 
            - fenetre : fenetre dans laquelle l'inputbox est dessiné (fenetre pyGame).
        
        Dessine le rectangle associé à l'inputbox ainsi que son texte dans la fenêtre. 
        """

        # Blit le rectangle. 
        pygame.draw.rect(fenetre, self.color, self.rect, 2)
        # Blit le texte. 
        fenetre.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))

#Definition des choiceboxs (boutons de sélection de valeurs prédéfinies)

class ChoiceBox:
    """
    Classe d'objets graphiques définissant les boutons de choix (choiceboxs) dans pyGame. 
    Permet à l'utilisateur de choisir une valeur unique entre différents boutons de choix
    en cliquant sur le bouton désiré. 
    
    Comprend les méthodes :
        - initialisation : permet d'attribuer aux boutons de la classe leurs 
        caractéristiques (graphiques ou non).
        - handle_event : prend en entrée un évènement pyGame ainsi que la liste des boutons associés.
        Traite l'évènement donné en entrée et actualise les caractéristiques du bouton 
        et des ses boutons associés.
        - draw : prend en entrée la fenêtre pyGame et dessine le bouton dans la fenêtre. 
    """
    
    def __init__(self, x, y, w, h, text, active=False):
        """
        Prend en entrée : 
            - x : abscisse du coin en haut à gauche du rectangle du bouton (float).
            - y : ordonnée du coin en haut à gauche du rectangle du bouton (float).
            - w : largeur du rectangle du bouton (float).
            - h : hauteur du rectangle du bouton (float).
            - text : texte du bouton (string). 
            - active : état d'activité du bouton, non-actif par défaut (booléen).
        
        Initialise les attributs correspondant à ces éléments d'entrées ainsi que 
        les attributs :
            - rect : rectangle du bouton (rectangle, objet graphique pyGame).
            - color : couleur (color, objet graphique pyGame). 
            - txt_surface : surface graphique du texte du bouton (surface, objet graphique pyGame).
        """
        
        self.rect = pygame.Rect(x, y, w, h)
        if active==False:
            self.color = COLOR_INACTIVE
        else:
            self.color = COLOR_ACTIVE
        self.text = text
        self.txt_surface = police2.render(text, True, self.color)
        self.active=active
    
    def handle_event(self, event, ChoiceBox_associees=[]):
        """
        Méthode permettant de gérer, pour le bouton, les évenements pyGame 
        associés à l'utilisation de l'ordinateur par l'utilisateur. 
        
        Prend en entrée : 
            - event : évènement pyGame (event).
            - ChoiceBox_associees : boutons de choix associés au bouton. 
            L'utilisateur peut réaliser un choix unique entre tous ces boutons. 
        
        Actualise, en fonction de l'évènement d'entrée, les états d'activité et les couleurs 
        du bouton et de ses boutons associés. 
        Si l'utilisateur clique sur le bouton, celui-ci devient actif, et les boutons 
        associés sont inactivés. 
        """
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
        """
        Méthode permettant de dessiner le bouton de choix dans la fenêtre. 
        
        Prend en entrée : 
            - fenetre : fenetre dans laquelle le bouton est dessiné (fenetre pyGame).
        
        Dessine le rectangle associé au bouton ainsi que son texte dans la fenêtre. 
        """
        # Blit le rectangle. 
        pygame.draw.rect(fenetre, self.color, self.rect, 2)
        # Blit le texte. 
        fenetre.blit(self.txt_surface, (self.rect.x+20, self.rect.y+5))
        
    
def affiche_plateau(plat,fenetre):
    """
    Fonction permettant d'afficher une instance de la classe plateau 
    dans la fenêtre pyGame. 
    
    Prend en entrée :
        - plat : plateau de jeu (plateau).
        - fenetre : fenetre pyGame (fenetre). 
    
    Charge l'ensembles des objets graphiques nécessaires au plateau dans pyGame
    et affiche place ces objets dans la fenêtre en fonction des paramètres
    du plateau. 
    """
    
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
    fantome_cible = pygame.image.load("fantome_cible.png").convert_alpha()
    pepite = pygame.image.load("pepite.png").convert_alpha()
    indeplacable = pygame.image.load("indeplacable.png").convert_alpha()
    fleche1= pygame.image.load("fleche1.png").convert_alpha()
    fleche2= pygame.image.load("fleche2.png").convert_alpha()
    fleche3= pygame.image.load("fleche3.png").convert_alpha()
    fleche4= pygame.image.load("fleche4.png").convert_alpha()
    
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
    x_fleche1 = 40
    y_fleche1 = 40
    fleche1 = pygame.transform.scale(fleche1, (int(x_fleche1*(7/N)),int(y_fleche1*(7/N))))
    x_fleche2 = 40
    y_fleche2 = 40
    fleche2 = pygame.transform.scale(fleche2, (int(x_fleche2*(7/N)),int(y_fleche2*(7/N))))
    x_fleche3 = 40
    y_fleche3 = 40
    fleche3 = pygame.transform.scale(fleche3, (int(x_fleche3*(7/N)),int(y_fleche3*(7/N))))
    x_fleche4 = 40
    y_fleche4 = 40
    fleche4 = pygame.transform.scale(fleche4, (int(x_fleche4*(7/N)),int(y_fleche4*(7/N))))
    x_joueur = 60
    y_joueur = 60
    for i in range (4) :
        liste_im_joueur[i] = pygame.transform.scale(liste_im_joueur[i], (int(x_joueur*(7/N)),int(y_joueur*(7/N))))
    
    #Création de la police du jeu
    police = pygame.font.SysFont("calibri", int(20*7/N), bold=True) #Load font object.
    
    #Affichage des cases du plateau
    for i in range(len(plat.position)) :
        for j in range(len(plat.position)) :
            x=plat.dico_cartes[plat.position[i,j]].coord[0]*int(100*7/N)
            y=plat.dico_cartes[plat.position[i,j]].coord[1]*int(100*7/N)
            fenetre.blit(fond_a_jouer,(y,x))

            # Ajout d'un graphisme pour les cartes déplaçables et indéplaçable   
            if plat.dico_cartes[plat.position[i,j]].deplacable==False :
                fenetre.blit(indeplacable,(y,x))
            
            # Affichage des murs
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
                       
            #affichage des pépites           
            if plat.dico_cartes[plat.position[i,j]].presence_pepite==True:
                fenetre.blit(pepite,(y,x))
                
            #affichage des fantomes
            if plat.dico_cartes[plat.position[i,j]].id_fantome!=0 :
                if plat.dico_cartes[plat.position[i,j]].id_fantome == plat.id_dernier_fantome+1 :
                    #le fantome cible est affiché en rouge
                    fenetre.blit(fantome_cible,(y,x))
                else :
                    #les autres fantomes sont affichés en orange
                    fenetre.blit(fantome,(y,x))
                #les numréos des fantomes sont affichés à côté de chaque fantome
                fenetre.blit(police.render(str(plat.dico_cartes[plat.position[i,j]].id_fantome),True,pygame.Color("#FFFFFF")),(y+10,x+30))
    
    #On met des flèches là ou les insertions sont possibles
    for i in plat.insertions_possibles :
        if i[0]==0 :
            x=i[0]*int(100*7/N)+((((100*7/N))/2)-int(x_fleche1*(7/N))/2)
            y=i[1]*int(100*7/N)+((((100*7/N))/2)-int(y_fleche1*(7/N))/2)
            fenetre.blit(fleche1,(y,x))
        elif i[1]== 0 :
            x=i[0]*int(100*7/N)+((((100*7/N))/2)-int(x_fleche3*(7/N))/2)
            y=i[1]*int(100*7/N)+((((100*7/N))/2)-int(y_fleche3*(7/N))/2)
            fenetre.blit(fleche3,(y,x))
        elif i[0]<i[1]:
            x=i[0]*int(100*7/N)+((((100*7/N))/2)-int(x_fleche4*(7/N))/2)
            y=i[1]*int(100*7/N)+((((100*7/N))/2)-int(y_fleche4*(7/N))/2)
            fenetre.blit(fleche4,(y,x))
        else :
            x=i[0]*int(100*7/N)+((((100*7/N))/2)-int(x_fleche2*(7/N))/2)
            y=i[1]*int(100*7/N)+((((100*7/N))/2)-int(y_fleche2*(7/N))/2)
            fenetre.blit(fleche2,(y,x))
                               
    for i in range(len(plat.dico_joueurs)) :
        x=plat.dico_joueurs[i].carte_position.coord[0]*int(100*7/N)+((((100*7/N))/2)-int(x_joueur*(7/N))/2)
        y=plat.dico_joueurs[i].carte_position.coord[1]*int(100*7/N)+((((100*7/N))/2)-int(y_joueur*(7/N))/2)
        fenetre.blit(liste_im_joueur[i],(y,x))                   
        
    #on place la carte à jouer dans le coin droite haut du plateau 
    x=750
    y=50
    fenetre.blit(fond_a_jouer,(x,y))
    #avec ses murs
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
    #et sa pépite éventuellement
    if plat.carte_a_jouer.presence_pepite==True:
        fenetre.blit(pepite,(x,y))
               
               
def actualise_fenetre(plateau,fenetre,joueur,info,bouton,etape_texte,joker):
    """
    Fonction permettant d'actualiser l'affichage du plateau 
    dans la fonction jeu (game). 
    
    Prend en entrée :
        - plateau : plateau de jeu (plateau).
        - fenetre : fenetre pyGame (fenetre). 
        - joueur : joueur dont c'est le tour (joueur). 
        - info : message d'erreur ou d'information de jeu (string). 
        - bouton : bouton permettant d'afficher les commandes (bouton). 
        - etape_texte : message contenant l'étape du jeu (string). 
    """
    #affichage du plateau
    affiche_plateau(plateau,fenetre)
    
    #affichage des avatars des joueurs
    liste_im_joueur = [pygame.image.load("joueur"+str(i)+".png").convert_alpha() for i in range(1,5)]
    for i in range (4) :
        x_joueur = 60
        y_joueur = 60
        liste_im_joueur[i] = pygame.transform.scale(liste_im_joueur[i], (int(x_joueur),int(y_joueur)))
    
    #Informations sur les joueurs (scores, ordres de mission, jokers). 
    for i in range(len(plateau.dico_joueurs)) :
                fenetre.blit(liste_im_joueur[i],(1030,320+i*80))
                fenetre.blit(police_small.render(str(plateau.dico_joueurs[i].nom) + " : ",False,pygame.Color("#000000")),(800,340+i*75))
                fenetre.blit(police1.render("Score : "+str(plateau.dico_joueurs[i].points),False,pygame.Color("#000000")),(800,340+i*75+15))
                fenetre.blit(police1.render("Ordre de mission : "+str(sorted(plateau.dico_joueurs[i].fantome_target)),False,pygame.Color("#000000")),(800,340+i*75+30))
                fenetre.blit(police1.render("Jokers restants : "+str(plateau.dico_joueurs[i].nb_joker),False,pygame.Color("#000000")),(800,340+i*75+45))
                
    #test texte pour afficher le joueur qui joue
    fenetre.blit(police.render("C'est a "+str(joueur.nom)+" de jouer",False,pygame.Color(0,0,0)),(800,240))
 
    #affichage du message d'erreur
    for i in range(len(info)) :                       
        fenetre.blit(police.render(info[i],False,pygame.Color("#000000")),(760,180+i*20))
    if joker!="IA" :
        fenetre.blit(police.render("Joker restants : "+str(joker)+" (J pour activer)",False,pygame.Color("#000000")),(760,180+len(info)*20))
    #affichage de l'étape de jeu                               
    fenetre.blit(police.render(etape_texte,False,pygame.Color("#000000")),(760,160))
                                                             
    #dessin du bouton                                                        
    bouton.draw(fenetre)
    
    #actualisation de la fenêtre                                                         
    pygame.display.flip()
                
pygame.display.quit()
