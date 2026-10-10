"""Genera componentes.json: biblioteca de componentes de agujero pasante (THT)
con huellas calculadas para placas de una cara hechas por planchado.
Medidas en mm. Reglas caseras: pad 2,0 mm / mecha 0,8 mm por defecto."""
import json, re

P = 2.54
R = lambda v: round(v, 3)

def pad(n, x, y, d=2.0, drill=0.8, sq=None, w=None, h=None, sw=None, sh=None):
    p = {"n": n, "x": R(x), "y": R(y), "d": d, "drill": drill, "sq": (n == 1) if sq is None else sq}
    if w: p.update(w=w, h=h)
    if sw: p.update(sw=sw, sh=sh)
    return p

def center(fp):
    xs = [p["x"] for p in fp["pads"]]; ys = [p["y"] for p in fp["pads"]]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    if abs(cx) < 1e-6 and abs(cy) < 1e-6: return fp
    for p in fp["pads"]: p["x"], p["y"] = R(p["x"] - cx), R(p["y"] - cy)
    for s in fp["silk"]:
        for kx in ("x", "cx", "x1", "x2"):
            if kx in s: s[kx] = R(s[kx] - cx)
        for ky in ("y", "cy", "y1", "y2"):
            if ky in s: s[ky] = R(s[ky] - cy)
        if "d" in s:  # path: desplazar pares de coordenadas absolutas
            nums = s["d"].split()
            out, i, coord = [], 0, []
            for tok in nums: out.append(tok)
            s["d"] = shift_path(s["d"], cx, cy)
            if "bb" in s: s["bb"] = [R(s["bb"][0]-cx), R(s["bb"][1]-cy), R(s["bb"][2]-cx), R(s["bb"][3]-cy)]
    for t in fp.get("texts", []): t["x"], t["y"] = R(t["x"] - cx), R(t["y"] - cy)
    return fp

def shift_path(d, cx, cy):
    # solo comandos M, L, A absolutos (como los generamos nosotros)
    toks = d.replace(",", " ").split(); out = []; i = 0
    while i < len(toks):
        c = toks[i]; out.append(c); i += 1
        if c in ("M", "L"):
            out += [str(R(float(toks[i]) - cx)), str(R(float(toks[i+1]) - cy))]; i += 2
        elif c == "A":
            out += toks[i:i+5]; out += [str(R(float(toks[i+5]) - cx)), str(R(float(toks[i+6]) - cy))]; i += 7
    return " ".join(out)

mm = lambda v: (f"{v:g}").replace(".", ",") + " mm"

# ---------------- encapsulados ----------------
def dip(n, row=7.62):
    h = n // 2; L = (h - 1) * P; pads = []
    for i in range(h): pads.append(pad(i + 1, -row / 2, -L / 2 + i * P, 2.4, w=2.4, h=1.8))
    for i in range(h): pads.append(pad(h + i + 1, row / 2, L / 2 - i * P, 2.4, w=2.4, h=1.8))
    bw = row - 3.2; top = -L / 2 - 1.6
    return {"pkg": f"DIP-{n}" + (" ancho" if row > 8 else ""), "pads": pads, "row": row,
            "silk": [{"t": "rect", "x": R(-bw/2), "y": R(top), "w": R(bw), "h": R(L + 3.2)},
                     {"t": "path", "d": f"M -1 {R(top)} A 1 1 0 0 0 1 {R(top)}", "bb": [-1, R(top), 1, R(top+1)]}],
            "dims": [[1, 2, "2,54 mm"], [1, n, mm(row)]]}

def sip(n, pitch=P, name=None):
    L = (n - 1) * pitch
    pads = [pad(i + 1, 0, -L / 2 + i * pitch, 2.4, w=2.4, h=1.8) for i in range(n)]
    return {"pkg": name or f"Tira {n} pines", "pads": pads,
            "silk": [{"t": "rect", "x": -1.27, "y": R(-L/2-1.27), "w": 2.54, "h": R(L+2.54)}],
            "dims": [[1, 2, mm(pitch)]] if n > 1 else []}

def axial(name, span, L, D, band=False, drill=0.8, d=2.0):
    pads = [pad(1, -span/2, 0, d, drill, sq=band), pad(2, span/2, 0, d, drill, sq=False)]
    silk = [{"t": "rect", "x": R(-L/2), "y": R(-D/2), "w": L, "h": D},
            {"t": "line", "x1": R(-span/2 + d/2 + .2), "y1": 0, "x2": R(-L/2), "y2": 0},
            {"t": "line", "x1": R(L/2), "y1": 0, "x2": R(span/2 - d/2 - .2), "y2": 0}]
    if band: silk.append({"t": "rect", "x": R(L/2 - 1.3), "y": R(-D/2), "w": 0.7, "h": D, "fill": 1})
    return {"pkg": name, "pads": pads, "silk": silk, "dims": [[1, 2, mm(span)]]}

def radial(name, pitch, dia, polar=False, drill=0.8):
    o = {}
    if pitch < 2.7: o = dict(w=R(max(1.4, pitch - 0.6)), h=2.2)
    return {"pkg": name, "pads": [pad(1, -pitch/2, 0, 2.2 if o else 2.0, drill, sq=polar, **o), pad(2, pitch/2, 0, 2.2 if o else 2.0, drill, sq=False, **o)],
            "silk": [{"t": "circle", "cx": 0, "cy": 0, "r": dia/2}],
            "texts": [{"x": R(-pitch/2 - 1.8), "y": R(-dia/2 + 0.4), "s": "+"}] if polar else [],
            "dims": [[1, 2, mm(pitch)]]}

def boxcap(name, pitch, w, h):
    return {"pkg": name, "pads": [pad(1, -pitch/2, 0, sq=False), pad(2, pitch/2, 0, sq=False)],
            "silk": [{"t": "rect", "x": R(-w/2), "y": R(-h/2), "w": w, "h": h}], "dims": [[1, 2, mm(pitch)]]}

def disc(name, pitch, w, h):
    return {"pkg": name, "pads": [pad(1, -pitch/2, 0, sq=False), pad(2, pitch/2, 0, sq=False)],
            "silk": [{"t": "rect", "x": R(-w/2), "y": R(-h/2), "w": w, "h": h, "rx": R(h/2)}], "dims": [[1, 2, mm(pitch)]]}

def led(dia):
    r = dia/2 + 0.4
    return {"pkg": f"LED {mm(dia)}", "pads": [pad(1, -P/2, 0, 2.2, w=1.9, h=2.2), pad(2, P/2, 0, 2.2, sq=False, w=1.9, h=2.2)],
            "silk": [{"t": "path", "d": f"M {R(-r*.82)} {R(-r*.57)} A {R(r)} {R(r)} 0 1 1 {R(-r*.82)} {R(r*.57)} L {R(-r*.82)} {R(-r*.57)}", "bb": [R(-r), R(-r), R(r), R(r)]}],
            "texts": [{"x": R(-P/2), "y": R(-r - 0.8), "s": "K"}], "dims": [[1, 2, "2,54 mm"]]}

def to92():
    return {"pkg": "TO-92", "pads": [pad(1, -P, 0, 1.9), pad(2, 0, 0, 1.9, sq=False), pad(3, P, 0, 1.9, sq=False)],
            "silk": [{"t": "path", "d": "M -2.6 1.4 A 2.9 2.9 0 1 1 2.6 1.4 L -2.6 1.4", "bb": [-2.9, -2.9, 2.9, 1.4]}],
            "dims": [[1, 2, "2,54 mm"]], "nota": "Con la cara plana mirando hacia vos, el pin 1 es el de la izquierda."}

def to126():
    p = 2.29
    return {"pkg": "TO-126", "pads": [pad(1, -p, 0, 2.4, 1.0, w=1.6, h=2.4), pad(2, 0, 0, 2.4, 1.0, sq=False, w=1.6, h=2.4), pad(3, p, 0, 2.4, 1.0, sq=False, w=1.6, h=2.4)],
            "silk": [{"t": "rect", "x": -4, "y": -2.4, "w": 8, "h": 3.4}], "dims": [[1, 2, "2,29 mm"]],
            "nota": "Con la cara con letras mirando hacia vos, el pin 1 es el de la izquierda."}

