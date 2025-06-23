import os
import pandas as pd
import subprocess
import torch
from TTS.api import TTS
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import XttsAudioConfig
from TTS.config.shared_configs import BaseDatasetConfig
from TTS.tts.models.xtts import XttsArgs

# ======================
# ⚙️ CONFIGURAÇÕES
# ======================
calibragem_wav = "calibragem.wav"
index_csv = "index.csv"
csv_traducoes = "frases_en_pt.csv"
saida_base = "CrewChief_PT"
speed_factor = 1.2
ganho_db = 6

# ======================
# 🔊 XTTS INIT
# ======================
torch.serialization.add_safe_globals([XttsConfig, XttsAudioConfig, BaseDatasetConfig, XttsArgs])
tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2")
tts.to("cuda")

# ======================
# 📚 CARREGA OS CSVs
# ======================
df_index = pd.read_csv(index_csv)
df_trad = pd.read_csv(csv_traducoes)
mapa_traducao = dict(zip(
    df_trad["ingles"].str.strip().str.lower(),
    df_trad["traducao_pt"].str.strip()
))

# Agrupa por pasta
pastas = df_index.groupby("pasta")

nao_traduzidas = []

# ======================
# 🔧 FUNÇÕES
# ======================
def acelerar_audio(input_path, output_path, speed=1.0):
    subprocess.run(["sox", input_path, output_path, "tempo", str(speed)], check=True)

def aplicar_ganho(path, ganho_db):
    temp_path = path.replace(".wav", "_temp.wav")
    subprocess.run(["sox", path, temp_path, "gain", f"+{ganho_db}"], check=True)
    os.replace(temp_path, path)

def remover_silencio_final(input_path):
    temp_path = input_path.replace(".wav", "_trim.wav")
    subprocess.run([
        "sox", input_path, temp_path,
        "silence", "1", "0.001", "1%", "-1", "0.3", "1%"
    ], check=True)
    os.replace(temp_path, input_path)

# ======================
# 🚀 PROCESSAMENTO
# ======================
print("🎙️ Iniciando geração de áudios...")
for pasta, grupo in pastas:
    caminho_absoluto = os.path.join(saida_base, pasta)
    os.makedirs(caminho_absoluto, exist_ok=True)

    subtitles = []

    for _, row in grupo.iterrows():
        nome_wav = str(row["wav"]).strip()
        texto_en = str(row["ingles"]).strip()
        texto_key = texto_en.lower()
        texto_pt = mapa_traducao.get(texto_key)

        wav_final = os.path.join(caminho_absoluto, nome_wav)
        wav_temp = os.path.join(caminho_absoluto, f"temp_{nome_wav}")

        if not texto_pt:
            nao_traduzidas.append([nome_wav, texto_en])
            print(f"⚠️ Tradução ausente: {nome_wav} | \"{texto_en}\"")
            continue

        if os.path.exists(wav_final):
            print(f"⏩ Pulando {nome_wav}, já existe.")
            continue

        try:
            print(f"🔈 Gerando {nome_wav} → {texto_pt}")
            tts.tts_to_file(
                text=texto_pt,
                speaker_wav=calibragem_wav,
                language="pt",
                file_path=wav_temp
            )
            acelerar_audio(wav_temp, wav_final, speed_factor)
            aplicar_ganho(wav_final, ganho_db)
            remover_silencio_final(final_wav)
            os.remove(wav_temp)
            subtitles.append([nome_wav, texto_pt])
        except Exception as e:
            print(f"❌ Falha ao gerar {nome_wav}: {e}")

    if subtitles:
        df_out = pd.DataFrame(subtitles)
        df_out.to_csv(
            os.path.join(caminho_absoluto, "subtitles.csv"),
            index=False, header=False, encoding="utf-8"
        )

# ======================
# 📄 SALVA LOG DE FALHAS
# ======================
if nao_traduzidas:
    df_nao = pd.DataFrame(nao_traduzidas, columns=["arquivo", "ingles"])
    df_nao.to_csv("nao_traduzidas.csv", index=False, encoding="utf-8-sig")
    print("\n📦 Log de frases não traduzidas salvo como 'nao_traduzidas.csv'")
else:
    print("\n✅ Todas as falas foram traduzidas com sucesso!")

print("\n🏁 Projeto montado com sucesso com base no index!")

