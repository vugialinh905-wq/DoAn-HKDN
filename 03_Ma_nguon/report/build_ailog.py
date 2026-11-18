"""Tao nhat ky su dung AI (giai doan lam lai, phien 43-55) theo mau cua AI_Development_Log_v2."""
import os
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(os.path.dirname(HERE)), "04_Nhat_ky_AI", "AI_Development_Log_v3_lam_lai.docx")
C1 = "13fd571"  # commit khoi tao kho moi (ma, bao cao, slide)
TOOL = "Claude Code (ứng dụng desktop, Anthropic), model Claude Sonnet 5.5 (claude-sonnet-5-5)"

d = Document()
s = d.sections[0]; s.left_margin = s.right_margin = Cm(2.5); s.top_margin = s.bottom_margin = Cm(2.2)
st = d.styles["Normal"]; st.font.name = "Times New Roman"; st.font.size = Pt(12)
st.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman"); st.paragraph_format.space_after = Pt(4)


def P(t, bold=False, align=None, size=None, italic=False):
    p = d.add_paragraph(); r = p.add_run(t); r.bold = bold; r.italic = italic
    if size: r.font.size = Pt(size)
    if align == "c": p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    return p


def L(label, text):
    p = d.add_paragraph(); p.paragraph_format.left_indent = Cm(.5)
    r = p.add_run(label + ": "); r.bold = True; p.add_run(text)


def table(header, rows, widths):
    t = d.add_table(rows=1, cols=len(header)); t.style = "Table Grid"
    for i, h in enumerate(header):
        c = t.rows[0].cells[i]; c.text = ""; c.paragraphs[0].add_run(h).bold = True
    for row in rows:
        cs = t.add_row().cells
        for i, v in enumerate(row): cs[i].text = v
    for row in t.rows:
        for i, w in enumerate(widths): row.cells[i].width = Cm(w)
        for c in row.cells:
            for p in c.paragraphs: p.paragraph_format.space_after = Pt(2)
    d.add_paragraph()


P("NHẬT KÝ SỬ DỤNG CÔNG CỤ AI", True, "c", 15)
P("(AI DEVELOPMENT LOG) – GIAI ĐOẠN LÀM LẠI, PHIÊN 43–55", True, "c", 12)
P("Đề tài: Nhận dạng bệnh trên lá sầu riêng bằng học chuyển giao: huấn luyện trên hai bộ dữ liệu và đánh giá ngoài miền", align="c")
P("Sinh viên thực hiện: Vũ Gia Linh (MSSV: 070305004702); Lê Ngọc Bích Loan (MSSV: 060305003162)")
P("Công cụ AI sử dụng: " + TOOL + ". Công cụ có quyền đọc/ghi tệp và chạy lệnh trên máy của sinh viên trong thư mục được cấp.")
P("Phạm vi ghi nhận: 13 phiên làm việc (Phiên 43–55) trong cuộc trò chuyện ngày 17–18/11/2026, tiếp nối nhật ký 42 phiên trước (AI_Development_Log_v2.docx).")
P("Cách làm việc: sinh viên đặt mục tiêu, chọn hướng đi và ra từng lệnh; công cụ AI thực hiện phần soạn mã, chạy thực nghiệm và soạn thảo văn bản theo lệnh đó và báo kết quả để sinh viên quyết định bước tiếp theo. "
  "Cần nói rõ: toàn bộ mã nguồn mới, các biểu đồ và bản nháp báo cáo, slide trong giai đoạn này do công cụ AI soạn thảo và chạy; sinh viên chịu trách nhiệm về quyết định, nội dung nộp và phải tự kiểm tra lại (xem Phụ lục A).")
P("Các prompt được chuẩn hóa về văn phong viết, giữ nguyên nội dung yêu cầu thực tế. Các ô [SV xác nhận] là việc chỉ sinh viên mới biết hoặc mới thực hiện được, cần tự điền trước khi nộp.", italic=True)

