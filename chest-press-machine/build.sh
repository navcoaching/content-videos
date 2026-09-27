#!/usr/bin/env bash
# Rebuild the Chest Press Machine edit from the raw iPhone clips.
# Usage: put IMG_2880..2883.MOV in work/src/, then ./build.sh
# Needs: ffmpeg with libzimg (zscale) + libx264, python3 with opencv-python-headless, pillow (raqm), numpy.
set -euo pipefail
cd "$(dirname "$0")"
FFMPEG=${FFMPEG:-ffmpeg}
mkdir -p work/sdr fonts out

# 1) HLG HDR (iPhone) -> SDR bt709, rotation applied automatically.
for n in 2880 2881 2882 2883; do
  [ -f work/sdr/$n.mp4 ] && continue
  "$FFMPEG" -hide_banner -loglevel error -y -i work/src/IMG_$n.MOV \
    -vf "zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p" \
    -c:v libx264 -crf 14 -preset medium -an work/sdr/$n.mp4
done

# 2) Fonts (Google Fonts, OFL): Tajawal 500/800/900, Montserrat 900.
fetch_font() { # family weight outfile
  [ -f "fonts/$3" ] && return
  url=$(curl -sS -A "Mozilla/4.0" "https://fonts.googleapis.com/css2?family=$1:wght@$2" | grep -oE 'https://[^)]+\.ttf' | head -1)
  curl -sS -o "fonts/$3" "$url"
}
fetch_font Tajawal 500 Tajawal-500.ttf
fetch_font Tajawal 800 Tajawal-800.ttf
fetch_font Tajawal 900 Tajawal-900.ttf
fetch_font Montserrat 900 Montserrat-900.ttf

# 3) Render + mux (SFX version and clean version for voice-over).
FFMPEG="$FFMPEG" python3 render.py
"$FFMPEG" -hide_banner -loglevel error -y -i out/video_only.mp4 -i out/sfx.wav \
  -c:v copy -c:a aac -b:a 192k -shortest out/ChestPress_Machine_SFX.mp4
"$FFMPEG" -hide_banner -loglevel error -y -i out/video_only.mp4 -f lavfi -i anullsrc=r=48000:cl=stereo \
  -c:v copy -c:a aac -b:a 128k -shortest out/ChestPress_Machine_Clean.mp4
echo "done -> out/"
