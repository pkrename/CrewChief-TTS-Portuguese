import os
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
pasta_origem = "CrewChief_en/driver_names"
pasta_destino = "CrewChief_PT/driver_names"
calibragem_wav = "calibragem.wav"
speed_factor = 1.2       # 🎚️ Aceleração do áudio
ganho_db = 6             # 🔊 Ganho extra via SoX

# ======================
# 🔊 XTTS INIT
# ======================
torch.serialization.add_safe_globals([XttsConfig, XttsAudioConfig, BaseDatasetConfig, XttsArgs])
tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2")
tts.to("cuda")

# ======================
# 🛠️ FUNÇÕES AUXILIARES
# ======================
def acelerar_audio(input_path, output_path, speed=1.0):
    subprocess.run(["sox", input_path, output_path, "tempo", str(speed)], check=True)

def aplicar_ganho(path, ganho_db):
    temp_path = path.replace(".wav", "_temp.wav")
    subprocess.run(["sox", path, temp_path, "gain", f"+{ganho_db}"], check=True)
    os.replace(temp_path, path)

# ======================
# 🚀 PROCESSAMENTO
# ======================
os.makedirs(pasta_destino, exist_ok=True)

arquivos = [f for f in os.listdir(pasta_origem) if f.endswith(".wav")]
print(f"🎯 Encontrados {len(arquivos)} nomes de pilotos")

for nome_arquivo in arquivos:
    nome = os.path.splitext(nome_arquivo)[0]  # remove extensão
    nome_formatado = nome.capitalize()        # ex: "aachban" → "Aachban"

    entrada_wav = os.path.join(pasta_destino, nome_arquivo)
    temp_wav = os.path.join(pasta_destino, f"temp_{nome_arquivo}")

    if os.path.exists(entrada_wav):
        print(f"⏩ {nome_arquivo} já existe. Pulando.")
        continue

    try:
        print(f"🎙️ Gerando: {nome_formatado} → {nome_arquivo}")
        tts.tts_to_file(
            text=nome_formatado,
            speaker_wav=calibragem_wav,
            language="pt",
            file_path=temp_wav
        )
        acelerar_audio(temp_wav, entrada_wav, speed_factor)
        aplicar_ganho(entrada_wav, ganho_db)
        os.remove(temp_wav)

    except Exception as e:
        print(f"❌ Erro ao gerar {nome_arquivo}: {e}")

print("\n✅ Nomes de pilotos gerados com sucesso!")

