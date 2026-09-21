# --------------------------------------------------------------- imports--------------------------------------
#checking
# import os
# import random
# import shutil
# import uuid
# import zipfile

# import yaml
# from flask import Flask, jsonify, render_template, request, send_file

# try:
#     from PIL import Image
#     PIL_OK = True
# except Exception:
#     PIL_OK = False

# app = Flask(__name__)

# BASE = os.path.dirname(os.path.abspath(__file__))
# WORK_DIR = os.path.join(BASE, "workspace")
# os.makedirs(WORK_DIR, exist_ok=True)

# SPLITS = ["train", "valid", "test"]
# IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

# DB = {}  # dataset_id -> info


# # --------------------------------------------------------------- helpers
# def find_root(extract_path):
#     entries = [e for e in os.listdir(extract_path) if not e.startswith(".")]
#     if len(entries) == 1 and os.path.isdir(os.path.join(extract_path, entries[0])):
#         root = os.path.join(extract_path, entries[0])
#         inner = [e for e in os.listdir(root) if not e.startswith(".")]
#         if len(inner) == 1 and os.path.isdir(os.path.join(root, inner[0])):
#             sub = os.path.join(root, inner[0])
#             if all(os.path.isdir(os.path.join(sub, s)) for s in SPLITS):
#                 return sub
#         return root
#     return extract_path


# def list_images(d):
#     if not os.path.isdir(d):
#         return []
#     return sorted(f for f in os.listdir(d) if os.path.splitext(f)[1].lower() in IMG_EXTS)


# def list_labels(d):
#     if not os.path.isdir(d):
#         return []
#     return sorted(f for f in os.listdir(d) if f.lower().endswith(".txt"))


# def structure_errors(root):
#     """Step 2:1 / 7:1 - folder form + yaml presence check"""
#     errors = []
#     if not os.path.isfile(os.path.join(root, "data.yaml")):
#         errors.append("data.yaml is missing in dataset root")
#     for s in SPLITS:
#         d = os.path.join(root, s)
#         if not os.path.isdir(d):
#             errors.append(f"missing folder: {s}/")
#             continue
#         if not os.path.isdir(os.path.join(d, "images")):
#             errors.append(f"missing folder: {s}/images")
#         if not os.path.isdir(os.path.join(d, "labels")):
#             errors.append(f"missing folder: {s}/labels")
#     return errors


# def split_details(root):
#     """Step 2:2 / 7:2 - image & label name/count matching"""
#     details, problems = {}, []
#     for s in SPLITS:
#         idir, ldir = os.path.join(root, s, "images"), os.path.join(root, s, "labels")
#         imgs, lbls = list_images(idir), list_labels(ldir)
#         img_stems = {os.path.splitext(f)[0] for f in imgs}
#         lbl_stems = {os.path.splitext(f)[0] for f in lbls}
#         orphan_img = sorted(img_stems - lbl_stems)
#         orphan_lbl = sorted(lbl_stems - img_stems)
#         empty = 0
#         if os.path.isdir(ldir):
#             empty = sum(1 for f in lbls
#                         if os.path.getsize(os.path.join(ldir, f)) == 0)
#         details[s] = {"images": len(imgs), "labels": len(lbls),
#                       "missing_labels": len(orphan_img),
#                       "missing_images": len(orphan_lbl),
#                       "empty_labels": empty}
#         if orphan_img:
#             pv = ", ".join(orphan_img[:5]) + (" ..." if len(orphan_img) > 5 else "")
#             problems.append(f"{s}: {len(orphan_img)} image(s) WITHOUT label -> {pv}")
#         if orphan_lbl:
#             pv = ", ".join(orphan_lbl[:5]) + (" ..." if len(orphan_lbl) > 5 else "")
#             problems.append(f"{s}: {len(orphan_lbl)} label(s) WITHOUT image -> {pv}")
#     return details, problems


# def build_report(details, errors, warnings):
#     lines = ["DATASET SPECS", "-------------"]
#     for s in SPLITS:
#         d = details.get(s, {})
#         lines.append(s.upper())
#         lines.append(f"  Images         : {d.get('images', 0)}")
#         lines.append(f"  Labels         : {d.get('labels', 0)}")
#         lines.append(f"  Missing Labels : {d.get('missing_labels', 0)}")
#         lines.append(f"  Empty Labels   : {d.get('empty_labels', 0)}")
#     ti = sum(d.get("images", 0) for d in details.values())
#     tl = sum(d.get("labels", 0) for d in details.values())
#     lines.append(f"TOTAL : Images {ti} | Labels {tl}")
#     lines += ["", "ERRORS", "------"]
#     lines += errors if errors else ["No errors found"]
#     lines += ["", "WARNINGS", "--------"]
#     lines += warnings if warnings else ["No warnings"]
#     return "\n".join(lines)


# def read_yaml_at(path):
#     try:
#         with open(path, "r", encoding="utf-8") as f:
#             return yaml.safe_load(f) or {}
#     except Exception:
#         return {}


# def write_yaml_at(path, data):
#     with open(path, "w", encoding="utf-8") as f:
#         yaml.safe_dump(data, f, sort_keys=False, default_flow_style=False)


# def yaml_names(root):
#     data = read_yaml_at(os.path.join(root, "data.yaml"))
#     names = data.get("names", [])
#     if isinstance(names, dict):
#         return [str(names[k]) for k in sorted(names)]
#     if isinstance(names, list):
#         return [str(n) for n in names]
#     return []


# def zip_directory(folder, zip_path):
#     with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
#         for base, _dirs, files in os.walk(folder):
#             for fn in files:
#                 fp = os.path.join(base, fn)
#                 zf.write(fp, os.path.relpath(fp, folder))


# # --------------------------------------------------------------- routes
# @app.route("/")
# def index():
#     return render_template("index.html")

# KIND_MAP = {"pos": "object", "neg": "nonobject",
#             "positive": "object", "negative": "nonobject",
#             "object": "object", "nonobject": "nonobject"}

# @app.route("/api/upload/<kind>", methods=["POST"])
# def upload(kind):
#     kind = KIND_MAP.get(kind.lower(), kind)
#     if kind not in ("object", "nonobject"):
#         return jsonify(error="unknown dataset kind"), 400
#     f = request.files.get("file")
#     if not f or not f.filename.lower().endswith(".zip"):
#         return jsonify(error="please upload a .zip dataset"), 400
#     ds_id = uuid.uuid4().hex[:10]
#     ds_dir = os.path.join(WORK_DIR, ds_id)
#     os.makedirs(ds_dir, exist_ok=True)
#     zpath = os.path.join(ds_dir, "upload.zip")
#     f.save(zpath)
#     extract = os.path.join(ds_dir, "extracted")
#     try:
#         with zipfile.ZipFile(zpath) as zf:
#             zf.extractall(extract)
#     except zipfile.BadZipFile:
#         shutil.rmtree(ds_dir, ignore_errors=True)
#         return jsonify(error="invalid zip file"), 400
#     DB[ds_id] = {"kind": kind, "dir": ds_dir, "root": find_root(extract),
#                  "final": None, "zip": None, "folder_name": None}
#     return jsonify(dataset_id=ds_id, filename=f.filename)


# @app.route("/api/check/<ds_id>")
# def check(ds_id):
#     ds = DB.get(ds_id)
#     if not ds:
#         return jsonify(error="dataset not found - upload again"), 404
#     root = ds["root"]
#     errors = structure_errors(root)                       # step 2:1 / 7:1
#     details, problems, warnings = {}, [], []
#     if not errors:
#         details, problems = split_details(root)           # step 2:2 / 7:2
#     if ds["kind"] == "object":
#         empty_total = sum(d.get("empty_labels", 0) for d in details.values())
#         if empty_total:
#             warnings.append(f"{empty_total} empty label file(s) found")
#     all_errors = errors + problems
#     ok = len(all_errors) == 0                             # both same -> next step
#     return jsonify(ok=ok, errors=all_errors, warnings=warnings,
#                    details=details, report=build_report(details, all_errors, warnings))


