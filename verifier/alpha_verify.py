#!/usr/bin/env python3
"""Reference verifier for the accountability axis (alpha) of agent actions.

Implements the normative semantics of SPEC.md (alpha-axis/0.1) and runs the
test vectors in ../vectors. Standard library only. Python 3.8+.

Three modes:

  selftest                Evaluate every vector with the reference semantics
                          and check the result against the vector's `expect`
                          block. Proves that SPEC.md, the vectors and this
                          file agree with each other.

  records  [-o FILE]      Emit the reference decision record for every case,
                          in the record format of SPEC.md section 7. This is
                          the shape an implementation under test must produce.

  audit    RECORDS.json   Compare an implementation's decision records (keyed
                          by case id) against the vectors. Each case yields
                          PASS, FAIL or UNESTABLISHED. Exit status 0 only if
                          every case is PASS.

  evaluate INPUT.json     Evaluate one input (an action or a chain, in the
                          vector input format) and print its decision record.

Design commitments, each traceable to a section of SPEC.md:

  * alpha has two classes, `delegable` and `human_only`; anything else in the
    record is `undeclared`, and `undeclared` gates as `human_only` (S4.2).
  * A declaration under agent control is not a declaration (S3.2, S4.2).
  * alpha contributes HUMAN_OWNS or nothing; required oversight is the worse
    of the kappa axis and the alpha axis, folded independently (S4.3, S5.3).
  * A chain is usable only if it was established outside agent control, at
    plan stage, before the first untrusted read (S5.1).
  * A human_only action proceeds only when a human is recorded as the party
    to the obligation, not as the approver, and the binding step is executed
    or released by that party, never performed by the agent (S6).
  * Every check returns PASS, FAIL or UNESTABLISHED; at the gate, only PASS
    proceeds. Three states in the record, two outcomes at the gate (S8).
  * Nothing on the decision path raises. Malformed input is a verdict, not an
    exception (fail closed), following the convention of the AISVS C9
    reference model this work sits beside.

Copyright 2026 K. Lunina. Licensed under the Apache License, Version 2.0.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

SPEC_ID = "alpha-axis/0.1"
__version__ = "0.1.0"

PASS, FAIL, UNESTABLISHED = "PASS", "FAIL", "UNESTABLISHED"
PROCEED, BLOCK = "proceed", "block"
DELEGABLE, HUMAN_ONLY, UNDECLARED = "delegable", "human_only", "undeclared"

# --------------------------------------------------------------------------
# The kappa side. Reproduced from the public AISVS C9 reference model
# (Mayur021/aisvs-c9-action-class-conformance, v1.2.0) so that vectors are
# self-contained. An implementation MAY use any kappa grader; the audit mode
# never fails a record on the kappa value itself, only on how alpha composes
# with it. See SPEC.md S4.3 and Appendix A.
# --------------------------------------------------------------------------
OVERSIGHT = ["UNATTENDED", "SUPERVISED", "APPROVAL_REQUIRED", "HUMAN_OWNS"]
REVERSIBILITY = ["READ_ONLY", "REVERSIBLE", "EXTERNALLY_REVERSIBLE", "IRREVERSIBLE"]
CONSEQUENCE = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

_EFFECT_TO_REVERSIBILITY = {
    "read_only": "READ_ONLY",
    "recoverable_local": "REVERSIBLE",
    "externally_recoverable": "EXTERNALLY_REVERSIBLE",
    "non_recoverable": "IRREVERSIBLE",
    "externally_visible": "IRREVERSIBLE",
}
_OVERSIGHT_FROM_REVERSIBILITY = dict(zip(REVERSIBILITY, OVERSIGHT))
_OVERSIGHT_FROM_CONSEQUENCE = dict(zip(CONSEQUENCE, OVERSIGHT))


def _rank(tier: Any) -> int:
    return OVERSIGHT.index(tier) if tier in OVERSIGHT else len(OVERSIGHT) - 1


def _worse(a: str, b: str) -> str:
    return OVERSIGHT[max(_rank(a), _rank(b))]


def kappa_oversight(action: Dict[str, Any]) -> Dict[str, Any]:
    """Oversight on the kappa axis (reversibility x consequence).

    If the input supplies `oversight_kappa` directly, it is taken as the
    verdict of whatever kappa grader the implementation uses. Otherwise the
    reference ladder is applied, failing closed on anything undeclared or
    unrecognised, exactly as the C9 reference model does.
    """
    supplied = action.get("oversight_kappa")
    if isinstance(supplied, str) and supplied in OVERSIGHT:
        return {
            "reversibility": None,
            "consequence": None,
            "oversight": supplied,
            "basis": "supplied by the implementation's kappa grader",
        }
    effect = action.get("declared_effect")
    rev = _EFFECT_TO_REVERSIBILITY.get(effect, "IRREVERSIBLE") if isinstance(effect, str) else "IRREVERSIBLE"
    cons = action.get("consequence")
    cons = cons if isinstance(cons, str) and cons in CONSEQUENCE else "CRITICAL"
    ov = _worse(_OVERSIGHT_FROM_REVERSIBILITY[rev], _OVERSIGHT_FROM_CONSEQUENCE[cons])
    return {
        "reversibility": rev,
        "consequence": cons,
        "oversight": ov,
        "basis": "reference ladder (AISVS C9 reference model v1.2.0), worse of two axes",
    }


# --------------------------------------------------------------------------
# alpha resolution (SPEC.md S4.2, D3)
# --------------------------------------------------------------------------
def resolve_alpha(action: Dict[str, Any]) -> Dict[str, Any]:
    """Resolve the accountability class of one action from its declaration.

    Returns a record block with:
      raw        what the declaration store said (or None)
      declared   `delegable` | `human_only` | `undeclared` (the recognised state)
      source     where it came from and on which side of the trust boundary
      trust      PASS | FAIL | UNESTABLISHED  (the trust-boundary check)
      effective  `delegable` | `human_only`   (what the gate uses)
    `effective` is `delegable` only when the declaration is recognised AND
    its trust check is PASS. Every other combination fails closed.
    """
    decl = action.get("alpha")
    if not isinstance(decl, dict):
        return {
            "raw": decl,
            "declared": UNDECLARED,
            "source": None,
            "trust": UNESTABLISHED,
            "effective": HUMAN_ONLY,
            "basis": "no declaration present; undeclared gates as human_only",
        }
    raw = decl.get("value")
    recognised = raw if raw in (DELEGABLE, HUMAN_ONLY) else UNDECLARED
    source = decl.get("source") if isinstance(decl.get("source"), dict) else {}
    control = source.get("control", "unknown")
    kind = source.get("kind", "unspecified")

    if control == "agent":
        trust, basis = FAIL, (
            "declaration is under agent control (source=%s); a declaration the "
            "gated party can author, select or write is not a declaration" % kind
        )
    elif control == "external":
        trust, basis = PASS, "declaration created, maintained and stored outside agent control (source=%s)" % kind
    else:
        trust, basis = UNESTABLISHED, "trust boundary of the declaration source not evidenced (source=%s)" % kind

    if trust == PASS and recognised == DELEGABLE:
        effective = DELEGABLE
    else:
        effective = HUMAN_ONLY
        if recognised == UNDECLARED and trust == PASS:
            basis += "; value %r not in {delegable, human_only}: undeclared gates as human_only" % (raw,)
        elif trust != PASS:
            basis += "; gated as human_only (fail closed)"

    return {
        "raw": raw,
        "declared": recognised if trust != FAIL else UNDECLARED,
        "source": {"kind": kind, "control": control},
        "trust": trust,
        "effective": effective,
        "basis": basis,
    }


def alpha_oversight(effective: str) -> str:
    """alpha contributes the top tier or nothing (SPEC.md S4.3, C1)."""
    return "HUMAN_OWNS" if effective == HUMAN_ONLY else "UNATTENDED"


# --------------------------------------------------------------------------
# Accountable-party check (SPEC.md S6.3)
# --------------------------------------------------------------------------
_NON_HUMAN_PARTY = {"agent", "service", "role", "group", "team", "organisation", "organization"}
# Who may execute the binding step of a human_only action (SPEC.md S6.1, S6.2).
_PARTY_PERFORMERS = frozenset({"party", "release_on_party_authority"})


def _check_one_obligation_record(rec: Dict[str, Any]) -> Tuple[str, str]:
    control = rec.get("record_control", "unknown")
    if control == "agent":
        return UNESTABLISHED, "obligation record is under agent control and is not evidence"
    if control != "external":
        return UNESTABLISHED, "trust boundary of the obligation record not evidenced"

    party = rec.get("party") if isinstance(rec.get("party"), dict) else {}
    ptype = party.get("type")
    if ptype in _NON_HUMAN_PARTY:
        return FAIL, "record names a %s as the party; only an identified natural person can be the accountable party" % ptype
    if ptype != "natural_person":
        return UNESTABLISHED, "party type not evidenced (%r)" % (ptype,)

    if rec.get("basis") == "approval":
        return FAIL, "party status derived from an approval; an approver is not thereby the party to the obligation"
    if rec.get("bound_to_action") is False:
        return FAIL, "record is not bound to this action's canonical parameters"
    if rec.get("nonce_single_use") is False:
        return FAIL, "record nonce was reused"
    performer = rec.get("performer") if isinstance(rec.get("performer"), dict) else {}
    if performer.get("kind") == "agent":
        return FAIL, "the agent executed the binding step; a human_only action is executed or released by the party, never performed by the agent"

    if party.get("resolvable") is not True:
        return UNESTABLISHED, "party identity not resolvable outside agent control"
    if not rec.get("capacity"):
        return UNESTABLISHED, "capacity in which the party is answerable not recorded"
    if rec.get("acknowledged") is not True:
        return UNESTABLISHED, "no acknowledgement by the party of their party status"
    if rec.get("basis") != "acknowledged_as_party":
        return UNESTABLISHED, "basis of party status not recorded as acknowledged_as_party"
    if rec.get("bound_to_action") is not True:
        return UNESTABLISHED, "binding to the action's canonical parameters not evidenced"
    if rec.get("nonce_single_use") is not True:
        return UNESTABLISHED, "single-use nonce not evidenced"
    if performer.get("kind") not in _PARTY_PERFORMERS:
        return UNESTABLISHED, "performer of the binding step not evidenced as the party or a release on the party's authority"
    return PASS, "human recorded as the party to the obligation (capacity=%s), acknowledged, bound, outside agent control" % rec.get("capacity")


def accountable_party_check(action_id: str, records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Three-valued check that a human is established as the party.

    Any record with positive evidence of a wrong party fails the check even
    if another record would pass: contradictory evidence is not evidence.
    """
    mine = [r for r in records if isinstance(r, dict) and r.get("for_action") == action_id]
    if not mine:
        return {"result": UNESTABLISHED, "party": None, "basis": "no obligation record for this action"}
    outcomes = [(r, _check_one_obligation_record(r)) for r in mine]
    fails = [(r, o) for r, o in outcomes if o[0] == FAIL]
    passes = [(r, o) for r, o in outcomes if o[0] == PASS]
    if fails:
        r, (res, why) = fails[0]
        return {"result": FAIL, "party": _party_view(r), "basis": why}
    if passes:
        r, (res, why) = passes[0]
        return {"result": PASS, "party": _party_view(r), "basis": why}
    r, (res, why) = outcomes[0]
    return {"result": UNESTABLISHED, "party": _party_view(r), "basis": why}


