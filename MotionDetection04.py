#! /usr/bin/python3.7.1
from cvtools    import *  # utilitaires divers
from videotools import *  # utilitaires video
  
#°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°
#
#°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°

def frame_diff(frame1:np.ndarray,frame2:np.ndarray) -> np.ndarray :
    frame1 = cv.cvtColor(frame1,cv.COLOR_BGR2GRAY)
    frame2 = cv.cvtColor(frame2,cv.COLOR_BGR2GRAY)
    diff = cv.absdiff(frame2,frame1)
    diff = diff.astype(np.float32)/255
    return diff

def diff_gamma_zero(diff:np.ndarray,gamma:float)->np.ndarray:
    g = 1-diff**gamma
    return g

def diff_gamma_inf(diff:np.ndarray,gamma:float)->np.ndarray:
    g = 1./max(gamma,0.00000001)
    return diff**g
def diff_binary_median(diff:np.ndarray,seuil:float=0)->np.ndarray:
    diff = cv.medianBlur(diff,3)
    (_,tmp) = cv.threshold(diff,seuil,1,cv.THRESH_BINARY)
    return tmp
if __name__ == '__main__':
    
  
  try:
    # essaie d'ouvrir le fichier vidéo passé en argument
    # -> si pas d'arg. (ou echec) : essaie d'ouvrir la caméra (0)
    vidin = cv.VideoCapture(argv[1] if len(argv)>1 else 0)
  except :
    print("unable to read video vidin")
    exit(1)

  
  VIDEOREAD = False
  # Affichage (et récupération) d'infos sur la vidéo
  (height,width,fps,duration) = video_info(vidin)
  frame1 = readframe(vidin,480)
  frame2 = readframe(vidin,480)

  cv.namedWindow("CTRL")
  MIN= 0.01
  V0 = 1.0
  MAX = 2.0 
  PAS = 0.01
  Gbar = Scroll('gamma',MIN,V0,MAX,PAS,'CTRL')

  Kbar = Scroll('seuil',MIN,0.5,1.0,PAS,'CTRL')

  KerBar = Scroll('kernel',0,1,5,1,'CTRL')


  
  while vidin.isOpened() :


    Gbar.event()
    Kbar.event()
    KerBar.event()
    k = int(KerBar.value())
    ksize = 2*k +1
    kernel = np.ones((ksize,ksize),np.uint8())
    gamma = Gbar.value()
    seuil = Kbar.value()
    diff = 1 - frame_diff(frame1,frame2)

    diffg = diff_gamma_inf(diff,gamma)

    diffm = diff_binary_median(diffg,seuil)
    
    #img = cv.erode(diffm,kernel,iteration=1)
    #img = cv.dilate(img,kernel,iteration=1)
    img = cv.morphologyEx(diffm,cv.MORPH_OPEN,kernel)
    img = np.uint8(255*img)
    (cont,_) = cv.findContours(img,cv.RETR_EXTERNAL,cv.CHAIN_APPROX_SIMPLE)

    t = cv.cvtColor(img,cv.COLOR_GRAY2BGR)


    aire = [cv.contourArea(c) for c in cont]
    max_aires = max(aire)
    max_idx = aire.index(max_aires)
    cv.drawContours(t,cont,-1,(0,255,0),2)

    

    cv.imshow('contour',t)
    k = cv.waitKey(1000//fps)
    if k == keyb.SPC : VIDEOREAD = not VIDEOREAD
    if k == keyb.ESC : break
    if not VIDEOREAD : continue

    frame1 = frame2
    frame2 = readframe(vidin,480)

vidin.release()
cv.destroyAllWindows()

  
#version 3 = elle passe en binaire