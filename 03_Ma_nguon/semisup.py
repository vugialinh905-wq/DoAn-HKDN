"""Hoc ban giam sat: huan luyen tren Mendeley (co nhan), dung anh Kaggle KHONG nhan de cai thien tren Kaggle.

Bai toan: 4 lop chung (Algal, Blight, Healthy, Phomopsis).
  - Co nhan  : Mendeley train
  - Khong nhan (pool): 300 anh/lop tu Kaggle train (da loai anh trung Mendeley)
  - Test     : Kaggle test (ngoai mien) va Mendeley test (trong mien, kiem tra khong bi quen)
Vong lap (R vong, moi vong fine-tune tiep EPOCHS epoch):
  control : chi huan luyen tiep tren anh co nhan (doi chung: cung so epoch, khong dung anh khong nhan)
  pseudo  : them anh pool co do tin cay >= TH voi nhan giu (pseudo-label)
  human   : nhu pseudo + moi vong "con nguoi" gan lai nhan cho HUMAN anh co do tin cay thap nhat
            (mo phong: nhan that lay tu ten thu muc; day la gia lap viec gan nhan, khong co nguoi that)
Chay: python semisup.py [--rounds 3] [--variants control pseudo human]
"""
import os, json, time, argparse, math
import numpy as np, pandas as pd, torch, torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import transforms as T
from train_base import DATA, OUT, MEAN, STD, make_model, DS

SHARED = ["Algal", "Blight", "Healthy", "Phomopsis"]
TH, HUMAN, EPOCHS, R0_EPOCHS = 0.9, 150, 3, 5

ap = argparse.ArgumentParser()
ap.add_argument("--rounds", type=int, default=3)
ap.add_argument("--variants", nargs="+", default=["control", "pseudo", "human"])
ap.add_argument("--bs", type=int, default=32)
a = ap.parse_args()
dev = "cuda" if torch.cuda.is_available() else "cpu"

man = pd.read_csv(os.path.join(OUT, "manifest.csv"))
man["dup_in_mendeley"] = man.dup_in_mendeley.fillna(False).astype(bool)
sel = man[man.keep & man.label.isin(SHARED)]
src = sel[(sel.source == "mendeley") & (sel.split == "train")].reset_index(drop=True)
m_test = sel[(sel.source == "mendeley") & (sel.split == "test") & ~sel.dup_in_mendeley].reset_index(drop=True)
k_test = sel[(sel.source == "kaggle") & (sel.split == "test")].reset_index(drop=True)
k_pool = sel[(sel.source == "kaggle") & (sel.split == "train")].groupby("label", group_keys=False).sample(300, random_state=0).reset_index(drop=True)
print("source", len(src), "pool", len(k_pool), "kaggle test", len(k_test), "mendeley test", len(m_test), flush=True)

tr_tf = T.Compose([T.RandomResizedCrop(224, scale=(0.6, 1.0)), T.RandomHorizontalFlip(), T.ColorJitter(0.5, 0.5, 0.4, 0.05), T.ToTensor(), T.Normalize(MEAN, STD)])
ev_tf = T.Compose([T.Resize((224, 224)), T.ToTensor(), T.Normalize(MEAN, STD)])


def loader(df, tf, shuffle):
    return DataLoader(DS(df, tf, SHARED), batch_size=a.bs, shuffle=shuffle, num_workers=0)


def fit(model, df, epochs, lr):
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    sch = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=epochs); lf = nn.CrossEntropyLoss(label_smoothing=0.05)
    dl = loader(df, tr_tf, True)
    for ep in range(epochs):
        model.train(); tot = 0
        for x, y in dl:
            opt.zero_grad(); l = lf(model(x.to(dev)), y.to(dev)); l.backward(); opt.step(); tot += l.item() * len(y)
        sch.step()
    return tot / len(dl.dataset)


def probs(model, df):
    model.eval(); out = []
    with torch.no_grad():
        for x, _ in loader(df, ev_tf, False):
            out.append(torch.softmax(model(x.to(dev)), 1).cpu())
    return torch.cat(out).numpy()


def acc_ci(model, df):
    p = probs(model, df); y = np.array([SHARED.index(l) for l in df.label]); n = len(y); k = int((p.argmax(1) == y).sum()); ph = k / n; z = 1.96
    c = (ph + z * z / (2 * n)) / (1 + z * z / n); h = z * math.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return dict(acc=ph, lo=c - h, hi=c + h, n=n)


torch.manual_seed(42); np.random.seed(42)
r0 = os.path.join(OUT, "semisup_round0.pt")
base = make_model(4).to(dev)
if os.path.exists(r0):
    base.load_state_dict(torch.load(r0, map_location=dev)); print("round0 nap tu file", flush=True)
else:
    t0 = time.time(); l = fit(base, src, R0_EPOCHS, 3e-4); torch.save(base.state_dict(), r0); print("round0 xong %.0fs loss %.3f" % (time.time() - t0, l), flush=True)
res_p = os.path.join(OUT, "semisup_result.json")
res = json.load(open(res_p)) if os.path.exists(res_p) else {}
res["round0"] = dict(kaggle=acc_ci(base, k_test), mendeley=acc_ci(base, m_test)); print("round0", res["round0"], flush=True)
json.dump(res, open(res_p, "w"), indent=1)
ytrue = np.array([SHARED.index(l) for l in k_pool.label])

for var in a.variants:
    model = make_model(4).to(dev); model.load_state_dict(torch.load(r0, map_location=dev))
    human = set(); rows = []
    for rd in range(1, a.rounds + 1):
        t0 = time.time(); pool_p = probs(model, k_pool); pred = pool_p.argmax(1); conf = pool_p.max(1)
        parts = [src]; info = dict(round=rd)
        if var in ("pseudo", "human"):
            if var == "human":
                order = [i for i in np.argsort(conf) if i not in human]
                human |= set(order[:HUMAN])
            hum = np.array(sorted(human), dtype=int)
            ps = np.array([i for i in range(len(k_pool)) if conf[i] >= TH and i not in human], dtype=int)
            info.update(n_pseudo=int(len(ps)), pseudo_precision=float((pred[ps] == ytrue[ps]).mean()) if len(ps) else None, n_human=int(len(hum)))
            if len(ps):
                d1 = k_pool.iloc[ps].copy(); d1["label"] = [SHARED[i] for i in pred[ps]]; parts.append(d1)
            if len(hum):
                parts.append(k_pool.iloc[hum].copy())  # nhan that (mo phong con nguoi gan nhan)
        train_df = pd.concat(parts, ignore_index=True)
        l = fit(model, train_df, EPOCHS, 1.5e-4)
        info.update(train_size=len(train_df), loss=l, kaggle=acc_ci(model, k_test), mendeley=acc_ci(model, m_test), sec=time.time() - t0)
        rows.append(info); print(var, json.dumps(info), flush=True)
        res[var] = rows; json.dump(res, open(res_p, "w"), indent=1)
print("XONG", flush=True)