def to220():
    return {"pkg": "TO-220", "pads": [pad(1, -P, 0, 2.6, 1.0, w=1.9, h=2.6), pad(2, 0, 0, 2.6, 1.0, sq=False, w=1.9, h=2.6), pad(3, P, 0, 2.6, 1.0, sq=False, w=1.9, h=2.6)],
            "silk": [{"t": "rect", "x": -5.2, "y": -3.3, "w": 10.4, "h": 4.8}, {"t": "line", "x1": -5.2, "y1": -2.1, "x2": 5.2, "y2": -2.1}],
            "dims": [[1, 2, "2,54 mm"]], "nota": "Con las letras mirando hacia vos y las patas abajo, el pin 1 es el de la izquierda. La línea gruesa marca la aleta metálica."}

def bornera(n, p=5.08):
    L = (n-1)*p
    return {"pkg": f"Bornera {n} vías 5,08 mm", "pads": [pad(i+1, -L/2+i*p, 0, 2.6, 1.2, sq=(i == 0)) for i in range(n)],
            "silk": [{"t": "rect", "x": R(-L/2-2.54), "y": -3.8, "w": R(L+5.08), "h": 7.6}, {"t": "line", "x1": R(-L/2-2.54), "y1": 2.4, "x2": R(L/2+2.54), "y2": 2.4}],
            "dims": [[1, 2, "5,08 mm"]]}

ENC = {}
def add(key, fp): ENC[key] = center(fp)

for n in (4, 6, 8, 14, 16, 18, 20, 28): add(f"DIP-{n}", dip(n))
add("DIP-24W", dip(24, 15.24)); add("DIP-40W", dip(40, 15.24))
add("DISP-7SEG", (lambda f: (f.update(pkg="Display 7 segmentos 0,56\"", silk=[{"t": "rect", "x": -6.3, "y": -9.5, "w": 12.6, "h": 19}]), f)[1])(dip(10, 15.24)))
f = dip(30, 15.24); f["pkg"] = "Arduino Nano (2×15)"; f["silk"] = [{"t": "rect", "x": -9, "y": -21.7, "w": 18, "h": 43.4}, {"t": "rect", "x": -3.8, "y": -23, "w": 7.6, "h": 3.6}]
add("NANO", f)
for n in range(1, 41): add(f"SIP-{n}", sip(n))
add("TO-92", to92()); add("TO-126", to126()); add("TO-220", to220())
add("AX-R14", axial("Axial 1/4 W · 10,16 mm", 10.16, 6.3, 2.5))
add("AX-R12", axial("Axial 1/2 W · 12,7 mm", 12.7, 9, 3.2))
add("AX-R1W", axial("Axial 1 W · 15,24 mm", 15.24, 11, 4.5, drill=1.0))
add("AX-R2W", axial("Axial 2 W · 20,32 mm", 20.32, 15, 5, drill=1.0))
add("AX-R5W", axial("Cemento 5 W · 27,94 mm", 27.94, 22, 9.5, drill=1.2, d=2.6))
add("DO-35", axial("DO-35 · 7,62 mm", 7.62, 4, 1.9, band=True))
add("DO-41", axial("DO-41 · 10,16 mm", 10.16, 5.2, 2.7, band=True, drill=1.0))
add("DO-201", axial("DO-201AD · 15,24 mm", 15.24, 9.5, 5.3, band=True, drill=1.4, d=2.8))
ELEC = [(5, 2.0), (6.3, 2.5), (8, 3.5), (10, 5.0), (13, 5.0), (16, 7.5)]
for dia, pt in ELEC: add(f"CE-D{dia}", radial(f"Radial Ø{mm(dia)} · {mm(pt)}", pt, dia, polar=True))
f = disc("Disco cerámico · 2,54 mm", 2.54, 4.6, 2.6)
for p_ in f["pads"]: p_.update(w=1.9, h=2.2, d=2.2)
add("CC-2.54", f)
add("CC-5.08", disc("Disco cerámico · 5,08 mm", 5.08, 7, 3.2))
for pt, w, h in ((5, 7.2, 3.5), (7.5, 10, 4.5), (10, 13, 6), (15, 18, 8)):
    add(f"CP-{pt}", boxcap(f"Caja poliéster · {mm(pt)}", pt, w, h))
add("CT-2.54", radial("Tantalio gota · 2,54 mm", 2.54, 5, polar=True))
for dd in (3, 5, 10): add(f"LED-{dd}", led(dd))
add("LDR", (lambda f: (f.update(silk=[{"t": "rect", "x": -2.55, "y": -2.15, "w": 5.1, "h": 4.3, "rx": 1.8}]), f)[1])(radial("LDR 5 mm · 3,4 mm", 3.4, 5)))
add("NTC", disc("NTC disco · 5,08 mm", 5.08, 6, 3))
add("BUZZER", radial("Buzzer Ø12 · 7,6 mm", 7.6, 12, polar=True))
for n in (2, 3): add(f"BORN-{n}", bornera(n))
add("PUL6", {"pkg": "Pulsador 6×6 mm", "pads": [pad(1, -3.25, -2.25, 2.1, 1.0), pad(2, 3.25, -2.25, 2.1, 1.0), pad(3, -3.25, 2.25, 2.1, 1.0), pad(4, 3.25, 2.25, 2.1, 1.0)],
             "silk": [{"t": "rect", "x": -3, "y": -3, "w": 6, "h": 6}, {"t": "circle", "cx": 0, "cy": 0, "r": 1.75}], "dims": [[1, 2, "6,5 mm"], [1, 3, "4,5 mm"]]})
add("3386P", {"pkg": "Preset 3386P", "pads": [pad(1, -P, 1.27), pad(2, 0, -1.27, sq=False), pad(3, P, 1.27, sq=False)],
              "silk": [{"t": "rect", "x": -4.8, "y": -4.8, "w": 9.6, "h": 9.6}, {"t": "circle", "cx": 0, "cy": 0, "r": 3}], "dims": [[1, 3, "5,08 mm"]]})
add("POT9", {"pkg": "Potenciómetro 9 mm (RV09)", "pads": [pad(1, 0, 0, 2.4, 1.0, w=2.4, h=1.8), pad(2, 0, 2.5, 2.4, 1.0, w=2.4, h=1.8), pad(3, 0, 5, 2.4, 1.0, w=2.4, h=1.8),
             pad(4, 7.5, 7.3, 2.8, 1.1, sq=False, w=2.8, h=3.4, sw=1.1, sh=1.8), pad(5, 7.5, -2.3, 2.8, 1.1, sq=False, w=2.8, h=3.4, sw=1.1, sh=1.8)],
             "silk": [{"t": "rect", "x": 1, "y": -2.25, "w": 11.35, "h": 9.5}, {"t": "circle", "cx": 7.5, "cy": 2.5, "r": 3.5}], "dims": [[1, 2, "2,5 mm"]],
             "nota": "Los pads 4 y 5 son las patas de sujeción: van soldadas pero no se conectan a nada."})
add("HC49", {"pkg": "Cristal HC-49 · 4,88 mm", "pads": [pad(1, -2.44, 0, sq=False), pad(2, 2.44, 0, sq=False)],
             "silk": [{"t": "rect", "x": -5.6, "y": -2.3, "w": 11.2, "h": 4.6, "rx": 2.3}], "dims": [[1, 2, "4,88 mm"]]})
add("SRD", {"pkg": "Relé Songle SRD", "pads": [pad(1, 0, 0, 3.0, 1.3), pad(2, 1.95, 6.05, 2.5, 1.0, sq=False), pad(3, 14.15, 6.05, 3.0, 1.3, sq=False),
            pad(4, 14.2, -6.0, 3.0, 1.3, sq=False), pad(5, 1.95, -5.95, 2.5, 1.0, sq=False)],
            "silk": [{"t": "rect", "x": -1.3, "y": -7.7, "w": 19.6, "h": 15.4}], "dims": [[2, 5, "12 mm"]],
            "nota": "Para saber cuál es NC: medí con el tester sin energía; la pata que tiene continuidad con COM es NC."})
