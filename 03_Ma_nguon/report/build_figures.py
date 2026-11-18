import json, os, glob, random
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as pa
from PIL import Image

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = os.path.join(R, "report", "fig")
os.makedirs(F, exist_ok=True)
rj = lambda n: json.load(open(os.path.join(R, "results", n), encoding="utf8"))
plt.rcParams.update({"font.family": "Arial", "font.size": 11, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.alpha": .25, "figure.dpi": 150})
GRN, AMB, TEAL, GRY, RED = "#2E7D32", "#F9A825", "#00838F", "#78909C", "#C62828"
base, mend, merg = rj("base_result.json"), rj("mendeley_result.json"), rj("merged_result.json")
cd, fs = rj("cross_domain_result.json"), rj("fewshot_result.json")

# 1. loss + val acc
fig, ax = plt.subplots(1, 2, figsize=(10, 3.9))
for r, lab, c in ((base, "Chỉ Kaggle", GRN), (mend, "Chỉ Mendeley", AMB), (merg, "Gộp 2 bộ", TEAL)):
    e = [h["epoch"] for h in r["history"]]
    ax[0].plot(e, [h["loss"] for h in r["history"]], "o-", color=c, label=lab, lw=2)
    ax[1].plot(e, [100 * h["val_acc"] for h in r["history"]], "o-", color=c, label=lab, lw=2)
ax[0].set(title="Loss huấn luyện theo epoch", xlabel="Epoch", ylabel="Loss (cross-entropy)")
ax[1].set(title="Accuracy trên tập validation", xlabel="Epoch", ylabel="Accuracy (%)", ylim=(88, 97))
ax[0].legend(); ax[1].legend(loc="lower right"); fig.tight_layout(); fig.savefig(f"{F}/loss.png"); plt.close()

# 2. in-domain results
fig, ax = plt.subplots(figsize=(7.5, 3.8))
lab = ["Mô hình chỉ Kaggle\ntest Kaggle", "Mô hình chỉ Mendeley\ntest Mendeley", "Mô hình gộp\ntest Kaggle", "Mô hình gộp\ntest Mendeley"]
v = [93.69, 95.43, 94.71, 93.96]
b = ax.bar(lab, v, color=[GRN, AMB, TEAL, TEAL], width=.6)
for x, y in zip(b, v):
    ax.text(x.get_x() + x.get_width() / 2, y + .3, f"{y:.1f}%".replace(".", ","), ha="center", fontweight="bold")
ax.set(ylim=(80, 100), ylabel="Accuracy (%)", title="Kết quả trong miền (cùng nguồn ảnh với tập huấn luyện)")
fig.tight_layout(); fig.savefig(f"{F}/indomain.png"); plt.close()

# 3. cross-domain
fig, ax = plt.subplots(1, 2, figsize=(10, 3.9), gridspec_kw={"width_ratios": [1, 1.6]})
v = [cd["mendeley_model_on_kaggle"]["acc"] * 100, cd["kaggle_model_on_mendeley"]["acc"] * 100]
b = ax[0].bar(["Huấn luyện Mendeley\n→ test Kaggle", "Huấn luyện Kaggle\n→ test Mendeley"], v, color=[RED, AMB], width=.55)
for x, y in zip(b, v):
    ax[0].text(x.get_x() + x.get_width() / 2, y + 1.2, f"{y:.1f}%".replace(".", ","), ha="center", fontweight="bold")
ax[0].set(ylim=(0, 100), ylabel="Accuracy (%)", title="Chuyển nguồn, 4 lớp chung")
cls = ["Algal", "Blight", "Healthy", "Phomopsis"]; w = .38; x = np.arange(4)
ax[1].bar(x - w / 2, [100 * cd["mendeley_model_on_kaggle"]["per_class"][c] for c in cls], w, color=RED, label="Mendeley → Kaggle")
ax[1].bar(x + w / 2, [100 * cd["kaggle_model_on_mendeley"]["per_class"][c] for c in cls], w, color=AMB, label="Kaggle → Mendeley")
ax[1].set_xticks(x); ax[1].set_xticklabels(cls)
ax[1].set(ylim=(0, 118), ylabel="Tỷ lệ đúng (%)", title="Theo từng lớp"); ax[1].legend(loc="upper center", ncol=2, frameon=False)
fig.tight_layout(); fig.savefig(f"{F}/crossdomain.png"); plt.close()

# 4. few-shot
fig, ax = plt.subplots(figsize=(7, 3.9)); K = [1, 5, 10]
for key, lab, c, ls in (("linear_kaggle", "Hồi quy logistic, backbone Kaggle", TEAL, "-"), ("proto_kaggle", "Prototype, backbone Kaggle", TEAL, "--"),
                        ("linear_imagenet", "Hồi quy logistic, chỉ ImageNet", GRY, "-"), ("proto_imagenet", "Prototype, chỉ ImageNet", GRY, "--")):
    ax.errorbar(K, [100 * fs["results"][f"{key}_{k}shot"]["acc"] for k in K], yerr=[100 * fs["results"][f"{key}_{k}shot"]["ci95"] for k in K],
                color=c, ls=ls, marker="o", lw=2, label=lab, capsize=3)
ax.set(xticks=K, xlabel="Số ảnh mẫu mỗi lớp (K)", ylabel="Accuracy (%)", title="Few-shot trên Mendeley (6 lớp, 600 episode)")
ax.legend(frameon=False, fontsize=9)
fig.tight_layout(); fig.savefig(f"{F}/fewshot.png"); plt.close()


# 5. confusion matrices
def cm(mat, labels, name, title, row_labels=None):
    m = np.array(mat); rl = row_labels or labels
    keep = [i for i in range(len(rl)) if m[i].sum() > 0]
    mm = m[keep]; pr = mm / mm.sum(1, keepdims=True)
    fig, ax = plt.subplots(figsize=(5.2 + .25 * len(labels), 4.3))
    ax.imshow(pr, cmap="Greens", vmin=0, vmax=1)
    ax.set_xticks(range(len(labels))); ax.set_xticklabels(labels, rotation=40, ha="right")
    ax.set_yticks(range(len(keep))); ax.set_yticklabels([rl[i] for i in keep])
    for i in range(len(keep)):
        for j in range(len(labels)):
            ax.text(j, i, mm[i, j], ha="center", va="center", color="white" if pr[i, j] > .55 else "black", fontsize=9)
    ax.set(xlabel="Dự đoán", ylabel="Nhãn thật", title=title); ax.grid(False)
    fig.tight_layout(); fig.savefig(f"{F}/{name}.png"); plt.close()


C5, C6, C7 = base["classes"], mend["classes"], merg["classes"]
cm(base["test"]["confusion"], C5, "cm_kaggle", "Mô hình Kaggle, test Kaggle")
cm(mend["test"]["confusion"], C6, "cm_mendeley", "Mô hình Mendeley, test Mendeley")
cm(merg["test_by_source"]["kaggle"]["confusion"], C7, "cm_merged_kaggle", "Mô hình gộp, test Kaggle")
cm(merg["test_by_source"]["mendeley"]["confusion"], C7, "cm_merged_mendeley", "Mô hình gộp, test Mendeley")
S4 = ["Algal", "Blight", "Healthy", "Phomopsis"]
cm(cd["mendeley_model_on_kaggle"]["confusion"], S4, "cm_cross_m2k", "Huấn luyện Mendeley → test Kaggle")
cm(cd["kaggle_model_on_mendeley"]["confusion"], S4, "cm_cross_k2m", "Huấn luyện Kaggle → test Mendeley")

# 6. dataset composition
man = pd.read_csv(os.path.join(R, "results", "manifest.csv"))
fig, ax = plt.subplots(1, 2, figsize=(10, 3.6))
kg = man[man.source == "kaggle"].groupby("label").agg(n=("path", "size"), keep=("keep", "sum"))
ax[0].barh(kg.index, kg.keep, color=GRN, label="Giữ lại")
ax[0].barh(kg.index, kg.n - kg.keep, left=kg.keep, color=RED, label="Loại (trùng)")
ax[0].set(title=f"Kaggle: {int(kg.n.sum()):,} ảnh, giữ {int(kg.keep.sum()):,}".replace(",", "."), xlabel="Số ảnh")
ax[0].legend(frameon=False, loc="lower right"); ax[0].invert_yaxis()
md = man[man.source == "mendeley"].groupby("label").size()
ax[1].barh(md.index, md.values, color=AMB)
ax[1].set(title=f"Mendeley: {int(md.sum()):,} ảnh".replace(",", "."), xlabel="Số ảnh"); ax[1].invert_yaxis()
fig.tight_layout(); fig.savefig(f"{F}/dataset.png"); plt.close()

# 7. Healthy comparison (can data/; neu khong co thi giu hinh da co)
if os.path.isdir(os.path.join(R, "data")):
    random.seed(1)
    fig, ax = plt.subplots(2, 5, figsize=(10, 4.4))
    for r, (nm, pat) in enumerate((("Mendeley – Healthy", "data/mendeley/test/Leaf_Healthy/*"), ("Kaggle – Healthy", "data/kaggle/test/HEALTHY_LEAF/*"))):
        for c, p in enumerate(random.sample(glob.glob(os.path.join(R, pat)), 5)):
            ax[r, c].imshow(Image.open(p).convert("RGB").resize((224, 224))); ax[r, c].axis("off")
            if c == 0:
                ax[r, c].set_title(nm, loc="left", fontsize=11, fontweight="bold")
    fig.tight_layout(); fig.savefig(f"{F}/healthy_compare.png"); plt.close()


# 8. pipeline diagram
fig, ax = plt.subplots(figsize=(10, 2.6)); ax.axis("off"); ax.set_xlim(0, 10); ax.set_ylim(0, 2.6)
steps = [("Kaggle\n4.437 ảnh", GRN), ("Mendeley\n2.595 ảnh", AMB), ("Khử trùng\nvà chia tập", GRY), ("MobileNetV2\nfine-tune", TEAL),
         ("Đánh giá trong\nvà ngoài miền", RED), ("Demo\nStreamlit", GRN)]
pos = [(.1, 1.45), (.1, .15), (2.0, .8), (4.0, .8), (6.1, .8), (8.2, .8)]
for (t, c), (x, y) in zip(steps, pos):
    ax.add_patch(pa.FancyBboxPatch((x, y), 1.7, 1.0, boxstyle="round,pad=.03,rounding_size=.1", fc=c, ec="none"))
    ax.text(x + .85, y + .5, t, ha="center", va="center", color="white", fontweight="bold", fontsize=10)
for (x1, y1, x2, y2) in ((1.85, 1.95, 2.0, 1.55), (1.85, .65, 2.0, 1.05), (3.75, 1.3, 4.0, 1.3), (5.75, 1.3, 6.1, 1.3), (7.85, 1.3, 8.2, 1.3)):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle="->", lw=1.8, color="#455A64"))
fig.savefig(f"{F}/pipeline.png", bbox_inches="tight"); plt.close()
print(sorted(os.listdir(F)))
