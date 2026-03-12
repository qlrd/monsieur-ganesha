#!/usr/bin/env bash
# install.sh — configura monsieur-ganesha no repositório da piscine
set -euo pipefail

HOOKS_REPO="https://github.com/qlrd/monsieur-ganesha"
CONFIG_FILE=".pre-commit-config.yaml"
TOML_FILE=".ganesha.toml"
DAWON_TOML=".dawon.toml"

echo "==> monsieur-ganesha: configurando hooks para piscine 42..."

# 1. Configurar editor git como vim
echo "  -> Configurando git editor como vim..."
git config --global core.editor vim

# 2. Instalar pre-commit
if ! command -v pre-commit &>/dev/null; then
    echo "  -> Instalando pre-commit..."
    if command -v uv &>/dev/null; then
        uv tool install pre-commit
    elif command -v pip3 &>/dev/null; then
        pip3 install --user pre-commit
    else
        echo "ERRO: pip3 ou uv não encontrado. Instale Python 3 primeiro."
        exit 1
    fi
fi

# 3. Criar .pre-commit-config.yaml se não existir
if [ ! -f "$CONFIG_FILE" ]; then
    echo "  -> Criando $CONFIG_FILE..."
    cat > "$CONFIG_FILE" <<EOF
repos:
  - repo: $HOOKS_REPO
    rev: v0.1.2
    hooks:
      - id: norminette
      - id: c-compiler
      - id: forbidden-functions
      - id: commit-message
EOF
    echo "     Criado! Edite 'rev' para a versão desejada."
else
    echo "  -> $CONFIG_FILE já existe, pulando."
fi

# 4. Criar .ganesha.toml template se não existir
if [ ! -f "$TOML_FILE" ]; then
    echo "  -> Criando $TOML_FILE (template)..."
    cat > "$TOML_FILE" <<'EOF'
[project]
# Nome do módulo atual (C00, C01, rush01, etc.)
name = "C00"
# Caminho opcional para dawon-check no pre-push
# module = "C00"

[forbidden]
# Funções proibidas para este subject — consulte o PDF
functions = ["printf", "malloc", "realloc", "free", "calloc"]

[commit]
# Padrão padrão: Conventional Commits 1.0.0
# Para usar o formato 42-school, descomente a linha abaixo:
# pattern = "^(ex|rush|exam)\\d+: .+"
EOF
    echo "     Criado! Edite .ganesha.toml com as funções do seu subject."
else
    echo "  -> $TOML_FILE já existe, pulando."
fi

# 5. Criar .dawon.toml template se não existir (companion evaluator)
if [ ! -f "$DAWON_TOML" ]; then
    echo "  -> Criando $DAWON_TOML (template para dawon)..."
    cat > "$DAWON_TOML" <<'EOF'
[project]
# Módulo atual: C00, C01, rush00, etc.
# module = "C00"

[checks]
# Descomente para desativar checks opcionais:
# no_sanitizers = true
# no_valgrind   = true
EOF
    echo "     Criado! Edite .dawon.toml se necessário."
else
    echo "  -> $DAWON_TOML já existe, pulando."
fi

# 6. Instalar hooks no git
echo "  -> Instalando hooks no git..."
pre-commit install
pre-commit install --hook-type commit-msg

echo ""
echo "Pronto! Hooks instalados."
echo ""
echo "Próximos passos:"
echo "  1. Edite .ganesha.toml com as funções proibidas do seu subject"
echo "  2. Teste: git add . && git commit -m 'feat: minha implementação'"
echo "  3. Check manual: pre-commit run --all-files"
echo "  4. Antes de dar push: dawon check --path . (se dawon estiver instalado)"
