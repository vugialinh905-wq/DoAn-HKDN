"""Test ngoai mien: 2 chieu tren 4 lop chung (Algal, Blight, Healthy, Phomopsis).

  A) Mo hinh huan luyen tren Mendeley  -> test tren Kaggle (anh khac vuon, khac thiet bi)
  B) Mo hinh huan luyen tren Kaggle    -> test tren Mendeley
Chi dung anh test/val/train cua bo dich (toan bo anh cua 4 lop chung, vi mo hinh chua tung thay bo do),
nhung loai anh Blight trung noi dung giua 2 bo (121 anh) de khong ro ri.
Chay: python eval_cross_domain.py
"""
import os, json
import numpy as np, pandas as pd, torch
from PIL import Image
from torchvision import transforms as T
from sklearn.metrics import f1_score, confusion_matrix
from train_base import DATA, OUT, MEAN, STD, CLASSES_BY, make_model
from prepare_data import vec

SHARED = ["Algal", "Blight", "Healthy", "Phomopsis"]


def predict(model, paths, dev, allowed, classes, bs=64):
    tf = T.Compose([T.Resize((224, 224)), T.ToTensor(), T.Normalize(MEAN, STD)])
    mask = torch.full((len(classes),), -1e9); [mask.__setitem__(classes.index(c), 0.0) for c in allowed]
    out = []; model.eval()
    with torch.no_grad():
        for i in range(0, len(paths), bs):
            x = torch.stack([tf(Image.open(os.path.join(DATA, p)).convert("RGB")) for p in paths[i:i + bs]]).to(dev)
            out += (model(x).cpu() + mask).argmax(1).tolist()
    return [classes[i] for i in out]


def report(y, p):
    y, p = np.array(y), np.array(p)
    cm = confusion_matrix(y, p, labels=SHARED)
    return dict(n=len(y), acc=float((y == p).mean()), macro_f1=float(f1_score(y, p, labels=SHARED, average="macro")),
                per_class={c: float((p[y == c] == c).mean()) for c in SHARED}, confusion=cm.tolist())


def main():
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    man = pd.read_csv(os.path.join(OUT, "manifest.csv"))
    kg = man[(man.source == "kaggle") & man.label.isin(SHARED)]
    md = man[(man.source == "mendeley") & man.label.isin(SHARED)].reset_index(drop=True)
    kg_ok = kg[~kg.mendeley_overlap.astype(bool)].reset_index(drop=True)   # bo anh trung Mendeley
    # anh Mendeley trung noi dung voi Kaggle (de bo khi test mo hinh Kaggle)
    kg_ov = kg[kg.mendeley_overlap.astype(bool)]
    A = np.stack([vec(os.path.join(DATA, p)) for p in md.path]); B = np.stack([vec(os.path.join(DATA, p)) for p in kg_ov.path])
    md_ok = md[(A @ B.T).max(1) < 0.95].reset_index(drop=True)
    print("Kaggle dung:", len(kg_ok), " Mendeley dung:", len(md_ok), "(bo", len(md) - len(md_ok), "anh trung)")

    res = {}
    mm = make_model(6); mm.load_state_dict(torch.load(os.path.join(OUT, "mendeley_best.pt"), map_location="cpu")); mm.to(dev)
    res["mendeley_model_on_kaggle"] = report(kg_ok.label, predict(mm, list(kg_ok.path), dev, SHARED, CLASSES_BY["mendeley"]))
    mk = make_model(5); mk.load_state_dict(torch.load(os.path.join(OUT, "base_best.pt"), map_location="cpu")); mk.to(dev)
    res["kaggle_model_on_mendeley"] = report(md_ok.label, predict(mk, list(md_ok.path), dev, SHARED, CLASSES_BY["kaggle"]))
    for k, v in res.items():
        print(k, "n=%d acc=%.3f macroF1=%.3f" % (v["n"], v["acc"], v["macro_f1"]), {c: round(a, 2) for c, a in v["per_class"].items()})
    json.dump(res, open(os.path.join(OUT, "cross_domain_result.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
