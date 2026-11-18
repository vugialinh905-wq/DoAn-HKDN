# Nhận dạng bệnh lá sầu riêng bằng học chuyển giao (MobileNetV2)

Mã nguồn của hệ thống: huấn luyện, đánh giá và ứng dụng minh họa. Dữ liệu huấn luyện không kèm theo vì dung lượng.

| Đường dẫn | Nội dung |
|---|---|
| `03_Ma_nguon/prepare_data.py` | Gom hai bộ dữ liệu, loại ảnh trùng, ghi `results/manifest.csv` |
| `03_Ma_nguon/train_base.py` | Huấn luyện MobileNetV2 (`--source kaggle|mendeley|merged`) |
| `03_Ma_nguon/eval_cross_domain.py`, `eval_fewshot.py`, `eval_mendeley_filtered.py`, `ci_table.py` | Đánh giá ngoài miền, few-shot, khoảng tin cậy |
| `03_Ma_nguon/semisup.py` | Thí nghiệm học bán giám sát |
| `03_Ma_nguon/seeds_summary.py` | Tổng hợp mô hình gộp qua nhiều seed |
| `03_Ma_nguon/demo/` | Ứng dụng Streamlit và mô hình |
| `03_Ma_nguon/results/` | Kết quả và trọng số đã lưu |
| `CAI_THU_VIEN.bat`, `CHAY_DEMO.bat`, `CHAY_3_SEED.bat` | Cài thư viện, chạy demo (`http://localhost:8501`), chạy thêm 3 seed |

## Dữ liệu
Đặt vào `03_Ma_nguon/data/`:
- `data/kaggle/{train,val,test}/<LỚP>/` từ Kaggle `cthng123/durian-leaf-disease-dataset` (`DLD_FinalDataset_224_spit`).
- `data/mendeley/{train,val,test}/<Lớp>/` từ Mendeley Data "A Durian Leaf Image Dataset of Common Diseases in Vietnam..." (`Durian_Leaf_Diseases`).

## Chạy lại (từ `03_Ma_nguon`)
```
pip install -r requirements.txt
python prepare_data.py
python train_base.py --source kaggle   --epochs 6 --tag base
python train_base.py --source mendeley --epochs 6 --tag mendeley
python train_base.py --source merged   --epochs 6 --tag merged
python eval_cross_domain.py
python eval_fewshot.py
python semisup.py --rounds 3 --variants control pseudo human
```
Không có GPU: mỗi epoch khoảng 4–13 phút trên CPU. Demo không cần dữ liệu.