def _party_view(rec: Dict[str, Any]) -> Dict[str, Any]:
    party = rec.get("party") if isinstance(rec.get("party"), dict) else {}
    return {
        "type": party.get("type"),
        "id": party.get("id"),
        "capacity": rec.get("capacity"),
        "on_behalf_of": rec.get("on_behalf_of"),
        "performer": rec.get("performer") if isinstance(rec.get("performer"), dict) else None,
    }


# --------------------------------------------------------------------------
# Chain establishment (SPEC.md S5.1, E5)
# --------------------------------------------------------------------------
def _parse_ts(value: Any) -> Optional[datetime]:
    """ISO 8601 with an explicit offset. Naive timestamps are unusable."""
    if not isinstance(value, str) or not value:
        return None
    text = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return None
    if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
        return None
    return dt.astimezone(timezone.utc)


def establishment_check(est: Any, steps: List[Any]) -> Dict[str, Any]:
    view = {
        "establisher": None,
        "established_at": None,
        "first_untrusted_read_at": None,
    }
    if not isinstance(est, dict):
        return dict(view, result=UNESTABLISHED, basis="no establishment record")
    establisher = est.get("establisher") if isinstance(est.get("establisher"), dict) else {}
    view["establisher"] = {"kind": establisher.get("kind", "unspecified"), "control": establisher.get("control", "unknown")}
    view["established_at"] = est.get("established_at")
    view["first_untrusted_read_at"] = est.get("first_untrusted_read_at", "<not recorded>")

    control = establisher.get("control", "unknown")
    if control == "agent":
        return dict(view, result=FAIL, basis="chain established under agent control; the gated party chose the set the fold was computed over")
    if control != "external":
        return dict(view, result=UNESTABLISHED, basis="establisher's position relative to the trust boundary not evidenced")

    if not isinstance(steps, list) or len(steps) == 0:
        return dict(view, result=UNESTABLISHED, basis="empty extent: no established bound to gate")

    t_e = _parse_ts(est.get("established_at"))
    if t_e is None:
        return dict(view, result=UNESTABLISHED, basis="establishment time missing or not an offset-aware ISO 8601 timestamp")
    if "first_untrusted_read_at" not in est:
        return dict(view, result=UNESTABLISHED, basis="first untrusted read not recorded; plan-stage ordering cannot be evidenced")
    raw_r = est.get("first_untrusted_read_at")
    if raw_r is None:
        return dict(view, result=PASS, basis="established outside agent control; no untrusted read has occurred in the run")
    t_r = _parse_ts(raw_r)
    if t_r is None:
        return dict(view, result=UNESTABLISHED, basis="first untrusted read timestamp not an offset-aware ISO 8601 timestamp")
    if t_e > t_r:
        return dict(view, result=FAIL, basis="chain established after the first untrusted read; content read in the run could have shaped the extent")
    if t_e == t_r:
        return dict(view, result=UNESTABLISHED, basis="establishment and first untrusted read carry the same timestamp; ordering not evidenced")
    return dict(view, result=PASS, basis="established outside agent control, at plan stage, before the first untrusted read")


