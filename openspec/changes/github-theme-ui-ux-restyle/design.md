## Context

O frontend usa React + Vite e ja possui estilos distribuidos entre layout principal e componentes. A solicitacao e uma reestilizacao visual ampla com referencia explicita no tema do GitHub: fonte menor, familia tipografica do GitHub, paleta de cores do GitHub e melhor contraste geral, incluindo painel lateral mais largo. Como e uma mudanca transversal de UI/UX, o risco principal e inconsistencias entre telas e regressao de legibilidade em diferentes breakpoints.

## Goals / Non-Goals

**Goals:**
- Definir tokens globais de tema (cores, tipografia, bordas, estados) alinhados ao GitHub theme.
- Reduzir a escala tipografica global e aplicar stack de fontes no padrao do GitHub em toda a aplicacao.
- Aumentar a largura do painel lateral com comportamento responsivo para desktop e mobile.
- Melhorar contraste entre fundo, texto, bordas e estados interativos para elevar legibilidade.
- Garantir consistencia visual em layout, paineis, cards, formularios e navegacao.

**Non-Goals:**
- Alterar regras de negocio, fluxos funcionais, contratos de API ou persistencia de dados.
- Criar sistema de temas alternativos (ex.: dark mode novo) fora do escopo solicitado.
- Reestruturar arquitetura de componentes alem do necessario para aplicar o novo visual.

## Decisions

1. Adotar tokens globais de design baseados na paleta do GitHub (light) via CSS variables.
   - **Rationale:** centraliza identidade visual e evita valores hardcoded conflitantes.
   - **Alternatives considered:**
     - Ajustes pontuais por componente: rejeitado por aumentar divergencia visual.
     - Criar paleta propria: rejeitado por conflitar com requisito de usar GitHub theme como referencia.

2. Aplicar stack tipografico do GitHub como fonte padrao e reduzir escala base (ex.: corpo em 14px, auxiliares em 12-13px, headings proporcionalmente ajustados).
   - **Rationale:** melhora densidade de informacao sem comprometer leitura.
   - **Alternatives considered:**
     - Manter fonte atual e apenas diminuir tamanho: rejeitado por nao atender alinhamento tipografico solicitado.
     - Adotar fonte custom externa: rejeitado por custo de carregamento e desvio do padrao GitHub.

3. Ajustar painel lateral para largura maior com regra responsiva (desktop mais largo; mobile preserva usabilidade e nao bloqueia conteudo principal).
   - **Rationale:** melhora descoberta de itens e legibilidade da navegacao.
   - **Alternatives considered:**
     - Largura fixa unica para todos os breakpoints: rejeitado por risco de overflow em telas menores.

4. Padronizar contraste com pares de cor de texto/superficie/borda inspirados no GitHub e validacao minima de acessibilidade (texto normal >= 4.5:1 quando aplicavel).
   - **Rationale:** legibilidade consistente em toda a aplicacao.
   - **Alternatives considered:**
     - Melhorar apenas telas principais: rejeitado por manter inconsistencias no restante da interface.

## Risks / Trade-offs

- [Regressao visual em componentes isolados] -> Mitigacao: aplicar tokens globais e revisar componentes criticos (sidebar, canvas, formulios, paineis) em conjunto.
- [Aumento de densidade por fonte menor pode prejudicar leitura em alguns contextos] -> Mitigacao: manter hierarquia clara de pesos/tamanhos e espacamentos minimos.
- [Largura maior da sidebar pode reduzir area util em resolucoes menores] -> Mitigacao: usar breakpoints com largura adaptativa e comportamento colapsavel no mobile.
- [Dependencia de referencia visual externa (GitHub)] -> Mitigacao: formalizar mapa de tokens no codigo para evitar interpretacoes inconsistentes.

## Migration Plan

1. Introduzir tokens globais de cor/tipografia em um ponto unico de tema (CSS global ou arquivo de tokens).
2. Atualizar layout base e sidebar para usar tokens e nova largura responsiva.
3. Atualizar componentes essenciais (botoes, inputs, cards, paineis, labels, estados hover/focus/disabled).
4. Validar contraste e responsividade (desktop/mobile), corrigindo regresses visuais.
5. Liberar com rollback simples via reversao dos arquivos de tema/layout afetados.

## Open Questions

- Qual largura exata final da sidebar em desktop sera adotada apos validacao visual (valor alvo e limite maximo)?
- O escopo da reestilizacao inclui 100% das telas nesta iteracao ou foco inicial nas telas de maior uso?