add("JACK", {"pkg": "Jack DC 5,5×2,1 mm", "pads": [pad(1, 0, 0, 3.5, 1.0, sq=True, w=3.5, h=3.5, sw=1.0, sh=3.0), pad(2, -6, 0, 3.0, 1.0, sq=False, w=3.0, h=3.5, sw=1.0, sh=3.0),
             pad(3, -3, 4.7, 3.5, 1.0, sq=False, w=3.5, h=3.5, sw=3.0, sh=1.0)],
             "silk": [{"t": "rect", "x": -13.7, "y": -4.5, "w": 14.5, "h": 9}, {"t": "line", "x1": -10.2, "y1": -4.5, "x2": -10.2, "y2": 4.5}], "dims": [[1, 2, "6 mm"]],
             "nota": "Los agujeros son ranuras: hacé dos agujeros juntos de 1 mm y uní con una lima fina."})
add("BR-W", {"pkg": "Puente redondo W04 / 2W10", "pads": [pad(1, 0, 0, 2.0, 1.0), pad(2, 0, 5.08, 2.0, 1.0), pad(3, 5.08, 5.08, 2.0, 1.0), pad(4, 5.08, 0, 2.0, 1.0)],
             "silk": [{"t": "circle", "cx": 2.54, "cy": 2.54, "r": 4.9}], "dims": [[1, 4, "5,08 mm"]]})
add("BR-KBP", {"pkg": "Puente en línea KBP", "pads": [pad(i+1, i*3.85, 0, 2.2, 1.2) for i in range(4)],
               "silk": [{"t": "rect", "x": -1.59, "y": -2.41, "w": 14.73, "h": 4.83}], "dims": [[1, 2, "3,85 mm"]]})

# ---------------- componentes ----------------
C = []
def comp(nombre, cat, enc, alias, desc, pines=None, **kw):
    a = sorted({re.sub(r"[\s\-_./]", "", x.lower()) for x in alias}, key=len, reverse=True)
    d = {"nombre": nombre, "cat": cat, "enc": enc, "alias": a, "desc": desc}
    if pines: d["pines"] = pines
    d.update(kw); C.append(d)

# Resistencias
comp("Resistencia de carbón 1/4 W", "Resistencias", "AX-R14", ["resistencia", "resistor", "resist", "1/4w", "14w", "carbon"], "La más común. Se dobla dejando 10,16 mm entre patas. El valor se lee por los colores.")
comp("Resistencia 1/2 W", "Resistencias", "AX-R12", ["1/2w", "12w", "medio watt", "mediowatt"], "Un poco más grande que la de 1/4 W, aguanta el doble de potencia.")
comp("Resistencia 1 W", "Resistencias", "AX-R1W", ["1w", "unwatt", "1watt"], "Para cargas que calientan. Dejala separada un par de milímetros de la placa.")
comp("Resistencia 2 W", "Resistencias", "AX-R2W", ["2w", "2watt", "doswatt"], "Resistencia de potencia. Dejala separada de la placa para que ventile.")
comp("Resistencia de cemento 5 W", "Resistencias", "AX-R5W", ["5w", "cemento", "ceramica5w", "5watt"], "Cuerpo cerámico blanco. Calienta mucho: nunca apoyada sobre la placa.")
comp("LDR (fotorresistencia) 5 mm", "Resistencias", "LDR", ["ldr", "fotorresistencia", "fotoresistencia", "gl5528", "sensordeluz"], "Su resistencia baja cuando le da la luz. No tiene polaridad. Medí la separación de tus patas: suele ser 3,4 mm.")
comp("Termistor NTC", "Resistencias", "NTC", ["ntc", "termistor"], "Su resistencia baja cuando sube la temperatura. No tiene polaridad.")
comp("Preset 3386P (trimpot)", "Resistencias", "3386P", ["preset", "trimpot", "trimmer", "3386"], "Resistencia ajustable con destornillador. La pata del medio es el cursor.", ["Extremo 1", "Cursor", "Extremo 2"])
comp("Potenciómetro 9 mm", "Resistencias", "POT9", ["potenciometro", "pote", "rv09", "potenciometrochico"], "Potenciómetro con eje para perilla. El de 16 mm grande se conecta con cables.", ["Extremo 1", "Cursor", "Extremo 2", "Sujeción", "Sujeción"])

# Capacitores electrolíticos (tamaño típico 16–25 V)
EL = [(1, 5), (2.2, 5), (4.7, 5), (10, 5), (22, 5), (47, 6.3), (100, 6.3), (220, 8), (470, 10), (1000, 10), (2200, 13), (4700, 16)]
prev = 0
for v, dia in EL:
    comp(f"Electrolítico {f'{v:g}'.replace('.', ',')} µF", "Capacitores", f"CE-D{dia}", ["electrolitico", "electrolit"],
         f"Tiene polaridad: la franja del cuerpo marca el negativo. El pad cuadrado es el +. Tamaño típico para 16–25 V; si es de más voltaje, el cuerpo es más grande.",
         ["+ (positivo)", "− (negativo)"], familia="electrolitico", rango=[prev, v]); prev = v
comp("Capacitor cerámico chico (hasta 1 nF)", "Capacitores", "CC-2.54", ["ceramico", "lenteja", "disco"], "Sin polaridad. Valores en pF: 22 pF para cristales, 100 pF, 1 nF.", familia="ceramico", rango=[0, 1])
comp("Capacitor cerámico (más de 1 nF)", "Capacitores", "CC-5.08", ["ceramico", "lenteja", "104", "multicapa"], "Sin polaridad. El 100 nF (código 104) va al lado de cada integrado para filtrar ruido.", familia="ceramico", rango=[1, 1000])
for pt, lo, hi, txt in ((5, 0, 100, "1 nF a 100 nF"), (7.5, 100, 470, "220 nF a 470 nF"), (10, 470, 1000, "1 µF"), (15, 1000, 4700, "2,2 µF a 4,7 µF")):
    comp(f"Poliéster {txt}", "Capacitores", f"CP-{pt}", ["poliester", "mkt", "mylar", "mkp"],
         "Sin polaridad, estable y preciso. Bueno para filtros y temporizadores. Verificá la separación de patas de tu capacitor.", familia="poliester", rango=[lo, hi])
comp("Tantalio (gota)", "Capacitores", "CT-2.54", ["tantalio", "tantalo"], "Tiene polaridad: la pata más larga o marcada con + es el positivo.", ["+ (positivo)", "− (negativo)"])

