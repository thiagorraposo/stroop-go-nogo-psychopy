# Implantação WEB na VPS HostGator e Integração ao GitHub Flow

Este documento estabelece os procedimentos operacionais e mecanismos técnicos de implantação da aplicação WEB na VPS HostGator existente (`strooptest.thiagorraposo.dev`), integrados ao **GitHub Flow** com Pull Request, Push e Merge Commit tradicional.

Decisões arquiteturais associadas: [ADR-002](../arquitetura/ADR-002-hospedagem-vps.md) (hospedagem VPS), [ADR-004](../arquitetura/ADR-004-replanejamento-plataforma.md) (replanejamento da plataforma web), [ADR-006](../arquitetura/ADR-006-autenticacao-local.md) (autenticação profissional local) e governança em [CONTRIBUTING.md](../../CONTRIBUTING.md) e [WORKFLOW_CODEX_CLI.md](../WORKFLOW_CODEX_CLI.md).

> [!IMPORTANT]
> O repositório adota **deploy controlado sob demanda** (`workflow_dispatch`). O merge de Pull Requests na `main` **não** executa deploy automático. A implantação de releases em produção requer autorização explícita do responsável e validação prévia na CI. O marco M10 do backlog canônico reserva a implantação formal e não é antecipado implicitamente.

---

## 1. Visão Geral e Infraestrutura

A aplicação Stroop Web está hospedada em uma VPS dedicada na HostGator Brasil, configurada exclusivamente para o projeto:

| Parâmetro | Valor / Configuração |
|---|---|
| **URL Pública** | `https://strooptest.thiagorraposo.dev` |
| **Acesso SSH** | `raposo@108.174.145.177`, porta `22022`, chave OpenSSH Ed25519 |
| **Sistema Operacional** | Ubuntu 22.04.5 LTS (Jammy Jellyfish), kernel 6.8 |
| **Recursos de Hardware** | 2 vCPUs AMD EPYC, 4 GB RAM, 98 GB SSD (11% ocupado) |
| **Motor de Contêineres** | Docker Engine 29.8+, Docker Compose v5+ |
| **Diretório da Aplicação** | `/home/raposo/stroop-web` |
| **Release Ativa** | Symlink `/home/raposo/stroop-web/current` apontando para a release atual |
| **Arquivo de Ambiente** | `/home/raposo/stroop-web/web.env` (permissão `0600`, fora do repositório) |
| **Secrets Operacionais** | `/home/raposo/.local/share/stroop-web/secrets` (`0700` diretório, `0600` arquivos) |
| **Certificado TLS** | Let's Encrypt (ECDSA), renovado via Certbot webroot (`acme/`) |
| **Portas Públicas** | `80/tcp` (redirecionamento HTTPS) e `443/tcp` (TLS 1.3 Nginx proxy) |
| **Portas Internas** | `5432` (PostgreSQL) e `8000` (FastAPI) restritas às redes internas Docker |
| **Persistência WEB** | Volume Docker nomeado `stroop-web_web_postgres_data` |

Nenhum arquivo `.env` com credenciais, chave privada ou dump de dados é versionado no Git.

---

## 2. Ciclo de Desenvolvimento e GitHub Flow com Deploy

O fluxo de entrega do projeto preserva rigorosamente as seguintes etapas:

```
Branch de entrega (feat/fix/docs)
      │
      ▼
Commit convencional em português
      │
      ▼
Push com upstream (git push -u origin BRANCH)
      │
      ▼
Pull Request para a main (gh pr create)
      │
      ▼
CI remota obrigatória (job verify em web.yml)
      │
      ▼
Merge Commit tradicional na main (gh pr merge --merge)
      │
      ▼
Deploy controlado sob demanda (workflow_dispatch em deploy.yml)
      │
      ▼
Validação do SHA, status da CI e healthchecks pós-deploy
```

