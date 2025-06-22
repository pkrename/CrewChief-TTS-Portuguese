# 🇧🇷 CrewChief-TTS-Portuguese

Este projeto tem como objetivo criar uma versão localizada em **português brasileiro** do sistema de voz do [CrewChief](http://thecrewchief.org/) — com **áudios sintetizados via voz neural**, correção de tempo, ganho e estrutura organizacional totalmente automatizada.

Ele permite:
- 🔁 Gerar todos os áudios em `.wav` com base em frases mapeadas via `index.csv`
- 🗂️ Montar as pastas `spotter`, `radio_check` e `driver_names` como no jogo original
- 🧠 Traduzir usando um banco de frases humanas (`frases_en_pt.csv`) pré-validado
- 🔊 Aplicar aceleração e ganho para sonoridade ideal no jogo
- 🧪 Reproduzir toda a estrutura sem depender dos arquivos de áudio originais

---

## 🧰 Requisitos

Instale as dependências com:

```bash
pip install torch TTS pandas
sudo apt install sox
```

> Recomendado: Python 3.10+

---

## 🧠 Tecnologias utilizadas

| Componente | Finalidade |
|-----------|------------|
| [Coqui TTS (XTTS)](https://github.com/coqui-ai/TTS) | Geração de fala neural com suporte a PT-BR |
| [SoX](http://sox.sourceforge.net/) | Processamento de áudio (tempo + ganho) |
| `pandas`, `subprocess`, `torch` | Scripts Python para automação |

---

## 📁 Estrutura

```
CrewChief-TTS-Portuguese/
├── calibragem.wav               # Áudio base para entonação do TTS
├── dados/
│   ├── index.csv                # Estrutura de localização: pasta, arquivo, frase original
│   └── frases_en_pt.csv         # Banco de traduções (colunas: ingles, traducao_pt)
├── scripts/
│   ├── gera_index_csv.py        # Cria o index.csv com base na estrutura do CrewChief original
│   ├── gera_nomes_pilotos.py    # Gera a voz dos nomes de pilotos da pasta driver_names/
│   └── monta_projeto_com_index.py # Gera áudios + estrutura + subtitles.csv com base no index
└── README.md
```

---

## ⚙️ Como usar

1. Prepare o ambiente:

```bash
python3 -m venv venv
source venv/bin/activate
pip install torch TTS pandas
sudo apt install sox
```

2. Coloque seu `calibragem.wav` na raiz do projeto  
   (esse áudio define a voz base que o XTTS vai imitar)

3. Preencha seu `frases_en_pt.csv` com:

```csv
ingles,traducao_pt
"You're on the right, 3 wide","Você está na direita, três carros lado a lado"
"Radio check","Teste de rádio"
...
```

4. Rode o script principal:

```bash
python scripts/monta_projeto_com_index.py
```

Isso irá:
- Criar a estrutura `CrewChief_PT/` com todos os áudios `.wav`
- Gerar os arquivos `subtitles.csv` com as traduções
- Aplicar tempo e ganho com SoX
- Copiar as pastas `spotter` e `radio_check` para seu uso final

---

## 📦 Outros utilitários

```bash
python scripts/gera_index_csv.py        # Gera o index.csv a partir da pasta CrewChief_en/
python scripts/gera_nomes_pilotos.py    # Gera os áudios de driver_names/
```

---

## 📃 Logs úteis

- `nao_traduzidas.csv`: frases não encontradas no banco de traduções
- Os scripts ignoram arquivos já existentes — são seguros para múltiplas execuções

---

## 🎤 Sobre calibragem.wav

Esse é um pequeno trecho de áudio (entre 2 a 5 segundos) da sua voz base, ou de qualquer voz que você deseja replicar nas falas do TTS. Ele serve para que o XTTS aprenda o estilo da locução.

---

## 👨‍🔧 Criação

Este projeto foi idealizado por [@Pedro] com apoio da IA Microsoft Copilot — como forma de tornar o CrewChief acessível para jogadores de língua portuguesa e dar mais vida às pistas.

---

## 📄 Licença

Este projeto não inclui os áudios originais do CrewChief. Apenas a estrutura textual, scripts de automação e mapeamentos estão incluídos.  
Todos os áudios são gerados localmente via TTS.
