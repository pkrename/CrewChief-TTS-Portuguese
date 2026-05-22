import gc
import os
import re
import subprocess
from pathlib import Path

import pandas as pd
import torch
import torchaudio

from TTS.api import TTS

# ============================================
# CONFIG
# ============================================

INPUT_CSV = "./Dados/tts_ready.csv"

OUTPUT_BASE = "./CrewChief_PT"

REFERENCE_WAV = "./calibragem.wav"

DEFAULT_LANGUAGE = "pt"

USE_CUDA = True

SKIP_EXISTING = True

MAX_RETRIES = 3

CACHE_CLEAN_INTERVAL = 25

# ============================================
# DEVICE
# ============================================

device = "cuda" if USE_CUDA and torch.cuda.is_available() else "cpu"

print(f"\n🚀 Inicializando XTTS em {device.upper()}")

# ============================================
# XTTS INIT
# ============================================

tts = TTS(
    model_name="tts_models/multilingual/multi-dataset/xtts_v2"
)

tts.to(device)

print("✅ XTTS carregado")

# ============================================
# LOAD CSV
# ============================================

print("📚 Carregando dataset...")

df = pd.read_csv(INPUT_CSV)

print(f"📦 Total de linhas: {len(df)}")

# ============================================
# HELPERS
# ============================================

def safe_text(value):

    if pd.isna(value):
        return ""

    return str(value).strip()


def prepare_tts_text(text, token_type):

    text = safe_text(text)

    if not text:
        return ""

    # ----------------------------------------
    # normalize spaces
    # ----------------------------------------

    text = re.sub(r"\s+", " ", text)

    # ----------------------------------------
    # XTTS stability
    # evita bug de sentence splitting estranho
    # ----------------------------------------

    text = text.replace("...", ",")

    # remove pontuação repetida
    text = re.sub(r"([!?.,]){2,}", r"\1", text)

    # evita espaços antes da pontuação
    text = re.sub(r"\s+([,.!?])", r"\1", text)

    # ----------------------------------------
    # força fechamento leve
    # XTTS odeia frase seca
    # ----------------------------------------

    if not re.search(r"[,.!?]$", text):
        text += ","

    return text.strip()

# ============================================
# AUDIO VALIDATION
# ============================================

def is_audio_invalid(path, text):

    try:

        info = torchaudio.info(path)

        duration = info.num_frames / info.sample_rate

        expected = max(1.2, len(text) / 14)

        # ----------------------------------------
        # duração absurda
        # ----------------------------------------

        if duration > expected * 2.5:

            print(f"⚠️ WAV inválido: duração excessiva ({duration:.2f}s)")

            return True

        # ----------------------------------------
        # arquivo gigante
        # ----------------------------------------

        size_mb = os.path.getsize(path) / (1024 * 1024)

        if size_mb > 2:

            print(f"⚠️ WAV inválido: tamanho excessivo ({size_mb:.2f}MB)")

            return True

        # ----------------------------------------
        # áudio vazio
        # ----------------------------------------

        waveform, sr = torchaudio.load(path)

        peak = waveform.abs().max().item()

        if peak < 0.005:

            print("⚠️ WAV inválido: áudio muito baixo")

            return True

        return False

    except Exception as e:

        print(f"⚠️ Erro validando áudio: {e}")

        return True

# ============================================
# SOX PROCESSING
# ============================================

