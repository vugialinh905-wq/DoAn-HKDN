# Bài nộp V2: Nhận dạng bệnh lá sầu riêng bằng học chuyển giao

Sinh viên: Vũ Gia Linh, Lê Ngọc Bích Loan · GVHD: TS. Trần Thế Vinh

| Thư mục / file | Nội dung |
|---|---|
| `CHAY_3_SEED.bat` | Chạy lại mô hình gộp với 3 seed thêm |
| `CHAY_DEMO.bat` | Bấm đúp để chạy demo Streamlit (`http://localhost:8501`) |
| `01_Bao_cao/` | Báo cáo (`.docx`, kèm bản `.pdf`) |
| `02_Slide/` | Slide bảo vệ (20 slide, có ghi chú thuyết trình) |
| `03_Ma_nguon/` | Mã nguồn, demo, kết quả đã lưu (`results/`) và mã tạo biểu đồ, báo cáo, slide (`report/`) |

## Dữ liệu (không kèm theo, vì dung lượng)
Để chạy lại huấn luyện, đặt hai bộ dữ liệu vào `03_Ma_nguon/data/`:
- `data/kaggle/{train,val,test}/<LỚP>/` từ Kaggle `cthng123/durian-leaf-disease-dataset` (`DLD_FinalDataset_224_spit`).
- `data/mendeley/{train,val,test}/<Lớp>/` từ Mendeley Data "A Durian Leaf Image Dataset of Common Diseases in Vietnam..." (thư mục `Durian_Leaf_Diseases`).

Demo và việc dựng lại biểu đồ, báo cáo, slide từ `results/` **không cần** dữ liệu.

## Chạy lại (từ `03_Ma_nguon`)
```
pip install -r requirements.txt
python prepare_data.py                                   # khử trùng, ghi results/manifest.csv
python train_base.py --source kaggle   --epochs 6 --tag base
python train_base.py --source mendeley --epochs 6 --tag mendeley
python train_base.py --source merged   --epochs 6 --tag merged
python eval_cross_domain.py                              # ngoài miền, 4 lớp chung
python eval_fewshot.py                                   # few-shot 1/5/10 mẫu
python semisup.py --rounds 3 --variants control pseudo human   # học bán giám sát (Mục 5.6)
python report/build_fig_semisup.py
python report/build_figures.py                           # biểu đồ (cần data/ cho một hình minh họa)
python report/build_report.py ; python report/build_slides.py
```
Máy không có GPU: mỗi epoch khoảng 4–13 phút trên CPU.

## Lưu ý
- Báo cáo còn ô `[Nhóm điền ...]` ở bảng phân công công việc, cần điền trước khi nộp.
- Số liệu ngưỡng độ tin cậy (slide 15, Bảng 14) lấy từ một lần chạy thử, chưa có file kết quả lưu kèm.
- Sau khi dựng lại báo cáo bằng `build_report.py`, mở file trong Word và cập nhật trường (Word tự hỏi khi mở) để mục lục và danh mục đúng số trang. Bản PDF hiện tại xuất bằng LibreOffice nên số trang có thể lệch so với Word.

## Học bán giám sát (Mục 5.6 báo cáo, slide 16)
`03_Ma_nguon/semisup.py`, kết quả ở `results/semisup_result.json` (đối chứng lần 1, tự gán nhãn, người gán lại) và `results/semisup_control_rerun.json` (đối chứng lần 2). Trọng số vòng 0 lưu ở `results/semisup_round0.pt` để mọi nhánh cùng điểm xuất phát. Accuracy trên Kaggle test sau 3 vòng: đối chứng 40,3% và 33,2%, tự gán nhãn 27,4%, người gán lại (mô phỏng bằng nhãn có sẵn) 81,1%. Mỗi nhánh chạy một lần.

## Mô hình gộp qua 4 seed (Bảng 9 báo cáo)
Bấm đúp `CHAY_3_SEED.bat` (chạy seed 43, 44, 45 rồi `seeds_summary.py`, khoảng 35 phút/seed trên CPU). Kết quả ở `results/merged_s4{3,4,5}_result.json` và `results/merged_seeds.json`: Kaggle 94,79 ± 0,11%, Mendeley 95,01 ± 0,74%, tính chung 94,86 ± 0,25% (n = 4, gồm seed 42). Trọng số các seed thêm không đưa lên kho.

## Còn dở dang
- Chưa có nhánh gán nhãn ngẫu nhiên 150 ảnh/vòng để so với nhánh người gán lại.
