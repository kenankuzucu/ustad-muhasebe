# -*- coding: utf-8 -*-
"""
ÜSTAD MUHASEBE · dışa aktarma motoru (Word .docx + Excel .xlsx)
Sadece Python standart kütüphanesi kullanır (openpyxl / python-docx GEREKMEZ).
xlsx ve docx aslında birer ZIP + XML paketidir; burada o paketler elle kurulur.
"""
import zipfile
import datetime
import html


# ---------------------------------------------------------------- yardımcılar
def _harf(sayac):
    """1 -> A, 27 -> AA"""
    s = ""
    while sayac > 0:
        sayac, kalan = divmod(sayac - 1, 26)
        s = chr(65 + kalan) + s
    return s


def _hucre(deger, satir_no, sutun_no, stil=0):
    ref = "%s%d" % (_harf(sutun_no), satir_no)
    if isinstance(deger, (int, float)) and not isinstance(deger, bool):
        return '<c r="%s" s="%d"><v>%s</v></c>' % (ref, stil, repr(float(deger)).rstrip("0").rstrip(".") if isinstance(deger, float) else deger)
    metin = "" if deger is None else str(deger)
    return '<c r="%s" s="%d" t="inlineStr"><is><t xml:space="preserve">%s</t></is></c>' % (
        ref, stil, html.escape(metin))


# ---------------------------------------------------------------- Excel (.xlsx)
CONTENT_TYPES_XLSX = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>
</Types>"""

RELS_XLSX = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
</Relationships>"""

WB_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>"""

STYLES_XLSX = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
<numFmts count="2">
<numFmt numFmtId="164" formatCode="#,##0.00"/>
<numFmt numFmtId="165" formatCode="DD.MM.YYYY"/>
</numFmts>
<fonts count="4">
<font><sz val="11"/><color rgb="FF1B2430"/><name val="Calibri"/></font>
<font><b/><sz val="11"/><color rgb="FFFFFFFF"/><name val="Calibri"/></font>
<font><b/><sz val="14"/><color rgb="FF0B5F7A"/><name val="Calibri"/></font>
<font><b/><sz val="11"/><color rgb="FF0B5F7A"/><name val="Calibri"/></font>
</fonts>
<fills count="4">
<fill><patternFill patternType="none"/></fill>
<fill><patternFill patternType="gray125"/></fill>
<fill><patternFill patternType="solid"><fgColor rgb="FF0E7490"/><bgColor indexed="64"/></patternFill></fill>
<fill><patternFill patternType="solid"><fgColor rgb="FFE6F6FB"/><bgColor indexed="64"/></patternFill></fill>
</fills>
<borders count="2">
<border/>
<border><left style="thin"><color rgb="FFB7C4D4"/></left><right style="thin"><color rgb="FFB7C4D4"/></right><top style="thin"><color rgb="FFB7C4D4"/></top><bottom style="thin"><color rgb="FFB7C4D4"/></bottom></border>
</borders>
<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>
<cellXfs count="7">
<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>
<xf numFmtId="0" fontId="1" fillId="2" borderId="0" xfId="0" applyFont="1" applyFill="1"/>
<xf numFmtId="164" fontId="0" fillId="0" borderId="0" xfId="0" applyNumberFormat="1"/>
<xf numFmtId="164" fontId="1" fillId="2" borderId="0" xfId="0" applyNumberFormat="1" applyFont="1" applyFill="1"/>
<xf numFmtId="0" fontId="2" fillId="0" borderId="0" xfId="0" applyFont="1"/>
<xf numFmtId="0" fontId="3" fillId="3" borderId="0" xfId="0" applyFont="1" applyFill="1"/>
<xf numFmtId="164" fontId="0" fillId="3" borderId="0" xfId="0" applyNumberFormat="1" applyFill="1"/>
</cellXfs>
</styleSheet>"""


