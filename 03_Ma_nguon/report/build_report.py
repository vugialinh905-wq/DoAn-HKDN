import os
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(HERE, "fig")
OUT = os.path.join(HERE, "Bao_cao_TTTN_V2.docx")
import json
SEEDS = json.load(open(os.path.join(os.path.dirname(HERE), "results", "merged_seeds.json"), encoding="utf8"))  # chay seeds_summary.py truoc
pc = lambda v: f"{100 * v:.1f}".replace(".", ",")
ms = lambda k: f"{pc(SEEDS['summary'][k]['mean'])} ± {pc(SEEDS['summary'][k]['std'])}%"
sd = lambda k: pc(SEEDS["summary"][k]["std"])
f3 = lambda v: f"{v:.3f}".replace(".", ",")
FONT = "Times New Roman"
GREEN = RGBColor(0x1B, 0x5E, 0x20)

d = Document()
sec = d.sections[0]
sec.page_width, sec.page_height = Cm(21), Cm(29.7)
sec.left_margin, sec.right_margin, sec.top_margin, sec.bottom_margin = Cm(3), Cm(2), Cm(2.5), Cm(2.5)


def setfont(style, size, bold=False, color=None, italic=False):
    style.font.name = FONT; style.font.size = Pt(size); style.font.bold = bold; style.font.italic = italic
    if color is not None:
        style.font.color.rgb = color
    rpr = style.element.get_or_add_rPr(); rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts"); rpr.append(rf)
    for a in list(rf.attrib):
        if "Theme" in a:
            del rf.attrib[a]
    for a in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        rf.set(qn(a), FONT)


st = d.styles
setfont(st["Normal"], 13)
st["Normal"].paragraph_format.line_spacing = 1.3
st["Normal"].paragraph_format.space_after = Pt(6)
for name, size, before, after in (("Heading 1", 16, 18, 8), ("Heading 2", 14, 12, 6), ("Heading 3", 13, 10, 4)):
    setfont(st[name], size, bold=True, color=GREEN)
    pf = st[name].paragraph_format; pf.space_before, pf.space_after, pf.keep_with_next = Pt(before), Pt(after), True
setfont(st["Caption"], 11, italic=True, color=RGBColor(0x33, 0x33, 0x33))

fig_n = [0]; tab_n = [0]


def P(text="", bold=False, italic=False, align=None, size=None, after=None, indent=True, color=None):
    p = d.add_paragraph()
    if indent and align is None:
        p.paragraph_format.first_line_indent = Cm(1)
    if align == "c":
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    elif align == "j" or align is None:
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    if after is not None:
        p.paragraph_format.space_after = Pt(after)
    parts = text.split("**")
    for i, s in enumerate(parts):
        if not s:
            continue
        r = p.add_run(s); r.bold = bold or (i % 2 == 1); r.italic = italic
        if size: r.font.size = Pt(size)
        if color is not None: r.font.color.rgb = color
    return p


def H(text, lvl=1):
    return d.add_heading(text, level=lvl)


def BUL(items):
    for t in items:
        p = d.add_paragraph(style="List Bullet"); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_after = Pt(3)
        parts = t.split("**")
        for i, s in enumerate(parts):
            if s:
                r = p.add_run(s); r.bold = (i % 2 == 1)


def shade(cell, color):
    tcPr = cell._tc.get_or_add_tcPr(); sh = OxmlElement("w:shd")
    sh.set(qn("w:val"), "clear"); sh.set(qn("w:color"), "auto"); sh.set(qn("w:fill"), color); tcPr.append(sh)


def cap_par(label, seqid, n, text, keep=False):
    cp = d.add_paragraph(style="Caption"); cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if keep:
        cp.paragraph_format.keep_with_next = True; cp.paragraph_format.space_after = Pt(3)
    cp.add_run(f"{label} ")
    for kind in ("begin", "instr", "separate", "text", "end"):
        r = cp.add_run()
        if kind == "instr":
            it = OxmlElement("w:instrText"); it.set(qn("xml:space"), "preserve"); it.text = f" SEQ {seqid} \\* ARABIC "; r._r.append(it)
        elif kind == "text":
            r.text = str(n)
        else:
            fc = OxmlElement("w:fldChar"); fc.set(qn("w:fldCharType"), kind); r._r.append(fc)
    cp.add_run(f". {text}")
    return cp


def TABLE(caption, header, rows, widths=None, size=11, bold_last=False):
    tab_n[0] += 1
    cap_par("Bảng", "Bang", tab_n[0], caption, keep=True)
    t = d.add_table(rows=1, cols=len(header)); t.style = "Table Grid"; t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(header):
        c = t.rows[0].cells[i]; c.text = ""; r = c.paragraphs[0].add_run(h); r.bold = True; r.font.size = Pt(size)
        r.font.color.rgb = RGBColor(255, 255, 255); shade(c, "2E7D32"); c.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    for ri, row in enumerate(rows):
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ""; r = cells[i].paragraphs[0].add_run(str(v)); r.font.size = Pt(size)
            if bold_last and ri == len(rows) - 1: r.bold = True
            cells[i].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.LEFT if i == 0 else WD_ALIGN_PARAGRAPH.CENTER
            if ri % 2 == 1: shade(cells[i], "F1F8E9")
    for row in t.rows:
        for c in row.cells:
            for p in c.paragraphs:
                p.paragraph_format.space_after = Pt(2); p.paragraph_format.line_spacing = 1.1
    if widths:
        for row in t.rows:
            for i, w in enumerate(widths):
                row.cells[i].width = Cm(w)
    d.add_paragraph().paragraph_format.space_after = Pt(4)


def FIGURE(fname, caption, width=14.5):
    fig_n[0] += 1
    p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(os.path.join(FIG, fname), width=Cm(width))
    cap_par("Hình", "Hinh", fig_n[0], caption)


def pagebreak():
    d.add_paragraph().add_run().add_break(WD_BREAK.PAGE)


def field(par, instr):
    r = par.add_run(); f1 = OxmlElement("w:fldChar"); f1.set(qn("w:fldCharType"), "begin"); r._r.append(f1)
    r2 = par.add_run(); it = OxmlElement("w:instrText"); it.set(qn("xml:space"), "preserve"); it.text = instr; r2._r.append(it)
    r3 = par.add_run(); f2 = OxmlElement("w:fldChar"); f2.set(qn("w:fldCharType"), "separate"); r3._r.append(f2)
    r4 = par.add_run("Nhấn chuột phải và chọn Update Field để cập nhật mục lục." if "TOC" in instr else "1")
    r5 = par.add_run(); f3 = OxmlElement("w:fldChar"); f3.set(qn("w:fldCharType"), "end"); r5._r.append(f3)


# footer page number
fp = sec.footer.paragraphs[0]; fp.alignment = WD_ALIGN_PARAGRAPH.CENTER; field(fp, "PAGE")

# ---------------- BÌA ----------------
for t, b, s in (("TRƯỜNG ĐẠI HỌC GIAO THÔNG VẬN TẢI TP. HỒ CHÍ MINH", True, 14), ("VIỆN CÔNG NGHỆ THÔNG TIN VÀ ĐIỆN, ĐIỆN TỬ", True, 14)):
    P(t, bold=b, align="c", size=s, after=4)
