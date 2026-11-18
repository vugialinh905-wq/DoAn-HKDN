# DoAn_TTTN_V2 - Nhan dang benh la sau rieng (huan luyen tren Kaggle, danh gia few-shot tren Mendeley)

Thay PlantVillage bang bo Kaggle `cthng123/durian-leaf-disease-dataset` (5 lop, 4.437 anh).
Danh gia few-shot tren bo Mendeley "Durian Leaf Image Dataset ... Vietnam" (6 lop, 2.595 anh).

## Du lieu (thu muc `data/`)
- `data/kaggle/{train,val,test}/<LOP>/`  (tu `archive.zip`)
- `data/mendeley/{train,val,test}/<Lop>/` (tu zip Mendeley, thu muc `Durian_Leaf_Diseases`)

## Thu tu chay
| Buoc | Lenh | Ket qua |
|---|---|---|
| 1 | `python prepare_data.py` | `results/manifest.csv` (loai 121 anh Kaggle trung Mendeley + 2 anh trung noi bo) |
| 2 | `python train_base.py --epochs 8` | `results/base_best.pt`, `base_result.json` (test Kaggle) |
| 3 | `python eval_fewshot.py` | `results/fewshot_result.json` |

Buoc 2 luu checkpoint moi epoch va tu tiep tuc neu chay lai. May ca nhan khong co GPU (~15 phut/epoch): nen chay buoc 2-3 tren Colab.

## Chay tren Google Colab
1. Chay lai buoc 1 tren may, roi nen thu muc `DoAn_TTTN_V2` (kem `data/` va `results/manifest.csv`) len Drive.
2. Colab: Runtime > Change runtime type > GPU, roi:
```
from google.colab import drive; drive.mount('/content/drive')
%cd /content/drive/MyDrive/DoAn_TTTN_V2
!pip -q install -r requirements.txt
!python train_base.py --epochs 8
!python eval_fewshot.py
```
(`manifest.csv` dung duong dan tuong doi nen dung duoc tren may khac.)

## Giao thuc danh gia (khong ro ri)
- Support lay tu Mendeley `train`, query lay tu Mendeley `test`, bo anh gan trung noi bo.
- Bao cao rieng 4 lop chung voi Kaggle (Algal, Blight, Healthy, Phomopsis) va 2 lop moi (Colletotrichum, Rhizoctonia).
- Doi chung: cung backbone nhung chi pretrain ImageNet (khong qua Kaggle) de thay viec dung bo Kaggle co giup khong.
