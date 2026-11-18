import os, json
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION, XL_LABEL_POSITION, XL_TICK_LABEL_POSITION

HERE = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(HERE); FIG = os.path.join(HERE, "fig")
OUT = os.path.join(HERE, "Slide_TTTN_V2.pptx")
rj = lambda n: json.load(open(os.path.join(R, "results", n), encoding="utf8"))
base, mend, merg, cd, fs = rj("base_result.json"), rj("mendeley_result.json"), rj("merged_result.json"), rj("cross_domain_result.json"), rj("fewshot_result.json")

c = lambda h: RGBColor.from_string(h)
DARK, GREEN, LIGHT, AMBER, TEAL, RED, INK, MUTED, WHITE, GRAY = "173F2A", "2E7D32", "F1F8E9", "F9A825", "00838F", "C62828", "1F2933", "5F6B73", "FFFFFF", "78909C"
HF, BF = "Cambria", "Calibri"

prs = Presentation(); prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
BLANK = prs.slide_layouts[6]
TOTAL = 19
num = [0]


def bg(slide, color):
    f = slide.background.fill; f.solid(); f.fore_color.rgb = c(color)


def text(slide, x, y, w, h, t, size=18, bold=False, color=INK, font=BF, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, italic=False, name=None):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h)); tf = tb.text_frame; tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0; tf.vertical_anchor = anchor
    lines = t if isinstance(t, list) else [t]
    for i, ln in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph(); p.alignment = align
        r = p.add_run(); r.text = ln; r.font.size = Pt(size); r.font.bold = bold; r.font.italic = italic; r.font.color.rgb = c(color); r.font.name = font
    if name: tb.name = name
    return tb


def bullets(slide, x, y, w, h, items, size=18, color=INK, gap=8):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h)); tf = tb.text_frame; tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    for i, it in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph(); p.space_after = Pt(gap)
        pPr = p._p.get_or_add_pPr(); pPr.set("marL", "285750"); pPr.set("indent", "-285750")
        bu = pPr.makeelement("{http://schemas.openxmlformats.org/drawingml/2006/main}buChar", {"char": "•"}); pPr.append(bu)
        parts = it.split("**")
        for k, s in enumerate(parts):
            if s:
                r = p.add_run(); r.text = s; r.font.size = Pt(size); r.font.bold = (k % 2 == 1); r.font.color.rgb = c(color); r.font.name = BF
    return tb


def box(slide, x, y, w, h, fill, shape=MSO_SHAPE.ROUNDED_RECTANGLE, line=None, radius=0.08, name=None):
    s = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h)); s.fill.solid(); s.fill.fore_color.rgb = c(fill)
    if line: s.line.color.rgb = c(line); s.line.width = Pt(1)
    else: s.line.fill.background()
    s.shadow.inherit = False
    if shape == MSO_SHAPE.ROUNDED_RECTANGLE: s.adjustments[0] = radius
    if name: s.name = name
    return s


def new(tag, title, dark=False):
    s = prs.slides.add_slide(BLANK); num[0] += 1
    bg(s, DARK if dark else WHITE)
    if tag: text(s, .6, .38, 9, .3, tag, 12, True, "A5D6A7" if dark else GREEN, BF, name="Section")
    text(s, .6, .7, 12.1, 1.0, title, 30, True, WHITE if dark else INK, HF, anchor=MSO_ANCHOR.TOP, name="Title")
    if num[0] > 1:
        text(s, 11.9, 7.0, 0.9, .3, f"{num[0]:02d} / {TOTAL}", 11, False, "A5D6A7" if dark else MUTED, BF, PP_ALIGN.RIGHT, name="PageNum")
    return s


def notes(s, t): s.notes_slide.notes_text_frame.text = t


def card(s, x, y, w, h, title, body, fill=LIGHT, tcolor=GREEN, size=15):
    box(s, x, y, w, h, fill)
    text(s, x + .25, y + .2, w - .5, .4, title, 16, True, tcolor, BF)
    text(s, x + .25, y + .7, w - .5, h - .85, body, size, False, INK, BF)


def style_chart(ch, legend=True, size=12):
    ch.font.size = Pt(size); ch.font.name = BF; ch.font.color.rgb = c(INK)
    ch.has_legend = legend
    if legend:
        ch.legend.position = XL_LEGEND_POSITION.BOTTOM; ch.legend.include_in_layout = False; ch.legend.font.size = Pt(size)


def axes(ch, ymin=None, ymax=None, title_y=None, fmt='0', major=None):
    va = ch.value_axis; va.has_major_gridlines = True; va.major_gridlines.format.line.color.rgb = c("E0E0E0"); va.format.line.fill.background()
    va.tick_labels.font.size = Pt(12); va.tick_labels.number_format = fmt; va.tick_labels.number_format_is_linked = False
    if ymin is not None: va.minimum_scale = ymin
    if ymax is not None: va.maximum_scale = ymax
    if major: va.major_unit = major
    ca = ch.category_axis; ca.tick_labels.font.size = Pt(12); ca.format.line.color.rgb = c("BDBDBD"); ca.has_major_gridlines = False
    if title_y:
        va.has_title = True; va.axis_title.text_frame.text = title_y
        va.axis_title.text_frame.paragraphs[0].runs[0].font.size = Pt(12); va.axis_title.text_frame.paragraphs[0].runs[0].font.bold = False