def xlsx_yaz(yol, baslik, basliklar, satirlar, sayi_ilk_sutun=None, alt_satirlar=None):
    """Basit ama geçerli bir .xlsx üretir. Satırlarda değer int/float/str olabilir."""
    if sayi_ilk_sutun is None:
        sayi_ilk_sutun = len(basliklar)  # hiçbiri sayı değil

    def sayi_mi(i, deger):
        return isinstance(deger, (int, float)) or (i + 1) >= sayi_ilk_sutun

    xml = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
           '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">',
           '<cols>']
    for i in range(len(basliklar)):
        gen = 30 if i < 2 else 16
        xml.append('<col min="%d" max="%d" width="%d" customWidth="1"/>' % (i + 1, i + 1, gen))
    xml.append('</cols><sheetData>')

    satir_no = 1
    # üst başlık şeridi
    xml.append('<row r="1" ht="24" customHeight="1">%s</row>' % _hucre(baslik, 1, 1, 4))
    satir_no = 2
    # firma/rapor bilgisi
    bilgi = "ÜSTAD MUHASEBE · %s · %s" % (baslik, datetime.datetime.now().strftime("%d.%m.%Y %H:%M"))
    xml.append('<row r="2">%s</row>' % _hucre(bilgi, 2, 1, 0))
    satir_no = 4
    hucreler = "".join(_hucre(b, satir_no, i + 1, 1) for i, b in enumerate(basliklar))
    xml.append('<row r="%d" ht="20" customHeight="1">%s</row>' % (satir_no, hucreler))
    satir_no += 1
    for satir in satirlar:
        hucreler = []
        for i, deger in enumerate(satir):
            stil = 2 if sayi_mi(i, deger) and i + 1 >= sayi_ilk_sutun else 0
            hucreler.append(_hucre(deger, satir_no, i + 1, stil))
        xml.append('<row r="%d">%s</row>' % (satir_no, "".join(hucreler)))
        satir_no += 1
    if alt_satirlar:
        for etiket, deger in alt_satirlar:
            hucreler = [_hucre(etiket, satir_no, 1, 5)]
            for i in range(1, len(basliklar)):
                hucreler.append(_hucre(None, satir_no, i + 1, 5))
            hucreler[-1] = _hucre(deger, satir_no, len(basliklar), 6)
            xml.append('<row r="%d">%s</row>' % (satir_no, "".join(hucreler)))
            satir_no += 1
    xml.append('</sheetData><autoFilter ref="A4:%s%d"/></worksheet>' % (_harf(len(basliklar)), max(4, satir_no - 1)))
    sheet = "".join(xml)

    wb = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
          '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
          'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
          '<sheets><sheet name="%s" sheetId="1" r:id="rId1"/></sheets></workbook>'
          % html.escape(baslik[:28]))

    with zipfile.ZipFile(yol, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", CONTENT_TYPES_XLSX)
        z.writestr("_rels/.rels", RELS_XLSX)
        z.writestr("xl/workbook.xml", wb)
        z.writestr("xl/_rels/workbook.xml.rels", WB_RELS)
        z.writestr("xl/styles.xml", STYLES_XLSX)
        z.writestr("xl/worksheets/sheet1.xml", sheet)
    return yol


# ---------------------------------------------------------------- Word (.docx)
CONTENT_TYPES_DOCX = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
</Types>"""

RELS_DOCX = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""

DOC_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>"""

STYLES_DOCX = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
<w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Segoe UI" w:hAnsi="Segoe UI"/><w:sz w:val="21"/></w:rPr></w:rPrDefault></w:docDefaults>
<w:style w:type="paragraph" w:styleId="Normal" w:default="1"><w:name w:val="Normal"/></w:style>
<w:style w:type="paragraph" w:styleId="Serit"><w:name w:val="Serit"/><w:pPr><w:spacing w:before="120" w:after="80"/><w:shd w:val="clear" w:color="auto" w:fill="0E7490"/></w:pPr><w:rPr><w:color w:val="FFFFFF"/><w:b/><w:sz w:val="26"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Baslik2"><w:name w:val="Baslik2"/><w:pPr><w:spacing w:before="160" w:after="60"/></w:pPr><w:rPr><w:color w:val="0E7490"/><w:b/><w:sz w:val="24"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Alt"><w:name w:val="Alt"/><w:pPr><w:jc w:val="center"/></w:pPr><w:rPr><w:color w:val="6B7A90"/><w:sz w:val="16"/></w:rPr></w:style>
</w:styles>"""


def _p(metin, stil=None, kalin=False, renk=None, boyut=None, hiza=None):
    ppr = ""
    if stil:
        ppr = '<w:pStyle w:val="%s"/>' % stil
    if hiza:
        ppr += '<w:jc w:val="%s"/>' % hiza
    if ppr:
        ppr = "<w:pPr>%s</w:pPr>" % ppr
    rpr = ""
    if kalin:
        rpr += "<w:b/>"
    if renk:
        rpr += '<w:color w:val="%s"/>' % renk
    if boyut:
        rpr += '<w:sz w:val="%d"/>' % boyut
    if rpr:
        rpr = "<w:rPr>%s</w:rPr>" % rpr
    return ('<w:p>%s<w:r>%s<w:t xml:space="preserve">%s</w:t></w:r></w:p>'
            % (ppr, rpr, html.escape("" if metin is None else str(metin))))


def _hucre_w(metin, genislik, dolgu=None, kalin=False, renk=None, sayi=False):
    ppr = '<w:pPr><w:spacing w:before="40" w:after="40"/>%s</w:pPr>' % (
        '<w:shd w:val="clear" w:color="auto" w:fill="%s"/>' % dolgu if dolgu else "")
    rpr = ""
    if kalin:
        rpr += "<w:b/>"
    if renk:
        rpr += '<w:color w:val="%s"/>' % renk
    rpr += '<w:sz w:val="19"/>'
    rpr = "<w:rPr>%s</w:rPr>" % rpr
    tcpr = '<w:tcPr><w:tcW w:w="%d" w:type="dxa"/>%s</w:tcPr>' % (
        genislik, '<w:shd w:val="clear" w:color="auto" w:fill="%s"/>' % dolgu if dolgu else "")
    return ('<w:tc>%s<w:p>%s<w:r>%s<w:t xml:space="preserve">%s</w:t></w:r></w:p></w:tc>'
            % (tcpr, ppr, rpr, html.escape("" if metin is None else str(metin))))


def _tablo(basliklar, satirlar, genislikler=None, zebra=True):
    n = len(basliklar)
    toplam = 9360
    if not genislikler:
        genislikler = [toplam // n] * n
    kenar = '<w:tblBorders>' + "".join(
        '<w:%s w:val="single" w:sz="6" w:color="B7C4D4"/>' % k
        for k in ("top", "left", "bottom", "right", "insideH", "insideV")) + "</w:tblBorders>"
    xml = ['<w:tbl><w:tblPr><w:tblW w:w="%d" w:type="dxa"/>%s</w:tblPr><w:tblGrid>%s</w:tblGrid>'
           % (toplam, kenar, "".join('<w:gridCol w:w="%d"/>' % g for g in genislikler))]
    xml.append("<w:tr>" + "".join(
        _hucre_w(b, genislikler[min(i, len(genislikler) - 1)], dolgu="0E7490", kalin=True, renk="FFFFFF")
        for i, b in enumerate(basliklar)) + "</w:tr>")
    for j, satir in enumerate(satirlar):
        dolgu = "F2FAFD" if (zebra and j % 2) else None
        xml.append("<w:tr>" + "".join(
            _hucre_w(d, genislikler[min(i, len(genislikler) - 1)], dolgu=dolgu) for i, d in enumerate(satir))
            + "</w:tr>")
    xml.append("</w:tbl>")
    return "".join(xml)


def docx_yaz(yol, baslik, bolumler):
    """bolumler: [{"baslik": str, "paragraf": [str, ...], "tablo": (basliklar, satirlar), "not": str}, ...]"""
    govde = [_p("ÜSTAD MUHASEBE", stil="Serit"),
             _p(baslik, stil="Baslik2"),
             _p("Oluşturma: %s" % datetime.datetime.now().strftime("%d.%m.%Y %H:%M"), stil="Alt")]
    for b in bolumler:
        if b.get("baslik"):
            govde.append(_p(b["baslik"], stil="Serit"))
        for p in b.get("paragraf", []) or []:
            govde.append(_p(p))
        if b.get("tablo"):
            basliklar, satirlar = b["tablo"]
            govde.append(_p(""))
            govde.append(_tablo(basliklar, satirlar, b.get("genislikler")))
        if b.get("not"):
            govde.append(_p(b["not"], stil="Alt"))
        govde.append(_p(""))

    doc = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
           '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
           '<w:body>%s<w:sectPr><w:pgSz w:w="11906" w:h="16838"/>'
           '<w:pgMar w:top="1134" w:right="1134" w:bottom="1134" w:left="1134"/></w:sectPr>'
           '</w:body></w:document>' % "".join(govde))

    with zipfile.ZipFile(yol, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", CONTENT_TYPES_DOCX)
        z.writestr("_rels/.rels", RELS_DOCX)
        z.writestr("word/document.xml", doc)
        z.writestr("word/_rels/document.xml.rels", DOC_RELS)
        z.writestr("word/styles.xml", STYLES_DOCX)
    return yol


if __name__ == "__main__":
    import os
    t = os.environ.get("TMPDIR", ".")
    xlsx_yaz(os.path.join(t, "deneme.xlsx"), "Cari Listesi",
             ["Kod", "Ünvan", "Tip", "Borç", "Alacak", "Bakiye"],
             [["C-001", "Yalçın Kuzucu", "Müşteri", 12000.0, 5000.0, 7000.0],
              ["C-002", "Gülşah Demir", "Tedarikçi", 0, 9500.0, -9500.0]],
             sayi_ilk_sutun=4, alt_satirlar=[("TOPLAM", 2500.0)])
    docx_yaz(os.path.join(t, "deneme.docx"), "Cari Ekstresi",
             [{"baslik": "Özet", "paragraf": ["Bu bir denemedir."],
               "tablo": (["Tarih", "Açıklama", "Borç", "Alacak"], [["01.09.2026", "Tahsilat", "", "5.000,00"]])}])
    print("yazıldı:", t)
