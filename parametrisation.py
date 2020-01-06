
"""
FICHIER DEFINISSANT LES FONCTIONS D'ACCES AU FICHIER DE PARAMETRISATION
"""

#définition du fichier de parametrisation
fichier="mine_hantee_config.txt" 

def lecture(fichier):
    """
    Fonction permettant de lire le fichier de paramétrage.  

    Prend en entrée :
        - fichier : nom du fichier texte de paramétrage (string, finissant par .txt). 

    Renvoie un dictionnaire contenant l'ensemble des paramètres
    lus dans le fichier.
    """
    f=open(fichier,"r")
    lignes=f.readlines()
    dico_parametres={}
    for ligne in lignes:
        if ligne[0]!='#' and len(ligne)!=0 and ligne[0]!='\n':
            ligne=ligne[:-1]
            ligne_coupe = ligne.split("=")
            dico_parametres[ligne_coupe[0]]=ligne_coupe[1]
    return dico_parametres

def ecriture(fichier, dico_parametres):
    """
    Fonction permettant de remplir / d'actualiser le fichier de paramétrage 
    à partir d'un dictionnaire contenant les nouveaux paramètres.

    Prend en entrée :
        - fichier : nom du fichier texte de paramétrage (string, finissant par .txt). 
        - dico_paramètres : dictionnaire contenant les paramètres à actualiser dans le 
        fichier de paramétrage ainsi que leurs nouvelles valeurs (dictionnaire). 
    """
    f=open(fichier,"r")
    lignes=f.readlines()
    f.close()
    f_new=open(fichier,"w")
    for ligne in lignes:
        if ligne[0]!='#' and len(ligne)!=0 and ligne[0]!='\n':
            #récupération des anciens paramètres
            parametres=ligne[:-1]
            parametres=parametres.split("=")
            if parametres[0] in dico_parametres.keys():
                #comparaison avec les nouveaux paramètres
                #si le paramètre a été changé, on met le nouveau paramètre
                if dico_parametres[parametres[0]]!=parametres[1]:
                    parametres[1]=dico_parametres[parametres[0]]
                    #écriture de la ligne modifiée
                    f_new.write(parametres[0]+"="+str(parametres[1])+"\n")
                else:
                    f_new.write(ligne)
            else:
                f_new.write(ligne)
        else:
            f_new.write(ligne)
    f_new.close()  
    

def enregistrement_inputs(dico):
    global fichier
    """
    Fonction permettant d'enregistrer dans le fichier de paramétrage
    les nouveaux paramètres rentrés par l'utilisateur lors des différentes 
    étapes de paramétrisation. 
    enregistrement_inputs lance également, après l'enregistrement, les fonctions
    suivantes (tests, suite de la paramétrisation ou jeu). 

    Prend en entrée :
        - dico : dictionnaire des paramètres entrés par l'utilisateur 
        lors de la paramétrisation (dictionnaire). 
        L'un des paramètres contenus dans ce dictionnaire (fonction)
        correspond à la fonction suivante appelée après l'enregistrement. 
    """
    
    ecriture(fichier, dico)
    
    if dico['test_null']==True:
        tests_null_inputs(dico)
    elif dico['test_max']==True:
        tests_max_inputs(dico)
    else:
        fonction_suivante=dico['fonction']
        fonction_suivante()