P("", align="c", after=40)
P("BÁO CÁO THỰC TẬP TỐT NGHIỆP", bold=True, align="c", size=22, after=24, color=GREEN)
P("ĐỀ TÀI:", bold=True, align="c", size=14, after=6)
P("NHẬN DẠNG BỆNH TRÊN LÁ SẦU RIÊNG BẰNG HỌC CHUYỂN GIAO: HUẤN LUYỆN TRÊN HAI BỘ DỮ LIỆU VÀ ĐÁNH GIÁ NGOÀI MIỀN", bold=True, align="c", size=16, after=50)
P("Giảng viên hướng dẫn: TS. Trần Thế Vinh", align="c", size=13, after=14)
P("Sinh viên thực hiện:", bold=True, align="c", size=13, after=4)
P("Vũ Gia Linh – MSSV 070305004702", align="c", size=13, after=2)
P("Lê Ngọc Bích Loan – MSSV 060305003162", align="c", size=13, after=60)
P("Thành phố Hồ Chí Minh, tháng 11 năm 2026", align="c", size=13)
pagebreak()

# ---------------- PHÂN CÔNG + LỜI CẢM ƠN ----------------
H("Bảng phân chia công việc", 1)
TABLE("Phân công công việc", ["Họ và tên", "Nhiệm vụ", "Mức độ hoàn thành"],
      [["Vũ Gia Linh", "[Nhóm điền nhiệm vụ của giai đoạn này]", "[điền]"], ["Lê Ngọc Bích Loan", "[Nhóm điền nhiệm vụ của giai đoạn này]", "[điền]"]],
      widths=[4, 9, 3])
H("Lời cảm ơn", 1)
P("Nhóm chúng em xin gửi lời cảm ơn chân thành đến thầy TS. Trần Thế Vinh đã tận tình hướng dẫn và đưa ra những nhận xét thẳng thắn, giúp nhóm nhìn lại cách đặt bài toán và cách đánh giá kết quả. Những góp ý đó là lý do đề tài được thu gọn và làm lại theo hướng sát thực tế hơn.")
P("Chúng em cũng cảm ơn nhà trường và Viện Công nghệ Thông tin và Điện, Điện tử đã tạo điều kiện để sinh viên vận dụng kiến thức vào một bài toán thực tế, đồng thời rèn luyện kỹ năng làm việc nhóm và trình bày báo cáo khoa học. Xin cảm ơn các nhóm tác giả đã công bố hai bộ dữ liệu ảnh lá sầu riêng được dùng trong đề tài.")
pagebreak()

# ---------------- MỤC LỤC ----------------
H("Mục lục", 1)
tp = d.add_paragraph(); field(tp, 'TOC \\o "1-3" \\h \\z \\u')
pagebreak()

H("Danh mục từ viết tắt", 1)
TABLE("Các thuật ngữ và từ viết tắt dùng trong báo cáo", ["Từ viết tắt", "Ý nghĩa"],
      [["AdamW", "Adam with decoupled Weight decay: bộ tối ưu dùng trong huấn luyện"], ["CC BY 4.0", "Giấy phép Creative Commons Attribution 4.0"],
       ["CPU / GPU", "Bộ xử lý trung tâm / bộ xử lý đồ họa"], ["DOI", "Digital Object Identifier: mã định danh tài liệu số"],
       ["F1", "Trung bình điều hòa của precision và recall; macro F1 là trung bình F1 của các lớp"], ["Fine-tuning", "Huấn luyện tinh chỉnh mô hình đã pretrain"],
       ["Few-shot", "Học ít mẫu: nhận lớp mới từ rất ít ảnh mẫu"], ["ImageNet", "Bộ dữ liệu ảnh quy mô lớn dùng để pretrain mô hình"],
       ["Kappa", "Cohen's Kappa: độ đồng thuận giữa hai người gán nhãn"], ["MSSV", "Mã số sinh viên"],
       ["N-way K-shot", "Episode có N lớp, mỗi lớp K ảnh mẫu"], ["Pseudo-label", "Nhãn giả: nhãn do mô hình tự dự đoán cho ảnh chưa gán nhãn"], ["SHA-256", "Hàm băm dùng để phát hiện ảnh trùng chính xác"]],
      widths=[3.5, 12])
pagebreak()
H("Danh mục hình", 1)
lf = d.add_paragraph(); field(lf, 'TOC \\h \\z \\c "Hinh"')
H("Danh mục bảng", 1)
lt = d.add_paragraph(); field(lt, 'TOC \\h \\z \\c "Bang"')
pagebreak()

# ---------------- TÓM TẮT ----------------
H("Tóm tắt", 1)
P("Giai đoạn đầu của đề tài so sánh học ít mẫu (Prototypical Network) và học chuyển giao (Fine-tuning) khi huấn luyện trên ảnh cà chua, khoai tây (PlantVillage) rồi đánh giá trên các lớp bệnh lá sầu riêng chưa từng thấy. Độ chính xác chỉ đạt khoảng 30–54%, quá thấp để áp dụng thực tế. Báo cáo này trình bày phần làm lại: thu hẹp đề tài về nhận dạng bệnh lá sầu riêng và thay PlantVillage bằng hai bộ dữ liệu lá sầu riêng, gồm bộ Kaggle (4.437 ảnh, 5 lớp) và bộ Mendeley (2.595 ảnh, 6 lớp).")
P("Nhóm kiểm tra sự trùng lặp giữa hai bộ (121 ảnh Blight trùng nhau, cộng 2 ảnh trùng nội bộ) và loại chúng trước khi huấn luyện. Mô hình MobileNetV2 pretrained ImageNet được fine-tune toàn mạng theo ba cấu hình: chỉ Kaggle, chỉ Mendeley và gộp hai bộ. Trên tập test cùng nguồn, ba cấu hình đạt 93,7%, 96,1% và 94,5% (mô hình gộp: 94,7% trên Kaggle, 94,0% trên Mendeley). Tuy nhiên khi đổi nguồn ảnh, mô hình chỉ huấn luyện trên Mendeley chỉ đạt 32,0% trên ảnh Kaggle, còn mô hình chỉ huấn luyện trên Kaggle đạt 76,2% trên ảnh Mendeley (4 lớp chung). Kết quả cho thấy khoảng cách giữa các nguồn ảnh là nguyên nhân chính khiến mô hình khó dùng ngoài thực tế, và việc gộp nhiều nguồn là một hướng khắc phục.")
P("Kết quả few-shot (1, 5, 10 ảnh mẫu mỗi lớp) trên Mendeley đạt 56,8%, 71,9% và 76,7% khi dùng đặc trưng từ mô hình huấn luyện trên Kaggle. Thí nghiệm học bán giám sát (huấn luyện trên Mendeley, thêm 1.200 ảnh Kaggle chưa gán nhãn, 4 lớp chung) cho thấy chỉ tự gán nhãn thì không cải thiện (27,4% trên Kaggle sau 3 vòng, trong khi nhánh đối chứng tự dao động 29–40%); khi mỗi vòng có thêm 150 ảnh độ tin cậy thấp nhất được gán nhãn đúng (mô phỏng người gán lại), accuracy trên Kaggle tăng từ 35,0% lên 81,1%. Đề tài kèm một ứng dụng minh họa Streamlit. Báo cáo nêu rõ các giới hạn: chưa có nguồn dữ liệu thứ ba độc lập, ngưỡng độ tin cậy chưa loại được ảnh ngoài phạm vi, và chỉ mô hình gộp được chạy lại nhiều seed (4 seed: " + ms("tong") + " tổng).")
P("**Từ khóa:** nhận dạng bệnh lá sầu riêng, học chuyển giao, MobileNetV2, dịch chuyển miền dữ liệu, đánh giá ngoài miền.", indent=False)
pagebreak()