def process_audio(
    input_path,
    output_path,
    speech_rate,
    radio_fx
):

    command = [
        "sox",

        input_path,

        "-r", "44100",
        "-c", "1",

        output_path,

        # ====================================
        # TEMPO
        # ====================================

        "tempo",
        str(speech_rate),

        # ====================================
        # REMOVE SILENCE
        # ====================================

        "silence",
        "1",
        "0.02",
        "0.3%",
        "-1",
        "0.3",
        "0.3%",
    ]

    # ========================================
    # RADIO FX
    # ========================================

    if radio_fx == "standard_radio":

        command += [
            "highpass", "250",
            "lowpass", "3400",

            "compand",
            "0.02,0.18",
            "6:-80,-30,-10",
            "-5",
            "-90",
            "0.1"
        ]

    elif radio_fx == "codriver_radio":

        command += [
            "highpass", "180",
            "lowpass", "4200",

            "compand",
            "0.02,0.18",
            "5:-80,-28,-10",
            "-4",
            "-90",
            "0.1"
        ]

    elif radio_fx == "warning_radio":

        command += [
            "highpass", "250",
            "lowpass", "5000",

            "compand",
            "0.01,0.12",
            "6:-80,-25,-8",
            "-3",
            "-90",
            "0.1"
        ]

    elif radio_fx == "aggressive_radio":

        command += [
            "overdrive", "4",

            "compand",
            "0.01,0.10",
            "6:-80,-22,-6",
            "-2",
            "-90",
            "0.1"
        ]

    elif radio_fx == "spotter_radio":

        command += [
            "highpass", "300",
            "lowpass", "3500",

            "compand",
            "0.02,0.14",
            "5:-80,-26,-8",
            "-4",
            "-90",
            "0.1"
        ]

    # ========================================
    # GLOBAL NORMALIZATION
    # padroniza TODOS os audios
    # ========================================

    command += [

        # limiter suave
        "gain", "-n",

        # loudness padronizado
        "norm", "-3"
    ]

    subprocess.run(
        command,
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

# ============================================
# GENERATION LOOP
# ============================================

print("\n🎙️ Iniciando geração...\n")

generated = 0

failed = []

for idx, row in df.iterrows():

    pasta = safe_text(row["pasta"])

    wav_name = safe_text(row["wav"])

    text = prepare_tts_text(
        row["tts_text"],
        row["token_type"]
    )

    if not text:
        continue

    speech_rate = float(row["speech_rate"])

    radio_fx = safe_text(row["radio_fx"])

    output_dir = os.path.join(OUTPUT_BASE, pasta)

    Path(output_dir).mkdir(
        parents=True,
        exist_ok=True
    )

    final_path = os.path.join(
        output_dir,
        wav_name
    )

    raw_path = os.path.join(
        output_dir,
        f"raw_{wav_name}"
    )

    # ========================================
    # SKIP EXISTING
    # ========================================

    if SKIP_EXISTING and os.path.exists(final_path):

        print(f"⏩ Pulando: {wav_name}")

        continue

    success = False

    for attempt in range(MAX_RETRIES):

        try:

            print(f"\n🔈 {wav_name}")
            print(f"   ↳ tentativa {attempt + 1}")
            print(f"   ↳ {text}")

            # ====================================
            # PERIODIC CLEANUP
            # ====================================

            if idx % CACHE_CLEAN_INTERVAL == 0:

                gc.collect()

                if device == "cuda":

                    torch.cuda.empty_cache()

                    torch.cuda.synchronize()

            # ====================================
            # XTTS INFERENCE
            # ====================================

            with torch.inference_mode():

                wav = tts.tts(
                    text=text,
                    speaker_wav=REFERENCE_WAV,
                    language=DEFAULT_LANGUAGE,
                    split_sentences=False
                )

            wav_tensor = torch.tensor(
                wav,
                dtype=torch.float32
            ).unsqueeze(0)

            torchaudio.save(
                raw_path,
                wav_tensor.cpu(),
                24000
            )

            del wav
            del wav_tensor

            # ====================================
            # VALIDATION
            # ====================================

            if is_audio_invalid(raw_path, text):

                if os.path.exists(raw_path):
                    os.remove(raw_path)

                continue

            # ====================================
            # FINAL PROCESSING
            # ====================================

            process_audio(
                raw_path,
                final_path,
                speech_rate,
                radio_fx
            )

            # ====================================
            # REMOVE RAW
            # ====================================

            if os.path.exists(raw_path):
                os.remove(raw_path)

            generated += 1

            success = True

            break

        except Exception as e:

            print(f"❌ Falha: {e}")

            gc.collect()

            if device == "cuda":

                torch.cuda.empty_cache()

    # ========================================
    # FAIL LOG
    # ========================================

    if not success:

        failed.append({
            "wav": wav_name,
            "text": text
        })

# ============================================
# EXPORT FAILURES
# ============================================

if failed:

    pd.DataFrame(failed).to_csv(
        "tts_failures.csv",
        index=False,
        encoding="utf-8-sig"
    )

    print("\n⚠️ Falhas salvas em tts_failures.csv")

# ============================================
# DONE
# ============================================

print("\n===================================")
print("✅ Geração concluída")
print(f"🎧 WAVs gerados: {generated}")
print(f"❌ Falhas: {len(failed)}")
print("===================================")
