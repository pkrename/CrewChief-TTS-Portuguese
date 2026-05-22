import pandas as pd
import csv
import unicodedata
import re
from pathlib import Path

# ============================================
# CONFIG
# ============================================

INPUT_CSV = "./Dados/enriched_phrases.csv"
OUTPUT_CSV = "./Dados/tts_ready.csv"

# ============================================
# LOAD CSV
# ============================================

df = pd.read_csv(INPUT_CSV)

# ============================================
# HELPERS
# ============================================

def safe_text(text):
    if pd.isna(text):
        return ""
    return str(text).strip()

# ============================================
# TEXT NORMALIZATION
# ============================================

def normalize_text(text, token_type):

    text = safe_text(text)

    if not text:
        return ""

    # ----------------------------------------
    # Unicode normalization
    # ----------------------------------------

    text = unicodedata.normalize("NFC", text)

    # ----------------------------------------
    # Remove duplicated spaces
    # ----------------------------------------

    text = re.sub(r"\s+", " ", text)

    # ----------------------------------------
    # Remove spaces before punctuation
    # ----------------------------------------

    text = re.sub(r"\s+([,.!?])", r"\1", text)

    # ----------------------------------------
    # Cleanup repeated punctuation
    # ----------------------------------------

    text = re.sub(r"([!?.,]){2,}", r"\1", text)

    if token_type == "full_phrase":

        if not re.search(r"[.!?]$", text):
            text += ","

    if token_type == "number":

        # XTTS odeia número seco
        text += ","

    if token_type == "fragment":

        # fragmentos precisam de fechamento
        text += ","

    return text.strip()

# ============================================
# SPEECH RATE
# ============================================

def infer_speech_rate(category, urgency, token_type):

    rate = 1.00

    # ----------------------------------------
    # Fast paced calls
    # ----------------------------------------

    if category == "codriver":
        rate += 0.08

    if category == "spotter":
        rate += 0.10

    # ----------------------------------------
    # Urgent calls
    # ----------------------------------------

    if urgency == "high":
        rate += 0.05

    elif urgency == "medium":
        rate += 0.02

    # ----------------------------------------
    # Procedural fragments
    # ----------------------------------------

    if token_type == "fragment":
        rate += 0.03

    # ----------------------------------------
    # Calm engineer calls
    # ----------------------------------------

    if category in [
        "strategy",
        "fuel",
        "lap_times"
    ]:
        rate -= 0.05

    return round(rate, 2)

# ============================================
# PAUSES
# ============================================

def infer_pause_before(category, token_type):

    if token_type == "fragment":
        return 40

    if category == "codriver":
        return 30

    if category == "spotter":
        return 20

    return 80


def infer_pause_after(category, urgency):

    if urgency == "high":
        return 100

    if category == "codriver":
        return 60

    if category == "spotter":
        return 40

    return 160

# ============================================
# EMPHASIS
# ============================================

def infer_emphasis(text):

    text = safe_text(text).lower()

    keywords = [
        "box",
        "amarelo",
        "atenção",
        "cuidado",
        "penalidade",
        "volta anulada",
        "esquerda",
        "direita",
        "tráfego",
        "bandeira",
        "pneu",
        "aquecendo"
    ]

    for word in keywords:
        if word in text:
            return word

    return ""

# ============================================
# RADIO FX
# ============================================

def infer_radio_fx(category, emotion):

    if category == "spotter":
        return "spotter_radio"

    if category == "codriver":
        return "codriver_radio"

    if emotion == "warning":
        return "warning_radio"

    if emotion == "aggressive":
        return "aggressive_radio"

    return "standard_radio"

# ============================================
# VOICE PROFILE
# ============================================

def infer_tts_voice(role):

    mapping = {
        "race_engineer": "engineer_main",
        "spotter": "spotter_main",
        "codriver": "codriver_main",
        "crew_chief": "chief_main"
    }

    return mapping.get(role, "engineer_main")

# ============================================
# DYNAMIC GAIN
# ============================================

def infer_dynamic_gain(intensity):

    try:
        intensity = float(intensity)
    except:
        intensity = 0.5

    # Range aproximado:
    # 0.5 → -1.0 dB
    # 0.9 → +0.6 dB

    gain = -4 + (intensity * 3)

    return round(gain, 2)

# ============================================
# PROSODY PROFILE
# ============================================

def infer_prosody(category, urgency, emotion):

    if category == "codriver":
        return "fast_paced"

    if category == "spotter":
        return "reactive"

    if urgency == "high":
        return "urgent"

    if emotion == "aggressive":
        return "aggressive"

    if category in [
        "strategy",
        "fuel",
        "lap_times"
    ]:
        return "calm"

    return "standard"

# ============================================
# APPLY PROCESSING
# ============================================

def build_tts_text(row):

    pasta = safe_text(row["pasta"])

    # ========================================
    # DRIVER NAMES BYPASS
    # ========================================

    if pasta == "driver_names":

        return normalize_text(
            row["ingles"],
            "fragment"
        )

    # ========================================
    # DEFAULT PIPELINE
    # ========================================

    return normalize_text(
        row["traducao_pt"],
        row["token_type"]
    )

df["tts_text"] = df.apply(
    build_tts_text,
    axis=1
)

df["speech_rate"] = df.apply(
    lambda row: infer_speech_rate(
        row["category"],
        row["urgency"],
        row["token_type"]
    ),
    axis=1
)

df["pause_before_ms"] = df.apply(
    lambda row: infer_pause_before(
        row["category"],
        row["token_type"]
    ),
    axis=1
)

df["pause_after_ms"] = df.apply(
    lambda row: infer_pause_after(
        row["category"],
        row["urgency"]
    ),
    axis=1
)

df["emphasis"] = df["tts_text"].apply(infer_emphasis)

df["radio_fx"] = df.apply(
    lambda row: infer_radio_fx(
        row["category"],
        row["emotion"]
    ),
    axis=1
)

df["tts_voice"] = df["speaker_role"].apply(infer_tts_voice)

df["dynamic_gain"] = df["intensity"].apply(infer_dynamic_gain)

df["prosody_profile"] = df.apply(
    lambda row: infer_prosody(
        row["category"],
        row["urgency"],
        row["emotion"]
    ),
    axis=1
)

# ============================================
# EXPORT
# ============================================

Path("./dados").mkdir(exist_ok=True)

df.to_csv(
    OUTPUT_CSV,
    index=False,
    quoting=csv.QUOTE_ALL,
    encoding="utf-8"
)

# ============================================
# DONE
# ============================================

print(f"✅ TTS dataset salvo em: {OUTPUT_CSV}")
print(f"📦 Total de linhas processadas: {len(df)}")
