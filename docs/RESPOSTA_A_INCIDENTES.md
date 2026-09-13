# Resposta a incidentes

Este procedimento e provisório ate a instituicao designar controlador,
encarregado, pesquisador responsável, equipe tecnica e canais de contato. Nao
usar dados reais antes dessas definicoes.

## Procedimento

1. Conter: retirar somente a entrada HTTP/HTTPS, preservar o volume e impedir
   novos logins/importacoes; nao apagar evidencias.
2. Preservar: registrar horario do conhecimento, sistemas, categorias de dados,
   quantidade estimada de titulares, contas e backups afetados, sem copiar CSV
   ou dados clínicos para tickets ou chats.
3. Avaliar: pesquisador responsável, controlador/encarregado e seguranca
   classificam probabilidade e dano relevante, alcance e necessidade de
   notificacao.
4. Erradicar: bloquear identidades, revogar secrets/certificados, corrigir a
   causa e reconstruir imagens fixadas. A chave de backup so e rotacionada com
   plano que preserve a recuperacao das geracoes ainda necessárias.
5. Recuperar: restaurar a ultima geracao integra em ambiente isolado, validar
   migrations/contagens, reabrir primeiro internamente e monitorar recorrencia.
6. Comunicar e aprender: cumprir decisoes do controlador, registrar medidas e
   atualizar threat model, procedimentos e testes.

Incidente que possa acarretar risco ou dano relevante deve ser comunicado pelo
controlador à ANPD e aos titulares em **tres dias uteis**, contados do
conhecimento, salvo prazo específico aplicavel. Se as informacoes estiverem
incompletas, a comunicacao à ANPD pode ser preliminar e depois complementar.
Nao se deve aguardar a investigacao perfeita para iniciar a avaliacao do prazo.
Fonte oficial: [Comunicacao de Incidente de Seguranca da ANPD](https://www.gov.br/anpd/pt-br/canais_atendimento/agente-de-tratamento/comunicado-de-incidente-de-seguranca-cis).

## Registro e comunicacao

O registro de todo incidente, comunicado ou nao, deve ser mantido por pelo
menos cinco anos e conter as informacoes exigidas pela regulamentacao aplicavel.
Ele fica em repositorio institucional protegido, separado dos logs tecnicos,
backups e Git. Nao incluir token, credencial, chave, conteúdo de CSV ou copia
desnecessária de dado pessoal.

A comunicacao aos titulares usa linguagem simples, canal individual quando
possivel e informa natureza/categoria dos dados, controles existentes, riscos,
impactos, medidas, data de conhecimento e contato. Somente o controlador ou
responsavel formalmente delegado comunica ANPD ou titulares.

## Evidencia tecnica minima

Preservar, com acesso restrito: IDs aleatorios de requisicao, horario, status,
versoes/digests das imagens, eventos OIDC, hashes dos arquivos rejeitados,
estado dos containers, checksum dos backups e comandos operacionais executados.
Nao coletar retrospectivamente dados identificaveis que nao faziam parte dos
logs. O prazo de 30 dias dos logs e 180 dias da auditoria nao substitui os cinco
anos do registro formal do incidente.
