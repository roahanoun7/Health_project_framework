"""
Creates the spoken digits for the PASAT: audio/1.wav ... audio/9.wav

Run this ONCE, in the same folder as pasat.py:
    python make_audio.py

Nothing to install: it uses the voice built into your computer
(Windows, Mac or Linux). Then share the finished "audio" folder with your
group, so everyone hears the exact same voice.
"""
import platform
import shutil
import subprocess
import sys
from pathlib import Path

# ======================= SETTINGS: change these =======================
WIN_RATE = -2        # Windows speed, -10 (slow) to 10 (fast)
MAC_RATE = 130       # Mac speed in words per minute
MAC_VOICE = "Samantha"   # an English Mac voice; falls back to the default if missing
LINUX_RATE = 130     # Linux speed in words per minute
# ======================================================================

out_dir = Path(__file__).parent / "audio"
out_dir.mkdir(exist_ok=True)


def make_windows(digit, file):
    path = str(file).replace("'", "''")
    script = (
        "Add-Type -AssemblyName System.Speech; "
        "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
        "$en = $s.GetInstalledVoices() | Where-Object { $_.VoiceInfo.Culture.Name -like 'en-*' } | Select-Object -First 1; "
        "if ($en) { $s.SelectVoice($en.VoiceInfo.Name) }; "
        f"$s.Rate = {WIN_RATE}; $s.SetOutputToWaveFile('{path}'); $s.Speak('{digit}'); $s.Dispose()"
    )
    subprocess.run(["powershell", "-NoProfile", "-Command", script], check=True)


def make_mac(digit, file):
    temp = file.with_suffix(".aiff")
    try:
        subprocess.run(["say", "-v", MAC_VOICE, "-r", str(MAC_RATE), "-o", str(temp), str(digit)], check=True)
    except subprocess.CalledProcessError:   # voice not installed: use the default
        subprocess.run(["say", "-r", str(MAC_RATE), "-o", str(temp), str(digit)], check=True)
    subprocess.run(["afconvert", "-f", "WAVE", "-d", "LEI16", str(temp), str(file)], check=True)
    temp.unlink()


def make_linux(digit, file):
    exe = shutil.which("espeak-ng") or shutil.which("espeak")
    if not exe:
        sys.exit("Install a voice first:  sudo apt install espeak-ng")
    subprocess.run([exe, "-v", "en", "-s", str(LINUX_RATE), "-w", str(file), str(digit)], check=True)


make = {"Windows": make_windows, "Darwin": make_mac}.get(platform.system(), make_linux)

for digit in range(1, 10):
    file = out_dir / f"{digit}.wav"
    try:
        make(digit, file)
    except Exception as error:
        sys.exit(f"Could not create {file.name}: {error}")

missing = [d for d in range(1, 10) if not (out_dir / f"{d}.wav").exists()]
if missing:
    print("These files are missing:", missing)
else:
    print(f"Done. 9 files created in: {out_dir}")
    print("Now run pasat.py again. The start screen should say 'Voice: on'.")