# ---------------- 1 GIỚI THIỆU ----------------
H("1. Giới thiệu", 1)
H("1.1. Bối cảnh", 2)
P("Sầu riêng là cây ăn quả có giá trị xuất khẩu lớn của Việt Nam, nhưng bệnh trên lá (đốm tảo, cháy lá, thán thư và các bệnh khác) làm giảm sức khỏe cây và năng suất. Việc phát hiện bệnh hiện chủ yếu dựa vào quan sát của người làm vườn, vì vậy kết quả phụ thuộc vào kinh nghiệm và điều kiện ánh sáng. Một công cụ nhận dạng bệnh từ ảnh chụp bằng điện thoại có thể hỗ trợ chẩn đoán sớm nếu đủ chính xác và đáng tin cậy.")
H("1.2. Vấn đề của giai đoạn trước", 2)
P("Ở giai đoạn đầu, nhóm so sánh học ít mẫu (Prototypical Network, backbone Conv-4) và học chuyển giao (Fine-tuning MobileNetV2) theo cấu hình 5-way 1/5/10-shot. Hai mô hình được huấn luyện hoặc chọn trên ảnh cà chua, khoai tây và ớt chuông (PlantVillage), sau đó đánh giá trên sáu lớp lá sầu riêng mà mô hình chưa từng thấy. Với giao thức đã lọc ảnh trùng, độ chính xác chỉ khoảng 30%, 40–47% và 44–54% ở 1, 5 và 10 ảnh mẫu.")
P("Khi báo cáo, thầy nhận xét con số này quá thấp để áp dụng thực tế. Nhóm nhận thấy nguyên nhân gốc nằm ở thiết kế: mô hình học từ cây khác rồi phải nhận bệnh của cây mới, tức là một bài toán chuyển miền rất khó, trong khi mục tiêu cuối cùng chỉ là nhận dạng bệnh trên lá sầu riêng.")
H("1.3. Mục tiêu", 2)
BUL(["Thu gọn đề tài về nhận dạng bệnh lá sầu riêng và thay dữ liệu huấn luyện PlantVillage bằng dữ liệu lá sầu riêng.",
     "Huấn luyện mô hình học chuyển giao trên bộ Kaggle, bộ Mendeley và hai bộ gộp lại; đo độ chính xác trong miền.",
     "Đo độ chính xác ngoài miền (huấn luyện trên một nguồn, kiểm tra trên nguồn kia) để biết mô hình có dùng được khi ảnh đến từ nơi khác.",
     "Đánh giá few-shot (1, 5, 10 ảnh mẫu) để trả lời câu hỏi mô hình học trên dữ liệu sầu riêng có giúp nhận lớp mới nhanh hơn không.",
     "Xây dựng ứng dụng minh họa và nêu rõ giới hạn của kết quả."])
H("1.4. Phạm vi và giới hạn", 2)
P("Đề tài chỉ xét ảnh lá sầu riêng thuộc các lớp có trong hai bộ dữ liệu. Ứng dụng không có cơ chế loại ảnh ngoài phạm vi đáng tin cậy. Các kết quả chạy trên CPU với seed 42; riêng mô hình gộp được huấn luyện lại với 4 seed (42–45) để đo dao động giữa các lần huấn luyện, các mô hình và thí nghiệm khác chỉ chạy một lần. Không có nguồn dữ liệu thứ ba nên chưa kiểm tra được mô hình gộp ngoài miền.")
H("1.5. Đóng góp chính", 2)
BUL(["Phát hiện và loại 121 ảnh Blight trùng nhau giữa hai bộ dữ liệu, tránh rò rỉ khi đánh giá.",
     "Thiết kế phép đánh giá ngoài miền hai chiều trên 4 lớp chung, cho thấy mô hình huấn luyện trên một nguồn có thể giảm từ 96% xuống 32%.",
     "Huấn luyện mô hình gộp 7 lớp đạt 94–95% trên cả hai nguồn với một mô hình duy nhất.",
     "Đối chứng few-shot giữa đặc trưng huấn luyện trên Kaggle và đặc trưng chỉ pretrain ImageNet.",
     "Thử học bán giám sát theo gợi ý của thầy, có nhánh đối chứng chạy hai lần, cho thấy tự gán nhãn không đủ khi lệch miền lớn, còn có người gán lại thì cải thiện rõ.",
     "Trình bày trung thực các giới hạn và hướng khắc phục."])

# ---------------- 2 CƠ SỞ LÝ THUYẾT ----------------
H("2. Cơ sở lý thuyết", 1)
H("2.1. Học chuyển giao và fine-tuning", 2)
P("Học chuyển giao tận dụng tri thức đã học từ một bài toán nguồn để giải bài toán đích có ít dữ liệu hơn [Pan & Yang, 2010]. Trong thị giác máy tính, cách phổ biến là dùng mạng đã huấn luyện trên ImageNet làm điểm khởi đầu, thay lớp phân loại cuối bằng lớp mới và huấn luyện tiếp (fine-tuning) trên dữ liệu đích. Có hai mức: chỉ huấn luyện lớp cuối (đặc trưng đóng băng) hoặc huấn luyện toàn mạng với tốc độ học nhỏ. Báo cáo này dùng mức thứ hai cho việc huấn luyện chính, và dùng đặc trưng đóng băng cho thí nghiệm few-shot.")
H("2.2. MobileNetV2", 2)
P("MobileNetV2 là kiến trúc nhẹ dùng tích chập tách theo chiều sâu và khối residual đảo ngược [Sandler và cs., 2018]. Mạng có khoảng 3,5 triệu tham số và vector đặc trưng 1.280 chiều trước lớp phân loại, phù hợp với việc huấn luyện trên CPU. Nhóm dùng trọng số pretrained ImageNet của torchvision.")
H("2.3. Hàm mất mát và tối ưu", 2)
P("Mô hình được huấn luyện với hàm mất mát cross-entropy có làm mịn nhãn (label smoothing 0,05) [Müller và cs., 2019] để giảm hiện tượng quá tự tin. Bộ tối ưu là AdamW [Loshchilov & Hutter, 2019] với tốc độ học ban đầu 3×10⁻⁴, weight decay 10⁻⁴ và lịch giảm cosine theo số epoch. Biểu đồ loss ở Mục 5.1 là giá trị cross-entropy trung bình trên tập huấn luyện sau mỗi epoch.")
H("2.4. Thước đo đánh giá", 2)
P("Báo cáo dùng accuracy (tỷ lệ ảnh đúng), macro F1 (trung bình F1 của các lớp, không phụ thuộc số ảnh mỗi lớp) và ma trận nhầm lẫn. Khi một tập test không chứa đủ mọi lớp (ví dụ tập Kaggle không có Colletotrichum), macro F1 trên 7 lớp bị kéo thấp do lớp rỗng, nên báo cáo chủ yếu dùng accuracy theo từng nguồn.")
H("2.5. Few-shot và dịch chuyển miền", 2)
P("Trong thiết lập N-way K-shot, mỗi episode có N lớp, mỗi lớp K ảnh mẫu (support) và một số ảnh cần phân loại (query). Prototypical Network gán query cho lớp có prototype (trung bình embedding của ảnh mẫu) gần nhất [Snell và cs., 2017]. Báo cáo dùng thêm hồi quy logistic huấn luyện trên K ảnh mẫu. Dịch chuyển miền (domain shift) xảy ra khi phân phối ảnh lúc huấn luyện khác phân phối lúc dùng (ánh sáng, thiết bị chụp, nền, khoảng cách chụp), làm độ chính xác giảm dù lớp bệnh giống nhau.")