# @app.route("/api/class/check", methods=["POST"])
# def class_check():
#     j = request.get_json(force=True)
#     ds = DB.get(j.get("dataset_id"))
#     cls = (j.get("class_name") or "").strip()
#     if not ds:
#         return jsonify(error="dataset not found"), 404
#     if not cls:
#         return jsonify(error="enter the class name"), 400
#     names = yaml_names(ds["root"])
#     if not names:
#         return jsonify(error="no class names found in data.yaml"), 400
#     matched = cls.lower() in [n.lower() for n in names]
#     return jsonify(matched=matched, class_name=cls, yaml_names=names)


# @app.route("/api/class/change", methods=["POST"])
# def class_change():
#     """Change class name in yaml file(s) of all folders"""
#     j = request.get_json(force=True)
#     ds = DB.get(j.get("dataset_id"))
#     cls = (j.get("class_name") or "").strip()
#     if not ds or not cls:
#         return jsonify(error="dataset id and class name required"), 400
#     changed = []
#     targets = [os.path.join(ds["root"], "data.yaml")]
#     for s in SPLITS:
#         targets.append(os.path.join(ds["root"], s, "data.yaml"))
#     for p in targets:
#         if os.path.isfile(p):
#             data = read_yaml_at(p)
#             data["names"] = [cls]
#             data["nc"] = 1
#             write_yaml_at(p, data)
#             changed.append(os.path.relpath(p, ds["root"]))
#     return jsonify(ok=bool(changed), changed=changed, class_name=cls)


# @app.route("/api/nonobject/clean", methods=["POST"])
# def clean_nonobject():
#     """Step 7:3 - empty label txt contents + delete yaml files"""
#     j = request.get_json(force=True)
#     ds = DB.get(j.get("dataset_id"))
#     if not ds or ds["kind"] != "nonobject":
#         return jsonify(error="non-object dataset not found"), 404
#     root = ds["root"]
#     emptied, created, removed_yaml = 0, 0, 0
#     for s in SPLITS:
#         idir, ldir = os.path.join(root, s, "images"), os.path.join(root, s, "labels")
#         if not os.path.isdir(ldir):
#             os.makedirs(ldir, exist_ok=True)
#         lbls = set(list_labels(ldir))
#         for f in list_images(idir):
#             stem = os.path.splitext(f)[0] + ".txt"
#             p = os.path.join(ldir, stem)
#             if stem not in lbls:
#                 open(p, "w").close()
#                 created += 1
#             elif os.path.getsize(p) > 0:
#                 open(p, "w").close()
#                 emptied += 1
#     for base, _dirs, files in os.walk(root):
#         for fn in files:
#             if fn.lower().endswith((".yaml", ".yml")):
#                 os.remove(os.path.join(base, fn))
#                 removed_yaml += 1
#     return jsonify(ok=True, emptied_labels=emptied,
#                    created_labels=created, removed_yaml=removed_yaml)


# @app.route("/api/combine", methods=["POST"])
# def combine():
#     """Step 5 / 8 - combine all folders as per dataset format"""
#     j = request.get_json(force=True)
#     ds = DB.get(j.get("dataset_id"))
#     if not ds:
#         return jsonify(error="dataset not found"), 404
#     root, final = ds["root"], os.path.join(ds["dir"], "final")
#     if os.path.isdir(final):
#         shutil.rmtree(final)
#     for s in SPLITS:
#         os.makedirs(os.path.join(final, s, "images"), exist_ok=True)
#         os.makedirs(os.path.join(final, s, "labels"), exist_ok=True)
#     counts = {}
#     for s in SPLITS:
#         imgs = list_images(os.path.join(root, s, "images"))
#         lbls = list_labels(os.path.join(root, s, "labels"))
#         lbl_set = set(lbls)
#         for f in imgs:
#             shutil.copy2(os.path.join(root, s, "images", f),
#                          os.path.join(final, s, "images", f))
#             stem = os.path.splitext(f)[0]
#             if ds["kind"] == "nonobject" and (stem + ".txt") not in lbl_set:
#                 open(os.path.join(final, s, "labels", stem + ".txt"), "w").close()
#         for f in lbls:
#             shutil.copy2(os.path.join(root, s, "labels", f),
#                          os.path.join(final, s, "labels", f))
#         counts[s] = {"images": len(imgs),
#                      "labels": len(imgs) if ds["kind"] == "nonobject" else len(lbls)}
#     names = []
#     if ds["kind"] == "object":
#         names = yaml_names(root)
#         write_yaml_at(os.path.join(final, "data.yaml"), {
#             "path": ".", "train": "train/images", "val": "valid/images",
#             "test": "test/images", "nc": len(names) or 1,
#             "names": names or ["object"]})
#     ds["final"] = final
#     totals = {"images": sum(c["images"] for c in counts.values()),
#               "labels": sum(c["labels"] for c in counts.values())}
#     return jsonify(ok=True, counts=counts, totals=totals, names=names)


# @app.route("/api/finalize", methods=["POST"])
# def finalize():
#     """Step 6 / 9 / final - enter folder name -> prepare download"""
#     j = request.get_json(force=True)
#     ds = DB.get(j.get("dataset_id"))
#     folder = (j.get("folder_name") or "").strip()
#     if not ds or not ds.get("final"):
#         return jsonify(error="combine the dataset first"), 400
#     if not folder:
#         return jsonify(error="enter the folder name"), 400
#     safe = "".join(c if (c.isalnum() or c in "-_") else "_" for c in folder).strip("_") or "dataset"
#     zpath = os.path.join(ds["dir"], safe + ".zip")
#     if os.path.exists(zpath):
#         os.remove(zpath)
#     zip_directory(ds["final"], zpath)
#     ds["zip"], ds["folder_name"] = zpath, safe
#     return jsonify(ok=True, folder_name=safe, download_url=f"/api/download/{j.get('dataset_id')}")


# @app.route("/api/download/<ds_id>")
# def download(ds_id):
#     ds = DB.get(ds_id)
#     if not ds or not ds.get("zip") or not os.path.isfile(ds["zip"]):
#         return jsonify(error="nothing to download yet"), 404
#     return send_file(ds["zip"], as_attachment=True,
#                      download_name=os.path.basename(ds["zip"]))


# @app.route("/api/balance/check", methods=["POST"])
# def balance_check():
#     """Step 10 - object 100% vs non-object 75-80% check"""
#     j = request.get_json(force=True)
#     pos, neg = DB.get(j.get("object_id")), DB.get(j.get("nonobject_id"))
#     if not pos or not neg or not pos.get("final") or not neg.get("final"):
#         return jsonify(error="finalize both datasets first"), 400

#     def total(ds):
#         return sum(len(list_images(os.path.join(ds["final"], s, "images")))
#                    for s in SPLITS)

#     pc, nc = total(pos), total(neg)
#     ratio = round(nc / pc * 100, 1) if pc else 0.0
#     target = int(round(pc * 0.78))
#     if 75 <= ratio <= 80:
#         verdict, action = True, "none"
#     elif ratio < 75:
#         verdict, action = False, "add"       # e.g. ~50% -> add more images
#     else:
#         verdict, action = False, "remove"    # above 80% -> remove images
#     return jsonify(ok=True, object_count=pc, nonobject_count=nc, ratio=ratio,
#                    balanced=verdict, action=action, target=target)


# @app.route("/api/balance/fix", methods=["POST"])
# def balance_fix():
#     j = request.get_json(force=True)
#     neg = DB.get(j.get("nonobject_id"))
#     action, target = j.get("action"), int(j.get("target") or 0)
#     if not neg or not neg.get("final"):
#         return jsonify(error="non-object dataset not ready"), 400
#     final = neg["final"]
#     pairs = []
#     for s in SPLITS:
#         for f in list_images(os.path.join(final, s, "images")):
#             pairs.append((s, f))
#     rnd, added, removed = random.Random(), 0, 0
#     if action == "remove" and len(pairs) > target:
#         rnd.shuffle(pairs)
#         for s, f in pairs[: len(pairs) - target]:
#             ipath = os.path.join(final, s, "images", f)
#             lpath = os.path.join(final, s, "labels", os.path.splitext(f)[0] + ".txt")
#             if os.path.exists(ipath):
#                 os.remove(ipath)
#             if os.path.exists(lpath):
#                 os.remove(lpath)
#             removed += 1
#     elif action == "add" and len(pairs) < target:
#         need, i = target - len(pairs), 0
#         while added < need and pairs:
#             s, f = pairs[i % len(pairs)]
#             stem, ext = os.path.splitext(f)
#             new_img = f"{stem}_aug{added:04d}{ext}"
#             src_i = os.path.join(final, s, "images", f)
#             dst_i = os.path.join(final, s, "images", new_img)
#             if PIL_OK:
#                 try:
#                     im = Image.open(src_i)
#                     if im.mode not in ("RGB", "L"):
#                         im = im.convert("RGB")
#                     im.transpose(Image.FLIP_LEFT_RIGHT).save(dst_i)
#                 except Exception:
#                     shutil.copy2(src_i, dst_i)
#             else:
#                 shutil.copy2(src_i, dst_i)
#             open(os.path.join(final, s, "labels",
#                  os.path.splitext(new_img)[0] + ".txt"), "w").close()
#             added += 1
#             i += 1
#     counts = {}
#     for s in SPLITS:
#         counts[s] = {"images": len(list_images(os.path.join(final, s, "images"))),
#                      "labels": len(list_labels(os.path.join(final, s, "labels")))}
#     return jsonify(ok=True, added=added, removed=removed, counts=counts,
#                    total=sum(c["images"] for c in counts.values()))