def line_chart(s, x, y, w, h, cats, series, colors, title, ymin=None, ymax=None, fmt='0.0', ytitle=None, major=None):
    cdt = CategoryChartData(); cdt.categories = cats
    for n, v in series: cdt.add_series(n, v)
    gf = s.shapes.add_chart(XL_CHART_TYPE.LINE_MARKERS, Inches(x), Inches(y), Inches(w), Inches(h), cdt); ch = gf.chart
    style_chart(ch); ch.has_title = True; ch.chart_title.text_frame.text = title
    ch.chart_title.text_frame.paragraphs[0].runs[0].font.size = Pt(14); ch.chart_title.text_frame.paragraphs[0].runs[0].font.bold = True
    for sr, col in zip(ch.plots[0].series, colors):
        sr.format.line.color.rgb = c(col); sr.format.line.width = Pt(2.75); sr.smooth = False
        sr.marker.format.fill.solid(); sr.marker.format.fill.fore_color.rgb = c(col); sr.marker.format.line.color.rgb = c(col); sr.marker.size = 8
    axes(ch, ymin, ymax, ytitle, fmt, major); return ch


def col_chart(s, x, y, w, h, cats, series, colors, title=None, ymin=None, ymax=None, fmt='0.0', labels=True, legend=False, vary=None, gap=60, ytitle=None):
    cdt = CategoryChartData(); cdt.categories = cats
    for n, v in series: cdt.add_series(n, v)
    gf = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(x), Inches(y), Inches(w), Inches(h), cdt); ch = gf.chart
    style_chart(ch, legend)
    if title:
        ch.has_title = True; ch.chart_title.text_frame.text = title
        ch.chart_title.text_frame.paragraphs[0].runs[0].font.size = Pt(14); ch.chart_title.text_frame.paragraphs[0].runs[0].font.bold = True
    else: ch.has_title = False
    pl = ch.plots[0]; pl.gap_width = gap; pl.overlap = -10 if len(series) > 1 else 0
    for sr, col in zip(pl.series, colors):
        sr.format.fill.solid(); sr.format.fill.fore_color.rgb = c(col); sr.invert_if_negative = False
    if vary:
        for i, col in enumerate(vary):
            pt = pl.series[0].points[i]; pt.format.fill.solid(); pt.format.fill.fore_color.rgb = c(col)
    if labels:
        pl.has_data_labels = True; dl = pl.data_labels; dl.font.size = Pt(13); dl.font.bold = True; dl.number_format = fmt; dl.number_format_is_linked = False
        dl.position = XL_LABEL_POSITION.OUTSIDE_END
    axes(ch, ymin, ymax, ytitle, '0'); return ch


def table(s, x, y, w, colw, header, rows, size=14, rowh=.42, hl=None):
    gt = s.shapes.add_table(len(rows) + 1, len(header), Inches(x), Inches(y), Inches(w), Inches(rowh * (len(rows) + 1))); t = gt.table
    for i, cw in enumerate(colw): t.columns[i].width = Inches(cw)
    for ci, hd in enumerate(header):
        cell = t.cell(0, ci); cell.fill.solid(); cell.fill.fore_color.rgb = c(GREEN); cell.text = ""
        r = cell.text_frame.paragraphs[0].add_run(); r.text = hd; r.font.size = Pt(size); r.font.bold = True; r.font.color.rgb = c(WHITE); r.font.name = BF
        cell.text_frame.paragraphs[0].alignment = PP_ALIGN.LEFT if ci == 0 else PP_ALIGN.CENTER; cell.vertical_anchor = MSO_ANCHOR.MIDDLE
    for ri, row in enumerate(rows, 1):
        for ci, v in enumerate(row):
            cell = t.cell(ri, ci); cell.fill.solid(); cell.fill.fore_color.rgb = c(LIGHT if ri % 2 == 0 else WHITE); cell.text = ""
            r = cell.text_frame.paragraphs[0].add_run(); r.text = str(v); r.font.size = Pt(size); r.font.color.rgb = c(INK); r.font.name = BF
            r.font.bold = (hl is not None and ri - 1 in hl)
            cell.text_frame.paragraphs[0].alignment = PP_ALIGN.LEFT if ci == 0 else PP_ALIGN.CENTER; cell.vertical_anchor = MSO_ANCHOR.MIDDLE
    return t


def pic(s, f, x, y, w=None, h=None):
    kw = {}
    if w: kw["width"] = Inches(w)
    if h: kw["height"] = Inches(h)
    return s.shapes.add_picture(os.path.join(FIG, f), Inches(x), Inches(y), **kw)


def takeaway(s, t, y=6.35):
    box(s, .6, y, 12.1, .6, LIGHT); text(s, .85, y, 11.6, .6, t, 16, True, DARK, BF, anchor=MSO_ANCHOR.MIDDLE)


# ================= 1. TITLE =================
s = new("", "", dark=True)
text(s, .8, .8, 11, .4, "TRƯỜNG ĐẠI HỌC GIAO THÔNG VẬN TẢI TP. HỒ CHÍ MINH", 14, True, "A5D6A7")
text(s, .8, 1.2, 11, .4, "Viện Công nghệ thông tin và Điện, Điện tử  ·  Báo cáo thực tập tốt nghiệp", 14, False, "C8E6C9")
text(s, .8, 2.3, 11.5, 2.0, "Nhận dạng bệnh lá sầu riêng bằng học chuyển giao", 44, True, WHITE, HF)
text(s, .8, 4.0, 11.5, .9, "Huấn luyện trên hai bộ dữ liệu và đánh giá ngoài miền", 26, False, "C8E6C9", HF)
text(s, .8, 5.6, 6, .35, "Giảng viên hướng dẫn: TS. Trần Thế Vinh", 16, False, WHITE)
text(s, .8, 6.0, 6, .35, "Vũ Gia Linh (070305004702)", 16, False, "C8E6C9")
text(s, .8, 6.4, 6, .35, "Lê Ngọc Bích Loan (060305003162)", 16, False, "C8E6C9")
notes(s, "Chào thầy/cô và hội đồng. Nhóm em là Vũ Gia Linh và Lê Ngọc Bích Loan, xin trình bày phần làm lại của đề tài sau buổi báo cáo trước, do thầy Trần Thế Vinh hướng dẫn. Đề tài giờ tập trung vào nhận dạng bệnh lá sầu riêng bằng học chuyển giao, huấn luyện trên hai bộ dữ liệu lá sầu riêng và đánh giá cả trong lẫn ngoài miền dữ liệu.")