# ---------------- 3 DỮ LIỆU ----------------
H("3. Dữ liệu và tiền xử lý", 1)
H("3.1. Bộ dữ liệu Kaggle", 2)
P("Bộ \"Durian Leaf Disease Dataset\" (Kaggle) có 4.437 ảnh thuộc 5 lớp: Algal leaf spot, Allocaridara attack, Healthy leaf, Leaf blight và Phomopsis leaf spot [Nguyen-Tat & Nong, 2026]. Ảnh được chụp bằng điện thoại tại các vườn ở miền Đông Nam Bộ trong nhiều điều kiện ánh sáng, thời tiết và góc chụp, kích thước 224×224. Hai chuyên gia gán nhãn độc lập, độ đồng thuận Cohen's Kappa đạt 98,25%, các mẫu bất đồng bị loại. Dữ liệu chia sẵn 70/10/20 và dùng giấy phép CC BY 4.0. Cần lưu ý Allocaridara là tổn thương do côn trùng (rầy), không phải bệnh nấm.")
H("3.2. Bộ dữ liệu Mendeley", 2)
P("Bộ \"A Durian Leaf Image Dataset of Common Diseases in Vietnam for Agricultural Diagnosis\" (Mendeley Data) có 2.595 ảnh, 6 lớp: Algal, Blight, Colletotrichum, Healthy, Phomopsis và Rhizoctonia, thu thập tại Bình Phước và Tiền Giang, kích thước 400×400, có chia sẵn train/val/test. Nhóm đã dùng bộ này ở giai đoạn trước làm tập đánh giá.")
TABLE("Số ảnh mỗi lớp của hai bộ dữ liệu (trước khi khử trùng)", ["Lớp", "Kaggle", "Mendeley"],
      [["Algal", "733", "462"], ["Allocaridara", "913", "–"], ["Blight", "937", "440"], ["Colletotrichum", "–", "400"], ["Healthy", "976", "484"],
       ["Phomopsis", "878", "411"], ["Rhizoctonia", "–", "398"], ["Tổng", "4.437", "2.595"]], widths=[5, 4, 4], bold_last=True)
FIGURE("dataset.png", "Số ảnh theo lớp; phần đỏ là ảnh Kaggle bị loại vì trùng.", 14.5)
P("Hai bộ có 4 lớp chung (Algal, Blight, Healthy, Phomopsis). Colletotrichum và Rhizoctonia chỉ có ở Mendeley, Allocaridara chỉ có ở Kaggle. Ảnh hai bộ khác nhau rõ rệt về phong cách chụp (Hình 8 ở Mục 5.4).")
H("3.3. Kiểm tra ảnh trùng lặp", 2)
P("Để tránh rò rỉ dữ liệu, nhóm so sánh từng cặp ảnh bằng độ tương quan giữa phiên bản xám 24×24 đã chuẩn hóa, cách này vẫn nhận ra cùng một ảnh dù khác kích thước. Kết quả tách bạch: 121 ảnh Mendeley khớp (tương quan ≥ 0,98) với ảnh trong bộ Kaggle, trong khi mọi cặp còn lại đều ≤ 0,8. Nhóm thử thêm lật ngang, lật dọc và xoay 90° và không tìm thấy cặp nào khác.")
BUL(["Cả 121 ảnh trùng đều thuộc lớp **Blight** và nằm trong tập train của Kaggle. Phía Mendeley chúng nằm ở train (89), val (15) và test (17).",
     "Bên trong Kaggle có 1 nhóm ảnh trùng chính xác (SHA-256) và vài cặp gần trùng; sau khi lọc có 2 ảnh bị loại.",
     "Bên trong Mendeley có 35 ảnh gần trùng ảnh khác (12 ở train, 10 ở val, 13 ở test); nhóm giữ nguyên ở train nhưng loại khỏi val và test của mô hình gộp và của bước đánh giá lại mô hình chỉ Mendeley (lần huấn luyện đầu của mô hình chỉ Mendeley chọn epoch trên tập val chưa lọc, 387 ảnh)."])
TABLE("Số ảnh sau khi khử trùng", ["Nguồn", "Train", "Val", "Test", "Tổng"],
      [["Kaggle (5 lớp)", "2.983", "443", "888", "4.314"], ["Mendeley (6 lớp)", "1.814", "377", "381", "2.572"]], widths=[5, 2.5, 2.5, 2.5, 2.5])
H("3.4. Tiền xử lý và tăng cường dữ liệu", 2)
P("Mọi ảnh được đưa về 224×224 và chuẩn hóa theo thống kê ImageNet. Khi huấn luyện dùng cắt ngẫu nhiên theo tỷ lệ (0,6–1,0), lật ngang và thay đổi độ sáng, tương phản, độ bão hòa (cường độ 0,3/0,3/0,2). Với mô hình gộp, nhóm tăng cường độ thay đổi màu lên 0,5/0,5/0,4 (kèm sắc độ 0,05) để mô hình bớt phụ thuộc vào ánh sáng của từng nguồn. Khi đánh giá chỉ đổi kích thước và chuẩn hóa.")

# ---------------- 4 PHƯƠNG PHÁP ----------------
H("4. Phương pháp", 1)
H("4.1. Quy trình tổng thể", 2)
FIGURE("pipeline.png", "Quy trình: chuẩn bị dữ liệu, huấn luyện, đánh giá và demo.", 15)
H("4.2. Cấu hình huấn luyện", 2)
TABLE("Cấu hình huấn luyện (giống nhau cho ba mô hình, trừ ghi chú)", ["Thành phần", "Giá trị"],
      [["Kiến trúc", "MobileNetV2, pretrained ImageNet, thay lớp phân loại cuối"], ["Huấn luyện", "Fine-tune toàn mạng"],
       ["Tối ưu", "AdamW, lr 3×10⁻⁴, weight decay 10⁻⁴, cosine"], ["Hàm mất mát", "Cross-entropy, label smoothing 0,05"],
       ["Batch / epoch", "32 / 6"], ["Chọn mô hình", "Epoch có accuracy validation cao nhất"],
       ["Seed", "42; mô hình gộp chạy thêm 43, 44, 45"], ["Phần cứng", "CPU; 4–13 phút mỗi epoch"]], widths=[4.5, 11])
H("4.3. Ba mô hình", 2)
TABLE("Ba cấu hình huấn luyện", ["Mô hình", "Dữ liệu huấn luyện", "Số lớp", "Số ảnh train"],
      [["Chỉ Kaggle", "Kaggle (đã khử trùng)", "5", "2.983"], ["Chỉ Mendeley", "Mendeley", "6", "1.814"],
       ["Gộp 2 bộ", "Kaggle + Mendeley", "7", "4.797"]], widths=[4, 5, 2.5, 3.5])
H("4.4. Giao thức đánh giá", 2)
BUL(["**Trong miền:** mỗi mô hình được test trên tập test cùng nguồn (đã loại ảnh gần trùng của Mendeley).",
     "**Ngoài miền:** huấn luyện trên một nguồn, test trên nguồn kia chỉ với 4 lớp chung; mô hình có nhiều lớp hơn được che bớt đầu ra. Ảnh Blight trùng nhau bị loại ở phía test (còn 3.403 ảnh Kaggle và 1.676 ảnh Mendeley).",
     "**Few-shot:** dùng đặc trưng 1.280 chiều. Support lấy từ Mendeley train, query (15 ảnh mỗi lớp) từ Mendeley test, 600 episode, seed 42, 6-way. Hai bộ phân loại: prototype và hồi quy logistic. Đối chứng là cùng backbone chỉ pretrain ImageNet."])

