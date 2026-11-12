# TAREFA — REDESIGN COMPLETO DE UX/UI DA ÁREA DA EQUIPE

Diretriz operacional canônica integrada ao [workflow do projeto](../../WORKFLOW_CODEX_CLI.md) e ao [backlog canônico](../../Projeto%20Stroop%20Test.md).

## 1. Objetivo

Realize uma reformulação profunda da experiência do usuário (UX) e da interface visual (UI) da área da equipe da aplicação Cores, tomando como referência as capturas de tela fornecidas e, principalmente, o código existente no repositório.

O objetivo é transformar a interface atual em uma aplicação de pesquisa profissional, intuitiva, organizada, responsiva e visualmente consistente, com qualidade semelhante à de um software SaaS moderno voltado à gestão de estudos científicos.

**Não quero apenas uma mudança de cores ou CSS. Quero uma melhoria efetiva da arquitetura da informação, organização dos componentes, navegação, interações, fluxos operacionais, visualização de dados e legibilidade.**

Implemente as melhorias diretamente no código, preservando as funcionalidades existentes.

## 2. Diagnóstico inicial

As capturas indicam os seguintes problemas que devem orientar a auditoria da interface:

1. **Densidade de informação excessiva:** muitos gráficos, tabelas, indicadores e controles são exibidos sequencialmente, tornando a página longa e cansativa.
2. **Hierarquia visual insuficiente:** elementos de importância diferente utilizam estilos semelhantes, dificultando identificar prioridades.
3. **Filtros complexos:** o painel contém muitos campos e listas simultâneas, aumentando o esforço necessário para configurar uma consulta.
4. **Tipografia pequena:** legendas, tabelas, valores e descrições apresentam leitura difícil nas capturas.
5. **Gráficos pouco expressivos:** diversas informações são representadas por barras horizontais básicas, sem otimização para comparação e interpretação.
6. **Tabelas extensas:** dados importantes ficam dispersos em muitas colunas, exigindo rolagem horizontal.
7. **Navegação pouco evidente:** funções operacionais e analíticas precisam de uma separação mais clara.
8. **Excesso de conteúdo técnico:** identificadores internos e metadados longos competem visualmente com informações úteis.
9. **Fluxo de preparação da avaliação:** seleção de paciente, avaliador, parâmetros da sessão e modalidade de aplicação precisam de orientação visual mais consistente.
10. **Baixa diferenciação entre seções:** áreas analíticas, operacionais e administrativas não possuem identidade estrutural suficientemente distinta.

Esses pontos são hipóteses iniciais baseadas nas capturas. Confirme-os no código e, quando possível, na interface em execução antes de implementar mudanças.

## 3. Regras obrigatórias

- Preserve integralmente as funcionalidades existentes, salvo alterações justificadas de apresentação e interação.
- Não altere fórmulas científicas, definições de métricas, critérios de validade ou regras de análise.
- Não modifique o funcionamento do experimento Stroop Go/No-Go.
- Preserve contratos de API, autenticação, autorização, banco de dados e compatibilidade com dados existentes.
- Não apresente métricas fictícias ou simuladas como resultados reais.
- Não esconda erros, avisos ou estados relevantes apenas para tornar a interface visualmente mais limpa.
- Preserve a terminologia científica apropriada e a linguagem em português do Brasil.
- Não introduza dependências desnecessárias nem reescreva o frontend inteiro sem justificativa técnica.
- Respeite o framework e a arquitetura existentes. Caso seja Streamlit, explore os recursos disponíveis e componentes compatíveis antes de considerar qualquer migração.
- Não execute deploy em produção nem realize push remoto automaticamente.
- Dê preferência a soluções simples, sustentáveis, reutilizáveis e testáveis.

## 4. Identidade visual e design system

Mantenha a identidade reconhecível da aplicação Cores, mas modernize sua apresentação.

### Direção visual

Adote uma estética minimalista e profissional, com:

- Fundo claro e neutro, preferencialmente branco suave ou tons discretos de cinza.
- Azul-marinho para títulos, textos de destaque e elementos estruturais.
- Roxo/violeta da identidade atual como cor de destaque para ações selecionadas e estados ativos.
- Bordas discretas, sombras sutis quando necessárias e arredondamentos moderados.
- Espaçamento consistente e generoso entre grupos de conteúdo.
- Ícones funcionais, discretos e visualmente consistentes.
- Elementos interativos claramente distinguíveis de elementos informativos.

