# -*- coding: utf-8 -*-
"""Συμπλήρωση του εντύπου Δ1 (δήλωση φόρου δωρεάς-γονικής παροχής μετά την 1-1-2002)
(έκδοση του λογισμικού του γραφείου, 4 σελίδες, η 4η περιστραμμένη).
Χρήση: python3 fill_d1.py <έντυπο.pdf> <data.json> <έξοδος.pdf>"""
import sys, json
from pypdf import PdfReader, PdfWriter
from overlay import Sheet, _wrap, PH

src, data_path, out = sys.argv[1], sys.argv[2], sys.argv[3]
D = json.load(open(data_path, encoding='utf-8'))
tmp = out + '.overlay.pdf'
S = Sheet(tmp)


def rows_text(x0, x1, rows, text, size, pad=2.0, start_line=0, per_row=2, font='F'):
    """Συνεχές κείμενο σε γραμμές πίνακα, per_row γραμμές κειμένου ανά γραμμή πίνακα.
    Επιστρέφει τον επόμενο ελεύθερο δείκτη γραμμής κειμένου."""
    lines = []
    for para in text.split('\n'):
        lines += _wrap(para, font, size, (x1 - x0) - 2 * pad)
    slots = []
    for (t, b) in rows:
        h = b - t
        if per_row == 1:
            slots.append(t + h / 2 + size * 0.33)
        else:
            slots.append(t + h * 0.30 + size * 0.36)
            slots.append(t + h * 0.74 + size * 0.36)
    if start_line + len(lines) > len(slots):
        S.log.append(f'ΥΠΕΡΧΕΙΛΙΣΗ γραμμών πίνακα: {len(lines)} γραμμές από τη θέση {start_line}, διαθέσιμες {len(slots)}')
    for i, ln in enumerate(lines):
        k = start_line + i
        if k >= len(slots):
            break
        S._draw_line(x0 + pad, PH - slots[k], ln, font, size)
    S.log.append(f'πίνακας: {len(lines)} γραμμές κειμένου, μέγεθος {size}')
    return start_line + len(lines)


# =========================== ΣΕΛΙΔΑ 1 ===========================
S.text(140.5, 89.0, D['pros_doy'], size=8.5, bold=True)
S.cell(441, 567, 86, 101, D['sxet_dilosi'], size=8, tag='σχετ.δήλωση')
S.cell(377, 567, 104, 121, D['sxet_doy'], size=8, tag='σχετ.ΔΟΥ')
S.cell(416, 556, 123.5, 142, D['eidos'], size=8, tag='είδος')

COLS = [(18, 88.5), (88.5, 219), (219, 287), (287, 345), (345, 400.5), (400.5, 473), (473, 527), (527, 576.5)]


def person(p, row_top, row_bot, addr_rows, birth_top, birth_bot):
    vals = [p['afm'], p['eponymo'], p['onoma'], p['patros'], p['syzygou'], p['doy'], p['til'], p['syggeneia']]
    for (x0, x1), v in zip(COLS, vals):
        S.cell(x0, x1, row_top, row_bot, v, size=7.8, align='center', tag='πρόσωπο')
    for (t, b), (vk, ve) in zip(addr_rows, p['addr']):
        S.cell(96.5, 237.5, t, b, vk, size=7.4, tag='διεύθυνση κατοικίας')
        S.cell(237.5, 381, t, b, ve, size=7.4, tag='διεύθυνση επαγγέλματος')
    S.cell(435.5, 509.5, birth_top, birth_bot, p['topos_gen'], size=7.4, align='center', tag='τόπος γέννησης')
    S.cell(509.5, 577, birth_top, birth_bot, p['imer_gen'], size=7.8, align='center', tag='ημ. γέννησης')


person(D['doritis'], 312.5, 347, [(386.5, 404.5), (404.5, 420), (420, 436), (436, 452.5), (452.5, 479)], 391.5, 425.5)
person(D['doreodoxos'], 545, 579.5, [(619, 637), (637, 652.5), (652.5, 668.5), (668.5, 685), (685, 711.5)], 624, 658)