# ---------------- 5 KẾT QUẢ ----------------
H("5. Thực nghiệm và kết quả", 1)
H("5.1. Quá trình huấn luyện", 2)
P("Hình 3 cho thấy loss huấn luyện giảm đều ở cả ba mô hình, từ 0,68–0,88 ở epoch 1 xuống 0,29–0,36 ở epoch 6, trong khi accuracy validation tăng từ khoảng 90% lên 94–96%. Loss của mô hình gộp cao hơn vì dùng tăng cường màu mạnh hơn và có nhiều lớp hơn. Loss chưa hội tụ hoàn toàn sau 6 epoch, nên có thể huấn luyện thêm, nhưng accuracy validation đã đi ngang ở các epoch cuối.")
FIGURE("loss.png", "Loss huấn luyện và accuracy validation theo epoch của ba mô hình.", 15.5)
TABLE("Loss huấn luyện và accuracy validation theo epoch (%)", ["Epoch", "Kaggle loss", "Kaggle val", "Mendeley loss", "Mendeley val", "Gộp loss", "Gộp val"],
      [["1", "0,802", "89,8", "0,685", "92,2", "0,876", "89,5"], ["2", "0,468", "92,8", "0,406", "92,5", "0,557", "92,7"],
       ["3", "0,390", "94,1", "0,353", "94,3", "0,466", "93,4"], ["4", "0,362", "95,0", "0,322", "95,1", "0,421", "94,5"],
       ["5", "0,327", "93,9", "0,304", "95,9", "0,374", "95,4"], ["6", "0,301", "94,4", "0,294", "95,6", "0,359", "95,2"]], size=10,
      widths=[1.6, 2.4, 2.2, 2.6, 2.4, 2.2, 2.0])
P("Ghi chú: accuracy validation của mô hình chỉ Mendeley tính trên toàn bộ tập val gốc (387 ảnh, chưa loại ảnh gần trùng). Nhóm chỉ ghi lại loss huấn luyện và accuracy validation, không ghi loss validation. Vì vậy biểu đồ không cho thấy trực tiếp mức quá khớp; chỉ có thể nhận xét qua accuracy validation, vốn ổn định hoặc tăng nhẹ.", italic=True, indent=False)
H("5.2. Kết quả trong miền", 2)
TABLE("Kết quả trên tập test cùng nguồn (seed 42; khoảng tin cậy Wilson 95% chỉ tính sai số do cỡ mẫu test)", ["Mô hình", "Tập test", "Số ảnh test", "Accuracy", "Khoảng tin cậy 95%", "Macro F1"],
      [["Chỉ Kaggle", "Kaggle (5 lớp)", "888", "93,7%", "91,9–95,1%", "0,936"], ["Chỉ Mendeley", "Mendeley (6 lớp)", "381", "96,1%", "93,6–97,6%", "0,959"],
       ["Gộp 2 bộ", "Kaggle", "888", "94,7%", "93,0–96,0%", "–"], ["Gộp 2 bộ", "Mendeley", "381", "94,0%", "91,1–95,9%", "0,937"], ["Gộp 2 bộ", "Cả hai", "1.269", "94,5%", "–", "0,939"]],
      widths=[2.8, 3.2, 2.2, 2.2, 3.2, 2.2], size=10)
FIGURE("indomain.png", "Accuracy trong miền của các mô hình (seed 42).", 12.5)
P("Để đo mức dao động giữa các lần huấn luyện, nhóm huấn luyện lại mô hình gộp với 3 seed khác (43, 44, 45), giữ nguyên dữ liệu và cấu hình. Seed thay đổi khởi tạo lớp phân loại cuối, thứ tự ảnh trong batch và tăng cường dữ liệu.")
TABLE("Mô hình gộp qua 4 seed, accuracy trên tập test cùng nguồn", ["Seed", "Kaggle (888 ảnh)", "Mendeley (381 ảnh)", "Cả hai (1.269 ảnh)", "Macro F1 (cả hai)"],
      [[str(k), pc(v["kaggle"]) + "%", pc(v["mendeley"]) + "%", pc(v["tong"]) + "%", f3(v["macro_f1"])] for k, v in sorted(SEEDS["per_seed"].items(), key=lambda x: int(x[0]))]
      + [["Trung bình ± độ lệch chuẩn", ms("kaggle"), ms("mendeley"), ms("tong"), f3(SEEDS["summary"]["macro_f1"]["mean"]) + " ± " + f3(SEEDS["summary"]["macro_f1"]["std"])]],
      widths=[4.2, 2.8, 2.8, 2.8, 2.8], size=10, bold_last=True)
P("Qua 4 seed, mô hình gộp đạt " + ms("kaggle") + " trên Kaggle, " + ms("mendeley") + " trên Mendeley và " + ms("tong") + " tính chung (độ lệch chuẩn mẫu, n = 4). Seed 42, dùng ở các phần khác của báo cáo, đạt " + pc(SEEDS["per_seed"]["42"]["tong"]) + "% tính chung; 4 lần chạy nằm trong khoảng "
  + pc(SEEDS["summary"]["tong"]["min"]) + "–" + pc(SEEDS["summary"]["tong"]["max"]) + "%. Với độ lệch chuẩn " + sd("kaggle") + " điểm (Kaggle) và " + sd("mendeley") + " điểm (Mendeley), chênh lệch nhỏ hơn khoảng hai lần độ lệch chuẩn giữa các mô hình có thể chỉ do khác lần huấn luyện. Riêng trên Mendeley, seed 42 (" + pc(SEEDS["per_seed"]["42"]["mendeley"]) + "%) là lần thấp nhất trong 4 lần, nên các con số của mô hình gộp ở những bảng khác hơi thấp hơn mức trung bình. Hai mô hình đơn nguồn và các thí nghiệm khác chưa được chạy lại nhiều seed.")
P("Cả ba mô hình đạt 93–96% trên tập test cùng nguồn. Các khoảng tin cậy chồng lên nhau (ví dụ 93,0–96,0% và 91,1–95,9% của mô hình gộp), nên chênh lệch giữa các mô hình chưa có ý nghĩa thống kê. Mô hình riêng Mendeley cao nhất (96,1%, tính trên 381 ảnh test sau khi loại 13 ảnh gần trùng nội bộ) vì tập test của nó có ít lớp hơn và cùng phong cách ảnh với tập huấn luyện. Mô hình gộp thấp hơn một chút trên Mendeley (94,0%) nhưng không còn thua hẳn khi gặp ảnh kiểu Kaggle (Mục 5.4). Macro F1 của riêng Kaggle trong mô hình gộp không báo cáo vì hai lớp Colletotrichum và Rhizoctonia không có ảnh trong tập test Kaggle.")
H("5.3. Phân tích lỗi", 2)
FIGURE("cm_merged_kaggle.png", "Ma trận nhầm lẫn của mô hình gộp trên tập test Kaggle.", 11)
FIGURE("cm_merged_mendeley.png", "Ma trận nhầm lẫn của mô hình gộp trên tập test Mendeley.", 11)
P("Trên Kaggle, lớp Healthy gần như không nhầm (194/195) còn Phomopsis nhầm nhiều nhất, rải sang Algal, Blight và Healthy (đúng 156/176). Trên Mendeley, lỗi tập trung ở bộ ba Blight, Colletotrichum và Rhizoctonia: 6 trên 57 ảnh Colletotrichum bị nhận nhầm (3 sang Phomopsis, 2 sang Blight, 1 sang Healthy), 9 trên 63 ảnh Blight bị nhận sang Colletotrichum (4), Rhizoctonia (3) hoặc Phomopsis (2), và 5 trên 61 ảnh Rhizoctonia bị nhận sang Blight (4) hoặc Phomopsis (1).")
H("5.4. Kiểm tra ngoài miền", 2)
P("Đây là thí nghiệm quan trọng nhất của báo cáo. Nhóm huấn luyện trên một nguồn rồi kiểm tra trên nguồn còn lại, chỉ với 4 lớp chung, và đã loại các ảnh Blight trùng nhau.")
TABLE("Accuracy khi đổi nguồn ảnh (4 lớp chung)", ["Huấn luyện trên", "Test trên", "Số ảnh test", "Accuracy", "Macro F1"],
      [["Mendeley", "Kaggle", "3.403", "32,0%", "0,248"], ["Kaggle", "Mendeley", "1.676", "76,2%", "0,729"]], widths=[3.5, 3, 3, 3, 3])
