// const $ = (id) => document.getElementById(id);
// const esc = (s) => String(s).replace(/[&<>"']/g,
//   c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

// const POS = { id:null, ready:false };
// const NEG = { id:null, ready:false };
// const TRAIN = { id:null };
// let BAL = null;

// const state = (k) => k === 'pos' ? POS : NEG;
// const fmt = (n) => (n || 0).toLocaleString();

// async function api(url, body = null) {
//   const opt = body ? { method:'POST', headers:{'Content-Type':'application/json'},
//                        body: JSON.stringify(body) } : {};
//   const r = await fetch(url, opt);
//   return r.json().catch(() => ({ error:'server error' }));
// }

// function setMsg(id, text, cls = '') {
//   const el = $(id);
//   el.hidden = !text;
//   el.className = 'msg ' + cls;
//   el.innerHTML = text;
// }

// function highlight(id) {
//   const el = $(id);
//   el.scrollIntoView({ behavior:'smooth', block:'center' });
//   el.classList.remove('flash'); void el.offsetWidth; el.classList.add('flash');
// }

// function wireUpload(kind) {
//   $(kind + '-file').addEventListener('change', () => {
//     const f = $(kind + '-file').files;
//     $(kind + '-fname').textContent = f.length ? f[0].name : 'No file chosen';
//     $(kind + '-check').disabled = !f.length;
//   });
//   $(kind + '-check').addEventListener('click', () => runCheck(kind));
// }

// async function uploadZip(kind) {
//   const fd = new FormData();
//   fd.append('file', $(kind + '-file').files[0]);
//   const r = await fetch('/api/upload/' + kind, { method:'POST', body: fd });
//   return r.json();
// }

// function hideSteps(kind) {
//   const steps = kind === 'pos'
//     ? ['pos-step-class', 'pos-step-final']
//     : ['neg-step-clean', 'neg-step-final'];
//   steps.forEach(i => $(i).hidden = true);
//   if (kind === 'pos') {
//     setMsg('pos-class-msg',''); setMsg('pos-combine-msg','');
//     setMsg('pos-final-msg',''); $('pos-dl-row').hidden = true;
//   } else {
//     setMsg('neg-clean-msg',''); setMsg('neg-combine-msg','');
//     setMsg('neg-final-msg',''); $('neg-dl-row').hidden = true;
//     $('neg-clean').disabled = false;
//   }
// }

// function renderReport(kind, res) {
//   const rep = $(kind + '-report');
//   rep.classList.remove('err');
//   if (res.ok) rep.textContent = '✅ CHECK PASSED\n\n' + res.report;
//   else { rep.classList.add('err');
//          rep.textContent = '❌ CHECK FAILED — fix the errors below to continue\n\n' + res.report; }
// }

// function renderSplit(kind, details) {
//   const t = details.train.images, v = details.valid.images, te = details.test.images;
//   const total = (t + v + te) || 1;
//   const pt = Math.round(t / total * 100), pv = Math.round(v / total * 100), pe = 100 - pt - pv;
//   $(kind+'-pct-train').textContent = pt + '%';
//   $(kind+'-pct-valid').textContent = pv + '%';
//   $(kind+'-pct-test').textContent  = pe + '%';
//   $(kind+'-n-train').textContent = t + ' images';
//   $(kind+'-n-valid').textContent = v + ' images';
//   $(kind+'-n-test').textContent  = te + ' images';
//   $(kind+'-bar-train').style.width = pt + '%';
//   $(kind+'-bar-valid').style.width = pv + '%';
//   $(kind+'-bar-test').style.width  = pe + '%';
//   $(kind + '-card').hidden = false;
// }

// async function runCheck(kind) {
//   const btn = $(kind + '-check');
//   btn.disabled = true; btn.textContent = 'Checking…';
//   hideSteps(kind);
//   const rep = $(kind + '-report');
//   rep.textContent = 'Checking dataset…';

//   const up = await uploadZip(kind);
//   if (up.error) {
//     rep.textContent = '❌ ' + up.error;
//     btn.disabled = false; btn.textContent = 'Check Dataset';
//     return;
//   }
//   state(kind).id = up.dataset_id;
//   state(kind).ready = false;

//   const res = await api('/api/check/' + up.dataset_id);
//   btn.disabled = false; btn.textContent = 'Check Dataset';
//   renderReport(kind, res);
//   if (res.details && res.details.train) renderSplit(kind, res.details);

//   if (!res.ok) return;                        // errors block next step
//   if (kind === 'pos') $('pos-step-class').hidden = false;
//   else $('neg-step-clean').hidden = false;
// }

