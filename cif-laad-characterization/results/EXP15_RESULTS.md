# EXP-15 Results: latency and throughput scaling study

**Status:** COMPLETE. Descriptive scaling study, no ADOPT or REJECT verdict, no
engine change. This is the final experiment of the release characterization
package.

**Engine integrity:** CIF-LAAD frozen engine (SHA-256 manifest 8712f113...7ad45,
14 files), batch inheritance mode, q=8 frozen default. Stone Soup GNN in the
EXP-9 locked configuration. Stone Soup JPDA in the EXP-14 locked configuration.
No tracker was retuned for this study. All three trackers ran in the same
process, on the same machine, back to back per seed, so relative timing is on
equal footing.

**Environment (captured in the results JSON):** Python 3.11.6, numpy 2.2.6,
scipy 1.14.1, Stone Soup 1.9.1, Linux x86_64 (kernel 6.17, AWS). Thread caps
unset (OMP/MKL/OpenBLAS unset). Simulation only, TRL 3.

**Seeds:** 5 per workload point (100 to 104). **Per-seed time cap:** 300 s.
**Total wall-clock for the corrected run:** 3218.62 s (about 54 minutes).

**Raw data:** `experiments/laad_series/out/exp15_scaling_benchmark.json`
(authoritative machine-readable record). Run log: `out/exp15.log`.

---

## 1. Executive summary

EXP-15 turns the fixed-size compute gaps observed in EXP-9 and EXP-14 into
scaling curves and locates, for each tracker, the workload at which it stops
meeting a fixed operational budget. Two independent sweeps were run: target count
(throughput) and clutter density (detection load).

The headline is a scaling-boundary result, stated as boundaries and never as a
win:

- **CIF-LAAD** completes every point in both sweeps within the time cap and never
  crosses either operational budget (500 ms/2 Hz primary, 100 ms/10 Hz
  secondary), even at p95, across the entire swept range (up to N=32 targets and
  up to clutter_rate=32). Its per-cycle cost grows smoothly and stays in the
  single-digit-to-low-double-digit millisecond range. This is a compute-cost
  statement only; CIF-LAAD's own tracking quality degrades as load grows (see
  Section 5), which is the real limit on how far it should be pushed.
- **Stone Soup GNN** and **Stone Soup JPDA** both reach a hard scaling boundary
  by hitting the 300 s per-seed time cap: at **N=8 targets** on the throughput
  sweep and at **clutter_rate=4** on the density sweep. Past those points they
  are skipped by the pre-registered rule. Before timing out, both also cross the
  100 ms secondary line at p95 much earlier (Section 4).

Three distinct boundaries are reported and kept separate throughout this
document: the 500 ms/2 Hz primary budget, the 100 ms/10 Hz secondary reference
line, and the 300 s experimental per-seed time cap. They are different thresholds
and must not be conflated.

An execution-harness correction was made during this experiment (Section 6). It
changed only timeout enforcement and checkpoint/resume persistence. It did not
change any tracker logic, parameter, seed, sweep value, budget, cap, skip rule,
or scoring. A control point confirmed the corrected harness reproduces the prior
quality outputs bit-for-bit.

---

## 2. What was measured

For every tracker at every workload point, over 5 seeds:

1. Wall-clock time per seed (full scenario).
2. Per-cycle (per-frame) processing time: mean, median, and p95, in
   milliseconds. Per-cycle time is the primary scaling quantity. The frame rate
   is 2 Hz (DT = 0.5 s), so the 500 ms/cycle budget is the real-time line.
3. Workload actually presented: mean detections per frame (after fusion) and
   mean live tracks per frame. These are the real-load x-axis quantities.
4. Tracking-quality metrics (RMSE, ID switches, continuity, false-track frames)
   for context. These are NOT the endpoints of EXP-15; accuracy comparison lives
   in EXP-9 and EXP-14.

---

## 3. Scaling curves (median / p95 per-cycle time, ms)

Entries read `median/p95` in milliseconds. `TIME CAP` means the tracker hit the
300 s per-seed cap at that point (a scaling boundary). `skipped` means the point
was not run because a smaller workload on the same axis already hit the boundary
for that tracker, per the pre-registered skip rule.

### Sweep A, throughput (clutter_rate = 1.0)

