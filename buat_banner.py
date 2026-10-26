import base64
import random

# ===================== PENGATURAN =====================
GAMBAR      = "baner.png"
OUTPUT      = "banner-teks.svg"
W, H        = 1280, 460            # ikut rasio foto. Untuk 4:1 ganti H = 320
POSISI      = "xMidYMid slice"     # "xMidYMin slice" = fokus bagian atas foto

TEXT_X      = 770                  # awal blok teks. Naikkan jika kena mawar
MARGIN_R    = 40                   # jarak dari tepi kanan

TAG         = "// HELLO, WORLD"
NAMA        = "M. Awaudin Ilhaqqi"
BARIS       = [
    "Hi there! I'm Awaudin",
    "Frontend Developer | Software Engineer",
    "Laravel | Flutter | PHP | Python",
    "Always experimenting with new tech",
]
TECH        = ["Laravel", "Flutter", "PHP", "Python", "React"]
STATUS      = "Open to collaborate"   # kosongkan "" untuk menghilangkan

WARNA_TEKS  = "#ffffff"            # warna tulisan typing
WARNA_AKSEN = "#ff3b5c"            # garis, kursor, chip, ujung gradasi nama
WARNA_GLOW  = "#ff1744"            # cahaya di sekitar mawar

DURASI      = 4                    # detik per baris typing
UKURAN_NAMA = 40
UKURAN_TEKS = 22                   # ukuran maksimum, otomatis mengecil jika kepanjangan
PARTIKEL    = 12                   # jumlah titik melayang (0 untuk mematikan)
# =======================================================

FONT_MONO = "'Fira Code','JetBrains Mono',Consolas,'Courier New',monospace"
FONT_SANS = "'Segoe UI',Arial,sans-serif"

mime = "image/png" if GAMBAR.lower().endswith("png") else "image/jpeg"
with open(GAMBAR, "rb") as f:
    b64 = base64.b64encode(f.read()).decode()

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

# ---------- ukuran & posisi ----------
AVAIL   = W - MARGIN_R - TEXT_X
PROMPT  = 26
TX      = TEXT_X + PROMPT
maxlen  = max(len(t) for t in BARIS)
ukuran  = int(min(UKURAN_TEKS, (AVAIL - PROMPT) / (maxlen * 0.6)))
cw      = ukuran * 0.6
uk_nama = int(min(UKURAN_NAMA, AVAIL / (len(NAMA) * 0.62)))

Y_TAG   = int(H * 0.2)
Y_NAMA  = Y_TAG + 14 + uk_nama
Y_GARIS = Y_NAMA + 18
Y_TEKS  = Y_GARIS + 34 + ukuran

def masuk(isi, dur, dx=30):
    return (f'<g><animate attributeName="opacity" from="0" to="1" dur="{dur}s" begin="0s" fill="freeze"/>'
            f'<animateTransform attributeName="transform" type="translate" from="{dx} 0" to="0 0" '
            f'dur="{dur}s" begin="0s" fill="freeze"/>{isi}</g>')

# ---------- chip teknologi ----------
chips, cx, cy, CH, FS = [], TEXT_X, Y_TEKS + 34, 28, 13
for t in TECH:
    wch = int(len(t) * FS * 0.6 + 26)
    if cx + wch > W - MARGIN_R:
        cx, cy = TEXT_X, cy + CH + 8
    chips.append(
        f'<rect x="{cx}" y="{cy}" width="{wch}" height="{CH}" rx="14" fill="#000" fill-opacity="0.35" '
        f'stroke="{WARNA_AKSEN}" stroke-opacity="0.75"/>'
        f'<text x="{cx + wch / 2}" y="{cy + 18}" font-size="{FS}" fill="#ffffff" text-anchor="middle" '
        f'font-family="{FONT_MONO}">{esc(t)}</text>'
    )
    cx += wch + 8
chips_bottom = cy + CH
chips_svg = masuk("".join(chips), 1.4)