// /* ---------------- POSITIVE flow ---------------- */
//  $('pos-compare').addEventListener('click', async () => {
//   const cls = $('pos-class').value.trim();
//   if (!cls) return setMsg('pos-class-msg', '⚠️ Enter the class name', 'warn');
//   const res = await api('/api/class/check', { dataset_id: POS.id, class_name: cls });
//   if (res.error) return setMsg('pos-class-msg', '⚠️ ' + res.error, 'warn');
//   if (res.matched) {
//     setMsg('pos-class-msg',
//       `✅ Success — class name "<b>${esc(res.class_name)}</b>" matched in data.yaml`, 'ok');
//     combinePositive();
//   } else {
//     setMsg('pos-class-msg',
//       `❌ Class name is different.<br>
//        yaml class name(s): <b>${res.yaml_names.map(esc).join(', ')}</b><br><br>
//        Can I change the class name in the given folders' yaml file?
//        <span class="confirm">
//          <button class="btn" id="pos-yes">OK</button>
//          <button class="btn ghost" id="pos-no">Cancel</button>
//        </span>`, 'warn');
//     $('pos-yes').onclick = async () => {
//       const ch = await api('/api/class/change', { dataset_id: POS.id, class_name: cls });
//       if (ch.ok) {
//         setMsg('pos-class-msg',
//           `✅ Class name changed to "<b>${esc(cls)}</b>" in: ${ch.changed.map(esc).join(', ')}`, 'ok');
//         combinePositive();
//       } else setMsg('pos-class-msg', '⚠️ ' + (ch.error || 'change failed'), 'warn');
//     };
//     $('pos-no').onclick = () =>
//       setMsg('pos-class-msg', 'Cancelled — you can re-enter a class name and compare again.', 'warn');
//   }
// });

// async function combinePositive() {
//   const res = await api('/api/combine', { dataset_id: POS.id });
//   if (res.error) return setMsg('pos-combine-msg', '⚠️ ' + res.error, 'warn');
//   $('pos-step-final').hidden = false;
//   setMsg('pos-combine-msg', '✅ All folders combined as per the dataset format', 'ok');
//   $('pos-details').innerHTML = detailsTable(res.counts, res.totals, res.names);
// }

// /* ---------------- NEGATIVE flow ---------------- */
//  $('neg-clean').addEventListener('click', async () => {
//   const res = await api('/api/nonobject/clean', { dataset_id: NEG.id });
//   if (res.error) return setMsg('neg-clean-msg', '⚠️ ' + res.error, 'warn');
//   setMsg('neg-clean-msg',
//     `✅ Removed data inside <b>${res.emptied_labels}</b> label file(s), ` +
//     `created <b>${res.created_labels}</b> empty label(s), deleted <b>${res.removed_yaml}</b> yaml file(s)`, 'ok');
//   $('neg-clean').disabled = true;
//   const cb = await api('/api/combine', { dataset_id: NEG.id, cleaned: true });
//   if (cb.error) return setMsg('neg-combine-msg', '⚠️ ' + cb.error, 'warn');
//   $('neg-step-final').hidden = false;
//   setMsg('neg-combine-msg', '✅ All folders combined as per the dataset format', 'ok');
//   $('neg-details').innerHTML = detailsTable(cb.counts, cb.totals);
// });

// /* ---------------- common ---------------- */
// function detailsTable(counts, totals, names = []) {
//   let h = '<table><tr><th>Folder</th><th>Images</th><th>Labels</th></tr>';
//   for (const s of ['train','valid','test'])
//     h += `<tr><td>${s}</td><td>${fmt(counts[s].images)}</td><td>${fmt(counts[s].labels)}</td></tr>`;
//   h += '</table>';
//   h += `<div class="totals">Total images: <b>${fmt(totals.images)}</b> · ` +
//        `Total labels: <b>${fmt(totals.labels)}</b>`;
//   if (names && names.length) h += ` · Classes: <b>${names.map(esc).join(', ')}</b>`;
//   return h + '</div>';
// }

// function wireFinalize(kind, obj) {
//   $(kind + '-finalize').addEventListener('click', async () => {
//     const folder = $(kind + '-folder').value.trim();
//     if (!folder) return setMsg(kind + '-final-msg', '⚠️ Enter the folder name', 'warn');
//     const res = await api('/api/finalize', { dataset_id: obj.id, folder_name: folder });
//     if (res.error) return setMsg(kind + '-final-msg', '⚠️ ' + res.error, 'warn');
//     setMsg(kind + '-final-msg', `✅ Folder "<b>${esc(res.folder_name)}</b>" is ready`, 'ok');
//     $(kind + '-dl').href = res.download_url;
//     $(kind + '-dl-row').hidden = false;
//     obj.ready = true;
//   });
// }

//  $('pos-continue').addEventListener('click', () => highlight('panel-neg'));

//  $('neg-continue').addEventListener('click', async () => {
//   if (!POS.id || !NEG.id) return alert('Complete both datasets first');
//   $('panel-balance').hidden = false;
//   highlight('panel-balance');
//   await runBalanceCheck();
// });

// /* ---------------- balance + train ---------------- */
// async function runBalanceCheck() {
//   setMsg('bal-msg', 'Checking balance…');
//   const res = await api('/api/balance/check', { object_id: POS.id, nonobject_id: NEG.id });
//   if (res.error) return setMsg('bal-msg', '⚠️ ' + res.error, 'warn');
//   BAL = res; setMsg('bal-msg', '');
//   $('bal-pos-count').textContent = fmt(res.object_count);
//   $('bal-neg-count').textContent = fmt(res.nonobject_count);
//   $('bal-neg-label').textContent = `Negative images (${res.ratio}%)`;
//   const bar = $('bal-ratio-bar');
//   bar.style.width = Math.min(res.ratio, 100) + '%';
//   bar.className = res.balanced ? 'ok' : 'bad';
//   $('bal-ratio-text').textContent = res.ratio + '%';
//   $('bal-fix').hidden = true;
//   $('train-final-row').hidden = true;
//   $('train-dl-row').hidden = true;
//   $('train-ready').hidden = true;