| N targets | dets/frame | tracks/frame | CIF-LAAD | Stone Soup GNN | Stone Soup JPDA |
|-----------|-----------|--------------|----------|----------------|-----------------|
| 2  | 8.3   | 2.0  | 2.2 / 3.7   | 6.9 / 12.0    | 8.3 / 14.2   |
| 4  | 13.6  | 4.0  | 2.6 / 4.2   | 12.9 / 27.4   | 14.5 / 23.1  |
| 6  | 18.5  | 6.0  | 3.6 / 5.5   | 50.8 / 1556.3 | 28.0 / 69.9  |
| 8  | 23.5  | 7.6  | 4.3 / 6.8   | TIME CAP      | TIME CAP     |
| 12 | 34.0  | 10.7 | 5.2 / 7.4   | skipped       | skipped      |
| 16 | 44.6  | 12.6 | 6.3 / 9.7   | skipped       | skipped      |
| 24 | 65.5  | 16.0 | 8.2 / 12.4  | skipped       | skipped      |
| 32 | 86.3  | 16.8 | 10.3 / 15.5 | skipped       | skipped      |

### Sweep B, detection density (N = 6 targets)

| clutter_rate | dets/frame | tracks/frame | CIF-LAAD | Stone Soup GNN | Stone Soup JPDA |
|--------------|-----------|--------------|----------|----------------|-----------------|
| 0  | 15.6  | 6.0 | 1.9 / 2.6   | 30.3 / 730.5   | 17.0 / 46.6  |
| 1  | 18.5  | 6.0 | 3.2 / 4.6   | 49.2 / 1364.2  | 26.7 / 63.5  |
| 2  | 21.6  | 5.6 | 4.7 / 6.8   | 68.0 / 2194.7  | 42.3 / 92.7  |
| 4  | 27.3  | 6.0 | 6.5 / 10.5  | TIME CAP       | TIME CAP     |
| 8  | 39.6  | 4.4 | 8.7 / 13.5  | skipped        | skipped      |
| 16 | 63.5  | 2.9 | 11.2 / 17.6 | skipped        | skipped      |
| 32 | 112.2 | 1.2 | 15.3 / 23.7 | skipped        | skipped      |

The shared point (N=6, clutter=1) appears in both sweeps and is internally
consistent (CIF 3.6/5.5 ms, GNN 50.8 ms median, JPDA 28.0 ms median in Sweep A;
CIF 3.2/4.6 ms, GNN 49.2 ms median, JPDA 26.7 ms median at Sweep B clutter=1),
which is the intended cross-check against the standalone EXP-9/EXP-14 six-target
numbers.

---

## 4. Scaling boundaries (three thresholds, kept distinct)

### 4.1 Primary budget: 500 ms per cycle (2 Hz real time)

No tracker crosses the 500 ms line on **median** per-cycle time at any completed
point in either sweep. CIF-LAAD does not cross it even at **p95** anywhere in the
swept range; its worst p95 is 23.7 ms (Sweep B, clutter=32). GNN and JPDA never
reach the 500 ms median line at their completed points; instead they exit the
swept range by hitting the 300 s time cap (Section 4.3) before median cost
approaches 500 ms. GNN does exceed 500 ms at **p95** early (1556.3 ms at Sweep A
N=6; 730.5 ms at Sweep B clutter=0), meaning its tail latency already blows the
primary budget well before its median does.

### 4.2 Secondary reference line: 100 ms per cycle (10 Hz)

- **CIF-LAAD:** never crosses 100 ms on median or p95 anywhere in either sweep.
- **Stone Soup GNN:** median stays under 100 ms at all completed points (max
  median 68.0 ms at Sweep B clutter=2), but **p95 crosses 100 ms very early**:
  between N=4 (p95 27.4 ms) and N=6 (p95 1556.3 ms) on the throughput sweep, and
  from the very first density point (clutter=0, p95 730.5 ms) on the density
  sweep. GNN's tail latency is the first thing to break the 10 Hz line.
- **Stone Soup JPDA:** median stays under 100 ms at all completed points (max
  median 42.3 ms at Sweep B clutter=2). **p95 crosses 100 ms** between Sweep B
  clutter=2 (92.7 ms) and clutter=4 (time cap); on the throughput sweep JPDA p95
  is still under 100 ms at N=6 (69.9 ms) and the next point (N=8) hits the time
  cap.

Interpretation: for GNN and JPDA the 100 ms/10 Hz line is first broken at the
tail (p95), not the median, and the median never gets the chance to cross it
because the 300 s cap is reached first.

### 4.3 Experimental per-seed time cap: 300 s (a scaling boundary)

This is an experiment-bounding cap, not an operational budget. Both comparators
hit it:

- **Sweep A (throughput):** GNN and JPDA both reach the cap at **N=8** targets
  (first seed terminated cleanly at 315.1 s / 315.1 s wall, including subprocess
  teardown). N=12 through N=32 skipped for both, per the skip rule.
- **Sweep B (density):** GNN and JPDA both reach the cap at **clutter_rate=4**.
  clutter 8, 16, 32 skipped for both.

CIF-LAAD never approaches the cap; its largest per-seed wall time is about 8 s
(Sweep A N=32).

