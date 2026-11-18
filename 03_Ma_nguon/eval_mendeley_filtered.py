"""Danh gia lai mo hinh chi-Mendeley tren tap test Mendeley da loai 13 anh gan trung noi bo (381 anh)."""
import os, json, numpy as np, pandas as pd, torch
from torch.utils.data import DataLoader
from torchvision import transforms as T
from sklearn.metrics import f1_score, confusion_matrix
from train_base import OUT, MEAN, STD, make_model, DS, CLASSES_BY
C = CLASSES_BY["mendeley"]
man = pd.read_csv(os.path.join(OUT, "manifest.csv")); man["dup_in_mendeley"] = man.dup_in_mendeley.fillna(False).astype(bool)
df = man[(man.source == "mendeley") & (man.split == "test") & ~man.dup_in_mendeley]
m = make_model(6); m.load_state_dict(torch.load(os.path.join(OUT, "mendeley_best.pt"), map_location="cpu")); m.eval()
ev = T.Compose([T.Resize((224, 224)), T.ToTensor(), T.Normalize(MEAN, STD)]); ps, ys = [], []
with torch.no_grad():
    for x, y in DataLoader(DS(df, ev, C), batch_size=64):
        ps += m(x).argmax(1).tolist(); ys += y.tolist()
ps, ys = np.array(ps), np.array(ys)
res = dict(n=len(ys), acc=float((ps == ys).mean()), macro_f1=float(f1_score(ys, ps, average="macro")), classes=C, confusion=confusion_matrix(ys, ps, labels=range(6)).tolist())
json.dump(res, open(os.path.join(OUT, "mendeley_test_filtered.json"), "w"), indent=1); print(res["n"], round(res["acc"], 4), round(res["macro_f1"], 4)); [print(r) for r in res["confusion"]]
