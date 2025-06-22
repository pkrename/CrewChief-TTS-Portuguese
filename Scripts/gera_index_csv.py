import os
import pandas as pd

base_folder = "CrewChief_en"
index_data = []

print("🚀 Gerando index.csv...")

# === Parte 1: Subtitles.csv ===
for root, dirs, files in os.walk(base_folder):
    if "subtitles.csv" in files:
        path_sub = os.path.join(root, "subtitles.csv")
        try:
            df = pd.read_csv(path_sub, header=None)
            df.columns = ["wav", "ingles"]

            relative_path = os.path.relpath(root, base_folder).replace("\\", "/")

            for _, row in df.iterrows():
                index_data.append({
                    "pasta": relative_path,
                    "wav": str(row["wav"]).strip(),
                    "ingles": str(row["ingles"]).strip()
                })

            print(f"✅ Subtitles: {relative_path} ({len(df)} entradas)")

        except Exception as e:
            print(f"❌ Erro ao ler {path_sub}: {e}")

# === Parte 2: Driver Names ===
driver_names_path = os.path.join(base_folder, "driver_names")

if os.path.isdir(driver_names_path):
    arquivos = [f for f in os.listdir(driver_names_path) if f.endswith(".wav")]
    for f in arquivos:
        nome = os.path.splitext(f)[0].capitalize()
        index_data.append({
            "pasta": "driver_names",
            "wav": f,
            "ingles": nome
        })
    print(f"✅ Driver Names: {len(arquivos)} nomes adicionados")

else:
    print("⚠️ Pasta driver_names não encontrada.")

# === Salvar o index.csv final ===
df_index = pd.DataFrame(index_data)
df_index.to_csv("index.csv", index=False, encoding="utf-8-sig")

print("\n📁 Arquivo 'index.csv' gerado com sucesso!")

