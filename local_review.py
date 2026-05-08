"""
WARMUP / ESTUDO — Code review local com Claude Haiku (SEM GitHub Actions).

Use este arquivo para SE FAMILIARIZAR com a lógica do bot de code review
antes de publicar o workflow no GitHub. Aqui o script roda na sua máquina,
lendo um diff fictício e gerando um comentário de review — exatamente o
que vai acontecer dentro do GitHub Action.

Comparação com o exemplo principal:

  scripts/review_pr.py (rodando no GitHub Action):
    PR aberto → checkout → ler diff (gh CLI) → Claude → comment via gh CLI

  local_review.py (este, warmup local):
    diff hardcoded → Claude → print do comentário no terminal

Como rodar (macOS):
    python3 -m venv .venv
    source .venv/bin/activate
    pip3 install -r requirements.txt
    export ANTHROPIC_API_KEY="sua_chave_aqui"
    python3 local_review.py

Como rodar (Windows):
    python -m venv .venv
    .venv\\Scripts\\activate
    pip install -r requirements.txt
    $env:ANTHROPIC_API_KEY="sua_chave_aqui"
    python local_review.py
"""

import os
import time
import anthropic
from anthropic import Anthropic


# ============================================================
# 1. DIFF DE EXEMPLO (em produção viria do gh pr diff)
# ============================================================

SAMPLE_DIFF = """diff --git a/checkout.py b/checkout.py
index 1234567..89abcdef 100644
--- a/checkout.py
+++ b/checkout.py
@@ -10,6 +10,12 @@ class Checkout:
     def __init__(self, items):
         self.items = items

+    def total(self):
+        total = 0
+        for item in self.items:
+            total += item.price * item.qty
+        return total
+
     def apply_discount(self, percent):
-        return self.total * (1 - percent / 100)
+        return self.total() * (1 - percent / 100)
"""

PR_TITLE = "Adiciona método total() ao Checkout"
PR_AUTHOR = "gleica"


# ============================================================
# 2. CLIENTE ANTHROPIC (com retry para 429)
# ============================================================

claude = Anthropic()
MODEL = "claude-haiku-4-5"


def call_claude(prompt: str, max_tokens: int = 600, max_retries: int = 4) -> str:
    """Wrapper com retry exponencial para rate limits."""
    for attempt in range(max_retries):
        try:
            response = claude.messages.create(
                model=MODEL,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text.strip()
        except anthropic.RateLimitError:
            wait = 2 ** attempt
            print(f"⏳ Rate limit. Aguardando {wait}s...")
            time.sleep(wait)
    raise RuntimeError("Rate limit persistiu.")


# ============================================================
# 3. PROMPT DE REVIEW
# ============================================================

REVIEW_INSTRUCTIONS = """Você é um revisor de código sênior. Analise o diff
abaixo de um pull request e produza um comentário CURTO em Markdown contendo:

1. ✅ Pontos positivos (1-2 itens)
2. ⚠️ Problemas encontrados (se houver), com sugestão de correção
3. 💡 Melhorias opcionais (1-2 itens, se aplicável)

Seja objetivo. Use bullet points. Não repita o código no comentário, só
mencione linhas/funções específicas. Limite total: 200 palavras."""


def review_diff(diff: str, title: str, author: str) -> str:
    """Gera o comentário de review para um diff."""
    prompt = (
        f"{REVIEW_INSTRUCTIONS}\n\n"
        f"PR título: {title}\n"
        f"PR autor: @{author}\n\n"
        f"DIFF:\n```diff\n{diff}\n```"
    )
    return call_claude(prompt)


# ============================================================
# 4. RODANDO A DEMO
# ============================================================

if __name__ == "__main__":
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("⚠️  Defina ANTHROPIC_API_KEY antes de rodar.")
        raise SystemExit(1)

    print("=" * 72)
    print(f"📩 Pull Request: {PR_TITLE} (por @{PR_AUTHOR})")
    print("=" * 72)

    print("\n🔍 Diff sendo revisado:")
    print(SAMPLE_DIFF)

    print("=" * 72)
    print("🤖 Comentário gerado pelo Claude:")
    print("=" * 72)
    review = review_diff(SAMPLE_DIFF, PR_TITLE, PR_AUTHOR)
    print()
    print(review)
    print()
    print("=" * 72)
    print("✅ Em produção, esse comentário seria postado no PR via gh CLI.")
    print("   Veja .github/workflows/claude-review.yml + scripts/review_pr.py")
