#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FFMPEG="$ROOT/.conda-ffmpeg/bin/ffmpeg"
FONT="/System/Library/Fonts/STHeiti Medium.ttc"
EARTH="$ROOT/DIY/Sources/nasa_earth_views_medium.mp4"
ROCKET="$ROOT/DIY/Sources/nasa_rocket_launch_medium.mp4"
WEBB="$ROOT/DIY/Sources/nasa_webb_highlights_medium.mp4"
AUDIO="$ROOT/Audio/a0001.mp3"
SEGMENTS="$ROOT/DIY/Work/segments"
CONCAT_LIST="$ROOT/DIY/Work/concat.txt"
SILENT_VIDEO="$ROOT/DIY/Work/diy_silent.mp4"
OUTPUT="$ROOT/DIY/Results/2023212290_附加实验.mp4"
STILL_CLIFFS="$ROOT/DIY/Work/webb_cliffs_clean.png"
STILL_GALAXIES="$ROOT/DIY/Work/webb_galaxies_clean.png"

mkdir -p "$SEGMENTS" "$ROOT/DIY/Results" "$ROOT/DIY/Logs"
rm -f "$SEGMENTS"/*.mp4 "$SILENT_VIDEO" "$OUTPUT"

"$FFMPEG" -hide_banner -loglevel error -y -ss 68 -i "$WEBB" -frames:v 1 "$STILL_CLIFFS"
"$FFMPEG" -hide_banner -loglevel error -y -ss 112 -i "$WEBB" -frames:v 1 "$STILL_GALAXIES"

common_video_args=(
  -an -r 25 -c:v libx264 -preset medium -crf 20
  -pix_fmt yuv420p -movflags +faststart
)

"$FFMPEG" -hide_banner -y -f lavfi -i "color=c=0x020817:s=1280x720:d=5:r=25" \
  -vf "drawtext=fontfile='$FONT':text='宇宙探索':fontcolor=white:fontsize=82:x=(w-text_w)/2:y=245,drawtext=fontfile='$FONT':text='从地球走向星辰':fontcolor=0x66CCFF:fontsize=42:x=(w-text_w)/2:y=360,drawtext=fontfile='$FONT':text='朱清扬  2023212290':fontcolor=white@0.75:fontsize=24:x=(w-text_w)/2:y=455,fade=t=in:st=0:d=1,fade=t=out:st=4:d=1" \
  "${common_video_args[@]}" "$SEGMENTS/01_title.mp4"

"$FFMPEG" -hide_banner -y -ss 20 -t 10 -i "$EARTH" \
  -vf "scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,fps=25,eq=saturation=1.08:contrast=1.04,drawbox=x=0:y=ih-105:w=iw:h=105:color=black@0.52:t=fill,drawtext=fontfile='$FONT':text='第一站：俯瞰我们的蓝色家园':fontcolor=white:fontsize=36:x=(w-text_w)/2:y=h-72,fade=t=in:st=0:d=0.7,fade=t=out:st=9.3:d=0.7" \
  "${common_video_args[@]}" "$SEGMENTS/02_earth.mp4"

"$FFMPEG" -hide_banner -y -ss 5 -t 10 -i "$ROCKET" \
  -vf "scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,fps=25,eq=saturation=1.12:contrast=1.07,drawbox=x=0:y=ih-105:w=iw:h=105:color=black@0.52:t=fill,drawtext=fontfile='$FONT':text='点火升空：向未知迈出一步':fontcolor=white:fontsize=36:x=(w-text_w)/2:y=h-72,fade=t=in:st=0:d=0.7,fade=t=out:st=9.3:d=0.7" \
  "${common_video_args[@]}" "$SEGMENTS/03_rocket.mp4"

"$FFMPEG" -hide_banner -y -i "$STILL_CLIFFS" \
  -vf "zoompan=z='min(zoom+0.00045,1.07)':d=150:s=1280x720:fps=25,eq=saturation=1.10:contrast=1.03,drawbox=x=0:y=ih-105:w=iw:h=105:color=black@0.52:t=fill,drawtext=fontfile='$FONT':text='穿越深空：凝望恒星诞生之地':fontcolor=white:fontsize=36:x=(w-text_w)/2:y=h-72,fade=t=in:st=0:d=0.7,fade=t=out:st=5.3:d=0.7" \
  -frames:v 150 "${common_video_args[@]}" "$SEGMENTS/04_webb_cliffs.mp4"

"$FFMPEG" -hide_banner -y -i "$STILL_GALAXIES" \
  -vf "zoompan=z='min(zoom+0.00028,1.07)':d=250:s=1280x720:fps=25,eq=saturation=1.10:contrast=1.03,drawbox=x=0:y=ih-105:w=iw:h=105:color=black@0.52:t=fill,drawtext=fontfile='$FONT':text='每一点星光，都来自遥远的过去':fontcolor=white:fontsize=36:x=(w-text_w)/2:y=h-72,fade=t=in:st=0:d=0.7,fade=t=out:st=9.3:d=0.7" \
  -frames:v 250 "${common_video_args[@]}" "$SEGMENTS/05_webb_galaxies.mp4"

"$FFMPEG" -hide_banner -y -f lavfi -i "color=c=0x020817:s=1280x720:d=5:r=25" \
  -vf "drawtext=fontfile='$FONT':text='探索未止  星辰在前':fontcolor=white:fontsize=60:x=(w-text_w)/2:y=270,drawtext=fontfile='$FONT':text='视频素材：NASA Image and Video Library':fontcolor=0x66CCFF:fontsize=26:x=(w-text_w)/2:y=390,drawtext=fontfile='$FONT':text='附加实验成片':fontcolor=white@0.70:fontsize=24:x=(w-text_w)/2:y=450,fade=t=in:st=0:d=1,fade=t=out:st=4:d=1" \
  "${common_video_args[@]}" "$SEGMENTS/06_end.mp4"

cat > "$CONCAT_LIST" <<EOF
file '$SEGMENTS/01_title.mp4'
file '$SEGMENTS/02_earth.mp4'
file '$SEGMENTS/03_rocket.mp4'
file '$SEGMENTS/04_webb_cliffs.mp4'
file '$SEGMENTS/05_webb_galaxies.mp4'
file '$SEGMENTS/06_end.mp4'
EOF

"$FFMPEG" -hide_banner -y -f concat -safe 0 -i "$CONCAT_LIST" -c copy "$SILENT_VIDEO"

"$FFMPEG" -hide_banner -y -stream_loop -1 -i "$AUDIO" -i "$SILENT_VIDEO" \
  -map 1:v:0 -map 0:a:0 -t 46 \
  -c:v libx264 -preset medium -b:v 2200k -maxrate 2400k -bufsize 4400k \
  -c:a aac -b:a 128k -af "volume=0.32,afade=t=in:st=0:d=2,afade=t=out:st=43:d=3" \
  -pix_fmt yuv420p -movflags +faststart "$OUTPUT"

"$ROOT/.conda-ffmpeg/bin/ffprobe" -v error \
  -show_entries format=filename,duration,size,bit_rate:stream=index,codec_name,codec_type,width,height,r_frame_rate \
  -of default=noprint_wrappers=1 "$OUTPUT" | tee "$ROOT/DIY/Logs/ffprobe_diy.txt"

echo "附加实验视频已生成：$OUTPUT"
