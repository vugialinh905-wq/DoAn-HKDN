"""Bieu do thi nghiem hoc ban giam sat (results/semisup_result.json, results/semisup_control_rerun.json neu co)."""
import json, os
import logging; logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = os.path.join(R, "report", "fig")
plt.rcParams.update({"font.family": ["Arial", "Liberation Sans", "DejaVu Sans"], "font.size": 11, "axes.spines.top": False,
                     "axes.spines.right": False, "axes.grid": True, "grid.alpha": .25, "figure.dpi": 150})
GRN, AMB, TEAL, GRY, RED = "#2E7D32", "#F9A825", "#00838F", "#78909C", "#C62828"
res = json.load(open(os.path.join(R, "results", "semisup_result.json"), encoding="utf8"))
rr = os.path.join(R, "results", "semisup_control_rerun.json")
rerun = json.load(open(rr, encoding="utf8"))["control"] if os.path.exists(rr) else None

x = [0, 1, 2, 3]
fig, ax = plt.subplots(1, 2, figsize=(10, 3.9))
series = [("Người gán lại (human)", res["human"], TEAL, "o-"), ("Đối chứng (lần 1)", res["control"], GRY, "s-"),
          ("Tự gán nhãn (pseudo)", res["pseudo"], RED, "^-")]
if rerun:
    series.insert(2, ("Đối chứng (lần 2)", rerun, GRY, "s--"))
for lab, rows, c, st in series:
    k = [100 * res["round0"]["kaggle"]["acc"]] + [100 * r["kaggle"]["acc"] for r in rows]
    lo = [100 * res["round0"]["kaggle"]["lo"]] + [100 * r["kaggle"]["lo"] for r in rows]
    hi = [100 * res["round0"]["kaggle"]["hi"]] + [100 * r["kaggle"]["hi"] for r in rows]
    ax[0].plot(x, k, st, color=c, label=lab, lw=2, alpha=.75 if "lần 2" in lab else 1)
    if "chạy lại" not in lab:
        ax[0].fill_between(x, lo, hi, color=c, alpha=.12, lw=0)
for lab, key, c, st in (("Tự gán nhãn (pseudo)", "pseudo", RED, "^-"), ("Người gán lại (human)", "human", TEAL, "o-")):
    ax[1].plot([1, 2, 3], [100 * r["pseudo_precision"] for r in res[key]], st, color=c, label=lab, lw=2)
ax[0].set(title="Accuracy trên Kaggle test (705 ảnh, 4 lớp)", xlabel="Vòng", ylabel="Accuracy (%)", xticks=x, ylim=(20, 90))
ax[1].set(title="Tỷ lệ nhãn giả đúng (ngưỡng 0,9)", xlabel="Vòng", ylabel="Nhãn giả đúng (%)", xticks=[1, 2, 3], ylim=(20, 90))
ax[0].legend(fontsize=9, loc="upper left"); ax[1].legend(fontsize=9)
fig.tight_layout(); fig.savefig(f"{F}/semisup.png"); plt.close()
print("saved", f"{F}/semisup.png")
