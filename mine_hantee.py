import numpy as np
import random as rd
from PIL import Image
import matplotlib.pyplot as plt

class carte(object):
    
    def __init__(self, ID, orientation, deplacable=False, id_fantome = 0):
        
        self.id = ID
        self.orientation = orientation
        self.deplacable = deplacable
        self.id_fantome = id_fantome
        self.presence_pepite = True
        
        
class joueur(object):

    def __init__(self, ID, nom, niveau, fantome_target, position):
        self.id = ID
        self.nom = nom
        self.niveau = niveau
        self.fantome_target = fantome_target
        self.position = position
        self.points = 0  





class plateau(object):
    """
    - seuls les N impairs sont acceptés
    """
    def __init__(self, nb_joueurs, liste_noms, liste_niveaux, N):
        self.position=np.zeros([N,N])
        self.id_dernier_fantome=0
        self.dict_cartes={}
        
        compte_id=0
        compte_deplacable=0
        #créer une combinaison des types de cartes
        nb_deplacable=N//2*(N//2+1+N)+1
        #orientations et types de murs de chaque carte
        pool1=[rd.choice([[1,0,1,0],[0,1,0,1]]) for i in range(int(nb_deplacable*13/34))]
        pool2=[rd.choice([[1,1,0,0],[0,1,1,0],[0,0,1,1],[1,0,0,1]]) for i in range(int(nb_deplacable*15/34))]
        pool3=[rd.choice([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]) for i in range(int(nb_deplacable*6/34))]
        pool=pool1+pool2+pool3
        while len(pool)<nb_deplacable:
            pool.append(rd.choice([rd.choice(pool1),rd.choice(pool2),rd.choice(pool3)]))
        pool=np.random.permutation(pool)
        
        for ligne in range(N):
            for colonne in range(N):
                
                self.position[ligne,colonne]=int(compte_id)
                #cases indéplaçables
                if ligne%2 ==0 and colonne%2==0:
                    deplacable=False
                    #cases du milieu où les joueurs commencent la partie
                    if ligne==N//2-1 and colonne==N//2-1:
                        orientation=[0,0,0,1]
                    elif ligne==N//2-1 and colonne==N//2+1:
                        orientation=[1,0,0,0]
                    elif ligne==N//2+1 and colonne==N//2-1:
                        orientation=[0,0,1,0]
                    elif ligne==N//2+1 and colonne==N//2+1:
                        orientation=[0,1,0,0]
                    
                    
                    #cases du coin et des diagonales
                    elif ligne==colonne or colonne==N-1-ligne:
                        if ligne<N//2 and colonne<N//2:
                            orientation=[1,0,0,1]
                        elif ligne<N//2 and colonne>N//2:
                            orientation=[1,1,0,0]
                        elif ligne>N//2 and colonne<N//2:
                            orientation=[0,0,1,1]
                        elif ligne>N//2 and colonne>N//2:
                            orientation=[0,1,1,0]
                    
                    #cases qui font les bords et les autres indéplaçables
                    
                    elif ligne<colonne and N-ligne-1>colonne:
                        orientation=[1,0,0,0]
                    elif ligne<colonne and N-ligne-1<colonne:
                        orientation=[0,1,0,0]
                    elif ligne>colonne and N-ligne-1<colonne:
                        orientation=[0,0,1,0]
                    elif ligne>colonne and N-ligne-1>colonne:
                        orientation=[0,0,0,1]
                
                #cases déplaçables
                else:
                    orientation=pool[compte_deplacable]
                    compte_deplacable+=1
                    deplacable=True

                    
                    
                    
                    
                self.dict_cartes[compte_id]=carte(compte_id, orientation, deplacable)
                compte_id+=1
        
           

                
                
test=plateau(3,["Antoine","Christine","Michel"],0,7)

def affiche_plateau(plateau):
    
    array_image=np.array([plateau.dict_cartes[i].orientation for i in plateau.dict_cartes]).reshape(7,7,4)
    
    
    grid=np.zeros((50*7,50*7,3), 'uint8')
    for ligne in range(len(array_image)):
        for colonne in range(len(array_image)):
            
            subgrid=np.zeros((50,50,3), 'uint8')
            subgrid[..., 0] = np.array([0 for i in range(50*50)]).reshape(50,50)
            subgrid[..., 1] = np.array([150 for i in range(50*50)]).reshape(50,50)
            subgrid[..., 2] = np.array([0 for i in range(50*50)]).reshape(50,50)
            orientation=array_image[ligne,colonne]
            
            for mur in range(4):
                if orientation[mur]==1 and mur==0:
                    subgrid[:5,:,1]=np.array([256 for i in range(5*50)]).reshape(5,50)
                elif orientation[mur]==1 and mur==1:
                    subgrid[:,45:,1]=np.array([256 for i in range(5*50)]).reshape(50,5)
                elif orientation[mur]==1 and mur==2:
                    subgrid[45:,:,1]=np.array([256 for i in range(5*50)]).reshape(5,50)
                elif orientation[mur]==1 and mur==3:
                    subgrid[:,:5,1]=np.array([256 for i in range(5*50)]).reshape(50,5)
                    
            grid[50*ligne:50*(ligne+1),50*colonne:50*(colonne+1),]=subgrid
    
    img = Image.fromarray(grid)
    plt.imshow(img)

affiche_plateau(test)