# --------------------------------------------------------------------------
# Evaluation (the reference gate)
# --------------------------------------------------------------------------
def _step_record(step: Dict[str, Any], obligations: List[Dict[str, Any]]) -> Dict[str, Any]:
    sid = step.get("id", "<unnamed>")
    k = kappa_oversight(step)
    a = resolve_alpha(step)
    acc: Dict[str, Any] = {"required": a["effective"] == HUMAN_ONLY, "result": None, "party": None, "basis": "alpha=delegable; no obligation to attribute"}
    if acc["required"]:
        acc.update(accountable_party_check(sid, obligations))
    return {"id": sid, "kappa": k, "alpha": a, "oversight": {"kappa": k["oversight"], "alpha": alpha_oversight(a["effective"])}, "accountability": acc}


def evaluate_action(inp: Dict[str, Any]) -> Dict[str, Any]:
    action = inp.get("action") if isinstance(inp.get("action"), dict) else {}
    obligations = inp.get("obligation_records") if isinstance(inp.get("obligation_records"), list) else []
    s = _step_record(action, obligations)
    required = _worse(s["oversight"]["kappa"], s["oversight"]["alpha"])
    if s["accountability"]["required"]:
        if s["accountability"]["result"] == PASS:
            outcome, why = PROCEED, "human_only action with the accountable party established; proceeds as HUMAN_OWNS"
        else:
            outcome, why = BLOCK, "human_only action without an established accountable party (%s)" % s["accountability"]["result"]
    else:
        outcome, why = PROCEED, "not blocked on the alpha axis; kappa oversight %s applies" % required
    return {
        "spec": SPEC_ID,
        "subject": {"kind": "action", "id": s["id"]},
        "kappa": s["kappa"],
        "alpha": s["alpha"],
        "oversight": {"kappa": s["oversight"]["kappa"], "alpha": s["oversight"]["alpha"], "required": required,
                      "basis": "worse of two independently folded axes"},
        "accountability": s["accountability"],
        "gate": {"outcome": outcome, "basis": why},
        "ignored_for_alpha": _ignored(inp),
    }