Evite gradientes excessivos, sombras pesadas, efeitos decorativos, cartões desnecessários, excesso de cores e aparência genérica de dashboard gerado por IA.

### Tipografia

Estabeleça uma escala tipográfica consistente:

- Título principal: aproximadamente 28–32 px.
- Títulos de seção: aproximadamente 20–24 px.
- Subtítulos: aproximadamente 16–18 px.
- Texto geral: aproximadamente 15–16 px.
- Legendas e metadados: preferencialmente 13–14 px, sem comprometer a leitura.
- Valores de indicadores: aproximadamente 24–32 px.

Use esses valores como referências adaptáveis à estrutura existente.

### Consistência

Centralize tokens de design, quando tecnicamente viável:

- Cores.
- Tipografia.
- Espaçamento.
- Raios de borda.
- Estilos de botões.
- Estados de foco e seleção.
- Estilos de tabelas.
- Layouts de formulários.
- Componentes de feedback.

Evite regras CSS duplicadas e estilização isolada sem necessidade.

## 5. Arquitetura da informação e navegação

Reavalie a organização da área da equipe.

A navegação deve representar tarefas e objetivos do usuário, não simplesmente uma sequência de funcionalidades técnicas.

Considere a seguinte estrutura, adaptando-a às rotas e permissões existentes:

**Visão geral**

Dashboard com indicadores, tendências e visão consolidada do projeto.

**Pacientes**

Consulta, cadastro e gerenciamento dos pacientes, conforme funcionalidades e permissões existentes.

**Avaliadores**

Consulta e gerenciamento de avaliadores.

**Preparar avaliação**

Fluxo dedicado à preparação e emissão de uma nova avaliação.

**Avaliações e histórico**

Pesquisa de avaliações, consulta de registros e acompanhamento longitudinal.

**Relatórios e exportações**

Acesso aos relatórios, tabelas e funcionalidades de exportação existentes.

**Administração**

Configurações e funções administrativas autorizadas.

Não crie páginas vazias nem funcionalidades artificiais apenas para preencher essa estrutura. Reorganize o que realmente existe.

A navegação deve ter estado ativo evidente, rótulos claros e comportamento consistente em diferentes larguras de tela.

Evite mostrar simultaneamente o conteúdo completo de várias áreas que representam objetivos diferentes.

## 6. Reformulação do dashboard

A visão geral deve responder rapidamente:

- Quantas avaliações válidas existem?
- Quantos participantes estão representados?
- Qual é o desempenho geral registrado?
- Como os resultados variam entre visitas e condições?
- Existem omissões, comissões ou avaliações interrompidas?
- Quais tendências merecem exploração adicional?

### 6.1. Cabeçalho

Criar uma região inicial limpa contendo:

- Título da seção.
- Descrição curta.
- Projeto selecionado.
- Contexto dos filtros aplicados.
- Ações relevantes, quando existentes.

Evitar textos longos e metadados técnicos nesse espaço.

### 6.2. Indicadores principais

Apresentar os KPIs existentes em cartões consistentes.

Priorizar, quando aplicável:

- Avaliações válidas.
- Participantes distintos.
- Precisão média.
- Precisão mediana.
- Tempo mediano de resposta.
- Total de omissões.
- Total de comissões.

A seleção e a disposição devem considerar a relevância e o espaço disponível.

Cada cartão deve apresentar:

1. Nome curto e inequívoco.
2. Valor em destaque.
3. Unidade correta.
4. Tooltip ou explicação acessível.
5. Estado sem dados, quando aplicável.

Agrupar métricas semanticamente relacionadas.

Não utilizar cores que sugiram melhora ou piora clínica sem justificativa metodológica.

### 6.3. Visualizações analíticas

Substituir gráficos excessivamente básicos ou redundantes por visualizações mais claras, quando isso realmente melhorar a compreensão dos dados.

Avaliar:

- Gráficos de barras para comparação entre visitas.
- Gráficos de linha para evolução temporal, quando o contexto permitir.
- Barras agrupadas para comparação entre condições Go e No-Go.
- Distribuições adequadas para tempos de resposta.
- Gráficos comparativos de omissões e comissões.