//   if (res.balanced) {
//     $('bal-verdict').innerHTML =
//       '<span class="ok">✅ True — non-object count is within 75–80% of object count</span>';
//     showTrainCombine();
//   } else if (res.action === 'add') {
//     $('bal-verdict').innerHTML =
//       `<span class="bad">❌ False — non-object count is only ${res.ratio}% (needs 75–80%). ` +
//       `Add ~${fmt(res.target - res.nonobject_count)} more images.</span>`;
//     $('bal-fix').hidden = false;
//   } else {
//     $('bal-verdict').innerHTML =
//       `<span class="bad">❌ False — non-object count is ${res.ratio}% (above 80%). ` +
//       `Remove ~${fmt(res.nonobject_count - res.target)} images.</span>`;
//     $('bal-fix').hidden = false;
//   }
// }

//  $('bal-fix').addEventListener('click', async () => {
//   $('bal-fix').disabled = true; $('bal-fix').textContent = 'Balancing…';
//   const res = await api('/api/balance/fix',
//     { nonobject_id: NEG.id, action: BAL.action, target: BAL.target });
//   $('bal-fix').disabled = false; $('bal-fix').textContent = '⚖ Auto Balance Dataset';
//   if (res.error) return setMsg('bal-msg', '⚠️ ' + res.error, 'warn');
//   setMsg('bal-msg', `✅ Balanced — added ${res.added} image(s), removed ${res.removed} image(s). ` +
//                     `Download the negative dataset again if needed.`, 'ok');
//   await runBalanceCheck();
// });

// async function showTrainCombine() {
//   const res = await api('/api/train/combine', { object_id: POS.id, nonobject_id: NEG.id });
//   if (res.error) return setMsg('bal-msg', '⚠️ ' + res.error, 'warn');
//   TRAIN.id = res.train_id;
//   $('train-title').hidden = false;
//   $('train-details').hidden = false;
//   $('train-details').innerHTML = detailsTable(res.counts, res.totals, res.names) +
//     '<div class="totals">Positive + Negative merged · negative labels are empty (background images)</div>';
//   $('train-final-row').hidden = false;
// }

//  $('train-go').addEventListener('click', () => { $('train-ready').hidden = false; highlight('train-ready'); });

// /* init */
// wireUpload('pos'); wireUpload('neg');
// wireFinalize('pos', POS); wireFinalize('neg', NEG); wireFinalize('train', TRAIN);

// --------------------------------------------------------------------------------------------------------------

// (() => {
//   const $ = (id) => document.getElementById(id);
//   const show = (el) => { el.hidden = false; };
//   const hide = (el) => { el.hidden = true; };

//   const state = {
//     pos: { batchId: null, files: [], ok: false, classOk: false, combined: false, finalized: false },
//     neg: { batchId: null, files: [], ok: false, cleaned: false, combined: false, finalized: false },
//   };

//   async function postJSON(url, body) {
//     const r = await fetch(url, {
//       method: "POST",
//       headers: { "Content-Type": "application/json" },
//       body: JSON.stringify(body),
//     });
//     const j = await r.json();
//     if (!r.ok) throw new Error(j.error || "request failed");
//     return j;
//   }

//   async function postForm(url, formData) {
//     const r = await fetch(url, { method: "POST", body: formData });
//     const j = await r.json();
//     if (!r.ok) throw new Error(j.error || "request failed");
//     return j;
//   }

//   function setMsg(el, text, ok) {
//     el.textContent = text;
//     el.className = "msg" + (ok ? " ok" : "");
//     show(el);
//   }

//   // ---------------------------------------------------------- split card
//   function renderSplitCard(prefix, aggDetails) {
//     const t = aggDetails.train || { images: 0 };
//     const v = aggDetails.valid || { images: 0 };
//     const te = aggDetails.test || { images: 0 };
//     const total = (t.images || 0) + (v.images || 0) + (te.images || 0);
//     const pct = (n) => (total ? Math.round((n / total) * 100) : 0);

//     $(`${prefix}-pct-train`).textContent = pct(t.images) + "%";
//     $(`${prefix}-pct-valid`).textContent = pct(v.images) + "%";
//     $(`${prefix}-pct-test`).textContent = pct(te.images) + "%";
//     $(`${prefix}-n-train`).textContent = (t.images || 0) + " images";
//     $(`${prefix}-n-valid`).textContent = (v.images || 0) + " images";
//     $(`${prefix}-n-test`).textContent = (te.images || 0) + " images";
//     $(`${prefix}-bar-train`).style.width = pct(t.images) + "%";
//     $(`${prefix}-bar-valid`).style.width = pct(v.images) + "%";
//     $(`${prefix}-bar-test`).style.width = pct(te.images) + "%";
//     show($(`${prefix}-card`));
//   }

//   function renderFileReports(prefix, files) {
//     const wrap = $(`${prefix}-file-reports`);
//     wrap.innerHTML = "";
//     files.forEach((f) => {
//       const details = document.createElement("details");
//       const summary = document.createElement("summary");
//       summary.innerHTML = `<span>${f.filename}</span><span class="status ${f.ok ? "ok" : "bad"}">${f.ok ? "OK" : "ERRORS"}</span>`;
//       const pre = document.createElement("pre");
//       pre.className = "report";
//       pre.textContent = f.report;
//       details.appendChild(summary);
//       details.appendChild(pre);
//       wrap.appendChild(details);
//     });
//   }