# @app.route("/api/train/combine", methods=["POST"])
# def train_combine():
#     """Merge finalized positive + negative datasets into train dataset"""
#     j = request.get_json(force=True)
#     pos, neg = DB.get(j.get("object_id")), DB.get(j.get("nonobject_id"))
#     if not pos or not neg or not pos.get("final") or not neg.get("final"):
#         return jsonify(error="finalize both datasets first"), 400
#     out = os.path.join(WORK_DIR, "train_" + uuid.uuid4().hex[:8])
#     counts = {}
#     for s in SPLITS:
#         os.makedirs(os.path.join(out, s, "images"), exist_ok=True)
#         os.makedirs(os.path.join(out, s, "labels"), exist_ok=True)
#         n = 0
#         for src in (pos["final"], neg["final"]):
#             idir, ldir = os.path.join(src, s, "images"), os.path.join(src, s, "labels")
#             for f in list_images(idir):
#                 stem, ext = os.path.splitext(f)
#                 dst = f
#                 while os.path.exists(os.path.join(out, s, "images", dst)):
#                     dst = f"{stem}_{uuid.uuid4().hex[:4]}{ext}"
#                 shutil.copy2(os.path.join(idir, f),
#                              os.path.join(out, s, "images", dst))
#                 lbl_src = os.path.join(ldir, stem + ".txt")
#                 lbl_dst = os.path.splitext(dst)[0] + ".txt"
#                 if os.path.isfile(lbl_src):
#                     shutil.copy2(lbl_src, os.path.join(out, s, "labels", lbl_dst))
#                 else:
#                     open(os.path.join(out, s, "labels", lbl_dst), "w").close()
#                 n += 1
#         counts[s] = {"images": n,
#                      "labels": len(list_labels(os.path.join(out, s, "labels")))}
#     names = yaml_names(pos["root"])
#     write_yaml_at(os.path.join(out, "data.yaml"), {
#         "path": ".", "train": "train/images", "val": "valid/images",
#         "test": "test/images", "nc": len(names) or 1,
#         "names": names or ["object"]})
#     tid = "train_" + uuid.uuid4().hex[:8]
#     DB[tid] = {"kind": "train", "dir": out, "root": out, "final": out,
#                "zip": None, "folder_name": None}
#     totals = {"images": sum(c["images"] for c in counts.values()),
#               "labels": sum(c["labels"] for c in counts.values())}
#     return jsonify(ok=True, train_id=tid, counts=counts, totals=totals, names=names)


# if __name__ == "__main__":
#     app.run(debug=True, port=5000)
    
    
# ---------------------------------------------------------------------------------------------------    
    
# import os
# import random
# import shutil
# import uuid
# import zipfile

# import yaml
# from flask import Flask, jsonify, render_template, request, send_file

# try:
#     from PIL import Image
#     PIL_OK = True
# except Exception:
#     PIL_OK = False

# app = Flask(__name__)

# BASE = os.path.dirname(os.path.abspath(__file__))
# WORK_DIR = os.path.join(BASE, "workspace")
# os.makedirs(WORK_DIR, exist_ok=True)

# SPLITS = ["train", "valid", "test"]
# IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

# # batch_id -> { kind, dir, parts: {part_id: {filename, root}}, final, zip, folder_name }
# DB = {}


# # --------------------------------------------------------------- helpers
# def find_root(extract_path):
#     """Zip files are often wrapped in one or two extra folders - drill down
#     until we find the level that actually contains train/valid/test."""
#     entries = [e for e in os.listdir(extract_path) if not e.startswith(".")]
#     if len(entries) == 1 and os.path.isdir(os.path.join(extract_path, entries[0])):
#         root = os.path.join(extract_path, entries[0])
#         inner = [e for e in os.listdir(root) if not e.startswith(".")]
#         if len(inner) == 1 and os.path.isdir(os.path.join(root, inner[0])):
#             sub = os.path.join(root, inner[0])
#             if all(os.path.isdir(os.path.join(sub, s)) for s in SPLITS):
#                 return sub
#         return root
#     return extract_path


# def list_images(d):
#     if not os.path.isdir(d):
#         return []
#     return sorted(f for f in os.listdir(d) if os.path.splitext(f)[1].lower() in IMG_EXTS)


# def list_labels(d):
#     if not os.path.isdir(d):
#         return []
#     return sorted(f for f in os.listdir(d) if f.lower().endswith(".txt"))


# def structure_errors(root):
#     """folder form + yaml presence check, per uploaded zip"""
#     errors = []
#     if not os.path.isfile(os.path.join(root, "data.yaml")):
#         errors.append("data.yaml is missing in dataset root")
#     for s in SPLITS:
#         d = os.path.join(root, s)
#         if not os.path.isdir(d):
#             errors.append(f"missing folder: {s}/")
#             continue
#         if not os.path.isdir(os.path.join(d, "images")):
#             errors.append(f"missing folder: {s}/images")
#         if not os.path.isdir(os.path.join(d, "labels")):
#             errors.append(f"missing folder: {s}/labels")
#     return errors


# def split_details(root):
#     """image & label name/count matching, per uploaded zip"""
#     details, problems = {}, []
#     for s in SPLITS:
#         idir, ldir = os.path.join(root, s, "images"), os.path.join(root, s, "labels")
#         imgs, lbls = list_images(idir), list_labels(ldir)
#         img_stems = {os.path.splitext(f)[0] for f in imgs}
#         lbl_stems = {os.path.splitext(f)[0] for f in lbls}
#         orphan_img = sorted(img_stems - lbl_stems)
#         orphan_lbl = sorted(lbl_stems - img_stems)
#         empty = 0
#         if os.path.isdir(ldir):
#             empty = sum(1 for f in lbls if os.path.getsize(os.path.join(ldir, f)) == 0)
#         details[s] = {"images": len(imgs), "labels": len(lbls),
#                       "missing_labels": len(orphan_img),
#                       "missing_images": len(orphan_lbl),
#                       "empty_labels": empty}
#         if orphan_img:
#             pv = ", ".join(orphan_img[:5]) + (" ..." if len(orphan_img) > 5 else "")
#             problems.append(f"{s}: {len(orphan_img)} image(s) WITHOUT label -> {pv}")
#         if orphan_lbl:
#             pv = ", ".join(orphan_lbl[:5]) + (" ..." if len(orphan_lbl) > 5 else "")
#             problems.append(f"{s}: {len(orphan_lbl)} label(s) WITHOUT image -> {pv}")
#     return details, problems


# def build_report(title, details, errors, warnings):
#     lines = [title, "-" * max(len(title), 12)]
#     for s in SPLITS:
#         d = details.get(s, {})
#         lines.append(s.upper())
#         lines.append(f"  Images         : {d.get('images', 0)}")
#         lines.append(f"  Labels         : {d.get('labels', 0)}")
#         lines.append(f"  Missing Labels : {d.get('missing_labels', 0)}")
#         lines.append(f"  Empty Labels   : {d.get('empty_labels', 0)}")
#     ti = sum(d.get("images", 0) for d in details.values())
#     tl = sum(d.get("labels", 0) for d in details.values())
#     lines.append(f"TOTAL : Images {ti} | Labels {tl}")
#     lines += ["", "ERRORS", "------"]
#     lines += errors if errors else ["No errors found"]
#     lines += ["", "WARNINGS", "--------"]
#     lines += warnings if warnings else ["No warnings"]
#     return "\n".join(lines)