Não inserir gráficos por decoração.

Toda visualização deve possuir título claro, unidades, legendas quando necessárias, tratamento de valores ausentes e comportamento responsivo.

Preserve a diferença entre contagens, porcentagens, médias e medianas. Não misture conceitos estatísticos.

Não apresente dados agregados como se representassem evolução individual.

### 6.4. Organização das análises

Distribuir as análises em seções como:

**Desempenho geral**
- Indicadores consolidados.
- Precisão.
- Tempo de resposta.

**Análises por visita**
- Comparações entre V1, V2 e outras visitas existentes.
- Indicadores por visita.
- Evolução dos participantes quando disponível.

**Análises por condição**
- Go.
- No-Go.
- Omissões e comissões.

**Análises operacionais**
- Avaliações por período.
- Situação das avaliações.
- Avaliadores.
- Registros interrompidos ou inválidos.

**Dados detalhados**
- Tabelas de avaliações filtradas.
- Informações técnicas.
- Metadados e exportação.

Utilize abas, seções recolhíveis ou páginas separadas conforme a melhor solução para o framework.

O conteúdo crítico deve permanecer facilmente descobrível.

## 7. Redesign completo dos filtros

O painel de filtros atual é um dos maiores pontos de melhoria.

Ele apresenta muitos controles simultâneos, listas pequenas e grupos que competem pela atenção do usuário.

### Nova organização

Criar um painel de filtros em dois níveis:

**Filtros principais**, imediatamente acessíveis:
- Projeto.
- Período.
- Participante.
- Visita.
- Status da avaliação.

**Filtros avançados**, disponíveis sob expansão:
- Avaliador.
- Instrumento.
- Versão.
- Plataforma.
- Condição experimental.
- Faixas de precisão.
- Faixas de tempo de reação.
- Outros critérios efetivamente existentes.

Adaptar a composição ao modelo de filtros real.

### Interações

- Oferecer campos pesquisáveis quando houver muitas opções.
- Melhorar seletores múltiplos e estados de seleção.
- Exibir claramente os filtros ativos.
- Permitir remoção individual de filtros, quando viável.
- Disponibilizar ações claras de aplicar e limpar.
- Manter consistência entre filtros e resultados.
- Evitar redefinições inesperadas ao mudar de aba ou interagir com gráficos.
- Informar quando um conjunto de filtros não retorna resultados.

Preservar a semântica atual de aplicação dos filtros. Caso seja necessário alterá-la, revisar cuidadosamente os efeitos sobre o estado da aplicação.

Não utilizar quatro colunas estreitas e densas quando isso prejudicar a legibilidade.

## 8. Redesign das tabelas

As tabelas atuais precisam ser mais fáceis de ler e investigar.

Melhorar, conforme a biblioteca disponível:

- Alinhamento de números.
- Formatação de unidades.
- Cabeçalhos.
- Espaçamento interno.
- Separação visual das linhas.
- Ordenação.
- Pesquisa.
- Paginação ou carregamento progressivo.
- Exibição de estados vazios.
- Responsividade.
- Exportação, quando já existente.

Para tabelas muito extensas, avaliar a separação entre:

**Visão resumida:** colunas fundamentais para identificar e comparar registros.

**Detalhes do registro:** informações completas disponibilizadas ao selecionar uma avaliação.

Identificadores técnicos longos não devem dominar a interface. Utilize nomes legíveis, códigos abreviados quando seguros e detalhes expandíveis.

Nunca elimine o acesso aos identificadores completos quando forem necessários para auditoria ou rastreabilidade.

Em telas estreitas, priorize colunas essenciais, detalhes sob demanda ou rolagem horizontal controlada.

Evite múltiplas regiões internas de rolagem quando a navegação pela página for suficiente.

## 9. Reformulação do fluxo "Preparar avaliação"

Essa área possui importância operacional e deve receber atenção especial.

Transforme a interface em um fluxo orientado, com etapas claramente identificadas.

### Etapa 1 — Identificação

Permitir localizar ou selecionar um paciente existente e, quando autorizado, cadastrar um novo paciente.

Distinguir claramente busca, seleção e cadastro.

### Etapa 2 — Avaliador responsável