FIGURE("crossdomain.png", "Accuracy ngoài miền, tổng và theo lớp.", 15.5)
P("Mô hình huấn luyện trên Mendeley gần như sụp đổ khi gặp ảnh Kaggle: nó gán nhãn Blight cho 98% ảnh Blight nhưng chỉ nhận đúng 10–12% ảnh Algal, Healthy và Phomopsis, phần lớn còn lại bị gán nhầm là Blight (ví dụ 806 trên 976 ảnh Healthy). Chiều ngược lại tốt hơn (76,2%) nhưng Blight chỉ đạt 57% và Phomopsis 45%.")
FIGURE("healthy_compare.png", "Ảnh lá khỏe mạnh ở hai bộ: ảnh Mendeley (hàng trên) tối hơn, chụp cận; ảnh Kaggle (hàng dưới) sáng hơn, nhiều lá.", 15)
P("Hình 8 cho thấy phong cách chụp hai bộ khác nhau rõ rệt. Nhóm cho rằng mô hình học theo ánh sáng và bối cảnh chụp của từng nguồn thay vì chỉ dấu hiệu bệnh. Đây là giả thuyết dựa trên quan sát và kết quả trên, chưa được kiểm chứng riêng (ví dụ bằng việc chuẩn hóa màu hoặc phân tích vùng ảnh mô hình chú ý).")
P("Ý nghĩa thực tế: độ chính xác 94–96% trong miền không đảm bảo mô hình hoạt động tốt với ảnh của người dùng chụp ở vườn khác. Bộ Kaggle đa dạng hơn nên chuyển sang Mendeley tốt hơn chiều ngược lại.")
H("5.5. Kết quả few-shot", 2)
TABLE("Few-shot trên Mendeley (6-way, 600 episode), accuracy %", ["Phương pháp", "1 mẫu", "5 mẫu", "10 mẫu"],
      [["Prototype, backbone Kaggle", "56,8", "68,8", "71,0"], ["Hồi quy logistic, backbone Kaggle", "56,8", "71,9", "76,7"],
       ["Prototype, chỉ ImageNet", "40,2", "62,8", "68,7"], ["Hồi quy logistic, chỉ ImageNet", "40,2", "65,1", "72,1"]], widths=[7, 2.8, 2.8, 2.8])
FIGURE("fewshot.png", "Few-shot trên Mendeley; thanh sai số là khoảng tin cậy 95% trên 600 episode.", 12)
P("Ở 1 mẫu, hồi quy logistic cần ít nhất hai mẫu mỗi lớp nên dùng lại prototype, vì vậy hai dòng giống nhau. Đặc trưng từ mô hình huấn luyện trên Kaggle giúp rõ rệt ở 1 mẫu (tăng khoảng 17 điểm) và khá ở 5 mẫu (tăng khoảng 7 điểm so với chỉ ImageNet), nhưng ở 10 mẫu chỉ hơn khoảng 4,6 điểm. Khi tách theo nhóm lớp, lợi ích đến chủ yếu từ 4 lớp chung với Kaggle (78,0% so với 70,7% ở 10 mẫu). Với hai lớp chỉ có ở Mendeley, hai backbone gần như hòa (74,1% so với 75,0%); do chỉ có 2 lớp nên số đo này nhiễu. So với kết quả giai đoạn trước (khoảng 54% ở 10 mẫu), mức tăng chủ yếu đến từ backbone MobileNetV2 và ảnh 224×224 chứ không riêng từ bộ dữ liệu Kaggle.")
H("5.6. Thí nghiệm học bán giám sát", 2)
P("Theo gợi ý của thầy, nhóm thử dùng ảnh chưa gán nhãn để cải thiện mô hình ở chiều ngoài miền khó nhất (huấn luyện Mendeley, test Kaggle). Thiết lập trên 4 lớp chung: dữ liệu có nhãn là 1.256 ảnh Mendeley train; dữ liệu không nhãn là 1.200 ảnh Kaggle train (300 ảnh mỗi lớp, đã loại ảnh trùng); test trên 705 ảnh Kaggle test và 263 ảnh Mendeley test (đã loại ảnh gần trùng). Vòng 0 huấn luyện 5 epoch trên dữ liệu có nhãn; sau đó mỗi vòng fine-tune tiếp 3 epoch (lr 1,5×10⁻⁴), tổng 3 vòng, cùng điểm xuất phát cho mọi nhánh:")
BUL(["**Đối chứng:** chỉ huấn luyện tiếp trên dữ liệu có nhãn, cùng số epoch, để tách phần thay đổi do huấn luyện thêm.",
     "**Tự gán nhãn (pseudo):** thêm các ảnh Kaggle mà mô hình dự đoán với độ tin cậy ≥ 0,9, dùng nhãn mô hình tự gán.",
     "**Người gán lại (human):** như trên, và mỗi vòng thêm 150 ảnh có độ tin cậy thấp nhất với nhãn đúng. Đây là mô phỏng: nhãn đúng lấy từ thư mục của bộ Kaggle, không có người gán thật."])
TABLE("Accuracy trên Kaggle test (705 ảnh, 4 lớp chung) qua các vòng; trong ngoặc là khoảng tin cậy Wilson 95%", ["Nhánh", "Vòng 0", "Vòng 1", "Vòng 2", "Vòng 3"],
      [["Đối chứng (lần 1)", "35,0%", "35,0%", "36,7%", "40,3% (36,7–43,9)"], ["Đối chứng (lần 2)", "35,0%", "36,5%", "29,1%", "33,2% (29,8–36,8)"],
       ["Tự gán nhãn", "35,0%", "31,5%", "28,4%", "27,4% (24,2–30,8)"], ["Người gán lại", "35,0%", "62,0%", "73,3%", "81,1% (78,1–83,9)"]],
      widths=[3.6, 2, 2, 2, 4.2], size=10)
TABLE("Nhãn giả và kích thước tập huấn luyện theo vòng", ["Nhánh", "Vòng", "Số ảnh nhãn giả", "Tỷ lệ nhãn giả đúng", "Ảnh người gán (cộng dồn)", "Tập huấn luyện"],
      [["Tự gán nhãn", "1", "260", "58,5%", "0", "1.516"], ["Tự gán nhãn", "2", "498", "38,0%", "0", "1.754"], ["Tự gán nhãn", "3", "830", "30,6%", "0", "2.086"],
       ["Người gán lại", "1", "260", "58,5%", "150", "1.666"], ["Người gán lại", "2", "418", "64,1%", "300", "1.974"], ["Người gán lại", "3", "460", "74,1%", "450", "2.166"]],
      widths=[3, 1.4, 2.6, 2.8, 3.2, 2.6], size=10)
