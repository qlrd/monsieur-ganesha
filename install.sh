#!/usr/bin/env bash
# install.sh — configura monsieur-ganesha no repositório da piscine
set -euo pipefail

HOOKS_REPO="https://github.com/qlrd/monsieur-ganesha"
CONFIG_FILE=".pre-commit-config.yaml"
TOML_FILE=".ganesha.toml"
DAWON_TOML=".dawon.toml"
DAWON_REPO="https://github.com/qlrd/dawon"
DAWON_BIN_DIR="$HOME/.local/bin"

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

# 6. Instalar dawon (companion evaluator)
echo "  -> Verificando dawon..."
if command -v dawon &>/dev/null; then
    echo "  -> dawon já instalado: $(dawon --version 2>/dev/null || echo 'versão desconhecida')"
else
    # Detect OS/arch for future pre-built binary downloads (issue qlrd/dawon#64)
    _os="$(uname -s)"
    _arch="$(uname -m)"
    _asset=""
    if [ "$_os" = "Linux" ] && [ "$_arch" = "x86_64" ]; then
        _asset="dawon-linux-x86_64"
    elif [ "$_os" = "Linux" ] && [ "$_arch" = "aarch64" ]; then
        _asset="dawon-linux-aarch64"
    elif [ "$_os" = "Darwin" ] && [ "$_arch" = "arm64" ]; then
        _asset="dawon-macos-aarch64"
    elif [ "$_os" = "Darwin" ] && [ "$_arch" = "x86_64" ]; then
        _asset="dawon-macos-x86_64"
    fi

    _installed=0
    # Try pre-built binary first (available once qlrd/dawon#64 is merged)
    if [ -n "$_asset" ]; then
        _url="https://github.com/qlrd/dawon/releases/latest/download/$_asset"
        mkdir -p "$DAWON_BIN_DIR"
        if command -v curl &>/dev/null; then
            if curl -fsSL "$_url" -o "$DAWON_BIN_DIR/dawon" 2>/dev/null; then
                chmod +x "$DAWON_BIN_DIR/dawon"
                _installed=1
                echo "  -> dawon instalado em $DAWON_BIN_DIR/dawon"
            fi
        elif command -v wget &>/dev/null; then
            if wget -qO "$DAWON_BIN_DIR/dawon" "$_url" 2>/dev/null; then
                chmod +x "$DAWON_BIN_DIR/dawon"
                _installed=1
                echo "  -> dawon instalado em $DAWON_BIN_DIR/dawon"
            fi
        fi
    fi

    # Fallback: cargo install (requires Rust)
    if [ "$_installed" -eq 0 ]; then
        if command -v cargo &>/dev/null; then
            echo "  -> Instalando dawon via cargo (pode demorar)..."
            if cargo install --git "$DAWON_REPO" 2>/dev/null; then
                _installed=1
                echo "  -> dawon instalado em ~/.cargo/bin/dawon"
                echo ""
                echo "  ATENÇÃO: adicione ~/.cargo/bin ao PATH se ainda não estiver:"
                echo "    echo 'export PATH=\"\$HOME/.cargo/bin:\$PATH\"' >> ~/.zshrc"
            fi
        fi
    fi

    if [ "$_installed" -eq 0 ]; then
        echo ""
        echo "  AVISO: dawon não foi instalado automaticamente."
        echo "  Para instalar manualmente, escolha uma opção:"
        echo ""
        echo "  Opção A — binário pré-compilado (recomendado):"
        echo "    mkdir -p ~/.local/bin"
        echo "    curl -fsSL https://github.com/qlrd/dawon/releases/latest/download/dawon-linux-x86_64 \\"
        echo "      -o ~/.local/bin/dawon && chmod +x ~/.local/bin/dawon"
        echo ""
        echo "  Opção B — compilar com Rust:"
        echo "    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh"
        echo "    cargo install --git $DAWON_REPO"
        echo ""
    fi

    # Advise PATH if dawon was placed in ~/.local/bin
    if [ "$_installed" -eq 1 ] && [[ ":$PATH:" != *":$DAWON_BIN_DIR:"* ]]; then
        echo ""
        echo "  ATENÇÃO: $DAWON_BIN_DIR não está no PATH."
        echo "  Adicione ao seu shell (zsh/bash):"
        echo "    echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.zshrc"
        echo "  Depois recarregue: source ~/.zshrc"
        echo ""
    fi
fi

# 7. Instalar hooks no git
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
echo "  4. Antes de dar push: dawon check --path ."