P("Các quyết định do sinh viên đưa ra trong giai đoạn này", True, size=13)
table(["Quyết định", "Nội dung"], [
    ["Q1", "Thu gọn đề tài về nhận dạng bệnh lá sầu riêng sau nhận xét của thầy (Phiên 44)."],
    ["Q2", "Dùng bộ Kaggle thay cho PlantVillage làm dữ liệu huấn luyện, bộ Mendeley cũ làm dữ liệu đánh giá (Phiên 44, 46)."],
    ["Q3", "Chọn hướng huấn luyện thường kết hợp chuyển giao thay vì giữ ProtoNet theo episode (Phiên 46)."],
    ["Q4", "Đặt dự án mới ở thư mục riêng, không ghi đè bài nộp cũ (Phiên 46)."],
    ["Q5", "Huấn luyện trên máy cá nhân thay vì Colab (Phiên 47)."],
    ["Q6", "Yêu cầu lần lượt: huấn luyện trên Mendeley, kiểm tra ngoài miền, huấn luyện gộp hai bộ, cập nhật demo (Phiên 48–51)."],
    ["Q7", "Yêu cầu làm lại báo cáo và slide, bổ sung sơ đồ loss còn thiếu (Phiên 52)."],
    ["Q8", "Yêu cầu truy vết nguồn số liệu của biểu đồ (Phiên 53), gom thư mục nộp bài và rà soát phần còn thiếu (Phiên 54)."],
    ["Q9", "Giao công cụ AI hoàn thiện mục lục, soạn nhật ký AI và tạo kho GitHub; sinh viên tự làm các mục còn lại (Phiên 55)."],
], [2, 13.5])

