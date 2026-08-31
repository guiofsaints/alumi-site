# -*- coding: utf-8 -*-
"""Gera assets/brasil.svg — mapa do Brasil com divisas estaduais.

    python tools/gen-mapa.py caminho/para/br_states.json

Script de execução única: o SVG resultante é versionado, então só é preciso
rodar de novo para mudar o desenho do mapa. O GeoJSON de origem (limites
estaduais do IBGE) não fica no repositório por causa do tamanho (5,3 MB):

    https://raw.githubusercontent.com/giuliano-macedo/geodata-br-states/main/geojson/br_states.json

Estados e cidades passam pela MESMA projeção de Mercator, que é o que garante
que os marcadores caiam no lugar certo — a versão anterior estimava a posição
por regra de três sobre uma silhueta estilizada, e errava.
"""
import json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)

LARGURA = 1000.0          # largura do viewBox
TOLERANCIA = 1.25         # Douglas-Peucker, em unidades do viewBox
AREA_MINIMA = 6.0         # descarta ilhotas menores que isso (unidades²)

# Rótulos: MG e SP são grandes e recebem a sigla dentro do próprio estado;
# RJ é pequeno demais, então sai para o lado com uma linha-guia.
ROTULO_INTERNO = {"MG", "SP"}
RJ_DESLOC = (108, 58)     # deslocamento do rótulo do RJ a partir do pino

UNIDADES = [  # uf, cidade, lat, lon
    ("SP", "Barueri",        -23.5106, -46.8761),
    ("RJ", "Rio de Janeiro", -22.9028, -43.1789),
    ("MG", "Guaxupé",        -21.3050, -46.7092),
]
DESTAQUE = {u[0] for u in UNIDADES}


def mercator(lon, lat):
    x = math.radians(lon)
    y = math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))
    return x, y


def dp(pts, tol):
    """Douglas-Peucker, iterativo — alguns anéis passam de 20 mil vértices e a
    versão recursiva estoura a pilha."""
    n = len(pts)
    if n < 3:
        return pts
    manter = [False] * n
    manter[0] = manter[-1] = True
    pilha = [(0, n - 1)]
    while pilha:
        ini, fim = pilha.pop()
        if fim - ini < 2:
            continue
        ax, ay = pts[ini]
        bx, by = pts[fim]
        dx, dy = bx - ax, by - ay
        norma = math.hypot(dx, dy)
        pior, idx = 0.0, -1
        for i in range(ini + 1, fim):
            px, py = pts[i]
            if norma == 0:
                d = math.hypot(px - ax, py - ay)
            else:
                d = abs(dy * px - dx * py + bx * ay - by * ax) / norma
            if d > pior:
                pior, idx = d, i
        if pior > tol and idx > 0:
            manter[idx] = True
            pilha.append((ini, idx))
            pilha.append((idx, fim))
    return [p for p, k in zip(pts, manter) if k]


def area(pts):
    s = 0.0
    for i in range(len(pts)):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % len(pts)]
        s += x1 * y2 - x2 * y1
    return abs(s) / 2


def centroide(pts):
    """Centroide de área do polígono — para posicionar a sigla dentro do estado."""
    cx = cy = s = 0.0
    for i in range(len(pts)):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % len(pts)]
        f = x1 * y2 - x2 * y1
        s += f
        cx += (x1 + x2) * f
        cy += (y1 + y2) * f
    if s == 0:
        return pts[0]
    return (cx / (3 * s), cy / (3 * s))


