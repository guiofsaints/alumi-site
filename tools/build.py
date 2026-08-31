# -*- coding: utf-8 -*-
"""Gera index.html (e dist/index.html) a partir de tools/index.template.html.

    python tools/build.py

O template carrega o CSS e a estrutura das seções; este script injeta os SVGs
inline (logotipo e mapa) e os blocos repetidos — produtos, capacidades,
mercados, diferenciais, valores e setores de contato.
"""
import os, re, base64, mimetypes

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
TPL  = os.path.join(HERE, "index.template.html")

# ---------------------------------------------------------------- vetores
# NB: CSS do documento não alcança o conteúdo clonado por <use> (shadow tree),
# então o logotipo entra inline em cada ponto de uso.
logo = open(os.path.join(SITE, "assets", "logo.svg"), encoding="utf-8").read()
logo_vb = re.search(r'viewBox="([^"]+)"', logo).group(1)
logo_inner = re.sub(r'^<svg[^>]*>|</svg>$', '', logo).strip()

def logo_svg(extra=""):
    cls = "logo" + (" " + extra if extra else "")
    return (f'<svg class="{cls}" viewBox="{logo_vb}" role="img" '
            f'aria-label="Alumi Metais">{logo_inner}</svg>')

LOGO_TOPO, LOGO_ROD = logo_svg(), logo_svg("logo--claro")

br = open(os.path.join(SITE, "assets", "brasil.svg"), encoding="utf-8").read()
brvb = re.search(r'viewBox="([^"]+)"', br).group(1)
brpath = re.search(r'\sd="([^"]+)"', br).group(1)

# ---------------------------------------------------------------- mapa
# x/y convertidos de lat/lon para o viewBox da silhueta extraída da apresentação.
# As três unidades ficam muito próximas no Sudeste, então cada pino recebe
# uma linha-guia até um rótulo afastado, senão os textos se sobrepõem.
UNID = [  # uf, x, y, x rótulo, y rótulo, âncora, nome
    ("MG", 696, 692, 600, 618, "end",   "Guaxupé · Minas Gerais"),
    ("SP", 691, 749, 556, 838, "end",   "Barueri · São Paulo (matriz)"),
    ("RJ", 785, 733, 898, 806, "start", "Centro · Rio de Janeiro"),
]
pins = "".join(
    f'<g><title>{nome}</title>'
    f'<path class="guia" d="M{x} {y}L{lx + (14 if anc == "end" else -14)} {ly - 12}"/>'
    f'<circle class="pin-halo" cx="{x}" cy="{y}" r="27"/>'
    f'<circle class="pin" cx="{x}" cy="{y}" r="11"/>'
    f'<text class="pin-txt" x="{lx}" y="{ly}" text-anchor="{anc}">{uf}</text>'
    f'</g>'
    for uf, x, y, lx, ly, anc, nome in UNID)
MAPA = (f'<svg class="mapa" viewBox="{brvb}" role="img" '
        f'aria-label="Mapa do Brasil com as unidades da Alumi em São Paulo, Rio de Janeiro e Minas Gerais">'
        f'<path class="terra" d="{brpath}"/>{pins}</svg>')

# ---------------------------------------------------------------- produtos
PRODUTOS = [
    ("Vergalhão de cobre",   "Ø 8,00 mm",                        "prod-vergalhao.webp",  "Vergalhão de cobre 8,00 mm"),
    ("Fio trefilado de cobre", "Ø 1,45 mm",                      "prod-fio.webp",        "Fio trefilado de cobre 1,45 mm"),
    ("Filamentos de cobre",  "Ø 0,25 mm a 0,40 mm",              "prod-filamentos.webp", "Filamentos de cobre 0,25–0,40 mm"),
    ("Cordas de cobre",      "Diversas bitolas",                 "prod-cordas.webp",     "Cordas de cobre"),
    ("Barramentos",          "Cobre e latão · todos os formatos","prod-barramentos.webp","Barramentos de cobre e latão"),
    ("Laminados",            "Cobre, latão e bronze",            "prod-laminados.webp",  "Laminados de cobre, latão e bronze"),
    ("Tubos de cobre",       "Consulte medidas disponíveis",     "prod-tubos.webp",      "Tubos de cobre"),
    ("Sucata de cobre moído","Compra e fornecimento",            "prod-sucata.webp",     "Sucata de cobre moído"),
]
ARROW = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" '
         'aria-hidden="true"><path d="M5 12h13m-5-6 6 6-6 6"/></svg>')
