# Especificacao visual e fluxo

Data: 2026-07-06.

Esta especificacao descreve a proxima versao visual e funcional do experimento Stroop Go/No-Go. Ela nao altera o `.psyexp`, os CSVs de condicoes, tempos, numero de tentativas, regras de resposta, exportacao ou dados coletados.

## A. Objetivo da interface

A interface deve reduzir ambiguidade da regra, separar claramente tutorial, pratica e tarefa principal, oferecer feedback apenas durante a pratica e manter a tarefa principal limpa, com minima distracao. O resumo final deve ser descritivo, sem interpretacao clinica, diagnostico, comparacao normativa ou recomendacao individual.

A experiencia deve funcionar em monitor desktop 16:9 e escalar para diferentes resolucoes usando unidades relativas do PsychoPy, preferencialmente `height`. Componentes de texto, botoes, barras e estimulos devem manter proporcoes consistentes sem depender de posicoes absolutas em pixels.

## B. Principios de UX

- Foco visual no estimulo central.
- Textos curtos e diretos.
- Uma acao principal por tela.
- Contraste suficiente entre texto, fundo e elementos interativos.
- Feedback nao deve depender apenas de cor.
- Botoes devem ser visualmente claros e ter alternativa por teclado quando forem navegacao.
- Titulo, barra superior, cartoes e rodape devem seguir um sistema consistente.
- A tarefa principal nao deve conter elementos decorativos excessivos.
- Nao usar logotipos, marcas, aparencia, textos ou composicao que sugiram vinculo com outra plataforma.
- A pratica pode ter feedback imediato; o bloco principal deve permanecer sem feedback por tentativa.

## C. Sistema visual original

A identidade visual deve ser propria e discreta, adequada a uma tarefa experimental. O visual pode usar padroes gerais de testes digitais, mas nao deve copiar marcas, paletas, formas, graficos, molduras, barras, textos ou logotipos de terceiros.

Diretrizes:

- Fundo principal: cinza-azulado muito claro ou off-white.
- Fundo secundario: gradiente discreto proprio ou formas abstratas suaves, sem padrao hexagonal.
- Barra superior: painel simples com cantos suavemente arredondados.
- Cartoes centrais: fundo branco, sombra leve e borda discreta.
- Botoes: estilo proprio, texto claro, alto contraste e estado visual distinto.
- Tipografia: sans-serif do sistema, preferencialmente DejaVu Sans, Arial ou Liberation Sans.
- Nao usar logos ou icones de terceiros.
- Nao usar grafico circular, moldura, barra ou composicao identica a plataformas de referencia.

### Tokens visuais sugeridos

| Token | Valor sugerido | Uso |
|---|---|---|
| Fundo principal | `#F4F7FA` | telas gerais e tarefa principal |
| Fundo secundario | `#E8EEF5` para `#F7FAFC` | telas de tutorial ou abertura |
| Painel/cartao | `#FFFFFF` | cartoes centrais e modais |
| Borda discreta | `#D8E1EA` | cartoes e barras |
| Primaria | `#22577A` | botoes principais e destaques |
| Primaria escura | `#163B52` | texto em botoes principais |
| Secundaria | `#6C5CE7` | detalhe visual secundario, sem dominar a tela |
| Texto principal | `#16212B` | titulos e corpo |
| Texto auxiliar | `#5D6B78` | subtitulos, rodape e lembretes |
| Sucesso | `#2E7D5B` | feedback correto, sempre com texto/simbolo |
| Erro | `#B23A48` | feedback de erro, sempre com texto |
| Alerta | `#B7791F` | aviso neutro ou atencao |
| Barra de progresso | `#22577A` sobre `#D8E1EA` | progresso discreto |
| Espacamento curto | `0.025 height` | separacao interna pequena |
| Espacamento medio | `0.045 height` | blocos de conteudo |
| Espacamento amplo | `0.075 height` | separacao entre secoes |
| Titulo grande | `0.060 height` | abertura |
| Titulo de tela | `0.045 height` | cartoes e etapas |
| Texto de corpo | `0.028 height` | instrucoes |
| Texto auxiliar | `0.022 height` | rodape e atalhos |
| Estimulo | `0.120 height` ou maior | palavra central |
| Raio de cartao | 8 a 12 px em asset proprio | cantos suaves, sem exagero |
| Sombra leve | baixa opacidade | se implementavel por asset proprio |