### Regras do fluxo integrado
1. **Reaproveitamento de CI sem duplicação:** O workflow `WEB validada` (`.github/workflows/web.yml`) é a fonte única de verificação automatizada (`verify`). O pipeline de deploy **não duplica** testes unitários, testes de navegador ou scanner de segredos; ele valida diretamente que o SHA alvo já foi aprovado com sucesso pelo job `verify`.
2. **Merge tradicional obrigatório:** Nunca utilizar Squash Merge, Rebase Merge ou push direto na `main`. Todos os commits da branch de entrega são preservados como ancestrais de `origin/main`.
3. **Deploy desacoplado do merge:** O merge na `main` integra o código aprovado, mas não toca na VPS. O deploy ocorre em momento controlado através do workflow `Deploy VPS HostGator` (`.github/workflows/deploy.yml`).

---

## 3. Configuração de Secrets e Proteção do Environment no GitHub

Para habilitar a execução do deploy via GitHub Actions, as credenciais de acesso à VPS e as proteções de ambiente devem ser configuradas na interface do GitHub:

### 3.1 Proteção do Environment `production`
1. Navegue até **Settings** → **Environments** → **New environment** → nome: `production`.
2. Em **Deployment protection rules**:
   - Ative **Required reviewers** e adicione os revisores autorizados (ex.: mantenedor do repositório). Isso garante que nenhum deploy execute sem aprovação humana expressa no GitHub.
   - Ative **Deployment branches** e configure para aceitar **apenas** a branch `main` (`Selected branches` → `main`).
3. Em **Environment URL**, informe: `https://strooptest.thiagorraposo.dev`.

### 3.2 Secrets do Repositório / Environment
Configure as seguintes secrets em **Settings** → **Secrets and variables** → **Actions** (ou vinculadas ao environment `production`):

| Secret | Descrição | Exemplo / Formato |
|---|---|---|
| `HOSTGATOR_SSH_HOST` | IP ou DNS público da VPS | `108.174.145.177` |
| `HOSTGATOR_SSH_PORT` | Porta do serviço OpenSSH | `22022` |
| `HOSTGATOR_SSH_USER` | Usuário do sistema na VPS | `raposo` |
| `HOSTGATOR_SSH_KEY` | Chave privada OpenSSH sem passphrase | Conteúdo de `id_ed25519` (iniciando em `-----BEGIN OPENSSH PRIVATE KEY-----`) |
| `HOSTGATOR_KNOWN_HOSTS` | Linha de hostkey pública da VPS | `[108.174.145.177]:22022 ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAI...` |

> [!CAUTION]
> Nunca versione a chave privada SSH ou a coloque em arquivos monitorados pelo Git. A ferramenta de verificação do CI (`verify_web_ci.py`) e o scanner Gitleaks bloqueiam commits que contenham padrões de chaves sensíveis.

---

## 4. Como Executar um Deploy Manual Autorizado

### 4.1 Via Interface Web do GitHub (Recomendado)
1. Acesse a aba **Actions** no repositório.
2. Na barra lateral esquerda, clique em **Deploy VPS HostGator**.
3. Clique no botão **Run workflow** (no canto superior direito):
   - **Branch**: Selecione `main`.
   - **commit_sha**: Deixe em branco para implantar o `HEAD` da `main`, ou informe o SHA exato de 40 caracteres a ser publicado.
   - **dry_run**: Mantenha desmarcado (`false`) para deploy real, ou marque (`true`) para realizar simulação sem alterações remotas.
   - **skip_ci_check**: Mantenha desmarcado (`false`).
4. Clique em **Run workflow**.
5. Se o Environment `production` exigir aprovação, o revisor receberá notificação e deverá aprovar a execução na interface do GitHub.

### 4.2 Via GitHub CLI (`gh`)
Para acionar o deploy pelo terminal:

```bash
# Simulação sem efeitos colaterais na VPS (dry-run):
gh workflow run deploy.yml -f commit_sha="HEAD" -f dry_run=true

# Deploy real autorizado da versão integrada na main:
gh workflow run deploy.yml -f commit_sha="b5fccbbd5e199e0312467b26486a7734448e20c8" -f dry_run=false

# Acompanhar a execução do job:
gh run list --workflow=deploy.yml
gh run watch
```