A time-cap hit and a budget crossing are different events and are reported
separately above. Neither is scored as a win for CIF-LAAD; each is a scaling
limitation of the tracker that reached it.

---

## 5. CIF-LAAD tracking quality across the sweeps (context, not endpoint)

CIF-LAAD completes every point, but completing a point is not the same as
tracking it well. Quality degrades as load grows, and this degradation, not
compute, is the real limit on how far CIF-LAAD should be pushed. All points below
have n_ok = 5/5 seeds.

### Sweep A (clutter=1.0), CIF-LAAD mean quality

| N | position RMSE (m) | ID switches | continuity | false-track frames |
|----|------|------|-------|-------|
| 2  | 10.3 | 1.0  | 0.979 | 6.0   |
| 4  | 18.0 | 2.2  | 0.941 | 17.0  |
| 6  | 24.0 | 5.2  | 0.935 | 28.8  |
| 8  | 25.5 | 8.6  | 0.857 | 59.2  |
| 12 | 30.9 | 19.6 | 0.768 | 117.2 |
| 16 | 34.0 | 35.4 | 0.655 | 174.0 |
| 24 | 38.2 | 65.4 | 0.502 | 317.2 |
| 32 | 40.4 | 85.4 | 0.409 | 303.4 |

### Sweep B (N=6), CIF-LAAD mean quality

| clutter | position RMSE (m) | ID switches | continuity | false-track frames |
|---------|------|------|-------|-------|
| 0  | 17.0 | 5.8 | 0.944 | 24.8  |
| 1  | 24.0 | 5.2 | 0.935 | 28.8  |
| 2  | 27.1 | 5.2 | 0.867 | 35.8  |
| 4  | 32.1 | 6.2 | 0.797 | 94.8  |
| 8  | 38.6 | 6.6 | 0.540 | 95.8  |
| 16 | 47.4 | 3.8 | 0.192 | 140.8 |
| 32 | 48.6 | 0.2 | 0.019 | 84.6  |

Read honestly: as target count rises from 2 to 32, CIF-LAAD RMSE roughly
quadruples (10.3 m to 40.4 m), ID switches climb from about 1 to about 85, and
continuity falls from 0.98 to 0.41. Under heavy clutter (clutter=32) continuity
collapses to 0.019 and ID switches fall to near zero because so few tracks are
held at all. CIF-LAAD stays cheap to compute at these loads, but its output
quality is well past usable at the high end of the sweep. The compute-scaling
advantage does not extend to an accuracy advantage at scale, and no such claim is
made.

For context at the low-N points where all three trackers complete, GNN and JPDA
position RMSE is lower than CIF-LAAD's (e.g. N=6: GNN 10.3 m, JPDA 10.6 m vs CIF
24.0 m), consistent with EXP-9 and EXP-14. EXP-15 does not revisit that accuracy
comparison; it is a compute-scaling study.

---

## 6. Execution-harness correction (methodology record)

EXP-15 was run three times. The first two runs are preserved here as part of the
methodology record; they were not experimental failures but execution-harness
failures.

**The two earlier runs.** Both terminated externally partway through, with an
empty stderr and no out-of-memory signal. Diagnosis: the original 300 s timeout
was enforced with a Python daemon `threading.Thread` plus `thread.join()`. Python
daemon threads cannot be forcibly killed. When a Stone Soup GNN or JPDA
computation exceeded 300 s, the join returned but the underlying compute thread
kept running at full CPU as an orphan. Those orphan threads accumulated, saturated
the cores, and the process was eventually reaped by an external watchdog. This is
a defect in timeout enforcement, not in the experimental design.

**The correction.** Two changes, and only these two:

1. **Killable timeout.** Each per-seed tracker run now executes in a separate
   `multiprocessing` subprocess (fork start method). The parent waits on a result
   queue with the same 300 s cap; on timeout the parent calls `terminate()` on
   the child, which actually kills the runaway computation and reclaims the CPU.
   The worker rebuilds the scenario deterministically from the same seed and runs
   the identical timed run functions, so results are unchanged.
2. **Checkpoint and resume.** After every completed workload point the results
   JSON is written atomically (temp file plus `os.replace`). On restart the
   harness reloads the existing JSON, keys completed points by
   `(n_targets, clutter_rate)`, and resumes from where it stopped.

Nothing else was touched. The frozen experimental design (target counts, seeds,
tracker configurations, sweep values, budgets, 300 s cap, skip rule, scoring) is
byte-for-byte unchanged. A unified diff against the pre-correction backup
(`exp15_scaling_benchmark.py.orig`) confirms the change is confined to imports,
the two new helpers, the per-seed subprocess call, and the resume/checkpoint
plumbing in `main`.