//   // ---------------------------------------------------------- file picker wiring
//   function wireFilePicker(prefix, kind) {
//     const input = $(`${prefix}-file`);
//     const fname = $(`${prefix}-fname`);
//     const chips = $(`${prefix}-chips`);
//     const checkBtn = $(`${prefix}-check`);

//     input.addEventListener("change", () => {
//       const files = Array.from(input.files || []);
//       state[prefix].files = files;
//       fname.textContent = files.length ? `${files.length} file(s) selected` : "No files chosen";
//       chips.innerHTML = "";
//       files.forEach((f) => {
//         const c = document.createElement("span");
//         c.className = "chip";
//         c.textContent = f.name;
//         chips.appendChild(c);
//       });
//       checkBtn.disabled = files.length === 0;
//       // reset downstream state whenever the selection changes
//       state[prefix].ok = false;
//       state[prefix].combined = false;
//       state[prefix].finalized = false;
//     });

//     checkBtn.addEventListener("click", () => runCheck(prefix, kind));
//   }

//   async function runCheck(prefix, kind) {
//     const checkBtn = $(`${prefix}-check`);
//     const report = $(`${prefix}-report`);
//     checkBtn.disabled = true;
//     report.textContent = "Uploading & checking " + state[prefix].files.length + " file(s)...";

//     try {
//       const fd = new FormData();
//       state[prefix].files.forEach((f) => fd.append("files", f));
//       const up = await postForm(`/api/upload/${kind}`, fd);
//       state[prefix].batchId = up.batch_id;

//       const res = await fetch(`/api/check/${up.batch_id}`);
//       const data = await res.json();
//       if (data.error) throw new Error(data.error);

//       report.textContent = data.aggregate.report;
//       renderFileReports(prefix, data.files);

//       if (Object.keys(data.aggregate.details).length) {
//         renderSplitCard(prefix, data.aggregate.details);
//       }

//       state[prefix].ok = data.ok;
//       if (data.ok) {
//         if (prefix === "pos") {
//           show($("pos-step-class"));
//         } else {
//           show($("neg-step-clean"));
//         }
//       }
//     } catch (err) {
//       report.textContent = "Error: " + err.message;
//     } finally {
//       checkBtn.disabled = false;
//     }
//   }

//   // ---------------------------------------------------------- POS: class name step
//   function wireClassStep() {
//     const compareBtn = $("pos-compare");
//     const changeBtn = $("pos-class-change");
//     const continueBtn = $("pos-class-continue");
//     const table = $("pos-class-table");
//     const msg = $("pos-class-msg");

//     compareBtn.addEventListener("click", async () => {
//       const cls = $("pos-class").value.trim();
//       if (!cls) { setMsg(msg, "Enter the class name.", false); return; }
//       if (!state.pos.batchId) return;
//       hide(changeBtn); hide(continueBtn);
//       try {
//         const data = await postJSON("/api/class/check", { batch_id: state.pos.batchId, class_name: cls });
//         table.innerHTML = "";
//         data.files.forEach((f) => {
//           const row = document.createElement("div");
//           row.className = "class-row";
//           row.innerHTML = `
//             <span class="fn">${f.filename}</span>
//             <span class="names">yaml: ${f.yaml_names.length ? f.yaml_names.join(", ") : "(none)"}</span>
//             <span class="tag ${f.matched ? "ok" : "bad"}">${f.matched ? "matches" : "different"}</span>`;
//           table.appendChild(row);
//         });
//         if (data.matched) {
//           setMsg(msg, `All uploaded folders already use class "${data.class_name}".`, true);
//           state.pos.classOk = true;
//           show(continueBtn);
//         } else {
//           setMsg(msg, `Class name is different in one or more folders. Change all folders' yaml to "${data.class_name}"?`, false);
//           state.pos.classOk = false;
//           show(changeBtn);
//         }
//       } catch (err) {
//         setMsg(msg, "Error: " + err.message, false);
//       }
//     });

//     changeBtn.addEventListener("click", async () => {
//       const cls = $("pos-class").value.trim();
//       if (!cls || !state.pos.batchId) return;
//       try {
//         const data = await postJSON("/api/class/change", { batch_id: state.pos.batchId, class_name: cls });
//         setMsg(msg, `Class name changed to "${data.class_name}" in ${data.changed.length} file(s).`, true);
//         state.pos.classOk = true;
//         hide(changeBtn);
//         show(continueBtn);
//       } catch (err) {
//         setMsg(msg, "Error: " + err.message, false);
//       }
//     });

//     continueBtn.addEventListener("click", () => combineAndShow("pos"));
//   }

//   // ---------------------------------------------------------- NEG: clean step
//   function wireCleanStep() {
//     const cleanBtn = $("neg-clean");
//     const msg = $("neg-clean-msg");
//     cleanBtn.addEventListener("click", async () => {
//       if (!state.neg.batchId) return;
//       cleanBtn.disabled = true;
//       try {
//         const data = await postJSON("/api/nonobject/clean", { batch_id: state.neg.batchId });
//         setMsg(msg, `Cleaned ${data.emptied_labels + data.created_labels} label file(s) and removed ${data.removed_yaml} yaml file(s).`, true);
//         state.neg.cleaned = true;
//         await combineAndShow("neg");
//       } catch (err) {
//         setMsg(msg, "Error: " + err.message, false);
//       } finally {
//         cleanBtn.disabled = false;
//       }
//     });
//   }

