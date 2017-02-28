# https://manifest.googlevideo.com/api/manifest/hls_playlist/id/QzQnFY6CioA.4/itag/94/source/yt_live_broadcast/requiressl/yes/ratebypass/yes/live/1/cmbypass/yes/goi/160/sgoap/gir%3Dyes%3Bitag%3D140/sgovp/gir%3Dyes%3Bitag%3D135/hls_chunk_host/r3---sn-5jucgv5qc5oq-cagz.googlevideo.com/gcr/in/playlist_type/DVR/mm/32/mn/sn-5jucgv5qc5oq-cagz/ms/lv/mv/m/pcm2cms/yes/pl/19/dover/6/upn/wEjl54lYOmI/beids/%5B9452306%5D/mt/1488192793/ip/106.51.66.100/ipbits/0/expire/1488214416/sparams/ip,ipbits,expire,id,itag,source,requiressl,ratebypass,live,cmbypass,goi,sgoap,sgovp,hls_chunk_host,gcr,playlist_type,mm,mn,ms,mv,pcm2cms,pl/signature/873ED3D7E6ECF5EFC4E2DEAAC44AB471A17254C4.2C291494DC98E9D622CC1E7B5FD1DF79B17F87A8/key/dg_yt0/playlist/index.m3u8


VIDEO_URL = "https://manifest.googlevideo.com/api/manifest/hls_playlist/id/l5vUW5ZRHK0.0/itag/94/source/yt_live_broadcast/requiressl/yes/ratebypass/yes/live/1/cmbypass/yes/goi/160/sgoap/gir%3Dyes%3Bitag%3D140/sgovp/gir%3Dyes%3Bitag%3D135/hls_chunk_host/r2---sn-5jucgv5qc5oq-cagz.googlevideo.com/gcr/in/playlist_type/DVR/mm/32/mn/sn-5jucgv5qc5oq-cagz/ms/lv/mv/m/pl/19/dover/6/upn/WqYvM_XDWOM/beids/%5B9452306%5D/mt/1488196396/ip/106.51.66.100/ipbits/0/expire/1488218103/sparams/ip,ipbits,expire,id,itag,source,requiressl,ratebypass,live,cmbypass,goi,sgoap,sgovp,hls_chunk_host,gcr,playlist_type,mm,mn,ms,mv,pl/signature/252042428928E4725F652130CC6C7E97B35F0B87.339052FF9F19DC67DFCD137B184856DF60CCC64D/key/dg_yt0/playlist/index.m3u8"

VIDEO_URL = 'http://95.161.181.202/mjpg/video.mjpg'


# VIDEO_URL = 'https://hddn01.skylinewebcams.com/live.m3u8?a=h784s5t5tp26g66uc86msn2he4'
import cv2
import subprocess as sp
import numpy
# Cascade
body_cascade = cv2.CascadeClassifier('haarcascade_fullbody.xml')
upperbody_cascade = cv2.CascadeClassifier('haarcascade_upperbody.xml')
lowerbody_cascade = cv2.CascadeClassifier('haarcascade_lowerbody.xml')

body_count = 0

FFMPEG_BIN = '/usr/bin/ffmpeg'
cv2.namedWindow("GoPro",cv2.WINDOW_AUTOSIZE)

pipe = sp.Popen([ FFMPEG_BIN, "-i", VIDEO_URL,

           "-an",   # disable audio
           "-f", "image2pipe",
           "-pix_fmt", "bgr24",
           "-vcodec", "rawvideo", "-"],
           stdin = sp.PIPE, stdout = sp.PIPE, bufsize=10**9)

font = cv2.FONT_HERSHEY_SIMPLEX
while True:
    raw_image = pipe.stdout.read(640*480*3) # read 640*480*3 bytes (= 1 frame)
    image =  numpy.fromstring(raw_image, dtype='uint8').reshape((480,640,3))

    # detection
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    bodies = body_cascade.detectMultiScale(gray, 1.2, 1)
    upper_bodies = upperbody_cascade.detectMultiScale(gray, 1.2, 1)
    lower_bodies = lowerbody_cascade.detectMultiScale(gray, 1.2, 1)

    for (x,y,w,h) in bodies:
        cv2.rectangle(image,(x,y),(x+w,y+h),(255,0,0),2)
        # roi_gray = gray[y:y+h, x:x+w]
        # roi_color = img[y:y+h, x:x+w]
        body_count += 1
        cv2.putText(image, str(body_count),(x+w,y), font, 0.5,(255,255,255),2,cv2.LINE_AA)
        
    # for (x,y,w,h) in upper_bodies:
    #     cv2.rectangle(image,(x,y),(x+w,y+h),(255,0,0),2)
    #     # roi_gray = gray[y:y+h, x:x+w]
    #     # roi_color = img[y:y+h, x:x+w]
    #     body_count += 1
        

    # for (x,y,w,h) in lower_bodies:
    #     cv2.rectangle(image,(x,y),(x+w,y+h),(255,0,0),2)
    #     # roi_gray = gray[y:y+h, x:x+w]
    #     # roi_color = img[y:y+h, x:x+w]
    #     body_count += 1
        
    cv2.imshow("GoPro",image)
    if cv2.waitKey(5) == 27:
        break

cv2.destroyAllWindows()