def main(origem):
    dados = json.load(open(origem, encoding="utf-8"))
    feats = dados["features"]

    # 1) projeta tudo e descobre os limites
    brutos, xs, ys = {}, [], []
    for f in feats:
        uf = f.get("id") or f["properties"]["SIGLA"]
        g = f["geometry"]
        polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        aneis = []
        for poly in polys:
            for ring in poly:
                p = [mercator(lon, lat) for lon, lat in ring]
                aneis.append(p)
                xs += [c[0] for c in p]
                ys += [c[1] for c in p]
        brutos[uf] = aneis

    x0, x1 = min(xs), max(xs)
    y0, y1 = min(ys), max(ys)
    esc = LARGURA / (x1 - x0)
    altura = (y1 - y0) * esc

    def para_tela(p):
        x, y = p
        return ((x - x0) * esc, (y1 - y) * esc)   # y invertido: SVG cresce para baixo

    # 2) simplifica e monta os paths
    paths, vertices, maior = {}, 0, {}
    for uf, aneis in brutos.items():
        partes = []
        for ring in aneis:
            pts = [para_tela(p) for p in ring]
            a = area(pts)
            if a < AREA_MINIMA:
                continue                       # ilhota irrelevante nesta escala
            pts = dp(pts, TOLERANCIA)
            if len(pts) < 4:
                continue
            if a > maior.get(uf, (0, None))[0]:
                maior[uf] = (a, pts)           # guarda o anel principal do estado
            vertices += len(pts)
            d = "M%.1f %.1f" % pts[0]
            d += "".join("L%.1f %.1f" % q for q in pts[1:])
            partes.append(d + "Z")
        paths[uf] = "".join(partes)

    # 3) marcadores, pela mesma projeção
    pinos = []
    for uf, cidade, lat, lon in UNIDADES:
        px, py = para_tela(mercator(lon, lat))
        pinos.append((uf, cidade, round(px, 1), round(py, 1)))

    # 4) SVG
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {LARGURA:.0f} {altura:.0f}" '
           f'role="img" aria-label="Mapa do Brasil com as unidades da Alumi destacadas em '
           f'São Paulo, Rio de Janeiro e Minas Gerais">']
    out.append('<g class="ufs">')
    for uf in sorted(paths):                       # destaques por último = ficam por cima
        if uf not in DESTAQUE and paths[uf]:
            out.append(f'<path class="uf" data-uf="{uf}" d="{paths[uf]}"/>')
    for uf in sorted(DESTAQUE):
        if paths.get(uf):
            out.append(f'<path class="uf uf--ativa" data-uf="{uf}" d="{paths[uf]}"/>')
    out.append('</g>')

    # rótulos: sigla dentro dos estados grandes, callout para o RJ
    out.append('<g class="rotulos">')
    for uf in sorted(ROTULO_INTERNO):
        if uf in maior:
            cx, cy = centroide(maior[uf][1])
            out.append(f'<text class="uf-sigla" x="{cx:.1f}" y="{cy:.1f}">{uf}</text>')
    rj = next((p for p in pinos if p[0] == "RJ"), None)
    if rj:
        _, _, px, py = rj
        lx, ly = px + RJ_DESLOC[0], py + RJ_DESLOC[1]
        out.append(f'<path class="guia" d="M{px} {py}L{lx - 12:.1f} {ly - 9:.1f}"/>')
        out.append(f'<text class="uf-sigla uf-sigla--fora" x="{lx:.1f}" y="{ly:.1f}">RJ</text>')
    out.append('</g>')

    out.append('<g class="pinos">')
    for uf, cidade, px, py in pinos:
        out.append(f'<g class="pino"><title>{cidade} — {uf}</title>'
                   f'<circle class="pino__anel" cx="{px}" cy="{py}" r="10"/>'
                   f'<circle class="pino__ponto" cx="{px}" cy="{py}" r="5"/></g>')
    out.append('</g></svg>')
    svg = "".join(out)

    destino = os.path.join(SITE, "assets", "brasil.svg")
    open(destino, "w", encoding="utf-8").write(svg)
    print(f"assets/brasil.svg  viewBox 0 0 {LARGURA:.0f} {altura:.0f}  "
          f"{len(svg)/1024:.1f} KB  {vertices} vértices")
    for uf, cidade, px, py in pinos:
        print(f"  {uf}  {cidade:<16} x={px:>6}  y={py:>6}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("uso: python tools/gen-mapa.py <br_states.json>")
    main(sys.argv[1])
