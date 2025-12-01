# O Pregador

Projeto local para esboços e ferramentas de apoio ao pregador.

Funcionalidades principais (versão local):
- Editor de esboços por usuário (login simples)
- Salvamento de esboços em `Banco_de_Sermoes/<usuario>`
- Integração opcional com Google Generative AI (chave necessária)
- Busca via DuckDuckGo
- Exemplo com animação Lottie

Como executar (local, usando o `venv` do projeto):

```bash
source /Users/felipefreitas/Desktop/o_pregador/venv/bin/activate
pip install -r requirements.txt
streamlit run app_clean.py
```

Observações:
- Este repositório foi inicializado localmente e está pronto para ser publicado no GitHub.
- Para criar o repositório remoto automaticamente, instale e autentique o GitHub CLI (`gh`) ou forneça um token.