FIGURE("semisup.png", "Học bán giám sát: accuracy trên Kaggle test theo vòng (vùng mờ là khoảng tin cậy 95%) và tỷ lệ nhãn giả đúng.", 15.5)
P("Nhánh đối chứng chạy hai lần, cùng điểm xuất phát và cùng cấu hình (lần 2 chạy trên máy khác), cho kết quả vòng 3 là 40,3% và 33,2%. Như vậy riêng việc huấn luyện thêm đã làm accuracy trên Kaggle dao động khoảng 29–40%, nên mọi nhánh phải so với khoảng này chứ không so với vòng 0.")
P("Tự gán nhãn không cải thiện: accuracy giảm còn 27,4%, nằm ở mép dưới khoảng dao động của đối chứng. Nguyên nhân thấy rõ ở tỷ lệ nhãn giả đúng: mô hình huấn luyện trên Mendeley vốn chỉ đạt 35% trên Kaggle, nên dù chỉ giữ dự đoán tin cậy ≥ 0,9, chỉ 58,5% nhãn giả đúng ở vòng 1. Huấn luyện trên nhãn sai làm mô hình càng tự tin vào lỗi của mình, nên số nhãn giả tăng (260 → 830) trong khi tỷ lệ đúng giảm (58,5% → 30,6%). Khi lệch miền lớn, độ tin cậy softmax không phải tín hiệu đủ tốt để tự gán nhãn, giống kết luận ở Mục 6.2.")
P("Khi có người gán lại, accuracy trên Kaggle tăng lên 62,0%, 73,3% rồi 81,1%, khoảng tin cậy ở vòng 3 (78,1–83,9%) tách hẳn khỏi đối chứng; nhãn giả cũng đúng hơn qua từng vòng (58,5% → 74,1%). Accuracy trên Mendeley test giữ ở 98,5–99,6% ở mọi nhánh, tức mô hình không quên miền cũ.")
P("Cần đọc kết quả này thận trọng. Sau 3 vòng, nhánh người gán lại đã dùng 450 ảnh Kaggle có nhãn đúng (37,5% tập không nhãn), nên phần lớn mức tăng có thể đến từ việc có dữ liệu có nhãn của miền đích chứ chưa chắc từ cách chọn ảnh khó hay từ nhãn giả. Nhóm chưa chạy nhánh so sánh gán nhãn 450 ảnh chọn ngẫu nhiên, và mỗi nhánh chỉ chạy một lần. Việc \"người gán lại\" là mô phỏng bằng nhãn có sẵn; với người gán thật sẽ có sai sót và tốn công.", italic=False)
H("5.7. Những điều số liệu chưa chứng minh", 2)
BUL(["Chưa chứng minh mô hình gộp dùng được với ảnh của nguồn thứ ba; chỉ có bằng chứng ngoài miền cho mô hình đơn nguồn.",
     "Chỉ mô hình gộp được chạy 4 seed (độ lệch chuẩn " + sd("kaggle") + " điểm trên Kaggle, " + sd("mendeley") + " điểm trên Mendeley); hai mô hình đơn nguồn chỉ một seed, nên chênh lệch dưới 1–2 điểm giữa các mô hình (ví dụ 94,0% và 96,1%) không nên diễn giải mạnh.",
     "Giả thuyết về ánh sáng và nền chưa được kiểm chứng riêng.",
     "Các lớp Colletotrichum, Rhizoctonia chỉ có một nguồn nên khả năng tổng quát hóa của hai lớp này chưa được kiểm tra.",
     "Học bán giám sát: chưa tách được phần đóng góp của cách chọn ảnh khó so với việc có thêm 450 ảnh có nhãn của miền đích (chưa có nhánh gán nhãn ngẫu nhiên); mỗi nhánh chỉ chạy một lần."])

# ---------------- 6 DEMO ----------------
H("6. Ứng dụng minh họa", 1)
H("6.1. Chức năng", 2)
P("Ứng dụng Streamlit dùng mô hình gộp 7 lớp. Người dùng upload ảnh lá và nhận lớp dự đoán, độ tin cậy và biểu đồ xác suất của 7 lớp. Ứng dụng có tab ảnh mẫu lấy từ tập test, tab lịch sử và tab ghi giới hạn cùng kết quả đánh giá. Ứng dụng chạy độc lập trên máy cá nhân, không cần dữ liệu huấn luyện (thư mục demo khoảng 11 MB).")
H("6.2. Ngưỡng cảnh báo độ tin cậy", 2)
P("Ứng dụng hiện cảnh báo \"độ tin cậy thấp\" khi xác suất lớn nhất nhỏ hơn một ngưỡng (mặc định 0,7). Nhóm đo thử trên 600 ảnh test (đã loại ảnh trùng) và 15 ảnh lá ớt, cà chua dùng làm ảnh ngoài phạm vi.")
TABLE("Ngưỡng độ tin cậy: giữ ảnh đúng miền và loại ảnh lá cây khác", ["Ngưỡng", "Tỷ lệ ảnh sầu riêng được giữ", "Tỷ lệ ảnh lá cây khác bị loại"],
      [["0,5", "97%", "7%"], ["0,6", "93%", "20%"], ["0,7", "90%", "27%"], ["0,8", "86%", "40%"], ["0,9", "71%", "60%"]], widths=[3, 6, 6])
P("Kết quả cho thấy độ tin cậy softmax không phải bộ phát hiện ảnh ngoài phạm vi đáng tin cậy: ở ngưỡng 0,7 chỉ loại được 4/15 ảnh lá cây khác, và nhiều ảnh vẫn được gán bệnh sầu riêng với độ tin cậy trên 0,9. Số ảnh ngoài phạm vi chỉ 15 nên con số mang tính tham khảo. Do đó ứng dụng chỉ nên dùng với ảnh lá sầu riêng; muốn loại ảnh ngoài phạm vi cần thêm lớp \"không phải lá sầu riêng\" hoặc một bộ phát hiện riêng.")

# ---------------- 7 HẠN CHẾ ----------------
H("7. Phân tích, hạn chế và hướng phát triển", 1)
H("7.1. Hạn chế", 2)
BUL(["**Không có nguồn thứ ba:** mô hình gộp chưa được kiểm tra trên ảnh từ vườn hoặc thiết bị khác ngoài hai bộ đã huấn luyện.",
     "**Ít seed, CPU:** chỉ mô hình gộp chạy 4 seed; các mô hình đơn nguồn, phép thử ngoài miền, few-shot và học bán giám sát chỉ một lần chạy. Chưa thử thêm epoch hay kiến trúc lớn hơn.",
     "**Không ghi loss validation:** nên khó đánh giá quá khớp bằng đường cong.",
     "**Học bán giám sát:** người gán lại chỉ là mô phỏng bằng nhãn có sẵn, thiếu nhánh gán nhãn ngẫu nhiên để so sánh, và chỉ thử chiều Mendeley → Kaggle trên 4 lớp chung.",
     "**Ảnh ngoài phạm vi:** ngưỡng độ tin cậy không đủ tin cậy (Mục 6.2).",
     "**Nhãn:** Allocaridara là tổn thương do côn trùng; Colletotrichum và Rhizoctonia chỉ có ở một nguồn.",
     "**Đánh giá ban đầu so với giai đoạn trước:** hai giai đoạn dùng giao thức khác nhau nên không so trực tiếp từng con số."])