# =========================== ΣΕΛΙΔΑ 2 ===========================
S.next_page()
a = D['antikl']
S.cell(127, 197, 38.5, 50, a['afm'], size=7.6, tag='αντίκλ ΑΦΜ')
S.cell(237, 362, 38.5, 50, a['eponymo'], size=7.6, tag='αντίκλ επώνυμο')
S.cell(391, 464, 38.5, 50, a['onoma'], size=7.6, tag='αντίκλ όνομα')
S.cell(440, 594, 49.0, 57.0, a['dieuth'], size=6.4, align='right', tag='αντίκλ διεύθυνση')
# 6. Αιτία υποβολής: συνέχεια μετά το τυπωμένο «Σύνταξη συμβολαίου»
S.cell(270, 580, 58.0, 77.5, D['aitia'], size=7.6, valign='top', tag='αιτία')
# 7. Ζει ο άλλος γονέας;
if D['allos_zei'] == 'OXI':
    S.mark_x(426.5, 438.5, 76.5, 88)
elif D['allos_zei'] == 'NAI':
    S.mark_x(386.5, 398.5, 76.5, 88)
S.cell(494, 558, 72.7, 91.7, D['allos_im_thanatou'], size=8, align='center', tag='ημ θανάτου')

# 9. Περιουσιακά στοιχεία (14 γραμμές πίνακα, δύο γραμμές κειμένου ανά γραμμή)
ROWS9 = [(143.5, 160.5), (160.5, 177.5), (177.5, 194.2), (194.5, 211), (211.5, 228), (228, 245), (245, 262),
         (262, 278.5), (279, 295.5), (296, 312.5), (313, 329.5), (329.5, 346.5), (346.5, 363), (363.5, 380)]
it = D['periousiako']
S.cell(18, 36, ROWS9[0][0], ROWS9[0][1], '1', size=8, align='center', tag='α/α')
rows_text(36, 479.5, ROWS9, it['perigrafi'], size=it.get('size', 6.7), pad=3.0)
rows_text(479.5, 533, ROWS9, it['eidos'], size=6.6, pad=2.0)
rows_text(533, 574, ROWS9, it['katigoria'], size=6.2, pad=1.6)

# 11. Βάρη
if D.get('vari'):
    S.cell(37, 364.5, 441.5, 456, D['vari'], size=7.5, tag='βάρη')
# 13. Απαλλαγή πρώτης κατοικίας
if D.get('proti_katoikia') == 'OXI':
    S.mark_x(50.5, 62.5, 558.5, 570)
# 14. Άμεση φορολογία ψιλής κυριότητας
if D.get('psili') == 'OXI':
    S.mark_x(101, 113, 598, 609.5)

# 15. Προγενέστερες δωρεές - γονικές παροχές (σελ. 2)
ROWS15 = [(664.5, 680.5), (680.5, 696.5), (697, 713), (713, 729)]
for i, pr in enumerate(D['progenesteres']):
    t, b = ROWS15[i]
    S.cell(18, 37, t, b, str(i + 1), size=7.5, align='center', tag='15 α/α')
    S.cell(37, 211, t, b, pr['symvolaio'], size=7.6, align='center', tag='15 συμβόλαιο')
    S.cell(211, 291.5, t, b, pr['afm_symv'], size=7.4, align='center', tag='15 ΑΦΜ συμβ')
    S.cell(291.5, 576.5, t, b, pr['onoma_symv'], size=7.4, tag='15 όνομα συμβ')

# =========================== ΣΕΛΙΔΑ 3 ===========================
S.next_page()
S.text(122.0, 30.6, D['symv_arith'], size=8.5)
S.text(338.0, 30.6, D['symv_dimdiam'], size=8.0)
S.text(482.0, 30.6, D['symv_til'], size=8.0)
# 8. Στοιχεία άλλου γονέα
S.cell(178, 260, 74.5, 88, D['allos_afm'], size=7.6, tag='άλλος ΑΦΜ')
S.cell(326, 590, 74.5, 88, D['allos_onoma'], size=7.4, tag='άλλος όνομα')
# 10. Αξία
ROWS10 = ROWS9
ax = D['axia']
S.cell(14.5, 77.5, ROWS10[0][0], ROWS10[0][1], ax['antikeimeniki'], size=7.8, bold=True, align='center', tag='αντικ. αξία')
S.cell(77.5, 156, ROWS10[0][0], ROWS10[0][1], ax['dilotheisa'], size=7.8, bold=True, align='center', tag='δηλωθείσα')
if ax.get('a_keimeno'):
    rows_text(14.5, 77.5, ROWS10[1:], ax['a_keimeno'], size=6.0, pad=1.8)