SESS = [
 ("Phiên 43 — Đọc lại bài nộp cũ", "17/11/2026",
  "Nắm cấu trúc và nội dung bài nộp cũ trước khi sửa đổi.",
  "Đọc thư mục DoAn_TTTN_Nop_Bai trong Documents trước, chỉ đọc; các yêu cầu sẽ đưa sau.",
  "Không phát sinh mã nguồn.",
  "Liệt kê 6 thư mục, trích văn bản từ báo cáo, slide và nhật ký, tóm tắt đề tài, số liệu benchmark ban đầu và danh sách việc còn tồn đọng trong README cũ.",
  "Chưa yêu cầu chỉnh sửa; giữ nguyên bản cũ.",
  "Công cụ đọc trực tiếp các tệp. [SV xác nhận] đã đối chiếu bản tóm tắt với bài nộp cũ."),
 ("Phiên 44 — Thu gọn đề tài, đánh giá và tìm bộ dữ liệu thay thế", "17/11/2026",
  "Đánh giá bộ dữ liệu Kaggle sinh viên tìm được và tìm thêm bộ phù hợp hơn để thay PlantVillage.",
  "Dán ghi chú nhận xét của thầy (accuracy khoảng 50%, cần thu gọn về lá sầu riêng, gợi ý học bán giám sát); nêu rằng thầy đánh giá kết quả trên sầu riêng quá thấp nên phải thu gọn đề tài; gửi liên kết bộ Kaggle cthng123 và nhờ đánh giá, tìm thêm bộ khác. Sau đó dán mô tả đầy đủ của bộ Kaggle và hỏi có trùng bộ cũ không.",
  "Không phát sinh mã nguồn.",
  "Tìm thấy bộ Mendeley (đúng bộ nhóm đang dùng), bộ Mendeley 10 bệnh ở Vĩnh Long, một số dự án Roboflow nhỏ và bài báo Thái Lan chưa có dữ liệu công khai. Nhận định nguyên nhân độ chính xác thấp nằm ở thiết kế chuyển miền. Không mở được trang Kaggle nên phải dựa vào mô tả sinh viên dán. Nêu Allocaridara là côn trùng, không phải bệnh nấm.",
  "Q1, Q2: thu gọn đề tài và chọn bộ Kaggle làm dữ liệu mới; yêu cầu kiểm tra mức trùng với bộ cũ.",
  "Thông tin về bộ Kaggle dựa trên mô tả sinh viên cung cấp và kết quả tìm kiếm web, chưa kiểm chứng từ trang gốc. [SV xác nhận] đã tự xem trang Kaggle và giấy phép."),
 ("Phiên 45 — Kiểm tra trùng lặp giữa hai bộ dữ liệu", "17/11/2026",
  "Xác định bộ Kaggle có phải bản đăng lại hoặc cắt ghép của bộ Mendeley hay không.",
  "Hỏi làm sao để công cụ trực tiếp xem dữ liệu; chỉ vào hai tệp zip mới nhất trong Downloads (bộ Kaggle và test_durian). Sau đó nhận ra test_durian chưa đầy đủ và cung cấp tệp Mendeley đầy đủ để so sánh lại.",
  "Mã so sánh tạm trong thư mục làm việc của công cụ (không nằm trong kho). Logic được tích hợp vào prepare_data.py.",
  "Lần 1 (chỉ có 18 ảnh cũ): 4/10 ảnh support lớp Blight trùng ảnh Kaggle. Lần 2 (đủ 2.595 ảnh Mendeley): 121 ảnh trùng, chỉ lớp Blight, nằm trong tập train Kaggle; lật/xoay không tìm thêm cặp nào. Trong Kaggle có 1 nhóm trùng SHA-256 và vài cặp gần trùng. Kết luận: không phải bản đăng lại, chỉ trùng một phần Blight.",
  "Phát hiện và chỉnh lỗi của công cụ: ban đầu mô tả ảnh Mendeley là đã tách nền; sau khi xem ảnh thực tế đã đính chính (ảnh nền tự nhiên). Sinh viên quyết định hai bộ phải khử trùng trước khi dùng.",
  "Công cụ chạy so sánh và xem ảnh 3 cặp trùng cạnh nhau. Giới hạn: phương pháp tương quan ảnh xám có thể sót ảnh bị cắt hoặc chỉnh màu mạnh. [SV xác nhận] đã xem lại các cặp ảnh trùng."),
 ("Phiên 46 — Thiết kế lại và chuẩn bị dữ liệu", "17/11/2026",
  "Chốt thiết kế mới và dựng dự án V2 với bước chuẩn bị dữ liệu.",
  "Nêu ý định lấy bộ mới để huấn luyện cho bộ cũ, bộ mới thay phần PlantVillage. Trả lời các lựa chọn của công cụ: chọn huấn luyện thường kết hợp chuyển giao và đặt dự án ở thư mục mới trong Documents. Hỏi nên làm trên VS Code hay Colab và hỏi nếu tắt máy thì phiên có bị ngắt không.",
  "prepare_data.py, requirements.txt, README.md (kho: " + C1 + ").",
  "Phân tích rủi ro: hai bộ chung 4/6 lớp nên không còn là few-shot lớp mới thuần túy; chỉ có 5 lớp nền nên meta-learning theo episode yếu. Tạo thư mục DoAn_TTTN_V2, sao chép dữ liệu, viết và chạy prepare_data.py: loại 121 ảnh Kaggle trùng Mendeley và 2 ảnh trùng nội bộ (còn 4.314 ảnh), đánh dấu 35 ảnh gần trùng của Mendeley. Máy không có GPU nên khuyến nghị code ở VS Code, huấn luyện nặng ở Colab; nêu rõ khi tắt máy phiên cục bộ dừng.",
  "Q3, Q4: chọn hướng huấn luyện thường kết hợp chuyển giao và thư mục dự án mới.",
  "Chạy prepare_data.py và đối chiếu số ảnh theo tập/lớp. [SV xác nhận] đã chạy lại prepare_data.py trên máy mình."),
 ("Phiên 47 — Huấn luyện mô hình nền trên Kaggle và đánh giá few-shot", "18/11/2026",
  "Huấn luyện MobileNetV2 trên Kaggle và đo few-shot trên Mendeley.",
  "Chọn chạy huấn luyện trên máy này (thay vì Colab); trong lúc chạy hỏi tiến độ huấn luyện.",
  "train_base.py, eval_fewshot.py (kho: " + C1 + ").",
  "Viết train_base.py (fine-tune toàn mạng, checkpoint tự tiếp tục) và eval_fewshot.py; thử nhanh bằng tập nhỏ rồi chạy 6 epoch trên CPU (khoảng 6 phút/epoch). Kết quả: test Kaggle 93,69%, macro F1 0,936. Few-shot trên Mendeley: tốt nhất 76,7% ở 10 mẫu (backbone Kaggle, hồi quy logistic) so với 72,1% đối chứng chỉ ImageNet; mức tăng so với bản cũ chủ yếu nhờ backbone MobileNetV2.",
  "Q5: chạy trên máy cá nhân; giữ máy bật để huấn luyện (công cụ xin giữ máy không ngủ trong lúc huấn luyện và yêu cầu được chấp nhận).",
  "Công cụ chạy và đọc lại log từng epoch. Chỉ một seed (42). [SV xác nhận] đã tự chạy lại hoặc xem log huấn luyện."),
 ("Phiên 48 — Huấn luyện có giám sát trên Mendeley", "18/11/2026",
  "Huấn luyện trực tiếp trên bộ Mendeley (6 lớp).",
  "Yêu cầu: Train trên Mendeley.",
  "train_base.py (thêm tùy chọn --source) (kho: " + C1 + ").",
  "Mở rộng train_base.py cho nhiều nguồn, chạy 6 epoch (khoảng 4 phút/epoch): test 95,43%, macro F1 0,952; lỗi chủ yếu ở Blight và Colletotrichum. Công cụ lưu ý đây mới là kết quả cùng nguồn.",
  "Q6: tiếp tục bước kiểm tra ngoài miền.",
  "Chạy thử nhanh trước khi chạy thật. [SV xác nhận] đã xem ma trận nhầm lẫn."),
 ("Phiên 49 — Kiểm tra ngoài miền", "18/11/2026",
  "Đo mô hình khi đổi nguồn ảnh, trên 4 lớp chung.",
  "Yêu cầu: Test ngoài miền.",
  "eval_cross_domain.py (kho: " + C1 + ").",
  "Viết eval_cross_domain.py, loại ảnh Blight trùng ở phía test. Kết quả: huấn luyện Mendeley, test Kaggle 32,03%; huấn luyện Kaggle, test Mendeley 76,19%. So sánh ảnh Healthy hai bộ và nêu giả thuyết khác phong cách chụp, ghi rõ chưa kiểm chứng.",
  "Chỉnh lỗi của công cụ: lỗi kiểu dữ liệu cột boolean khi đọc manifest, đã sửa và chạy lại. Sinh viên chọn tiếp tục bằng huấn luyện gộp hai bộ.",
  "Công cụ kiểm tra ma trận nhầm lẫn (mô hình gán Blight cho hầu hết ảnh Kaggle) để loại trừ lỗi nhãn. [SV xác nhận] đã xem ảnh so sánh Healthy."),
 ("Phiên 50 — Huấn luyện gộp hai bộ", "18/11/2026",
  "Huấn luyện một mô hình 7 lớp trên cả hai bộ.",
  "Yêu cầu: Train gộp 2 bộ.",
  "train_base.py (chế độ merged) (kho: " + C1 + ").",
  "Thêm chế độ merged với tăng cường màu mạnh hơn, 4.797 ảnh train, 6 epoch (khoảng 11 phút/epoch). Kết quả: Kaggle 94,71%, Mendeley 93,96%, tổng 94,48%; macro F1 Kaggle bị kéo thấp do lớp rỗng. Nêu giới hạn: chưa có nguồn thứ ba để kiểm tra ngoài miền.",
  "Q6: chuyển sang cập nhật demo.",
  "Chạy thử nhanh trước khi huấn luyện chính. [SV xác nhận] đã tự kiểm tra kết quả."),
 ("Phiên 51 — Cập nhật demo và xem trên trình duyệt", "18/11/2026",
  "Cập nhật ứng dụng Streamlit dùng mô hình gộp và xem giao diện.",
  "Yêu cầu: Cập nhật demo. Sau đó yêu cầu: Xem demo trên trình duyệt.",
  "demo/streamlit_app.py, demo/model.pt, demo/samples/, CHAY_DEMO.bat (kho: " + C1 + ").",
  "Viết demo mới (7 lớp, ngưỡng cảnh báo, ảnh mẫu, lịch sử, tab giới hạn). Đo ngưỡng độ tin cậy trên 600 ảnh test và 15 ảnh lá cây khác: ngưỡng 0,7 chỉ loại 4/15 ảnh ngoài phạm vi, nên demo ghi rõ giới hạn. 33/33 ảnh mẫu đoán đúng. Mở giao diện trong trình duyệt của ứng dụng và duyệt các tab; không upload được ảnh qua giao diện.",
  "Sinh viên yêu cầu xem demo trên trình duyệt; công cụ báo rõ phần chưa thử (upload qua giao diện).",
  "Kiểm tra tự động (AppTest) không lỗi và 33 ảnh mẫu. Số liệu ngưỡng chưa lưu thành tệp kết quả. [SV xác nhận] đã tự chạy demo và upload ảnh."),
 ("Phiên 52 — Làm lại báo cáo và slide", "18/11/2026",
  "Viết lại báo cáo và slide theo đề tài mới, thêm sơ đồ loss.",
  "Yêu cầu làm lại báo cáo và slide; nhấn mạnh slide cũ còn thiếu sơ đồ loss, cần thêm vào.",
  "report/build_figures.py, build_report.py, build_slides.py, fig/ (kho: " + C1 + ").",
  "Vẽ biểu đồ từ tệp kết quả JSON; dựng báo cáo (Word) và slide 19 trang kèm ghi chú thuyết trình, slide 8 là biểu đồ loss và accuracy validation của ba mô hình (chỉ có loss huấn luyện, không có loss validation, đã ghi rõ trong tài liệu). Xuất ra ảnh bằng Word và PowerPoint để kiểm tra bố cục.",
  "Chỉnh lỗi của công cụ: sai số thứ tự hình và mô tả sai các lỗi trong ma trận nhầm lẫn khi soạn báo cáo, sửa sau khi đối chiếu lại ma trận. Ô phân công công việc để trống chờ sinh viên điền.",
  "Kiểm tra bố cục bằng ảnh xuất ra. Tài liệu tham khảo do công cụ soạn theo kiến thức sẵn có, chưa tra lại từng nguồn. [SV xác nhận] đã đọc lại báo cáo, slide và kiểm tra tài liệu tham khảo."),
 ("Phiên 53 — Truy vết nguồn số liệu của biểu đồ", "18/11/2026",
  "Xác nhận các biểu đồ đến từ kết quả chạy thật.",
  "Hỏi: các ảnh biểu đồ đó chạy ra được từ kết quả chính xác đúng không.",
  "Không phát sinh mã mới.",
  "Đối chiếu số liệu gõ tay với tệp JSON (khớp). Nêu rõ biểu đồ ngưỡng độ tin cậy chưa có tệp kết quả lưu kèm.",
  "Sinh viên yêu cầu nêu rõ nguồn số liệu; công cụ ghi nhận hạn chế này trong tài liệu.",
  "So sánh trực tiếp số trong mã với tệp JSON. [SV xác nhận] đã chạy lại build_figures.py."),
 ("Phiên 54 — Gom thư mục nộp bài và rà soát phần còn thiếu", "18/11/2026",
  "Gom sản phẩm mới ra thư mục riêng và so với bài nộp cũ.",
  "Yêu cầu gom mã mới ra một thư mục riêng gồm cả báo cáo và slide. Sau đó hỏi so với bài nộp cũ đã xong chưa, còn thiếu gì.",
  "Thư mục DoAn_TTTN_V2_Nop_Bai, 05_Anh_thu_demo, CAI_THU_VIEN.bat (kho: " + C1 + ").",
  "Gom 01_Bao_cao, 02_Slide, 03_Ma_nguon; kiểm tra dựng lại biểu đồ, báo cáo, slide và demo từ thư mục mới. Tạo thư mục ảnh thử demo (2 ca đúng, 1 ca sai, 1 ảnh lá cà chua ngoài phạm vi). Liệt kê phần còn thiếu so với bản cũ: nhật ký AI, tài liệu ôn tập, kho GitHub, bảng phân công, danh mục.",
  "Q8: gom thư mục nộp bài và yêu cầu rà soát phần còn thiếu.",
  "Chạy thử dựng lại tệp và demo trong thư mục mới. Chưa chạy lại huấn luyện từ đầu trong thư mục mới."),
 ("Phiên 55 — Hoàn thiện mục lục, nhật ký AI và kho GitHub", "18/11/2026",
  "Hoàn thành mục lục báo cáo, soạn nhật ký này và tạo kho GitHub.",
  "Yêu cầu: tạo kho mới và đẩy lên; hoàn thành mục lục báo cáo; làm nhật ký AI theo kiểu sinh viên chủ động ra lệnh và làm việc; các mục còn lại sinh viên tự làm.",
  "report/build_report.py (danh mục viết tắt, hình, bảng, chú thích có đánh số tự động), report/build_ailog.py, 04_Nhat_ky_AI/ (kho: commit sau " + C1 + ").",
  "Bổ sung danh mục từ viết tắt, danh mục hình, danh mục bảng và cập nhật số trang trong Word; soạn nhật ký này theo mẫu cũ, ghi đúng vai trò (sinh viên ra lệnh và quyết định, công cụ AI soạn mã và văn bản). Tạo kho GitHub riêng tư và đẩy lên.",
  "Q9: sinh viên giữ lại tài liệu ôn tập, điền bảng phân công, xác nhận các ô [SV xác nhận] và kiểm tra tài liệu tham khảo.",
  "Kiểm tra mục lục bằng ảnh xuất ra từ Word. [SV xác nhận] đã đọc nhật ký này và xác nhận nội dung đúng với thực tế."),
]
for title, date, goal, prompt, files, result, dec, ver in SESS:
    P(title, True, size=13)
    L("Công cụ", TOOL); L("Ngày", date); L("Mục tiêu", goal); L("Prompt đã sử dụng", prompt)
    L("Tệp mã nguồn liên quan", files); L("Kết quả công cụ AI trả về", result)
    L("Quyết định và chỉnh sửa của sinh viên", dec); L("Cách kiểm thử và xác minh", ver)
    L("Commit tương ứng", C1 + " (kho DoAn-TTTN-V2-Durian-Leaf)")