Permitir selecionar o avaliador existente e cadastrá-lo quando permitido.

Exibir o avaliador selecionado com identificação suficiente para evitar erros.

### Etapa 3 — Parâmetros da sessão

Organizar:

- Projeto.
- Instrumento.
- Identificador do participante.
- Iniciais.
- Visita.
- Outros parâmetros efetivamente exigidos.

Agrupar campos por contexto.

Aplicar validação visível e contextual.

### Etapa 4 — Modalidade

Diferenciar claramente:

- Aplicação presencial/local.
- Aplicação remota por convite, quando disponível.

Apresentar explicações curtas sobre cada modalidade e suas consequências práticas.

### Etapa 5 — Revisão e confirmação

Antes de iniciar ou gerar convite, apresentar um resumo da sessão:

- Paciente.
- Avaliador.
- Projeto.
- Instrumento.
- Visita.
- Modalidade.
- Parâmetros relevantes.

Disponibilizar uma ação primária evidente.

A experiência deve minimizar erros de seleção e reduzir a carga cognitiva.

**Importante:** não transformar esse fluxo em um assistente de múltiplas páginas se isso causar perda de estado, incompatibilidade ou complexidade desnecessária. A solução deve respeitar o framework e a lógica de negócio.

## 10. Estados e feedback

Padronize os estados de interação:

- Carregamento.
- Sem dados.
- Erro.
- Sucesso.
- Permissão insuficiente.
- Filtro sem correspondências.
- Formulário incompleto.
- Operação indisponível.

As mensagens devem explicar o que aconteceu e, quando possível, como o usuário pode prosseguir.

Erros de preenchimento devem aparecer próximos aos campos relevantes.

Ações sensíveis devem utilizar confirmação quando apropriado.

Evitar mensagens excessivamente técnicas direcionadas ao usuário comum. Detalhes de depuração devem permanecer acessíveis nos mecanismos adequados.

## 11. Responsividade e acessibilidade

A aplicação deve funcionar adequadamente em:

- Desktop, aproximadamente 1440 px.
- Notebook, aproximadamente 1280 px.
- Tablet, aproximadamente 768 px.
- Celular, aproximadamente 390 px.

Essas dimensões são referências de validação, não layouts rígidos.

Priorizar o desktop, sem abandonar o uso em telas menores.

Implementar:

- Layouts fluidos.
- Redução progressiva do número de colunas.
- Cartões reorganizáveis.
- Navegação adaptável.
- Formulários sem campos excessivamente estreitos.
- Tabelas com estratégia responsiva.
- Botões com áreas de clique adequadas.
- Contraste compatível com WCAG AA nos textos essenciais.
- Estados de foco visíveis.
- Controles utilizáveis por teclado, quando suportado.
- Uso de cor acompanhado de textos ou outros indicadores.

Não resolver problemas de responsividade simplesmente diminuindo a tipografia.

Não usar truncamento indiscriminado que esconda dados relevantes.

## 12. Qualidade técnica

Antes de modificar arquivos:

1. Identifique o framework real.
2. Localize as páginas e componentes envolvidos.
3. Identifique regras de negócio associadas.
4. Mapeie estados, consultas e dependências.
5. Identifique testes existentes.
6. Verifique quais componentes podem ser reutilizados.

Durante a implementação:

- Evite duplicação de código.
- Separe apresentação, estado e lógica de negócio sempre que for adequado.
- Centralize estilos reutilizáveis.
- Minimize CSS global frágil e seletores dependentes de estrutura interna instável.
- Preserve controles de acesso por papel.
- Evite consultas desnecessárias ou recomputações custosas.
- Mantenha compatibilidade com as dependências existentes.
- Não altere configurações de produção sem necessidade.

Caso a aplicação utilize Streamlit, considere cuidadosamente o comportamento de reruns, `session_state`, formulários, cache e componentes interativos.

Não introduza componentes externos cuja manutenção ou compatibilidade sejam incertas sem benefício demonstrável.

## 13. Ordem de execução

Execute em fases para reduzir o risco de regressões.

### Fase 1 — Auditoria

Inspecione o projeto e identifique os arquivos relevantes.

Produza um diagnóstico objetivo de:
- Arquitetura atual.
- Principais problemas encontrados.
- Componentes reutilizáveis.
- Restrições técnicas.
- Melhorias prioritárias.