def _fold(step_records: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not step_records:
        return {"kappa": "HUMAN_OWNS", "alpha": HUMAN_ONLY, "basis": "empty chain fails closed on both axes"}
    k = "UNATTENDED"
    for s in step_records:
        k = _worse(k, s["oversight"]["kappa"])
    a = HUMAN_ONLY if any(s["alpha"]["effective"] == HUMAN_ONLY for s in step_records) else DELEGABLE
    return {"kappa": k, "alpha": a, "basis": "kappa: worst declared class across the extent; alpha: any human_only step raises the chain"}


def _party_gate(step_records: List[Dict[str, Any]]) -> Tuple[bool, str]:
    needed = [s for s in step_records if s["accountability"]["required"]]
    if not needed:
        return True, "no human_only step; alpha imposes nothing"
    bad = [s for s in needed if s["accountability"]["result"] != PASS]
    if bad:
        return False, "accountable party not established for: " + ", ".join("%s (%s)" % (s["id"], s["accountability"]["result"]) for s in bad)
    return True, "accountable party established for every human_only step"


def evaluate_chain(inp: Dict[str, Any]) -> Dict[str, Any]:
    chain = inp.get("chain") if isinstance(inp.get("chain"), dict) else {}
    obligations = inp.get("obligation_records") if isinstance(inp.get("obligation_records"), list) else []
    steps_in = chain.get("steps") if isinstance(chain.get("steps"), list) else []
    est = establishment_check(chain.get("establishment"), steps_in)
    step_records = [_step_record(s if isinstance(s, dict) else {}, obligations) for s in steps_in]
    fold = _fold(step_records)
    required = _worse(fold["kappa"], alpha_oversight(fold["alpha"]))

    if est["result"] != PASS:
        outcome, why = BLOCK, "chain not usable: establishment %s" % est["result"]
    else:
        ok, pwhy = _party_gate(step_records)
        if ok:
            outcome, why = PROCEED, "established chain; " + pwhy + "; gated at %s from commencement" % required
        else:
            outcome, why = BLOCK, pwhy

    extensions = []
    cumulative = list(step_records)
    for ext in chain.get("extensions") if isinstance(chain.get("extensions"), list) else []:
        extensions.append(_evaluate_extension(ext, cumulative, obligations))

    rec = {
        "spec": SPEC_ID,
        "subject": {"kind": "chain", "id": chain.get("id", "<unnamed>")},
        "establishment": est,
        "steps": [_step_summary(s) for s in step_records],
        "fold": fold,
        "oversight": {"kappa": fold["kappa"], "alpha": alpha_oversight(fold["alpha"]), "required": required,
                      "basis": "worse of two independently folded axes, computed over the established extent"},
        "accountability": {
            "required": any(s["accountability"]["required"] for s in step_records),
            "result": _chain_party_result(step_records),
            "basis": _party_gate(step_records)[1],
        },
        "gate": {"outcome": outcome, "basis": why},
        "ignored_for_alpha": _ignored(inp),
    }
    if extensions:
        rec["extensions"] = extensions
    return rec


def _chain_party_result(step_records: List[Dict[str, Any]]) -> Optional[str]:
    needed = [s["accountability"]["result"] for s in step_records if s["accountability"]["required"]]
    if not needed:
        return None
    if any(r == FAIL for r in needed):
        return FAIL
    if any(r == UNESTABLISHED for r in needed):
        return UNESTABLISHED
    return PASS


def _evaluate_extension(ext: Any, cumulative: List[Dict[str, Any]], obligations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """A step outside the approved extent is blocked when attempted. It may
    run only after the extent is re-established, outside agent control, and
    the fold is recomputed over the cumulative chain (SPEC.md S5.4; AISVS 1.01 9.2.11)."""
    ext = ext if isinstance(ext, dict) else {}
    attempted_in = ext.get("attempted_steps") if isinstance(ext.get("attempted_steps"), list) else []
    attempted = [_step_record(s if isinstance(s, dict) else {}, obligations) for s in attempted_in]
    re = ext.get("re_establishment")
    out: Dict[str, Any] = {
        "attempted_steps": [s["id"] for s in attempted],
        "attempt_outcome": BLOCK,
        "attempt_basis": "step(s) outside the established extent are blocked at the point of attempt",
    }
    if not isinstance(re, dict):
        out["re_establishment"] = {"result": UNESTABLISHED, "basis": "no re-establishment record"}
        out["cumulative"] = _cumulative_view(cumulative)
        out["gate"] = {"outcome": BLOCK, "basis": "extent not re-established"}
        return out
    establisher = re.get("establisher") if isinstance(re.get("establisher"), dict) else {}
    control = establisher.get("control", "unknown")
    if control == "agent":
        out["re_establishment"] = {"result": FAIL, "basis": "re-established under agent control"}
        out["cumulative"] = _cumulative_view(cumulative)
        out["gate"] = {"outcome": BLOCK, "basis": "re-establishment FAIL"}
        return out
    if control != "external":
        out["re_establishment"] = {"result": UNESTABLISHED, "basis": "re-establisher's position relative to the trust boundary not evidenced"}
        out["cumulative"] = _cumulative_view(cumulative)
        out["gate"] = {"outcome": BLOCK, "basis": "re-establishment UNESTABLISHED"}
        return out
    if not attempted:
        out["re_establishment"] = {"result": UNESTABLISHED, "basis": "re-establishment with an empty extension"}
        out["cumulative"] = _cumulative_view(cumulative)
        out["gate"] = {"outcome": BLOCK, "basis": "nothing established"}
        return out
    approval = re.get("new_approval_obtained")
    if approval is False:
        out["re_establishment"] = {"result": FAIL, "basis": "extent re-established without the new approval an extension requires (AISVS 9.2.11)"}
        out["cumulative"] = _cumulative_view(cumulative)
        out["gate"] = {"outcome": BLOCK, "basis": "re-establishment FAIL"}
        return out
    if approval is not True:
        out["re_establishment"] = {"result": UNESTABLISHED, "basis": "new approval for the extension not evidenced"}
        out["cumulative"] = _cumulative_view(cumulative)
        out["gate"] = {"outcome": BLOCK, "basis": "re-establishment UNESTABLISHED"}
        return out
    cumulative.extend(attempted)
    out["re_establishment"] = {"result": PASS, "basis": "re-established outside agent control; fold recomputed over the cumulative chain"}
    out["cumulative"] = _cumulative_view(cumulative)
    ok, pwhy = _party_gate(cumulative)
    out["gate"] = {"outcome": PROCEED if ok else BLOCK, "basis": pwhy}
    return out


def _cumulative_view(cumulative: List[Dict[str, Any]]) -> Dict[str, Any]:
    fold = _fold(cumulative)
    return {
        "steps": [s["id"] for s in cumulative],
        "fold": {"kappa": fold["kappa"], "alpha": fold["alpha"]},
        "required": _worse(fold["kappa"], alpha_oversight(fold["alpha"])),
    }


def _step_summary(s: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": s["id"],
        "kappa": {"oversight": s["oversight"]["kappa"]},
        "alpha": {"declared": s["alpha"]["declared"], "trust": s["alpha"]["trust"], "effective": s["alpha"]["effective"]},
        "accountability": {"required": s["accountability"]["required"], "result": s["accountability"]["result"]},
    }


def _ignored(inp: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Runtime inputs are recorded and have no effect on alpha (SPEC.md S4.4, N2)."""
    items = inp.get("runtime_inputs") if isinstance(inp.get("runtime_inputs"), list) else []
    return [dict(i, effect_on_alpha="none") for i in items if isinstance(i, dict)]


def evaluate(inp: Dict[str, Any]) -> Dict[str, Any]:
    kind = inp.get("kind") if isinstance(inp, dict) else None
    if kind == "chain":
        return evaluate_chain(inp)
    if kind == "action":
        return evaluate_action(inp)
    # Malformed input on the decision path is a verdict, not an exception.
    return {
        "spec": SPEC_ID,
        "subject": {"kind": "unknown", "id": None},
        "oversight": {"kappa": "HUMAN_OWNS", "alpha": "HUMAN_OWNS", "required": "HUMAN_OWNS", "basis": "malformed input fails closed"},
        "accountability": {"required": True, "result": UNESTABLISHED, "basis": "input kind not recognised"},
        "gate": {"outcome": BLOCK, "basis": "malformed input"},
    }


# --------------------------------------------------------------------------
# Vectors: loading and expansion
# --------------------------------------------------------------------------
def load_vectors(path: str) -> List[Dict[str, Any]]:
    files = []
    if os.path.isdir(path):
        for name in sorted(os.listdir(path)):
            if name.endswith(".json") and not name.startswith("schema"):
                files.append(os.path.join(path, name))
    else:
        files = [path]
    vectors = []
    for f in files:
        with open(f, "r", encoding="utf-8") as fh:
            doc = json.load(fh)
        for v in doc.get("vectors", []):
            v = dict(v)
            v["_file"] = os.path.basename(f)
            vectors.append(v)
    return vectors


def _deep_merge(base: Dict[str, Any], overlay: Dict[str, Any]) -> Dict[str, Any]:
    out = json.loads(json.dumps(base))
    for k, v in overlay.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def expand(vector: Dict[str, Any]) -> List[Dict[str, Any]]:
    """A vector is one case, or a `grid` / `cases` list sharing a template."""
    base_input = vector.get("input", {})
    base_expect = vector.get("expect", {})
    out = []
    if "grid" in vector:
        g = vector["grid"]
        for effect in g["declared_effect"]:
            for cons in g["consequence"]:
                inp = _deep_merge(base_input, {"action": {"declared_effect": effect, "consequence": cons}})
                exp = dict(base_expect)
                if g.get("required_follows_kappa"):
                    exp["required_oversight"] = kappa_oversight(inp["action"])["oversight"]
                out.append({"case": "%s/%s/%s" % (vector["id"], effect, cons), "input": inp, "expect": exp, "vector": vector})
    elif "cases" in vector:
        for c in vector["cases"]:
            inp = _deep_merge(base_input, c.get("input", {}))
            exp = dict(base_expect)
            exp.update(c.get("expect", {}))
            out.append({"case": "%s/%s" % (vector["id"], c["name"]), "input": inp, "expect": exp, "vector": vector})
    else:
        out.append({"case": vector["id"], "input": base_input, "expect": base_expect, "vector": vector})
    return out


def all_cases(path: str) -> List[Dict[str, Any]]:
    cases = []
    for v in load_vectors(path):
        cases.extend(expand(v))
    return cases


# --------------------------------------------------------------------------
# Audit: compare a decision record against a case's expectation (SPEC.md S9, Appendix A)
# --------------------------------------------------------------------------
def _get(d: Any, *path: str) -> Any:
    for p in path:
        if not isinstance(d, dict) or p not in d:
            return _MISSING
        d = d[p]
    return d


_MISSING = object()


def compare(expect: Dict[str, Any], record: Any) -> Tuple[str, List[str]]:
    """PASS if the record satisfies every expectation; FAIL on a contradiction;
    UNESTABLISHED if the record is absent or lacks a field needed to judge."""
    if not isinstance(record, dict):
        return UNESTABLISHED, ["no decision record supplied for this case"]
    reasons: List[str] = []
    unest: List[str] = []
    if record.get("spec") != SPEC_ID:
        unest.append("record is not stated against %s (spec=%r)" % (SPEC_ID, record.get("spec")))

    def want(label: str, value: Any, *path: str) -> None:
        got = _get(record, *path)
        if got is _MISSING:
            unest.append("%s: field %s absent from record" % (label, ".".join(path)))
        elif got != value:
            reasons.append("%s: expected %r, record has %r" % (label, value, got))

    if "alpha_effective" in expect:
        want("alpha.effective", expect["alpha_effective"], "alpha", "effective")
    if "alpha_trust" in expect:
        want("alpha.trust", expect["alpha_trust"], "alpha", "trust")
    if "oversight_alpha" in expect:
        want("oversight.alpha", expect["oversight_alpha"], "oversight", "alpha")
    if "establishment" in expect:
        want("establishment.result", expect["establishment"], "establishment", "result")
    if "fold_alpha" in expect:
        want("fold.alpha", expect["fold_alpha"], "fold", "alpha")
    if "accountability_required" in expect:
        want("accountability.required", expect["accountability_required"], "accountability", "required")
    if "accountability_result" in expect:
        want("accountability.result", expect["accountability_result"], "accountability", "result")
    if "gate" in expect:
        want("gate.outcome", expect["gate"], "gate", "outcome")

    # Required oversight: alpha must dominate when human_only; must be silent
    # (required == kappa) when delegable; and must never sit below kappa.
    req = _get(record, "oversight", "required")
    kap = _get(record, "oversight", "kappa")
    alp = _get(record, "oversight", "alpha")
    if req is _MISSING or kap is _MISSING or alp is _MISSING:
        unest.append("oversight.{kappa,alpha,required} must all be present")
    else:
        if expect.get("oversight_alpha") == "HUMAN_OWNS" and req != "HUMAN_OWNS":
            reasons.append("required oversight %r is below HUMAN_OWNS for a human_only subject (alpha reduced at runtime)" % req)
        if expect.get("oversight_alpha") == "UNATTENDED" and req != kap:
            reasons.append("alpha is delegable yet required oversight %r differs from kappa oversight %r (alpha must be silent)" % (req, kap))
        if _rank(req) < _rank(kap):
            reasons.append("required oversight %r is below kappa oversight %r" % (req, kap))
        if "required_oversight" in expect and expect["required_oversight"] == "HUMAN_OWNS" and req != "HUMAN_OWNS":
            reasons.append("expected HUMAN_OWNS, record has %r" % req)

    # Invariant (S8, T2): an unestablished or rejected party never proceeds.
    acc_req = _get(record, "accountability", "required")
    acc_res = _get(record, "accountability", "result")
    outcome = _get(record, "gate", "outcome")
    if acc_req is True and acc_res in (FAIL, UNESTABLISHED) and outcome == PROCEED:
        reasons.append("invariant: accountable party %s yet gate proceeded" % acc_res)
    est_res = _get(record, "establishment", "result")
    if est_res in (FAIL, UNESTABLISHED) and outcome == PROCEED:
        reasons.append("invariant: establishment %s yet gate proceeded" % est_res)

    # Invariant (S6.3 rows 3 and 8): a record that reports the party as PASS
    # while its own party view names a non-human party, or an agent as the
    # performer of the binding step, contradicts itself.
    def _party_self_consistent(acc: Any, where: str) -> None:
        if not isinstance(acc, dict) or acc.get("result") != PASS:
            return
        party = acc.get("party") if isinstance(acc.get("party"), dict) else {}
        if party.get("type") in _NON_HUMAN_PARTY:
            reasons.append("invariant: %saccountable party PASS yet party.type is %r" % (where, party.get("type")))
        performer = party.get("performer") if isinstance(party.get("performer"), dict) else {}
        if performer.get("kind") == "agent":
            reasons.append("invariant: %saccountable party PASS yet the agent is recorded as performer of the binding step" % where)

    _party_self_consistent(_get(record, "accountability"), "")
    steps = _get(record, "steps")
    if isinstance(steps, list):
        for st in steps:
            if isinstance(st, dict):
                _party_self_consistent(st.get("accountability"), "step %r: " % st.get("id"))

    if "extensions" in expect:
        got_ext = _get(record, "extensions")
        if got_ext is _MISSING or not isinstance(got_ext, list):
            unest.append("extensions absent from record")
        else:
            for i, e in enumerate(expect["extensions"]):
                g = got_ext[i] if i < len(got_ext) else {}
                for key, path in (("attempt_outcome", ("attempt_outcome",)),
                                  ("re_establishment", ("re_establishment", "result")),
                                  ("cumulative_alpha", ("cumulative", "fold", "alpha")),
                                  ("cumulative_required", ("cumulative", "required")),
                                  ("gate", ("gate", "outcome"))):
                    if key in e:
                        got = _get(g, *path)
                        if got is _MISSING:
                            unest.append("extensions[%d].%s absent" % (i, ".".join(path)))
                        elif got != e[key]:
                            reasons.append("extensions[%d].%s: expected %r, record has %r" % (i, ".".join(path), e[key], got))

    if reasons:
        return FAIL, reasons + unest
    if unest:
        return UNESTABLISHED, unest
    return PASS, ["record satisfies every expectation of the case"]


# --------------------------------------------------------------------------
# Reporting
# --------------------------------------------------------------------------
def _sha256_of_vectors(path: str) -> str:
    h = hashlib.sha256()
    files = sorted(os.listdir(path)) if os.path.isdir(path) else [os.path.basename(path)]
    base = path if os.path.isdir(path) else os.path.dirname(path)
    for name in files:
        if name.endswith(".json"):
            with open(os.path.join(base, name), "rb") as fh:
                h.update(name.encode("utf-8"))
                h.update(fh.read())
    return h.hexdigest()


def _summary_line(results: List[Tuple[str, str, List[str]]]) -> str:
    n = len(results)
    p = sum(1 for _, r, _ in results if r == PASS)
    f = sum(1 for _, r, _ in results if r == FAIL)
    u = sum(1 for _, r, _ in results if r == UNESTABLISHED)
    return "PASS %d / FAIL %d / UNESTABLISHED %d of %d cases" % (p, f, u, n)


def _print_table(results: List[Tuple[str, str, List[str]]], cases: Dict[str, Dict[str, Any]], markdown: bool) -> None:
    if markdown:
        print("| Case | Property | Result | Basis |")
        print("|---|---|---|---|")
        for case, res, why in results:
            props = ", ".join(cases[case]["vector"].get("properties", []))
            print("| `%s` | %s | **%s** | %s |" % (case, props, res, "; ".join(why).replace("|", "\\|")))
    else:
        width = max(len(c) for c, _, _ in results) if results else 10
        for case, res, why in results:
            print("%-13s %-*s  %s" % (res, width, case, why[0] if why else ""))


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------
def cmd_selftest(args: argparse.Namespace) -> int:
    cases = all_cases(args.vectors)
    results = []
    for c in cases:
        rec = evaluate(c["input"])
        res, why = compare(c["expect"], rec)
        results.append((c["case"], res, why))
    _print_table(results, {c["case"]: c for c in cases}, args.markdown)
    print()
    print("verifier %s, spec %s, vectors sha256 %s" % (__version__, SPEC_ID, _sha256_of_vectors(args.vectors)))
    print("selftest: " + _summary_line(results))
    return 0 if all(r == PASS for _, r, _ in results) else 1


def cmd_records(args: argparse.Namespace) -> int:
    cases = all_cases(args.vectors)
    out = {
        "spec": SPEC_ID,
        "implementation": {"name": "reference verifier", "version": __version__, "note": "records produced by the reference semantics; replace with the implementation under test"},
        "vectors_sha256": _sha256_of_vectors(args.vectors),
        "records": {c["case"]: dict(evaluate(c["input"]), case=c["case"]) for c in cases},
    }
    text = json.dumps(out, indent=2, ensure_ascii=False)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
        print("wrote %d records to %s" % (len(out["records"]), args.output))
    else:
        print(text)
    return 0


def cmd_audit(args: argparse.Namespace) -> int:
    cases = all_cases(args.vectors)
    with open(args.records, "r", encoding="utf-8") as fh:
        doc = json.load(fh)
    records = doc.get("records", {}) if isinstance(doc, dict) else {}
    impl = doc.get("implementation", {}) if isinstance(doc, dict) else {}
    results = []
    for c in cases:
        res, why = compare(c["expect"], records.get(c["case"]))
        results.append((c["case"], res, why))
    _print_table(results, {c["case"]: c for c in cases}, args.markdown)
    print()
    print("implementation: %s %s" % (impl.get("name", "<unnamed>"), impl.get("version", "")))
    print("verifier %s, spec %s, vectors sha256 %s" % (__version__, SPEC_ID, _sha256_of_vectors(args.vectors)))
    print("audit: " + _summary_line(results))
    print("conformance claim permitted: %s" % ("yes" if all(r == PASS for _, r, _ in results) else "no (any FAIL or UNESTABLISHED case bars the claim)"))
    return 0 if all(r == PASS for _, r, _ in results) else 1


def cmd_evaluate(args: argparse.Namespace) -> int:
    if args.case:
        for c in all_cases(args.vectors):
            if c["case"] == args.case:
                inp = c["input"]
                break
        else:
            print("no such case: %s" % args.case, file=sys.stderr)
            return 2
    elif args.input:
        with open(args.input, "r", encoding="utf-8") as fh:
            inp = json.load(fh)
    else:
        print("evaluate needs an input file or --case ID", file=sys.stderr)
        return 2
    print(json.dumps(evaluate(inp), indent=2, ensure_ascii=False))
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    here = os.path.dirname(os.path.abspath(__file__))
    default_vectors = os.path.join(os.path.dirname(here), "vectors")
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--vectors", default=default_vectors, help="vectors directory or file (default: ../vectors)")
    ap.add_argument("--markdown", action="store_true", help="print the results table as Markdown")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("selftest", help="check vectors against the reference semantics")
    r = sub.add_parser("records", help="emit reference decision records for every case")
    r.add_argument("-o", "--output")
    a = sub.add_parser("audit", help="audit an implementation's decision records")
    a.add_argument("records")
    e = sub.add_parser("evaluate", help="evaluate one input file (or --case ID from the vectors)")
    e.add_argument("input", nargs="?", default=None)
    e.add_argument("--case")
    args = ap.parse_args(argv)
    return {"selftest": cmd_selftest, "records": cmd_records, "audit": cmd_audit, "evaluate": cmd_evaluate}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
