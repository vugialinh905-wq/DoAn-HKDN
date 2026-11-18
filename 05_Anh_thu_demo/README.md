# Ảnh dùng khi demo

Upload từng ảnh vào ô "Upload ảnh lá sầu riêng" của ứng dụng. Kết quả dưới đây do mô hình gộp (`03_Ma_nguon/demo/model.pt`) cho ra khi chạy thử; ngưỡng cảnh báo mặc định 0,70.

| Ảnh | Nhãn thật | Mô hình dự đoán | Độ tin cậy | Ý nghĩa khi trình bày |
|---|---|---|---|---|
| `1_Rhizoctonia_dung_cao.jpg` | Rhizoctonia (Mendeley, test) | Rhizoctonia | 97% | Ca đúng, tin cậy cao |
| `2_Healthy_Kaggle_dung_cao.jpg` | Healthy (Kaggle, test) | Healthy | 98% | Ca đúng, ảnh nguồn Kaggle |
| `3_Phomopsis_bi_nhan_nham_Algal.jpg` | Phomopsis (Kaggle, test) | Algal | 43% | Ca sai, độ tin cậy thấp nên có cảnh báo |
| `4_La_ca_chua_ngoai_pham_vi.jpg` | Lá cà chua (không phải sầu riêng) | Blight | 100% | Ngoài phạm vi nhưng vẫn tin cậy cao: minh họa giới hạn |

Ảnh 1–3 lấy từ tập test của hai bộ dữ liệu (không dùng để huấn luyện); ảnh 4 lấy từ bộ ảnh thử PlantVillage của bài nộp cũ.
Thư mục `03_Ma_nguon/demo/samples/` còn 33 ảnh test khác (đều đoán đúng).