# def merge_totals(details_list):
#     agg = {s: {"images": 0, "labels": 0, "missing_labels": 0,
#                "missing_images": 0, "empty_labels": 0} for s in SPLITS}
#     for details in details_list:
#         for s in SPLITS:
#             d = details.get(s, {})
#             for k in agg[s]:
#                 agg[s][k] += d.get(k, 0)
#     return agg


# def read_yaml_at(path):
#     try:
#         with open(path, "r", encoding="utf-8") as f:
#             return yaml.safe_load(f) or {}
#     except Exception:
#         return {}


# def write_yaml_at(path, data):
#     with open(path, "w", encoding="utf-8") as f:
#         yaml.safe_dump(data, f, sort_keys=False, default_flow_style=False)


# def yaml_names(root):
#     data = read_yaml_at(os.path.join(root, "data.yaml"))
#     names = data.get("names", [])
#     if isinstance(names, dict):
#         return [str(names[k]) for k in sorted(names)]
#     if isinstance(names, list):
#         return [str(n) for n in names]
#     return []


# def zip_directory(folder, zip_path):
#     with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
#         for base, _dirs, files in os.walk(folder):
#             for fn in files:
#                 fp = os.path.join(base, fn)
#                 zf.write(fp, os.path.relpath(fp, folder))


# # --------------------------------------------------------------- pages
# @app.route("/")
# def index():
#     return render_template("index.html")


# KIND_MAP = {"pos": "object", "neg": "nonobject",
#             "positive": "object", "negative": "nonobject",
#             "object": "object", "nonobject": "nonobject"}


# # --------------------------------------------------------------- 1. upload (MULTIPLE zips)
# @app.route("/api/upload/<kind>", methods=["POST"])
# def upload(kind):
#     """Accepts several .zip files at once (field name 'files').
#     Every call starts a fresh batch for that panel - each zip becomes
#     one 'part' of the batch, so many dataset folders can be checked,
#     class-matched and finally combined into ONE single output folder."""
#     kind = KIND_MAP.get(kind.lower(), kind)
#     if kind not in ("object", "nonobject"):
#         return jsonify(error="unknown dataset kind"), 400

#     files = request.files.getlist("files") or request.files.getlist("file")
#     files = [f for f in files if f and f.filename]
#     if not files:
#         return jsonify(error="please choose at least one .zip dataset"), 400
#     bad = [f.filename for f in files if not f.filename.lower().endswith(".zip")]
#     if bad:
#         return jsonify(error=f"only .zip files are accepted: {', '.join(bad)}"), 400

#     batch_id = uuid.uuid4().hex[:10]
#     batch_dir = os.path.join(WORK_DIR, batch_id)
#     os.makedirs(batch_dir, exist_ok=True)

#     parts = {}
#     for f in files:
#         part_id = uuid.uuid4().hex[:8]
#         part_dir = os.path.join(batch_dir, "parts", part_id)
#         os.makedirs(part_dir, exist_ok=True)
#         zpath = os.path.join(part_dir, "upload.zip")
#         f.save(zpath)
#         extract = os.path.join(part_dir, "extracted")
#         try:
#             with zipfile.ZipFile(zpath) as zf:
#                 zf.extractall(extract)
#         except zipfile.BadZipFile:
#             shutil.rmtree(batch_dir, ignore_errors=True)
#             return jsonify(error=f"invalid zip file: {f.filename}"), 400
#         parts[part_id] = {"filename": f.filename, "root": find_root(extract)}

#     DB[batch_id] = {"kind": kind, "dir": batch_dir, "parts": parts,
#                      "final": None, "zip": None, "folder_name": None}
#     return jsonify(batch_id=batch_id,
#                     files=[{"part_id": pid, "filename": p["filename"]} for pid, p in parts.items()])


# # --------------------------------------------------------------- 2. check (per zip + combined)
# @app.route("/api/check/<batch_id>")
# def check(batch_id):
#     ds = DB.get(batch_id)
#     if not ds:
#         return jsonify(error="dataset not found - upload again"), 404

#     per_file, all_details = [], []
#     for part in ds["parts"].values():
#         root = part["root"]
#         errors = structure_errors(root)                       # 2:1 / 7:1 per zip
#         details, problems, warnings = {}, [], []
#         if not errors:
#             details, problems = split_details(root)           # 2:2 / 7:2 per zip
#             if ds["kind"] == "object":
#                 empty_total = sum(d.get("empty_labels", 0) for d in details.values())
#                 if empty_total:
#                     warnings.append(f"{empty_total} empty label file(s) found")
#         file_errors = errors + problems
#         all_details.append(details)
#         per_file.append({
#             "filename": part["filename"],
#             "ok": len(file_errors) == 0,
#             "errors": file_errors,
#             "warnings": warnings,
#             "details": details,
#             "report": build_report(part["filename"], details, file_errors, warnings),
#         })

#     ok = all(pf["ok"] for pf in per_file)                     # every zip must pass
#     agg_details = merge_totals(all_details) if ok else {}
#     agg_errors = [] if ok else ["fix the errors shown for each file below before continuing"]
#     return jsonify(ok=ok, files=per_file,
#                     aggregate={"details": agg_details,
#                                "report": build_report("COMBINED TOTAL (all files)", agg_details, agg_errors, [])})


# # --------------------------------------------------------------- 3. class name check/change (all zips)
# @app.route("/api/class/check", methods=["POST"])
# def class_check():
#     j = request.get_json(force=True)
#     ds = DB.get(j.get("batch_id"))
#     cls = (j.get("class_name") or "").strip()
#     if not ds:
#         return jsonify(error="dataset not found"), 404
#     if not cls:
#         return jsonify(error="enter the class name"), 400

#     per_file, all_matched = [], True
#     for part in ds["parts"].values():
#         names = yaml_names(part["root"])
#         matched = bool(names) and cls.lower() in [n.lower() for n in names]
#         all_matched = all_matched and matched
#         per_file.append({"filename": part["filename"], "yaml_names": names, "matched": matched})
#     return jsonify(matched=all_matched, class_name=cls, files=per_file)


# @app.route("/api/class/change", methods=["POST"])
# def class_change():
#     """Change class name in the yaml file(s) of every uploaded folder"""
#     j = request.get_json(force=True)
#     ds = DB.get(j.get("batch_id"))
#     cls = (j.get("class_name") or "").strip()
#     if not ds or not cls:
#         return jsonify(error="dataset id and class name required"), 400
#     changed = []
#     for part in ds["parts"].values():
#         root = part["root"]
#         targets = [os.path.join(root, "data.yaml")]
#         for s in SPLITS:
#             targets.append(os.path.join(root, s, "data.yaml"))
#         for p in targets:
#             if os.path.isfile(p):
#                 data = read_yaml_at(p)
#                 data["names"] = [cls]
#                 data["nc"] = 1
#                 write_yaml_at(p, data)
#                 changed.append(f"{part['filename']} -> {os.path.relpath(p, root)}")
#     return jsonify(ok=bool(changed), changed=changed, class_name=cls)


# # --------------------------------------------------------------- 7:3 non-object cleaning (all zips)
# @app.route("/api/nonobject/clean", methods=["POST"])
# def clean_nonobject():
#     j = request.get_json(force=True)
#     ds = DB.get(j.get("batch_id"))
#     if not ds or ds["kind"] != "nonobject":
#         return jsonify(error="non-object dataset not found"), 404
#     emptied = created = removed_yaml = 0
#     for part in ds["parts"].values():
#         root = part["root"]
#         for s in SPLITS:
#             idir, ldir = os.path.join(root, s, "images"), os.path.join(root, s, "labels")
#             if not os.path.isdir(ldir):
#                 os.makedirs(ldir, exist_ok=True)
#             lbls = set(list_labels(ldir))
#             for f in list_images(idir):
#                 stem = os.path.splitext(f)[0] + ".txt"
#                 p = os.path.join(ldir, stem)
#                 if stem not in lbls:
#                     open(p, "w").close()
#                     created += 1
#                 elif os.path.getsize(p) > 0:
#                     open(p, "w").close()
#                     emptied += 1
#         for base, _dirs, files in os.walk(root):
#             for fn in files:
#                 if fn.lower().endswith((".yaml", ".yml")):
#                     os.remove(os.path.join(base, fn))
#                     removed_yaml += 1
#     return jsonify(ok=True, emptied_labels=emptied, created_labels=created, removed_yaml=removed_yaml)