### Fase 2 — Fundação visual

Implemente o design system, tipografia, espaçamento, containers e componentes básicos.

### Fase 3 — Navegação e organização

Reorganize a navegação e a distribuição do conteúdo.

### Fase 4 — Dashboard

Melhore indicadores, gráficos, seções analíticas e exploração dos resultados.

### Fase 5 — Filtros e tabelas

Reformule a experiência de consulta e exploração dos registros.

### Fase 6 — Preparação da avaliação

Melhore o fluxo operacional completo, preservando sua lógica.

### Fase 7 — Responsividade e acabamento

Corrija problemas de diferentes tamanhos de tela, inconsistências visuais, estados de interação e acessibilidade.

### Fase 8 — Verificação

Execute as verificações disponíveis e corrija regressões identificadas.

Trabalhe de forma incremental. Não considere uma fase concluída apenas porque o código foi escrito.

## 14. Critérios de aceitação

Considere o redesign concluído somente quando:

- [ ] A navegação estiver claramente organizada.
- [ ] O dashboard apresentar hierarquia visual consistente.
- [ ] Os indicadores principais forem rapidamente identificáveis.
- [ ] Os gráficos forem legíveis e adequados às métricas.
- [ ] Os filtros forem mais simples de utilizar.
- [ ] Tabelas extensas permitirem exploração sem perda de informações.
- [ ] O fluxo de preparação de avaliação estiver claro e funcional.
- [ ] Textos e controles tiverem tamanho confortável.
- [ ] Não houver sobreposição ou cortes indevidos nos layouts testados.
- [ ] Os estados vazios, de carregamento e de erro estiverem adequadamente tratados.
- [ ] As funcionalidades anteriores permanecerem operacionais.
- [ ] As métricas e definições científicas permanecerem inalteradas.
- [ ] Não houver regressões conhecidas nos fluxos críticos.
- [ ] O código estiver organizado e sem duplicações desnecessárias.

Valide esses itens por testes automatizados e inspeção visual sempre que as ferramentas disponíveis permitirem.

Se algum item não puder ser comprovado, informe expressamente a limitação.

## 15. Autonomia e tomada de decisões

Você tem autonomia para realizar melhorias significativas de UX/UI dentro do escopo.

Não peça confirmação para escolhas comuns de layout, organização visual, espaçamento, tipografia ou componentes.

Tome decisões fundamentadas em:

1. Clareza das tarefas.
2. Facilidade de utilização.
3. Preservação funcional.
4. Legibilidade.
5. Consistência.
6. Acessibilidade.
7. Responsividade.
8. Manutenibilidade.

Evite tanto alterações superficiais quanto refatorações arquiteturais desnecessárias.

Caso uma melhoria exija alterar regras de negócio, contratos de dados ou funcionalidades científicas, preserve o comportamento atual e registre a proposta separadamente.

Não substitua funcionalidades existentes por protótipos, placeholders ou versões incompletas.

## 16. Entrega final

Ao finalizar, apresente um relatório conciso contendo:

**Alterações realizadas**
- Principais melhorias de UX/UI.
- Fluxos reorganizados.
- Componentes criados ou reutilizados.

**Arquivos modificados**
- Arquivos principais e respectivas responsabilidades.

**Validação**
- Testes executados.
- Resultados.
- Verificações visuais realizadas.
- Problemas encontrados e corrigidos.

**Limitações**
- Melhorias não implementadas.
- Restrições do framework.
- Pendências que ainda necessitam de validação.

**Resultado**
- Avaliação objetiva das melhorias.
- Próximos aperfeiçoamentos recomendados, separados do que foi efetivamente entregue.

## Instrução final

Não limite a execução à elaboração de um plano ou de recomendações. Inspecione o repositório e implemente as melhorias viáveis.

Priorize mudanças que produzam ganhos reais de usabilidade e qualidade visual.

O resultado esperado é uma interface profissional de pesquisa científica: organizada, elegante, funcional, compreensível e preparada para manutenção futura.

A aplicação deve deixar de parecer uma coleção extensa de formulários, tabelas e gráficos independentes e passar a oferecer uma experiência de software coesa, com navegação orientada por tarefas e exploração eficiente dos dados.
