#! /usr/bin/python3
# -------------------------------------------------------- 
# E.Incerti - Université Gustave Eiffel
# eric.incerti@univ-eiffel.fr
# -------------------------------------------------------- 
# Quelques fonctions utilitaires pour OpenCV/pyhton3
# révision 2026/03/06
# -------------------------------------------------------- 

from cvtools import *  # utilitaires divers

#----------------------------------------------------------------------------------
#----------------------------------------------------------------------------------
def video_info(vidin) -> tuple : 
  ''' caractéristiques principales de la video : 
      ATTENTION - par défaut, ce sont des <float32>
     -> selon l'usage il faut les convertir (à l'entier le plus proche)
      -----------------------------------------------------------------
  '''
  # 1) total number of frame
  vlen   = vidin.get(cv.CAP_PROP_FRAME_COUNT) 
  vlen   = int(vlen)
  # 2) frame rate (nbre d'image par seconde)
  # ATTENTION : la valeur de <fps> peut être calculée comme une moyenne (Variable Bit Rate)
  # -> c'est donc par nature un réel
  vfps   = vidin.get(cv.CAP_PROP_FPS)
  vfps   = int(round(vfps))
  # dimensions (largeur/hauteur)
  width  = vidin.get(cv.CAP_PROP_FRAME_WIDTH)
  width  = int(width)
  height = vidin.get(cv.CAP_PROP_FRAME_HEIGHT)
  height = int(height)
  # fourcc ('4 Characters Code'): identification du CoDec video 'h264', 'mp4v', 'xvid', 'divx', 'mpeg' ....
  # -> cf aussi 'Magic Number'
  # OpenCV utilise la suite de CoDec <ffmpeg>
  # -> ce code DOIT être converti en <int32> pour être utilisable
  fourcc = vidin.get(cv.CAP_PROP_FOURCC)
  fourcc = int(fourcc) 
  
  print("-------------------------")
  print("> input video properties : ")
  print("| dimendions (w:"+str(width)+",h:"+str(height)+") - ratio:"+str(width/height))
  print("| total number of frame : ",vlen)
  print("| frame rate : ",vfps,"frame/sec.")
  print("| duration : ",vlen/vfps,"sec.")
  print("| CoDec id : "+chr(fourcc&0xFF)+chr((fourcc>>8)&0xFF)+chr((fourcc>>16)&0xFF)+chr((fourcc>>24)&0xFF))

  return (height,width,vfps,vlen)
  
#----------------------------------------------------------------------------------
#----------------------------------------------------------------------------------
def init_video_recorder(filename:str, fourcc:str, height:int, width:int, fps:int) : 
  ''' Mise en place du flux vidéo de sortie 
      Pour l'encodage vidéo OpenCV fait appel à la suite ffmpeg (et donc la bibliothèque libavcodec) 
      En théorie, on devrait pouvoir choisir entre plusieurs CoDec : 'h264', 'mp4v', 'xvid', 'mpg2' (au moins)
      Mais en pratique, des choses ont changé dans la lib. et les choix sont plus limités
      Ou alors il faut installer ffmpeg "à la main" : sources +  compil avec les options adéquates
      En outre il y a une incohérence (OpenCV ? ffmpeg ? libavcodec ?) puis qu'il faut IMPERATIVEMENT donner
      une extension de format ET un Codec ('fourcc').
      - l'extension (.mp4, .mkv, .avi) fait réference au Conteneur, le 'fourcc' détermine l'algo d'encodage
      => Les combinaisons sont au final assez limitées :
      Conteneurs: 
      - .mp4 .mov -> QuickTime (Apple)
      - .mkv -> Matroska  (OpenSource ?)
      - .avi -> DivX (Obsolete) 
      CoDec : mp4v (.mp4|.mkv) ou xvid (.avi)
      Les encodeurs '{h|x}264/{h|x}265'  (bien meilleurs) sont passés sous licence et ne sont plus disponibles en free 
      => Choisir "output.mkv" avec "mp4v"
  '''
  try:
    # choix du CoDec d'enregistrement 
    codec  = cv.VideoWriter_fourcc(*fourcc)
    vidout = cv.VideoWriter(filename, codec, fps, (width, height))
    assert vidout.isOpened()
  except:
    print("\nunsupported codec or file extension")
    print(filename)
    print(fourcc)
    exit(2)
  print("--------------------------  ")
  print("> output video properties : ")
  print("| dimendions (w:"+str(width)+",h:"+str(height)+")")
  print("| frame rate :",24,"frame/sec.")
  # pour voir le CoDec réellement utilisé par ffmpeg 
  codec = vidout.get(cv.CAP_PROP_FOURCC)
  codec = int(codec) 
  print("| CoDec id : "+chr(codec&0xFF)+chr((codec>>8)&0xFF)+chr((codec>>16)&0xFF)+chr((codec>>24)&0xFF))
  return vidout

#----------------------------------------------------------------------------------
#----------------------------------------------------------------------------------
def readframe(video:cv.VideoCapture, height:int=0, width:int=0)->np.ndarray :
  '''
    lecture de la frame courante du flux vidéo d'entrée, avec redimensionnement éventuel
    - si c'est une vidéo sur fichier : lecture en boucle
    - si c'est la camera, passe les images foireuses éventuelles
  '''
  (ok,frame) = video.read()
  if not ok : 
    vidin.set(cv.CAP_PROP_POS_FRAMES, 0)
    return readframe(video,height,width)
  if height==0 : return frame
  return resize_image(frame,height)
  
