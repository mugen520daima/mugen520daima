# -*- coding: utf-8 -*-
"""GitHub Profile 图片素材美化脚本"""
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps
import os, random

BASE = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(BASE, "assets")

def load_font(px, bold=True):
    cands = []
    if bold:
        cands += [r"C:\Windows\Fonts\HarmonyOS_Sans_SC_Bold.ttf",
                  r"C:\Windows\Fonts\msyhbd.ttc", r"C:\Windows\Fonts\segoeuib.ttf"]
    cands += [r"C:\Windows\Fonts\HarmonyOS_Sans_SC_Regular.ttf",
              r"C:\Windows\Fonts\msyh.ttc", r"C:\Windows\Fonts\simhei.ttf"]
    for c in cands:
        try:
            return ImageFont.truetype(c, px)
        except Exception as e:
            print("font fail:", c, repr(e))
    return ImageFont.load_default(px)

def content_bbox(img):
    """内容边界：优先 alpha，其次从边缘洪水填充去黑底（保护角色暗色服装）"""
    if img.mode == "RGBA":
        alpha = img.getchannel("A")
        bbox = alpha.getbbox()
        if bbox and (bbox[2]-bbox[0]) > img.width*0.3:
            return img, bbox
    rgb = img.convert("RGB")
    w, h = rgb.size
    small = rgb.resize((w//4, h//4))
    mask = Image.new("L", small.size, 255)
    from collections import deque
    px = small.load()
    mk = mask.load()
    seed_pts = [(0,0),(small.width-1,0),(0,small.height-1),(small.width-1,small.height-1)]
    def is_bg(p):
        r,g,b = px[p]
        return r < 32 and g < 32 and b < 32
    seen = set()
    dq = deque()
    for p in seed_pts:
        if is_bg(p) and p not in seen:
            seen.add(p); dq.append(p)
    while dq:
        x, y = dq.popleft()
        mk[x, y] = 0
        for nx, ny in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
            if 0 <= nx < small.width and 0 <= ny < small.height and (nx,ny) not in seen and is_bg((nx,ny)):
                seen.add((nx,ny)); dq.append((nx,ny))
    mask = mask.resize((w, h), Image.BILINEAR)
    mask = mask.filter(ImageFilter.GaussianBlur(1.2))
    rgba = rgb.convert("RGBA")
    rgba.putalpha(mask)
    bbox = mask.getbbox()
    return rgba, bbox or (0, 0, w, h)

def rounded(img, radius):
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, img.width-1, img.height-1], radius=radius, fill=255)
    out = img.copy()
    out.putalpha(mask)
    return out

# ---------- 1. 千夏立绘处理 ----------
q = Image.open(os.path.join(A, "qiansha_raw.png"))
print("qiansha:", q.mode, q.size)
q, qb = content_bbox(q)
q = q.crop(qb)
q.thumbnail((420, 1000), Image.LANCZOS)
q.save(os.path.join(A, "qiansha.png"))
print("qiansha cropped:", q.size)

# ---------- 2. 木更头像处理 ----------
m = Image.open(os.path.join(A, "mugen_raw.png")).convert("RGB")
print("mugen:", m.mode, m.size)
# 裁中心偏上的方形区域（脸部）
s = m.size[0]
face = m.crop((int(s*0.10), int(s*0.06), int(s*0.90), int(s*0.86)))
face = ImageOps.fit(face, (360, 360), Image.LANCZOS)

# 圆形头像
size = 360
circle = Image.new("RGBA", (size+16, size+16), (0,0,0,0))
d = ImageDraw.Draw(circle)
d.ellipse([2, 2, size+13, size+13], fill=(244, 114, 182, 255))  # 粉色描边
mask = Image.new("L", (size, size), 0)
ImageDraw.Draw(mask).ellipse([0, 0, size-1, size-1], fill=255)
circle.paste(face.resize((size, size)), (8, 8), mask)
circle.save(os.path.join(A, "mugen_avatar.png"))

