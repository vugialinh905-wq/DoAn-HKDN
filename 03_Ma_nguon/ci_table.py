"""Khoang tin cay Wilson 95% cho cac accuracy da bao cao (chi phan anh sai so do kich thuoc tap test, khong phan anh dao dong giua cac lan huan luyen)."""
import json, math, os
import numpy as np
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results"); rj = lambda n: json.load(open(os.path.join(R, n), encoding="utf8"))
def wilson(k, n, z=1.96):
    p = k / n; c = (p + z * z / (2 * n)) / (1 + z * z / n); h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n); return p, c - h, c + h
def fromcm(cm):
    m = np.array(cm); return wilson(int(np.trace(m)), int(m.sum())) + (int(m.sum()),)
b, m, g, cd = rj("base_result.json"), rj("mendeley_result.json"), rj("merged_result.json"), rj("cross_domain_result.json")
rows = {"Chi Kaggle, test Kaggle": fromcm(b["test"]["confusion"]), "Chi Mendeley, test Mendeley": fromcm(rj("mendeley_test_filtered.json")["confusion"]),
        "Gop, test Kaggle": fromcm(g["test_by_source"]["kaggle"]["confusion"]), "Gop, test Mendeley": fromcm(g["test_by_source"]["mendeley"]["confusion"]),
        "Mendeley -> Kaggle (4 lop chung)": fromcm(cd["mendeley_model_on_kaggle"]["confusion"]), "Kaggle -> Mendeley (4 lop chung)": fromcm(cd["kaggle_model_on_mendeley"]["confusion"])}
out = {k: dict(acc=v[0], lo=v[1], hi=v[2], n=v[3]) for k, v in rows.items()}
json.dump(out, open(os.path.join(R, "ci_existing.json"), "w"), indent=1, ensure_ascii=False)
for k, v in out.items(): print("%-36s n=%4d  %.1f%%  [%.1f, %.1f]" % (k, v["n"], 100 * v["acc"], 100 * v["lo"], 100 * v["hi"]))
