#! /usr/bin/python3
# -------------------------------------------------------- 
# E.Incerti - Université Gustave Eiffel
# eric.incerti@univ-eiffel.fr
# -------------------------------------------------------- 
# Quelques fonctions utilitaires pour OpenCV/pyhton3
# révision 2026/03/06
# -------------------------------------------------------- 

# libs standard --------
from sys  import argv   # pour les arguments de la ligne de commande
from time import time   # pour évaluer les temps de calcul
from os   import system # pour appel à la fonction <system>
# NumPy & OpenCV2
import numpy as np      # parcequ'on ne fait pas d'OpenCV sans Numpy ...
import cv2   as cv

# mode verbeux
VERBOSE = False

# dimension par défaut - redimensionnement automatique
SCREENWIDTH  = 1024
SCREENHEIGHT = 768
# détection d'événement scrollbar
SCROLL_EVENT = True

# XTerm colors --------
class xtc :
    DFLT  = '\033[0m'  # reset to default
    BOLD  = '\033[1m'  # bold font
    ULIN  = '\033[4m'  # underline
    COL1  = '\033[91m' # 6 xterm colors 
    COL2  = '\033[92m' # (depend on xterm config.)
    COL3  = '\033[93m'
    COL4  = '\033[94m'
    COL5  = '\033[95m'
    COL6  = '\033[96m'
# ---------------------

#---------------------------------------------------------------------------------
def usage(scriptname, arguments):
  '''  '''
  print(xtc.BOLD+xtc.COL1+"\t usage"+xtc.DFLT+xtc.COL1+" : py",scriptname,arguments)
  print(xtc.COL2+"  > --------------------------------------------------")
  print("  > OpenCV  version "+cv.__version__)
  print("  > NumPy   version "+np.__version__)
  print("  > --------------------------------------------------"+xtc.DFLT)
  exit(1)

#----------------------------------------------------------------------------------
# ScrollBars
#----------------------------------------------------------------------------------
class Scroll :
  ''' '''
  # ne sert à rien, mais est indispensable....
  def on_scroll(self,x) : return x

  # constructeur par défaut
  def __init__(self,name:str,vmin:float,v0:float,vmax:float,step:float,window:str) -> None :
    ''' * self : le Scroll
        * name : son nom (dans la fenêtre) 
        * vmin-vmax : intervalle de valeurs
        * v0 : valeur initiale 
        * N  : nbre de subdivisions de [vmin-vmax] 
               N=1 => Scroll "Booléen" 
        * window : la fenêtre support du Scroll
    '''
    assert ((vmin<=v0) and (v0<=vmax) and step>0), print("erreur definition Scroll("+nom+")")
    nbsubdiv = int((vmax-vmin)/step)
    self.name = name
    self.win  = window
    self.vmin = float(vmin)
    self.vmax = float(vmax)
    self.step = float(step)
    self.curr = int((nbsubdiv*(v0-vmin)/(vmax-vmin)))
    self.old  = self.curr
    self.evt  = False
    # creation
    cv.namedWindow(window,cv.WINDOW_NORMAL)
    cv.createTrackbar(name,self.win,self.curr,nbsubdiv,self.on_scroll)    

  # détection d'événement
  def event(self) -> bool :
    global SCROLL_EVENT
    self.curr = cv.getTrackbarPos(self.name,self.win)
    # changement de valeur
    if self.curr != self.old : 
      self.old = self.curr
      SCROLL_EVENT = self.evt = True
    return self.evt
 
  # valeur courante (format : np.float32)
  def value(self) -> np.float32 :
    ''' '''
    # évt. déjà "consommé" -> false
    self.evt = False
    # mise à jour
    return ((self.vmin+self.curr*self.step))