# # --------------------------------------------------------------- 5 / 8. combine ALL zips into ONE folder
# @app.route("/api/combine", methods=["POST"])
# def combine():
#     j = request.get_json(force=True)
#     ds = DB.get(j.get("batch_id"))
#     if not ds:
#         return jsonify(error="dataset not found"), 404

#     final = os.path.join(ds["dir"], "final")
#     if os.path.isdir(final):
#         shutil.rmtree(final)
#     for s in SPLITS:
#         os.makedirs(os.path.join(final, s, "images"), exist_ok=True)
#         os.makedirs(os.path.join(final, s, "labels"), exist_ok=True)

#     counts = {s: {"images": 0, "labels": 0} for s in SPLITS}
#     names = []
#     for part in ds["parts"].values():
#         root = part["root"]
#         if ds["kind"] == "object" and not names:
#             names = yaml_names(root)
#         for s in SPLITS:
#             idir, ldir = os.path.join(root, s, "images"), os.path.join(root, s, "labels")
#             for f in list_images(idir):
#                 stem, ext = os.path.splitext(f)
#                 dst_name = f
#                 while os.path.exists(os.path.join(final, s, "images", dst_name)):
#                     dst_name = f"{stem}_{uuid.uuid4().hex[:6]}{ext}"  # avoid clashes between zips
#                 shutil.copy2(os.path.join(idir, f), os.path.join(final, s, "images", dst_name))
#                 dst_stem = os.path.splitext(dst_name)[0]
#                 src_lbl = os.path.join(ldir, stem + ".txt")
#                 dst_lbl = os.path.join(final, s, "labels", dst_stem + ".txt")
#                 if os.path.isfile(src_lbl):
#                     shutil.copy2(src_lbl, dst_lbl)
#                 elif ds["kind"] == "nonobject":
#                     open(dst_lbl, "w").close()
#                 counts[s]["images"] += 1
#     for s in SPLITS:
#         counts[s]["labels"] = len(list_labels(os.path.join(final, s, "labels")))

#     if ds["kind"] == "object":
#         write_yaml_at(os.path.join(final, "data.yaml"), {
#             "path": ".", "train": "train/images", "val": "valid/images",
#             "test": "test/images", "nc": len(names) or 1,
#             "names": names or ["object"]})

#     ds["final"] = final
#     totals = {"images": sum(c["images"] for c in counts.values()),
#               "labels": sum(c["labels"] for c in counts.values())}
#     return jsonify(ok=True, counts=counts, totals=totals, names=names, source_files=len(ds["parts"]))


# # --------------------------------------------------------------- 6 / 9. finalize + download (single folder/zip)
# @app.route("/api/finalize", methods=["POST"])
# def finalize():
#     j = request.get_json(force=True)
#     ds = DB.get(j.get("batch_id"))
#     folder = (j.get("folder_name") or "").strip()
#     if not ds or not ds.get("final"):
#         return jsonify(error="combine the dataset first"), 400
#     if not folder:
#         return jsonify(error="enter the folder name"), 400
#     safe = "".join(c if (c.isalnum() or c in "-_") else "_" for c in folder).strip("_") or "dataset"
#     zpath = os.path.join(ds["dir"], safe + ".zip")
#     if os.path.exists(zpath):
#         os.remove(zpath)
#     zip_directory(ds["final"], zpath)
#     ds["zip"], ds["folder_name"] = zpath, safe
#     return jsonify(ok=True, folder_name=safe, download_url=f"/api/download/{j.get('batch_id')}")


# @app.route("/api/download/<batch_id>")
# def download(batch_id):
#     ds = DB.get(batch_id)
#     if not ds or not ds.get("zip") or not os.path.isfile(ds["zip"]):
#         return jsonify(error="nothing to download yet"), 404
#     return send_file(ds["zip"], as_attachment=True, download_name=os.path.basename(ds["zip"]))


# # --------------------------------------------------------------- 10. balance check / fix
# @app.route("/api/balance/check", methods=["POST"])
# def balance_check():
#     j = request.get_json(force=True)
#     pos, neg = DB.get(j.get("object_batch_id")), DB.get(j.get("nonobject_batch_id"))
#     if not pos or not neg or not pos.get("final") or not neg.get("final"):
#         return jsonify(error="finalize both datasets first"), 400

#     def total(ds):
#         return sum(len(list_images(os.path.join(ds["final"], s, "images"))) for s in SPLITS)

#     pc, nc = total(pos), total(neg)
#     ratio = round(nc / pc * 100, 1) if pc else 0.0
#     target = int(round(pc * 0.78))
#     if 75 <= ratio <= 80:
#         verdict, action = True, "none"
#     elif ratio < 75:
#         verdict, action = False, "add"
#     else:
#         verdict, action = False, "remove"
#     return jsonify(ok=True, object_count=pc, nonobject_count=nc, ratio=ratio,
#                    balanced=verdict, action=action, target=target)


# @app.route("/api/balance/fix", methods=["POST"])
# def balance_fix():
#     j = request.get_json(force=True)
#     neg = DB.get(j.get("nonobject_batch_id"))
#     action, target = j.get("action"), int(j.get("target") or 0)
#     if not neg or not neg.get("final"):
#         return jsonify(error="non-object dataset not ready"), 400
#     final = neg["final"]
#     pairs = []
#     for s in SPLITS:
#         for f in list_images(os.path.join(final, s, "images")):
#             pairs.append((s, f))
#     rnd, added, removed = random.Random(), 0, 0
#     if action == "remove" and len(pairs) > target:
#         rnd.shuffle(pairs)
#         for s, f in pairs[: len(pairs) - target]:
#             ipath = os.path.join(final, s, "images", f)
#             lpath = os.path.join(final, s, "labels", os.path.splitext(f)[0] + ".txt")
#             if os.path.exists(ipath):
#                 os.remove(ipath)
#             if os.path.exists(lpath):
#                 os.remove(lpath)
#             removed += 1
#     elif action == "add" and len(pairs) < target:
#         need, i = target - len(pairs), 0
#         while added < need and pairs:
#             s, f = pairs[i % len(pairs)]
#             stem, ext = os.path.splitext(f)
#             new_img = f"{stem}_aug{added:04d}{ext}"
#             src_i = os.path.join(final, s, "images", f)
#             dst_i = os.path.join(final, s, "images", new_img)
#             if PIL_OK:
#                 try:
#                     im = Image.open(src_i)
#                     if im.mode not in ("RGB", "L"):
#                         im = im.convert("RGB")
#                     im.transpose(Image.FLIP_LEFT_RIGHT).save(dst_i)
#                 except Exception:
#                     shutil.copy2(src_i, dst_i)
#             else:
#                 shutil.copy2(src_i, dst_i)
#             open(os.path.join(final, s, "labels", os.path.splitext(new_img)[0] + ".txt"), "w").close()
#             added += 1
#             i += 1
#     counts = {}
#     for s in SPLITS:
#         counts[s] = {"images": len(list_images(os.path.join(final, s, "images"))),
#                      "labels": len(list_labels(os.path.join(final, s, "labels")))}
#     return jsonify(ok=True, added=added, removed=removed, counts=counts,
#                    total=sum(c["images"] for c in counts.values()))


