set -e
G="eq=contrast=1.1:saturation=0.82:brightness=-0.03,colorbalance=rs=-0.05:gs=0:bs=0.07:rh=0.07:gh=0.02:bh=-0.06"
FIN="vignette=PI/4.5,noise=alls=5:allf=t,fps=30,format=yuv420p"
# seg name src ss dur cropW cropH cropX cropY
seg(){ n=$1; s=$2; ss=$3; d=$4; cw=$5; ch=$6; cx=$7; cy=$8; ov=$9
ffmpeg -loglevel error -y -ss $ss -t $d -i src/$s.mp4 -loop 1 -t $d -i ov/$ov.png -filter_complex "\
[0:v]split[a][b];\
[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=30:2,eq=brightness=-0.18,$G[bg];\
[b]crop=$cw:$ch:$cx:$cy,scale=1080:1080:force_original_aspect_ratio=decrease,$G[fg];\
[bg][fg]overlay=(W-w)/2:420[v];[v][1:v]overlay=0:0,$FIN" -an -t $d seg/$n.mp4; }
# full-bleed segment
full(){ n=$1; s=$2; ss=$3; d=$4; ov=$5
ffmpeg -loglevel error -y -ss $ss -t $d -i src/$s.mp4 -loop 1 -t $d -i ov/$ov.png -filter_complex "\
[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,$G,eq=brightness=-0.22,boxblur=4:1[bg];[bg][1:v]overlay=0:0,$FIN" -an -t $d seg/$n.mp4; }
full 0 52101 0.3 2.2 hook
seg 1 16201 0.5 3 720 720 220 0 s1
seg 2 739 1 3 1280 720 0 0 s2
seg 3 44438 1.6 3 720 720 260 0 s3
seg 4 44437 14 3 720 720 0 0 s4
seg 5 5060 5 3 900 720 300 0 s5
seg 6 52101 0 3 560 560 330 160 s6
full 7 44440 2 2.5 end
printf "file 'seg/%s.mp4'\n" 0 1 2 3 4 5 6 7 > list.txt
ffmpeg -loglevel error -y -f concat -safe 0 -i list.txt -c:v libx264 -crf 20 -preset medium -movflags +faststart hipreel.mp4