# Diodos
comp("Diodo 1N4007", "Diodos", "DO-41", ["1n4007", "1n4001", "1n4002", "1n4003", "1n4004", "1n4005", "1n4006", "diodo", "rectificador"], "Diodo rectificador de 1 A. La banda del cuerpo marca el cátodo (K).", ["A (ánodo)", "K (cátodo)"])
comp("Diodo Schottky 1N5819", "Diodos", "DO-41", ["1n5819", "1n5817", "1n5818", "schottky"], "Diodo rápido con poca caída de tensión. Ideal para fuentes y protección.", ["A (ánodo)", "K (cátodo)"])
comp("Diodo rápido UF4007 / FR107", "Diodos", "DO-41", ["uf4007", "fr107", "fr207", "her107"], "Diodo de recuperación rápida para fuentes conmutadas.", ["A (ánodo)", "K (cátodo)"])
comp("Diodo 1N5408 (3 A)", "Diodos", "DO-201", ["1n5408", "1n5400", "1n5404", "1n5406", "diodo3a"], "Diodo rectificador de 3 A. Patas gruesas: mecha de 1,4 mm.", ["A (ánodo)", "K (cátodo)"])
comp("Diodo 1N4148", "Diodos", "DO-35", ["1n4148", "1n914", "4148", "diododesenal"], "Diodo chico de señal, rápido. La banda negra marca el cátodo.", ["A (ánodo)", "K (cátodo)"])
comp("Zener 1/2 W (BZX55)", "Diodos", "DO-35", ["bzx55", "bzx79", "zener05", "zenerchico"], "Mantiene una tensión fija. La banda marca el cátodo.", ["A (ánodo)", "K (cátodo)"])
comp("Zener 1 W (1N47xx)", "Diodos", "DO-41", ["zener", "1n4728", "1n4733", "1n4742", "1n4744", "1n47"], "Zener de 1 W. 1N4733 = 5,1 V, 1N4742 = 12 V. La banda marca el cátodo.", ["A (ánodo)", "K (cátodo)"])
comp("Puente rectificador redondo W04", "Diodos", "BR-W", ["w04", "w10", "2w10", "puenteredondo", "puente", "puenterectificador"], "Cuatro diodos en uno. Revisá las marcas + y ~ del cuerpo.", ["+", "~ (alterna)", "−", "~ (alterna)"])
comp("Puente rectificador KBP", "Diodos", "BR-KBP", ["kbp", "kbp206", "kbp307", "kbp210", "puenteenlinea"], "Puente en línea. El pin con el bisel es el +.", ["+", "~ (alterna)", "~ (alterna)", "−"])

# LEDs y ópticos
comp("LED 5 mm", "LEDs y ópticos", "LED-5", ["led5", "led", "leds", "diodoled", "led5mm"], "La pata corta y el lado plano son el cátodo (K, negativo). Siempre con una resistencia en serie.", ["K (cátodo, −)", "A (ánodo, +)"])
comp("LED 3 mm", "LEDs y ópticos", "LED-3", ["led3", "led3mm"], "LED chico. Pata corta y lado plano: cátodo.", ["K (cátodo, −)", "A (ánodo, +)"])
comp("LED 10 mm", "LEDs y ópticos", "LED-10", ["led10", "led10mm", "ledgrande"], "LED grande. Pata corta y lado plano: cátodo.", ["K (cátodo, −)", "A (ánodo, +)"])
seg = ["e", "d", "Común", "c", "DP (punto)", "b", "a", "Común", "f", "g"]
comp("Display 7 segmentos 0,56\"", "LEDs y ópticos", "DISP-7SEG", ["display", "7segmentos", "sietesegmentos", "5161"], "Pines comunes en el medio (3 y 8). Puede ser ánodo o cátodo común: probalo con una pila de 3 V.", seg)
comp("Optoacoplador PC817", "LEDs y ópticos", "DIP-4", ["pc817", "817", "optoacoplador", "opto", "el817"], "Separa eléctricamente dos circuitos con luz.", ["A (ánodo LED)", "K (cátodo LED)", "E (emisor)", "C (colector)"])
comp("Optoacoplador 4N35", "LEDs y ópticos", "DIP-6", ["4n35", "4n25", "4n26", "4n33"], "Optoacoplador con transistor de salida.", ["A (ánodo LED)", "K (cátodo LED)", "Sin uso", "E (emisor)", "C (colector)", "B (base)"])
comp("Optotriac MOC3021", "LEDs y ópticos", "DIP-6", ["moc3021", "moc3041", "moc3022", "moc3023", "moc3063", "optotriac"], "Para disparar un triac desde un microcontrolador. Cuidado: el lado del triac va a 220 V.", ["A (ánodo LED)", "K (cátodo LED)", "Sin uso", "MT (terminal)", "Sin uso", "MT (terminal)"])

# Transistores
CBE = ["C (colector)", "B (base)", "E (emisor)"]; EBC = CBE[::-1]; ECB = ["E (emisor)", "C (colector)", "B (base)"]; BCE = ["B (base)", "C (colector)", "E (emisor)"]
comp("Transistor BC547 (NPN)", "Transistores", "TO-92", ["bc547", "bc546", "bc548", "bc549", "bc550"], "NPN de señal, el más usado en la escuela. Orden europeo: C-B-E.", CBE)
comp("Transistor BC557 (PNP)", "Transistores", "TO-92", ["bc557", "bc556", "bc558", "bc559", "bc560"], "PNP de señal, complemento del BC547. Orden C-B-E.", CBE)
comp("Transistor BC337 (NPN)", "Transistores", "TO-92", ["bc337", "bc338"], "NPN de 800 mA, para relés chicos. Orden C-B-E.", CBE)
comp("Transistor BC327 (PNP)", "Transistores", "TO-92", ["bc327", "bc328"], "PNP de 800 mA. Orden C-B-E.", CBE)
comp("Transistor BC639 (NPN)", "Transistores", "TO-92", ["bc639", "bc640"], "Transistor de 1 A. Ojo: orden E-C-B, distinto al BC547.", ECB)
comp("Transistor 2N2222A (NPN)", "Transistores", "TO-92", ["2n2222", "pn2222", "2n2222a", "2n222"], "NPN de uso general, versión americana. Orden E-B-C (al revés que el BC547).", EBC)
comp("Transistor 2N2907A (PNP)", "Transistores", "TO-92", ["2n2907", "pn2907"], "PNP complemento del 2N2222. Orden E-B-C.", EBC)
comp("Transistor 2N3904 (NPN)", "Transistores", "TO-92", ["2n3904"], "NPN de señal. Orden E-B-C.", EBC)
comp("Transistor 2N3906 (PNP)", "Transistores", "TO-92", ["2n3906"], "PNP de señal. Orden E-B-C.", EBC)
comp("Transistor 2N5551 (NPN alta tensión)", "Transistores", "TO-92", ["2n5551", "2n5550"], "Aguanta hasta 160 V. Orden E-B-C.", EBC)
comp("Transistor 2N5401 (PNP alta tensión)", "Transistores", "TO-92", ["2n5401", "2n5400"], "PNP de 150 V. Orden E-B-C.", EBC)
comp("Transistor MPSA42 (NPN 300 V)", "Transistores", "TO-92", ["mpsa42", "mpsa92", "ksp42"], "Para alta tensión. Orden E-B-C.", EBC)
comp("Transistor S8050 (NPN)", "Transistores", "TO-92", ["s8050", "s8550", "ss8050", "ss8550", "8050", "8550"], "Muy común en módulos chinos. Orden E-B-C.", EBC)
comp("MOSFET 2N7000", "Transistores", "TO-92", ["2n7000"], "MOSFET chico de canal N, se maneja directo desde Arduino.", ["S (fuente)", "G (compuerta)", "D (drenador)"])
comp("MOSFET BS170", "Transistores", "TO-92", ["bs170"], "Como el 2N7000 pero con el orden de patas invertido.", ["D (drenador)", "G (compuerta)", "S (fuente)"])
comp("Transistor BD139 (NPN)", "Transistores", "TO-126", ["bd139", "bd135", "bd137"], "Potencia media, 1,5 A. Orden E-C-B.", ECB)
comp("Transistor BD140 (PNP)", "Transistores", "TO-126", ["bd140", "bd136", "bd138"], "Complemento del BD139. Orden E-C-B.", ECB)
comp("Transistor TIP31 (NPN)", "Transistores", "TO-220", ["tip31", "tip29", "tip41", "tip31c", "tip41c"], "NPN de potencia de 3 A (TIP41: 6 A). Orden B-C-E.", BCE)
comp("Transistor TIP32 (PNP)", "Transistores", "TO-220", ["tip32", "tip30", "tip42", "tip32c", "tip42c"], "PNP de potencia, complemento del TIP31. Orden B-C-E.", BCE)
comp("Darlington TIP120 (NPN)", "Transistores", "TO-220", ["tip120", "tip121", "tip122"], "Darlington de 5 A: maneja motores y tiras LED con poca corriente de base.", BCE)
comp("Darlington TIP125 (PNP)", "Transistores", "TO-220", ["tip125", "tip126", "tip127"], "Darlington PNP, complemento del TIP120.", BCE)
comp("Transistor BD243 (NPN)", "Transistores", "TO-220", ["bd243", "bd244"], "Potencia de 6 A. Orden B-C-E.", BCE)
comp("MOSFET IRFZ44N", "Transistores", "TO-220", ["irfz44", "irfz44n", "irf3205", "irf540", "irf540n", "irf520", "irf"], "MOSFET de potencia canal N. Para manejarlo bien desde 5 V conviene un IRLZ44N.", ["G (compuerta)", "D (drenador)", "S (fuente)"])
comp("MOSFET IRF9540 (canal P)", "Transistores", "TO-220", ["irf9540", "irf9530", "irf4905"], "MOSFET de potencia canal P.", ["G (compuerta)", "D (drenador)", "S (fuente)"])
comp("Triac BT136", "Transistores", "TO-220", ["bt136", "bt137", "bt138", "bta16", "bta12", "bta08", "triac"], "Controla cargas de 220 V alterna. Peligroso: trabajalo siempre con un adulto o docente.", ["MT1", "MT2", "G (compuerta)"])
comp("Tiristor BT151 (SCR)", "Transistores", "TO-220", ["bt151", "tic106", "tic116", "scr", "tiristor"], "Rectificador controlado. Una vez disparado, sigue conduciendo.", ["K (cátodo)", "A (ánodo)", "G (compuerta)"])

