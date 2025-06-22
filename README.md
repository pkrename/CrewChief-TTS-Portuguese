# 🇧🇷 CrewChief-TTS-Portuguese

Este projeto tem como objetivo criar uma versão localizada em **português brasileiro** do sistema de voz do [CrewChief](http://thecrewchief.org/) — com áudios gerados por inteligência artificial, aceleração de tempo, ganho e estruturação automatizada.

---

## ✨ Funcionalidades

- 🔁 Geração de áudios `.wav` a partir de um dicionário customizado e estrutura definida por CSV
- 🗂️ Criação automática das pastas `spotter`, `radio_check`, `driver_names`
- 🧠 Traduções via `frases_en_pt.csv`
- 🔊 Ajuste de velocidade e ganho com [SoX](http://sox.sourceforge.net/)
- 🎙️ Produção neural por [XTTS (CoquiTTS)](https://docs.coqui.ai/en/latest/)

---

## 🧰 Requisitos

- Python 3.10+
- Linux com suporte a CUDA (opcional)
- Docker (recomendado)
- GPU NVIDIA com drivers e CUDA ativados

Instale as bibliotecas:

```bash
pip install torch TTS pandas
sudo apt install sox
```

---

## 🐳 Setup com Docker (opcional, recomendado)

Foi utilizado um container baseado em CUDA + CoquiTTS para garantir isolamento do ambiente:

<details>
<summary><strong>🧱 Comandos Docker para Fedora (ou distribuições baseadas em DNF)</strong></summary>

```bash
# Instale o Docker
sudo dnf install -y dnf-plugins-core
sudo dnf config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo
sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
sudo systemctl restart docker
# (ou reinicie o sistema após esse passo)
```

</details>

<details>
<summary><strong>⚙️ Instalação dos drivers NVIDIA e suporte CUDA para Docker</strong></summary>

```bash
sudo dnf install akmod-nvidia
sudo dnf install xorg-x11-drv-nvidia-cuda
sudo dnf config-manager --add-repo https://nvidia.github.io/nvidia-docker/fedora/nvidia-docker.repo
sudo dnf install -y nvidia-docker2
sudo systemctl restart docker

# Verifique se está funcionando:
docker run --rm --gpus all nvidia/cuda:12.3.2-base-ubuntu22.04 nvidia-smi
```

</details>

<details>
<summary><strong>📦 Dockerfile utilizado</strong></summary>

```Dockerfile
FROM nvidia/cuda:12.3.2-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
RUN pip install TTS

WORKDIR /workspace
ENTRYPOINT ["bash"]
```
</details>

<details>
<summary><strong>🧩 docker-compose.yml</strong></summary>

```yaml
version: '3.9'
services:
  coqui-tts:
    build: .
    container_name: coqui-tts
    volumes:
      - ./workspace:/workspace
    deploy:
      resources:
        reservations:
          devices:
            - capabilities: [gpu]
    stdin_open: true
    tty: true
```

</details>

Use:

```bash
docker compose up --build -d
docker exec -it coqui-tts bash
```

> **🗂️ Coloque todos os scripts e o arquivo `calibragem.wav` na pasta `workspace/` para começar a usar dentro do container.**

---

## 🧠 Estrutura do Projeto

```
CrewChief-TTS-Portuguese/
├── calibragem.wav
├── dados/
│   ├── index.csv
│   └── frases_en_pt.csv
├── scripts/
│   ├── gera_index_csv.py
│   ├── gera_nomes_pilotos.py
│   └── monta_projeto_com_index.py
└── README.md
```

---

## 🚀 Executando

1. Certifique-se de que `calibragem.wav`, `index.csv` e `frases_en_pt.csv` estão corretamente configurados.
2. Rode:

```bash
python3 scripts/monta_projeto_com_index.py
```

Isso irá:
- Criar a árvore `CrewChief_PT/` com todos os `.wav`
- Gerar os `subtitles.csv` por pasta
- Aplicar tempo e ganho com SoX
- Copiar as pastas `radio_check` e `spotter` para exportação final

---

## 📑 Referências

- 🎓 **Projeto que inspirou este trabalho**: [crew-chief-autovoicepack](https://github.com/cktlco/crew-chief-autovoicepack)
- 👨‍🔧 **Crew Chief**: Download [CrewChief](https://thecrewchief.org/forumdisplay.php?28-Download-and-Links)
- 🎙️ **Coqui TTS (XTTS)**: [https://docs.coqui.ai/en/latest/](https://docs.coqui.ai/en/latest/)
- 🎥 **Tutorial do XTTS** no YouTube: [https://www.youtube.com/watch?v=g9VASNxpXV0](https://www.youtube.com/watch?v=g9VASNxpXV0)
- 📦 **Docker + NVIDIA** Base: [https://hub.docker.com/r/nvidia/cuda](https://hub.docker.com/r/nvidia/cuda)

---

## 👨‍🔧 Autor

Este projeto foi idealizado por **[@pkrename](https://github.com/pkrename)** com apoio da **Microsoft Copilot**, combinando automação de scripts, inteligência artificial e amor pela simulação automobilística 🏎️🇧🇷

---

## 📄 Licença

Este projeto não inclui os áudios originais do CrewChief. Apenas a estrutura textual, scripts de automação e mapeamentos estão incluídos.  
Todos os áudios são gerados localmente via TTS.
=======
Este projeto **não distribui arquivos originais do CrewChief**. Apenas a estrutura textual, mapeamentos e scripts estão incluídos.  
Todos os áudios são gerados localmente via TTS com base na voz fornecida em `calibragem.wav`.
