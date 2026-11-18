"""Buoc 2: huan luyen mo hinh nen tren Kaggle (5 lop), co checkpoint va tu tiep tuc.

Vi du:
  python train_base.py --epochs 8                       # day du (nen chay tren Colab GPU)
  python train_base.py --epochs 1 --max_per_class 20 --tag smoke   # thu nhanh tren CPU
Bien moi truong: DATA_DIR (thu muc chua kaggle/ va mendeley/), OUT_DIR (noi luu ket qua).
"""
import os, json, time, argparse
import numpy as np, pandas as pd, torch, torch.nn as nn
from PIL import Image
from torch.utils.data import Dataset, DataLoader
from torchvision import models, transforms as T

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get("DATA_DIR", os.path.join(HERE, "data"))
OUT = os.environ.get("OUT_DIR", os.path.join(HERE, "results"))
CLASSES_BY = {"kaggle": ["Algal", "Allocaridara", "Blight", "Healthy", "Phomopsis"],
              "mendeley": ["Algal", "Blight", "Colletotrichum", "Healthy", "Phomopsis", "Rhizoctonia"],
              "merged": ["Algal", "Allocaridara", "Blight", "Colletotrichum", "Healthy", "Phomopsis", "Rhizoctonia"]}
CLASSES = CLASSES_BY["kaggle"]  # mac dinh (eval_fewshot dung)
MEAN, STD = [0.485, 0.456, 0.406], [0.229, 0.224, 0.225]


class DS(Dataset):
    def __init__(self, df, tf, classes):
        self.p, self.y, self.tf = list(df.path), [classes.index(l) for l in df.label], tf

    def __len__(self):
        return len(self.p)

    def __getitem__(self, i):
        return self.tf(Image.open(os.path.join(DATA, self.p[i])).convert("RGB")), self.y[i]


def make_model(n=5):
    m = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.IMAGENET1K_V1)
    m.classifier[1] = nn.Linear(m.last_channel, n)
    return m


def evaluate(model, dl, dev, n=5):
    model.eval(); ys, ps = [], []
    with torch.no_grad():
        for x, y in dl:
            ps += model(x.to(dev)).argmax(1).cpu().tolist(); ys += y.tolist()
    ys, ps = np.array(ys), np.array(ps)
    from sklearn.metrics import f1_score, confusion_matrix
    return dict(acc=float((ys == ps).mean()), macro_f1=float(f1_score(ys, ps, average="macro")),
                confusion=confusion_matrix(ys, ps, labels=range(n)).tolist())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--epochs", type=int, default=8)
    ap.add_argument("--bs", type=int, default=32)
    ap.add_argument("--lr", type=float, default=3e-4)
    ap.add_argument("--max_per_class", type=int, default=0, help="0 = dung het (chi de thu nhanh)")
    ap.add_argument("--tag", default="base")
    ap.add_argument("--source", default="kaggle", choices=["kaggle", "mendeley", "merged"])
    ap.add_argument("--seed", type=int, default=42)
    a = ap.parse_args()
    torch.manual_seed(a.seed); np.random.seed(a.seed)
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    os.makedirs(OUT, exist_ok=True)

    man = pd.read_csv(os.path.join(OUT, "manifest.csv"))
    classes = CLASSES_BY[a.source]; nc = len(classes)
    kg = man[man.keep] if a.source == "merged" else man[(man.source == a.source) & man.keep]
    if a.source in ("mendeley", "merged"):  # val/test bo anh gan trung noi bo cua Mendeley
        kg = kg[(kg.split == "train") | ~kg.dup_in_mendeley.fillna(False).astype(bool)]
    def sub(split):
        d = kg[kg.split == split]
        if a.max_per_class:
            d = d.groupby("label", group_keys=False).head(a.max_per_class)
        return d
    tr_tf = T.Compose([T.RandomResizedCrop(224, scale=(0.6, 1.0)), T.RandomHorizontalFlip(),
                       T.ColorJitter(*((0.5, 0.5, 0.4, 0.05) if a.source == "merged" else (0.3, 0.3, 0.2))), T.ToTensor(), T.Normalize(MEAN, STD)])
    ev_tf = T.Compose([T.Resize((224, 224)), T.ToTensor(), T.Normalize(MEAN, STD)])
    dl = lambda split, tf, sh: DataLoader(DS(sub(split), tf, classes), batch_size=a.bs, shuffle=sh, num_workers=0)
    tr, va, te = dl("train", tr_tf, True), dl("val", ev_tf, False), dl("test", ev_tf, False)

    model = make_model(nc).to(dev)
    opt = torch.optim.AdamW(model.parameters(), lr=a.lr, weight_decay=1e-4)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=a.epochs)
    ck = os.path.join(OUT, f"{a.tag}_last.pt"); best_p = os.path.join(OUT, f"{a.tag}_best.pt")
    ep0, best, hist = 0, -1, []
    if os.path.exists(ck):  # tu tiep tuc
        s = torch.load(ck, map_location=dev)
        model.load_state_dict(s["model"]); opt.load_state_dict(s["opt"]); sched.load_state_dict(s["sched"])
        ep0, best, hist = s["epoch"], s["best"], s["hist"]
        print(f"Tiep tuc tu epoch {ep0}")
    lossf = nn.CrossEntropyLoss(label_smoothing=0.05)
    for ep in range(ep0, a.epochs):
        model.train(); t0 = time.time(); tot = 0
        for x, y in tr:
            opt.zero_grad(); l = lossf(model(x.to(dev)), y.to(dev)); l.backward(); opt.step(); tot += l.item() * len(y)
        sched.step()
        v = evaluate(model, va, dev, nc)
        hist.append(dict(epoch=ep + 1, loss=tot / len(tr.dataset), val_acc=v["acc"], sec=time.time() - t0))
        print(hist[-1], flush=True)
        if v["acc"] > best:
            best = v["acc"]; torch.save(model.state_dict(), best_p)
        torch.save(dict(model=model.state_dict(), opt=opt.state_dict(), sched=sched.state_dict(),
                        epoch=ep + 1, best=best, hist=hist), ck)
    model.load_state_dict(torch.load(best_p, map_location=dev))
    by_src = {}
    if a.source == "merged":  # bao cao rieng tung nguon tren tap test
        for src in ("kaggle", "mendeley"):
            d = sub("test"); d = d[d.source == src]
            by_src[src] = evaluate(model, DataLoader(DS(d, ev_tf, classes), batch_size=a.bs), dev, nc)
            print("TEST", src, "acc %.4f macroF1 %.4f" % (by_src[src]["acc"], by_src[src]["macro_f1"]))
    res = dict(test_by_source=by_src, classes=classes, best_val_acc=best, test=evaluate(model, te, dev, nc), history=hist,
               n_train=len(tr.dataset), device=dev)
    json.dump(res, open(os.path.join(OUT, f"{a.tag}_result.json"), "w"), indent=1)
    print("TEST acc %.4f  macroF1 %.4f" % (res["test"]["acc"], res["test"]["macro_f1"]))


if __name__ == "__main__":
    main()