### 4.3 Via Utilitário Local Direto (`scripts/deploy_vps.py`)
Um operador devidamente autorizado com chave SSH local configurada em `~/.ssh/` pode executar o script canônico diretamente:

```bash
# Validação de integridade do SHA e status na CI:
python3 scripts/deploy_vps.py validate --commit HEAD

# Simulação completa de deploy:
python3 scripts/deploy_vps.py deploy --commit HEAD --dry-run

# Execução real com chave privada local:
python3 scripts/deploy_vps.py deploy \
  --commit HEAD \
  --ssh-host 108.174.145.177 \
  --ssh-port 22022 \
  --ssh-user raposo \
  --ssh-key-file ~/.ssh/hostgator_stroop_ed25519
```

---

## 5. Sequência Técnica de Atualização na VPS

O script `scripts/deploy_vps.py` orquestra a implantação seguindo 8 etapas atômicas:

1. **Validação pré-voo:**
   - Valida que o SHA informado possui 40 caracteres hexadecimais válidos.
   - Confirma que o commit pertence à branch estável `main`.
   - Consulta a API do GitHub Actions para garantir que o check `verify` foi concluído com `success`.
2. **Conectividade SSH:**
   - Testa a autenticação via chave SSH e a resolução da VPS com timeout seguro.
3. **Snapshot e Salvaguarda Pré-Deploy:**
   - Executa backup criptografado do banco PostgreSQL com a chave `/home/raposo/.local/share/stroop-web/keys/predeploy.key`.
   - Grava snapshot de segurança de `web.env` em `web.env.pre-deploy`.
   - Registra o caminho da release anterior ativa em `/home/raposo/stroop-web/previous_release`.
4. **Criação do Diretório de Release:**
   - Cria `/home/raposo/stroop-web/releases/<SHA>`.
   - Gera o manifesto imutável `release.json` com SHA, timestamp UTC, autor e tags das imagens.
5. **Atualização Controlada das Tags de Imagem:**
   - Atualiza `WEB_API_IMAGE=stroop-web-api:deploy-<SHA>` e `WEB_PROXY_IMAGE=stroop-web-proxy:deploy-<SHA>` no arquivo `web.env`.
   - Nenhuma credencial ou variável de conexão é modificada.
6. **Migrations e Permissões:**
   - Executa migrations pendentes de forma idempotente via contêiner efêmero `web-migrate`.
   - Executa provisionamento de papéis e privilégios via `web-provision`.
7. **Chaveamento Atômico de Tráfego:**
   - Atualiza o symlink de produção: `ln -sfn /home/raposo/stroop-web/releases/<SHA> /home/raposo/stroop-web/current`.
   - Recria os contêineres de aplicação (`web-api` e `web-proxy`) com `--wait` via Compose:
     ```bash
     docker compose --project-name stroop-web --env-file web.env \
       -f current/compose.web.yaml -f compose.vps.yaml \
       --profile web up -d --no-deps --no-build --wait web-api web-proxy
     ```
   - O contêiner de banco de dados (`web-postgres`) e seu volume persistente são preservados sem reinicialização.
8. **Healthcheck Pós-Deploy:**
   - Sonda o endpoint público de prontidão `https://strooptest.thiagorraposo.dev/health/ready` por até 8 tentativas.
   - Em caso de insucesso, dispara rollback automático imediato.

---

## 6. Verificação do SHA Publicado e Monitoramento

Após o deploy, confirme a integridade da versão em produção:

### 6.1 Verificação do Endpoint HTTPS
```bash
# Prontidão da aplicação:
curl -fsS https://strooptest.thiagorraposo.dev/health/ready
# Esperado: {"status":"ready"}

# Verificação do cabeçalho de segurança e redirecionamento:
curl -I https://strooptest.thiagorraposo.dev/
```

### 6.2 Inspecionando o Manifesto Remoto na VPS
No terminal SSH da VPS:

```bash
# Ler o manifesto da release ativa:
cat /home/raposo/stroop-web/current/release.json

# Verificar a saúde dos contêineres:
docker compose --project-name stroop-web --env-file /home/raposo/stroop-web/web.env \
  -f /home/raposo/stroop-web/current/compose.web.yaml -f /home/raposo/stroop-web/compose.vps.yaml \
  --profile web ps

# Executar diagnóstico pelo script oficial de monitoramento:
python3 /home/raposo/stroop-web/current/scripts/monitor_web.py \
  --env-file /home/raposo/stroop-web/web.env --project-name stroop-web
```

---

## 7. Investigação de Falhas e Procedimento de Rollback

### 7.1 Rollback Automático
O script `deploy_vps.py` aciona rollback automático sempre que:
- Ocorrer erro durante a execução de migrations ou provisionamento de papéis;
- A recriação dos contêineres `web-api` ou `web-proxy` falhar;
- O healthcheck público `/health/ready` não responder HTTP 200 dentro do tempo limite estipulado.

O rollback automático restaura imediatamente o symlink `current` para a release gravada em `previous_release`, reaplica o `web.env.pre-deploy` e recria os contêineres na versão anterior estável, finalizando com código de saída 1 para alertar os operadores.

### 7.2 Rollback Manual Rápido (RTO < 30s)
Caso seja necessário reverter manualmente uma versão com anomalia funcional:

#### Opção A: Pelo utilitário local
```bash
python3 scripts/deploy_vps.py rollback \
  --ssh-host 108.174.145.177 \
  --ssh-port 22022 \
  --ssh-user raposo \
  --ssh-key-file ~/.ssh/hostgator_stroop_ed25519
```

#### Opção B: Diretamente na VPS via script canônico
```bash
# Reverte para a release anterior gravada em previous_release:
sh /home/raposo/stroop-web/current/deploy/vps-web-rollback.sh

# Ou especificando uma release conhecida:
sh /home/raposo/stroop-web/current/deploy/vps-web-rollback.sh 26fa9bf
```

### 7.3 Rollback Emergencial para a Stack Streamlit Legada
Se houver falha catastrófica de infraestrutura que impeça a stack React/FastAPI de subir, a VPS preserva os contêineres legados do Streamlit (`stroop-production-dashboard-1` e `stroop-production-proxy-1`). O retorno pode ser executado via:

```bash
sh /home/raposo/stroop-web/deploy/vps-rollback.sh
```

Esse script desativa o proxy WEB e religa o proxy legado nas portas 80/443, confirmando resposta HTTPS em `/_stcore/health` antes de concluir.

---

## 8. Condições para Habilitar Deploy Automático no Futuro

Atualmente, o deploy automático em push na `main` é **proibido por governança** (marcos M8–M10 do backlog). Para que um gatilho de Continuous Deployment (CD) direto após o merge possa ser habilitado no futuro, os seguintes pré-requisitos técnicos e institucionais devem ser atendidos:

1. **Aprovação Formal dos Marcos M8, M9 e M10:**
   - Conclusão e aceite da réplica externa independente e runbooks de recuperação (`WEB-031` e `WEB-032`).
   - Validação metodológica e temporal do experimento em ambiente controlado (`WEB-034` e `WEB-036`).
   - Conclusão da homologação e handoff operacional (`WEB-037` a `WEB-040`).
2. **Decisão Institucional DEC-05:**
   - Autorização expressa do coordenador da pesquisa e do responsável pelo repositório para transição para o modo operacional contínuo.
3. **Maturidade e Idempotência Total de Migrations:**
   - Comprovação de que todas as alterações de schema do banco relacional são puramente aditivas e compatíveis retroativamente (Zero Downtime Migrations / expand-contract pattern).
4. **Infraestrutura de Observabilidade Remota:**
   - Notificações automatizadas (ex.: webhook Slack/Discord ou e-mail seguro) informando sobre deploys realizados e alertas de falha no monitor agendado.

Enquanto essas condições não forem formalizadas, o acionamento via `workflow_dispatch` permanece a única via homologada de publicação.