# 圆角方图（正文用）
sq = rounded(face.convert("RGBA"), 40)
sq.save(os.path.join(A, "mugen.png"))
print("mugen done")

# ---------- 3. Banner 合成 ----------
W, H = 1280, 420
banner = Image.new("RGB", (W, H))
# 对角渐变：深紫 -> GitHub 深空蓝 -> 底部微粉
top = (22, 12, 46); bot = (13, 17, 23)
for y in range(H):
    t = y / (H - 1)
    r = int(top[0]*(1-t) + bot[0]*t)
    gg = int(top[1]*(1-t) + bot[1]*t)
    b = int(top[2]*(1-t) + bot[2]*t)
    ImageDraw.Draw(banner).line([(0, y), (W, y)], fill=(r, gg, b))
banner = banner.convert("RGBA")

# 右下角粉色光晕
glow = Image.new("RGBA", (W, H), (0,0,0,0))
ImageDraw.Draw(glow).ellipse([W-560, H-320, W+160, H+260], fill=(236, 72, 153, 40))
glow = glow.filter(ImageFilter.GaussianBlur(90))
banner = Image.alpha_composite(banner, glow)

# 星点
draw = ImageDraw.Draw(banner)
random.seed(7)
for _ in range(90):
    x, y = random.randint(0, W-1), random.randint(0, H-1)
    rr = random.choice([1, 1, 1, 2])
    c = random.choice([(255,255,255), (244,114,182), (129,140,248)])
    a = random.randint(40, 140)
    draw.ellipse([x-rr, y-rr, x+rr, y+rr], fill=c+(a,))

# 左侧文字（带粉色霓虹光）
txt = Image.new("RGBA", (W, H), (0,0,0,0))
td = ImageDraw.Draw(txt)
f_big = load_font(66, True)
f_sub = load_font(26, True)
f_cn = load_font(24, False)
td.text((70, 96), "mugen520daima", font=f_big, fill=(255, 255, 255, 255))
td.text((72, 196), "AI Agent \u00b7 RAG \u00b7 Compiler \u00b7 Game QA", font=f_sub, fill=(148, 163, 184, 255))
td.text((72, 252), "\u767d\u5929\u5199\u4ee3\u7801\uff0c\u665a\u4e0a\u770b\u8d29", font=f_cn, fill=(244, 114, 182, 255))
td.rounded_rectangle([70, 300, 260, 306], radius=3, fill=(236, 72, 153, 255))
neon = txt.filter(ImageFilter.GaussianBlur(14))
layer = Image.new("RGBA", (W, H), (0,0,0,0))
ImageDraw.Draw(layer).rectangle([0, 0, W, H], fill=(236, 72, 153, 90))
neon = Image.composite(layer, Image.new("RGBA", (W, H), (0,0,0,0)), neon.getchannel("A"))
banner = Image.alpha_composite(banner, neon)
banner = Image.alpha_composite(banner, txt)

# 右侧千夏卡片
card_w, card_h = 300, 380
card = Image.new("RGBA", (card_w, card_h), (13, 17, 23, 230))
cd = ImageDraw.Draw(card)
cd.rounded_rectangle([0, 0, card_w-1, card_h-1], radius=24, outline=(244, 114, 182, 200), width=3)
qi = Image.open(os.path.join(A, "qiansha.png")).convert("RGBA")
qi.thumbnail((card_w-36, card_h-36), Image.LANCZOS)
card.alpha_composite(qi, ((card_w-qi.width)//2, (card_h-qi.height)//2))
banner.alpha_composite(card, (W-card_w-60, (H-card_h)//2))

banner.convert("RGB").save(os.path.join(A, "banner.png"), optimize=True)
print("banner done")

# ---------- 4. 文件体积检查 ----------
for f in ["banner.png", "qiansha.png", "mugen.png", "mugen_avatar.png"]:
    p = os.path.join(A, f)
    print(f, os.path.getsize(p)//1024, "KB")