# # --------------------------------------------------------------- final: merge object + non-object -> train dataset
# @app.route("/api/train/combine", methods=["POST"])
# def train_combine():
#     j = request.get_json(force=True)
#     pos, neg = DB.get(j.get("object_batch_id")), DB.get(j.get("nonobject_batch_id"))
#     if not pos or not neg or not pos.get("final") or not neg.get("final"):
#         return jsonify(error="finalize both datasets first"), 400
#     out = os.path.join(WORK_DIR, "train_" + uuid.uuid4().hex[:8])
#     counts = {}
#     for s in SPLITS:
#         os.makedirs(os.path.join(out, s, "images"), exist_ok=True)
#         os.makedirs(os.path.join(out, s, "labels"), exist_ok=True)
#         n = 0
#         for src in (pos["final"], neg["final"]):
#             idir, ldir = os.path.join(src, s, "images"), os.path.join(src, s, "labels")
#             for f in list_images(idir):
#                 stem, ext = os.path.splitext(f)
#                 dst = f
#                 while os.path.exists(os.path.join(out, s, "images", dst)):
#                     dst = f"{stem}_{uuid.uuid4().hex[:4]}{ext}"
#                 shutil.copy2(os.path.join(idir, f), os.path.join(out, s, "images", dst))
#                 lbl_src = os.path.join(ldir, stem + ".txt")
#                 lbl_dst = os.path.splitext(dst)[0] + ".txt"
#                 if os.path.isfile(lbl_src):
#                     shutil.copy2(lbl_src, os.path.join(out, s, "labels", lbl_dst))
#                 else:
#                     open(os.path.join(out, s, "labels", lbl_dst), "w").close()
#                 n += 1
#         counts[s] = {"images": n, "labels": len(list_labels(os.path.join(out, s, "labels")))}
#     names = yaml_names(pos["final"])
#     write_yaml_at(os.path.join(out, "data.yaml"), {
#         "path": ".", "train": "train/images", "val": "valid/images",
#         "test": "test/images", "nc": len(names) or 1,
#         "names": names or ["object"]})
#     tid = "train_" + uuid.uuid4().hex[:8]
#     DB[tid] = {"kind": "train", "dir": out, "parts": {}, "final": out, "zip": None, "folder_name": None}
#     totals = {"images": sum(c["images"] for c in counts.values()),
#               "labels": sum(c["labels"] for c in counts.values())}
#     return jsonify(ok=True, batch_id=tid, counts=counts, totals=totals, names=names)


# if __name__ == "__main__":
#     app.run(debug=True, port=5000)
# ---------------------------------------------------------------------------------------------------

import os
import random
import shutil
import threading
import time
import uuid
import zipfile

import yaml
from flask import Flask, jsonify, render_template, request, send_file

try:
    from PIL import Image
    PIL_OK = True
except Exception:
    PIL_OK = False

app = Flask(__name__)

BASE = os.path.dirname(os.path.abspath(__file__))
WORK_DIR = os.path.join(BASE, "workspace")
os.makedirs(WORK_DIR, exist_ok=True)

SPLITS = ["train", "valid", "test"]
IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

# batch_id -> { kind, dir, parts: {part_id: {filename, root}}, final, zip, folder_name }
DB = {}

# One lock per batch_id so a double-click / duplicate request can never run
# combine (or finalize) twice at once on the same folder - that race is what
# causes "directory not empty" / "file not found" errors on Windows.
_LOCKS_GUARD = threading.Lock()
_BATCH_LOCKS = {}


def get_lock(batch_id):
    with _LOCKS_GUARD:
        if batch_id not in _BATCH_LOCKS:
            _BATCH_LOCKS[batch_id] = threading.Lock()
        return _BATCH_LOCKS[batch_id]


def safe_rmtree(path, attempts=6, delay=0.25):
    """shutil.rmtree, but retries briefly on Windows when a file is still
    momentarily locked (antivirus / indexer) instead of crashing the request."""
    if not os.path.isdir(path):
        return
    last_err = None
    for i in range(attempts):
        try:
            shutil.rmtree(path)
            return
        except OSError as e:
            last_err = e
            time.sleep(delay)
    raise last_err


# --------------------------------------------------------------- helpers
def find_root(extract_path):
    """Zip files are often wrapped in one or two extra folders - drill down
    until we find the level that actually contains train/valid/test."""
    entries = [e for e in os.listdir(extract_path) if not e.startswith(".")]
    if len(entries) == 1 and os.path.isdir(os.path.join(extract_path, entries[0])):
        root = os.path.join(extract_path, entries[0])
        inner = [e for e in os.listdir(root) if not e.startswith(".")]
        if len(inner) == 1 and os.path.isdir(os.path.join(root, inner[0])):
            sub = os.path.join(root, inner[0])
            if all(os.path.isdir(os.path.join(sub, s)) for s in SPLITS):
                return sub
        return root
    return extract_path


def list_images(d):
    if not os.path.isdir(d):
        return []
    return sorted(f for f in os.listdir(d) if os.path.splitext(f)[1].lower() in IMG_EXTS)


def list_labels(d):
    if not os.path.isdir(d):
        return []
    return sorted(f for f in os.listdir(d) if f.lower().endswith(".txt"))


def structure_errors(root):
    """folder form + yaml presence check, per uploaded zip"""
    errors = []
    if not os.path.isfile(os.path.join(root, "data.yaml")):
        errors.append("data.yaml is missing in dataset root")
    for s in SPLITS:
        d = os.path.join(root, s)
        if not os.path.isdir(d):
            errors.append(f"missing folder: {s}/")
            continue
        if not os.path.isdir(os.path.join(d, "images")):
            errors.append(f"missing folder: {s}/images")
        if not os.path.isdir(os.path.join(d, "labels")):
            errors.append(f"missing folder: {s}/labels")
    return errors


def split_details(root):
    """image & label name/count matching, per uploaded zip"""
    details, problems = {}, []
    for s in SPLITS:
        idir, ldir = os.path.join(root, s, "images"), os.path.join(root, s, "labels")
        imgs, lbls = list_images(idir), list_labels(ldir)
        img_stems = {os.path.splitext(f)[0] for f in imgs}
        lbl_stems = {os.path.splitext(f)[0] for f in lbls}
        orphan_img = sorted(img_stems - lbl_stems)
        orphan_lbl = sorted(lbl_stems - img_stems)
        empty = 0
        if os.path.isdir(ldir):
            empty = sum(1 for f in lbls if os.path.getsize(os.path.join(ldir, f)) == 0)
        details[s] = {"images": len(imgs), "labels": len(lbls),
                      "missing_labels": len(orphan_img),
                      "missing_images": len(orphan_lbl),
                      "empty_labels": empty}
        if orphan_img:
            pv = ", ".join(orphan_img[:5]) + (" ..." if len(orphan_img) > 5 else "")
            problems.append(f"{s}: {len(orphan_img)} image(s) WITHOUT label -> {pv}")
        if orphan_lbl:
            pv = ", ".join(orphan_lbl[:5]) + (" ..." if len(orphan_lbl) > 5 else "")
            problems.append(f"{s}: {len(orphan_lbl)} label(s) WITHOUT image -> {pv}")
    return details, problems


def build_report(title, details, errors, warnings):
    lines = [title, "-" * max(len(title), 12)]
    for s in SPLITS:
        d = details.get(s, {})
        lines.append(s.upper())
        lines.append(f"  Images         : {d.get('images', 0)}")
        lines.append(f"  Labels         : {d.get('labels', 0)}")
        lines.append(f"  Missing Labels : {d.get('missing_labels', 0)}")
        lines.append(f"  Empty Labels   : {d.get('empty_labels', 0)}")
    ti = sum(d.get("images", 0) for d in details.values())
    tl = sum(d.get("labels", 0) for d in details.values())
    lines.append(f"TOTAL : Images {ti} | Labels {tl}")
    lines += ["", "ERRORS", "------"]
    lines += errors if errors else ["No errors found"]
    lines += ["", "WARNINGS", "--------"]
    lines += warnings if warnings else ["No warnings"]
    return "\n".join(lines)


def merge_totals(details_list):
    agg = {s: {"images": 0, "labels": 0, "missing_labels": 0,
               "missing_images": 0, "empty_labels": 0} for s in SPLITS}
    for details in details_list:
        for s in SPLITS:
            d = details.get(s, {})
            for k in agg[s]:
                agg[s][k] += d.get(k, 0)
    return agg


def read_yaml_at(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}


def write_yaml_at(path, data):
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False, default_flow_style=False)


def yaml_names(root):
    data = read_yaml_at(os.path.join(root, "data.yaml"))
    names = data.get("names", [])
    if isinstance(names, dict):
        return [str(names[k]) for k in sorted(names)]
    if isinstance(names, list):
        return [str(n) for n in names]
    return []