# ---------------------
# INTERRUPTIONS CLAVIER : quelques touches prédéfinies
# ---------------------
class keyb :
    # touches spéciales
    BS    =  8 # Back-Space
    TAB   =  9 # Tabulation
    CR    = 13 # Entrée
    ESC   = 27 # Echap.
    SPC   = 32 # Barre Espace
    # pavé fléché
    Larw1 = 81 # Left  Arrow
    Uarw1 = 82 # Up    Arrow
    Rarw1 = 83 # Right Arrow
    Darw1 = 84 # Down  Arrow    
    PgUp1 = 85 # Page-Up
    PdDw1 = 86 # Page-Down
    # pavé num SANS verouillage num
    Larw2 = 150 # Left  Arrow '4'
    Uarw2 = 151 # Up    Arrow '8'
    Rarw2 = 152 # Right Arrow '6'
    Darw2 = 153 # Down  Arrow '2'   
    PgUp1 = 154 # Page-Up     '9'
    PdDw1 = 155 # Page-Down   '3'  
    PLUS  = 43
    MINUS = 45

#---------------------------------------------------------------------------------
def get_key(message:str) -> str :
  ''' attend une saisie clavier :
      * <ESC> : sortie propre (fermeture + signal <exit>)
      * sinon : renvoie le caractère saisi
  '''
  print(" wait.for.key >"+message)
  k = cv.waitKey(0)
  if k == keyb.ESC :
    cv.destroyAllWindows()
    exit()
  return chr(k)

#---------------------------------------------------------------------------------
def break_loop() -> bool :
  ''' attend que l'utilisateur presse <ESC> pour sortir de la boucle '''
  global SCROLL_EVENT
  # évt. déjà "consommé" -> false
  SCROLL_EVENT = False
  k = cv.waitKey(1)
  if k == 27 : return True
  return False

#---------------------------------------------------------------------------------
# FONCTIONS IMAGE
#---------------------------------------------------------------------------------
def get_image_dim(img:np.ndarray) -> tuple :
  ''' donne les dimensions (height|width) de l'image ainsi que le nombre de canaux 
      GRAYSCALE               : 1
      GRAYSCALE + ALPHA CHAN  : 2
      RGB                     : 3
      RGB + ALPHA CHAN (RGBA) : 4
  '''
  h = img.shape[0]
  w = img.shape[1]
  c = 1 if len(img.shape)==2 else img.shape[2]
  return (h,w,c)

#---------------------------------------------------------------------------------
def resize_image(img:np.ndarray,height:int=SCREENHEIGHT,width:int=SCREENWIDTH)->np.ndarray :
  ''' taille de la fenêtre pour retailler les images trop grandes
      utilisable directement au chargement ou simplement à l'affichage
  '''
  global VERBOSE
  xfactor = min(1.0,width /img.shape[1])
  yfactor = min(1.0,height/img.shape[0])
  if (xfactor==1.0 and yfactor==1.0) : return img
  w = int(img.shape[1]*min(xfactor,yfactor))
  h = int(img.shape[0]*min(xfactor,yfactor))
  dim = (w,h)
  if VERBOSE : 
    print("tailles de l'image ajustée : ("+str(img.shape[0])+","+str(img.shape[1])+")->("+str(h)+","+str(w)+")")
  return cv.resize(img,dim,interpolation = cv.INTER_CUBIC)

