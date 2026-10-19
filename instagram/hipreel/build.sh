set -e
G="eq=contrast=1.1:saturation=0.82:brightness=-0.05,colorbalance=rs=-0.05:bs=0.07:rh=0.07:gh=0.02:bh=-0.06"
FIN="vignette=PI/5,noise=alls=5:allf=t,fps=30,format=yuv420p"
D=6
strip(){ echo "[$1:v]trim=start=$2:duration=$D,setpts=PTS-STARTPTS,fps=30,crop=$3:$4:$5:$6,scale=1080:640,$G[s$1]"; }
page(){ n=$1; ov=$2; shift 2
 a=($@)
 ffmpeg -loglevel error -y -i src/${a[0]}.mp4 -i src/${a[6]}.mp4 -i src/${a[12]}.mp4 -loop 1 -t $D -i ov/$ov.png -filter_complex "\
$(strip 0 ${a[1]} ${a[2]} ${a[3]} ${a[4]} ${a[5]});$(strip 1 ${a[7]} ${a[8]} ${a[9]} ${a[10]} ${a[11]});$(strip 2 ${a[13]} ${a[14]} ${a[15]} ${a[16]} ${a[17]});\
[s0][s1][s2]vstack=3[v];[v][3:v]overlay=0:0,$FIN" -an -t $D seg/$n.mp4; }
full(){ ffmpeg -loglevel error -y -ss $3 -t $4 -i src/$2.mp4 -loop 1 -t $4 -i ov/$5.png -filter_complex "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,$G,eq=brightness=-0.22,boxblur=4:1[bg];[bg][1:v]overlay=0:0,$FIN" -an -t $4 seg/$1.mp4; }
full 0 52101 0.3 2.2 hook
page 1 p1  887 0 1215 720 30 0   5388 1 1215 720 30 0   21273 0.5 1215 720 30 0
page 2 p2  40138 2 1215 720 0 0   739 1 1215 720 30 0   52101 0 760 450 230 220
full 3 44440 2 2.5 end
printf "file 'seg/%s.mp4'\n" 0 1 2 3 > list.txt
ffmpeg -loglevel error -y -f concat -safe 0 -i list.txt -c:v libx264 -crf 20 -preset medium -movflags +faststart hipreel.mp4
