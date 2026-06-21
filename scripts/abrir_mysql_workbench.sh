#!/usr/bin/env bash
set -euo pipefail

# Exemplo didatico/local: abre o MySQL Workbench ja apontando para uma conexao.
# Evite versionar senhas reais em projetos compartilhados.
MYSQL_HOST="127.0.0.1"
MYSQL_PORT="3306"
MYSQL_USER="root"
MYSQL_PASSWORD="sua_senha_aqui"
MYSQL_DATABASE="nome_do_banco"

if ! command -v mysqlworkbench >/dev/null 2>&1; then
  echo "Erro: mysqlworkbench nao foi encontrado no PATH."
  echo "Instale o MySQL Workbench ou abra a conexao manualmente pela interface grafica."
  exit 1
fi

# Algumas versoes do Workbench aceitam abrir o editor SQL por string de conexao.
# Se a sua versao pedir a senha novamente, salve a senha no cofre do proprio Workbench.
CONNECTION_URI="mysql://${MYSQL_USER}:${MYSQL_PASSWORD}@${MYSQL_HOST}:${MYSQL_PORT}/${MYSQL_DATABASE}"

echo "Abrindo MySQL Workbench para ${MYSQL_USER}@${MYSQL_HOST}:${MYSQL_PORT}/${MYSQL_DATABASE}..."
mysqlworkbench --query "${CONNECTION_URI}" >/dev/null 2>&1 &