# Reguladores y sensores
comp("Regulador 7805 (5 V)", "Reguladores y sensores", "TO-220", ["7805", "lm7805", "l7805", "7806", "7808", "7809", "7812", "7815", "7824", "lm7812", "regulador"], "Regulador fijo positivo (7812 = 12 V). Lleva un capacitor en la entrada y otro en la salida.", ["IN (entrada)", "GND", "OUT (salida)"])
comp("Regulador 7905 (−5 V)", "Reguladores y sensores", "TO-220", ["7905", "lm7905", "7912", "7915", "79"], "Regulador negativo. Ojo: el orden de patas es distinto al 7805.", ["GND", "IN (entrada)", "OUT (salida)"])
comp("Regulador LM317 (ajustable)", "Reguladores y sensores", "TO-220", ["lm317", "317", "lm317t"], "Tensión ajustable de 1,25 a 37 V con dos resistencias.", ["ADJ (ajuste)", "OUT (salida)", "IN (entrada)"])
comp("Regulador LM337 (ajustable negativo)", "Reguladores y sensores", "TO-220", ["lm337", "337"], "Versión negativa del LM317.", ["ADJ (ajuste)", "IN (entrada)", "OUT (salida)"])
comp("Regulador 78L05 (chico)", "Reguladores y sensores", "TO-92", ["78l05", "78l12", "78l09"], "Regulador de 100 mA en cuerpo de transistor.", ["OUT (salida)", "GND", "IN (entrada)"])
comp("Referencia TL431", "Reguladores y sensores", "TO-92", ["tl431", "431"], "Zener ajustable de precisión.", ["REF", "A (ánodo)", "K (cátodo)"])
comp("Sensor de temperatura LM35", "Reguladores y sensores", "TO-92", ["lm35", "lm35dz"], "Da 10 mV por cada grado. Con la cara plana hacia vos: +5 V, salida, GND.", ["+VS", "VOUT (salida)", "GND"])
comp("Sensor de temperatura DS18B20", "Reguladores y sensores", "TO-92", ["ds18b20", "18b20"], "Sensor digital de un solo cable. Lleva una resistencia de 4,7 kΩ entre DQ y VDD.", ["GND", "DQ (datos)", "VDD"])

