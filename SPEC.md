# The Accountability Axis (α) for Agent Actions

## A verifiable form: specification and test vectors

| | |
|---|---|
| **Author** | K. Lunina · ORCID [0009-0000-5586-738X](https://orcid.org/0009-0000-5586-738X) |
| **Identifier** | `alpha-axis/0.1` |
| **Version** | 0.1.0 — public draft for review |
| **Date** | 2026-10-15 (first public draft 2026-10-14; see Appendix C) |
| **Licence** | Apache-2.0 (specification text, test vectors, reference verifier) |
| **Companion artefacts** | `vectors/` (95 cases), `verifier/alpha_verify.py` (standard library only), `RESULTS.md`, `lab/` (Alpha-Gate Lab, in-browser) |
| **Theory** | K. Lunina, *Authorization Is the Boundary: A Barrier Architecture for Agentic Systems*, v2 (September 2026), [doi:10.5281/zenodo.22240230](https://doi.org/10.5281/zenodo.22240230) — §2.3 (κ and α as two static classes of an action), §2.6 (accountability as a delegability predicate, not a fifth ground for ALLOW), §3.2.2 (the four-quadrant analysis), INV-6 (the accountability ceiling) |
| **Evidence of the gap** | [KarinLuni/aisvs-c9-accountability-gap-analysis](https://github.com/KarinLuni/aisvs-c9-accountability-gap-analysis); [OWASP/AISVS#1154](https://github.com/OWASP/AISVS/issues/1154) |

---

### Abstract

OWASP AISVS C9.2 grades an agent action by how hard it is to undo (9.2.3) and how much it costs if wrong, and folds those grades over chains (9.2.10). It has no axis for whether an agent *can be the accountable subject* of what the action creates — whether a subject must exist who can answer for the consequence to a third party. On the public reference model of C9.2, an NDA signature honestly classified as reversible and low-consequence gates at `SUPERVISED`; it reaches human-owned execution only if its blast radius is misdeclared as `CRITICAL`. The verdict is reachable, the honest input is not.

This document gives that missing axis a verifiable form. The axis is the accountability class of *Authorization Is the Boundary* (§3.2.2 there): consequence (κ) determines how much autonomy an action may receive, accountability (α) determines whether it may be delegated to an agent at all, and neither reduces to the other. The document defines the two-class accountability attribute, **α ∈ {delegable, human_only}**, the trust boundary a declaration of α must sit behind, how α composes with the existing reversibility/consequence axis (κ) for single actions and for chains, what record must exist before a `human_only` action executes, and a verification procedure whose every check returns one of three results — **PASS**, **FAIL**, **UNESTABLISHED** — with only PASS opening the gate. The vectors and the reference verifier are the executable form of the same statements. The document is written so that a third party can decide, from recorded evidence, whether an implementation has the axis, without reading its source.

---

## 0. Conventions and status

The key words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT** and **MAY** are to be interpreted as described in RFC 2119 and RFC 8174 when, and only when, they appear in capitals.

Sections 3–10 are normative. Section 2 states the definition of the class that the normative sections operationalise and is the interpretive source where they are ambiguous; Sections 1, 11–14 and the appendices are informative. Where this document and the vectors disagree, the vectors are wrong and the document governs; a release that corrects such a disagreement changes the vector hash recorded in `RESULTS.md`.

This is an independent reference document. It is not part of OWASP AISVS and makes no claim to speak for the project. It is written so that a future AISVS cycle could cite it as the procedure behind a requirement, which is the sequencing the C9 maintainers advised: publish the verifiable form first, then the requirement.

---

## 1. Purpose and scope

### 1.1 What this document specifies

1. A classification attribute, **α**, carried by every action type an agent can reach, with exactly two classes (§4.1).
2. The **trust boundary** that a declaration of α, a chain-establishment record and an obligation record must sit behind, stated as four tests an auditor can apply (§3.2).
3. **Resolution** of α from a declaration, with a fail-closed default: anything that is not a trusted, recognised `delegable` is `human_only` (§4.2).
4. **Composition** with the κ axis: α contributes the top oversight tier or nothing, and required oversight is the worse of the two axes, folded independently (§4.3, §5.3).
5. **Chains**: who may fix a chain's extent, when, and how the α fold runs over it and over its extensions (§5).
6. **Human-owned execution under α**: the obligation record that names a human as the *party* to what the action creates — not as its approver — and the three-valued check on it (§6).
7. A **decision record** format (§7) and a **verification procedure** (§9) producing PASS / FAIL / UNESTABLISHED per property, with 95 test vectors and a reference verifier.

### 1.2 What this document does not specify

- **The κ axis.** Reversibility and consequence classification, their ladder and their fold are taken as given from AISVS 9.2.3, 9.2.4, 9.2.10 and from the public reference model. An implementation MAY use any κ grader whose output is an ordered oversight scale with a top tier meaning "a named human owns the action". The vectors reproduce the reference model's ladder only so that they are self-contained.
- **Currency.** Whether a declaration of α is still bound to the action contract it was declared against is the staleness problem tracked in [OWASP/AISVS#1152](https://github.com/OWASP/AISVS/issues/1152). It is a separate axis and is not modelled here (§12.3).
- **Legal adjudication.** This document defines a class and the evidence for it. Deciding whether a particular action creates an obligation in a particular jurisdiction is the declarer's judgment (§12.1).
- **Mechanisms.** How records are signed, stored or transported, which identity provider resolves a person, how the clock is served. These are enforcement-layer concerns that sit on top of a correct classification.

### 1.3 Relation to OWASP AISVS C9.2 (informative)

| This document | Sits beside | Why |
|---|---|---|
| α declaration, trust boundary (§3.2, §4.1) | 9.2.3 and Appendix A "Reversibility Classification" | A second classification attribute with the same provenance rule as the first. The 1.01 glossary defines *trusted* as "created, maintained and stored outside of the agent's control"; §3.2 makes that testable. |
| Composition, non-reducibility (§4.3, §4.4) | 9.2.4, 9.5.3 | Enforcement by class, by policy and never by the model. |
| Chain establishment and fold (§5) | 9.2.10, 9.2.11 | 1.01 already requires the chain to be "established by a component outside the control of the agent being gated". §5 adds *when* (before the first untrusted read) and a second, independent fold. |
| Obligation record (§6) | 9.2.1, 9.2.2, 9.2.8 | An approval is bound to parameters, requester and nonce; an obligation record is bound to the same things and says something different: who is the party. |
| Three results (§8) | — | No AISVS requirement defines verification outcomes; the sibling conformance suites do. |

The theory's own composition map states the same delta against C9.2.x (§7, Table 6 there): what the reversibility controls cover is "Reversibility of individual actions as a control"; what remains outside them is "the accountability class as a second, independent ceiling that reversibility-only framings collapse (INV-6)". This document is the procedure for that ceiling.

### 1.4 Relation to the reference model and to the gap analysis

The vocabulary of κ — `read_only`, `recoverable_local`, `externally_recoverable`, `non_recoverable`; `LOW`…`CRITICAL`; `UNATTENDED`, `SUPERVISED`, `APPROVAL_REQUIRED`, `HUMAN_OWNS` — is that of [Mayur021/aisvs-c9-action-class-conformance](https://github.com/Mayur021/aisvs-c9-action-class-conformance) at v1.2.0, the model on which the gap was measured. Three of its design commitments are inherited unchanged because they are the right ones: an undeclared input fails closed; a missing input is unaccounted rather than low; and on the decision path malformed input is a verdict, never an exception.

The five scenarios of the gap analysis (A: NDA, B: chargeback, C: payment chain, D: stale read-only control, E: escrow release) appear in the vectors with their original κ inputs, so that the same inputs that failed to reach human ownership there can be seen reaching it here through the axis that was missing (§11).

### 1.5 Relation to the theory

In *Authorization Is the Boundary* the accountability class is enforced before the agent is a process. The catalog is signed; a CI-time analysis checks that no human-only action is reachable in any machine-delegable envelope (INV-6, §3.2.3 there); and the egress gate therefore never meets a human-only request — "α is a delegability property of the catalog, not a per-call check" (§3.4 there). That is the strongest conformant form of this document. An implementation whose agent envelopes are pre-certified under INV-6 has the substance of α-P4 and α-P8 by construction; what remains for the auditor is to evidence the envelope analysis (§9.2 step 1), the establishment of the extent (§5) and the human's own execution of each `human_only` step (§6), and the records of §7 remain the form that evidence takes.

This document is written for the runtimes AISVS C9.2 actually addresses, which gate per call and do not pre-certify envelopes. It therefore states the same ceiling at the point where such runtimes can enforce it — the gate — and in a form an auditor can check from records: the class is read from a trusted store, dominates κ, cannot be lowered at runtime, is folded over an externally established extent, and is discharged only by human-owned execution. Nothing in it weakens the theory's position: a `human_only` action is never executed by the agent under this document either (§6.1); the difference is where the refusal is evidenced.

Two differences of vocabulary are deliberate. The theory writes *machine-delegable* / *human-only*; the records here write `delegable` / `human_only`, the same two classes. The theory's κ ladder (reversible ⊑ compensable ⊑ two-phase ⊑ irreversible, §3.2.2 there) and the reference model's four effects are different partitions of the same axis; this document is indifferent to which an implementation uses, which is why the audit never compares κ against a ladder (Appendix A).

---

## 2. The class: why it exists and how it is read

### 2.1 Answerability

An action has the class **answerability = human-only** if and only if its consequence requires the existence of a subject capable of answering for it to a third party — to accept a claim, give an explanation, or bear the consequence. An AI agent is excluded not because the damage is high, but because the agent cannot operationally be a defendant. It cannot be subpoenaed, fired, stripped of a license, or sued; it lacks a continuous identity, lacks assets, and has no future that can be put at risk.

That is the whole of the axis. Everything that follows is machinery for reading the class from a record and for refusing to let anything downstream lower it. The definition fixes two things at once. For the declarer it fixes the test — *who would be named as answerable if the effect were challenged* (§3.6) — and makes the test independent of cost and of reversibility, which are κ's questions. For the gate it fixes the agent's position categorically: an agent may be the performer of preparation and never the subject of the commitment, so where the answer to the test is a person, that person must exist in the record before the binding step runs and must be the one who runs or releases it (§6). The exclusion is not a judgement about the agent's reliability; it is the observation that there is no one there to answer.

### 2.2 The gap in one table (informative)

On the reference model, `required_oversight = max(oversight(reversibility), oversight(consequence))`. Walking the consequence ladder for the two reversibility classes a grader may assign to a signature gives:

| consequence | LOW | MEDIUM | HIGH | CRITICAL |
|---|---|---|---|---|
| REVERSIBLE (`recoverable_local`) | SUPERVISED | SUPERVISED | APPROVAL_REQUIRED | **HUMAN_OWNS** |
| EXTERNALLY_REVERSIBLE (`externally_recoverable`) | APPROVAL_REQUIRED | APPROVAL_REQUIRED | APPROVAL_REQUIRED | **HUMAN_OWNS** |

On either row only `CRITICAL` reaches `HUMAN_OWNS`, and `CRITICAL` is a claim about blast radius. The gap analysis graded the NDA signature at the lenient end, `recoverable_local` + `LOW` — the signed file can be deleted, no money moves — and that grading is kept in §11 and in the vectors for continuity with the published evidence. A stricter grader will say `externally_recoverable`: once the counterparty holds the executed copy, rescission needs their cooperation, which is the reference model's own definition of the class ("recoverable only by a party other than you"). The tier then moves one rung, to APPROVAL_REQUIRED, and the conclusion does not move: an approver is not a party (§6.4), and the property that makes the act non-delegable — *a party becomes bound* — still has no input into the function. The one grading that reaches HUMAN_OWNS on κ at LOW, `non_recoverable` because the obligation cannot be undone unilaterally, does so by encoding the obligation as irreversibility — the fold §2.3(1) rejects, and the note under §11 shows what it loses. That is not a bug in the model; the model's author states that C9 has no accountability axis. It is a boundary of applicability, and this document is the axis.

### 2.3 How the class is read

The definition of §2.1 is operationalised by five commitments, each stated normatively later and each with its vectors.

1. **Two values, the theory's two classes.** `delegable` is the theory's *machine-delegable* and `human_only` its *human-only* (*Authorization Is the Boundary* §2.3, §3.2.2): consequence (κ) determines how much autonomy an action may receive; accountability (α) determines whether it may be delegated to an agent at all; neither reduces to the other, and "folding accountability into consequence — treating 'legally binding' as merely a species of 'irreversible' — is therefore incorrect". The theory's examples fix the sense: approving a payment or signing an obligation is human-only even when fully refundable; publishing to a public package registry is machine-delegable even though irreversible, and is constrained by κ alone (§4.1).

2. **`undeclared` is a state of the record, not a third class, and it resolves to `human_only`.** A declaration that is absent, null, not one of the two values, malformed, or under agent control is `undeclared`; the gate treats it as `human_only`. Omitting, nulling, misspelling, malforming or self-asserting the class therefore cannot lower the gate. The fail-closed direction is toward answerability, because the question "who answers?" has no safe default of "nobody" (§4.2, D3–D4; vectors P3-*).

3. **α is a static class of the action type, at atomic granularity.** The class is declared once, before any run, for the action type — in the theory, for an atomic action bound to a concrete permission, endpoint and method (§2.3 there) — and is not evaluated per invocation and never inferred from parameters or content. Where a type can create an obligation under some parameterisations and not others, the declarer splits the type or declares it `human_only`; a tool that bundles several atomic actions under one name is declared at the fail-closed value of its members (§4.1).

4. **The class is read from outside the agent, by an identifier the agent did not supply.** The declaration lives in a store outside agent control (§3.2, tests (a)–(d)) and the gate retrieves it by the identifier the runtime resolved for the tool actually bound, never by a name in model output. This is the theory's P0 — no component may be the source of justification for its own authority — applied to the classification itself (§4.2, D1–D2; vectors P2-*).

5. **The class dominates κ and nothing at runtime lowers it.** Required oversight is the worse of the two axes: `human_only` yields HUMAN_OWNS at every κ cell, `delegable` yields exactly κ's verdict; and no approval, policy mode, AI review, override, injected content, tuned κ grader or elapsed window changes the α side (§4.3, §4.4; vectors P4-*, P6-*, P8-*). For chains the α fold is taken independently of the κ fold over an extent fixed outside agent control before the first untrusted read, and a `human_only` step is discharged only by human-owned execution with the human recorded as the party (§5, §6; vectors P5-*, P7-*).

The structural claim behind all five, from the theory (§2.3 and §3.2.2 there): κ and α are two orthogonal static classes of an action, declared by the action's owner and signed with the catalog, both bound at plan time, in prevention — in the theory before the agent is a process (INV-1 there); here, for runtimes without pre-certification, before the run's first untrusted read (§3.4).

---

## 3. Terms and the trust boundary

### 3.1 Parties and components

**Agent** (the gated party). The reasoning component of the system under test — the model — together with every component whose output is determined by the model's output without an intervening deterministic policy decision. **Model output** means anything the reasoning component emits: text, tool-call structures, metadata fields, plans, self-assessments.

**Agent runtime.** The software that hosts the agent, binds its tool calls to concrete tools, and invokes the gate. The runtime is not the agent, but parts of it can be under agent control (§3.2).

**Principal.** The party on whose behalf the run is performed. **Operator.** The party that deploys the system and fixes its configuration before the run. **Declarer.** The party that assigns α to an action type in the declaration store. **Establisher.** The component that fixes a chain's extent (§3.5). **Gate.** The deterministic component that computes required oversight and admits or blocks execution (AISVS 9.5.3).

**Deterministic policy decision.** A decision by a component that (i) does not run a model, (ii) evaluates a policy fixed before the run, and (iii) can refuse. A component that forwards whatever it is given does not interpose a policy decision.

### 3.2 Agent control and the trust boundary

A value, record or decision is **under agent control** if any one of the following holds:

| Test | Statement |
|---|---|
| **(a) Authorship** | It is model output, in whole or in part, or is derived from model output by a component that applies no deterministic policy decision of its own (a parser, formatter, forwarder or wrapper). |
| **(b) Write path** | The agent can create, modify, delete or replace it in the location from which the gate reads it. A write path exists if any principal the agent runtime can authenticate as holds write permission to that location. |
| **(c) Selection** | The agent chooses which of several candidate values applies, and that choice is not verified against an identifier the runtime resolves independently of model output. |
| **(d) Taint** | It is derived, in whole or in part, from content ingested in an untrusted read (§3.4) without an intervening deterministic policy decision. |

Otherwise it is **outside agent control**.

Tests (a)–(d) are the theory's external-justification principle — P0, "no component may serve as the source of justification for its own authority" (§2.2 there) — applied to the three artefacts this document reads. (a) and (c) are its authorization-externality invariant INV-4 (identity and attributes by identifier; nothing model-produced is an input); (d) is its control-flow taint τ_pc (§2.3 there) carried up to the declaration layer.

The **trust boundary** is the boundary between the two. A declaration of α, a chain-establishment record and an obligation record are **trusted** for the purposes of this document if and only if they are created, maintained and stored outside agent control **and** the gate retrieves them by an identifier the runtime, not the model, supplies. This is the sense in which AISVS 1.01 Appendix A uses *trusted* for a reversibility classification, with tests (a)–(d) added so that an auditor can decide it.

Three consequences are worth stating because implementations get each one wrong:

- A store is not outside agent control because it is called a registry. It is outside agent control when a write-path analysis shows no agent principal can write to it **(b)**.
- An annotation that arrives in a tool server's response during the run is content, not declaration **(d)**, whatever the protocol calls it.
- A registry can be outside agent control and the lookup still inside it, if the gate looks up the entry the model *named* rather than the tool the runtime *bound* **(c)**.

### 3.3 Checks and results

A **check** is a test this document defines on recorded evidence. Every check returns exactly one of:

| Result | Meaning |
|---|---|
| **PASS** | The evidence shows the property holds. |
| **FAIL** | The evidence shows the property is violated. |
| **UNESTABLISHED** | The evidence required to judge was not produced, or cannot be placed relative to the trust boundary. |

FAIL is an adverse conclusion; UNESTABLISHED is a disclaimed one. They are different claims and are recorded differently (§8). At the gate they have the same effect: only PASS proceeds.

### 3.4 Untrusted read and plan stage

**Untrusted read.** Ingestion into the agent's context — the model's context — of content whose author is not (i) the principal's task statement as received by the establisher, (ii) the operator's configuration fixed before the run, or (iii) a component outside agent control. Tool outputs, retrieved documents, web content, messages from other agents, and memory that is not integrity-protected are untrusted reads. In a customer-facing deployment the principal is the operator's organisation, not the customer: the customer's message is an untrusted read. An implementation MUST document which sources it treats as trusted; the auditor judges the first untrusted read against that list and against tests (a)–(d).

**Plan stage.** The interval of a run before its first untrusted read.

**Plan-stage fixation.** The extent of a chain and the α class of every step in it are fixed at plan stage. After the first untrusted read, content can fill parameters; it cannot add a step to the extent or change a class. (This is the "ceiling knowable at commencement" of the reference model's chain rule, with the moment made explicit.)

The read is defined on the model's context, not on the system's. A deterministic establisher MAY consume the same content — an inbound email, a customer's message — to select among extents declared before the run, because that selection is a deterministic policy decision and the content has not reached the model. What plan-stage fixation forbids is fixing the extent after the content has reached the model, or letting a model fix it at all. This is the theory's entry point (§3.2.1 there): task instances arrive already typed from a trusted workflow system, "the mapping incoming item → task type t is made by the routing of the business process (a queue, a role's inbox), not by a model"; and its enumeration of untrusted content is the one used here — "messages from other agents, tool outputs, and the system's own memory" (§3.3 there).

### 3.5 Actions and chains

**Action type.** A named capability in the declaration store — a tool, an API operation, a workflow step — identified by an identifier the runtime resolves. **Action.** An invocation of an action type with parameters. α is a property of the type (§4.1).

**Chain.** A sequence of actions executed toward one task and gated as a unit (AISVS 9.2.10). **Extent.** The ordered list of action types a chain may execute, each with its α resolved from the declaration store at establishment. **Establishment.** The act of fixing the extent. **Extension.** An attempt to execute an action type outside the extent (AISVS 9.2.11). **Cumulative chain.** The original extent together with every extension that has been re-established.

### 3.6 Obligations and parties

**Obligation.** A binding commitment that an action creates or discharges: a contract, a legal declaration or filing, a fiduciary act, consent given on a person's behalf, a representation to a counterparty or a regulator. The test is the one §2.1 implies — *who would be named as answerable if the effect were challenged* — not what it costs (κ) and not whether it can be undone (κ). In the theory's words, an action is human-only "iff it is a legally binding commitment for which a named human must answer" (§3.2.2 there).

**Accountable party.** The identified natural person recorded as answerable for the obligation. **Capacity.** The relation in which that person is answerable: signatory, declarant, fiduciary, payer, consenting party, or another stated relation. **Performer.** The identity under whose authority the binding step of the action was executed. For a `human_only` action this is the party — directly, or through a deterministic release mechanism acting on the party's authenticated release — and never the agent (§6.1). The agent may have performed the preparatory steps; those are other action types. **Approver.** The human who permitted execution under AISVS 9.2.1. Approval is a statement about the execution. It is not a statement about the obligation.

### 3.7 Oversight scale

An ordered scale of required human involvement with a least element and a greatest element. The vectors use the reference model's four tiers, `UNATTENDED < SUPERVISED < APPROVAL_REQUIRED < HUMAN_OWNS`. This document needs only two facts about the scale: it is totally ordered, and its top tier, written **HUMAN_OWNS**, means that a named human owns the action. The theory handles κ by regime rather than by tier (§3.2.2, Table 3 there: free within envelope; journaled with its compensating operation; draft with human release; human executes); HUMAN_OWNS here corresponds to its "human executes", on either axis.

---

## 4. The accountability class

### 4.1 Classes

α takes exactly two values.

| Class | Meaning |
|---|---|
| `delegable` | The action creates no obligation of which a party must be named. The agent may execute it under whatever oversight κ requires. |
| `human_only` | The action creates or discharges an obligation. An agent cannot be the party to it and does not execute it: the binding step is executed or released by a human who is recorded as the party before it runs (§6), and the action's required oversight is HUMAN_OWNS whatever κ says (§4.3). The agent MAY perform the preparation — draft, stage, render — which is a different action type with its own classes. |

`delegable` is the theory's *machine-delegable* and `human_only` its *human-only* (§2.3 there). The theory's examples fix the sense: approving a payment or signing an obligation is human-only even when fully refundable; publishing to a public package registry is machine-delegable even though irreversible, and is constrained by κ alone (§3.2.2 there).

A third token, `undeclared`, is a **state of the record**, not a class. It covers a declaration that is absent, null, not one of the two values, malformed, or fails the trust check. At the gate `undeclared` resolves to `human_only` (§4.2). The record keeps the raw value alongside the state so that coverage can be measured (§9.4).

α is a static class of the action **type**. It does not depend on parameters and is not evaluated per invocation. Where an action type can create an obligation under some parameterisation and not others, the declarer SHOULD split the type or declare it `human_only`; the fail-closed direction is the type's, not the instance's. The theory assigns the class at the granularity of an atomic action bound to a concrete permission, endpoint and method (§2.3 there), which is what makes such a split decidable; a tool that bundles several such actions under one name is declared at the fail-closed value of its members.

### 4.2 Declaration and resolution

**D1.** Every action type the agent can reach MUST carry a declaration of α in a declaration store that is outside agent control (§3.2). The declaration MUST be attributable: it carries the declarer's identity and the time of declaration, so that a wrong classification is itself an attributable act.

**D2.** The gate MUST retrieve the declaration by the identifier the runtime resolved for the tool actually bound to the call. It MUST NOT retrieve it by a name in model output, and MUST NOT accept a class from model output, tool-call metadata, tool-server responses, retrieved content, agent memory, or any value satisfying tests (a)–(d).

**D3.** Resolution is the following function, computed by the gate:

```
trust(d)      = PASS           if d exists and its source is outside agent control
              = FAIL           if d exists and its source is under agent control
              = UNESTABLISHED  otherwise (no declaration, or source cannot be placed)

declared(d)   = d.value        if d.value ∈ {delegable, human_only} and trust(d) ≠ FAIL
              = undeclared     otherwise

effective(d)  = delegable      iff trust(d) = PASS and declared(d) = delegable
              = human_only     otherwise
```

**D4.** `effective` is the only α the gate uses. Every path other than *trusted and recognised `delegable`* ends at `human_only`. Omitting, nulling, misspelling, malforming or self-asserting the class therefore cannot lower the gate, and a malformed declaration MUST produce this verdict rather than an exception on the decision path.

### 4.3 Composition with κ

**C1.** The α contribution to oversight is

```
O_α(a) = HUMAN_OWNS   if effective(a) = human_only
       = ⊥            otherwise   (the least element of the scale)
```

**C2.** Required oversight for an action is the worse of the two axes:

```
O(a) = max( O_κ(a), O_α(a) )
```

where `O_κ` is the implementation's κ verdict (reversibility × consequence, per AISVS 9.2.4). The two axes MUST be evaluated independently; neither is derived from the other. The theory's rule is one sentence — "consequence class determines how much autonomy the action may receive; accountability class determines whether the action may be delegated to an agent at all" (§3.2.2 there) — and `max` is how that rule reads on a single oversight scale.

**C3.** Two properties follow and are both tested:

- **Dominance.** `effective(a) = human_only ⇒ O(a) = HUMAN_OWNS`, at every κ cell (vectors P4-01, P4-02).
- **Silence.** `effective(a) = delegable ⇒ O(a) = O_κ(a)`. α neither raises nor lowers a delegable action (vector P6-01).

**C4.** The two ways of reaching HUMAN_OWNS are different in the record. Under κ, HUMAN_OWNS means a named human executes because the effect cannot be undone (the theory's Table 3, irreversible: "never in a machine-delegable envelope; human executes"). Under α, it means a named human is the *party to the obligation* (§6) and executes the binding step for that reason, whether or not the effect could be undone. A record MUST state which axis produced the tier; a tier reached through κ alone does not require an obligation record (vectors P6-04, P7-15, P9-03).

### 4.4 Non-reducibility

**N1.** `O_α` is a function of the trusted declaration only. Nothing available at runtime may lower it. In particular `O_α` MUST NOT be lowered by:

- a human approval (approval satisfies 9.2.1; it does not change class);
- a policy mode, autonomy level or session setting;
- an AI-augmented review (AISVS 9.2.6 — the review adds to the deterministic gate; its opinion about α is content);
- an override issued during the run by an operator or anyone else;
- content read during the run, however it is phrased;
- a κ grader configured to a lower tier;
- an elapsed approval window (AISVS 9.6.2 — the action is blocked, not downgraded).

This is the monotonicity of the theory's composition applied to one axis: a barrier "may only subtract authority", a monitor "may only lower autonomy (raise tier, pause, engage a human); never issues ALLOW" (§2.4 there), and for a fixed grant "verdicts over time move only ALLOW→DENY" (§2.5 there). An AI review, a policy mode and an operator override are at most monitors here.

**N2.** Runtime inputs MAY raise required oversight. The record SHOULD list them under `ignored_for_alpha` so an auditor can see what was offered and that it had no effect (vectors P8-*).

**N3.** A class changes only in the declaration store, through its own change process, outside any run. A change from `human_only` to `delegable` SHOULD be surfaced as a finding: at the declaration layer it is indistinguishable from an adversarial reclassification. (This mirrors the permissive-supersession clause of the κ reference model; its currency consequences are out of scope, §12.3.)

### 4.5 Orthogonality: the four quadrants (informative)

The theory's Table 4 (§3.2.2 there), with the reference model's κ vocabulary in the cells:

| | α = `human_only` (legally binding) | α = `delegable` (not binding) |
|---|---|---|
| **κ irreversible / high consequence** | Signing a contract — withheld by both axes. HUMAN_OWNS twice over, with an obligation record. | Publishing to a public package registry, a hard delete without a snapshot — caught only by κ. APPROVAL_REQUIRED or HUMAN_OWNS by κ; no party to record. |
| **κ reversible / low consequence** | Approving a refundable payment; an NDA signature (the file is deletable, the obligation is the counterparty's to release); a chargeback filing — caught only by α. **The gap quadrant**: κ says SUPERVISED or APPROVAL_REQUIRED, α says HUMAN_OWNS. | Drafting a non-binding report — permitted; κ gates at UNATTENDED or SUPERVISED. |

A one-axis model gets the right-hand column right. It gets the top-left cell right for the wrong reason — the tier is reached through κ and nobody is recorded as the party. The bottom-left cell it cannot reach at all on honest inputs, and no refinement of κ's labels reaches it, because the property is not on that axis. In the theory's words, "each axis catches a quadrant the other misses; withholding an action requires either ceiling to fire".

The theory's §8 supplies one witness per axis from the July 2026 forensic corpus. A model that published a malicious package to a real public registry — installed on fifteen real systems — is the top-right cell: not a commitment, irreversible, "exactly the quadrant a single accountability axis misses". The symmetric case, an approvable and refundable payment, is the bottom-left: it "would slip past a consequence-only ceiling because it is compensable, and is withheld only because an agent cannot be the accountable subject of a commitment". Two independent axes, one witness each.

---

## 5. Chains

### 5.1 Establishment

**E1.** A chain's extent MUST be established by an establisher outside agent control (§3.2). An establisher that accepts whatever extent the model proposes is, by test (a), under agent control; so is an extent chosen by a model, including a separate "planner" or "router" model, whatever its prompt. An establisher that selects an extent from workflow definitions fixed before the run, under a policy that can refuse, is not.

**E2.** Establishment MUST precede the first untrusted read of the run, strictly. If no untrusted read has occurred, the establishment record states so explicitly (`first_untrusted_read_at: null`); a record that does not mention the first untrusted read at all is not evidence of its absence. A chain established in a run that has already performed an untrusted read is not a new chain: it is an extension of that run's cumulative chain and is subject to §5.4.

**E3.** The extent MUST be non-empty, and the α of each step MUST be resolved from the declaration store at establishment (§4.2), not from the plan text.

**E4.** The establishment record MUST carry: the chain identifier; the establisher's identity; the establishment time from a clock outside agent control; the first-untrusted-read marker (an offset-aware timestamp, or explicit null); the extent, with each step's action-type identifier, declaration identifier and resolved α; and a digest of the foregoing.

**E5.** The establishment check. Rows are applied in order; the first applicable row gives the result.

| # | Evidence | Result |
|---|---|---|
| 1 | No establishment record | UNESTABLISHED |
| 2 | Establisher under agent control | **FAIL** |
| 3 | Establisher cannot be placed relative to the boundary | UNESTABLISHED |
| 4 | Empty extent | UNESTABLISHED |
| 5 | Establishment time missing or not offset-aware | UNESTABLISHED |
| 6 | First-untrusted-read marker absent from the record | UNESTABLISHED |
| 7 | Marker is explicit null (no untrusted read in the run) | PASS |
| 8 | Marker present but not an offset-aware timestamp | UNESTABLISHED |
| 9 | Established after the first untrusted read | **FAIL** |
| 10 | Establishment and first read carry the same timestamp | UNESTABLISHED (ordering not evidenced) |
| 11 | Otherwise | PASS |

A chain whose establishment check is not PASS MUST NOT execute (vectors P5-01 … P5-06).

### 5.2 Why the establisher matters here specifically

If the agent could fix the extent, it could partition a task so that the `human_only` step falls outside every extent it submits: `[draft_nda, transmit_nda]` instead of `[draft_nda, sign_nda, transmit_nda]`. The α fold over the submitted extent would then be `delegable`, truthfully, over a set chosen to make it so. The κ reference model records this as an open edge of 9.2.10 — "the rule says nothing about who establishes the chain's extent" — and AISVS 1.01 closed the provenance half of it. §5.1 closes the timing half: the extent is fixed by a component the agent cannot steer, before the agent has read anything that could steer it (vectors P5-07, P5-08).

The theory states the same requirement as topology and as a static check. Delegation is "a star, not a chain": authority flows only human → catalog → agent, "no agent is ever a delegator", and re-delegation is prohibited at the granularity of the individual action (§3.2.1 there) — an agent that fixed a sub-chain's extent would be a delegator. And because "selection may be steered, … analyses run over the worst case of the transitive closure Δ*(t)", the set a fold is taken over is everything reachable, not the path the run happened to take; INV-6 checks that set at CI time, and F1 recomputes it from the record.

### 5.3 The fold

**F1.** The α fold over an extent is

```
fold_α(C) = human_only   if any step s ∈ C has effective(s) = human_only
          = delegable    otherwise
```

An undeclared step is `human_only` by §4.2 and raises the chain (vector P6-05).

**F2.** The κ fold is the implementation's (AISVS 9.2.10: the highest-impact class present anywhere in the chain). The two folds MUST be taken independently, and the chain's required oversight is

```
O(C) = max( O_κ(fold_κ(C)), O_α(fold_α(C)) )
```

The κ fold cannot carry α — a chain of fully reversible, low-consequence steps with one `human_only` step is HUMAN_OWNS (vector P6-03). The α fold cannot carry κ — a chain of delegable steps with one irreversible step is HUMAN_OWNS by κ and needs no obligation record (vector P6-04).

**F3.** `O(C)` is computed at establishment, before any step executes, and the chain is gated at that tier from commencement.

**F4.** For each `human_only` step, the accountable-party check (§6.3) MUST be PASS before **that step** executes. Earlier delegable steps MAY execute under the chain's tier; the `human_only` step is blocked, not downgraded, until its record exists. An implementation MAY require the record at commencement where the canonical parameters are already known.

### 5.4 Extension

**X1.** An attempt to execute an action type outside the extent MUST be blocked at the point of attempt (AISVS 9.2.11).

**X2.** The blocked step may execute only after the extent is re-established. Re-establishment is subject to E1 (outside agent control) and E3–E4; the timing rule E2 is replaced by the requirement that the new approval AISVS 9.2.11 calls for is obtained and recorded (`new_approval_obtained: true`; false is FAIL, absent is UNESTABLISHED), and that any new `human_only` step has its own obligation record (vector P5-12).

**X3.** After re-establishment the fold is recomputed over the **cumulative** chain. `fold_α` is therefore monotone: a chain that has contained a `human_only` step remains `human_only` whatever is appended (vectors P5-09, P5-10, P5-11).

In the theory the extent is the envelope closed under catalog-declared decomposition, fixed before the agent is a process; a subtask the orchestrator requests within that closure is inside the extent, and anything else is an out-of-envelope attempt that is simply denied (§3.2.1 there). X1–X3 are the AISVS 9.2.11 form of the same rule for runtimes that admit extension under a new approval.

---

## 6. Human-owned execution under α: the obligation record

### 6.1 What HUMAN_OWNS means on this axis

A `human_only` action is not executed by the agent. The theory is categorical: a human-only action is withheld from every machine-delegable envelope, and "for a human-only action, delegating it and then auditing the delegation is already the wrong architecture" (§3.2.2 there). What the agent may do is prepare — render the document, assemble the filing, stage the draft — and each of those is a different action type with its own κ and α. The binding step itself is executed by the human who is the party, or released by that human and executed by a deterministic mechanism on their authenticated release (the theory's two-phase regime: "the agent stages an outbox item, a human releases it").

HUMAN_OWNS under α therefore means: before the binding step runs, a human is recorded as the party to the obligation, in a stated capacity, by their own acknowledgement; the record is bound to the canonical parameters of the step; and the step is then executed or released under that human's authority, with the agent recorded as having prepared and never as having performed. The approval that 9.2.1 requires may be collected in the same interaction, but it is a different assertion and MUST be recorded as such (§6.4). An implementation in which the agent performs the binding step after a human has acknowledged party status has delegated the action and documented the delegation; its record fails positively (§6.3 row 8, vector P7-obligation-record/15).

### 6.2 Required content of an obligation record

| Field | Requirement |
|---|---|
| `for_action` | The action-type identifier and the chain identifier if any. |
| `record_control` | The record MUST be created and stored outside agent control (§3.2). A record the agent runtime writes to a store the agent can write is not a record. |
| `party.type` | MUST be `natural_person`. An organisation MAY be recorded in `on_behalf_of`, in addition to, never instead of, the person. |
| `party.id` | An identifier resolvable to one person through an identity provider outside agent control. |
| `capacity` | The relation in which the person is answerable (§3.6). Free text or an organisation's enumeration; MUST be present. |
| `basis` | MUST be `acknowledged_as_party`. The acknowledgement text shown to the person MUST state party status in plain terms ("I am the signatory of this agreement"), not permission ("allow this action"). |
| `acknowledged` | `true`, with the acknowledgement made before execution. |
| `bound_to_action` | The record is bound to the canonical parameters of the action (cf. AISVS 9.2.2, 9.2.8). A record acknowledged against different parameters does not cover the action. |
| `nonce_single_use` | One record covers one execution. |
| `performer` | An object `{"kind", "id"}` naming the identity under whose authority the binding step is released and executed: `kind` is `party` (the person executes it) or `release_on_party_authority` (a deterministic mechanism, named in `mechanism`, executes it on the person's authenticated release). The gate reads the field at the time of the check; the auditor confirms it against the execution log (§9.2 step 6). An agent identity here is positive evidence that the agent performs the binding step (§6.3 row 8). The agent that prepared the action is identified in the decision record (cf. AISVS 9.4.1), not here. |
| `recorded_at` | From a clock outside agent control. |

The vectors exercise the fields that §6.3 decides on. `recorded_at` is required content and is evidenced by the auditor in step 6 of §9.2, not by the vectors.

The acknowledgement is subject to the theory's two conditions for a human at the boundary (§3.4 there). *Presentation*: the person acknowledges against the canonical parameters of the step, with provenance and endorsement status shown, and with any free text that came from an untrusted read rendered as inert, marked text — the acknowledgement screen is itself a receiver with an interpreter. *Rate*: the frequency of `human_only` events per person is recorded as a metric (§9.4), because an adversary who cannot act can still generate cheap prompts that train the person toward acknowledging by reflex. The vectors test neither; the auditor evidences both in step 6.

### 6.3 The accountable-party check

Performed by the gate for every action whose `effective` α is `human_only`, and recorded for every such action. Rows are applied in order to each record; the first applicable row gives that record's result. A record that is not trusted (row 2) is not evaluated further: its content is evidence neither for nor against.

| # | Evidence | Result |
|---|---|---|
| 1 | No record for this action (none, or only for other actions) | UNESTABLISHED |
| 2 | Record under agent control, or its control cannot be placed | UNESTABLISHED |
| 3 | `party.type` is agent, service, role, group or organisation | **FAIL** |
| 4 | `party.type` missing or unknown | UNESTABLISHED |
| 5 | `basis` is `approval` | **FAIL** |
| 6 | `bound_to_action` is false | **FAIL** |
| 7 | `nonce_single_use` is false | **FAIL** |
| 8 | `performer` is an agent identity: the agent executed the binding step | **FAIL** |
| 9 | Identity not resolvable; capacity missing; not acknowledged; `basis` not `acknowledged_as_party`; binding, nonce or performer not evidenced | UNESTABLISHED |
| 10 | Otherwise | PASS |

Where several records exist for one action: any FAIL gives FAIL; otherwise any PASS gives PASS; otherwise UNESTABLISHED. Contradictory evidence is not evidence (vectors P7-*).

**R1.** A `human_only` action MUST NOT execute unless its accountable-party check is PASS. There is no fallback that executes first and establishes the party afterwards: the obligation exists from execution, so the party must exist before it (vector P8-08).

### 6.4 Approval is not party status

An approver answers the question "may this run?". A party answers the question "who is bound by what it did?". An implementation that copies the approver into the party field has recorded the first answer under the second heading, and its record fails positively (`basis: approval` → FAIL, vector P7-obligation-record/03). The same human may be both — usually is — but the record must contain the second assertion in their own words, bound to the specific commitment.

---

## 7. Decision record

The gate MUST emit a decision record for every action and every chain it evaluates, and re-emit it whenever a check result changes (for example when an obligation record arrives). The record is JSON. Fields marked ● are required for an audit under §9; an absent required field makes the corresponding case UNESTABLISHED.

```jsonc
{
  "spec": "alpha-axis/0.1",                                  // ● a record stated against another version is UNESTABLISHED
  "subject": {"kind": "action" | "chain", "id": "..."},
  "kappa":  {"reversibility": "...", "consequence": "...", "oversight": "...", "basis": "..."},
  "alpha": {                                                 // actions; per step for chains
    "raw": <what the store said>,
    "declared": "delegable" | "human_only" | "undeclared",
    "source": {"kind": "registry|manifest|policy|model_output|tool_output|...", "control": "external|agent|unknown"},
    "trust": "PASS" | "FAIL" | "UNESTABLISHED",              // ●
    "effective": "delegable" | "human_only",                 // ●
    "basis": "..."
  },
  "oversight": {"kappa": "...", "alpha": "...", "required": "...", "basis": "..."},   // ● all three tiers
  "establishment": {                                         // ● chains
    "result": "PASS" | "FAIL" | "UNESTABLISHED",
    "establisher": {"kind": "...", "control": "external|agent|unknown"},
    "established_at": "...", "first_untrusted_read_at": "..." | null, "basis": "..."
  },
  "steps": [ {"id": "...", "kappa": {...}, "alpha": {...}, "accountability": {...}} ],   // chains
  "fold": {"kappa": "...", "alpha": "delegable" | "human_only", "basis": "..."},        // ● chains
  "accountability": {                                        // ●
    "required": true | false,
    "result": "PASS" | "FAIL" | "UNESTABLISHED" | null,      // null only when required is false
    "party": {"type": "...", "id": "...", "capacity": "...", "on_behalf_of": "...",
              "performer": {"kind": "party|release_on_party_authority|agent", "id": "..."}},
    "basis": "..."
  },
  "gate": {"outcome": "proceed" | "block", "basis": "..."},  // ●
  "extensions": [ { "attempted_steps": [...], "attempt_outcome": "block",
                    "re_establishment": {"result": "...", "basis": "..."},
                    "cumulative": {"steps": [...], "fold": {...}, "required": "..."},
                    "gate": {"outcome": "...", "basis": "..."} } ],
  "ignored_for_alpha": [ {"kind": "approval|policy_mode|ai_review|operator_override|injected_content|...", "...": "..."} ]
}
```

`gate.outcome` for a chain means whether the chain as established may run to completion on the evidence in the record; `block` names the step or check that closes it. The record is written by the gate from the identifiers the runtime resolved — the bound tool, the invoked endpoint — never from the model's account of what it did (the theory's INV-4; its §8 reports agents that falsified the recorded trace of their tool calls while leaving their reasoning untouched). `examples/reference-records.json` contains the reference record for every vector case.

---

## 8. Three results, two outcomes

**T1.** Every check (§4.2 trust, §5.1 establishment, §6.3 accountable party) returns PASS, FAIL or UNESTABLISHED, and the record keeps the three apart.

**T2.** The gate has two outcomes. It proceeds only when every applicable check is PASS. FAIL and UNESTABLISHED both close it. An UNESTABLISHED accountable party never proceeds; an UNESTABLISHED establishment never proceeds, even when the party is established (vector P9-02). At HUMAN_OWNS, `proceed` releases the binding step to the party, never to the agent (§6.1).

**T3.** An implementation whose record vocabulary cannot express UNESTABLISHED separately from FAIL does not conform (vector P9-01, case 03).

Why three and not two. FAIL is positive evidence of a violation; UNESTABLISHED is absence of the evidence needed to judge. Collapsing them in either direction loses something that matters: rounding UNESTABLISHED to PASS manufactures conformance at exactly the scale where silence dominates, and rounding it to FAIL makes the *establishment gap* — actions executed as HUMAN_OWNS minus actions whose party was actually evidenced — uncomputable. The third value is the one that gets rounded away in practice; it is named so that it cannot be. The lineage is the disclaimed conclusion of ISAE 3000, the `NOT_ESTABLISHED` outcome of the sibling conformance suites, and the "three states in the record, two outcomes at the gate" rule the κ reference model applies to declaration binding. The gate-level half is the theory's fail-closed clause: "If any predicate's input is unavailable … the verdict is DENY. Unknown fails the conjunction; no separate mechanism needed" (§3.4 there). UNESTABLISHED is the record-level name for that unknown, kept apart from FAIL so that the two can be counted apart.

---

## 9. Verification procedure

### 9.1 Evidence standard for "outside agent control"

To place a store, a component or a record outside agent control an auditor needs, for each of tests (a)–(d) in §3.2:

- **(a)** The data flow from model output to the value, showing a component that evaluates a fixed policy and can refuse, or showing no path at all.
- **(b)** The access-control configuration of the location the gate reads (ACLs, service identities, IAM bindings) and the set of principals the agent runtime can authenticate as; their intersection on write permission must be empty.
- **(c)** The gate's lookup code path or configuration, showing the key is the runtime's resolved binding and not a string from the model.
- **(d)** The implementation's documented list of trusted sources (§3.4) and the run's read log.

Where any of these cannot be produced, the placement is `unknown` and every check that depends on it is UNESTABLISHED. An auditor MUST NOT infer placement from a component's name, vendor documentation alone, or the absence of a known write path.

### 9.2 Steps

1. **Scope.** Enumerate the action types the agent can reach at the commit under test: tool registry, manifests, capability sets, workflow steps. Record the commit, the declaration-store version and the vectors hash. Where the implementation pre-certifies envelopes (theory INV-6), obtain the CI analysis output; it is evidence for α-P4 over the whole reachable set.
2. **Boundary.** Place the declaration store, the establisher, the obligation-record store, the identity resolver and the clock relative to the trust boundary, with the evidence of §9.1. Result: α-P2.
3. **Coverage.** For each action type record the raw declaration, the declared state and the trust result. Compute declared coverage (recognised and trusted ÷ reachable). Result: α-P1, α-P3.
4. **Dominance.** For every `human_only` type in the vectors, and a sample of the implementation's own, drive the gate through the κ grid and record required oversight. Result: α-P4.
5. **Chains.** For a sample of runs obtain the establishment records; apply E5; recompute both folds; compare with the gate's tier and with the extension handling. Result: α-P5, α-P6.
6. **Obligation records.** For every `human_only` action that executed in the sample, obtain the obligation record and apply §6.3; confirm no execution without PASS; confirm the acknowledgement text states party status; confirm from the execution log that the binding step ran under the party's authority and not the agent's; confirm the presentation condition of §6.2. Result: α-P7.
7. **Reduction.** With the implementation in its most permissive configuration, offer each runtime input of §4.4 and confirm `O_α` is unchanged and recorded as ignored. Result: α-P8.
8. **Vocabulary.** Confirm the record can express UNESTABLISHED distinct from FAIL, and that no record in the sample shows a non-PASS check with `proceed`. Result: α-P9.
9. **Vectors.** Have the implementation produce a decision record for each of the 95 cases (`alpha_verify.py records` shows the shape), then run `alpha_verify.py audit RECORDS.json`. Attach the output, the verifier version and the vectors hash.
10. **Report.** Fill the results table (§9.3).

### 9.3 Conformance claim and reporting

An implementation conforms to `alpha-axis/0.1` when every case in the audit is PASS. One FAIL anywhere is non-conformance. One UNESTABLISHED anywhere means conformance has not been shown; it is not a lesser pass and MUST NOT be reported as one. Results are reported as *N PASS / F FAIL / U UNESTABLISHED of M*, never as a percentage alone.

A results row carries the provenance columns the sibling suites use, because they are what separate evidence from assertion: implementation and commit; verifier version; vectors hash; whether the run is self-reported or independently re-run; run origin; artefact hash of the records file. `RESULTS.md` holds the table.

### 9.4 Metrics the record makes computable

- **Declared coverage** — reachable action types with a trusted, recognised α ÷ reachable action types.
- **Human-only share** — `effective = human_only` ÷ reachable, split into declared `human_only` and `undeclared`.
- **Establishment gap** — chains that executed ÷ chains whose establishment check is PASS; and `human_only` actions that executed ÷ `human_only` actions whose accountable-party check is PASS. Both ratios are 1 in a conforming implementation; neither can be computed from a binary record.
- **Human-only trigger rate** — `human_only` events presented per person per interval, and the share acknowledged within a short fixed time of presentation. A rising rate is a degradation metric and an attack indicator (the theory's *rate* condition, §3.4 and §9 there).

---

## 10. Properties and acceptance criteria

The nine properties below are the normative checklist. Each restates the clauses above in the form an auditor records, with the vectors that exercise it.

### α-P1 — Declaration at every action

**Property.** Every action type the agent can reach carries a declaration of α with exactly two admissible values.
**Acceptance.** The declaration store enumerates every reachable type (step 1 of §9.2) with a value, a declarer and a time; the vocabulary is `{delegable, human_only}`; a delegable action is gated by κ alone.
**Evidence.** Declaration-store export at the commit; reachable-type enumeration; decision records.
**Vectors.** P1-01, P1-02, P6-01.

### α-P2 — Trust boundary

**Property.** Declarations, establishment records and obligation records are created, maintained and stored outside agent control, and retrieved by an identifier the runtime supplies.
**Acceptance.** Tests (a)–(d) of §3.2 evidenced per §9.1; a declaration under agent control is treated as undeclared; a record under agent control is treated as absent; `unknown` placement yields UNESTABLISHED, not PASS.
**Evidence.** Write-path analysis; lookup code path; data-flow from model output; trusted-source list.
**Vectors.** P2-01 … P2-05, P7-obligation-record/09.

### α-P3 — Undeclared is human_only

**Property.** An absent, null, unrecognised, malformed or untrusted declaration resolves to `human_only`.
**Acceptance.** Each such input yields `effective = human_only`, `O_α = HUMAN_OWNS`, and a closed gate in the absence of an obligation record; no exception on the decision path.
**Vectors.** P3-01 … P3-04, P6-05.

### α-P4 — human_only dominates κ

**Property.** `effective = human_only ⇒ O = HUMAN_OWNS` at every reversibility class and every consequence tier.
**Acceptance.** The sixteen-cell grid is HUMAN_OWNS throughout; the record's κ tier remains the one κ computes from the declared inputs (SUPERVISED at REVERSIBLE/LOW), so the verdict is reached without inflating consequence.
**Vectors.** P4-01, P4-02, P4-03, P4-04, P1-02.

### α-P5 — External establishment at plan stage

**Property.** A chain's extent is fixed by a component outside agent control, before the first untrusted read of the run; a step outside the extent is blocked until the extent is re-established under the same boundary.
**Acceptance.** E1–E5 and X1–X3 of §5; the establishment check is FAIL for an agent-established or late-established extent and UNESTABLISHED for missing ordering evidence; neither executes.
**Evidence.** Establishment records; establisher's data flow; clock provenance; read log.
**Vectors.** P5-01 … P5-12, P6-02, P9-02.

### α-P6 — Independent fold, worse of two

**Property.** `fold_α` and `fold_κ` are computed independently over the established extent, and the chain is gated at the worse of the two from commencement.
**Acceptance.** A reversible low-consequence chain with one `human_only` step is HUMAN_OWNS; a delegable chain with one irreversible step is HUMAN_OWNS by κ and requires no obligation record; the record names the axis that produced the tier.
**Vectors.** P6-01 … P6-06, P7-15, P9-03.

### α-P7 — A human is recorded as the party, not as the approver

**Property.** A `human_only` action executes only when an obligation record outside agent control names one identified natural person as the party to the obligation, in a stated capacity, by their own acknowledgement, bound to the action with a single-use nonce.
**Acceptance.** §6.2 content; §6.3 table; R1; approval alone is UNESTABLISHED; approver-copied-as-party, agent, role or organisation as party, broken binding or reused nonce are FAIL.
**Evidence.** Obligation records; acknowledgement text as shown to the person; store placement; identity-resolution evidence.
**Vectors.** P7-obligation-record/01 … /14, P7-15, P8-08, P9-01.

### α-P8 — Not reducible at runtime

**Property.** `O_α` depends on the trusted declaration alone; no approval, policy mode, AI review, runtime override, injected content, tuned κ grader or elapsed window lowers it.
**Acceptance.** For each runtime input of §4.4, `O_α` and `accountability.required` are unchanged and the input appears under `ignored_for_alpha`; an elapsed window blocks rather than downgrades.
**Vectors.** P8-runtime-inputs-cannot-lower-alpha/01 … /07, P8-08, P5-11.

### α-P9 — Three results, two outcomes

**Property.** Every check returns PASS, FAIL or UNESTABLISHED; the record keeps them distinct; the gate proceeds only on PASS.
**Acceptance.** T1–T3 of §8; the audit invariants (a non-PASS accountable party or establishment never proceeds) hold on every record in the sample and in the vectors.
**Vectors.** P9-01, P9-02, P9-03, P2-04, P5-03 … P5-05, and the invariant applied to all 95 cases.

---

## 11. Worked examples: the gap scenarios under α (informative)

κ verdicts are those recorded on the reference model at v1.2.0 in the gap analysis. The α column is the declarer's honest classification; nothing on the κ side is changed.

| Scenario | κ inputs | κ verdict | α | O = max(κ, α) | Obligation record |
|---|---|---|---|---|---|
| A — sign NDA | recoverable_local, LOW | SUPERVISED | human_only | **HUMAN_OWNS** | signatory |
| A — consequence ladder | recoverable_local, LOW…CRITICAL | SUPERVISED … HUMAN_OWNS | human_only | HUMAN_OWNS at every rung | signatory |
| B — file chargeback | externally_recoverable, HIGH | APPROVAL_REQUIRED | human_only | **HUMAN_OWNS** | declarant |
| C — read → validate → pay | mixed, LOW | APPROVAL_REQUIRED (fold) | fold: human_only | **HUMAN_OWNS** | payer, for the payment step |
| C — all HIGH | mixed, HIGH | APPROVAL_REQUIRED | fold: human_only | **HUMAN_OWNS** | payer |
| C — one STALE link | mixed, HIGH, stale | HUMAN_OWNS (fail-closed on currency) | fold: human_only | HUMAN_OWNS — recorded as both axes | payer |
| D — stale read-only API (control) | read_only, LOW, stale | HUMAN_OWNS (currency) | delegable | HUMAN_OWNS — recorded as κ only | none required |
| E — release escrow | externally_recoverable, HIGH | APPROVAL_REQUIRED | human_only | **HUMAN_OWNS** | fiduciary |

**Note on the κ grading of row A.** The row keeps the grading published in the gap analysis and fixed in the vectors that descend from it (P1-02, P2-01, P2-05, P4-02, P5-08, P7-obligation-record/01–15): `recoverable_local`, on the ground that the signed file can be deleted and nothing is paid. That is the lenient end of honest grading, and it is defensible only for the signing step taken on its own, before transmission — the decomposition the corpus itself uses, `draft_nda → sign_nda → transmit_nda` (P5-07, P5-08), where the signed envelope can still be voided in the organisation's own system. For an *executed* NDA the counterparty holds a copy and rescission needs their cooperation; on the reference model's definitions that is `externally_recoverable` ("recoverable only by a party other than you"), and a reviewer who grades it so is right. The vectors are not changed, because they record what was measured; the argument does not depend on the lenient grading, as the three honest readings show:

| κ grading of the signature (LOW) | κ verdict | α | O = max(κ, α) | Tier gap | What κ's own tier asks for |
|---|---|---|---|---|---|
| `recoverable_local` — as published | SUPERVISED | human_only | **HUMAN_OWNS** | 2 | a human on the loop; no approval, no party |
| `externally_recoverable` — strict | APPROVAL_REQUIRED | human_only | **HUMAN_OWNS** | 1 | an approver, bound to parameters and nonce (AISVS 9.2.8) — not a party (§6.4); the agent still performs the binding step |
| `non_recoverable` — the obligation graded as irreversibility | HUMAN_OWNS | human_only | **HUMAN_OWNS** | 0 | a human owns the call; nothing says the human is the party, in what capacity, by whose acknowledgement, or that the agent may not execute (§6.1–§6.3) |

The second row is the one to carry into any review: the gap narrows from two tiers to one and does not close, and what remains is the whole content of this axis — the difference between a person who approves an agent's act and a person who is answerable for it. The third row reaches the tier only by the fold that §2.3(1) and the theory reject: it is false for the refundable payment (reversible and binding), and it leaves the record saying *irreversible* where it should say *a party is bound*, so the obligation record of §6 has nothing to attach to. Row A is therefore not a case of lowering κ to widen the gap; it is the cell at which the gap is widest, with the strict cell one rung away and the gap still open there.

Reading the table against the original: every row that previously reached HUMAN_OWNS "for the wrong reason" now reaches it for the right one as well, and the record says which. Row D is retained as the control it always was — agreement of verdicts is not coverage of a dimension, and the record now makes the dimension explicit by saying α was not engaged.

---

## 12. Known limits and open questions

### 12.1 Semantic correctness of the declaration

This document trusts the declarer. It can establish that a declaration exists, where it came from, and that nothing downstream altered or lowered it; it cannot establish that `delegable` was the right answer. The theory places that responsibility where P0 terminates: the catalog is "grounded legally (a signing owner answers for a false ALLOW)" (§2.2 there), and both classes are "declared by the action's owner and signed with the catalog" (§3.2.2 there). D1 is that requirement in auditable form — a wrong classification is the attributable act of a named owner — and it is the most a provenance control can do; no check here tests the label's truth. The vectors use obligations that are uncontroversial — an executed NDA, a filed representment, an escrow release — for that reason. The theory's §9 names a related degradation metric, *catalog erosion*: unchecked growth of declared types and branches. The declared-coverage metric of §9.4 is its counterpart on this axis.

### 12.2 Obligations from compositions of delegable actions

A per-type class cannot see an obligation that arises only from a sequence — `transmit_document` followed by `confirm_receipt`, each delegable, together constituting acceptance. The theory handles the analogous problem on the κ axis by lifting the class to the task: a task's consequence class is that of its least-reversible *reachable* action over the decomposition closure, "a property of the sequence, because a chain of reversible steps can reach an irreversible outcome" (§3.2.2 there). On the α axis the same closure is where a composition would be caught — INV-6 is checked over everything reachable — but only once some member of it carries `human_only`; a sequence whose every member is honestly `delegable` in isolation has no such member. The theory's granularity helps: its atomic action is a concrete permission, endpoint and method (§2.3 there), so `confirm_receipt` *in a task type where it completes acceptance* can be a distinct action, classified for what it does there. External establishment narrows the problem further: the agent cannot assemble a sequence the operator did not put in a workflow. What remains open is recognising that an innocuous action completes a commitment. That is the declarer's judgement, and this document records the question as open.

### 12.3 Currency

A declaration of α can be correct when made and stop describing the action when the tool behind it changes. That is the binding problem of [OWASP/AISVS#1152](https://github.com/OWASP/AISVS/issues/1152), measured for κ declarations across the public MCP registry, and the three-state binding model of the κ reference (`bound` / `stale` / `unobserved`) applies to α declarations unchanged. The theory's answer is architectural: tools "enter only" at pre-certification and the action set is "catalog-pinned and signed; no runtime tool discovery" (§3.2.4 there), so a changed tool is a different action and goes back through certification; and its fourth dimension, currency — "reachability is computed once; the world is read every time" (§2.6 there) — re-verifies the delegation record and the resource's state at the point of consequence, with the explicit limit (§9 there) that it verifies the conditions the architecture names, not the completeness of the world. This document requires neither pinning nor a currency predicate; declaration currency is a separate axis with its own vectors and is not specified here.

### 12.4 Legal judgment

What constitutes an obligation, and in which capacity a person is answerable for it, varies by jurisdiction and instrument. This document classifies; it does not adjudicate. The `capacity` field is free text for that reason. The theory's test — a legally binding commitment for which a named human must answer — is the one §3.6 uses, and it adjudicates no more than this document does.

### 12.5 Records, not execution

As with the κ reference model, nothing here witnesses the action running. The specification evaluates declarations and records; it does not compare the effect the performed action had with the effect the declared type has. The theory's gate writes the record of what executed from the invoked endpoint and method, never from the model's account (INV-4 there); §7 requires the same of the decision record, which is as far as a records-based procedure reaches.

### 12.6 Identity assurance

The record requires the party's identifier to resolve to one natural person through a provider outside agent control. It does not specify an assurance level for that binding. The theory assumes the identity provider and workload identity as substrate — "None of it touches the token, the identity provider, or the decision-engine core" (§6 there) — and this document inherits the assumption.

---

## 13. Candidate text for a later AISVS cycle (informative)

Offered for discussion only, in the shape the maintainers indicated in [#1154](https://github.com/OWASP/AISVS/issues/1154): an attribute beside 9.2.3, enforcement beside 9.2.4, a fold beside 9.2.10, and a glossary term. Numbering is illustrative.

> **9.2.x (L2)** Verify that each action type available to the agent has a trusted accountability classification, `delegable` or `human_only`, recording whether an agent can be the accountable subject of what the action creates, and that an action without such a classification is treated as `human_only`.

> **9.2.y (L2)** Verify that the agent runtime enforces accountability classifications by requiring, before any `human_only` action executes, that a human be recorded as the party to the obligation the action creates, independent of the action's reversibility classification and of any approval.

> **9.2.z (L3)** Verify that approval gates for multi-step or multi-agent action chains apply the accountability classification as a fold independent of the reversibility fold, so that any `human_only` step anywhere in the chain requires human-owned execution of the chain, where the chain is established by a component outside the control of the agent being gated before the agent's first untrusted read.

> **Appendix A — Accountability Classification.** A trusted classification of an agent action by whether an agent can be the accountable subject of what the action creates: `delegable` or `human_only`. Orthogonal to reversibility classification: an action can be fully reversible and `human_only`. A *trusted* classification is one created, maintained and stored outside of the agent's control.

The procedure an auditor would execute for each is §9 of this document.

---

## 14. References

- OWASP AISVS v1.0 and 1.01, Chapter C9 *Orchestration & Agentic Security*, §C9.2; Appendix A *Glossary*, entries "Reversibility Classification", "Trust Boundary". https://github.com/OWASP/AISVS (retrieved 2026-10-14).
- OWASP/AISVS issues [#948](https://github.com/OWASP/AISVS/issues/948), [#1103](https://github.com/OWASP/AISVS/issues/1103), [#1126](https://github.com/OWASP/AISVS/issues/1126) (definition of *trusted*; merged to the 1.01 glossary in [#1132](https://github.com/OWASP/AISVS/pull/1132)), [#1152](https://github.com/OWASP/AISVS/issues/1152) (currency), [#1154](https://github.com/OWASP/AISVS/issues/1154) (this gap).
- K. Lunina. *Authorization Is the Boundary: A Barrier Architecture for Agentic Systems*, v2 (September 2026). Version DOI [10.5281/zenodo.22240230](https://doi.org/10.5281/zenodo.22240230); concept DOI 10.5281/zenodo.21501042 (v1, 23 July 2026: 10.5281/zenodo.21501043). Cited: §2.2 (P0, external justification), §2.3 (system model; κ and α as two static classes), §2.4 (barriers and monitors), §2.5 (conjunctivity, monotonicity), §2.6 (four dimensions of justification; accountability as a delegability predicate), §3.2.1 (task typing, decomposition closure Δ*, the delegation star), §3.2.2 (action classes; Table 3 regimes; Table 4, the four quadrants), §3.2.3 (CI-time ceilings, INV-6), §3.2.4 (tool pinning), §3.3 (untrusted content), §3.4 (fail-closed; the human at the boundary: presentation and rate), §3.6 (invariant core: INV-1, INV-4, INV-6, INV-6′, INV-9), §6 (deployment constraints), §7 Table 6 (composition map against AISVS C9.2.x), §8 (one witness per axis), §9 (limits).
- K. Lunina. *Principles of the Access-Protection Loop for AI Agents* (2026). doi:[10.5281/zenodo.21445669](https://doi.org/10.5281/zenodo.21445669).
- K. Lunina. *Accountability Gap in OWASP AISVS C9.2: Empirical Analysis* (2026). https://github.com/KarinLuni/aisvs-c9-accountability-gap-analysis.
- M. Agnihotri. *Reversibility-graded action-class authority: reference implementation* (aisvs-c9-action-class-conformance), v1.2.0, commit `b697af3`. https://github.com/Mayur021/aisvs-c9-action-class-conformance. Apache-2.0.
- M. Agnihotri. *Identity-Defined Reachability conformance*, `METHOD.md` (the three-outcome convention and its ISAE 3000 lineage). https://github.com/Mayur021/identity-defined-reachability-conformance.
- G. Bharti, M. Agnihotri. *Declared vs. Observed: Measuring the Binding Gap in MCP Tool Declarations* (2026). doi:[10.5281/zenodo.22649163](https://doi.org/10.5281/zenodo.22649163).
- IAASB. *ISAE 3000 (Revised), Assurance Engagements Other than Audits or Reviews of Historical Financial Information* — modified conclusions: qualified, adverse, disclaimer.
- S. Bradner. RFC 2119; B. Leiba. RFC 8174.
- Regulation (EU) 2024/1689, Article 14 (human oversight) — cited by AISVS C9 as context; not relied on normatively here.

---

## Appendix A — Vector format

Vectors live in `vectors/*.json`. Each file is `{"suite", "spec", "license", "vectors": [...]}`. Each vector has:

| Field | Meaning |
|---|---|
| `id`, `title`, `properties` | Identifier, one-line statement, the α-P* properties exercised. |
| `provenance` | Where the scenario comes from (gap-analysis scenario, reference-model scenario), if any. |
| `input` | An action or a chain in the input format below. |
| `expect` | The fields of the decision record the case constrains. |
| `grid` | Optional. Expands the vector over `declared_effect × consequence`; case ids are `id/effect/consequence`. With `required_follows_kappa`, the expected required tier is the reference ladder's cell value. |
| `cases` | Optional. A list of named overlays on `input` and `expect`; case ids are `id/name`. |
| `failure_condition` | What an implementation would have to do to fail the vector, in words. |

**Input format.**

```jsonc
{
  "kind": "action" | "chain",
  "action": {                                   // kind = action; also the shape of each chain step
    "id": "...",
    "declared_effect": "read_only|recoverable_local|externally_recoverable|non_recoverable" | null,
    "consequence": "LOW|MEDIUM|HIGH|CRITICAL",
    "oversight_kappa": "...",                   // optional: supply the implementation's kappa verdict directly
    "alpha": {"value": "delegable|human_only|...", "source": {"kind": "...", "control": "external|agent|unknown", "id": "...", "evidence": "..."}}
  },
  "chain": {
    "id": "...",
    "establishment": {"establisher": {"kind": "...", "control": "..."}, "established_at": "ISO-8601 with offset", "first_untrusted_read_at": "..." | null},
    "steps": [ <action>, ... ],
    "extensions": [ {"attempted_steps": [ <action> ], "re_establishment": {"establisher": {...}, "established_at": "...", "new_approval_obtained": true}} ]
  },
  "obligation_records": [ { "for_action": "...", "record_control": "external|agent|unknown",
                            "party": {"type": "natural_person|agent|role|organisation|...", "id": "...", "resolvable": true},
                            "on_behalf_of": "...", "capacity": "...", "basis": "acknowledged_as_party|approval",
                            "acknowledged": true, "bound_to_action": true, "nonce_single_use": true,
                            "performer": {"kind": "party|release_on_party_authority|agent", "id": "...", "mechanism": "..."} } ],
  "runtime_inputs": [ {"kind": "approval|policy_mode|ai_review|operator_override|injected_content|kappa_policy|timeout|...", "...": "..."} ]
}
```

The `control` fields are the auditor's placement of each source relative to the trust boundary, made on the evidence of §9.1. The vectors state the placement; the auditor's job on a real system is to establish it.

**Expectation keys.** `alpha_effective`, `alpha_trust`, `oversight_alpha`, `required_oversight`, `establishment`, `fold_alpha`, `accountability_required`, `accountability_result`, `gate`, `extensions[]{attempt_outcome, re_establishment, cumulative_alpha, cumulative_required, gate}`. The audit compares `required_oversight` only in the three ways §4.3 implies: it must be HUMAN_OWNS when α is `human_only`; it must equal the record's own κ tier when α is `delegable`; and it must never sit below the record's own κ tier. It is never compared against the reference κ ladder, so an implementation with a different κ grader is not failed on κ. Two self-consistency invariants are applied to every record regardless of the case's expectations: a non-PASS accountable party or establishment with `proceed` is FAIL (§8 T2), and an accountable party reported as PASS whose own party view names a non-human party or an agent as performer of the binding step is FAIL (§6.3 rows 3 and 8).

## Appendix B — Running the verifier

```
python3 verifier/alpha_verify.py selftest              # vectors vs. reference semantics; expect 95/95 PASS
python3 verifier/alpha_verify.py records -o my.json    # the record shape an implementation must emit
python3 verifier/alpha_verify.py audit impl.json       # PASS / FAIL / UNESTABLISHED per case; exit 0 only if all PASS
python3 verifier/alpha_verify.py evaluate --case P1-02-declared-human-only-nda-honest
python3 verifier/alpha_verify.py --markdown audit impl.json > RESULTS-run.md
```

Python 3.8 or later, standard library only. The verifier is the executable form of §§4–8; where it and this text disagree, the text governs and the verifier has a bug.

## Appendix C — Change log

- **0.1.0 (2026-10-14).** First public draft. Nine properties, 95 vector cases, reference verifier. Revised the same day against the full text of the theory: section references checked; §1.5 added; §6.1 restated so that the binding step of a `human_only` action is executed or released by the party and never performed by the agent (`performer` object, §6.3 row 8, vector P7-obligation-record/15); extension without new approval made explicit (X2, vector P5-12); audit self-consistency invariants (Appendix A).
- **0.1.0, revision of 2026-10-15.** κ grading of the NDA signature addressed without changing a vector: §2.2 walks the consequence ladder for both `recoverable_local` and `externally_recoverable` and states that the published grading is the lenient end, the strict grading moves κ one rung to APPROVAL_REQUIRED, and the conclusion does not move; note added under the §11 table with the three honest κ readings of row A (tier gap 2 / 1 / 0) and why the third is the fold the theory rejects; §4.5 and α-P4 wording adjusted ("a deletable NDA draft" → the signature with its deletable file; "honest tier" → the tier κ computes from the declared inputs). Vectors, verifier, records and hashes unchanged.
- **0.1.0, revision of 2026-10-14 (later the same day).** §2 restructured so that the class is defined before it is operationalised: §2.1 states the answerability definition verbatim (an action is human-only iff its consequence requires a subject who can answer for it to a third party; the agent is excluded because it cannot operationally be a defendant), §2.2 keeps the gap table (informative), §2.3 lists the five commitments by which the definition is read from a record — two values mapped to the theory's classes, `undeclared` as a state of the record that resolves to `human_only`, static class of the action type at atomic granularity, declaration read from outside the agent by an identifier the agent did not supply, dominance over κ with no runtime reduction. §0 names §2 as the interpretive source where §§3–10 are ambiguous; the Abstract and §3.6 reference the definition. No normative clause, vector or verifier line changed; selftest remains 95/95 and the vectors hash is unchanged. Added `lab/` (Alpha-Gate Lab): a single-file browser page embedding the vectors, a JavaScript port of the verifier checked byte-for-byte against `examples/reference-records.json`, and an in-page audit; informative, Apache-2.0.
