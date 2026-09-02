"""FusionEngine - the CIF-LAAD core.

Pipeline per cycle (SENSE -> CORRELATE -> TRACK -> EVALUATE COHERENCE ->
PRODUCE EVIDENCE -> HAND OFF). It STOPS at handoff. It never authorises or
executes anything.

  1. validate every observation; rejects emit an Event and never enter the
     filter (fail visibly).
  2. predict all live tracks to the current clock.
  3. associate (chi-square gate + Hungarian) - shared with the baseline.
  4. update matched tracks; fold provenance and class votes.
  5. evaluate coherence (kinematic + identity + modal diversity) and record
     contradictions.
  6. compute a fail-closed confidence state.
  7. spawn tentative tracks for unassigned observations; run the lifecycle
     (confirm / coast / delete) WITH inheritance re-linking.
  8. append evidence records and produce track snapshots for handoff.

Every process() call is timed; latency is measured, never assumed.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Any, Tuple, Optional
import time
import numpy as np

from .observation import validate, ObservationError, SensorObservation
from .kalman import KalmanCV
from .correlation import associate, gate_threshold
from .track import Track, TENTATIVE, CONFIRMED, COASTING, DELETED
from . import coherence as coh
from . import confidence as conf


@dataclass
class FusionConfig:
    q: float = 8.0
    p_gate: float = 0.99
    confirm_hits: int = 3
    coast_misses: int = 3          # misses before a CONFIRMED track coasts
    inherit_window_s: float = 6.0  # how long a coasting id can be re-linked
    delete_misses: int = 8         # misses before a coasting track is deleted
    max_skew_s: float = 5.0
    min_hits_conf: int = 3
    merge_gate_p: float = 0.5      # tight gate for track-to-track de-duplication
    # --- coherence-gated inheritance (ARK-CIFLAAD clutter-regression fix) ---
    # inherit_mode selects the re-link algorithm under test:
    #   "legacy" - original one-obs-at-a-time revive on first gated blip
    #              (wide assoc. gate, no corroboration). The pre-experiment CIF.
    #   "batch"  - batch revive: a coasting id may absorb ALL its gated
    #              unassigned obs in one cycle (wide gate, support 1).
    #   "gated"  - coherence-gated: tighter re-link gate + >= inherit_min_support
    #              corroborating obs required to revive an id.
    # Default is "batch": empirically the best re-link policy on the 25-seed
    # matrix (fewest false tracks, best continuity, preserves the dropout win,
    # no harm on benign scenarios). The pre-registered "gated" hypothesis was
    # tested and FALSIFIED - it made clutter WORSE, not better. See
    # docs/07_COHERENCE_GATED_INHERITANCE.md.
    inherit_mode: str = "batch"
    coherence_gated_inherit: bool = False  # legacy alias, kept for meta/logging
    inherit_gate_p: float = 0.95   # TIGHTER gate for re-link (vs 0.99 assoc.)
    inherit_min_support: int = 2   # corroborating obs required to revive an id


@dataclass
class EngineResult:
    events: List[Dict[str, Any]]
    tracks: List[Dict[str, Any]]
    rejected: List[Dict[str, Any]]
    latency_s: float
    n_obs: int


class FusionEngine:
    def __init__(self, config: Optional[FusionConfig] = None):
        self.cfg = config or FusionConfig()
        self.gate = gate_threshold(self.cfg.p_gate)
        self.merge_gate = gate_threshold(self.cfg.merge_gate_p)
        self.inherit_gate = gate_threshold(self.cfg.inherit_gate_p)
        self.tracks: List[Track] = []
        self._coasted: List[Track] = []      # retained for inheritance
        self._next_id = 1
        self._seen_seq: Dict[str, int] = {}  # sensor_id -> last seq (replay)
        self.events: List[Dict[str, Any]] = []
        self.contradiction_log: List[Dict[str, Any]] = []

    # ---- helpers ----
    def _emit(self, chain, t, etype, payload):
        self.events.append({"t": t, "event_type": etype, **payload})
        if chain is not None:
            chain.append(t, etype, payload)

    def _spawn(self, obs: SensorObservation, now: float) -> Track:
        x0 = np.zeros(6)
        x0[:3] = obs.position
        P0 = np.eye(6) * 500.0
        P0[:3, :3] = obs.position_cov
        tr = Track(id=self._next_id, kf=KalmanCV(x0, P0, self.cfg.q),
                   status=TENTATIVE, created_t=now, last_update_t=now, hits=1)
        tr.contributing_sensors.add(obs.sensor_id)
        tr.contributing_modalities.add(obs.sensor_type)
        if obs.class_label:
            tr.class_posterior[obs.class_label] = obs.class_confidence
        if obs.rf_id:
            tr.rf_ids.add(obs.rf_id)
        tr.evidence_chain.append(now, "TRACK_CREATED", {
            "track_id": tr.id, "sensor_id": obs.sensor_id,
            "sensor_type": obs.sensor_type, "position": [float(x) for x in obs.position],
        })
        tr.provenance.append({"t": now, "sensor_id": obs.sensor_id,
                              "sensor_type": obs.sensor_type, "event": "created"})
        self._next_id += 1
        return tr

    def _try_inherit(self, obs: SensorObservation, now: float):
        """ORIGINAL (legacy) re-link: revive a coasting id on the FIRST
        unassigned obs that falls in the WIDE association gate of its
        predicted state. One obs, no corroboration. Preserved verbatim so the
        pre-experiment behaviour can be reproduced for honest comparison.
        """
        best = None
        best_d2 = None
        for tr in self._coasted:
            if now - tr.last_update_t > self.cfg.inherit_window_s:
                continue
            tr.predict(now)
            y, S = tr.kf.innovation(obs.position, obs.position_cov)
            d2 = float(y.T @ np.linalg.inv(S) @ y)
            if d2 <= self.gate and (best_d2 is None or d2 < best_d2):
                best, best_d2 = tr, d2
        if best is not None:
            best.status = CONFIRMED
            best.inherited = True
            best.misses = 0
            best.update_with(obs, best_d2, now)
            best.evidence_chain.append(now, "TRACK_INHERITED", {
                "track_id": best.id, "sensor_id": obs.sensor_id, "d2": best_d2,
                "support": 1, "coherence_gated": False,
                "gap_s": now - best.provenance[-1]["t"] if best.provenance else None,
            })
            self._coasted.remove(best)
            self.tracks.append(best)
        return best

    def _inherit_batch(self, unassigned: List[int],
                       valid: List[SensorObservation], now: float) -> set:
        """Coherence-gated inheritance. Returns the set of consumed obs indices.

        A coasting id is revived to CONFIRMED only when it is CORROBORATED by
        at least ``inherit_min_support`` unassigned observations that fall
        within the TIGHT inheritance gate of its predicted state in the SAME
        cycle. A lone clutter false-alarm therefore cannot yank a coasting
        track's estimate onto clutter and revive it as a confirmed false
        track - the original heavy-clutter regression.

        When ``coherence_gated_inherit`` is False the support requirement
        drops to 1 and the WIDE association gate is used (the original
        single-blip behaviour), so before/after can be compared cleanly.
        """
        consumed: set = set()
        if not self._coasted or not unassigned:
            return consumed
        gated = self.cfg.inherit_mode == "gated"
        gate = self.inherit_gate if gated else self.gate
        min_support = self.cfg.inherit_min_support if gated else 1

        # gather candidate unassigned obs per eligible coasting track
        cand = []  # (best_d2, track, [(oi, d2), ...])
        for tr in self._coasted:
            if now - tr.last_update_t > self.cfg.inherit_window_s:
                continue
            tr.predict(now)
            matches = []
            for oi in unassigned:
                ob = valid[oi]
                y, S = tr.kf.innovation(ob.position, ob.position_cov)
                d2 = float(y.T @ np.linalg.inv(S) @ y)
                if d2 <= gate:
                    matches.append((oi, d2))
            if matches:
                matches.sort(key=lambda m: m[1])
                cand.append((matches[0][1], tr, matches))

        # greedily revive the best-fitting tracks first; each obs used once
        cand.sort(key=lambda c: c[0])
        for _best_d2, tr, matches in cand:
            avail = [(oi, d2) for (oi, d2) in matches if oi not in consumed]
            if len(avail) < min_support:
                continue
            avail.sort(key=lambda m: m[1])
            primary_oi, primary_d2 = avail[0]
            tr.status = CONFIRMED
            tr.inherited = True
            tr.misses = 0
            tr.update_with(valid[primary_oi], primary_d2, now)
            tr.evidence_chain.append(now, "TRACK_INHERITED", {
                "track_id": tr.id, "sensor_id": valid[primary_oi].sensor_id,
                "d2": primary_d2, "support": len(avail),
                "coherence_gated": gated,
                "gap_s": now - tr.provenance[-1]["t"] if tr.provenance else None,
            })
            for oi, _ in avail:
                consumed.add(oi)
            self._coasted.remove(tr)
            self.tracks.append(tr)
        return consumed

    # ---- main cycle ----
    def process(self, observations: List[SensorObservation], now: float) -> EngineResult:
        t0 = time.perf_counter()
        self.events = []
        rejected: List[Dict[str, Any]] = []

        # 1. validate + replay/duplicate defence
        valid: List[SensorObservation] = []
        for ob in observations:
            try:
                validate(ob, now, self.cfg.max_skew_s)
            except ObservationError as e:
                rejected.append({"sensor_id": getattr(ob, "sensor_id", None),
                                 "code": e.code, "reason": str(e)})
                self._emit(None, now, "OBS_REJECTED",
                           {"sensor_id": getattr(ob, "sensor_id", None), "code": e.code})
                continue
            if ob.seq is not None:
                last = self._seen_seq.get(ob.sensor_id)
                if last is not None and ob.seq <= last:
                    rejected.append({"sensor_id": ob.sensor_id, "code": "E_REPLAY",
                                     "reason": f"seq {ob.seq} <= last {last}"})
                    self._emit(None, now, "OBS_REPLAY_REJECTED",
                               {"sensor_id": ob.sensor_id, "seq": ob.seq})
                    continue
                self._seen_seq[ob.sensor_id] = ob.seq
            valid.append(ob)

        # 2. predict live tracks
        for tr in self.tracks:
            tr.predict(now)

        # 3. associate + update, multi-pass so co-temporal observations from
        #    several sensors fold into ONE track (sequential Kalman update).
        #    Hungarian assignment is one-to-one per pass; repeated passes let a
        #    track accept corroborating observations from other modalities.
        assigned_tracks = set()
        per_track: Dict[int, List[Tuple[SensorObservation, float]]] = {}
        remaining_idx = list(range(len(valid)))
        while remaining_idx and self.tracks:
            subset = [valid[j] for j in remaining_idx]
            assignments, unassigned = associate(self.tracks, subset, self.gate)
            if not assignments:
                break
            for ti, oj, d2 in assignments:
                ob = subset[oj]
                tr = self.tracks[ti]
                tr.update_with(ob, d2, now)
                per_track.setdefault(ti, []).append((ob, d2))
                assigned_tracks.add(ti)
            remaining_idx = [remaining_idx[j] for j in unassigned]
        unassigned = remaining_idx

        # 4./5./6. coherence + confidence per updated track
        for ti, obs_list in per_track.items():
            tr = self.tracks[ti]
            # coherence over this cycle's contributors
            class_votes = dict(tr.class_posterior)
            modalities = [ob.sensor_type for ob, _ in obs_list]
            rf_ids = [ob.rf_id for ob, _ in obs_list if ob.rf_id]
            cres = coh.evaluate(tr.smoothed_nis, class_votes, list(tr.rf_ids) + rf_ids,
                                sorted(tr.contributing_modalities), now)
            tr.coherence_score = cres.score
            for c in cres.contradictions:
                self.contradiction_log.append({"track_id": tr.id, "t": now,
                                               "kind": c.kind, "detail": c.detail,
                                               "severity": c.severity})
                tr.evidence_chain.append(now, "CONTRADICTION", {
                    "track_id": tr.id, "kind": c.kind, "detail": c.detail,
                    "severity": c.severity, "sources": c.sources})
            cstate = conf.evaluate(
                tr.hits, tr.misses, cres.score, cres.modal_diversity,
                float(np.trace(tr.kf.position_cov)), bool(cres.contradictions),
                min_hits=self.cfg.min_hits_conf)
            tr.confidence = cstate
            if tr.status == TENTATIVE and tr.hits >= self.cfg.confirm_hits:
                tr.status = CONFIRMED
                tr.evidence_chain.append(now, "TRACK_CONFIRMED", {"track_id": tr.id})
            tr.evidence_chain.append(now, "TRACK_UPDATED", {
                "track_id": tr.id, "coherence": cres.score,
                "confidence": cstate.level, "nis": tr.smoothed_nis,
                "position": [float(x) for x in tr.kf.position]})

        # 7. misses + lifecycle + inheritance
        for i, tr in enumerate(self.tracks):
            if i not in assigned_tracks:
                tr.mark_miss()
                if tr.status == CONFIRMED and tr.misses >= self.cfg.coast_misses:
                    tr.status = COASTING
                    tr.evidence_chain.append(now, "TRACK_COASTING", {
                        "track_id": tr.id, "misses": tr.misses})

        # move coasting tracks into the retained pool
        still_live: List[Track] = []
        for tr in self.tracks:
            if tr.status == COASTING:
                self._coasted.append(tr)
            elif tr.status == TENTATIVE and tr.misses >= self.cfg.coast_misses:
                tr.status = DELETED
                tr.evidence_chain.append(now, "TRACK_DELETED", {"track_id": tr.id,
                                                                 "reason": "tentative_timeout"})
            else:
                still_live.append(tr)
        self.tracks = still_live

        # spawn / inherit for unassigned observations. Group co-temporal
        # unassigned observations that gate to each other into a single new
        # track so one target seen by N sensors does not create N tracks.
        if self.cfg.inherit_mode == "legacy":
            consumed = set()
            for oi in unassigned:
                if self._try_inherit(valid[oi], now) is not None:
                    consumed.add(oi)
        else:
            consumed = self._inherit_batch(unassigned, valid, now)
        for oi in unassigned:
            if oi in consumed:
                continue
            ob = valid[oi]
            merged = False
            for tr in self.tracks:
                if now - tr.last_update_t > 0:
                    continue
                y, S = tr.kf.innovation(ob.position, ob.position_cov)
                d2 = float(y.T @ np.linalg.inv(S) @ y)
                if d2 <= self.gate:
                    tr.update_with(ob, d2, now)
                    merged = True
                    break
            if not merged:
                self.tracks.append(self._spawn(ob, now))

        # de-duplicate: two confirmed tracks whose predicted states coincide
        # within a TIGHT gate are the same target seen twice (e.g. a noisy
        # sensor spawned a parallel track). Merge the weaker into the stronger.
        # The gate is tight (p=0.5) so genuinely distinct targets that merely
        # cross are NOT merged. Same routine runs in the baseline for fairness.
        self._merge_duplicates(now)

        # expire coasting tracks past the delete window
        kept_coast: List[Track] = []
        for tr in self._coasted:
            if now - tr.last_update_t > max(self.cfg.inherit_window_s,
                                            self.cfg.delete_misses * 0.5):
                tr.status = DELETED
                tr.evidence_chain.append(now, "TRACK_DELETED", {
                    "track_id": tr.id, "reason": "coast_expired"})
            else:
                kept_coast.append(tr)
        self._coasted = kept_coast

        latency = time.perf_counter() - t0
        snapshots = [tr.to_track_api() for tr in self.tracks
                     if tr.status in (CONFIRMED, COASTING)]
        return EngineResult(events=list(self.events), tracks=snapshots,
                            rejected=rejected, latency_s=latency, n_obs=len(observations))

    def _merge_duplicates(self, now: float) -> None:
        kept: List[Track] = []
        # survivor is the better-established track (more hits, then older id)
        for tr in sorted(self.tracks, key=lambda t: (-t.hits, t.id)):
            dup_of = None
            for kt in kept:
                dy = tr.kf.position - kt.kf.position
                Ssum = tr.kf.position_cov + kt.kf.position_cov
                d2 = float(dy @ np.linalg.inv(Ssum) @ dy)
                if d2 <= self.merge_gate:
                    dup_of = (kt, d2)
                    break
            if dup_of is None:
                kept.append(tr)
                continue
            kt, d2 = dup_of
            kt.contributing_sensors |= tr.contributing_sensors
            kt.contributing_modalities |= tr.contributing_modalities
            kt.rf_ids |= tr.rf_ids
            for k, v in tr.class_posterior.items():
                kt.class_posterior[k] = kt.class_posterior.get(k, 0.0) + v
            kt.hits = max(kt.hits, tr.hits)
            kt.inherited = kt.inherited or tr.inherited
            kt.evidence_chain.append(now, "TRACK_MERGED", {
                "kept_id": kt.id, "absorbed_id": tr.id, "d2": d2})
        self.tracks = kept

    def all_tracks(self) -> List[Track]:
        return list(self.tracks) + list(self._coasted)

    def verify_all_evidence(self) -> bool:
        return all(tr.evidence_chain.verify() for tr in self.all_tracks())