# ---------- status ----------
Y_STATUS = chips_bottom + 36
if STATUS:
    status_inner = (
        f'<circle cx="{TEXT_X + 5}" cy="{Y_STATUS - 5}" r="4.5" fill="#3ddc84">'
        f'<animate attributeName="opacity" values="1;0.3;1" dur="1.6s" repeatCount="indefinite"/></circle>'
        f'<text x="{TEXT_X + 18}" y="{Y_STATUS}" font-size="13" fill="#d0d0d0" '
        f'font-family="{FONT_SANS}">{esc(STATUS)}</text>'
    )
    status_svg = masuk(status_inner, 1.6)
    bottom = Y_STATUS + 8
else:
    status_svg, bottom = "", chips_bottom

BAR_TOP = Y_TAG - 16
BAR_H   = bottom - BAR_TOP

# ---------- typing + kursor ----------
n, total = len(BARIS), len(BARIS) * DURASI
d = 1 / n
clips, texts = [], []
cur_t, cur_v = [], []
for i, teks in enumerate(BARIS):
    s, e = i * d, (i + 1) * d
    w = len(teks) * cw
    pts = [(0, 0)]
    if s > 0:
        pts.append((s, 0))
    pts += [(s + 0.45 * d, w), (e - 0.001, w), (e, 0)]
    if e < 1:
        pts.append((1, 0))
    kt = ";".join(f"{t:.4f}" for t, _ in pts)
    vl = ";".join(f"{v:.1f}" for _, v in pts)
    clips.append(
        f'<clipPath id="c{i}"><rect x="{TX}" y="{Y_TEKS - ukuran - 2}" height="{int(ukuran * 1.5)}" width="0">'
        f'<animate attributeName="width" dur="{total}s" repeatCount="indefinite" keyTimes="{kt}" values="{vl}"/>'
        f'</rect></clipPath>'
    )
    texts.append(
        f'<text x="{TX}" y="{Y_TEKS}" font-size="{ukuran}" fill="{WARNA_TEKS}" font-weight="600" '
        f'font-family="{FONT_MONO}" textLength="{w:.1f}" lengthAdjust="spacing" '
        f'clip-path="url(#c{i})" filter="url(#glow)">{esc(teks)}</text>'
    )
    cur_t += [s, s + 0.45 * d, e - 0.001]
    cur_v += [TX, TX + w, TX + w]
cur_t.append(1)
cur_v.append(TX)
cur_kt = ";".join(f"{t:.4f}" for t in cur_t)
cur_vl = ";".join(f"{v:.1f}" for v in cur_v)
cursor_svg = (
    f'<rect x="{TX}" y="{Y_TEKS - ukuran + 1}" width="3" height="{int(ukuran * 1.1)}" fill="{WARNA_AKSEN}">'
    f'<animate attributeName="x" dur="{total}s" repeatCount="indefinite" keyTimes="{cur_kt}" values="{cur_vl}"/>'
    f'<animate attributeName="opacity" values="1;0;1" dur="0.9s" calcMode="discrete" repeatCount="indefinite"/>'
    f'</rect>'
)
prompt_svg = (
    f'<text x="{TEXT_X}" y="{Y_TEKS}" font-size="{ukuran}" fill="{WARNA_AKSEN}" font-weight="700" '
    f'font-family="{FONT_MONO}">&gt;</text>'
)

# ---------- partikel ----------
random.seed(7)
parts = []
for _ in range(PARTIKEL):
    x = random.randint(int(W * 0.5), W - 20)
    y = random.randint(int(H * 0.3), H - 20)
    r = round(random.uniform(1.2, 2.8), 1)
    dur = random.randint(5, 9)
    delay = round(random.uniform(0, 4), 1)
    parts.append(
        f'<circle cx="{x}" cy="{y}" r="{r}" fill="{WARNA_AKSEN}" opacity="0">'
        f'<animate attributeName="cy" values="{y};{y - 70}" dur="{dur}s" begin="{delay}s" repeatCount="indefinite"/>'
        f'<animate attributeName="opacity" values="0;0.7;0" dur="{dur}s" begin="{delay}s" repeatCount="indefinite"/>'
        f'</circle>'
    )

