import pandas as pd
import csv
from pathlib import Path

# =========================
# CONFIG
# =========================

INDEX_CSV = "./Dados/index.csv"
TRANSLATION_CSV = "./Dados/frases_en_pt.csv"
OUTPUT_CSV = "./Dados/enriched_phrases.csv"

# =========================
# LOAD CSV
# =========================

index_df = pd.read_csv(INDEX_CSV)
translation_df = pd.read_csv(TRANSLATION_CSV)

# =========================
# NORMALIZATION
# =========================

index_df["ingles"] = index_df["ingles"].astype(str).str.strip().str.lower()
translation_df["ingles"] = translation_df["ingles"].astype(str).str.strip().str.lower()

# =========================
# MERGE
# =========================

df = pd.merge(
    index_df,
    translation_df,
    on="ingles",
    how="left"
)

# =========================
# CATEGORY INFERENCE
# =========================

def infer_category(path):
    path = str(path).lower()

    categories = [
        "acknowledge",
        "alarm_clock",
        "battery",
        "codriver",
        "conditions",
        "corners",
        "damage_reporting",
        "driver_swaps",
        "engine_monitor",
        "flags",
        "frozen_order",
        "fuel",
        "incidents",
        "lap_counter",
        "lap_times",
        "licence",
        "mandatory_pit_stops",
        "multiclass",
        "numbers",
        "opponents",
        "overtaking_aids",
        "pace_notes",
        "pearls_of_wisdom",
        "penalties",
        "position",
        "push_now",
        "race_time",
        "radio_check",
        "rants",
        "spotter",
        "strategy",
        "timings",
        "tyre_monitor",
        "watched_opponents"
    ]

    for category in categories:
        if category in path:
            return category

    return "unknown"

# =========================
# EMOTION INFERENCE
# =========================

def infer_emotion(text):
    text = str(text).lower()

    if any(x in text for x in [
        "crash",
        "yellow",
        "damage",
        "penalty",
        "black flag",
        "warning"
    ]):
        return "warning"

    if any(x in text for x in [
        "push",
        "attack",
        "go go go",
        "fight"
    ]):
        return "aggressive"

    if any(x in text for x in [
        "good job",
        "nice work",
        "well done"
    ]):
        return "positive"

    return "neutral"

# =========================
# URGENCY
# =========================

def infer_urgency(text):
    text = str(text).lower()

    if any(x in text for x in [
        "immediately",
        "now",
        "yellow",
        "crash"
    ]):
        return "high"

    if any(x in text for x in [
        "watch",
        "careful",
        "track limits"
    ]):
        return "medium"

    return "low"

# =========================
# TOKEN TYPE
# =========================

def infer_token_type(text):
    text = str(text)

    if text.replace(".", "").isdigit():
        return "number"

    if len(text.split()) <= 2:
        return "fragment"

    return "full_phrase"

# =========================
# ASSEMBLY MODE
# =========================

def infer_assembly_mode(token_type):
    if token_type == "fragment":
        return "procedural"

    return "static"

# =========================
# RADIO STYLE
# =========================

def infer_radio_style(category):
    aggressive_categories = [
        "push_now",
        "rants",
        "spotter"
    ]

    calm_categories = [
        "strategy",
        "lap_times",
        "fuel"
    ]

    if category in aggressive_categories:
        return "aggressive"

    if category in calm_categories:
        return "calm"

    return "standard"

# =========================
# SPEAKER ROLE
# =========================

def infer_speaker_role(category):

    mapping = {
        "spotter": "spotter",
        "codriver": "codriver",
        "pace_notes": "codriver",
        "strategy": "race_engineer",
        "fuel": "race_engineer",
        "rants": "crew_chief"
    }

    return mapping.get(category, "race_engineer")

# =========================
# PAUSE PROFILE
# =========================

def infer_pause_profile(token_type):

    if token_type == "fragment":
        return "micro_pause"

    return "normal_pause"

# =========================
# INTENSITY
# =========================

def infer_intensity(emotion, urgency):

    if urgency == "high":
        return 0.9

    if emotion == "aggressive":
        return 0.8

    if emotion == "warning":
        return 0.7

    return 0.5

# =========================
# APPLY ENRICHMENT
# =========================

df["category"] = df["pasta"].apply(infer_category)

df["emotion"] = df["ingles"].apply(infer_emotion)

df["urgency"] = df["ingles"].apply(infer_urgency)

df["token_type"] = df["ingles"].apply(infer_token_type)

df["assembly_mode"] = df["token_type"].apply(infer_assembly_mode)

df["radio_style"] = df["category"].apply(infer_radio_style)

df["speaker_role"] = df["category"].apply(infer_speaker_role)

df["pause_profile"] = df["token_type"].apply(infer_pause_profile)

df["intensity"] = df.apply(
    lambda row: infer_intensity(
        row["emotion"],
        row["urgency"]
    ),
    axis=1
)

# =========================
# EXPORT
# =========================

Path("data").mkdir(exist_ok=True)

df.to_csv(
    OUTPUT_CSV,
    index=False,
    quoting=csv.QUOTE_ALL,
    encoding="utf-8"
)

print(f"Arquivo enriquecido salvo em: {OUTPUT_CSV}")
