# -*- coding: utf-8 -*-
"""Μηχανή επικάλυψης κειμένου πάνω στο έντυπο Δ1 (4 σελίδες A4, η 4η περιστραμμένη).
Συντεταγμένες: x από αριστερά, top από πάνω (όπως pdfplumber), σε pt.
Για τη σελίδα 4: LX κατά μήκος της ανάγνωσης (= top του PDF), LY από την «πάνω» πλευρά
του οριζόντιου φύλλου (= 595.276 - x του PDF)."""
import re
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import Color

pdfmetrics.registerFont(TTFont('F', '/usr/share/fonts/truetype/crosextra/Carlito-Regular.ttf'))
pdfmetrics.registerFont(TTFont('FB', '/usr/share/fonts/truetype/crosextra/Carlito-Bold.ttf'))
PW, PH = 595.276, 841.89
INK = Color(0.0, 0.0, 0.45)          # σκούρο μπλε, ώστε να ξεχωρίζει από το τυπωμένο έντυπο
HL = Color(1.0, 0.93, 0.25)          # κίτρινη επισήμανση για κενά προς συμπλήρωση
PH_RE = re.compile(r'(\[[^\]]*\]|\{\{[^}]*\}\})')  # [..........] ή {{τιμή προς επιβεβαίωση}}


def _segments(text):
    """Χωρίζει ένα κείμενο σε τμήματα (κείμενο, είναι_επισημασμένο).
    Τα [..] τυπώνονται με τις αγκύλες, τα {{..}} χωρίς άγκιστρα, και τα δύο με κίτρινη επισήμανση."""
    out = []
    for part in PH_RE.split(text):
        if not part:
            continue
        if part.startswith('{{') and part.endswith('}}'):
            out.append((part[2:-2], True))
        else:
            out.append((part, bool(PH_RE.fullmatch(part))))
    return out


def plain(text):
    """Το κείμενο όπως θα τυπωθεί (χωρίς τα {{ }}), για μέτρηση πλάτους."""
    return re.sub(r'\{\{([^}]*)\}\}', r'\1', text)


def _wrap(text, font, size, width):
    # τα {{..}} δεν σπάνε σε γραμμές
    text = re.sub(r'\{\{([^}]*)\}\}', lambda m: '{{' + m.group(1).replace(' ', '\u00a0') + '}}', text)
    lines = []
    for para in text.split('\n'):
        words = para.split(' ')
        cur = ''
        for w in words:
            trial = (cur + ' ' + w) if cur else w
            if pdfmetrics.stringWidth(plain(trial), font, size) <= width:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                # λέξη μεγαλύτερη από το πλάτος: σπάσιμο ανά χαρακτήρα
                while pdfmetrics.stringWidth(w, font, size) > width and len(w) > 1:
                    k = len(w)
                    while k > 1 and pdfmetrics.stringWidth(w[:k], font, size) > width:
                        k -= 1
                    lines.append(w[:k])
                    w = w[k:]
                cur = w
        lines.append(cur)
    return lines


class Sheet:
    def __init__(self, path):
        self.c = canvas.Canvas(path, pagesize=(PW, PH))
        self.page = 1
        self.log = []

    def next_page(self):
        self.c.showPage()
        self.page += 1

    # ---------- χαμηλού επιπέδου σχεδίαση μιας γραμμής με επισήμανση κενών ----------
    def _draw_line(self, x, y, line, font, size, rotated=False):
        c = self.c
        cx = 0.0
        for seg, is_ph in _segments(line):
            w = pdfmetrics.stringWidth(seg, font, size)
            if is_ph:
                c.setFillColor(HL)
                c.rect(x + cx - 0.3, y - size * 0.22, w + 0.6, size * 1.02, stroke=0, fill=1)
            c.setFillColor(INK)
            c.setFont(font, size)
            c.drawString(x + cx, y, seg)
            cx += w

    # ---------- κείμενο σε κελί (όρθια σελίδα) ----------
    def cell(self, x0, x1, top, bottom, text, size=8.0, bold=False, align='left',
             valign='middle', min_size=3.6, pad=1.6, leading=1.12, tag=''):
        if not text:
            return
        font = 'FB' if bold else 'F'
        width = (x1 - x0) - 2 * pad
        height = (bottom - top) - 2 * pad * 0.6
        s = size
        while True:
            lines = _wrap(text, font, s, width)
            need = len(lines) * s * leading
            if need <= height or s <= min_size:
                break
            s = round(s - 0.2, 2)
        if need > height + 0.5:
            self.log.append(f'ΥΠΕΡΧΕΙΛΙΣΗ σελ.{self.page} {tag}: {text[:60]}')
        block = len(lines) * s * leading
        if valign == 'middle':
            y_top = top + ((bottom - top) - block) / 2
        elif valign == 'top':
            y_top = top + pad * 0.6
        else:
            y_top = bottom - pad * 0.6 - block
        for i, ln in enumerate(lines):
            lw = pdfmetrics.stringWidth(plain(ln), font, s)
            if align == 'center':
                lx = x0 + ((x1 - x0) - lw) / 2
            elif align == 'right':
                lx = x1 - pad - lw
            else:
                lx = x0 + pad
            base_top = y_top + i * s * leading + s * 0.82
            self._draw_line(lx, PH - base_top, ln, font, s)
        self.log.append(f'σελ.{self.page} {tag}: μέγεθος {s} γραμμές {len(lines)}')

    def text(self, x, base_top, text, size=8.0, bold=False):
        self._draw_line(x, PH - base_top, text, 'FB' if bold else 'F', size)

    def mark_x(self, x0, x1, top, bottom):
        c = self.c
        c.setStrokeColor(INK)
        c.setLineWidth(1.1)
        m = 1.6
        c.line(x0 + m, PH - (top + m), x1 - m, PH - (bottom - m))
        c.line(x0 + m, PH - (bottom - m), x1 - m, PH - (top + m))

    # ---------- κείμενο σε κελί της περιστραμμένης σελίδας 4 ----------
    def rcell(self, lx0, lx1, ly0, ly1, text, size=7.0, bold=False, align='left',
              valign='middle', min_size=3.4, pad=1.4, leading=1.12, tag=''):
        if not text:
            return
        font = 'FB' if bold else 'F'
        width = (lx1 - lx0) - 2 * pad
        height = (ly1 - ly0) - 2 * pad * 0.6
        s = size
        while True:
            lines = _wrap(text, font, s, width)
            need = len(lines) * s * leading
            if need <= height or s <= min_size:
                break
            s = round(s - 0.2, 2)
        if need > height + 0.5:
            self.log.append(f'ΥΠΕΡΧΕΙΛΙΣΗ σελ.4 {tag}: {text[:60]}')
        block = len(lines) * s * leading
        if valign == 'middle':
            y_top = ly0 + ((ly1 - ly0) - block) / 2
        else:
            y_top = ly0 + pad * 0.6
        c = self.c
        for i, ln in enumerate(lines):
            lw = pdfmetrics.stringWidth(plain(ln), font, s)
            if align == 'center':
                lx = lx0 + ((lx1 - lx0) - lw) / 2
            else:
                lx = lx0 + pad
            base_ly = y_top + i * s * leading + s * 0.82
            c.saveState()
            c.translate(PW - base_ly, PH - lx)
            c.rotate(-90)
            self._draw_line(0, 0, ln, font, s)
            c.restoreState()
        self.log.append(f'σελ.4 {tag}: μέγεθος {s} γραμμές {len(lines)}')

    def save(self):
        self.c.showPage()
        self.c.save()
