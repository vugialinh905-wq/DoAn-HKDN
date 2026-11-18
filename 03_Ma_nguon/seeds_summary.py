"""Tong hop mo hinh gop qua nhieu seed: seed 42 (merged_result.json) va merged_s43/44/45_result.json."""
import json, os, statistics as st
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
files = {42: "merged_result.json", 43: "merged_s43_result.json", 44: "merged_s44_result.json", 45: "merged_s45_result.json"}
rows = {}
for seed, f in files.items():
    p = os.path.join(OUT, f)
    if not os.path.exists(p):
        print("thieu", f); continue
    r = json.load(open(p, encoding="utf8"))
    rows[seed] = dict(kaggle=r["test_by_source"]["kaggle"]["acc"], mendeley=r["test_by_source"]["mendeley"]["acc"],
                      tong=r["test"]["acc"], macro_f1=r["test"]["macro_f1"], best_val=r["best_val_acc"])
summ = {}
for k in ("kaggle", "mendeley", "tong", "macro_f1", "best_val"):
    v = [x[k] for x in rows.values()]
    summ[k] = dict(mean=st.mean(v), std=st.stdev(v) if len(v) > 1 else 0.0, min=min(v), max=max(v), n=len(v))
json.dump(dict(per_seed=rows, summary=summ), open(os.path.join(OUT, "merged_seeds.json"), "w", encoding="utf8"), indent=1)
for seed, x in rows.items():
    print(seed, " ".join("%s %.2f%%" % (k, 100 * v) if k != "macro_f1" else "F1 %.3f" % v for k, v in x.items()))
for k, s in summ.items():
    print("%-9s %.2f +- %.2f (n=%d)" % (k, 100 * s["mean"], 100 * s["std"], s["n"]))
