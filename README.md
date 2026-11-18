# Bài nộp V2: Nhận dạng bệnh lá sầu riêng bằng học chuyển giao

Sinh viên: Vũ Gia Linh, Lê Ngọc Bích Loan · GVHD: TS. Trần Thế Vinh

| Thư mục / file | Nội dung |
|---|---|
| `CHAY_DEMO.bat` | Bấm đúp để chạy demo Streamlit (`http://localhost:8501`) |
| `01_Bao_cao/` | Báo cáo (`.docx`, kèm bản `.pdf`) |
| `02_Slide/` | Slide bảo vệ (19 slide, có ghi chú thuyết trình) |
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
python report/build_figures.py                           # biểu đồ (cần data/ cho một hình minh họa)
python report/build_report.py ; python report/build_slides.py
```
Máy không có GPU: mỗi epoch khoảng 4–13 phút trên CPU.

## Lưu ý
- Báo cáo còn ô `[Nhóm điền ...]` ở bảng phân công công việc, cần điền trước khi nộp.
- Số liệu ngưỡng độ tin cậy (slide 15, Bảng 11) lấy từ một lần chạy thử, chưa có file kết quả lưu kèm.

## Thí nghiệm dở dang
`03_Ma_nguon/semisup.py` (học bán giám sát) mới chạy xong vòng 0 và nhánh đối chứng; hai nhánh chính (tự gán nhãn, người gán lại) và 3 seed thêm cho mô hình gộp chưa chạy. Không dùng kết quả bán giám sát để kết luận.