# ---------- elemen statis ----------
tag_svg = masuk(
    f'<text x="{TEXT_X}" y="{Y_TAG}" font-size="13" letter-spacing="3" fill="{WARNA_AKSEN}" '
    f'font-family="{FONT_MONO}">{esc(TAG)}</text>', 0.8)
nama_svg = masuk(
    f'<text x="{TEXT_X}" y="{Y_NAMA}" font-size="{uk_nama}" font-weight="700" fill="url(#gn)" '
    f'font-family="{FONT_SANS}" filter="url(#glow)">{esc(NAMA)}</text>'
    f'<rect x="{TEXT_X}" y="{Y_GARIS}" width="160" height="3" rx="1.5" fill="{WARNA_AKSEN}"/>', 1.0)
bar_svg = (
    f'<rect x="{TEXT_X - 22}" y="{BAR_TOP}" width="3" height="0" rx="1.5" fill="{WARNA_AKSEN}">'
    f'<animate attributeName="height" from="0" to="{BAR_H}" dur="1.2s" begin="0s" fill="freeze"/></rect>'
)
bracket_svg = (
    f'<path d="M {W - 64} 28 H {W - 28} V 64" stroke="{WARNA_AKSEN}" stroke-width="2" fill="none" opacity="0.8"/>'
    f'<path d="M 28 {H - 64} V {H - 28} H 64" stroke="{WARNA_AKSEN}" stroke-width="2" fill="none" opacity="0.8"/>'
)

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <defs>
    <linearGradient id="ovh" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0.42" stop-color="#000" stop-opacity="0"/>
      <stop offset="0.62" stop-color="#000" stop-opacity="0.45"/>
      <stop offset="1" stop-color="#000" stop-opacity="0.7"/>
    </linearGradient>
    <linearGradient id="ovv" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#000" stop-opacity="0.35"/>
      <stop offset="0.25" stop-color="#000" stop-opacity="0"/>
      <stop offset="0.75" stop-color="#000" stop-opacity="0"/>
      <stop offset="1" stop-color="#000" stop-opacity="0.45"/>
    </linearGradient>
    <linearGradient id="gn" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#ffffff"/>
      <stop offset="1" stop-color="{WARNA_AKSEN}"/>
    </linearGradient>
    <linearGradient id="ln" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{WARNA_AKSEN}" stop-opacity="0"/>
      <stop offset="0.5" stop-color="{WARNA_AKSEN}" stop-opacity="0.9"/>
      <stop offset="1" stop-color="{WARNA_AKSEN}" stop-opacity="0"/>
    </linearGradient>
    <radialGradient id="gl">
      <stop offset="0" stop-color="{WARNA_GLOW}" stop-opacity="0.45"/>
      <stop offset="1" stop-color="{WARNA_GLOW}" stop-opacity="0"/>
    </radialGradient>
    <filter id="glow" x="-20%" y="-50%" width="140%" height="200%">
      <feGaussianBlur stdDeviation="2" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    {"".join(clips)}
  </defs>

  <image width="{W}" height="{H}" preserveAspectRatio="{POSISI}" xlink:href="data:{mime};base64,{b64}"/>
  <circle cx="{int(W * 0.52)}" cy="{int(H * 0.36)}" r="190" fill="url(#gl)">
    <animate attributeName="opacity" values="0.5;1;0.5" dur="4s" repeatCount="indefinite"/>
  </circle>
  <rect width="{W}" height="{H}" fill="url(#ovh)"/>
  <rect width="{W}" height="{H}" fill="url(#ovv)"/>
  {"".join(parts)}
  {bracket_svg}
  <rect x="0" y="{H - 3}" width="{W}" height="3" fill="url(#ln)"/>

  {bar_svg}
  {tag_svg}
  {nama_svg}
  {prompt_svg}
  {"".join(texts)}
  {cursor_svg}
  {chips_svg}
  {status_svg}
</svg>'''

with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write(svg)
print("Selesai ->", OUTPUT)