//   // ---------------------------------------------------------- combine + finalize (shared)
//   async function combineAndShow(prefix) {
//     const combineMsg = $(`${prefix}-combine-msg`);
//     const detailsBox = $(`${prefix}-details`);
//     try {
//       const data = await postJSON("/api/combine", { batch_id: state[prefix].batchId });
//       state[prefix].combined = true;
//       setMsg(combineMsg, `Combined ${data.source_files} folder(s) into one dataset — ${data.totals.images} images, ${data.totals.labels} labels.`, true);
//       detailsBox.innerHTML = "";
//       ["train", "valid", "test"].forEach((s) => {
//         const c = data.counts[s];
//         const box = document.createElement("div");
//         box.className = "box";
//         box.innerHTML = `<b>${c.images}</b><small>${s.toUpperCase()} images</small><b style="margin-top:6px">${c.labels}</b><small>${s.toUpperCase()} labels</small>`;
//         detailsBox.appendChild(box);
//       });
//       show($(`${prefix}-step-final`));
//     } catch (err) {
//       setMsg(combineMsg, "Error: " + err.message, false);
//     }
//   }

//   function wireFinalizeStep(prefix) {
//     const btn = $(`${prefix}-finalize`);
//     const msg = $(`${prefix}-final-msg`);
//     const dlRow = $(`${prefix}-dl-row`);
//     const dl = $(`${prefix}-dl`);
//     const continueBtn = $(`${prefix}-continue`);

//     btn.addEventListener("click", async () => {
//       const folder = $(`${prefix}-folder`).value.trim();
//       if (!folder) { setMsg(msg, "Enter the folder name.", false); return; }
//       try {
//         const data = await postJSON("/api/finalize", { batch_id: state[prefix].batchId, folder_name: folder });
//         setMsg(msg, `Folder "${data.folder_name}" is ready.`, true);
//         dl.href = data.download_url;
//         state[prefix].finalized = true;
//         show(dlRow);
//       } catch (err) {
//         setMsg(msg, "Error: " + err.message, false);
//       }
//     });

//     continueBtn.addEventListener("click", () => {
//       if (state.pos.finalized && state.neg.finalized) {
//         runBalanceCheck();
//       } else {
//         alert("Finish and download both the Positive and Negative datasets first.");
//       }
//     });
//   }

//   // ---------------------------------------------------------- balance check
//   async function runBalanceCheck() {
//     show($("panel-balance"));
//     $("panel-balance").scrollIntoView({ behavior: "smooth" });
//     const msg = $("bal-msg");
//     hide(msg);
//     try {
//       const data = await postJSON("/api/balance/check", {
//         object_batch_id: state.pos.batchId,
//         nonobject_batch_id: state.neg.batchId,
//       });
//       $("bal-pos-count").textContent = data.object_count;
//       $("bal-neg-count").textContent = data.nonobject_count;
//       $("bal-neg-label").textContent = `Negative images (${data.ratio}%)`;
//       $("bal-ratio-bar").style.width = Math.min(data.ratio, 100) + "%";
//       $("bal-ratio-text").textContent = data.ratio + "%";

//       const verdict = $("bal-verdict");
//       const fixBtn = $("bal-fix");
//       if (data.balanced) {
//         verdict.innerHTML = `<div class="msg ok">Balanced. Non-object dataset is within the 75–80% target range.</div>`;
//         hide(fixBtn);
//         await runTrainCombine();
//       } else {
//         const dir = data.action === "add" ? "add more images to" : "remove images from";
//         verdict.innerHTML = `<div class="msg">Not balanced (target ≈ ${data.target} images). Recommend to ${dir} the non-object dataset.</div>`;
//         fixBtn.dataset.action = data.action;
//         fixBtn.dataset.target = data.target;
//         show(fixBtn);
//       }
//     } catch (err) {
//       setMsg(msg, "Error: " + err.message, false);
//     }
//   }

//   function wireBalanceFix() {
//     const fixBtn = $("bal-fix");
//     fixBtn.addEventListener("click", async () => {
//       fixBtn.disabled = true;
//       try {
//         await postJSON("/api/balance/fix", {
//           nonobject_batch_id: state.neg.batchId,
//           action: fixBtn.dataset.action,
//           target: fixBtn.dataset.target,
//         });
//         await runBalanceCheck();
//       } catch (err) {
//         alert("Error: " + err.message);
//       } finally {
//         fixBtn.disabled = false;
//       }
//     });
//   }

//   // ---------------------------------------------------------- final train combine
//   async function runTrainCombine() {
//     try {
//       const data = await postJSON("/api/train/combine", {
//         object_batch_id: state.pos.batchId,
//         nonobject_batch_id: state.neg.batchId,
//       });
//       state.train = { batchId: data.batch_id };
//       show($("train-title"));
//       const box = $("train-details");
//       box.innerHTML = "";
//       ["train", "valid", "test"].forEach((s) => {
//         const c = data.counts[s];
//         const d = document.createElement("div");
//         d.className = "box";
//         d.innerHTML = `<b>${c.images}</b><small>${s.toUpperCase()} images</small><b style="margin-top:6px">${c.labels}</b><small>${s.toUpperCase()} labels</small>`;
//         box.appendChild(d);
//       });
//       show(box);
//       show($("train-final-row"));
//     } catch (err) {
//       alert("Error: " + err.message);
//     }
//   }

