"""
Script que roda DENTRO do GitHub Action (claude-review.yml).

Fluxo:
  1. Lê o diff do PR (entre base.sha e head.sha)
  2. Pede review pro Claude Haiku
  3. Posta o comentário no PR via gh CLI

Variáveis de ambiente esperadas (vêm do workflow):
  ANTHROPIC_API_KEY · GITHUB_TOKEN · PR_NUMBER · PR_TITLE
  PR_AUTHOR · BASE_SHA · HEAD_SHA · REPO
"""

import os
import time
import subprocess
import anthropic
from anthropic import Anthropic


claude = Anthropic()
MODEL = "claude-haiku-4-5"
MAX_DIFF_CHARS = 30_000   # limite para não estourar o context window


def call_claude(prompt: str, max_tokens: int = 600, max_retries: int = 4) -> str:
    """Wrapper com retry exponencial para 429."""
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
    raise RuntimeError("Rate limit persistiu após múltiplas tentativas.")


def get_diff(base_sha: str, head_sha: str) -> str:
    """Pega o diff entre as duas commits via git."""
    result = subprocess.run(
        ["git", "diff", f"{base_sha}...{head_sha}"],
        capture_output=True, text=True, check=True,
    )
    diff = result.stdout
    if len(diff) > MAX_DIFF_CHARS:
        diff = diff[:MAX_DIFF_CHARS] + "\n\n[... diff truncado para caber no context window ...]"
    return diff


REVIEW_INSTRUCTIONS = """Você é um revisor de código sênior. Analise o diff abaixo de um pull request e produza um comentário em Markdown contendo:

1. ✅ Pontos positivos (1-2 itens)
2. ⚠️ Problemas encontrados (se houver), com sugestão de correção
3. 💡 Melhorias opcionais (1-2 itens, se aplicável)

Seja objetivo. Use bullet points. Não repita o código no comentário, só mencione linhas/funções específicas. Limite total: 250 palavras."""


def post_comment(pr_number: str, repo: str, body: str):
    """Posta um comentário no PR via gh CLI (já autenticado pelo GITHUB_TOKEN)."""
    subprocess.run(
        ["gh", "pr", "comment", pr_number, "--repo", repo, "--body", body],
        check=True,
    )


def main():
    pr_number = os.environ["PR_NUMBER"]
    pr_title  = os.environ["PR_TITLE"]
    pr_author = os.environ["PR_AUTHOR"]
    base_sha  = os.environ["BASE_SHA"]
    head_sha  = os.environ["HEAD_SHA"]
    repo      = os.environ["REPO"]

    print(f"🔍 Revisando PR #{pr_number}: {pr_title} (@{pr_author})")

    diff = get_diff(base_sha, head_sha)
    print(f"📄 Diff capturado: {len(diff)} chars")

    prompt = (
        f"{REVIEW_INSTRUCTIONS}\n\n"
        f"PR título: {pr_title}\n"
        f"PR autor: @{pr_author}\n\n"
        f"DIFF:\n```diff\n{diff}\n```"
    )
    review = call_claude(prompt)

    body = f"## 🤖 Claude PR Review\n\n{review}\n\n---\n*Gerado automaticamente · `claude-haiku-4-5`*"
    post_comment(pr_number, repo, body)
    print("✅ Comentário postado no PR.")


if __name__ == "__main__":
    main()
