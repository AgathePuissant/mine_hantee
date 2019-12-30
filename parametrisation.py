
"""
FICHIER DEFINISSANT LES FONCTIONS D'ACCES AU FICHIER DE PARAMETRISATION
"""

#définition du fichier de parametrisation
fichier="mine_hantee_config.txt" 

#lecture du fichier de paramétrage

def lecture(fichier):
    """
    fonction qui lit le fichier de paramètres
    et retourne le dictionnaire des paramètres
    (si l'utilisateur modifie directement le fichier des paramètres)
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

#écriture du fichier de paramétrage

def ecriture(fichier, dico_parametres):
    """
    fonction qui remplit le fichier de paramètres à partir du dictionnaire des nouveaux paramètres 
    donnée en entrée dans dico_parametres. 
    (si l'utilisateur modifie les paramètres vie l'interface de jeu (avancée ou non))
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
    fonction d'enregistrement des paramètres inputs
    dico : dictionnaire avec les paramètres, 
    dont un paramètre (fonction) correspond à la fonction suivante appelée. 
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
    fonction qui teste la conformité des paramètres  renseignés par les joueurs. 
    dico : dictionnaire avec les paramètres, 
    dont un paramètre (fonction) correspond à la fonction suivante appelée.
    dont un paramètre (fonction_prec) correspond à la fonction d'origine. 
    Les types ne sont pas testés car ils sont forcés lors de l'entrée de l'utilisateur.
    La fonction vérifie si les valeurs maximale ne sont pas dépassées. 
    """
    
    #dictionnaire des maximums autorisés pour chaque paramètre (s'il y en a).
    n=int(dico['dimensions_plateau'])
    nb_fant=(n-2)*(n//2)+(n//2)*(n//2-1)
    dico_max={'nb_fantomes': nb_fant, 'nb_fantomes_mission': nb_fant//int(dico['nb_joueurs']), 
                'nb_joker': 10, 'points_pepite': 50, 'points_fantome': 200, 
                'points_fantome_mission': 200, 'bonus_mission': 500}
    
    dico_erreurs={}
    
    for cle_input in dico.keys():
        
        #on vérifie si les valeurs renseignées ne dépassent pas le maximum autorisé
        for cle_max in dico_max:
            if cle_input==cle_max:
                if int(dico[cle_input])>dico_max[cle_max]:
                    dico_erreurs[cle_input]='max'
                    
    if len(dico_erreurs)==0:
        dico['test_max']=False
        fonction_suivante=dico['fonction']
        if fonction_suivante==dico['fonction_game']:
            fonction_suivante()
        else:
            fonction_suivante(dico)
    else:
        dico_erreurs['type']='max'
        fonction_prec=dico['fonction_prec']
        fonction_prec(dico_erreurs)
                        
def tests_null_inputs(dico):
    """
    fonction qui teste la conformité des paramètres  renseignés par les joueurs. 
    dico : dictionnaire avec les paramètres, 
    dont un paramètre (fonction) correspond à la fonction suivante appelée.
    dont un paramètre (fonction_prec) correspond à la fonction d'origine. 
    Les types ne sont pas testés car ils sont forcés lors de l'entrée de l'utilisateur.
    La fonction vérifie que les inputsboxs ne sont pas vide et renvoie un message d'erreur si c'est le cas. 
    """
    
    #liste qui renseigne les paramètres ne pouvant être nulls. 
    #(seulement ceux pour lesquels il est possible que l'utilisateur entre une valeur nulle).
    L_null=['pseudo_joueur_1', 'pseudo_joueur_2','pseudo_joueur_3','pseudo_joueur_4',
            'nb_fantomes', 'nb_fantomes_mission','nb_joker', 'points_pepite', 
            'points_fantome', 'points_fantome_mission', 'bonus_mission']
    
    dico_erreurs={}
    
    for cle_input in dico.keys():
        
        #on vérifie que l'utilisateur a bien renseigné les valeurs
        for cle_null in L_null:
            if cle_null==cle_input:
                if len(dico[cle_input])==0:
                    dico_erreurs[cle_null]='null'
                    
    if len(dico_erreurs)==0:
        dico['test_null']=False
        if dico['test_max']==True:
            fonction_suite=tests_max_inputs
            fonction_suite(dico)
        else:
            fonction_suite=dico['fonction']
            fonction_suite()
    else:
        dico_erreurs['type']='null'
        fonction_prec=dico['fonction_prec']
        fonction_prec(dico_erreurs)