CARDS = "\n".join(
    f'''<article class="card ch rev">
        <div class="card__img"><img src="assets/img/{img}" alt="{alt}" loading="lazy"></div>
        <div class="card__b">
          <h3>{nome}</h3>
          <p class="card__spec">{spec}</p>
          <button class="card__cta" type="button" data-produto="{alt}">Solicitar cotação {ARROW}</button>
        </div>
      </article>''' for nome, spec, img, alt in PRODUTOS)
OPCOES = "\n".join(f'<option>{alt}</option>' for *_, alt in PRODUTOS)

# ---------------------------------------------------------------- capacidades (objeto social)
CAPS = [
    ("Metalurgia do cobre", "Transformação do cobre em insumos industriais, do vergalhão ao filamento.", "CNAE 24.43-1-00"),
    ("Fios, cabos e condutores", "Fabricação de fios, cabos e condutores elétricos.", "CNAE 27.33-3-00"),
    ("Alumínio e laminados", "Produção de alumínio e suas ligas em formas primárias e de laminados.", "CNAE 24.41-5-01 / 02"),
    ("Fundição de não-ferrosos", "Fundição de metais não-ferrosos e suas ligas.", "CNAE 24.52-1-00"),
    ("Outros não-ferrosos", "Metalurgia de outros metais não-ferrosos e suas ligas.", "CNAE 24.49-1-99"),
    ("Resíduos e sucatas metálicos", "Comércio atacadista de resíduos e sucatas — compra de cobre moído.", "CNAE 46.87-7-03"),
    ("Transporte rodoviário de cargas", "Frete municipal, intermunicipal, interestadual e internacional.", "CNAE 49.30-2-01 / 02"),
    ("Comissária de despachos", "Despacho e intermediação documental das cargas.", "CNAE 52.50-8-01"),
]
CAPACIDADES = "\n".join(
    f'<div class="cap"><h3>{t}</h3><p>{d}</p><span class="cnae num">{c}</span></div>'
    for t, d, c in CAPS)

# ---------------------------------------------------------------- mercados
IC = {
 "fabrica": '<path d="M2 20h20M4 20V10l5 3V10l5 3V6l5 3v11"/><path d="M8 20v-4h3v4"/>',
 "frio":    '<path d="M12 2v20M4.9 6.5l14.2 11M19.1 6.5 4.9 17.5"/><path d="m9 4 3 2 3-2M9 20l3-2 3 2"/>',
 "auto":    '<path d="M4 17.2v-3.4l1.8-4A2 2 0 0 1 7.6 8.5h8.8a2 2 0 0 1 1.8 1.3l1.8 4v3.4"/>'
            '<path d="M4 13.8h16"/><circle cx="7.8" cy="17.2" r="1.7"/><circle cx="16.2" cy="17.2" r="1.7"/>',
 "recicla": '<path d="M20 11.5A8 8 0 0 0 6.3 6.3L4 8.6"/><path d="M4 4.2v4.4h4.4"/>'
            '<path d="M4 12.5a8 8 0 0 0 13.7 5.2l2.3-2.3"/><path d="M20 19.8v-4.4h-4.4"/>',
}
MERC = [
    ("fabrica", "Fábricas", "Insumo de cobre para linhas de produção que exigem constância de bitola e liga."),
    ("frio",    "Empresas de refrigeração", "Tubos e condutores para serpentinas, trocadores e sistemas de frio."),
    ("auto",    "Indústria automotiva", "Filamentos, cordas e barramentos para chicotes, motores e componentes."),
    ("recicla", "Compradores de sucata moída", "Fornecimento e compra de cobre moído para reprocesso."),
]
MERCADOS = "\n".join(
    f'''<div class="merc__i ch rev">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"
             stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{IC[k]}</svg>
        <b>{t}</b><span>{d}</span></div>''' for k, t, d in MERC)

# ---------------------------------------------------------------- diferenciais (vídeo institucional)
DIF = [
    ("Qualidade e incentivo fiscal",
     "O nosso compromisso não é apenas oferecer excelência nos insumos de cobre, mas também proporcionar o "
     "atendimento e serviço de alto padrão, com preços competitivos do mercado e vantagens adicionais aos "
     "nossos clientes."),
    ("Atendimento personalizado",
     "Contamos com um time de ponta que está sempre disponível para te atender nos canais de comunicação."),
    ("Parcerias a longo prazo",
     "Estabelecemos relacionamentos sólidos e de confiança com clientes e parceiros, baseados na transparência "
     "e na colaboração. Parcerias fortes são a base para o crescimento mútuo e contínuo no mercado."),
    ("Logística que acompanha sua linha",
     "Prezamos por uma entrega rápida e segura, com sistema de logística próprio no objeto social, para manter "
     "sua produção em constante evolução."),
]
DIFERENCIAIS = "\n".join(f'<div class="dif__i"><h3>{t}</h3><p>{d}</p></div>' for t, d in DIF)