def zip_directory(folder, zip_path):
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for base, _dirs, files in os.walk(folder):
            for fn in files:
                fp = os.path.join(base, fn)
                zf.write(fp, os.path.relpath(fp, folder))


# --------------------------------------------------------------- pages
@app.route("/")
def index():
    return render_template("index.html")


KIND_MAP = {"pos": "object", "neg": "nonobject",
            "positive": "object", "negative": "nonobject",
            "object": "object", "nonobject": "nonobject"}


# --------------------------------------------------------------- 1. upload (MULTIPLE zips)
@app.route("/api/upload/<kind>", methods=["POST"])
def upload(kind):
    """Accepts several .zip files at once (field name 'files').
    Every call starts a fresh batch for that panel - each zip becomes
    one 'part' of the batch, so many dataset folders can be checked,
    class-matched and finally combined into ONE single output folder."""
    kind = KIND_MAP.get(kind.lower(), kind)
    if kind not in ("object", "nonobject"):
        return jsonify(error="unknown dataset kind"), 400

    files = request.files.getlist("files") or request.files.getlist("file")
    files = [f for f in files if f and f.filename]
    if not files:
        return jsonify(error="please choose at least one .zip dataset"), 400
    bad = [f.filename for f in files if not f.filename.lower().endswith(".zip")]
    if bad:
        return jsonify(error=f"only .zip files are accepted: {', '.join(bad)}"), 400

    batch_id = uuid.uuid4().hex[:10]
    batch_dir = os.path.join(WORK_DIR, batch_id)
    os.makedirs(batch_dir, exist_ok=True)

    parts = {}
    for f in files:
        part_id = uuid.uuid4().hex[:8]
        part_dir = os.path.join(batch_dir, "parts", part_id)
        os.makedirs(part_dir, exist_ok=True)
        zpath = os.path.join(part_dir, "upload.zip")
        f.save(zpath)
        extract = os.path.join(part_dir, "extracted")
        try:
            with zipfile.ZipFile(zpath) as zf:
                zf.extractall(extract)
        except zipfile.BadZipFile:
            shutil.rmtree(batch_dir, ignore_errors=True)
            return jsonify(error=f"invalid zip file: {f.filename}"), 400
        parts[part_id] = {"filename": f.filename, "root": find_root(extract)}

    DB[batch_id] = {"kind": kind, "dir": batch_dir, "parts": parts,
                     "final": None, "zip": None, "folder_name": None}
    return jsonify(batch_id=batch_id,
                    files=[{"part_id": pid, "filename": p["filename"]} for pid, p in parts.items()])


# --------------------------------------------------------------- 2. check (per zip + combined)
@app.route("/api/check/<batch_id>")
def check(batch_id):
    ds = DB.get(batch_id)
    if not ds:
        return jsonify(error="dataset not found - upload again"), 404

    per_file, all_details = [], []
    for part in ds["parts"].values():
        root = part["root"]
        errors = structure_errors(root)                       # 2:1 / 7:1 per zip
        details, problems, warnings = {}, [], []
        if not errors:
            details, problems = split_details(root)           # 2:2 / 7:2 per zip
            if ds["kind"] == "object":
                empty_total = sum(d.get("empty_labels", 0) for d in details.values())
                if empty_total:
                    warnings.append(f"{empty_total} empty label file(s) found")
        file_errors = errors + problems
        all_details.append(details)
        per_file.append({
            "filename": part["filename"],
            "ok": len(file_errors) == 0,
            "errors": file_errors,
            "warnings": warnings,
            "details": details,
            "report": build_report(part["filename"], details, file_errors, warnings),
        })

    ok = all(pf["ok"] for pf in per_file)                     # every zip must pass
    agg_details = merge_totals(all_details) if ok else {}
    agg_errors = [] if ok else ["fix the errors shown for each file below before continuing"]
    return jsonify(ok=ok, files=per_file,
                    aggregate={"details": agg_details,
                               "report": build_report("COMBINED TOTAL (all files)", agg_details, agg_errors, [])})


# --------------------------------------------------------------- 3. class name check/change (all zips)
@app.route("/api/class/check", methods=["POST"])
def class_check():
    j = request.get_json(force=True)
    ds = DB.get(j.get("batch_id"))
    cls = (j.get("class_name") or "").strip()
    if not ds:
        return jsonify(error="dataset not found"), 404
    if not cls:
        return jsonify(error="enter the class name"), 400

    per_file, all_matched = [], True
    for part in ds["parts"].values():
        names = yaml_names(part["root"])
        matched = bool(names) and cls.lower() in [n.lower() for n in names]
        all_matched = all_matched and matched
        per_file.append({"filename": part["filename"], "yaml_names": names, "matched": matched})
    return jsonify(matched=all_matched, class_name=cls, files=per_file)


@app.route("/api/class/change", methods=["POST"])
def class_change():
    """Change class name in the yaml file(s) of every uploaded folder"""
    j = request.get_json(force=True)
    ds = DB.get(j.get("batch_id"))
    cls = (j.get("class_name") or "").strip()
    if not ds or not cls:
        return jsonify(error="dataset id and class name required"), 400
    changed = []
    for part in ds["parts"].values():
        root = part["root"]
        targets = [os.path.join(root, "data.yaml")]
        for s in SPLITS:
            targets.append(os.path.join(root, s, "data.yaml"))
        for p in targets:
            if os.path.isfile(p):
                data = read_yaml_at(p)
                data["names"] = [cls]
                data["nc"] = 1
                write_yaml_at(p, data)
                changed.append(f"{part['filename']} -> {os.path.relpath(p, root)}")
    return jsonify(ok=bool(changed), changed=changed, class_name=cls)


# --------------------------------------------------------------- 7:3 non-object cleaning (all zips)
@app.route("/api/nonobject/clean", methods=["POST"])
def clean_nonobject():
    j = request.get_json(force=True)
    ds = DB.get(j.get("batch_id"))
    if not ds or ds["kind"] != "nonobject":
        return jsonify(error="non-object dataset not found"), 404
    emptied = created = removed_yaml = 0
    for part in ds["parts"].values():
        root = part["root"]
        for s in SPLITS:
            idir, ldir = os.path.join(root, s, "images"), os.path.join(root, s, "labels")
            if not os.path.isdir(ldir):
                os.makedirs(ldir, exist_ok=True)
            lbls = set(list_labels(ldir))
            for f in list_images(idir):
                stem = os.path.splitext(f)[0] + ".txt"
                p = os.path.join(ldir, stem)
                if stem not in lbls:
                    open(p, "w").close()
                    created += 1
                elif os.path.getsize(p) > 0:
                    open(p, "w").close()
                    emptied += 1
        for base, _dirs, files in os.walk(root):
            for fn in files:
                if fn.lower().endswith((".yaml", ".yml")):
                    os.remove(os.path.join(base, fn))
                    removed_yaml += 1
    return jsonify(ok=True, emptied_labels=emptied, created_labels=created, removed_yaml=removed_yaml)


# --------------------------------------------------------------- 5 / 8. combine ALL zips into ONE folder
@app.route("/api/combine", methods=["POST"])
def combine():
    j = request.get_json(force=True)
    batch_id = j.get("batch_id")
    ds = DB.get(batch_id)
    if not ds:
        return jsonify(error="dataset not found"), 404

    lock = get_lock(batch_id)
    if not lock.acquire(blocking=False):
        return jsonify(error="this dataset is already being combined - please wait a moment and try again"), 409

    try:
        final = os.path.join(ds["dir"], "final")
        safe_rmtree(final)
        for s in SPLITS:
            os.makedirs(os.path.join(final, s, "images"), exist_ok=True)
            os.makedirs(os.path.join(final, s, "labels"), exist_ok=True)

        counts = {s: {"images": 0, "labels": 0} for s in SPLITS}
        names = []
        for part in ds["parts"].values():
            root = part["root"]
            if ds["kind"] == "object" and not names:
                names = yaml_names(root)
            for s in SPLITS:
                idir, ldir = os.path.join(root, s, "images"), os.path.join(root, s, "labels")
                for f in list_images(idir):
                    stem, ext = os.path.splitext(f)
                    dst_name = f
                    while os.path.exists(os.path.join(final, s, "images", dst_name)):
                        dst_name = f"{stem}_{uuid.uuid4().hex[:6]}{ext}"  # avoid clashes between zips
                    shutil.copy2(os.path.join(idir, f), os.path.join(final, s, "images", dst_name))
                    dst_stem = os.path.splitext(dst_name)[0]
                    src_lbl = os.path.join(ldir, stem + ".txt")
                    dst_lbl = os.path.join(final, s, "labels", dst_stem + ".txt")
                    if os.path.isfile(src_lbl):
                        shutil.copy2(src_lbl, dst_lbl)
                    elif ds["kind"] == "nonobject":
                        open(dst_lbl, "w").close()
                    counts[s]["images"] += 1
        for s in SPLITS:
            counts[s]["labels"] = len(list_labels(os.path.join(final, s, "labels")))

        if ds["kind"] == "object":
            write_yaml_at(os.path.join(final, "data.yaml"), {
                "path": ".", "train": "train/images", "val": "valid/images",
                "test": "test/images", "nc": len(names) or 1,
                "names": names or ["object"]})

        ds["final"] = final
        totals = {"images": sum(c["images"] for c in counts.values()),
                  "labels": sum(c["labels"] for c in counts.values())}
        return jsonify(ok=True, counts=counts, totals=totals, names=names, source_files=len(ds["parts"]))
    finally:
        lock.release()