//   function wireTrainFinalize() {
//     const btn = $("train-finalize");
//     const msg = $("train-final-msg");
//     const dlRow = $("train-dl-row");
//     const dl = $("train-dl");
//     btn.addEventListener("click", async () => {
//       const folder = $("train-folder").value.trim();
//       if (!folder) { setMsg(msg, "Enter the folder name.", false); return; }
//       try {
//         const data = await postJSON("/api/finalize", { batch_id: state.train.batchId, folder_name: folder });
//         setMsg(msg, `Folder "${data.folder_name}" is ready.`, true);
//         dl.href = data.download_url;
//         show(dlRow);
//         show($("train-ready"));
//       } catch (err) {
//         setMsg(msg, "Error: " + err.message, false);
//       }
//     });
//   }

//   // ---------------------------------------------------------- init
//   wireFilePicker("pos", "object");
//   wireFilePicker("neg", "nonobject");
//   wireClassStep();
//   wireCleanStep();
//   wireFinalizeStep("pos");
//   wireFinalizeStep("neg");
//   wireBalanceFix();
//   wireTrainFinalize();
// })();

// ========================================================================================

(() => {
  const $ = (id) => document.getElementById(id);
  const show = (el) => { el.hidden = false; };
  const hide = (el) => { el.hidden = true; };

  const state = {
    pos: { batchId: null, files: [], ok: false, classOk: false, combined: false, finalized: false },
    neg: { batchId: null, files: [], ok: false, cleaned: false, combined: false, finalized: false },
  };

  async function postJSON(url, body) {
    const r = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const j = await r.json();
    if (!r.ok) throw new Error(j.error || "request failed");
    return j;
  }

  async function postForm(url, formData) {
    const r = await fetch(url, { method: "POST", body: formData });
    const j = await r.json();
    if (!r.ok) throw new Error(j.error || "request failed");
    return j;
  }

  function setMsg(el, text, ok) {
    el.textContent = text;
    el.className = "msg" + (ok ? " ok" : "");
    show(el);
  }

  // ---------------------------------------------------------- split card
  function renderSplitCard(prefix, aggDetails) {
    const t = aggDetails.train || { images: 0 };
    const v = aggDetails.valid || { images: 0 };
    const te = aggDetails.test || { images: 0 };
    const total = (t.images || 0) + (v.images || 0) + (te.images || 0);
    const pct = (n) => (total ? Math.round((n / total) * 100) : 0);

    $(`${prefix}-pct-train`).textContent = pct(t.images) + "%";
    $(`${prefix}-pct-valid`).textContent = pct(v.images) + "%";
    $(`${prefix}-pct-test`).textContent = pct(te.images) + "%";
    $(`${prefix}-n-train`).textContent = (t.images || 0) + " images";
    $(`${prefix}-n-valid`).textContent = (v.images || 0) + " images";
    $(`${prefix}-n-test`).textContent = (te.images || 0) + " images";
    $(`${prefix}-bar-train`).style.width = pct(t.images) + "%";
    $(`${prefix}-bar-valid`).style.width = pct(v.images) + "%";
    $(`${prefix}-bar-test`).style.width = pct(te.images) + "%";
    show($(`${prefix}-card`));
  }

  function renderFileReports(prefix, files) {
    const wrap = $(`${prefix}-file-reports`);
    wrap.innerHTML = "";
    files.forEach((f) => {
      const details = document.createElement("details");
      const summary = document.createElement("summary");
      summary.innerHTML = `<span>${f.filename}</span><span class="status ${f.ok ? "ok" : "bad"}">${f.ok ? "OK" : "ERRORS"}</span>`;
      const pre = document.createElement("pre");
      pre.className = "report";
      pre.textContent = f.report;
      details.appendChild(summary);
      details.appendChild(pre);
      wrap.appendChild(details);
    });
  }

  // ---------------------------------------------------------- file picker wiring
  function wireFilePicker(prefix, kind) {
    const input = $(`${prefix}-file`);
    const fname = $(`${prefix}-fname`);
    const chips = $(`${prefix}-chips`);
    const checkBtn = $(`${prefix}-check`);

    input.addEventListener("change", () => {
      const files = Array.from(input.files || []);
      state[prefix].files = files;
      fname.textContent = files.length ? `${files.length} file(s) selected` : "No files chosen";
      chips.innerHTML = "";
      files.forEach((f) => {
        const c = document.createElement("span");
        c.className = "chip";
        c.textContent = f.name;
        chips.appendChild(c);
      });
      checkBtn.disabled = files.length === 0;
      // reset downstream state whenever the selection changes
      state[prefix].ok = false;
      state[prefix].combined = false;
      state[prefix].finalized = false;
    });

    checkBtn.addEventListener("click", () => runCheck(prefix, kind));
  }

  async function runCheck(prefix, kind) {
    const checkBtn = $(`${prefix}-check`);
    const report = $(`${prefix}-report`);
    checkBtn.disabled = true;
    report.textContent = "Uploading & checking " + state[prefix].files.length + " file(s)...";

    try {
      const fd = new FormData();
      state[prefix].files.forEach((f) => fd.append("files", f));
      const up = await postForm(`/api/upload/${kind}`, fd);
      state[prefix].batchId = up.batch_id;

      const res = await fetch(`/api/check/${up.batch_id}`);
      const data = await res.json();
      if (data.error) throw new Error(data.error);

      report.textContent = data.aggregate.report;
      renderFileReports(prefix, data.files);

      if (Object.keys(data.aggregate.details).length) {
        renderSplitCard(prefix, data.aggregate.details);
      }

      state[prefix].ok = data.ok;
      if (data.ok) {
        if (prefix === "pos") {
          show($("pos-step-class"));
        } else {
          show($("neg-step-clean"));
        }
      }
    } catch (err) {
      report.textContent = "Error: " + err.message;
    } finally {
      checkBtn.disabled = false;
    }
  }

  // ---------------------------------------------------------- POS: class name step
  function wireClassStep() {
    const compareBtn = $("pos-compare");
    const changeBtn = $("pos-class-change");
    const continueBtn = $("pos-class-continue");
    const table = $("pos-class-table");
    const msg = $("pos-class-msg");

    compareBtn.addEventListener("click", async () => {
      const cls = $("pos-class").value.trim();
      if (!cls) { setMsg(msg, "Enter the class name.", false); return; }
      if (!state.pos.batchId) return;
      hide(changeBtn); hide(continueBtn);
      try {
        const data = await postJSON("/api/class/check", { batch_id: state.pos.batchId, class_name: cls });
        table.innerHTML = "";
        data.files.forEach((f) => {
          const row = document.createElement("div");
          row.className = "class-row";
          row.innerHTML = `
            <span class="fn">${f.filename}</span>
            <span class="names">yaml: ${f.yaml_names.length ? f.yaml_names.join(", ") : "(none)"}</span>
            <span class="tag ${f.matched ? "ok" : "bad"}">${f.matched ? "matches" : "different"}</span>`;
          table.appendChild(row);
        });
        if (data.matched) {
          setMsg(msg, `All uploaded folders already use class "${data.class_name}".`, true);
          state.pos.classOk = true;
          show(continueBtn);
        } else {
          setMsg(msg, `Class name is different in one or more folders. Change all folders' yaml to "${data.class_name}"?`, false);
          state.pos.classOk = false;
          show(changeBtn);
        }
      } catch (err) {
        setMsg(msg, "Error: " + err.message, false);
      }
    });

    changeBtn.addEventListener("click", async () => {
      const cls = $("pos-class").value.trim();
      if (!cls || !state.pos.batchId) return;
      try {
        const data = await postJSON("/api/class/change", { batch_id: state.pos.batchId, class_name: cls });
        setMsg(msg, `Class name changed to "${data.class_name}" in ${data.changed.length} file(s).`, true);
        state.pos.classOk = true;
        hide(changeBtn);
        show(continueBtn);
      } catch (err) {
        setMsg(msg, "Error: " + err.message, false);
      }
    });

    continueBtn.addEventListener("click", () => combineAndShow("pos"));
  }

  // ---------------------------------------------------------- NEG: clean step
  function wireCleanStep() {
    const cleanBtn = $("neg-clean");
    const msg = $("neg-clean-msg");
    cleanBtn.addEventListener("click", async () => {
      if (!state.neg.batchId) return;
      cleanBtn.disabled = true;
      try {
        const data = await postJSON("/api/nonobject/clean", { batch_id: state.neg.batchId });
        setMsg(msg, `Cleaned ${data.emptied_labels + data.created_labels} label file(s) and removed ${data.removed_yaml} yaml file(s).`, true);
        state.neg.cleaned = true;
        await combineAndShow("neg");
      } catch (err) {
        setMsg(msg, "Error: " + err.message, false);
      } finally {
        cleanBtn.disabled = false;
      }
    });
  }

  // ---------------------------------------------------------- combine + finalize (shared)
  async function combineAndShow(prefix) {
    if (state[prefix].combining) return; // guard against double-click / duplicate calls
    state[prefix].combining = true;
    const combineMsg = $(`${prefix}-combine-msg`);
    const detailsBox = $(`${prefix}-details`);
    const triggerBtn = prefix === "pos" ? $("pos-class-continue") : null;
    if (triggerBtn) triggerBtn.disabled = true;
    try {
      const data = await postJSON("/api/combine", { batch_id: state[prefix].batchId });
      state[prefix].combined = true;
      setMsg(combineMsg, `Combined ${data.source_files} folder(s) into one dataset — ${data.totals.images} images, ${data.totals.labels} labels.`, true);
      detailsBox.innerHTML = "";
      ["train", "valid", "test"].forEach((s) => {
        const c = data.counts[s];
        const box = document.createElement("div");
        box.className = "box";
        box.innerHTML = `<b>${c.images}</b><small>${s.toUpperCase()} images</small><b style="margin-top:6px">${c.labels}</b><small>${s.toUpperCase()} labels</small>`;
        detailsBox.appendChild(box);
      });
      show($(`${prefix}-step-final`));
    } catch (err) {
      setMsg(combineMsg, "Error: " + err.message, false);
    } finally {
      state[prefix].combining = false;
      if (triggerBtn) triggerBtn.disabled = false;
    }
  }

  function wireFinalizeStep(prefix) {
    const btn = $(`${prefix}-finalize`);
    const msg = $(`${prefix}-final-msg`);
    const dlRow = $(`${prefix}-dl-row`);
    const dl = $(`${prefix}-dl`);
    const continueBtn = $(`${prefix}-continue`);

    btn.addEventListener("click", async () => {
      const folder = $(`${prefix}-folder`).value.trim();
      if (!folder) { setMsg(msg, "Enter the folder name.", false); return; }
      btn.disabled = true;
      try {
        const data = await postJSON("/api/finalize", { batch_id: state[prefix].batchId, folder_name: folder });
        setMsg(msg, `Folder "${data.folder_name}" is ready.`, true);
        dl.href = data.download_url;
        state[prefix].finalized = true;
        show(dlRow);
      } catch (err) {
        setMsg(msg, "Error: " + err.message, false);
      } finally {
        btn.disabled = false;
      }
    });

    continueBtn.addEventListener("click", () => {
      if (state.pos.finalized && state.neg.finalized) {
        runBalanceCheck();
      } else {
        alert("Finish and download both the Positive and Negative datasets first.");
      }
    });
  }

  // ---------------------------------------------------------- balance check
  async function runBalanceCheck() {
    show($("panel-balance"));
    $("panel-balance").scrollIntoView({ behavior: "smooth" });
    const msg = $("bal-msg");
    hide(msg);
    try {
      const data = await postJSON("/api/balance/check", {
        object_batch_id: state.pos.batchId,
        nonobject_batch_id: state.neg.batchId,
      });
      $("bal-pos-count").textContent = data.object_count;
      $("bal-neg-count").textContent = data.nonobject_count;
      $("bal-neg-label").textContent = `Negative images (${data.ratio}%)`;
      $("bal-ratio-bar").style.width = Math.min(data.ratio, 100) + "%";
      $("bal-ratio-text").textContent = data.ratio + "%";

      const verdict = $("bal-verdict");
      const fixBtn = $("bal-fix");
      if (data.balanced) {
        verdict.innerHTML = `<div class="msg ok">Balanced. Non-object dataset is within the 75–80% target range.</div>`;
        hide(fixBtn);
        await runTrainCombine();
      } else {
        const dir = data.action === "add" ? "add more images to" : "remove images from";
        verdict.innerHTML = `<div class="msg">Not balanced (target ≈ ${data.target} images). Recommend to ${dir} the non-object dataset.</div>`;
        fixBtn.dataset.action = data.action;
        fixBtn.dataset.target = data.target;
        show(fixBtn);
      }
    } catch (err) {
      setMsg(msg, "Error: " + err.message, false);
    }
  }

  function wireBalanceFix() {
    const fixBtn = $("bal-fix");
    fixBtn.addEventListener("click", async () => {
      fixBtn.disabled = true;
      try {
        await postJSON("/api/balance/fix", {
          nonobject_batch_id: state.neg.batchId,
          action: fixBtn.dataset.action,
          target: fixBtn.dataset.target,
        });
        await runBalanceCheck();
      } catch (err) {
        alert("Error: " + err.message);
      } finally {
        fixBtn.disabled = false;
      }
    });
  }

  // ---------------------------------------------------------- final train combine
  async function runTrainCombine() {
    try {
      const data = await postJSON("/api/train/combine", {
        object_batch_id: state.pos.batchId,
        nonobject_batch_id: state.neg.batchId,
      });
      state.train = { batchId: data.batch_id };
      show($("train-title"));
      const box = $("train-details");
      box.innerHTML = "";
      ["train", "valid", "test"].forEach((s) => {
        const c = data.counts[s];
        const d = document.createElement("div");
        d.className = "box";
        d.innerHTML = `<b>${c.images}</b><small>${s.toUpperCase()} images</small><b style="margin-top:6px">${c.labels}</b><small>${s.toUpperCase()} labels</small>`;
        box.appendChild(d);
      });
      show(box);
      show($("train-final-row"));
    } catch (err) {
      alert("Error: " + err.message);
    }
  }

  function wireTrainFinalize() {
    const btn = $("train-finalize");
    const msg = $("train-final-msg");
    const dlRow = $("train-dl-row");
    const dl = $("train-dl");
    btn.addEventListener("click", async () => {
      const folder = $("train-folder").value.trim();
      if (!folder) { setMsg(msg, "Enter the folder name.", false); return; }
      btn.disabled = true;
      try {
        const data = await postJSON("/api/finalize", { batch_id: state.train.batchId, folder_name: folder });
        setMsg(msg, `Folder "${data.folder_name}" is ready.`, true);
        dl.href = data.download_url;
        show(dlRow);
        show($("train-ready"));
      } catch (err) {
        setMsg(msg, "Error: " + err.message, false);
      } finally {
        btn.disabled = false;
      }
    });
  }

  // ---------------------------------------------------------- init
  wireFilePicker("pos", "object");
  wireFilePicker("neg", "nonobject");
  wireClassStep();
  wireCleanStep();
  wireFinalizeStep("pos");
  wireFinalizeStep("neg");
  wireBalanceFix();
  wireTrainFinalize();
})();