def tests_max_inputs(dico):
    """
    Fonction qui teste la conformité des paramètres renseignés par l'utilisateur. 
    La fonction vérifie si les valeurs maximales des paramètres ne sont pas dépassées.
    Pour deux paramètres (nb_fantomes et nb_fantomes_mission), elle vérifie également
    les valeurs minimales. 
    
    Prend en entrée : 
        - dico : dictionnaire des paramètres entrés par l'utilisateur 
        lors de la paramétrisation (dictionnaire). 
        Contient également : 
            - un paramètre fonction correspond à la fonction suivante appelée.
            - un paramètre fonction_prec correspond à la fonction d'origine.
            - un paramètre test_max indiquant que les maximums n'ont pas encore été testés. 
    
    Crée un dictionnaire contenant les paramètres avec des erreurs ainsi que les erreurs associées. 
    
    Appelle la fonction suivante.
    """
    #initialisation du dictionnaire des maximums autorisés pour chaque paramètre (s'il y en a).
    n=int(dico['dimensions_plateau'])
    nb_fant=(n-2)*(n//2)+(n//2)*(n//2-1)
    dico_max={'nb_fantomes': nb_fant, 'nb_fantomes_mission': nb_fant//int(dico['nb_joueurs']), 
                'nb_joker': 10, 'points_pepite': 50, 'points_fantome': 200, 
                'points_fantome_mission': 200, 'bonus_mission': 500}
    
    #initialisation du dictionnaire des minimums autorisés pour chaque paramètre (s'il y en a).
    dico_min={'nb_fantomes': int(dico['nb_joueurs'])*int(dico['nb_fantomes_mission']), 'nb_fantomes_mission':1}
    
    #initialisation du dictionnaire contenant les erreurs et leurs types. 
    dico_erreurs={}
    
    for cle_input in dico.keys():
        
        #on vérifie si les valeurs renseignées ne dépassent pas le maximum autorisé
        for cle_max in dico_max:
            if cle_input==cle_max:
                if int(dico[cle_input])>dico_max[cle_max]:
                    dico_erreurs[cle_input]='max'
                    erreur='max'
        
        #on vérifie si les valeurs renseignées ne dépassent pas le minimum autorisé
        for cle_min in dico_min:
            if cle_input==cle_min:
                if int(dico[cle_input])<dico_min[cle_min]:
                    dico_erreurs[cle_input]='min'
                    erreur='min'
    
    #s'il n'y a pas d'erreurs, on appelle la fonction suivante. 
    if len(dico_erreurs)==0:
        dico['test_max']=False
        fonction_suivante=dico['fonction']
        if fonction_suivante==dico['fonction_game']:
            fonction_suivante()
        else:
            fonction_suivante(dico)
            
    #s'il y a des erreurs, on appelle la fonction précédente, 
    #en fournissant le dictionnaire des erreurs. 
    else:
        dico_erreurs['type']=erreur
        fonction_prec=dico['fonction_prec']
        fonction_prec(dico_erreurs)
                        
def tests_null_inputs(dico):
    """
    Fonction qui teste la conformité des paramètres renseignés par l'utilisateur. 
    La fonction vérifie si les inputsboxs de la paramétrisation ne sont pas vides. 
    
    Prend en entrée : 
        - dico : dictionnaire des paramètres entrés par l'utilisateur 
        lors de la paramétrisation (dictionnaire). 
        Contient également : 
            - un paramètre fonction correspond à la fonction suivante appelée.
            - un paramètre fonction_prec correspond à la fonction d'origine.
            - un paramètre test_null indiquant que la nullité n'a pas encore été testée. 
    
    Crée un dictionnaire contenant les paramètres avec des erreurs ainsi que les erreurs associées. 
    
    Appelle la fonction suivante.
    """
    #initialisation de la liste qui renseigne les paramètres ne pouvant être nulls. 
    #(seulement ceux pour lesquels il est possible que l'utilisateur entre une valeur nulle).
    L_null=['pseudo_joueur_1', 'pseudo_joueur_2','pseudo_joueur_3','pseudo_joueur_4',
            'nb_fantomes', 'nb_fantomes_mission','nb_joker', 'points_pepite', 
            'points_fantome', 'points_fantome_mission', 'bonus_mission']
    
    #initialisation du dictionnaire contenant les erreurs et leurs types. 
    dico_erreurs={}
    
    for cle_input in dico.keys():
        
        #on vérifie que l'utilisateur a bien renseigné les valeurs
        for cle_null in L_null:
            if cle_null==cle_input:
                if len(dico[cle_input])==0:
                    dico_erreurs[cle_null]='null'
                    
    #s'il n'y a pas d'erreurs, on appelle la fonction suivante.                 
    if len(dico_erreurs)==0:
        dico['test_null']=False
        if dico['test_max']==True:
            fonction_suite=tests_max_inputs
            fonction_suite(dico)
        else:
            fonction_suite=dico['fonction']
            fonction_suite()
            
    #s'il y a des erreurs, on appelle la fonction précédente, 
    #en fournissant le dictionnaire des erreurs. 
    else:
        dico_erreurs['type']='null'
        fonction_prec=dico['fonction_prec']
        fonction_prec(dico_erreurs)