## D. Paleta dos estimulos

A paleta experimental futura deve usar dez palavras em caixa alta e valores visuais seguros para PsychoPy. Os nomes em `ink_color` devem ser simples, legiveis em CSV e compativeis com PsychoPy.

| Chave interna | Palavra exibida | Nome em portugues | Hexadecimal | Valor compativel com PsychoPy | Observacao de contraste |
|---|---|---|---|---|---|
| `green` | `VERDE` | verde | `#16A34A` | `green` ou `#16A34A` | bom contraste em fundo claro |
| `yellow` | `AMARELO` | amarelo | `#B77900` | `#B77900` | amarelo escurecido para legibilidade |
| `pink` | `ROSA` | rosa | `#DB2777` | `#DB2777` | saturado sem ficar claro demais |
| `black` | `PRETO` | preto | `#111111` | `black` ou `#111111` | contraste muito alto |
| `red` | `VERMELHO` | vermelho | `#DC2626` | `red` ou `#DC2626` | bom contraste e leitura clara |
| `orange` | `LARANJA` | laranja | `#EA580C` | `#EA580C` | laranja escurecido para fundo claro |
| `brown` | `MARROM` | marrom | `#92400E` | `#92400E` | contraste alto |
| `purple` | `ROXO` | roxo | `#7C3AED` | `#7C3AED` | legivel e distinto do azul |
| `blue` | `AZUL` | azul | `#2563EB` | `blue` ou `#2563EB` | bom contraste |
| `gray` | `CINZA` | cinza | `#64748B` | `#64748B` | cinza escuro para nao sumir no fundo |

Na implementacao futura, se o Builder aceitar diretamente hexadecimais no componente de texto, usar os codigos sugeridos. Se a compatibilidade local exigir nomes simples, manter nomes reconhecidos pelo PsychoPy e validar visualmente em Pilot.

## E. Estrutura geral do Flow futuro

Ordem prevista, sem alterar o `.psyexp` nesta etapa:

1. `abertura`
2. `tutorial_introducao`
3. `tutorial_regra`
4. `pratica_inicio`
5. `pratica_loop`
   - `trial_pratica`
   - `feedback_pratica`
6. `pratica_confirmacao`
7. `principal_lembrete`
8. `principal_loop`
   - `trial_principal`
9. `resultados`
10. `encerramento`

Rotinas atuais que podem ser reaproveitadas:

- `boas_vindas`: base para `abertura`.
- `instr_regra`, `instr_congruente`, `instr_incongruente`: base para tutorial e regra.
- `contagem`: pode ser mantida ou substituida por telas de transicao.
- `trial_pratica`: base da tentativa de pratica.
- `feedback_pratica`: base dos feedbacks da pratica.
- `resumo_pratica`: base para confirmacao apos a pratica.
- `trial_principal`: base da tentativa principal.
- `fim`: base para encerramento.

Rotinas que provavelmente precisarao ser criadas ou separadas:

- `tutorial_introducao`
- `tutorial_regra`
- `pratica_inicio`
- `pratica_confirmacao`
- `principal_lembrete`
- `resultados`
- `encerramento`

Decisoes para etapas futuras:

- Ampliar condicoes para dez cores sem alterar o paradigma.
- Definir se a pratica podera ser repetida por loop adicional ou controle no Flow.
- Implementar resumo descritivo somente depois de consolidar dados disponiveis.
- Implementar CSV unificado em etapa propria.

## F. Especificacao tela por tela