# Integrados
P555 = ["GND", "TRIG (disparo)", "OUT (salida)", "RESET", "CTRL (control)", "THR (umbral)", "DIS (descarga)", "VCC (+)"]
DUAL = ["OUT 1", "IN 1 −", "IN 1 +", "GND / V−", "IN 2 +", "IN 2 −", "OUT 2", "VCC (+)"]
comp("NE555 (temporizador)", "Integrados", "DIP-8", ["ne555", "555", "lm555", "ne555p", "timer", "temporizador"], "Genera pulsos, hace titilar LEDs y arma sirenas.", P555)
comp("NE556 (doble 555)", "Integrados", "DIP-14", ["ne556", "556"], "Dos 555 en un solo integrado.", ["DIS 1", "THR 1", "CTRL 1", "RESET 1", "OUT 1", "TRIG 1", "GND", "TRIG 2", "OUT 2", "RESET 2", "CTRL 2", "THR 2", "DIS 2", "VCC"])
comp("LM741 (amplificador operacional)", "Integrados", "DIP-8", ["lm741", "741", "ua741", "tl071", "tl081", "ca3140"], "Operacional clásico de un canal (TL071 y TL081 usan la misma huella).", ["Offset", "IN −", "IN +", "V −", "Offset", "OUT", "V +", "Sin uso"])
comp("LM358 (operacional doble)", "Integrados", "DIP-8", ["lm358", "358", "lm358n"], "Dos operacionales, funciona con una sola fuente de 5 V.", DUAL)
comp("TL072 / TL082 (operacional doble)", "Integrados", "DIP-8", ["tl072", "tl082", "ne5532", "4558", "jrc4558"], "Operacional doble para audio. Usa fuente partida (+ y −).", DUAL)
comp("LM393 (comparador doble)", "Integrados", "DIP-8", ["lm393", "393"], "Dos comparadores. La salida necesita resistencia a +VCC.", DUAL)
comp("LM311 (comparador)", "Integrados", "DIP-8", ["lm311", "311"], "Comparador rápido.", ["GND", "IN +", "IN −", "V −", "Balance", "Balance/Strobe", "OUT", "V +"])
comp("LM386 (amplificador de audio)", "Integrados", "DIP-8", ["lm386", "386"], "Amplificador para parlante chico, funciona con 9 V.", ["GAIN", "IN −", "IN +", "GND", "OUT (salida)", "VS (+)", "BYPASS", "GAIN"])
comp("LM324 (operacional cuádruple)", "Integrados", "DIP-14", ["lm324", "324", "tl074", "tl084"], "Cuatro operacionales en un chip.", ["OUT 1", "IN 1 −", "IN 1 +", "VCC", "IN 2 +", "IN 2 −", "OUT 2", "OUT 3", "IN 3 −", "IN 3 +", "GND", "IN 4 +", "IN 4 −", "OUT 4"])
comp("LM339 (comparador cuádruple)", "Integrados", "DIP-14", ["lm339", "339"], "Cuatro comparadores.", ["OUT 2", "OUT 1", "VCC", "IN 1 −", "IN 1 +", "IN 2 −", "IN 2 +", "IN 3 −", "IN 3 +", "IN 4 −", "IN 4 +", "GND", "OUT 4", "OUT 3"])
comp("ICL7660 (inversor de tensión)", "Integrados", "DIP-8", ["icl7660", "7660"], "Saca −5 V a partir de +5 V.", ["Sin uso", "CAP +", "GND", "CAP −", "VOUT (−)", "LV", "OSC", "V +"])
G4 = ["1A", "1B", "1Y (salida)", "2A", "2B", "2Y (salida)", "GND", "3Y (salida)", "3A", "3B", "4Y (salida)", "4A", "4B", "VCC (+5 V)"]
HEX = ["1A", "1Y (salida)", "2A", "2Y (salida)", "3A", "3Y (salida)", "GND", "4Y (salida)", "4A", "5Y (salida)", "5A", "6Y (salida)", "6A", "VCC (+5 V)"]
comp("7400 (4 compuertas NAND)", "Integrados", "DIP-14", ["7400", "74ls00", "74hc00"], "Lógica TTL 5 V.", G4)
comp("7402 (4 compuertas NOR)", "Integrados", "DIP-14", ["7402", "74ls02", "74hc02"], "Ojo: las salidas están primero, distinto al 7400.", ["1Y (salida)", "1A", "1B", "2Y (salida)", "2A", "2B", "GND", "3A", "3B", "3Y (salida)", "4A", "4B", "4Y (salida)", "VCC (+5 V)"])
comp("7404 (6 inversores)", "Integrados", "DIP-14", ["7404", "74ls04", "74hc04"], "Seis compuertas NOT.", HEX)
comp("74HC14 (6 inversores Schmitt)", "Integrados", "DIP-14", ["74hc14", "7414", "74ls14"], "Inversores que limpian señales con ruido, ideal para pulsadores.", HEX)
comp("7408 (4 compuertas AND)", "Integrados", "DIP-14", ["7408", "74ls08", "74hc08"], "Lógica TTL 5 V.", G4)
comp("7432 (4 compuertas OR)", "Integrados", "DIP-14", ["7432", "74ls32", "74hc32"], "Lógica TTL 5 V.", G4)
comp("7486 (4 compuertas XOR)", "Integrados", "DIP-14", ["7486", "74ls86", "74hc86"], "Lógica TTL 5 V.", G4)
comp("74LS47 (decodificador a 7 segmentos)", "Integrados", "DIP-16", ["7447", "74ls47", "7448"], "Convierte un número binario en el display (ánodo común).", ["B", "C", "LT", "BI/RBO", "RBI", "D", "A", "GND", "e", "d", "c", "b", "a", "g", "f", "VCC"])
comp("74LS138 (decodificador 3 a 8)", "Integrados", "DIP-16", ["74ls138", "74hc138", "74138"], "Activa una de 8 salidas según 3 entradas.", ["A", "B", "C", "G2A", "G2B", "G1", "Y7", "GND", "Y6", "Y5", "Y4", "Y3", "Y2", "Y1", "Y0", "VCC"])
comp("74HC595 (registro de desplazamiento)", "Integrados", "DIP-16", ["74hc595", "595", "74595"], "Maneja 8 salidas con solo 3 pines del microcontrolador.", ["QB", "QC", "QD", "QE", "QF", "QG", "QH", "GND", "QH' (cascada)", "SRCLR (borrar)", "SRCLK (reloj)", "RCLK (latch)", "OE (habilitar)", "SER (datos)", "QA", "VCC"])
comp("74HC165 (entrada paralelo a serie)", "Integrados", "DIP-16", ["74hc165", "165"], "Lee 8 botones con 3 pines.", ["SH/LD", "CLK", "E", "F", "G", "H", "QH'", "GND", "QH", "SER", "A", "B", "C", "D", "CLK INH", "VCC"])
comp("74HC164 (registro serie a paralelo)", "Integrados", "DIP-14", ["74hc164", "164"], "Registro de 8 bits sin latch.", ["A (datos)", "B (datos)", "QA", "QB", "QC", "QD", "GND", "CLK", "CLR", "QE", "QF", "QG", "QH", "VCC"])
CM4 = ["A", "B", "J (salida)", "K (salida)", "C", "D", "VSS (GND)", "E", "F", "L (salida)", "M (salida)", "G", "H", "VDD (+)"]
CMH = ["A", "G (salida)", "B", "H (salida)", "C", "I (salida)", "VSS (GND)", "J (salida)", "D", "K (salida)", "E", "L (salida)", "F", "VDD (+)"]
comp("CD4011 (4 NAND CMOS)", "Integrados", "DIP-14", ["cd4011", "4011"], "Lógica CMOS de 3 a 15 V.", CM4)
comp("CD4093 (4 NAND Schmitt)", "Integrados", "DIP-14", ["cd4093", "4093"], "NAND con Schmitt: sirve para osciladores simples.", CM4)
comp("CD4001 (4 NOR CMOS)", "Integrados", "DIP-14", ["cd4001", "4001"], "Lógica CMOS de 3 a 15 V.", CM4)
comp("CD4081 (4 AND CMOS)", "Integrados", "DIP-14", ["cd4081", "4081"], "Lógica CMOS de 3 a 15 V.", CM4)
comp("CD4071 (4 OR CMOS)", "Integrados", "DIP-14", ["cd4071", "4071"], "Lógica CMOS de 3 a 15 V.", CM4)
comp("CD4070 (4 XOR CMOS)", "Integrados", "DIP-14", ["cd4070", "4070"], "Lógica CMOS de 3 a 15 V.", CM4)
comp("CD4069 (6 inversores CMOS)", "Integrados", "DIP-14", ["cd4069", "4069", "cd40106", "40106"], "Seis compuertas NOT (40106 con Schmitt).", CMH)
comp("CD4013 (doble flip-flop D)", "Integrados", "DIP-14", ["cd4013", "4013"], "Dos flip-flops: divide frecuencias y hace interruptores de un toque.", ["Q1", "Q1 negado", "CLK 1", "RESET 1", "DATA 1", "SET 1", "VSS (GND)", "SET 2", "DATA 2", "RESET 2", "CLK 2", "Q2 negado", "Q2", "VDD (+)"])
comp("CD4066 (4 llaves analógicas)", "Integrados", "DIP-14", ["cd4066", "4066"], "Cuatro interruptores controlados por señal.", ["Llave A", "Llave A", "Llave B", "Llave B", "Control B", "Control C", "VSS (GND)", "Llave C", "Llave C", "Llave D", "Llave D", "Control D", "Control A", "VDD (+)"])
comp("CD4017 (contador de décadas)", "Integrados", "DIP-16", ["cd4017", "4017"], "Con un 555 arma el clásico juego de luces.", ["Q5", "Q1", "Q0", "Q2", "Q6", "Q7", "Q3", "VSS (GND)", "Q8", "Q4", "Q9", "CO (acarreo)", "CE (habilitar)", "CLK (reloj)", "RESET", "VDD (+)"])
comp("CD4511 (decodificador 7 segmentos)", "Integrados", "DIP-16", ["cd4511", "4511"], "Convierte BCD a display de cátodo común.", ["B", "C", "LT", "BL", "LE", "D", "A", "VSS (GND)", "e", "d", "c", "b", "a", "g", "f", "VDD (+)"])
comp("CD4060 (contador con oscilador)", "Integrados", "DIP-16", ["cd4060", "4060"], "Oscilador y divisor en uno, para temporizadores largos.", ["Q12", "Q13", "Q14", "Q6", "Q5", "Q7", "Q4", "VSS (GND)", "CTC", "RTC", "RS", "RESET", "Q9", "Q8", "Q10", "VDD (+)"])
comp("CD4040 (contador binario)", "Integrados", "DIP-16", ["cd4040", "4040", "cd4020", "4020"], "Contador binario de 12 etapas.")
comp("CD4051 (multiplexor 8 canales)", "Integrados", "DIP-16", ["cd4051", "4051"], "Elige uno de 8 canales analógicos.")
comp("L293D (driver de motores)", "Integrados", "DIP-16", ["l293d", "l293", "sn754410"], "Maneja dos motores de corriente continua en ambos sentidos.", ["EN 1-2", "IN 1", "OUT 1", "GND", "GND", "OUT 2", "IN 2", "VS (motores)", "EN 3-4", "IN 3", "OUT 3", "GND", "GND", "OUT 4", "IN 4", "VSS (+5 V lógica)"])
comp("ULN2003 (driver darlington)", "Integrados", "DIP-16", ["uln2003", "uln2004"], "Siete salidas para relés y motor paso a paso 28BYJ-48.", ["IN 1", "IN 2", "IN 3", "IN 4", "IN 5", "IN 6", "IN 7", "GND", "COM (+ de la carga)", "OUT 7", "OUT 6", "OUT 5", "OUT 4", "OUT 3", "OUT 2", "OUT 1"])
comp("ULN2803 (driver 8 canales)", "Integrados", "DIP-18", ["uln2803", "uln2804"], "Como el ULN2003 pero con 8 salidas.")
comp("MAX232 (conversor RS-232)", "Integrados", "DIP-16", ["max232", "232"], "Comunica un microcontrolador con un puerto serie de PC. Lleva 4 capacitores de 1 µF.", ["C1 +", "V +", "C1 −", "C2 +", "C2 −", "V −", "T2 OUT", "R2 IN", "R2 OUT", "T2 IN", "T1 IN", "R1 OUT", "R1 IN", "T1 OUT", "GND", "VCC"])
comp("DS1307 (reloj de tiempo real)", "Integrados", "DIP-8", ["ds1307", "1307", "rtc"], "Lleva cristal de 32,768 kHz y pila CR2032.", ["X1 (cristal)", "X2 (cristal)", "VBAT (pila)", "GND", "SDA", "SCL", "SQW (salida)", "VCC"])
comp("Memoria EEPROM 24C02", "Integrados", "DIP-8", ["24c02", "24c04", "24c08", "24c16", "24lc256", "24c256", "eeprom"], "Guarda datos aunque se corte la luz. Se comunica por I2C.", ["A0", "A1", "A2", "GND", "SDA", "SCL", "WP (protección)", "VCC"])
comp("MAX485 (RS-485)", "Integrados", "DIP-8", ["max485", "485", "sn75176"], "Comunicación a larga distancia por dos cables.", ["RO", "RE", "DE", "DI", "GND", "A", "B", "VCC"])