# ---------------------------------------------------------------- valores
VALS = [
    ("Excelência em qualidade", "Mantemos os mais altos padrões de qualidade em todos os aspectos dos produtos e serviços, visando à satisfação e confiança dos clientes."),
    ("Sustentabilidade ambiental", "Priorizamos a sustentabilidade, reutilizando materiais e adotando práticas ecologicamente responsáveis na produção."),
    ("Parceria e confiança", "Relacionamentos sólidos e de longo prazo com clientes e parceiros, baseados na transparência e na colaboração."),
    ("Inovação e adaptação", "Sempre em busca de maneiras criativas de aprimorar produtos e processos, atendendo às necessidades em constante evolução do mercado."),
]
VALORES = "\n".join(f'<div class="val"><h4>{t}</h4><p>{d}</p></div>' for t, d in VALS)

# ---------------------------------------------------------------- setores
SET = [
    ("Comercial", ["joaorocha@alumimetais.com.br", "vaniasobral@alumimetais.com.br", "junior@alumimetais.com.br"]),
    ("Logística", ["logistica@alumimetais.com.br"]),
    ("Financeiro", ["financeiro@alumimetais.com.br"]),
    ("Faturamento", ["faturamento@alumimetais.com.br"]),
    ("Crédito e cobrança", ["deboradonato@alumimetais.com.br"]),
    ("Relações com investidores", ["ajh@alumimetais.com.br"]),
]
SETORES = "\n".join(
    '<div class="setor"><b>%s</b><span class="mails">%s</span></div>' % (
        nome, "".join(f'<a href="mailto:{e}">{e}</a>' for e in mails))
    for nome, mails in SET)

# ---------------------------------------------------------------- montagem
html = open(TPL, encoding="utf-8").read()
for k, v in {
    "{{LOGO_TOPO}}": LOGO_TOPO, "{{LOGO_ROD}}": LOGO_ROD, "{{MAPA}}": MAPA,
    "{{PRODUTOS}}": CARDS, "{{OPCOES_PRODUTO}}": OPCOES, "{{CAPACIDADES}}": CAPACIDADES,
    "{{MERCADOS}}": MERCADOS, "{{DIFERENCIAIS}}": DIFERENCIAIS, "{{VALORES}}": VALORES,
    "{{SETORES}}": SETORES,
}.items():
    assert k in html, "placeholder ausente: " + k
    html = html.replace(k, v)

assert "{{" not in html, "sobrou placeholder"
out = os.path.join(SITE, "index.html")
open(out, "w", encoding="utf-8").write(html)
print(f"index.html  {len(html)/1024:.0f} KB")

# ---------------------------------------------------------------- versão self-contained (artifact)
DIST = os.path.join(SITE, "dist")
os.makedirs(DIST, exist_ok=True)
inl = html

def datauri(rel):
    p = os.path.join(SITE, rel.replace("/", os.sep))
    mt = mimetypes.guess_type(p)[0] or "application/octet-stream"
    return "data:%s;base64,%s" % (mt, base64.b64encode(open(p, "rb").read()).decode())

for rel in sorted(set(re.findall(r'src="(assets/[^"]+)"', inl))):
    inl = inl.replace('src="%s"' % rel, 'src="%s"' % datauri(rel))
inl = inl.replace('<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">', '')
# o artifact injeta seu próprio esqueleto <html>/<head>/<body>
body = re.search(r'<head>(.*?)</head>.*?<body>(.*?)</body>', inl, re.S)
frag = body.group(1).strip() + "\n" + body.group(2).strip()
frag = re.sub(r'<meta charset[^>]*>\s*|<meta name="viewport"[^>]*>\s*', '', frag)
# o charset precisa cair nos primeiros 1024 bytes do documento montado,
# senão os acentos quebram — por isso volta como primeira linha do fragmento
frag = '<meta charset="utf-8">\n' + frag
open(os.path.join(DIST, "index.html"), "w", encoding="utf-8").write(frag)
print(f"dist/index.html  {len(frag.encode())/1024/1024:.2f} MB (auto-contido)")