**Control point (pre-authorized pass criterion).** Before the full rerun, the
single point N=2, clutter=1.0, seeds 100 to 104 was run both in-process (old
path) and via the corrected subprocess path and compared. Result: **maximum
absolute difference in deterministic quality outputs = 0.00e+00 (bit-identical)**
across all three trackers and all five seeds. All subprocesses terminated
cleanly, and the checkpoint JSON was written, reloaded, and its temp file cleaned.
Timing was in the same range as the prior logged result (subprocess mean-of-median
cycle times CIF 2.08, GNN 8.54, JPDA 9.66 ms vs prior 2.2, 10.1, 11.1 ms); timing
variance alone was pre-registered as not a failure. The control point passed, and
the full rerun proceeded exactly as pre-registered and corrected.

**Corrected-run validation.** The corrected harness survived both time-cap
boundaries (GNN and JPDA at Sweep A N=8 and Sweep B clutter=4), terminating each
runaway child cleanly at about 315 s, and it ran to completion through the
Sweep B clutter=0 point that had terminated both earlier runs. Checkpointing
advanced point by point, the final JSON is valid and reloadable, and stderr was
empty (0 bytes). Zero orphan worker processes remained after completion.

---

## 7. Measurement-cleanliness note (numbers superseded)

The corrected run supersedes the earlier (contaminated) log for CIF-LAAD's
large-N timings, and this is called out explicitly for the record.

In the earlier runs the orphan GNN/JPDA compute threads described in Section 6
kept running at full CPU for the remainder of the run after the N=8 time cap.
CIF-LAAD points measured after that (N=12 and up) were therefore timed while
sharing cores with two runaway threads, which inflated their per-cycle numbers.
The onset matches this mechanism exactly: CIF timings agree with the corrected
run up to and including N=8 (the last point before the timeouts) and diverge only
from N=12 onward, where the earlier log showed CIF rising to roughly 59 ms at
N=32 versus 10.3 ms in the clean corrected run.

This is presented as a strongly supported hypothesis, not a proven mechanism: the
exact-onset pattern and the bit-identical N=2 control both support it, but the
earlier per-seed numbers cannot be re-audited because the old contaminated log
was overwritten by the corrected run. The correct reading is narrow: the
corrected numbers in Section 3 are the clean measurement, and the earlier
large-N CIF figures should not be cited. This is a measurement-cleanliness
correction. It is not a CIF-LAAD performance win, and a lower measured latency
does not offset the quality degradation documented in Section 5.

---

## 8. What this study can and cannot conclude

- **CAN:** locate each tracker's compute-scaling boundary against fixed budgets
  on identical hardware, and show the shape of the cost curve versus real load.
  CIF-LAAD stays inside both operational budgets across the entire swept range;
  GNN and JPDA reach the 300 s time cap at N=8 (throughput) and clutter=4
  (density), with their p95 latency breaking the 100 ms line earlier still.
- **CANNOT:** establish accuracy superiority (that is EXP-9 and EXP-14), justify
  any engine change, or make any claim about hardware, real sensors, or
  deployment. CIF-LAAD's own quality degrades badly at the high end of both
  sweeps (Section 5), which bounds the usable range regardless of compute cost.
  Simulation only, TRL 3.

---

## 9. Standing guardrails honored

- Pre-registered before running; run exactly as pre-registered and corrected.
- No tracker retuned after evaluation began.
- A timeout or budget miss is reported as a scaling boundary, never a performance
  win, including for CIF-LAAD.
- The 500 ms/2 Hz budget, the 100 ms/10 Hz reference line, and the 300 s
  experimental time cap are reported as three distinct thresholds.
- v1 engine frozen and byte-identical (SHA-256 8712f113...7ad45); q=8 frozen
  default; GNN and JPDA configurations unchanged from EXP-9 and EXP-14.
- Harness correction limited to killable-subprocess timeout enforcement and
  checkpoint/resume persistence; the two earlier terminated runs and this
  correction note are preserved in the methodology record.
- This is the last experiment of the release. After EXP-15, experimentation stops
  and the package (EXP-9, EXP-10, EXP-11, EXP-12, EXP-14, EXP-15) is prepared for
  publication as part of the CIF-LAAD characterization package.

## 10. Deliverables

- `experiments/laad_series/exp15_scaling_benchmark.py` (corrected harness)
- `experiments/laad_series/exp15_scaling_benchmark.py.orig` (pre-correction backup)
- `experiments/laad_series/exp15_control_check.py` (control-point reproduction)
- `experiments/laad_series/out/exp15_scaling_benchmark.json` (raw results)
- `experiments/laad_series/out/exp15_control_check.json` (control-point results)
- `experiments/laad_series/EXP15_RESULTS.md` (this document, plus auto PDF/DOCX)
