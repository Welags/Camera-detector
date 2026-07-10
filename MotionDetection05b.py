#! /usr/bin/python3.7.1
from cvtools    import * # utilitaires divers
from videotools import * # utilitaires video
from datetime import datetime 

  
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
    vidin = cv.VideoCapture(argv[1] if len(argv)>1 else 0)
  except :
    print("unable to read video vidin")
    exit(1)

  VIDEOREAD = False

  (height,width,fps,duration) = video_info(vidin)
  frame1 = readframe(vidin,480)
  frame2 = readframe(vidin,480)

  cv.namedWindow("CTRL")
  MIN= 0.01
  V0 = 1.0
  MAX = 2.0 
  PAS = 0.01
  Gbar = Scroll('gamma',MIN,0.71,MAX,PAS,'CTRL')

  Kbar = Scroll('seuil',MIN,0.04,1.0,PAS,'CTRL')

  KerBar = Scroll('kernel',0,2,5,1,'CTRL')
  

  AreaBar = Scroll('area', 50, 500, 5000, 50, 'CTRL')


  taille_buffer = int(fps) 
  tampon_roulant = []
  filming = False
  frames = 0
  vidout = None 

  while vidin.isOpened() :

    Gbar.event()
    Kbar.event()
    KerBar.event()
    AreaBar.event()

    k = int(KerBar.value())
    ksize = 2*k +1
    kernel = np.ones((ksize,ksize),np.uint8())
    gamma = Gbar.value()
    seuil = Kbar.value()
    area = AreaBar.value() 


    diff = frame_diff(frame1,frame2)

    diffg = diff_gamma_inf(diff,gamma)

    diffm = diff_binary_median(diffg,seuil)
    
    img = cv.morphologyEx(diffm,cv.MORPH_OPEN,kernel)
    img = np.uint8(255*img)
    (cont,_) = cv.findContours(img,cv.RETR_EXTERNAL,cv.CHAIN_APPROX_SIMPLE)


    t = frame2.copy()
    detect = False

    if len(cont) > 0:
        aire = [cv.contourArea(c) for c in cont]
        max_aires = max(aire)

        if max_aires > area:
            max_i = aire.index(max_aires)
            contour = cont[max_i]

            x, y, w, h = cv.boundingRect(contour)
            cv.rectangle(t, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            detect = True


    texte_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cv.putText(t, texte_date, (10, 30), cv.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    if detect:
        cv.putText(t, "MOVMENT DETECTED", (10, 60), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    else:
        cv.putText(t, "NO MOVMENT", (10, 60), cv.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)


    if detect:
        frames = 0 
        if not filming:
            filming = True
            
            nom_fichier = datetime.now().strftime("video_%Y%m%d_%H%M%S.avi")
            h_out, w_out, _ = t.shape
            
            vidout = init_video_recorder(nom_fichier, "xvid", h_out, w_out, int(fps))
            
            for f in tampon_roulant:
                vidout.write(f)
    else:
        if filming:
            frames += 1
            if frames >= taille_buffer:
                filming = False
                vidout.release()
                vidout = None


    if filming and vidout is not None:
        vidout.write(t)
        cv.putText(t, "REC", (w_out - 100, 30), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    tampon_roulant.append(t.copy())
    if len(tampon_roulant) > taille_buffer:
        tampon_roulant.pop(0)

    cv.imshow('contour',t)
    
    k = cv.waitKey(1000//fps)
    if k == keyb.SPC : VIDEOREAD = not VIDEOREAD
    if k == keyb.ESC : break
    if not VIDEOREAD : continue

    frame1 = frame2
    frame2 = readframe(vidin,480)

if vidout is not None:
    vidout.release()
vidin.release()
cv.destroyAllWindows()