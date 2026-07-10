#! /usr/bin/python3.7.1
from cvtools    import *  # utilitaires divers
from videotools import *  # utilitaires video
  
#°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°
#
#°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°*°
if __name__ == '__main__':
    
  try:
    # essaie d'ouvrir le fichier vidéo passé en argument
    # -> si pas d'arg. (ou echec) : essaie d'ouvrir la caméra (0)
    vidin = cv.VideoCapture(argv[1] if len(argv)>1 else 0)
  except :
    print("unable to read video vidin")
    exit(1)

  # Affichage (et récupération) d'infos sur la vidéo
  (height,width,fps,duration) = video_info(vidin)

  
  # caractéristiques du flux de sortie
  # réduction du frame-rate
  jump  = int(2) 
  fps   = fps/jump
  # facteur d'échelle et tailles de sortie
  scale  = 0.5
  hout = int(round(height*scale))
  wout = int(round(width *scale))
 
   # Initialisation de l'enregistreur pour la sortie [ cf. videotools.py ]
  vidout = init_video_recorder("output.avi", "xvid", hout, wout, fps)
  
  # plans de découpage 1/2
  Xcut = wout//2
  # boucle de lecture de la vidéo 
  while vidin.isOpened():
    # pour traiter 1 image sur <jump>
    for _ in range(jump) : frame = readframe(vidin,hout,wout)
    
    # découpage 
    Lpart = frame[ :,    :Xcut ,: ] # moitié gauche
    Rpart = frame[ :,Xcut:     ,: ] # moitié droite
    
    frame = cv.hconcat([Lpart,255-Rpart])

    # affichage ... 
    cv.imshow("out",frame)
    # ... et enregistrement vidéo
    vidout.write(frame)

    # --------------------------------------------------------------
    k = cv.waitKey(int(1000/fps))
    if k == keyb.ESC : break
    if k == keyb.SPC : get_key('<SPACE> to continue')

  # fermeture des flux d'entrée/sortie
  vidin.release()
  vidout.release()
