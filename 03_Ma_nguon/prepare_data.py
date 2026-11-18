"""Buoc 1: gom 2 bo du lieu, danh dau anh trung, ghi manifest.csv.

Kaggle  (huan luyen): data/kaggle/{train,val,test}/<LOP>/*.jpg   (5 lop, 224x224)
Mendeley (danh gia):  data/mendeley/{train,val,test}/<Lop>/*.jpg (6 lop, 400x400)

Danh dau:
  mendeley_overlap : anh Kaggle trung noi dung voi anh Mendeley (se bi loai khoi huan luyen)
  dup_in_kaggle    : anh Kaggle trung chinh xac (SHA-256) hoac gan trung (>0.98) voi anh khac
                     cua Kaggle -> chi giu 1 anh, cac ban sao bi loai
Chay: python prepare_data.py   (bien moi truong DATA_DIR de doi thu muc du lieu)
"""
import os, glob, hashlib
import numpy as np
import pandas as pd
from PIL import Image

DATA = os.environ.get("DATA_DIR", os.path.join(os.path.dirname(os.path.abspath(__file__)), "data"))
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
os.makedirs(OUT, exist_ok=True)

# Ten lop chung (Kaggle -> ten thong nhat)
K_MAP = {"ALGAL_LEAF_SPOT": "Algal", "ALLOCARIDARA_ATTACK": "Allocaridara",
         "HEALTHY_LEAF": "Healthy", "LEAF_BLIGHT": "Blight", "PHOMOPSIS_LEAF_SPOT": "Phomopsis"}
M_MAP = {"Leaf_Algal": "Algal", "Leaf_Blight": "Blight", "Leaf_Colletotrichum": "Colletotrichum",
         "Leaf_Healthy": "Healthy", "Leaf_Phomopsis": "Phomopsis", "Leaf_Rhizoctonia": "Rhizoctonia"}


def vec(path, size=24):
    a = np.asarray(Image.open(path).convert("L").resize((size, size), Image.BILINEAR), dtype=np.float32).ravel()
    a = a - a.mean()
    return a / (np.linalg.norm(a) + 1e-6)


def collect(root, cmap, source):
    rows = []
    for split in ("train", "val", "test"):
        for p in sorted(glob.glob(os.path.join(root, split, "*", "*"))):
            if not p.lower().endswith((".jpg", ".jpeg", ".png")):
                continue
            cls = cmap[os.path.basename(os.path.dirname(p))]
            rows.append(dict(source=source, split=split, label=cls, path=os.path.relpath(p, DATA).replace("\\", "/")))
    return pd.DataFrame(rows)


def main():
    kg = collect(os.path.join(DATA, "kaggle"), K_MAP, "kaggle")
    md = collect(os.path.join(DATA, "mendeley"), M_MAP, "mendeley")
    print("Kaggle:", len(kg), "Mendeley:", len(md))

    print("Tinh dac trung 24x24 ...")
    K = np.stack([vec(os.path.join(DATA, p)) for p in kg.path])
    M = np.stack([vec(os.path.join(DATA, p)) for p in md.path])

    # 1) Kaggle trung Mendeley
    best = (K @ M.T).max(1)
    kg["mendeley_overlap"] = best > 0.95
    print("Anh Kaggle trung Mendeley:", int(kg.mendeley_overlap.sum()))

    # 2) Trung ben trong Kaggle: SHA-256 + gan trung
    sha = [hashlib.sha256(open(os.path.join(DATA, p), "rb").read()).hexdigest() for p in kg.path]
    kg["sha"] = sha
    G = K @ K.T
    np.fill_diagonal(G, 0)
    dup = np.zeros(len(kg), bool)
    # giu anh co chi so nho hon, loai anh co chi so lon hon cua moi cap trung
    for i, j in np.argwhere(np.triu(G > 0.98)):
        dup[j] = True
    first = {}
    for i, h in enumerate(sha):
        if h in first:
            dup[i] = True
        else:
            first[h] = i
    kg["dup_in_kaggle"] = dup
    print("Anh Kaggle bi loai vi trung noi bo:", int(dup.sum()))

    # 3) Trung giua Mendeley noi bo (de biet), khong loai
    GM = M @ M.T
    np.fill_diagonal(GM, 0)
    md["dup_in_mendeley"] = (np.triu(GM > 0.98).any(0))
    print("Anh Mendeley gan trung noi bo (thong tin):", int(md.dup_in_mendeley.sum()))

    kg["keep"] = ~(kg.mendeley_overlap | kg.dup_in_kaggle)
    md["keep"] = True
    man = pd.concat([kg, md], ignore_index=True)
    man.to_csv(os.path.join(OUT, "manifest.csv"), index=False, encoding="utf-8")
    print("\nSo anh Kaggle giu lai theo tap/lop:")
    print(kg[kg.keep].groupby(["split", "label"]).size().unstack(0))
    print("\nDa ghi results/manifest.csv")


if __name__ == "__main__":
    main()