H("7.2. Hướng phát triển", 2)
BUL(["**Gộp thêm nguồn và dùng chia theo nguồn:** thêm dữ liệu từ nhiều vườn và đánh giá bằng cách giữ riêng một nguồn làm tập test.",
     "**Hoàn thiện học bán giám sát:** Mục 5.6 cho thấy phải có người kiểm tra và sửa nhãn thì vòng lặp mới cải thiện. Bước tiếp theo là thêm nhánh gán nhãn ngẫu nhiên cùng số ảnh để biết cách chọn ảnh khó có giúp không, chạy nhiều seed, dùng người gán thật trên ảnh vườn chưa gán nhãn, và thử nhãn giả trên mô hình gộp (vốn đúng hơn nhiều so với mô hình chỉ Mendeley).",
     "**Giảm phụ thuộc vào ánh sáng và nền:** chuẩn hóa màu, tăng cường mạnh hơn hoặc tách lá khỏi nền.",
     "**Phát hiện ảnh ngoài phạm vi:** thêm lớp \"khác\" hoặc dùng độ đo khoảng cách trên đặc trưng.",
     "**Thu thập ảnh thực địa** để tạo một tập kiểm tra độc lập."])
H("7.3. Sử dụng công cụ AI", 2)
P("Nhóm sử dụng trợ lý AI (Claude) để hỗ trợ viết mã, chạy thực nghiệm và soạn thảo báo cáo ở giai đoạn làm lại. Các kết quả đều được chạy lại từ mã nguồn trong thư mục dự án, và nhóm chịu trách nhiệm về nội dung. Nhật ký chi tiết các phiên làm việc được lưu riêng.")

# ---------------- 8 KẾT LUẬN ----------------
H("8. Kết luận", 1)
P("Đề tài đã thu gọn về nhận dạng bệnh lá sầu riêng và thay dữ liệu PlantVillage bằng hai bộ ảnh lá sầu riêng. Sau khi loại 121 ảnh Blight trùng giữa hai bộ, mô hình MobileNetV2 fine-tune đạt 93,7% (Kaggle), 96,1% (Mendeley) và 94,5% (gộp 2 bộ; trung bình 4 seed " + ms("tong") + ") trên tập test cùng nguồn, cao hơn nhiều so với 30–54% của giai đoạn trước.")
P("Điểm quan trọng hơn là phép thử ngoài miền: mô hình chỉ học một nguồn có thể giảm xuống 32% khi gặp ảnh nguồn khác, nên con số 94–96% không nói lên độ chính xác thực tế. Gộp nhiều nguồn giúp một mô hình xử lý được cả hai kiểu ảnh, nhưng độ tổng quát hóa ra nguồn thứ ba vẫn cần kiểm chứng. Trong few-shot, đặc trưng học từ dữ liệu sầu riêng giúp rõ nhất ở 1–5 ảnh mẫu và với các lớp chung giữa hai bộ. Thí nghiệm học bán giám sát cho thấy tự gán nhãn không đủ khi lệch miền lớn, còn khi có người gán lại các ảnh khó, accuracy trên Kaggle tăng từ 35,0% lên 81,1% sau 3 vòng; mức tăng này một phần đến từ 450 ảnh có nhãn được thêm vào và mới chạy một lần. Các bước tiếp theo là thêm nguồn dữ liệu, hoàn thiện vòng lặp bán giám sát với người gán thật và bổ sung cơ chế loại ảnh ngoài phạm vi.")

# ---------------- TÀI LIỆU THAM KHẢO ----------------
H("Tài liệu tham khảo", 1)
refs = [
    "Nguyen-Tat, T. B., Nong, D. T. (2026). Lightweight deep learning framework and real-world dataset for durian leaf disease detection in smart agriculture. Displays, 103451. https://doi.org/10.1016/j.displa.2026.103451",
    "A Durian Leaf Image Dataset of Common Diseases in Vietnam for Agricultural Diagnosis. Mendeley Data, DOI 10.17632/pxzvksbwnj.4; bài báo mô tả: PMC12272783.",
    "Sandler, M., Howard, A., Zhu, M., Zhmoginov, A., Chen, L.-C. (2018). MobileNetV2: Inverted Residuals and Linear Bottlenecks. CVPR.",
    "Snell, J., Swersky, K., Zemel, R. (2017). Prototypical Networks for Few-shot Learning. NeurIPS.",
    "Pan, S. J., Yang, Q. (2010). A Survey on Transfer Learning. IEEE Transactions on Knowledge and Data Engineering, 22(10).",
    "Deng, J. và cs. (2009). ImageNet: A Large-Scale Hierarchical Image Database. CVPR.",
    "Loshchilov, I., Hutter, F. (2019). Decoupled Weight Decay Regularization. ICLR.",
    "Müller, R., Kornblith, S., Hinton, G. (2019). When Does Label Smoothing Help? NeurIPS.",
    "Hughes, D. P., Salathé, M. (2015). An open access repository of images on plant health to enable the development of mobile disease diagnostics. arXiv:1511.08060 (PlantVillage, bộ dữ liệu của giai đoạn trước).",
]
for i, r in enumerate(refs, 1):
    p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY; p.paragraph_format.left_indent = Cm(1); p.paragraph_format.first_line_indent = Cm(-1)
    p.add_run(f"[{i}] {r}")

# ---------------- PHỤ LỤC ----------------
H("Phụ lục", 1)
H("Phụ lục A – Hướng dẫn chạy lại", 2)
P("Mã nguồn nằm trong thư mục DoAn_TTTN_V2. Thứ tự chạy (từ thư mục gốc dự án, cần Python 3.11, torch, torchvision, pandas, scikit-learn, pillow):", indent=False)
BUL(["python prepare_data.py – gom hai bộ, đánh dấu và loại ảnh trùng, ghi results/manifest.csv.",
     "python train_base.py --source kaggle|mendeley|merged --epochs 6 --tag <tên> – huấn luyện và test.",
     "python train_base.py --source merged --epochs 6 --tag merged_s43 --seed 43 (tương tự 44, 45), rồi python seeds_summary.py – mô hình gộp qua nhiều seed (CHAY_3_SEED.bat chạy cả ba).",
     "python eval_cross_domain.py – kiểm tra ngoài miền hai chiều trên 4 lớp chung.",
     "python eval_fewshot.py – few-shot 1/5/10 mẫu trên Mendeley.",
     "python semisup.py --rounds 3 --variants control pseudo human – học bán giám sát (Mục 5.6), ghi results/semisup_result.json.",
     "Demo: bấm đúp CHAY_DEMO.bat hoặc python -m streamlit run streamlit_app.py trong thư mục demo."])
H("Phụ lục B – Ma trận nhầm lẫn của các mô hình đơn nguồn", 2)
FIGURE("cm_kaggle.png", "Mô hình chỉ Kaggle trên tập test Kaggle.", 10.5)
FIGURE("cm_mendeley.png", "Mô hình chỉ Mendeley trên tập test Mendeley.", 10.5)
H("Phụ lục C – Ma trận nhầm lẫn ngoài miền", 2)
FIGURE("cm_cross_m2k.png", "Huấn luyện Mendeley, test Kaggle (4 lớp chung).", 10)
FIGURE("cm_cross_k2m.png", "Huấn luyện Kaggle, test Mendeley (4 lớp chung).", 10)

d.save(OUT)
print("saved", OUT, "figures", fig_n[0], "tables", tab_n[0])
