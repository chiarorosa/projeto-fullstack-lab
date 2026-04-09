## Why

A interface atual não segue um sistema visual consistente para tipografia, cores e contraste, o que reduz legibilidade e percepção de qualidade. Precisamos alinhar a experiência ao padrão visual do GitHub para tornar a aplicação mais clara, coesa e confortável de usar em toda a navegação.

## What Changes

- Aplicar uma reestilização UI/UX major no frontend usando a paleta de cores do tema do GitHub como referência principal.
- Reduzir o tamanho base das fontes e padronizar a família tipográfica para o stack do GitHub em toda a aplicação.
- Aumentar a largura do painel lateral para melhorar escaneabilidade, hierarquia de conteúdo e usabilidade.
- Melhorar contraste em superfícies, textos, bordas e estados interativos para leitura mais nítida em toda a interface.
- Consolidar tokens visuais (cores, tipografia, espaçamento e bordas) para garantir consistência entre páginas, painéis e componentes.

## Capabilities

### New Capabilities
- `github-theme-ui-ux-restyle`: Define e aplica sistema visual inspirado no GitHub (fontes, paleta, contraste e layout do painel lateral) em todo o frontend.

### Modified Capabilities
- Nenhuma.

## Impact

- **Frontend**: Atualização de tokens globais de estilo (CSS variables/theme), estilos base de tipografia, layout principal e componentes de navegação/painel lateral.
- **UX Visual**: Mudança perceptível no look and feel com foco em legibilidade, contraste e consistência.
- **Risco técnico**: Necessidade de validação visual em desktop/mobile para evitar regressões de spacing, overflow e acessibilidade de contraste.
