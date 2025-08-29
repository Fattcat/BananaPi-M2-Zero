from flask import Flask, Response, render_template_string
import subprocess, threading

app = Flask(__name__)


# Works on BananaPiM2Zero with ArmbianOS = True
# Just need to connect with SSH to Banana Pi, then connect USB Cam with "builtin Mic"
# Then start this code


# Globálne premenné
arecord_process = None
ffmpeg_process = None
process_lock = threading.Lock()

# HTML stránka s vizualizáciou
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
  <title>Live Mic Stream</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      background-color: #1e1e1e;
      color: white;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: flex-start;
      min-height: 100vh;
      margin: 0;
      padding: 30px 0;
    }
    h1 { margin-bottom: 40px; }
    button {
      font-size: 20px;
      padding: 15px 30px;
      border: none;
      border-radius: 12px;
      background-color: #28a745;
      color: white;
      cursor: pointer;
      margin-bottom: 20px;
    }
    button.stop { background-color: #dc3545; }
    audio {
      margin-bottom: 20px;
      width: 80%;
      max-width: 600px;
      outline: none;
      border-radius: 6px;
    }
    #meterCanvas {
      background: #000;
      border-radius: 6px;
      width: 80%;
      max-width: 600px;
      height: 100px;
      display: block;
    }
  </style>
</head>
<body>
  <h1>🎤 Live Mic Stream</h1>
  <button id="micBtn" onclick="toggleMic()">Zapnúť Mic</button>
  <audio id="player" controls autoplay></audio>
  <canvas id="meterCanvas"></canvas>

<script>
let micOn = false;
let audioCtx, sourceNode, analyser, dataArray, canvasCtx;
const canvas = document.getElementById("meterCanvas");
canvasCtx = canvas.getContext("2d");

function toggleMic() {
  if (!micOn) {
    fetch('/start').then(() => {
      document.getElementById('player').src = '/audio';
      document.getElementById('micBtn').innerText = "Zastaviť Mic";
      document.getElementById('micBtn').classList.add("stop");
      micOn = true;
      startMeter();
    });
  } else {
    fetch('/stop').then(() => {
      document.getElementById('player').pause();
      document.getElementById('player').src = "";
      document.getElementById('micBtn').innerText = "Zapnúť Mic";
      document.getElementById('micBtn').classList.remove("stop");
      micOn = false;
      stopMeter();
    });
  }
}

function startMeter() {
  audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  sourceNode = audioCtx.createMediaElementSource(document.getElementById("player"));
  analyser = audioCtx.createAnalyser();
  sourceNode.connect(analyser);
  analyser.connect(audioCtx.destination);
  analyser.fftSize = 256;
  dataArray = new Uint8Array(analyser.frequencyBinCount);
  draw();
}

function stopMeter() {
  if(audioCtx) audioCtx.close();
  canvasCtx.clearRect(0,0,canvas.width,canvas.height);
}

function draw() {
  if (!micOn) return;
  requestAnimationFrame(draw);
  analyser.getByteFrequencyData(dataArray);
  canvasCtx.fillStyle = "#000";
  canvasCtx.fillRect(0,0,canvas.width,canvas.height);

  let barWidth = canvas.width / dataArray.length;
  for (let i = 0; i < dataArray.length; i++) {
    let barHeight = dataArray[i];
    let r = barHeight + 25*(i/dataArray.length);
    let g = 250*(i/dataArray.length);
    let b = 50;
    canvasCtx.fillStyle = "rgb(" + r + "," + g + "," + b + ")";
    canvasCtx.fillRect(i*barWidth, canvas.height-barHeight/2, barWidth, barHeight/2);
  }
}
</script>
</body>
</html>
"""

# FFmpeg logging
def log_ffmpeg(process):
    for line in iter(process.stderr.readline, b''):
        print("FFmpeg:", line.decode(errors="ignore"), end="")

# Routes
@app.route("/")
def index():
    return render_template_string(HTML_PAGE)

@app.route("/start")
def start_stream():
    global arecord_process, ffmpeg_process
    with process_lock:
        if arecord_process is None and ffmpeg_process is None:
            print("▶️ Spúšťam arecord + FFmpeg pipeline...")
            # arecord pipeline – menšie buffery pre nižšiu latenciu
            arecord_process = subprocess.Popen(
                ["arecord", "-D", "plughw:1,0", "-f", "cd", "-c", "1", "-r", "44100",
                 "--buffer-time=20000", "--period-size=1024"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            # FFmpeg – low-latency MP3
            ffmpeg_process = subprocess.Popen(
                ["ffmpeg",
                 "-f", "s16le", "-ar", "44100", "-ac", "1", "-i", "pipe:0",
                 "-acodec", "libmp3lame", "-ab", "128k",
                 "-fflags", "nobuffer", "-flags", "low_delay", "-tune", "zerolatency",
                 "-flush_packets", "1",
                 "-f", "mp3", "-"],
                stdin=arecord_process.stdout,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            threading.Thread(target=log_ffmpeg, args=(ffmpeg_process,), daemon=True).start()
    return "Started"

@app.route("/stop")
def stop_stream():
    global arecord_process, ffmpeg_process
    with process_lock:
        print("⏹️ Zastavujem arecord + FFmpeg...")
        if ffmpeg_process:
            ffmpeg_process.kill()
            ffmpeg_process = None
        if arecord_process:
            arecord_process.kill()
            arecord_process = None
    return "Stopped"

@app.route("/audio")
def audio_feed():
    def generate():
        global ffmpeg_process
        while ffmpeg_process and ffmpeg_process.stdout:
            data = ffmpeg_process.stdout.read(256)  # menší buffer = nižšia latencia
            if not data:
                break
            yield data
    return Response(generate(), mimetype="audio/mpeg")

# Spustenie Flask servera
if __name__ == "__main__":
    print("🚀 Spúšťam Flask server na http://0.0.0.0:4999")
    app.run(host="0.0.0.0", port=4999, threaded=True)