| ID | Rotina futura | Objetivo | Componentes visuais | Texto principal | Texto secundario | Elementos dinamicos | Acao principal | Mouse | Teclado | Entrada | Saida | Dados registrados | Observacoes PsychoPy |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 01 | `abertura` | Apresentar a tarefa de forma breve | Duas colunas; esquerda com titulo, explicacao e regras; direita com cartao ilustrativo proprio | `Tarefa de Correspondencia de Cores` | Responder apenas quando palavra e cor coincidirem | Palavra ficticia colorida em cartao | Iniciar tutorial | Botao `Iniciar tutorial` | Espaco ou Enter | inicio do experimento | avanca para tutorial | nenhum | usar layout 16:9 e nao mencionar plataformas |
| 02 | `tutorial_introducao` | Preparar para o treino | Barra superior `Tutorial`; cartao central; botao | `Pratica` | `Voce fara algumas tentativas de treino. Pressione Espaco apenas quando a palavra e a cor forem iguais.` | nenhum | Comecar pratica | Botao `Comecar pratica` | Espaco ou Enter | apos abertura | avanca para regra rapida ou pratica | nenhum | pode reaproveitar rotina de instrucao |
| 03 | `tutorial_regra` | Fixar regra imediatamente antes do treino | Barra superior `Tutorial`; frase central grande; lembrete inferior | `PRESSIONE ESPACO APENAS QUANDO A PALAVRA E A COR COMBINAREM.` | `Observe a cor das letras e o nome apresentado.` | nenhum | transicao automatica | nenhum obrigatorio | nenhum obrigatorio | antes da pratica | apos 1,5 a 2 s futuros | nenhum | duracao futura sem alterar nesta etapa |
| 04 | `trial_pratica` | Apresentar estimulo e permitir resposta | Barra `Pratica`; indicador `n de total`; progresso discreto; estimulo central | palavra do CSV | lembrete discreto se necessario | `word`, `ink_color`, tentativa atual | responder quando congruente | nao usado como resposta | Espaco | dentro de `pratica_loop` | fim da tentativa | tentativa, resposta, RT e classificacao | cliques nunca contam como resposta experimental |
| 05 | `feedback_pratica_correto` | Confirmar comportamento correto | Fundo escurecido leve; cartao; simbolo proprio; botao | `Resposta correta` | `Voce aplicou a regra corretamente.` | `error_type=hit` ou `correct_rejection` | continuar | Botao `Continuar` | Espaco ou Enter | apos tentativa correta de pratica | proxima pratica | nenhum adicional | nao depender apenas de verde |
| 06 | `feedback_pratica_omissao` | Explicar omissao | Fundo escurecido leve; cartao; simbolo proprio; botao | `Voce nao respondeu a tempo.` | `Quando a palavra e a cor coincidirem, pressione Espaco.` | `error_type=omission` | continuar | Botao `Continuar` | Espaco ou Enter | apos omissao na pratica | proxima pratica | nenhum adicional | evitar linguagem punitiva |
| 07 | `feedback_pratica_comissao` | Explicar resposta indevida | Fundo escurecido leve; cartao; simbolo proprio; botao | `Nao era necessario responder.` | `Quando a palavra e a cor forem diferentes, aguarde a proxima tentativa.` | `error_type=commission` | continuar | Botao `Continuar` | Espaco ou Enter | apos comissao na pratica | proxima pratica | nenhum adicional | feedback claro e nao clinico |
| 08 | `pratica_confirmacao` | Permitir iniciar tarefa ou repetir pratica | Cartao central; pergunta; dois botoes | `Voce esta pronto para iniciar a tarefa principal?` | `Se quiser, voce pode repetir o treino antes de continuar.` | escolha futura | iniciar ou repetir | Botoes `Iniciar tarefa` e `Repetir pratica` | Enter/Espaco inicia; R repete | pratica concluida | principal ou retorno a pratica | opcional para auditoria futura | implementar repeticao em etapa futura |
| 09 | `principal_lembrete` | Reforcar regra antes do bloco principal | Cartao simples; botao | `Lembre-se: pressione Espaco apenas quando a palavra e a cor coincidirem.` | `A tarefa principal nao tera feedback por tentativa.` | nenhum | comecar tarefa | Botao `Comecar tarefa` | Espaco ou Enter | antes do principal | entra em `principal_loop` | nenhum | nao criar nova pratica |
| 10 | `trial_principal` | Executar tarefa experimental sem feedback | Barra original; rotulo; cronometro; progresso; estimulo central | palavra do CSV | nenhum ou lembrete minimo | `word`, `ink_color`, tentativa atual, tempo decorrido | responder quando congruente | nao usado como resposta | Espaco | dentro de `principal_loop` | fim da tentativa | tentativa, resposta, RT e classificacao | manter tempos e numero de tentativas ate decisao futura |
| 11 | `resultados` | Mostrar resumo descritivo | Titulo; cartoes de metricas; aviso etico | `Resumo da execucao` | Aviso de nao diagnostico | precisao, hits, omissoes, rejeicoes corretas, comissoes, media/mediana de RT | continuar | Botao `Continuar` | Espaco ou Enter | apos bloco principal | encerramento | nenhum adicional | sem normas, ranking ou areas de melhoria |
| 12 | `encerramento` | Finalizar | Cartao simples; botao | `Execucao concluida.` | `Os dados foram registrados localmente para analise.` | nenhum | finalizar | Botao `Finalizar` | Espaco ou Enter | apos resumo | fim do experimento | nenhum | pode derivar de `fim` |

