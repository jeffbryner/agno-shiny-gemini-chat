# agno-shiny-gemini-chat
quickstart with agno, shiny and gemini in vertexAI

# installation
First get uv for package/env management
```
# mac
brew install uv

# windows
powershell -c "irm https://astral.sh/uv/install.ps1 | more"

# or install from https://github.com/astral-sh/uv/releases

```

Make an environment and install requirements: 

```

git clone git@github.com:jeffbryner/agno-shiny-gemini-chat.git
cd agno-shiny-gemini-chat
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt

```

Run via: 

```
gcloud config set project <projectid>
python shiny_chat.py
```
which will open a browser window locally that uses gemini in whatever project you have set

