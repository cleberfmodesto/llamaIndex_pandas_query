"""
Sincroniza apenas app.py e requirements.txt com o HuggingFace Space,
removendo todos os outros arquivos que estiverem lá.
Uso: python sincronizar_hf.py
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from huggingface_hub import HfApi

# ── Configurações ──────────────────────────────────────────────
load_dotenv()

TOKEN     = os.environ.get("HF_TOKEN")
REPO_ID   = "cleberfmodesto/llamaIndex_pandas_query"
REPO_TYPE = "space"

# Apenas estes arquivos devem existir no Space
ARQUIVOS_PERMITIDOS = {"app.py", "requirements.txt"}

# ── Main ───────────────────────────────────────────────────────
def main():
    if not TOKEN:
        raise EnvironmentError(
            "❌ HF_TOKEN não encontrado. "
            "Verifique se está no arquivo .env como HF_TOKEN=\"hf_...\""
        )

    api = HfApi(token=TOKEN)

    usuario = api.whoami()["name"]
    print(f"✅ Autenticado como: {usuario}")

    raiz = Path(__file__).parent

    # ── 1. Remove arquivos indesejados do Space ────────────────
    print("\n🗑️  Verificando arquivos no Space para remover...")
    arquivos_no_space = api.list_repo_files(repo_id=REPO_ID, repo_type=REPO_TYPE)
    removidos = 0
    for arquivo_remoto in arquivos_no_space:
        # Mantém apenas os arquivos permitidos e o .gitattributes (do HF)
        nome_base = arquivo_remoto.split("/")[0]
        if arquivo_remoto not in ARQUIVOS_PERMITIDOS and not arquivo_remoto.startswith(".git"):
            api.delete_file(
                path_in_repo=arquivo_remoto,
                repo_id=REPO_ID,
                repo_type=REPO_TYPE,
                commit_message=f"remove: {arquivo_remoto}",
            )
            print(f"   🗑️  Removido: {arquivo_remoto}")
            removidos += 1

    if removidos == 0:
        print("   Nenhum arquivo para remover.")

    # ── 2. Envia app.py e requirements.txt ────────────────────
    print(f"\n🚀 Enviando arquivos para: https://huggingface.co/spaces/{REPO_ID}")
    for nome in ARQUIVOS_PERMITIDOS:
        caminho = raiz / nome
        if not caminho.exists():
            print(f"   ⚠️  {nome} não encontrado localmente, pulando.")
            continue
        api.upload_file(
            path_or_fileobj=str(caminho),
            path_in_repo=nome,
            repo_id=REPO_ID,
            repo_type=REPO_TYPE,
            commit_message=f"sync: {nome}",
        )
        print(f"   ✔ {nome}")

    print(f"\n🎉 Sincronização concluída!")
    print(f"   👉 https://huggingface.co/spaces/{REPO_ID}")


if __name__ == "__main__":
    main()

