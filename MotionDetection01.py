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


if __name__ == '__main__':
    
  CAM = 0
  
  try:
    # essaie d'ouvrir le fichier vidéo passé en argument
    # -> si pas d'arg. (ou echec) : essaie d'ouvrir la caméra (0)
    vidin = cv.VideoCapture(argv[1] if len(argv)>1 else CAM)
  except :
    print("unable to read video vidin")
    exit(1)


  VIDEOREAD = False
  
  # Affichage (et récupération) d'infos sur la vidéo
  (height,width,fps,duration) = video_info(vidin)
  frame1 = readframe(vidin,480)
  frame2 = readframe(vidin,480)

  while vidin.isOpened() : 
    diff = frame_diff(frame1,frame2)
    
    cv.imshow('DIFF',1-diff)
    k = cv.waitKey(1000//fps)
    if k == keyb.SPC : VIDEOREAD = not VIDEOREAD
    if k == keyb.ESC : break
    if not VIDEOREAD : continue

    frame1 = frame2
    frame2 = readframe(vidin,480)

vidin.release()
cv.destroyAllWindows()

  