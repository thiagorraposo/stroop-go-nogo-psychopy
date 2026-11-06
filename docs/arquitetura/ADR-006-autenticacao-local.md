# ADR-006 — Autenticação profissional local com conta administrativa única

Data: 2026-11-06. Decisão de produto/arquitetura/segurança aprovada pelo
proprietário na missão documental CHG-004. **Implementação PLANEJADA**.
Estado, tarefas, riscos, evidências e aceite somente no
[backlog canônico](../Projeto%20Stroop%20Test.md). Complementa ADR-004, sem
revogar DEC-01–05, isolamento por projeto ou metodologia.

## Contexto e decisão durável

Retirar a dependência Google para acesso profissional na versão alvo WEB.
Login por usuário e senha validados exclusivamente no FastAPI; uma conta local
com perfil `administracao`, sem cadastro público nem autenticação externa
obrigatória. Múltiplas contas são extensão futura, não parte desta entrega.
Manter identidade técnica estável separada de credencial mutável e de vínculo
por projeto. Não simular claims Google para representar uma conta local.

A conta gerencia contas/projetos/vínculos conforme permissões existentes; só
consulta/exporta/prepara convites em projetos com vínculo explícito ativo.
O provisionamento não concede vínculos automaticamente. O emissor técnico de
convites e eventos identifica a conta, nunca cada profissional que a utiliza.
Compartilhamento provisório não equivale a autenticação individual ou assinatura
pessoal; uso com dados reais depende de avaliação institucional DEC-03.

## Fluxo e responsabilidades

React apresenta formulário profissional acessível, com usuário/senha, rótulos,
foco/teclado, loading e erros genéricos, compatível com gerenciador de senhas;
não muda gráficos/métricas/layout do dashboard. Contrato HTTP alvo e limites
ficam exclusivamente no [contrato API](../desenvolvimento/CONTRATO_API_WEB.md#autenticação-local--contrato-alvo-chg-004).
Backend limita tentativas antes de trabalho criptográfico, verifica senha por
biblioteca mantida Argon2id, revalida conta e emite nova sessão opaca. Guards
revalidam bloqueio, sessão e permissões/vínculos em cada operação; React não
autoriza. Cookie seguro e CSRF em RAM preservam separação participante/profissional.
Logout revoga no servidor; senha alterada/recuperada revoga todas as sessões.

Regras de senha, antiabuso, sessões e procedimento administrativo são a fonte
normativa em [autenticação](../seguranca/AUTENTICACAO_E_PERMISSOES.md#autenticação-local--especificação-alvo-chg-004).
Hashes, identidade e versão de credencial ficam no servidor. O domínio mantém
políticas puras; caso de uso coordena transação e adaptador criptográfico, sem
importar FastAPI, CLI, React ou Streamlit. Não criar serviço externo novo.

## Banco e migração incremental

Modelo aditivo e proteção de histórico no
[modelo de dados](../dados/MODELO_DE_DADOS.md#autenticação-local--evolução-aditiva-planejada-chg-004).
A implementação futura de WEB-021 deve primeiro fechar DDL/grants e contrato
administrativo na mesma unidade, testar em PG descartável e depois integrar API
/React/configuração. Nenhum dado real pode ser migrado por esta decisão.
Migrations 0001–0011 são imutáveis. Identidades legadas `iss/sub`, FKs de
projetos/convites/auditoria e resultado não podem ser renomeados ou reassociados
por e-mail, nome ou por serem da mesma equipe.

Adicionar representação local separada das identidades Google, com vínculo
explícito à autorização e à proveniência técnica; preservar capacidade de
representar vários principais sem habilitar criação de múltiplas contas agora.
A conta local recebe somente vínculos concedidos expressamente; nenhum backfill
apropria projetos. Sessões locais têm prazos próprios, sem `oidc_expires_at`
fictício. DDL exato é entrega futura, sujeito aos testes de compatibilidade.

Corte só após integração local e regressões aceitas em WEB-021/024: configuração
WEB deixa de exigir cliente Google, endpoints OIDC deixam de autenticar na
versão alvo e sessões OIDC antigas são invalidadas. Não deixar fallback oculto
para contornar login local. Testar falha segura se conta ausente, schema antigo,
secrets ausentes ou concorrência de rotação/login. Rollback não ressuscita
sessões/credenciais revogadas nem reativa automaticamente OIDC; usa imagem
compatível com schema aditivo e procedimento autorizado. Se não houver retorno
seguro, manter acesso fechado. Não remover tabelas/migrations/histórico.

## Consequências e limites

Retira dependência de provedor e transfere custódia, recuperação e proteção de
senha ao operador. Comprometimento da senha expõe todas as capacidades da conta;
saída de uma pessoa exige troca global, sem revogação individual. R12 permanece
mesmo com hash/HTTPS. Auditoria registra principal técnico e eventos fechados,
sem alegação de autoria individual; política real pode exigir contas individuais
antes da coleta. Backups contêm hashes sensíveis e exigem custódia/restore com
revogação. Streamlit/OIDC legado permanecem preservados até transição aprovada.
Não autoriza implementar, publicar, ativar research, coletar ou retirar legado.