#---------------------------------------------------------------------------------
def open_image(imgname:str, FLOAT01:bool=False, TRUESIZE:bool=False, ALLCHAN:bool=False) -> tuple :
  ''' ouverture image
      teste si une image est passée en paramètre
        sinon ouvre une image par défaut
          sinon exit
      FLOAT01  flag : si <vrai>, converti l'image en float32 dans ]0.,1.[, sinon : ubyte [0,255]
      ALLCHAN  flag : si <vrai>, ouvre en RGBA, si <faux> (default) converti en <RGB>
                      le flag cv.IMREAD_ANYCOLOR peut avoir d'autres effets de bords -> cf. manuel !!!
      TRUESIZE flag : si <vrai>, conserve les tailles originales, si <faux> (default), ajuste la taille 
                      si des tailles (height|width) sont données en paramètres retaillage à ces dimensions.
                      sinon, si l'image est trop grande, retaillage automatique (SCREENHEIGHT*SCREENWIDTH)
        sauf si 'height' est donné à 0 => là, c'est les tailles originales qui sont conservées
  '''
  global VERBOSE

  try :     # 1) nom lu directement dans les paramètre ou sur la ligne de commande  
    img = cv.imread(imgname, cv.IMREAD_ANYCOLOR if ALLCHAN else None)
    assert img is not None, print("  > unable top open "+imgname+" -> use default input")
  except : 
    try :   # 2) saisie utilisateur
      imgname = input("  > filename : ")
      img = cv.imread(imgname, cv.IMREAD_ANYCOLOR if ALLCHAN else None)
      assert img is not None, print("  > unable top open "+imgname+" -> exit")
    except : 
      try :   # 3) image par défaut
        imgname = "../IMG/OpenCV320.jpg"
        img = cv.imread(imgname, cv.IMREAD_ANYCOLOR if ALLCHAN else None)
        assert img is not None, print("  > unable top open "+imgname+" -> enter filename")
      except : 
        exit(1)

  if VERBOSE : 
    print("image chargée : ",imgname)
  
  # redimmensionne l'image pour ajuster à la fenêtre
  if not TRUESIZE : img = resize_image(img,min(SCREENHEIGHT,img.shape[0]),min(SCREENWIDTH,img.shape[1]))

  if not FLOAT01 : return (imgname,img)
  # conversion 3x[0-255] (uint8) -> 3x[0.-1.] (float32)
  # img = np.float32(img)/255.
  # version alternative, plus robuste -> dans ]0., 1.[ (bords exclus)
  # permet d'éviter certains effets "inverse-video" et "division par 0.
  img = (0.9999+np.float32(img))/256.
  return (imgname,img)


#---------------------------------------------------------------------------------
# HISTOGRAMMES
#---------------------------------------------------------------------------------
def histo_1(img) -> (np.array,float) :
  ''' renvoie l'histogramme [0,256] d'une image en niveau de gris 
      sous la forme d'un np.array simple
      la fonction renvoie également un coefficient de calibration
      pour que la valeur max. de l'histogramme corresponde à la 
      hauteur de l'image
  '''
  (h,_,_)=get_image_dim(img)
  img = np.uint8(img*255)
  hist = cv.calcHist([img],[0],None,[256],[0,256])
  hist = np.ravel(hist,'C')
  return (hist,h/np.max(hist))

def draw_histo_1( hist,calib,col,H)-> None :
  ''' trace l'histogramme <hist> calibré par <calib>, 
      avec la couleur <col>, sur l'image BGR <H> 
  '''
  (h,w,_) = get_image_dim(H)
  (u,v) = (0,0)
  a = w/256.
  for i in range(256) : 
    x = int(i*a)
    y = int(h-hist[i]*calib)
    cv.line(H,(u,v),(x,y),col,2)
    (u,v) = (x,y)

def full_histo_3(img) :
  ''' renvoie directement une image (même tailles que l'entrée) 
      avec le tracé sur fond blanc des histogrammes des 3 plans B,G,R
  '''
  (h,w,n) = get_image_dim(img)
  assert n==3, print("image must have 3 layers")

  (B,G,R) = cv.split(img)
  # les 3 histogrammes
  (hB,calB) = histo_1(B)
  (hG,calG) = histo_1(G)
  (hR,calR) = histo_1(R)
  # le coeff de calibrage global
  calib = min(calB,calG,calR)
  # on part d'une image vide, blanche
  H = np.ones_like(img)
  draw_histo_1(hB,calib,(255,0,0),H)
  draw_histo_1(hG,calib,(0,255,0),H)
  draw_histo_1(hR,calib,(0,0,255),H)
  return H
