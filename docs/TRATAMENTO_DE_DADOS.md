# Tratamento e retencao de dados

Politica provisória autorizada em 2026-09-13 para orientar o hardening. Ela nao
substitui protocolo de pesquisa, decisao do pesquisador responsável, parecer do
CEP, base legal, aviso aos titulares ou normas internas. Todos os prazos devem
ser confirmados institucionalmente antes de dados reais.

## Categorias e prazos

| Categoria | Conteudo permitido | Prazo provisorio | Destino ao final |
|---|---|---:|---|
| CSV recebido | arquivo integral em temporario privado | somente durante o processamento | eliminacao imediata, em sucesso ou rejeicao |
| rejeicao de importacao | SHA-256, status e codigo fechado de erro | 30 dias | eliminacao automatizavel |
| logs operacionais | horario, metodo, status, bytes, duracao e ID aleatorio | 30 dias | eliminacao no host |
| auditoria OIDC | `iss`, `sub`, acao, resultado, horario e ID aleatorio | 180 dias | eliminacao automatizavel |
| dados da pesquisa | avaliacoes, metricas, tentativas e identificadores autorizados | minimo de 5 anos apos o termino da pesquisa | eliminar, anonimizar ou reter alem do minimo somente conforme protocolo, pesquisador responsável e CEP |
| backups | copia criptografada do PostgreSQL | 30 geracoes diarias | destruicao da geracao e de eventual replica externa |
| registro formal de incidente | fatos, avaliacao, medidas e comunicacoes necessárias | minimo de 5 anos | destino conforme norma institucional |

Dados da pesquisa permanecem pseudonimizados e com acesso por menor privilegio;
pseudonimizacao nao equivale a anonimização e continua sujeita à LGPD. A chave
de correspondencia, se existir, deve permanecer fora deste sistema e sob
custodia institucional. `participant_name` e `initials` so podem ser mantidos se
o protocolo os autorizar e justificar como necessários.

A LGPD nao define um prazo universal: o termino depende de finalidade,
necessidade, periodo informado, solicitacao aplicavel do titular e determinacao
da ANPD. A conservacao para pesquisa nao justifica guarda indiscriminada e deve
manter vinculo real com a finalidade. Referencias:
[perguntas frequentes da ANPD](https://www.gov.br/anpd/pt-br/acesso-a-informacao/perguntas-frequentes) e
[guia para fins academicos e pesquisas](https://www.gov.br/anpd/pt-br/centrais-de-conteudo/materiais-educativos-e-publicacoes/web-guia-anpd-tratamento-de-dados-para-fins-academicos.pdf).

O minimo de cinco anos segue a responsabilidade de guarda prevista para
pesquisas com participantes na
[Resolucao CNS 510/2016](https://www.gov.br/conselho-nacional-de-saude/pt-br/atos-normativos/resolucoes/2016/resolucao-no-510.pdf/view).
A instituicao deve confirmar qual norma e protocolo se aplicam a este estudo.

## Regras operacionais

- nunca usar nome, iniciais, ID de participante ou nome original do arquivo em
  logs, mensagens, paths de temporario, backup, teste ou screenshot;
- nunca registrar corpo, linha, metrica, token, cookie, segredo ou DSN;
- restringir dados e backups aos perfis e operadores que precisam deles;
- manter chave AES-256 separada dos backups e de suas replicas;
- registrar e justificar legalmente qualquer suspensao de eliminacao;
- atender direitos dos titulares somente pelo procedimento institucional, sem
  apagar diretamente registros que estejam sob preservacao obrigatoria;
- revisar prazos ao encerrar a pesquisa, alterar finalidade, receber decisao do
  CEP ou mudar obrigacao legal.

O script de retencao remove apenas auditorias operacionais/OIDC. A eliminacao ou
anonimizacao das tabelas de pesquisa nao foi automatizada porque depende de
decisao humana documentada e nao pode ocorrer por simples variavel de ambiente.