## G. Fluxo de decisoes

```text
abertura
  -> tutorial
  -> pratica
  -> tentativa de pratica
      -> correta: feedback de acerto
      -> omissao: feedback de omissao
      -> comissao: feedback de comissao
  -> feedback
  -> proxima tentativa de pratica
  -> pratica concluida
  -> confirmacao
      -> iniciar: lembrete principal
      -> repetir: retorno ao inicio da pratica
  -> bloco principal
  -> resumo
  -> encerramento
```

## H. Regras de entrada por mouse e teclado

- Telas de navegacao: botao por mouse e Espaco/Enter como alternativa.
- Repeticao de pratica: tecla R e botao dedicado.
- Pratica e bloco principal: apenas Espaco como resposta experimental.
- Escape: reservado para abortar o experimento conforme configuracao segura.
- Cliques do mouse nunca devem ser registrados como resposta experimental nas tentativas.
- Botoes devem ser desativados ou ignorados durante tentativas experimentais.

## I. Restricoes metodologicas e eticas

- Nao coletar idade ou sexo para gerar pontuacao ou comparacao normativa.
- Caso dados demograficos sejam necessarios em pesquisa futura, coleta-los em formulario separado, com finalidade justificada, consentimento e armazenamento adequado.
- Nao transformar acuracia ou tempo de reacao em diagnostico.
- Nao afirmar equivalencia com produtos, baterias ou instrumentos de terceiros.
- Nao apresentar a tarefa como avaliacao de atencao, inibicao ou cognicao com validade clinica sem estudo especifico.
- Nao sugerir avaliacao clinica, tratamento, classificacao individual ou comparacao com populacoes.

## J. Plano de implementacao futura

| Fase | Escopo | Arquivos provaveis | Riscos tecnicos | Criterios de aceite | Testes necessarios |
|---|---|---|---|---|---|
| 1 | Ampliar CSVs para dez cores e validar combinacoes | `condicoes/*.csv`, docs | alterar distribuicao ou numero de tentativas sem decisao | todas as cores representadas com paradigma preservado | validacao estatica de CSVs e Pilot |
| 2 | Criar assets proprios em `assets/ui/`, se necessario | `assets/ui/*`, docs | assets com baixo contraste ou aparencia derivada de terceiros | assets proprios, legiveis e rastreados | revisao visual e checagem de licenca/origem |
| 3 | Implementar abertura e tutorial | `.psyexp`, docs | quebrar Flow ou atalhos | navegacao por mouse e teclado funcionando | Pilot curto e validacao de rotinas |
| 4 | Implementar pratica e feedback | `.psyexp`, docs | feedback aparecer no bloco principal por engano | feedback somente na pratica | Pilot com respostas corretas/incorretas |
| 5 | Implementar confirmacao e repeticao de pratica | `.psyexp`, possivel CSV auxiliar | loop de repeticao mal encerrado | iniciar ou repetir pratica de forma previsivel | Pilot repetindo e avancando |
| 6 | Implementar HUD do bloco principal | `.psyexp` | distracao visual ou progresso incorreto | progresso discreto e sem feedback de desempenho | Pilot do bloco principal |
| 7 | Implementar resumo descritivo | `.psyexp`, scripts se necessario | calculos divergentes ou linguagem clinica | metricas descritivas corretas e aviso etico visivel | comparar resumo com CSV local de teste |
| 8 | Implementar CSV unificado | `.psyexp`, `scripts/analisar_stroop.py`, docs | duplicacao de linhas ou perda de campos | um CSV por execucao com colunas finais | validacao estatica e leitura por script |
| 9 | Testar em modo Pilot e validar dados | docs, possiveis testes | usar dados reais como fixture ou alterar coleta | execucao piloto limpa e dados coerentes | Pilot, revisao de `data/`, validacao de CSV |

Nenhuma dessas fases deve ser implementada neste documento. Cada fase deve gerar commit proprio e atualizar documentacao relevante.