# Microcontroladores
M328 = ["PC6 · RESET", "PD0 · D0 (RX)", "PD1 · D1 (TX)", "PD2 · D2", "PD3 · D3", "PD4 · D4", "VCC", "GND", "PB6 · cristal", "PB7 · cristal", "PD5 · D5", "PD6 · D6", "PD7 · D7", "PB0 · D8", "PB1 · D9", "PB2 · D10", "PB3 · D11 (MOSI)", "PB4 · D12 (MISO)", "PB5 · D13 (SCK)", "AVCC", "AREF", "GND", "PC0 · A0", "PC1 · A1", "PC2 · A2", "PC3 · A3", "PC4 · A4 (SDA)", "PC5 · A5 (SCL)"]
comp("ATmega328P (Arduino Uno)", "Microcontroladores", "DIP-28", ["atmega328", "atmega328p", "328p", "atmega8", "atmega168", "atmega"], "El cerebro del Arduino Uno. Lleva cristal de 16 MHz con dos capacitores de 22 pF.", M328)
comp("ATtiny85", "Microcontroladores", "DIP-8", ["attiny85", "attiny45", "attiny13", "attiny"], "Microcontrolador chiquito de 8 patas, se programa con Arduino.", ["PB5 · RESET", "PB3", "PB4", "GND", "PB0", "PB1", "PB2", "VCC"])
P628 = ["RA2", "RA3", "RA4", "RA5 · MCLR", "VSS (GND)", "RB0 · INT", "RB1 · RX", "RB2 · TX", "RB3", "RB4", "RB5", "RB6", "RB7", "VDD (+5 V)", "RA6 · OSC2", "RA7 · OSC1", "RA0", "RA1"]
comp("PIC16F628A", "Microcontroladores", "DIP-18", ["pic16f628", "16f628", "pic16f628a", "pic16f648"], "Microcontrolador muy usado en escuelas técnicas. Tiene oscilador interno.", P628)
comp("PIC16F84A", "Microcontroladores", "DIP-18", ["pic16f84", "16f84", "pic16f84a"], "El PIC clásico. Necesita cristal externo.", ["RA2", "RA3", "RA4 · T0CKI", "MCLR", "VSS (GND)", "RB0 · INT", "RB1", "RB2", "RB3", "RB4", "RB5", "RB6", "RB7", "VDD (+5 V)", "OSC2", "OSC1", "RA0", "RA1"])
comp("PIC12F675", "Microcontroladores", "DIP-8", ["pic12f675", "12f675", "pic12f629", "pic12f683"], "PIC de 8 patas.", ["VDD (+)", "GP5", "GP4", "GP3 · MCLR", "GP2", "GP1", "GP0", "VSS (GND)"])
comp("PIC16F876A", "Microcontroladores", "DIP-28", ["pic16f876", "16f876", "pic16f886"], "PIC de 28 patas en cuerpo angosto.")
comp("PIC16F877A", "Microcontroladores", "DIP-40W", ["pic16f877", "16f877", "pic16f877a", "pic16f887", "18f4550", "pic18f4550"], "PIC de 40 patas. Cuerpo ancho: filas a 15,24 mm.")
comp("ATmega16 / ATmega32", "Microcontroladores", "DIP-40W", ["atmega16", "atmega32", "atmega1284"], "AVR de 40 patas en cuerpo ancho.")
comp("AT89S52 (8051)", "Microcontroladores", "DIP-40W", ["at89s52", "at89s51", "89c51", "8051"], "El clásico 8051 de 40 patas.")
comp("Arduino Nano", "Microcontroladores", "NANO", ["arduinonano", "nano"], "Módulo completo sobre tiras de pines. Filas separadas 15,24 mm.")

# Electromecánicos y conectores
comp("Relé Songle SRD (5 / 12 V)", "Electromecánicos y conectores", "SRD", ["rele", "relay", "srd", "songle", "srd05vdc", "rele5v", "rele12v"], "Relé de 10 A. Lleva un diodo 1N4007 en paralelo con la bobina.", ["COM (común)", "Bobina", "NC / NO", "NO / NC", "Bobina"])
comp("Pulsador táctil 6×6", "Electromecánicos y conectores", "PUL6", ["pulsador", "boton", "tactil", "switch", "tact"], "Las patas 1-2 y 3-4 ya vienen unidas por dentro.")
comp("Cristal HC-49", "Electromecánicos y conectores", "HC49", ["cristal", "crystal", "16mhz", "8mhz", "4mhz", "20mhz", "xtal", "32768", "hc49"], "Da el ritmo exacto al microcontrolador. Va con dos capacitores de 22 pF a GND.")
comp("Buzzer 12 mm", "Electromecánicos y conectores", "BUZZER", ["buzzer", "zumbador", "chicharra"], "El activo suena solo con tensión; el pasivo necesita una señal. El pad cuadrado es el +.", ["+ (positivo)", "− (negativo)"])
comp("Jack de alimentación DC", "Electromecánicos y conectores", "JACK", ["jack", "jackdc", "plug", "conectordealimentacion", "dc005", "fichadc"], "Para conectar una fuente de pared con ficha 5,5 × 2,1 mm.", ["Centro (+)", "Manguito (−)", "Contacto de detección"])
comp("Bornera 2 vías", "Electromecánicos y conectores", "BORN-2", ["bornera", "borne", "terminal", "bornera2", "kf301"], "Para atornillar cables de alimentación o motores.")
comp("Bornera 3 vías", "Electromecánicos y conectores", "BORN-3", ["bornera3", "borne3", "bornerade3"], "Para atornillar tres cables.")
comp("Tira de pines", "Electromecánicos y conectores", "SIP-n", ["tiradepines", "pinheader", "header", "espadin", "pines", "tirahembra", "tiramacho"], "Macho o hembra, paso 2,54 mm. Se corta del largo que necesites.", variable=True)
comp("Zócalo DIP", "Electromecánicos y conectores", "DIP-8", ["zocalo", "socket"], "Usá la misma huella que el integrado que va encima.")

# ---------------- amplificadores de audio ----------------
def stagger(name, n, pitch, offset, body, w=1.8, h=2.6, drill=1.0, nota=None):
    """Patas en zigzag: impares en la fila de adelante (y=0), pares atrás, hacia el cuerpo (y=-offset)."""
    pads = [pad(i + 1, i * pitch, 0 if i % 2 == 0 else -offset, max(w, h), drill, sq=(i == 0), w=w, h=h) for i in range(n)]
    x0, y0, x1, y1 = body
    fp = {"pkg": name, "pads": pads, "silk": [{"t": "rect", "x": x0, "y": y0, "w": R(x1 - x0), "h": R(y1 - y0)}],
          "dims": [[1, 3, mm(R(2 * pitch))]], "row": offset, "paso": pitch,
          "nota": nota or "Las patas van en zigzag: las impares adelante y las pares atrás, del lado de la aleta."}
    return fp

