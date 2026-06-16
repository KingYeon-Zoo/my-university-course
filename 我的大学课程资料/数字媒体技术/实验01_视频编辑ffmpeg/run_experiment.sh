#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FFMPEG="$ROOT/.conda-ffmpeg/bin/ffmpeg"
FFPROBE="$ROOT/.conda-ffmpeg/bin/ffprobe"
STUDENT_ID="${STUDENT_ID:-2023212290}"
FRAME_NUMBER="${FRAME_NUMBER:-90}"
FRAME_FILE="$(printf '%04d' "$FRAME_NUMBER")"

mkdir -p "$ROOT/Frames" "$ROOT/Results" "$ROOT/Evidence" "$ROOT/Logs"
rm -f "$ROOT/Frames/$FRAME_FILE.png" "$ROOT/Frames/${FRAME_FILE}wm.png"
rm -f "$ROOT/Results/"*.mp4 "$ROOT/Results/list.txt"
rm -f "$ROOT/Evidence/final_preview.jpg" "$ROOT/Logs/ffprobe_final.txt"

if [[ ! -x "$FFMPEG" || ! -x "$FFPROBE" ]]; then
  echo "FFmpeg isolated environment is missing: $ROOT/.conda-ffmpeg" >&2
  exit 1
fi

echo "Student ID used for watermark and final filename: $STUDENT_ID"
echo "Selected frame: $FRAME_NUMBER"
"$FFMPEG" -version | sed -n '1,4p'

echo "[1/7] Extract selected frame and add numeric watermark"
"$FFMPEG" -hide_banner -y \
  -i "$ROOT/Video/0001.mp4" \
  -vf "select=eq(n\\,$((FRAME_NUMBER - 1)))" \
  -fps_mode vfr -frames:v 1 -update 1 \
  "$ROOT/Frames/$FRAME_FILE.png"

"$FFMPEG" -hide_banner -y \
  -i "$ROOT/Frames/$FRAME_FILE.png" \
  -vf "drawtext=text='$STUDENT_ID':x=w-tw-220:y=h-th-40:fontsize=34:fontcolor=white:shadowx=2:shadowy=2" \
  -frames:v 1 -update 1 \
  "$ROOT/Frames/${FRAME_FILE}wm.png"

echo "[2/7] Convert the watermarked still image into a 3-second H.264 video"
"$FFMPEG" -hide_banner -y \
  -loop 1 -framerate 25 \
  -i "$ROOT/Frames/${FRAME_FILE}wm.png" \
  -t 3 -c:v libx264 -crf 25 -pix_fmt yuv420p -an \
  "$ROOT/Results/R0001.mp4"

echo "[3/7] Encode raw YUV420p material as H.264"
"$FFMPEG" -hide_banner -y \
  -f rawvideo -pixel_format yuv420p -video_size 1584x720 -framerate 25 \
  -i "$ROOT/Video/0002_1584x720_25.yuv" \
  -c:v libx264 -crf 25 -r 25 -pix_fmt yuv420p -an \
  "$ROOT/Results/R0002.mp4"

echo "[4/7] Transcode HEVC input to 1584x720 H.264 and remove audio"
"$FFMPEG" -hide_banner -y \
  -i "$ROOT/Video/0003.mp4" \
  -vf "scale=1584:720:flags=lanczos" \
  -c:v libx264 -crf 25 -r 25 -pix_fmt yuv420p -an \
  "$ROOT/Results/R0003.mp4"

echo "[5/7] Center-crop all three videos to standard 1280x720"
for n in 1 2 3; do
  "$FFMPEG" -hide_banner -y \
    -i "$ROOT/Results/R000${n}.mp4" \
    -vf "crop=1280:720" \
    -c:v libx264 -crf 25 -r 25 -pix_fmt yuv420p -an \
    "$ROOT/Results/R000${n}_720p.mp4"
done

cat > "$ROOT/Results/list.txt" <<EOF
file R0001_720p.mp4
file R0002_720p.mp4
file R0003_720p.mp4
EOF

echo "[6/7] Concatenate the three normalized video segments"
"$FFMPEG" -hide_banner -y \
  -f concat -safe 0 -i "$ROOT/Results/list.txt" \
  -c:v libx264 -crf 25 -r 25 -pix_fmt yuv420p -an \
  "$ROOT/Results/R123.mp4"

echo "[7/7] Replace background audio and create final deliverable"
"$FFMPEG" -hide_banner -y \
  -i "$ROOT/Results/R123.mp4" \
  -stream_loop -1 -i "$ROOT/Audio/a0001.mp3" \
  -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 128k -t 15 \
  "$ROOT/Results/${STUDENT_ID}.mp4"

"$FFPROBE" -hide_banner "$ROOT/Results/${STUDENT_ID}.mp4" \
  2>&1 | tee "$ROOT/Logs/ffprobe_final.txt"

"$FFMPEG" -hide_banner -y \
  -ss 00:00:02 -i "$ROOT/Results/${STUDENT_ID}.mp4" \
  -frames:v 1 -update 1 "$ROOT/Evidence/final_preview.jpg"

echo "Experiment completed: $ROOT/Results/${STUDENT_ID}.mp4"
