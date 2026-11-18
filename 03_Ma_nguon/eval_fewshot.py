"""Buoc 3: danh gia few-shot tren Mendeley (6 lop) voi mo hinh nen huan luyen tren Kaggle.

Giao thuc (khong ro ri):
  - support : rut tu Mendeley 'train'  (K anh moi lop, K = 1/5/10)
  - query   : rut tu Mendeley 'test'   (15 anh moi lop), bo anh gan trung noi bo
  - 600 episode, seed co dinh, 6-way (du 6 lop)
Phuong phap (tren dac trung 1280-chieu cua MobileNetV2):
  proto_kaggle   : prototype (trung binh embedding), backbone da train tren Kaggle
  linear_kaggle  : hoi quy logistic tren K anh support, backbone da train tren Kaggle
  proto_imagenet : doi chung - backbone chi pretrain ImageNet, khong qua Kaggle
  linear_imagenet: doi chung tuong tu
Bao cao accuracy tong, nhom 4 lop chung voi Kaggle, nhom 2 lop moi (Colletotrichum, Rhizoctonia).
Chay: python eval_fewshot.py --ckpt results/base_best.pt [--limit 0]
"""
import os, json, argparse
import numpy as np, pandas as pd, torch
from PIL import Image
from torchvision import models, transforms as T
from sklearn.linear_model import LogisticRegression
from train_base import DATA, OUT, MEAN, STD, make_model

NOVEL = ["Colletotrichum", "Rhizoctonia"]


def extract(model, paths, dev, bs=64):
    tf = T.Compose([T.Resize((224, 224)), T.ToTensor(), T.Normalize(MEAN, STD)])
    feats = []
    model.eval()
    with torch.no_grad():
        for i in range(0, len(paths), bs):
            x = torch.stack([tf(Image.open(os.path.join(DATA, p)).convert("RGB")) for p in paths[i:i + bs]]).to(dev)
            f = model.features(x).mean((2, 3))
            feats.append(torch.nn.functional.normalize(f, dim=1).cpu())
    return torch.cat(feats).numpy()


def run(F, y, split, ok_query, classes, K, n_ep, q=15, seed=42):
    rng = np.random.RandomState(seed)
    idx = {c: np.where((y == c) & (split == "train"))[0] for c in range(len(classes))}
    qidx = {c: np.where((y == c) & (split == "test") & ok_query)[0] for c in range(len(classes))}
    acc = {m: [] for m in ("proto", "linear")}; per = {m: np.zeros((len(classes), 2)) for m in acc}
    for _ in range(n_ep):
        S, SY, Q, QY = [], [], [], []
        for c in range(len(classes)):
            s = rng.choice(idx[c], K, replace=False); qq = rng.choice(qidx[c], min(q, len(qidx[c])), replace=False)
            S += list(s); SY += [c] * K; Q += list(qq); QY += [c] * len(qq)
        S, Q, SY, QY = F[S], F[Q], np.array(SY), np.array(QY)
        P = np.stack([S[SY == c].mean(0) for c in range(len(classes))])
        pp = (((Q[:, None] - P[None]) ** 2).sum(-1)).argmin(1)
        if K == 1:  # logistic can 2+ mau/lop; voi 1-shot dung chinh prototype
            lp = pp
        else:
            lp = LogisticRegression(max_iter=300, C=10).fit(S, SY).predict(Q)
        for m, p in (("proto", pp), ("linear", lp)):
            acc[m].append((p == QY).mean())
            for c in range(len(classes)):
                mk = QY == c; per[m][c] += [(p[mk] == c).sum(), mk.sum()]
    return acc, per


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", default=os.path.join(OUT, "base_best.pt"))
    ap.add_argument("--episodes", type=int, default=600)
    ap.add_argument("--limit", type=int, default=0, help="chi de thu nhanh: so anh toi da moi lop")
    ap.add_argument("--tag", default="fewshot")
    a = ap.parse_args()
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    man = pd.read_csv(os.path.join(OUT, "manifest.csv")); md = man[man.source == "mendeley"].reset_index(drop=True)
    if a.limit:
        md = md.groupby(["split", "label"], group_keys=False).head(a.limit).reset_index(drop=True)
    classes = sorted(md.label.unique()); y = md.label.map(classes.index).values
    split = md.split.values; ok_q = ~md.dup_in_mendeley.values
    paths = list(md.path)

    models_ = {}
    m_in = make_model(); models_["imagenet"] = m_in  # head 5 lop khong dung, chi lay features
    m_kg = make_model(); m_kg.load_state_dict(torch.load(a.ckpt, map_location="cpu")); models_["kaggle"] = m_kg
    res = {"classes": classes, "novel": NOVEL, "episodes": a.episodes, "results": {}}
    for name, m in models_.items():
        F = extract(m.to(dev), paths, dev)
        for K in (1, 5, 10):
            acc, per = run(F, y, split, ok_q, classes, K, a.episodes)
            for meth in ("proto", "linear"):
                a_ = np.array(acc[meth]); pc = per[meth][:, 0] / np.maximum(per[meth][:, 1], 1)
                shared = [i for i, c in enumerate(classes) if c not in NOVEL]; nov = [i for i, c in enumerate(classes) if c in NOVEL]
                key = f"{meth}_{name}_{K}shot"
                res["results"][key] = dict(acc=float(a_.mean()), ci95=float(1.96 * a_.std() / np.sqrt(len(a_))),
                                           per_class={c: float(pc[i]) for i, c in enumerate(classes)},
                                           acc_shared4=float(pc[shared].mean()), acc_novel2=float(pc[nov].mean()))
                print(key, "acc %.3f  chung4 %.3f  moi2 %.3f" % (a_.mean(), pc[shared].mean(), pc[nov].mean()), flush=True)
    json.dump(res, open(os.path.join(OUT, f"{a.tag}_result.json"), "w"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()