P("Phụ lục A — Việc sinh viên tự thực hiện và xác nhận trước khi nộp", True, size=13)
for t in ["[SV xác nhận] Đọc lại toàn bộ báo cáo và slide, đối chiếu các con số với tệp results/*.json.",
          "[SV xác nhận] Tự chạy demo (CHAY_DEMO.bat) với 4 ảnh trong 05_Anh_thu_demo trên máy dùng để bảo vệ.",
          "[SV xác nhận] Kiểm tra từng tài liệu tham khảo (tên bài, năm, nơi đăng).",
          "[SV xác nhận] Điền bảng phân công công việc trong báo cáo.",
          "[SV xác nhận] Xác nhận nội dung từng phiên của nhật ký này đúng với thực tế làm việc."]:
    P("☐ " + t)
P("Phụ lục B — Tệp mã nguồn của giai đoạn làm lại", True, size=13)
table(["Tệp", "Chức năng"], [
    ["prepare_data.py", "Gom hai bộ dữ liệu, phát hiện và loại ảnh trùng, ghi manifest.csv."],
    ["train_base.py", "Huấn luyện MobileNetV2 theo ba cấu hình (kaggle, mendeley, merged), có checkpoint tự tiếp tục."],
    ["eval_cross_domain.py", "Kiểm tra ngoài miền hai chiều trên 4 lớp chung."],
    ["eval_fewshot.py", "Đánh giá few-shot 1/5/10 mẫu trên Mendeley."],
    ["demo/streamlit_app.py", "Ứng dụng minh họa dùng mô hình gộp 7 lớp."],
    ["report/build_figures.py, build_report.py, build_slides.py", "Dựng biểu đồ, báo cáo, slide từ results/."],
    ["report/build_ailog.py", "Dựng nhật ký này."],
], [6, 9.5])
d.save(OUT); print("saved", OUT)