# Τόπος, ημερομηνία, δηλούντες
S.text(347.0, 492.0, D['ypografi_topos'], size=8.0)
S.cell(438, 513, 487, 504, D['ypografi_imer'], size=7.8, align='center', tag='ημερομηνία')
S.cell(300, 578, 523.5, 534, D['diloun_titlos'], size=8.2, bold=True, align='center', tag='δηλούντες')
S.cell(300, 578, 534.5, 566, D['diloun_paroxon'], size=6.5, align='center', valign='top', tag='για τον παρέχοντα')
S.cell(300, 578, 588, 605, D['diloun_dexomeni'], size=6.5, align='center', valign='top', tag='για τη δεχόμενη')
# Βεβαίωση γνησίου υπογραφής (αριστερά, για τη σφραγίδα της συμβολαιογράφου)
S.cell(128, 294, 560, 614, D['vevaiosi_gnisiou'], size=6.8, align='center', valign='top', tag='βεβαίωση γνησίου')
# 15 (συνέχεια): έδρα, αρ. δήλωσης/ΔΟΥ, αξία, φόρος, γονέας
ROWS15b = [(663.5, 679), (679.5, 695.5), (695.5, 711.5), (712, 727.5)]
for i, pr in enumerate(D['progenesteres']):
    t, b = ROWS15b[i]
    S.cell(18, 112, t, b, pr['edra'], size=7.4, align='center', tag='15 έδρα')
    S.cell(112, 206.5, t, b, pr['ar_dilosis'], size=7.2, align='center', tag='15 αρ δήλωσης')
    S.cell(206.5, 279, t, b, pr['axia_drx'], size=7.6, align='center', tag='15 αξία δρχ')
    S.cell(279, 352.5, t, b, pr['axia_eur'], size=7.6, align='center', tag='15 αξία ευρώ')
    S.cell(352.5, 421, t, b, pr['foros_drx'], size=7.4, align='center', tag='15 φόρος δρχ')
    S.cell(421, 476, t, b, pr['foros_eur'], size=7.4, align='center', tag='15 φόρος ευρώ')
    S.cell(476, 568, t, b, pr['goneas'], size=7.0, align='center', tag='15 γονέας')
if D.get('synolo15'):
    s15 = D['synolo15']
    S.cell(206.5, 279, 728, 744, s15['drx'], size=7.6, align='center', tag='σύνολο δρχ')
    S.cell(279, 352.5, 728, 744, s15['eur'], size=7.6, align='center', tag='σύνολο ευρώ')
if D.get('simeiosi15'):
    S.cell(18, 577, 749, 790, D['simeiosi15'], size=6.4, valign='top', tag='σημ. 15')

# =========================== ΣΕΛΙΔΑ 4 (περιστραμμένη) ===========================
S.next_page()
COL18 = [(16, 84.5), (84.5, 191.5), (191.5, 273), (273, 366), (366, 390), (390, 428), (428, 542), (542, 660.5),
         (660.5, 724), (724, 822.5)]
ROW18 = [(185.3, 203.8), (203.8, 222.8)]
for r, pl in zip(ROW18, D['plirexousioi']):
    vals = [pl['afm'], pl['eponymo'], pl['onoma'], pl['odos'], pl['arith'], pl['tk'], pl['dimos'], pl['dimdiam'],
            pl['til'], pl['eggrafo']]
    for (lx0, lx1), v in zip(COL18, vals):
        S.rcell(lx0, lx1, r[0], r[1], v, size=6.6, align='center' if lx1 - lx0 < 60 else 'left', tag='18')
L19 = [(286.5, 309.0), (309.5, 331.5), (331.5, 355.0), (356.0, 404.0)]
for (ly0, ly1), txt in zip(L19, D['dikaiologitika']):
    S.rcell(31, 405, ly0, ly1, txt, size=6.4, valign='top' if ly1 - ly0 > 30 else 'middle', tag='19')

S.save()

base = PdfReader(src)
ov = PdfReader(tmp)
w = PdfWriter()
for i, pg in enumerate(base.pages):
    pg.merge_page(ov.pages[i])
    w.add_page(pg)
w.add_metadata({'/Title': D.get('pdf_title', 'Δήλωση φόρου γονικής παροχής')})
with open(out, 'wb') as f:
    w.write(f)
print('\n'.join(S.log))
