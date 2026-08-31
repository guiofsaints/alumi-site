# Site Alumi Metais

![Alumi Metais — insumos de cobre para a indústria](assets/og-image.jpg)

**No ar:** <https://guiofsaints.github.io/alumi-site/>

Site institucional de uma página da **Alumi Condutores Elétricos Ltda** (marca *Alumi Metais*).

HTML estático, sem build e sem dependências de runtime. Todo o conteúdo, a paleta, a tipografia
e o logotipo saem do material oficial da marca (manual de identidade visual, apresentação
institucional, vídeo institucional e contrato social).

## Rodar localmente

```bash
python -m http.server 8000
```

Depois abra <http://localhost:8000>.

## Estrutura

```
index.html                 página completa (HTML + CSS + JS inline)
robots.txt, sitemap.xml    gerados pelo build
assets/logo.svg            logotipo vetorial, extraído do PDF do manual da marca
assets/brasil.svg          silhueta do Brasil, extraída da apresentação institucional
assets/favicon.svg         o "A" chanfrado do logotipo
assets/favicon-32.png      fallback PNG do favicon
assets/apple-touch-icon.png  ícone 180×180 para iOS
assets/og-image.jpg        cartão 1200×630 de compartilhamento
assets/img/*.webp          fotografia de produto e ambientação (536 KB no total)
tools/                     gerador do index.html — veja abaixo
vercel.json                configuração de deploy estático
```

## Editando

`index.html` é gerado por `tools/build.py` a partir de `tools/index.template.html` (o template
tem o CSS e a estrutura; o script injeta os SVGs inline e os blocos repetidos: produtos,
capacidades, mercados, diferenciais, valores, setores e o mapa).

- Para mexer em **texto de listas, produtos, CNAEs ou contatos** → edite `tools/build.py` e rode
  `python tools/build.py`.
- Para mexer em **CSS ou estrutura de seções** → edite `tools/index.template.html` e rode o build.
- Se preferir abandonar o gerador e trabalhar direto no HTML, edite `index.html` e apague `tools/`.

O build também escreve `dist/index.html`, uma versão auto-contida (imagens em `data:` URI) usada
para pré-visualização e compartilhamento. Não é necessária para o deploy.

## Metadados e domínio

`SITE_URL`, no topo de `tools/build.py`, é a **única** fonte da URL absoluta. Ela alimenta
`canonical`, `og:url`, `og:image`, `twitter:image`, o JSON-LD, o `robots.txt` e o `sitemap.xml`.

Ao migrar para o domínio próprio, troque essa linha e rode o build:

```python
SITE_URL = "https://alumicondutores.com.br"
```

O `<head>` traz Open Graph e Twitter Card completos e um bloco JSON-LD schema.org com dois nós:
`Organization` (razão social, CNPJ em `taxID`, data de fundação, telefone, e-mail, redes, as três
unidades em `location` e os 8 produtos em `hasOfferCatalog`) e `WebSite`. Para validar depois de
mexer, use o [Rich Results Test](https://search.google.com/test/rich-results) e o
[Sharing Debugger](https://developers.facebook.com/tools/debug/) do Facebook — este último também
serve para forçar a limpeza do cache da prévia.

## Imagem de compartilhamento

`assets/og-image.jpg` (1200×630) é uma captura de `tools/og.html`, que usa os mesmos ativos e a
mesma paleta da página. Para regerar depois de editar o cartão:

```bash
python tools/build.py          # injeta o logotipo → tools/og.built.html
python -m http.server 8000
```

Abra `http://localhost:8000/tools/og.built.html` num viewport de **1200×630 com DPR 2**, capture a
tela (2400×1260) e reduza para 1200×630 em JPEG de qualidade ~88. `tools/og.built.html` é gerado —
edite `tools/og.html`.

## Mapa do Brasil

`assets/brasil.svg` traz as 27 unidades federativas com as divisas reais, os estados de SP, RJ e MG
destacados e um pino em cada cidade onde a Alumi opera. É gerado por `tools/gen-mapa.py` a partir de
um GeoJSON de limites estaduais derivado do IBGE:

<https://raw.githubusercontent.com/giuliano-macedo/geodata-br-states/main/geojson/br_states.json>

```bash
curl -o br_states.json https://raw.githubusercontent.com/giuliano-macedo/geodata-br-states/main/geojson/br_states.json
python tools/gen-mapa.py br_states.json
python tools/build.py
```

O GeoJSON de origem (5,3 MB) não fica no repositório; o SVG resultante (30 KB) é versionado, então
só é preciso rodar isso para mudar o desenho ou as unidades. Os estados e as coordenadas das cidades
passam pela **mesma** projeção de Mercator dentro do script — é isso que garante que os pinos caiam
no lugar certo. As unidades ficam em `UNIDADES`, no topo do arquivo; `TOLERANCIA` controla a
simplificação (Douglas-Peucker) e, por consequência, o tamanho do SVG.

Vale confirmar a licença da fonte do GeoJSON antes de um uso comercial mais amplo, caso atribuição
seja uma exigência do seu lado.

### Preview do repositório no GitHub

A página do repositório em `github.com` **não** lê a `og:image` do site: ela tem a própria
`og:image`, gerada automaticamente pelo GitHub (`opengraph.githubassets.com`) com nome, descrição e
estatísticas. São duas previews independentes.

Para o repositório exibir o cartão da Alumi ao ser compartilhado:

**Settings → General → Social preview → Upload an image** e escolha
`tools/github-social-preview.jpg` (1280×640, 66 KB — o tamanho recomendado pelo GitHub).

Não há endpoint público na API REST para isso; o upload é só pela interface. O arquivo é gerado do
mesmo `tools/og.html`, na variante `tools/og.github.built.html`.

## Deploy

Site estático puro — funciona em qualquer host. Sem etapa de build.

- **Vercel** — importe o repositório; o `vercel.json` já está configurado. Framework: *Other*,
  build command vazio, output directory: raiz.
- **GitHub Pages** — já ativo neste repositório (`main` / `root`, HTTPS forçado). Cada push em
  `main` republica automaticamente.

Para apontar um domínio próprio (`alumicondutores.com.br`) para o Pages, crie um `CNAME` na raiz
com o domínio e configure o DNS conforme a documentação do GitHub Pages.

## Pendências antes de ir ao ar

1. **Formulário sem back-end.** Hoje ele monta a mensagem e abre e-mail ou WhatsApp. Para receber
   os pedidos por servidor, aponte o `<form id="form-cotacao">` para um endpoint.
2. **Marca exibida.** O site usa o logotipo "Alumi Metais" (o do manual) e traz a razão social
   "Alumi Condutores Elétricos Ltda" no rodapé. Confirmar se é assim que se quer aparecer.
3. **Celulares pessoais não publicados.** Só e-mails de setor e o telefone central
   (+55 11 2110-1974). Os celulares das assinaturas de e-mail podem ser acrescentados.
4. **"Qualidade e incentivo fiscal"** é citação literal do vídeo institucional — confirmar se
   continua válido.
5. **Fotos de produto** vêm da apresentação e têm resolução nativa baixa (~255×145 px). Valem
   uma refotografia.
6. **Domínio.** Os materiais citam `alumicondutores.com.br`; o cartão digital traz
   `sitealumi.com.br` como placeholder.

## Nota sobre o material de origem

A pasta `docs/` do workspace (manual, apresentação, papelaria) **não** faz parte deste
repositório: o contrato social contém CPF, RG e endereço residencial do sócio administrador.
Esses arquivos devem ser mantidos fora de qualquer repositório publicado.
