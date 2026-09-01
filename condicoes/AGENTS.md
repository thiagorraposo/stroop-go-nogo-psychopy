# Condicoes do experimento

Escopo: CSVs-fonte em `condicoes/`. Herda todas as regras da raiz.

- Estes CSVs sao fontes versionadas, nao dados coletados; a excecao de
  `.gitignore` e intencional.
- Antes de mudar cabecalhos, valores ou linhas, localize todas as referencias no
  `.psyexp` e valide a compatibilidade de nomes e tipos.
- Preserve as quatro classificacoes do paradigma e o balanceamento documentado
  em `docs/VALIDACAO_CONDICOES.md`, salvo decisao metodologica explicita.
- Execute os testes estaticos de condicoes e registre qualquer mudanca autorizada
  no protocolo em `docs/DECISOES_DO_EXPERIMENTO.md`.