add("PENTA", stagger("Pentawatt (TO-220-5 zigzag)", 5, 1.7, 3.7, (-1.6, -8.2, 8.4, -3.8), w=2.2))
add("MW11", stagger("Multiwatt-11", 11, 1.7, 5.08, (-1.6, -9.58, 18.6, -4.58), w=2.2))
add("MW15", stagger("Multiwatt-15", 15, 1.27, 5.08, (-1.21, -9.58, 18.99, -4.58),
     nota="Las patas van en zigzag cada 1,27 mm. Entre pads de la misma fila quedan 0,7 mm: imprimí con buen tóner y revisá con lupa antes de atacar con percloruro."))
add("SIP-9A", (lambda f: (f.update(pkg="SIL-9 (en línea)"), f)[1])(sip(9)))
add("TO220-11", stagger("TO-220-11 (LM3886)", 11, 1.7, 5.08, (-1.6, -9.58, 18.6, -4.58), w=2.2,
     nota="Medidas tomadas del Multiwatt-11. Antes de perforar, apoyá el integrado sobre la hoja impresa y confirmá la separación entre filas."))

A = "Amplificadores de audio"
VERIF = " El orden de patas no está cargado todavía: miralo en la hoja de datos antes de rutear."
P2030 = ["IN + (entrada)", "IN − (realimentación)", "−VS (o GND con fuente simple)", "OUT (salida)", "+VS"]
comp("TDA2030A (18 W)", A, "PENTA", ["tda2030", "tda2030a", "tda2040", "tda2030v"], "Amplificador mono clásico. Funciona con fuente simple o partida. Necesita disipador.", P2030)
comp("TDA2050 (32 W)", A, "PENTA", ["tda2050", "tda2050v"], "Versión más potente del TDA2030, misma huella y mismas patas. Disipador grande.", P2030)
comp("LM1875 (20 W)", A, "PENTA", ["lm1875", "lm1875t"], "Amplificador de muy buena calidad, mismo orden de patas que el TDA2030.", P2030)
comp("TDA2003 (10 W)", A, "PENTA", ["tda2003", "tda2002", "tda2003v"], "Amplificador para 12 V, ideal para auto o fuente de 12 V.", ["IN + (entrada)", "IN − (realimentación)", "GND", "OUT (salida)", "+VS"])
comp("TDA7294 (100 W)", A, "MW15", ["tda7294", "tda7294v", "tda7295", "tda7296"], "Amplificador potente con fuente partida (hasta ±40 V). Tiene Mute y Stand-by. La aleta está conectada a −VS: aislá el disipador.",
     ["Stand-by GND", "IN − (inversora)", "IN + (no inversora)", "SVR (rechazo de ripple)", "Sin uso", "Bootstrap", "+VS (señal)", "−VS (señal)", "Stand-by", "Mute", "Sin uso", "Sin uso", "+VS (potencia)", "OUT (salida)", "−VS (potencia)"])
comp("TDA7293 (100 W)", A, "MW15", ["tda7293", "tda7293v"], "Hermano del TDA7294, permite poner varios en paralelo. Casi el mismo orden de patas: cambian las 11 y 12." + VERIF)
comp("TDA7375 (4 × 35 W)", A, "MW15", ["tda7375", "tda7375v", "tda7375av"], "Amplificador de auto de 4 canales o 2 en puente, para 12 V." + VERIF)
comp("TDA7377 (4 × 30 W)", A, "MW15", ["tda7377", "tda7377v"], "Amplificador de auto de 4 canales para 12 V." + VERIF)
comp("TDA7297 (2 × 15 W)", A, "MW15", ["tda7297", "tda7266", "tda7266d"], "Estéreo en puente para 12 V, muy usado en parlantes de PC." + VERIF)
comp("LM4766 (2 × 40 W)", A, "MW15", ["lm4766", "lm4766t"], "Dos amplificadores tipo LM3886 en un solo integrado." + VERIF)
comp("TDA2005 (2 × 10 W)", A, "MW11", ["tda2005", "tda2005r"], "Amplificador de auto estéreo o en puente, para 12 V." + VERIF)
comp("TDA2009 (2 × 10 W)", A, "MW11", ["tda2009", "tda2009a"], "Estéreo para 12 a 24 V." + VERIF)
comp("TDA7265 (2 × 25 W)", A, "MW11", ["tda7265", "tda7264", "tda7391", "tda7240"], "Estéreo con fuente partida." + VERIF)
comp("LM3886 (68 W)", A, "TO220-11", ["lm3886", "lm3886t", "lm3886tf", "gainclone"], "El famoso 'gainclone'. Sonido excelente con fuente partida. La versión TF tiene la aleta aislada.",
     ["V +", "Sin uso", "OUT (salida)", "V −", "V +", "Sin uso", "GND", "MUTE", "IN − (inversora)", "IN + (no inversora)", "Sin uso"])
comp("TDA2822M (2 × 1 W)", A, "DIP-8", ["tda2822", "tda2822m", "ka2209", "ka22065"], "Amplificador estéreo chico para auriculares o parlantes de 4–8 Ω, desde 3 V.",
     ["OUT 1", "VCC", "OUT 2", "GND", "IN 2 −", "IN 2 +", "IN 1 +", "IN 1 −"])
comp("TDA7052 (1 W)", A, "DIP-8", ["tda7052"], "Amplificador mono en puente, sin capacitor de salida." + VERIF)
comp("TBA820M (2 W)", A, "DIP-8", ["tba820", "tba820m"], "Amplificador chico clásico para radios y timbres." + VERIF)
comp("LM380 (2,5 W)", A, "DIP-8", ["lm380", "lm380n8"], "Amplificador de potencia chico. Ojo: existe en DIP-8 y DIP-14." + VERIF)
comp("TDA7056 / TDA1517 (SIL-9)", A, "SIP-9A", ["tda7056", "tda7056b", "tda1517", "tda2616", "tda1516"], "Amplificadores en encapsulado de una fila de 9 patas. Medí el paso de tus patas antes de perforar." + VERIF)
comp("PT2399 (eco / delay)", A, "DIP-16", ["pt2399", "2399"], "Integrado de eco para pedales de guitarra y efectos." + VERIF)

# control de separación mínima entre pads (0,6 mm para planchado)
def gap(a, b):
    import math
    ax, ay = (a.get("w") or a["d"]) / 2, (a.get("h") or a["d"]) / 2
    bx, by = (b.get("w") or b["d"]) / 2, (b.get("h") or b["d"]) / 2
    dx, dy = abs(a["x"] - b["x"]) - ax - bx, abs(a["y"] - b["y"]) - ay - by
    return max(dx, dy) if (dx < 0 or dy < 0) else math.hypot(dx, dy)
bad = []
for k, f in ENC.items():
    ps = f["pads"]
    m = min((gap(a, b) for i, a in enumerate(ps) for b in ps[i+1:]), default=9)
    if m < 0.6: bad.append((k, round(m, 2)))
print("Separación menor a 0,6 mm:", bad or "ninguna")

lib = {"version": 3, "reglas": {"pad_mm": 2.0, "mecha_mm": 0.8, "pista_min_mm": 0.8, "separacion_min_mm": 0.6, "grilla_mm": 2.54},
       "encapsulados": ENC, "componentes": C}
for c in C:
    assert c["enc"] in ENC or c["enc"] == "SIP-n", c
    if "pines" in c and c["enc"] in ENC:
        assert len(c["pines"]) == len(ENC[c["enc"]]["pads"]), (c["nombre"], len(c["pines"]), len(ENC[c["enc"]]["pads"]))
s = json.dumps(lib, ensure_ascii=False, separators=(",", ":"))
import os
here = os.path.dirname(os.path.abspath(__file__))
open(os.path.join(here, "componentes.json"), "w", encoding="utf-8").write(s)
open(os.path.join(here, "componentes.js"), "w", encoding="utf-8").write("window.COMPONENTES=" + s + ";\n")
print(len(C), "componentes,", len(ENC), "encapsulados,", len(s) // 1024, "KB")
