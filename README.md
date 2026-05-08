# Demos — GitHub e CI/CD

Código pronto-pra-rodar das demos do tema. Setup escrito para **macOS** (com inputs para Windows ao lado quando aplicável).

> Se for a primeira vez que você usa Python no Mac e o `python3` não responder: `brew install python@3.13`.

---

## Os arquivos e quando usar cada um

| Arquivo | Quando rodar | Precisa de |
|---|---|---|
| **`local_review.py`** | Warmup — antes da gravação, pra entender o fluxo do code review sem precisar do GitHub Action | Apenas `ANTHROPIC_API_KEY` |
| **`.github/workflows/claude-review.yml`** | **Demo principal da aula** — workflow real que roda em todo PR do GitHub | Repo no GitHub + secret `ANTHROPIC_API_KEY` |
| **`.github/scripts/review_pr.py`** | Script Python que o workflow chama dentro do runner | Anthropic SDK (instalado pelo workflow) |
| **`example-bug.py`** | Arquivo com bugs sutis para gerar um PR de exemplo e ver o bot agir | Só pra demo |

---

## Setup base (uma vez só)

### macOS

```bash
brew install gh                    # GitHub CLI (opcional, facilita autenticação)
gh auth login                      # autenticar no GitHub

cd demos/
python3 -m venv .venv
source .venv/bin/activate
pip3 install --upgrade pip
pip3 install -r requirements.txt
export ANTHROPIC_API_KEY="sk-ant-..."
```

### Windows (PowerShell)

```powershell
winget install --id GitHub.cli     # GitHub CLI
gh auth login

cd demos\
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
$env:ANTHROPIC_API_KEY="sk-ant-..."
```

---

## Warmup — `local_review.py` 🔍

Use **antes** de configurar o workflow no GitHub. Roda 100% local: lê um diff fictício e gera o comentário de review usando Claude Haiku. Mesma lógica que o script vai ter dentro do GitHub Action.

```bash
python3 local_review.py
```

Você vai ver:
1. O diff sendo revisado (em um arquivo `checkout.py`)
2. O comentário gerado pelo Claude com pontos positivos, problemas e sugestões

---

## Demo principal — Bot de PR Review no GitHub Actions 🤖

**Este é o exemplo gravado na aula.** Configura um bot que comenta automaticamente em todo PR aberto.

### Passo 1 — Crie/use um repo no GitHub

```bash
# Opcional: criar um repo de teste vazio
gh repo create flowgrammers-claude-review-demo --public --clone
cd flowgrammers-claude-review-demo
```

### Passo 2 — Configure o secret no GitHub

No painel do repo: **Settings → Secrets and variables → Actions → New repository secret**

- **Name**: `ANTHROPIC_API_KEY`
- **Value**: sua chave (`sk-ant-...`)

Ou via gh CLI:

```bash
gh secret set ANTHROPIC_API_KEY --body "sk-ant-..."
```

### Passo 3 — Copie os arquivos do workflow

Copie a pasta `.github/` deste demo para a raiz do seu repo:

```bash
cp -r demos/.github /caminho/para/seu/repo/
cd /caminho/para/seu/repo
git add .github
git commit -m "Adiciona Claude PR Review workflow"
git push
```

### Passo 4 — Abra um PR de teste

```bash
git checkout -b test/code-review
cp /caminho/para/demos/example-bug.py checkout.py
git add checkout.py
git commit -m "Adiciona checkout com bugs intencionais"
git push -u origin test/code-review
gh pr create --title "Test: bot de review" --body "PR para testar o bot"
```

### Passo 5 — Veja o bot agir

Abra o PR no navegador. Em ~30s o workflow roda e o Claude posta o review como comentário.

---

## Troubleshooting

| Erro | Causa | Solução |
|---|---|---|
| `Resource not accessible by integration` | Permissões insuficientes | Confirme que o workflow tem `permissions: pull-requests: write` |
| Workflow não dispara | Branch protection / Action desabilitada | Settings → Actions → General → permitir workflows |
| `ANTHROPIC_API_KEY not found` | Secret não configurado | Settings → Secrets → Adicione `ANTHROPIC_API_KEY` |
| HTTP 429 (Anthropic) | Tier 1 estourou | Aguarde 60s OU adicione US$5 em console.anthropic.com |
| `gh: command not found` (Mac) | gh CLI não instalado | `brew install gh` |
| `gh: command not found` (Win) | gh CLI não instalado | `winget install --id GitHub.cli` |

---

## Variações se sobrar tempo na demo (até 20 min)

- **Subagentes paralelos**: split do review em "qualidade", "segurança" e "performance" rodando em paralelo
- **Auto-fix**: aplicar correções via Claude e dar push automático no PR
- **Trigger manual**: adicionar `workflow_dispatch` para rodar review on-demand
- **Filtro de arquivos**: revisar apenas `*.py` ou pastas específicas (`paths:` no trigger)
- **Trigger por comment**: rodar review apenas quando alguém comentar `@claude review`

---

## Anthropic Action oficial (alternativa)

Existe também a [`anthropics/claude-code-action`](https://github.com/anthropics/claude-code-action) — uma Action oficial que abstrai o setup. É mais "production-ready" mas menos didática para entender o que está acontecendo. Para a aula, usamos o caminho do Python direto.

Se quiser usar a Action oficial em produção, o YAML fica assim (versão simplificada):

```yaml
- uses: anthropics/claude-code-action@v1
  with:
    anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
    prompt: "Revise este PR"
```