# --------------------------------------------------------------- 6 / 9. finalize + download (single folder/zip)
@app.route("/api/finalize", methods=["POST"])
def finalize():
    j = request.get_json(force=True)
    batch_id = j.get("batch_id")
    ds = DB.get(batch_id)
    folder = (j.get("folder_name") or "").strip()
    if not ds or not ds.get("final"):
        return jsonify(error="combine the dataset first"), 400
    if not folder:
        return jsonify(error="enter the folder name"), 400

    lock = get_lock(batch_id)
    if not lock.acquire(blocking=False):
        return jsonify(error="this dataset is busy - please wait a moment and try again"), 409
    try:
        safe = "".join(c if (c.isalnum() or c in "-_") else "_" for c in folder).strip("_") or "dataset"
        zpath = os.path.join(ds["dir"], safe + ".zip")
        if os.path.exists(zpath):
            os.remove(zpath)
        zip_directory(ds["final"], zpath)
        ds["zip"], ds["folder_name"] = zpath, safe
        return jsonify(ok=True, folder_name=safe, download_url=f"/api/download/{batch_id}")
    finally:
        lock.release()


@app.route("/api/download/<batch_id>")
def download(batch_id):
    ds = DB.get(batch_id)
    if not ds or not ds.get("zip") or not os.path.isfile(ds["zip"]):
        return jsonify(error="nothing to download yet"), 404
    return send_file(ds["zip"], as_attachment=True, download_name=os.path.basename(ds["zip"]))


# --------------------------------------------------------------- 10. balance check / fix
@app.route("/api/balance/check", methods=["POST"])
def balance_check():
    j = request.get_json(force=True)
    pos, neg = DB.get(j.get("object_batch_id")), DB.get(j.get("nonobject_batch_id"))
    if not pos or not neg or not pos.get("final") or not neg.get("final"):
        return jsonify(error="finalize both datasets first"), 400

    def total(ds):
        return sum(len(list_images(os.path.join(ds["final"], s, "images"))) for s in SPLITS)

    pc, nc = total(pos), total(neg)
    ratio = round(nc / pc * 100, 1) if pc else 0.0
    target = int(round(pc * 0.78))
    if 75 <= ratio <= 80:
        verdict, action = True, "none"
    elif ratio < 75:
        verdict, action = False, "add"
    else:
        verdict, action = False, "remove"
    return jsonify(ok=True, object_count=pc, nonobject_count=nc, ratio=ratio,
                   balanced=verdict, action=action, target=target)


@app.route("/api/balance/fix", methods=["POST"])
def balance_fix():
    j = request.get_json(force=True)
    neg = DB.get(j.get("nonobject_batch_id"))
    action, target = j.get("action"), int(j.get("target") or 0)
    if not neg or not neg.get("final"):
        return jsonify(error="non-object dataset not ready"), 400
    final = neg["final"]
    pairs = []
    for s in SPLITS:
        for f in list_images(os.path.join(final, s, "images")):
            pairs.append((s, f))
    rnd, added, removed = random.Random(), 0, 0
    if action == "remove" and len(pairs) > target:
        rnd.shuffle(pairs)
        for s, f in pairs[: len(pairs) - target]:
            ipath = os.path.join(final, s, "images", f)
            lpath = os.path.join(final, s, "labels", os.path.splitext(f)[0] + ".txt")
            if os.path.exists(ipath):
                os.remove(ipath)
            if os.path.exists(lpath):
                os.remove(lpath)
            removed += 1
    elif action == "add" and len(pairs) < target:
        need, i = target - len(pairs), 0
        while added < need and pairs:
            s, f = pairs[i % len(pairs)]
            stem, ext = os.path.splitext(f)
            new_img = f"{stem}_aug{added:04d}{ext}"
            src_i = os.path.join(final, s, "images", f)
            dst_i = os.path.join(final, s, "images", new_img)
            if PIL_OK:
                try:
                    im = Image.open(src_i)
                    if im.mode not in ("RGB", "L"):
                        im = im.convert("RGB")
                    im.transpose(Image.FLIP_LEFT_RIGHT).save(dst_i)
                except Exception:
                    shutil.copy2(src_i, dst_i)
            else:
                shutil.copy2(src_i, dst_i)
            open(os.path.join(final, s, "labels", os.path.splitext(new_img)[0] + ".txt"), "w").close()
            added += 1
            i += 1
    counts = {}
    for s in SPLITS:
        counts[s] = {"images": len(list_images(os.path.join(final, s, "images"))),
                     "labels": len(list_labels(os.path.join(final, s, "labels")))}
    return jsonify(ok=True, added=added, removed=removed, counts=counts,
                   total=sum(c["images"] for c in counts.values()))


# --------------------------------------------------------------- final: merge object + non-object -> train dataset
@app.route("/api/train/combine", methods=["POST"])
def train_combine():
    j = request.get_json(force=True)
    pos, neg = DB.get(j.get("object_batch_id")), DB.get(j.get("nonobject_batch_id"))
    if not pos or not neg or not pos.get("final") or not neg.get("final"):
        return jsonify(error="finalize both datasets first"), 400
    out = os.path.join(WORK_DIR, "train_" + uuid.uuid4().hex[:8])
    counts = {}
    for s in SPLITS:
        os.makedirs(os.path.join(out, s, "images"), exist_ok=True)
        os.makedirs(os.path.join(out, s, "labels"), exist_ok=True)
        n = 0
        for src in (pos["final"], neg["final"]):
            idir, ldir = os.path.join(src, s, "images"), os.path.join(src, s, "labels")
            for f in list_images(idir):
                stem, ext = os.path.splitext(f)
                dst = f
                while os.path.exists(os.path.join(out, s, "images", dst)):
                    dst = f"{stem}_{uuid.uuid4().hex[:4]}{ext}"
                shutil.copy2(os.path.join(idir, f), os.path.join(out, s, "images", dst))
                lbl_src = os.path.join(ldir, stem + ".txt")
                lbl_dst = os.path.splitext(dst)[0] + ".txt"
                if os.path.isfile(lbl_src):
                    shutil.copy2(lbl_src, os.path.join(out, s, "labels", lbl_dst))
                else:
                    open(os.path.join(out, s, "labels", lbl_dst), "w").close()
                n += 1
        counts[s] = {"images": n, "labels": len(list_labels(os.path.join(out, s, "labels")))}
    names = yaml_names(pos["final"])
    write_yaml_at(os.path.join(out, "data.yaml"), {
        "path": ".", "train": "train/images", "val": "valid/images",
        "test": "test/images", "nc": len(names) or 1,
        "names": names or ["object"]})
    tid = "train_" + uuid.uuid4().hex[:8]
    DB[tid] = {"kind": "train", "dir": out, "parts": {}, "final": out, "zip": None, "folder_name": None}
    totals = {"images": sum(c["images"] for c in counts.values()),
              "labels": sum(c["labels"] for c in counts.values())}
    return jsonify(ok=True, batch_id=tid, counts=counts, totals=totals, names=names)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
