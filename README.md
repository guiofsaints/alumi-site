# Site Alumi Metais

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
index.html            página completa (HTML + CSS + JS inline)
assets/logo.svg       logotipo vetorial, extraído do PDF do manual da marca
assets/brasil.svg     silhueta do Brasil, extraída da apresentação institucional
assets/favicon.svg    o "A" chanfrado do logotipo
assets/img/*.webp     fotografia de produto e ambientação (536 KB no total)
tools/                gerador do index.html — veja abaixo
vercel.json           configuração de deploy estático
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

## Deploy

Site estático puro — funciona em qualquer host. Sem etapa de build.

- **Vercel** — importe o repositório; o `vercel.json` já está configurado. Framework: *Other*,
  build command vazio, output directory: raiz.
- **GitHub Pages** — Settings → Pages → Deploy from a branch → `main` / `root`.

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