# ================= 2. WHY REDO =================
s = new("01 · BỐI CẢNH", "Vì sao nhóm làm lại đề tài")
box(s, .6, 1.9, 4.6, 4.2, DARK)
text(s, .85, 2.2, 4.1, .4, "GIAI ĐOẠN TRƯỚC", 13, True, "A5D6A7")
text(s, .85, 2.75, 4.1, 1.3, "30–54%", 66, True, WHITE, HF)
text(s, .85, 4.3, 4.1, 1.6, "Accuracy khi huấn luyện trên cà chua, khoai tây rồi nhận bệnh lá sầu riêng chưa từng thấy (few-shot)", 16, False, "C8E6C9")
rows = [("1", "Quá thấp để dùng thực tế", "Thầy nhận xét số liệu trên sầu riêng quá thấp."), ("2", "Bài toán khó và xa mục tiêu", "Học từ cây khác rồi nhận bệnh cây mới là chuyển miền rất khó."),
        ("3", "Hướng mới", "Thu gọn về lá sầu riêng, thay PlantVillage bằng dữ liệu sầu riêng.")]
for i, (n, t1, t2) in enumerate(rows):
    y = 1.9 + i * 1.45
    o = box(s, 5.7, y + .05, .6, .6, GREEN, MSO_SHAPE.OVAL); text(s, 5.7, y + .05, .6, .6, n, 20, True, WHITE, BF, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
    text(s, 6.55, y, 6.1, .4, t1, 20, True, INK); text(s, 6.55, y + .5, 6.1, .8, t2, 16, False, MUTED)
notes(s, "Ở giai đoạn trước, nhóm huấn luyện mô hình trên ảnh cà chua và khoai tây rồi nhận bệnh lá sầu riêng chưa từng thấy. Với giao thức đã lọc ảnh trùng, độ chính xác chỉ khoảng 30 đến 54 phần trăm. Thầy nhận xét con số này quá thấp để áp dụng thực tế. Nhóm nhận ra nguyên nhân gốc nằm ở cách đặt bài toán: học từ cây khác rồi nhận bệnh cây mới là một bài toán chuyển miền rất khó, trong khi mục tiêu chỉ là nhận bệnh lá sầu riêng. Vì vậy nhóm thu gọn đề tài và thay dữ liệu huấn luyện bằng dữ liệu lá sầu riêng.")

# ================= 3. QUESTIONS =================
s = new("01 · BỐI CẢNH", "Bốn câu hỏi của phần làm lại")
qs = [("1", "Trong miền", "Học có giám sát trên dữ liệu lá sầu riêng đạt bao nhiêu?"), ("2", "Ngoài miền", "Mô hình có còn đúng khi ảnh đến từ nguồn khác (vườn, thiết bị chụp)?"),
      ("3", "Gộp nguồn", "Gộp hai bộ dữ liệu có giúp một mô hình dùng được cho cả hai?"), ("4", "Few-shot", "Học trên dữ liệu sầu riêng có giúp nhận lớp mới từ 1–10 ảnh mẫu?")]
for i, (n, t1, t2) in enumerate(qs):
    x = .6 + (i % 2) * 6.2; y = 1.95 + (i // 2) * 2.2
    box(s, x, y, 5.9, 1.95, LIGHT); box(s, x + .25, y + .25, .65, .65, GREEN, MSO_SHAPE.OVAL)
    text(s, x + .25, y + .25, .65, .65, n, 22, True, WHITE, BF, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
    text(s, x + 1.15, y + .25, 4.5, .4, t1, 20, True, GREEN); text(s, x + 1.15, y + .8, 4.5, 1.0, t2, 16, False, INK)
notes(s, "Phần làm lại trả lời bốn câu hỏi. Một, học có giám sát trên dữ liệu sầu riêng đạt bao nhiêu trong cùng một nguồn ảnh. Hai, mô hình còn đúng không khi ảnh đến từ nguồn khác. Ba, gộp hai bộ dữ liệu có giúp được không. Bốn, đặc trưng học trên dữ liệu sầu riêng có giúp nhận lớp mới từ vài ảnh mẫu hay không.")

# ================= 4. DATASETS =================
s = new("02 · DỮ LIỆU", "Hai bộ dữ liệu lá sầu riêng")
card(s, .6, 1.9, 3.9, 2.45, "Kaggle  ·  4.437 ảnh", ["5 lớp, ảnh 224×224", "Chụp bằng điện thoại, nền tự nhiên", "2 chuyên gia, Kappa 98,25%", "CC BY 4.0"], size=15)
card(s, .6, 4.55, 3.9, 2.35, "Mendeley  ·  2.595 ảnh", ["6 lớp, ảnh 400×400", "Bình Phước và Tiền Giang", "Chia sẵn train/val/test"], fill="FFF8E1", tcolor="B26A00", size=15)
table(s, 4.9, 1.95, 7.8, [3.0, 2.4, 2.4], ["Lớp", "Kaggle", "Mendeley"],
      [["Algal", "733", "462"], ["Blight", "937", "440"], ["Healthy", "976", "484"], ["Phomopsis", "878", "411"], ["Allocaridara (côn trùng)", "913", "–"],
       ["Colletotrichum", "–", "400"], ["Rhizoctonia", "–", "398"]], size=15, rowh=.52, hl=None)
text(s, 4.9, 6.2, 7.8, .7, "4 lớp chung (4 hàng đầu); Allocaridara chỉ có ở Kaggle, Colletotrichum và Rhizoctonia chỉ có ở Mendeley.", 14, False, MUTED, italic=True)
notes(s, "Nhóm dùng hai bộ dữ liệu. Bộ Kaggle có 4.437 ảnh, 5 lớp, chụp bằng điện thoại ngoài vườn, hai chuyên gia gán nhãn với độ đồng thuận Kappa 98,25 phần trăm. Bộ Mendeley có 2.595 ảnh, 6 lớp, là bộ nhóm đã dùng ở giai đoạn trước. Hai bộ có bốn lớp chung. Lưu ý Allocaridara là tổn thương do rầy, không phải bệnh nấm. Colletotrichum và Rhizoctonia chỉ có ở Mendeley.")

# ================= 5. DEDUP =================
s = new("02 · DỮ LIỆU", "Kiểm tra trùng lặp trước khi huấn luyện")
box(s, .6, 1.9, 3.6, 4.1, DARK)
text(s, .85, 2.2, 3.1, 1.3, "121", 80, True, "FFD54F", HF)
text(s, .85, 3.75, 3.1, 1.9, "ảnh Blight có mặt ở cả hai bộ; đều nằm trong tập train của Kaggle", 17, False, WHITE)
bullets(s, 4.6, 1.95, 4.2, 4.0, ["So từng cặp ảnh bằng độ tương quan ảnh xám 24×24 (không phụ thuộc kích thước)", "Kết quả tách bạch: 121 cặp ≥ 0,98, mọi cặp còn lại ≤ 0,8",
                                  "Lật, xoay không tìm thêm cặp nào", "Thêm 2 ảnh trùng nội bộ Kaggle; 35 ảnh gần trùng nội bộ Mendeley loại khỏi val và test"], size=16)
text(s, 9.2, 1.95, 3.5, .4, "Sau khi khử trùng", 16, True, GREEN)
table(s, 9.2, 2.45, 3.5, [1.4, .7, .7, .7], ["Nguồn", "Train", "Val", "Test"], [["Kaggle", "2.983", "443", "888"], ["Mendeley", "1.814", "377", "381"]], size=13, rowh=.5)
takeaway(s, "Nếu không loại, ảnh Blight trùng sẽ làm điểm chuyển nguồn cao giả.")
notes(s, "Trước khi huấn luyện nhóm kiểm tra ảnh trùng giữa hai bộ bằng độ tương quan ảnh xám thu nhỏ. Kết quả rất tách bạch: 121 ảnh khớp gần như hoàn toàn, tất cả đều thuộc lớp Blight, còn mọi cặp khác đều thấp. Nếu không loại các ảnh này, kết quả khi chuyển nguồn ở lớp Blight sẽ cao giả vì mô hình đã thấy đúng ảnh đó lúc huấn luyện. Nhóm cũng loại thêm 2 ảnh trùng nội bộ Kaggle và bỏ 35 ảnh gần trùng của Mendeley khỏi tập val và test.")

# ================= 6. METHOD =================
s = new("03 · PHƯƠNG PHÁP", "Quy trình và ba mô hình")
pic(s, "pipeline.png", .6, 1.9, w=12.1)
table(s, .6, 4.75, 12.1, [3.4, 4.7, 2.0, 2.0], ["Mô hình", "Dữ liệu huấn luyện", "Số lớp", "Ảnh train"],
      [["Chỉ Kaggle", "Kaggle (đã khử trùng)", "5", "2.983"], ["Chỉ Mendeley", "Mendeley", "6", "1.814"], ["Gộp 2 bộ", "Kaggle + Mendeley", "7", "4.797"]], size=15, rowh=.5)
notes(s, "Quy trình gồm: gom hai bộ dữ liệu, khử trùng và chia tập, fine-tune MobileNetV2, đánh giá trong và ngoài miền, rồi đưa vào demo. Nhóm huấn luyện ba mô hình giống hệt nhau về kiến trúc và cấu hình, chỉ khác dữ liệu: chỉ Kaggle với 2.983 ảnh, chỉ Mendeley với 1.814 ảnh, và gộp hai bộ với 4.797 ảnh, bảy lớp.")

# ================= 7. CONFIG =================
s = new("03 · PHƯƠNG PHÁP", "Cấu hình huấn luyện")
table(s, .6, 1.95, 7.4, [2.3, 5.1], ["Thành phần", "Giá trị"],
      [["Kiến trúc", "MobileNetV2 pretrained ImageNet"], ["Huấn luyện", "Fine-tune toàn mạng"], ["Tối ưu", "AdamW, lr 3×10⁻⁴, cosine"], ["Loss", "Cross-entropy, label smoothing 0,05"],
       ["Batch / epoch", "32 / 6"], ["Seed, phần cứng", "42; CPU, 4–13 phút mỗi epoch"]], size=15, rowh=.58)
card(s, 8.4, 1.95, 4.3, 2.0, "Tăng cường dữ liệu", ["Cắt ngẫu nhiên, lật ngang", "Đổi sáng, tương phản, bão hòa"], size=15)
card(s, 8.4, 4.15, 4.3, 2.0, "Mô hình gộp", ["Đổi màu mạnh hơn (0,5/0,5/0,4)", "để bớt phụ thuộc ánh sáng từng nguồn"], size=15, fill="FFF8E1", tcolor="B26A00")
notes(s, "Cả ba mô hình dùng MobileNetV2 pretrained ImageNet, fine-tune toàn mạng với AdamW, learning rate 3 nhân 10 mũ trừ 4, lịch cosine, label smoothing 0,05, batch 32, 6 epoch, seed 42, chạy trên CPU. Riêng mô hình gộp, nhóm tăng cường độ thay đổi màu để mô hình bớt phụ thuộc vào ánh sáng riêng của từng nguồn ảnh.")

# ================= 8. LOSS =================
s = new("04 · KẾT QUẢ", "Loss giảm đều, accuracy validation đạt 94–96%")
ep = [str(i) for i in range(1, 7)]
line_chart(s, .6, 1.85, 6.0, 4.4, ep, [("Chỉ Kaggle", [round(h["loss"], 3) for h in base["history"]]), ("Chỉ Mendeley", [round(h["loss"], 3) for h in mend["history"]]),
                                       ("Gộp 2 bộ", [round(h["loss"], 3) for h in merg["history"]])], [GREEN, AMBER, TEAL], "Loss huấn luyện theo epoch", 0.2, 1.0, '0.0', "Loss (cross-entropy)", 0.2)
line_chart(s, 6.8, 1.85, 5.9, 4.4, ep, [("Chỉ Kaggle", [round(100 * h["val_acc"], 1) for h in base["history"]]), ("Chỉ Mendeley", [round(100 * h["val_acc"], 1) for h in mend["history"]]),
                                        ("Gộp 2 bộ", [round(100 * h["val_acc"], 1) for h in merg["history"]])], [GREEN, AMBER, TEAL], "Accuracy validation theo epoch (%)", 88, 97, '0', "Accuracy (%)", 2)
takeaway(s, "Loss từ 0,68–0,88 xuống 0,29–0,36 sau 6 epoch; chưa ghi loss validation nên chỉ nhận xét quá khớp qua accuracy validation.", 6.4)
notes(s, "Đây là biểu đồ loss huấn luyện của ba mô hình. Bên trái là loss cross-entropy trên tập huấn luyện sau mỗi epoch: cả ba giảm đều từ khoảng 0,7 đến 0,9 ở epoch một xuống khoảng 0,3 đến 0,36 ở epoch sáu. Mô hình gộp có loss cao hơn vì dùng tăng cường màu mạnh hơn và có nhiều lớp hơn. Bên phải là accuracy trên tập validation, tăng từ khoảng 90 phần trăm lên 94 đến 96 phần trăm và đi ngang ở các epoch cuối. Cần nói thật là nhóm chỉ ghi loss huấn luyện, không ghi loss validation, nên chưa thể vẽ đường cong để kết luận về quá khớp; chỉ có accuracy validation ổn định làm bằng chứng gián tiếp.")

# ================= 9. IN-DOMAIN =================
s = new("04 · KẾT QUẢ", "Trong miền: 93–96% trên tập test cùng nguồn")
col_chart(s, .6, 1.85, 7.4, 4.4, ["Chỉ Kaggle\ntest Kaggle", "Chỉ Mendeley\ntest Mendeley", "Gộp\ntest Kaggle", "Gộp\ntest Mendeley"], [("Accuracy", [93.7, 96.1, 94.7, 94.0])],
          [GREEN], None, 80, 100, '0.0"%"', vary=[GREEN, AMBER, TEAL, TEAL], ytitle="Accuracy (%)")
bullets(s, 8.4, 2.0, 4.3, 4.0, ["Cả ba mô hình đạt 93–96% trên ảnh cùng nguồn", "Mô hình gộp: 94,5% tổng, macro F1 0,939", "Chênh lệch dưới 1–2 điểm chưa nên diễn giải mạnh (chỉ một seed)", "Cao hơn nhiều so với 30–54% của giai đoạn trước"], size=17, gap=12)
takeaway(s, "Đây mới là hiệu năng trong miền; kiểm tra ngoài miền ở các slide sau.", 6.4)
notes(s, "Trên tập test cùng nguồn với dữ liệu huấn luyện, mô hình chỉ Kaggle đạt 93,7 phần trăm, mô hình chỉ Mendeley đạt 96,1, và mô hình gộp đạt 94,7 trên Kaggle và 94,0 trên Mendeley, tổng 94,5 phần trăm. Đây là mức cao hơn nhiều so với giai đoạn trước. Tuy nhiên nhóm chỉ chạy một seed, nên chênh lệch dưới một đến hai điểm giữa các mô hình chưa nên diễn giải mạnh. Và quan trọng, đây mới chỉ là hiệu năng trong miền.")

# ================= 10. CONFUSION =================
s = new("04 · KẾT QUẢ", "Mô hình gộp nhầm ở đâu")
pic(s, "cm_merged_kaggle.png", .6, 1.8, h=3.9); pic(s, "cm_merged_mendeley.png", 6.9, 1.8, h=3.9)
text(s, .6, 5.8, 6, .6, "Kaggle: Phomopsis nhầm nhiều nhất (đúng 156/176); Healthy gần như không nhầm (194/195)", 14, False, MUTED)
text(s, 6.9, 5.8, 5.8, .6, "Mendeley: lỗi tập trung ở Blight, Colletotrichum, Rhizoctonia (vết hoại tử nâu giống nhau)", 14, False, MUTED)
takeaway(s, "Lỗi nằm ở các bệnh có triệu chứng giống nhau, không phải lỗi ngẫu nhiên.", 6.45)
notes(s, "Ma trận nhầm lẫn của mô hình gộp. Bên trái là test Kaggle: lớp Healthy gần như không nhầm, 194 trên 195 ảnh, còn Phomopsis nhầm nhiều nhất, rải sang Algal, Blight và Healthy. Bên phải là test Mendeley: lỗi tập trung ở bộ ba Blight, Colletotrichum và Rhizoctonia, vì các bệnh này đều có vết hoại tử màu nâu khá giống nhau ở giai đoạn sớm.")

# ================= 11. CROSS DOMAIN =================
s = new("04 · KẾT QUẢ", "Ngoài miền: đổi nguồn ảnh, độ chính xác tụt mạnh")
col_chart(s, .6, 1.85, 4.6, 4.3, ["Mendeley → Kaggle", "Kaggle → Mendeley"], [("Accuracy", [32.0, 76.2])], [RED], "Huấn luyện → test (4 lớp chung)", 0, 100, '0.0"%"', vary=[RED, AMBER], gap=70)
col_chart(s, 5.4, 1.85, 7.3, 4.3, ["Algal", "Blight", "Healthy", "Phomopsis"],
          [("Mendeley → Kaggle", [round(100 * cd["mendeley_model_on_kaggle"]["per_class"][k], 0) for k in ("Algal", "Blight", "Healthy", "Phomopsis")]),
           ("Kaggle → Mendeley", [round(100 * cd["kaggle_model_on_mendeley"]["per_class"][k], 0) for k in ("Algal", "Blight", "Healthy", "Phomopsis")])],
          [RED, AMBER], "Tỷ lệ đúng theo lớp (%)", 0, 115, '0', legend=True, gap=50)
takeaway(s, "Mô hình Mendeley gán Blight cho gần hết ảnh Kaggle: 96,1% trong miền nhưng chỉ 32,0% khi đổi nguồn.", 6.4)
notes(s, "Đây là kết quả quan trọng nhất. Nhóm huấn luyện trên một nguồn rồi kiểm tra trên nguồn còn lại, chỉ với bốn lớp chung và đã loại ảnh Blight trùng. Mô hình huấn luyện trên Mendeley chỉ đạt 32 phần trăm trên ảnh Kaggle, dù đạt 96,1 phần trăm trên ảnh Mendeley. Nó gán nhãn Blight cho gần như mọi ảnh, ví dụ 806 trên 976 ảnh Healthy bị gán Blight. Chiều ngược lại, huấn luyện Kaggle và test Mendeley đạt 76,2 phần trăm, tốt hơn vì Kaggle đa dạng hơn, nhưng Blight chỉ 57 và Phomopsis 45 phần trăm. Như vậy con số 94 đến 96 phần trăm trong miền không nói lên độ chính xác thực tế.")

# ================= 12. WHY =================
s = new("04 · KẾT QUẢ", "Vì sao: ảnh hai bộ khác phong cách chụp")
pic(s, "healthy_compare.png", .6, 1.85, w=7.6)
bullets(s, 8.6, 2.0, 4.1, 3.0, ["Mendeley: tối hơn, chụp cận một hai lá", "Kaggle: sáng hơn, nhiều lá, nhiều góc", "Cả hai đều là lớp Healthy"], size=17, gap=12)
box(s, 8.6, 4.55, 4.1, 1.55, "FFF8E1")
text(s, 8.85, 4.7, 3.6, 1.3, "Giả thuyết, chưa kiểm chứng: mô hình học theo ánh sáng và bối cảnh của từng nguồn hơn là dấu hiệu bệnh.", 15, False, INK, italic=True)
takeaway(s, "Gộp nhiều nguồn và tăng cường màu là hướng khắc phục hợp lý.", 6.4)
notes(s, "Để hiểu vì sao, nhóm đặt ảnh lá Healthy của hai bộ cạnh nhau. Ảnh Mendeley ở hàng trên tối hơn và chụp cận, ảnh Kaggle ở hàng dưới sáng hơn và có nhiều lá hơn. Nhóm cho rằng mô hình học theo ánh sáng và bối cảnh chụp của từng nguồn. Đây là giả thuyết dựa trên quan sát và kết quả, nhóm chưa kiểm chứng riêng, ví dụ bằng chuẩn hóa màu hay xem vùng ảnh mô hình chú ý.")

# ================= 13. FEW-SHOT =================
s = new("04 · KẾT QUẢ", "Few-shot: học trên sầu riêng giúp nhiều nhất ở 1–5 ảnh mẫu")
line_chart(s, .6, 1.85, 7.6, 4.4, ["1 mẫu", "5 mẫu", "10 mẫu"],
           [("Logistic, backbone Kaggle", [round(100 * fs["results"][f"linear_kaggle_{k}shot"]["acc"], 1) for k in (1, 5, 10)]),
            ("Prototype, backbone Kaggle", [round(100 * fs["results"][f"proto_kaggle_{k}shot"]["acc"], 1) for k in (1, 5, 10)]),
            ("Logistic, chỉ ImageNet", [round(100 * fs["results"][f"linear_imagenet_{k}shot"]["acc"], 1) for k in (1, 5, 10)]),
            ("Prototype, chỉ ImageNet", [round(100 * fs["results"][f"proto_imagenet_{k}shot"]["acc"], 1) for k in (1, 5, 10)])],
           [TEAL, "4DB6AC", GRAY, "B0BEC5"], "Few-shot trên Mendeley (6-way, 600 episode), %", 35, 80, '0', "Accuracy (%)", 10)
bullets(s, 8.6, 2.0, 4.1, 4.0, ["Backbone Kaggle hơn đối chứng: +17 điểm (1 mẫu), +7 (5 mẫu), +4,6 (10 mẫu)", "Lợi ích đến từ 4 lớp chung; 2 lớp chỉ có ở Mendeley gần như hòa", "Mức tăng so với giai đoạn trước chủ yếu nhờ MobileNetV2 và ảnh 224×224"], size=16, gap=12)
takeaway(s, "10 ảnh mẫu mỗi lớp cho 76,7% trên Mendeley với đặc trưng đóng băng.", 6.4)
notes(s, "Về few-shot, nhóm dùng đặc trưng của mô hình huấn luyện trên Kaggle để phân loại Mendeley chỉ từ một, năm hoặc mười ảnh mẫu mỗi lớp, và so với đối chứng chỉ pretrain ImageNet. Đặc trưng học từ dữ liệu sầu riêng giúp rõ ở một mẫu, tăng khoảng 17 điểm, và khá ở năm mẫu, tăng khoảng 7 điểm; ở mười mẫu chỉ hơn khoảng 4,6 điểm. Lợi ích đến chủ yếu từ bốn lớp chung với Kaggle; với hai lớp chỉ có ở Mendeley hai backbone gần như hòa, nhưng chỉ có hai lớp nên số đo này nhiễu. Cần lưu ý mức tăng so với giai đoạn trước chủ yếu là nhờ backbone MobileNetV2 và ảnh 224 chứ không riêng do bộ Kaggle.")

# ================= 14. DEMO =================
s = new("05 · ỨNG DỤNG MINH HỌA", "Ứng dụng Streamlit dùng mô hình gộp 7 lớp")
pic(s, "demo_ui.jpg", .6, 1.85, h=4.4)
bullets(s, 6.5, 2.0, 6.2, 4.0, ["Upload ảnh lá: hiện lớp dự đoán, độ tin cậy, biểu đồ xác suất 7 lớp", "Cảnh báo khi độ tin cậy thấp (ngưỡng chỉnh được)", "Tab ảnh mẫu từ tập test, lịch sử, giới hạn và kết quả", "Chạy độc lập trên máy cá nhân, thư mục demo khoảng 11 MB"], size=17, gap=12)
takeaway(s, "Cả 33 ảnh mẫu đều đoán đúng, nhưng chúng nằm trong tập test của hai bộ nên không phản ánh độ chính xác thực tế.", 6.4)
notes(s, "Nhóm cập nhật ứng dụng minh họa dùng mô hình gộp bảy lớp. Người dùng upload ảnh lá và nhận lớp dự đoán, độ tin cậy và biểu đồ xác suất; ứng dụng cảnh báo khi độ tin cậy thấp, có tab ảnh mẫu lấy từ tập test, lịch sử và tab ghi rõ giới hạn. Ứng dụng chạy độc lập trên máy cá nhân. Cả 33 ảnh mẫu đều đoán đúng, nhưng vì nằm trong tập test của hai bộ nên không phản ánh độ chính xác thực tế.")

# ================= 15. THRESHOLD =================
s = new("05 · ỨNG DỤNG MINH HỌA", "Ngưỡng độ tin cậy chưa loại được ảnh lá cây khác")
col_chart(s, .6, 1.85, 7.6, 4.4, ["0,5", "0,6", "0,7", "0,8", "0,9"], [("Giữ ảnh sầu riêng", [97, 93, 90, 86, 71]), ("Loại ảnh lá cây khác", [7, 20, 27, 40, 60])],
          [GREEN, RED], "Theo ngưỡng độ tin cậy, %", 0, 115, '0', legend=True, gap=50)
bullets(s, 8.6, 2.0, 4.1, 4.0, ["Thử trên 600 ảnh sầu riêng và 15 ảnh lá ớt, cà chua", "Ngưỡng 0,7 chỉ loại 4/15 ảnh lá cây khác", "Nhiều ảnh lá cây khác vẫn đạt trên 0,9"], size=17, gap=12)
takeaway(s, "Chỉ dùng demo với ảnh lá sầu riêng; muốn loại ảnh lạ cần thêm lớp \"khác\" hoặc bộ phát hiện riêng.", 6.4)
notes(s, "Nhóm đo thử ngưỡng độ tin cậy để loại ảnh không phải lá sầu riêng. Trên 600 ảnh sầu riêng và 15 ảnh lá ớt, cà chua, ở ngưỡng 0,7 ứng dụng giữ 90 phần trăm ảnh sầu riêng nhưng chỉ loại được khoảng 27 phần trăm ảnh lá cây khác, tức 4 trên 15 ảnh. Nhiều ảnh lá cây khác vẫn được gán bệnh với độ tin cậy trên 0,9. Số ảnh ngoài phạm vi chỉ 15 nên con số mang tính tham khảo. Kết luận là ngưỡng softmax không đủ tin cậy, demo chỉ nên dùng với ảnh lá sầu riêng.")

# ================= 16. LIMITS =================
s = new("06 · HẠN CHẾ", "Những điều số liệu chưa chứng minh")
items = [("Chưa có nguồn thứ ba", "Mô hình gộp chưa được kiểm tra ngoài hai bộ đã huấn luyện."), ("Một seed, CPU", "Chưa có khoảng tin cậy giữa các lần huấn luyện."),
         ("Chưa ghi loss validation", "Khó kết luận quá khớp bằng đường cong."), ("Giả thuyết ánh sáng", "Chưa kiểm chứng riêng bằng chuẩn hóa màu hay phân tích vùng ảnh."),
         ("Nhãn và lớp", "Allocaridara là côn trùng; hai lớp chỉ có một nguồn."), ("Ảnh ngoài phạm vi", "Ngưỡng độ tin cậy không đủ tin cậy.")]
for i, (t1, t2) in enumerate(items):
    x = .6 + (i % 2) * 6.2; y = 1.9 + (i // 2) * 1.5
    box(s, x, y, 5.9, 1.3, LIGHT); text(s, x + .25, y + .17, 5.4, .4, t1, 17, True, GREEN); text(s, x + .25, y + .65, 5.4, .6, t2, 15, False, INK)
notes(s, "Nhóm nêu rõ những giới hạn. Chưa có nguồn dữ liệu thứ ba để kiểm tra mô hình gộp ngoài miền. Mọi kết quả chỉ một seed trên CPU nên chưa có khoảng tin cậy giữa các lần huấn luyện. Chưa ghi loss validation. Giả thuyết về ánh sáng chưa được kiểm chứng riêng. Allocaridara là tổn thương do côn trùng, và hai lớp Colletotrichum, Rhizoctonia chỉ có một nguồn. Cuối cùng ngưỡng độ tin cậy không loại được ảnh ngoài phạm vi.")

# ================= 17. FUTURE =================
s = new("06 · HƯỚNG PHÁT TRIỂN", "Học bán giám sát: huấn luyện lặp trên ảnh chưa gán nhãn")
cyc = [("1  Huấn luyện", "Mô hình hiện có", GREEN), ("2  Dự đoán", "Trên ảnh sầu riêng chưa gán nhãn", TEAL), ("3  Kiểm tra", "Giữ dự đoán tin cậy cao, sửa nhãn sai", AMBER), ("4  Huấn luyện lại", "Thêm ảnh đã gán nhãn", GREEN)]
for i, (t1, t2, col) in enumerate(cyc):
    x = .6 + i * 3.1
    box(s, x, 2.1, 2.75, 1.9, col); text(s, x + .2, 2.3, 2.35, .45, t1, 18, True, WHITE if col != AMBER else INK); text(s, x + .2, 2.9, 2.35, 1.0, t2, 15, False, WHITE if col != AMBER else INK)
    if i < 3: text(s, x + 2.72, 2.8, .4, .5, "→", 26, True, MUTED, align=PP_ALIGN.CENTER)
bullets(s, .6, 4.5, 12.1, 1.7, ["Theo gợi ý của thầy: lặp lại để cải thiện độ chính xác thay vì dừng ở một mức", "Cần tập ảnh lá sầu riêng chưa gán nhãn đủ lớn (khó thu thập)", "Song song: thêm nguồn dữ liệu, chuẩn hóa màu, thêm lớp \"khác\" để loại ảnh ngoài phạm vi"], size=17, gap=10)
takeaway(s, "Kiểm tra ngoài miền nên dùng ảnh thực địa độc lập làm tập test.", 6.4)
notes(s, "Hướng phát triển chính theo gợi ý của thầy là học bán giám sát. Dùng mô hình hiện có dự đoán trên một tập lớn ảnh lá sầu riêng chưa gán nhãn, giữ lại các dự đoán tin cậy cao, kiểm tra thủ công và sửa các dự đoán sai, rồi đưa lại vào huấn luyện và lặp lại, thay vì dừng ở một mức độ chính xác. Cách này cần một tập ảnh chưa gán nhãn đủ lớn, vốn khó thu thập. Song song nhóm sẽ thêm nguồn dữ liệu, chuẩn hóa màu và thêm lớp ngoài phạm vi, và nên dùng ảnh thực địa độc lập làm tập kiểm tra.")

# ================= 18. CONCLUSION =================
s = new("07 · KẾT LUẬN", "Kết luận", dark=True)
ks = [("93–96%", "trong miền sau khi thu gọn về lá sầu riêng, so với 30–54% trước"), ("96% → 32%", "khi mô hình học một nguồn gặp ảnh nguồn khác"), ("1 mô hình, 7 lớp", "gộp hai bộ đạt 94–95% trên cả hai nguồn")]
for i, (big, small) in enumerate(ks):
    x = .6 + i * 4.1
    box(s, x, 1.95, 3.85, 3.3, "21533A"); text(s, x + .3, 2.3, 3.3, .9, big, 32 if i != 2 else 28, True, "FFD54F", HF); text(s, x + .3, 3.5, 3.3, 1.6, small, 17, False, WHITE)
text(s, .6, 5.75, 12.1, .9, "Bước tiếp theo: thêm nguồn dữ liệu, học bán giám sát trên ảnh chưa gán nhãn, và cơ chế loại ảnh ngoài phạm vi.", 18, False, "C8E6C9")
notes(s, "Tóm lại, khi thu gọn về lá sầu riêng và huấn luyện trên dữ liệu sầu riêng, độ chính xác trong miền đạt 93 đến 96 phần trăm so với 30 đến 54 phần trăm trước đó. Nhưng phép thử ngoài miền cho thấy mô hình học một nguồn có thể giảm từ 96 xuống 32 phần trăm khi gặp ảnh nguồn khác, nên con số trong miền không nói lên độ chính xác thực tế. Gộp hai bộ giúp một mô hình bảy lớp đạt 94 đến 95 phần trăm trên cả hai nguồn. Các bước tiếp theo là thêm nguồn dữ liệu, học bán giám sát và cơ chế loại ảnh ngoài phạm vi.")

# ================= 19. THANKS =================
s = new("", "", dark=True)
text(s, .8, 2.8, 11.7, 1.2, "Xin cảm ơn thầy/cô đã lắng nghe", 44, True, WHITE, HF)
text(s, .8, 4.3, 11.7, .5, "Nhóm sẵn sàng trả lời câu hỏi", 22, False, "C8E6C9", HF)
notes(s, "Xin cảm ơn thầy cô đã lắng nghe. Nhóm em sẵn sàng trả lời câu hỏi.")

prs.save(OUT); print("saved", OUT, len(prs.slides.__iter__.__self__._sldIdLst), "slides")
