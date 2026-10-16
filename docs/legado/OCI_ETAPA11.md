# Preparação pública para a Etapa 11 — OCI Always Free

Este documento registra somente fatos consultados em documentação pública da
Oracle em 2026-09-13. Nenhuma tenancy foi acessada, nenhum recurso foi criado,
nenhum domínio foi configurado e nenhum deploy foi executado nesta consulta.
O estado e as autorizações da Etapa 11 constam do
[backlog canônico](Projeto%20Stroop%20Test.md).

## Restrições verificadas

- A cota Always Free de computação deve ser tratada como até 2 OCPUs e 12 GB
  de memória no total da tenancy, equivalente às franquias mensais publicadas
  de 1.500 OCPU-horas e 9.000 GB-horas. O limite é da tenancy e depende da
  disponibilidade na região inicial (home region).
- O shape candidato é `VM.Standard.A1.Flex`, ARM64, com mínimo de 1 OCPU.
  Para o perfil deste projeto, a proposta inicial é reservar capacidade para o
  sistema operacional e manter limites do Compose configuráveis; o
  dimensionamento final não foi decidido nesta preparação.
- A disponibilidade de A1 não é garantida: a documentação alerta para falta de
  capacidade e para eventual recuperação de instâncias ociosas. A seleção de
  região e a confirmação da cota exigem consulta autenticada da tenancy.
- O armazenamento Always Free é regional e tem limite combinado publicado de
  200 GB para volumes de inicialização/bloco, além de limites próprios para
  backups. O destino externo do backup criptografado continua pendente da
  Etapa 11 e não foi configurado.
- A borda deverá publicar somente HTTP/HTTPS. PostgreSQL, dashboard e demais
  serviços internos devem permanecer em subnet privada ou sem regra pública,
  protegidos por NSG/lista de segurança e pelo firewall do sistema operacional.
  A abertura de portas, o domínio e o certificado real não foram configurados.
- Imagens Oracle Linux ou Ubuntu ARM64 são candidatas para A1. A documentação
  recomenda a rede paravirtualizada para imagens A1; a escolha da imagem e a
  instalação do Docker aguardam a autorização e a validação da tenancy.

## Pontos a confirmar antes de qualquer ação externa

1. Região assinada e capacidade disponível para `VM.Standard.A1.Flex`.
2. Cota efetiva de OCPU, memória, boot volume e block volume na tenancy.
3. Sistema operacional ARM64 e estratégia de acesso administrativo sem
   versionar chaves ou secrets.
4. Subnet pública mínima para a borda e subnet privada para PostgreSQL e
   dashboard, com regras de entrada apenas para 80/443.
5. Domínio, certificado real, destino externo de backup e custos, todos fora
   desta consulta pública.

## Fontes públicas consultadas

- [Free Tier da OCI](https://docs.oracle.com/iaas/Content/FreeTier/freetier.htm)
- [Recursos Always Free](https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm)
- [Criação de uma instância](https://docs.oracle.com/en-us/iaas/Content/Compute/Tasks/launchinginstance.htm)
- [Computação baseada em Arm](https://docs.oracle.com/en-us/iaas/Content/Compute/References/arm.htm)
- [Shapes de computação](https://docs.oracle.com/en-us/iaas/Content/Compute/References/computeshapes.htm)
- [Tutorial de primeira instância Linux](https://docs.oracle.com/en-us/iaas/Content/Compute/tutorials/first-linux-instance/overview.htm)
- [Listas de segurança](https://docs.oracle.com/en-us/iaas/tools/oci-cli/latest/oci_cli_docs/cmdref/network/security-list.html)
- [Regras de segurança para servidor web](https://docs.oracle.com/en/learn/publish-webserver-using-oci/index.html)
- [Problemas conhecidos de Compute](https://docs.oracle.com/en-us/iaas/Content/Compute/known-issues.htm)
- [Regiões disponíveis](https://docs.oracle.com/en-us/iaas/Content/General/organization/list-available-regions.htm)

As páginas podem apresentar limites distintos para períodos pagos ou de teste;
para o dimensionamento Always Free, deve prevalecer a página específica de
recursos Always Free e a cota efetivamente exibida na tenancy.
