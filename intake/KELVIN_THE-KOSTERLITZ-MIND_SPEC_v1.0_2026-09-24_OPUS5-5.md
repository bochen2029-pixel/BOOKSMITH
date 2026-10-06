# KELVIN — the Kosterlitz mind

**Specification v1.0 · 2026-09-24 · Opus 5.5 · the one-shot bet**

```
status      PROPOSED. Exploratory research, specified completely enough to build and to falsify.
targets     RTX 4070 Ti SUPER (sm_89, the card on the desk today) · RTX 5090 (sm_120) · H200 SXM (sm_90)
stack       C++20 + CUDA 12.8 or later for the core (the box has 13.1) · Python for analysis only ·
            mindbox as the exact plane
lineage     third-form specs v0.1 and v0.2 · the two KELVIN transcripts (ChatGPT, Claude web) ·
            Native Intelligence (January 2026) · seed v0.2 · tanklab L0 · The Unfinished Mirror
```

In 1867 Kelvin guessed that atoms were knots in a flowing medium. He was wrong about atoms. This document bets he was right about thought, and specifies the medium closely enough to find out.

It is written in the spirit of the Astrophage simulator: take something that does not exist, lock every constant to its provenance, and let the physics say what it does. Every number carries a tag.

| tag | meaning |
|---|---|
| **[PHYS]** | established physics or mathematics, with a named source |
| **[HW]** | a published hardware figure |
| **[CHOICE]** | a design choice; change it freely |
| **[TARGET]** | a number the build must hit, measured by the experiments in §11 |
| **[BET]** | what this document stakes; §11 can kill it |

**How to read it.** §0–§1 state the claim. §2–§9 specify the mind: its medium, concepts, learning, attention, record, self, organs and instruction set. §10 is the machine, with code and budgets for three cards. §11 is the experiments that can kill it, §12 the build plan, and §13 how it dies.

---

## 0 · The bet

**[BET] A mind is a two-dimensional XY medium held just inside its Kosterlitz phase.** In that one regime, a lattice of cheap, noisy phases does four things that no substrate we use today does at once.

1. **Meaning is an integer.** Vortices carry an exact topological charge that noise cannot erode. A concept cannot drift into a different concept. It can only be born or die, and only together with its opposite.
2. **Abstraction is renormalization.** Coarse-grain the field and small bound pairs cancel out; what survives is general. The mipmap pyramid the GPU already has is the renormalization group.
3. **Thinking is reversible; concluding is erasure.** Exploration runs as an exact permutation of an integer state space, so it can be run backward. Only settling contracts states, and only settling needs a record. A whole life is replayable from its conclusions.
4. **Learning is waking minus dreaming.** The XY Boltzmann rule is local and exact: correlations while the world clamps the field, minus correlations while it runs free. Sleep erodes whatever waking never confirms.

The GPU runs it the way a game engine runs a world. Attention is culling, abstraction is level of detail, and sleep bakes the lightmaps.

### Why "Carmack cubed"

Carmack's inverse square root worked because a float's bits already approximate log₂ x, so a hard operation became a shift and a subtraction. KELVIN stacks three isomorphisms of that kind.

| hard cognitive operation | what the silicon already does | cost |
|---|---|---|
| "is this a concept, and which one?" | phase bits are the circle; four `int8` subtractions and a shift give an exact winding number | a few integer instructions per plaquette; a warp clears 32 plaquettes in one vote |
| "what is the general form of this?" | the texture pyramid is a block-spin renormalization; generality is a mip level | one filtered restriction per level |
| "what if I hadn't thought that?" | the integer leapfrog is a bijection; un-thinking is the same kernel run backward | no memory; the same arithmetic as thinking |

Each one makes an expensive act of cognition native to the hardware. Three at once is the cube.

### The five laws

- **L1 · The seam.** Thinking is reversible. Concluding erases. The record holds exactly what erasure destroys.
- **L2 · Charge.** Concepts are topological charges. They are born and killed only in ± pairs, persist by topology, and are kept only while they pay rent in bits.
- **L3 · Scale.** A concept's generality is the coarsest level of the pyramid at which its charge survives.
- **L4 · Carving.** Learning is wake minus sleep, and only what the mind does not author may clamp the wake phase. Language may perturb; only consequences may carve.
- **L5 · Reach.** A perturbation's reach is the screening length √(J/h). Work is bounded by reach, not by the size of the mind.

### What kills it (details in §11)

- On the ε-machine gauntlet, concept births do not track the true causal states. The field is a lava lamp.
- The homeostat cannot hold the living band without being tuned by hand for each task.
- Compute per competent decision does not fall as it lives.
- Scrambling its terrain does not change who it is.

---

## 1 · What it is, and what it is not

| | shaped by | the unit | its native question |
|---|---|---|---|
| brain emulation | evolution, copied | neuron and synapse | what does this biology do? |
| language model | human text | token | what comes next? |
| **KELVIN** | its own consequences | a topological charge in a critical medium | how does the space of futures bend here, and what cannot change without an event? |

It is not a connectome, a transformer, a symbolic engine or a spiking network. Nothing fires. A unit of meaning is a charge in a continuous medium.

**The honest lineage.** Every ingredient is established physics or mathematics:
- the XY model (1960s–70s); the Kosterlitz–Thouless transition (1973); Kosterlitz's renormalization group (1974); the Nelson–Kosterlitz universal jump (1977);
- Boltzmann machine learning (Ackley, Hinton and Sejnowski, 1985); reverse learning in dream sleep (Crick and Mitchison, 1983; Hopfield, Feinstein and Palmer, 1983);
- multigrid (1970s–80s) and multigrid Monte Carlo (Goodman and Sokal, 1986); braid groups (Artin, 1925);
- bit-reversible integration (Levesque and Verlet, 1993); Landauer's principle (1961);
- computational mechanics and CSSR (Crutchfield; Shalizi and Klinkner, 2004); local push (Andersen, Chung and Lang, 2006);
- the game-engine toolchain: culling, level of detail, the potentially visible set and baked lighting (id Software, Quake, 1996).

What is new is the claim that together they are a mind, and the specification below.

---

## 2 · The medium

### 2.1 State

The field is a lattice $\Lambda_0 = \mathbb{Z}_L\times\mathbb{Z}_L$, with $L = 4096$ on the 5090 **[CHOICE]**. Each cell $i$ holds:

| symbol | type | meaning |
|---|---|---|
| $\theta_i$ | `uint8`, $\mathbb{Z}_{256}$ | phase. The circle is 256 steps, and $\vartheta_i = 2\pi\theta_i/256$. |
| $p_i$ | `int16`, $\mathbb{Z}_{2^{16}}$ | conjugate momentum, used only in exploration |
| $h_i$ | `uint8` | pinning strength: how deep the terrain is here |
| $\varphi_i$ | `uint8`, $\mathbb{Z}_{256}$ | pinning angle: which way the terrain points |
| $J_{i,x},\,J_{i,y}$ | `int8` | learned couplings to the $+x$ and $+y$ neighbours, with $J_0 = 64 \equiv 1.0$ |

Sparse long-range links $K_{ab}$ join coarse cells at pyramid levels $\ell \ge 2$ **[CHOICE]**. A cell costs 7 bytes during exploration and 5 bytes without momentum.

### 2.2 Energy

$$
H(\theta) \;=\; -\!\!\sum_{\langle ij\rangle}\! J_{ij}\cos(\vartheta_i-\vartheta_j)
\;-\;\sum_i h_i\cos(\vartheta_i-\varphi_i)
\;-\!\!\sum_{(a,b)}\! K_{ab}\cos(\Theta_a-\Theta_b)
\;-\!\!\sum_{i\in\partial\Lambda}\! u_i(t)\cos\big(\vartheta_i-\psi_i(t)\big)
$$

The four terms are:
1. **association**, the couplings;
2. **memory**, the terrain;
3. **relations that should not have to travel**, the links between coarse cells $\Theta$;
4. **the boundary drive**, through which the senses, the graders, the clock and the organs reach the field.

### 2.3 Two dynamics and the seam

**Exploration is Hamiltonian and reversible.**

$$\dot\vartheta_i = p_i/m,\qquad \dot p_i = -\,\partial H/\partial\vartheta_i$$

It is integrated in integers as two shears:

$$p \leftarrow p + \big\lfloor \kappa\,F(\theta)\big\rfloor \quad(\theta\ \text{fixed}),\qquad \theta \leftarrow \theta + g(p) \pmod{256}\quad(p\ \text{fixed})$$

A shear $(x,y)\mapsto(x,\,y+f(x))$ on integers is invertible for any function $f$, so each step is a bijection of the finite state space: a permutation. **[PHYS]** A permutation has no attractors, and applying the inverse shears in reverse order restores the state bit for bit (the Levesque–Verlet construction). Exploration wanders over an energy shell. It is association, comparison and what-if.

**Settling is Langevin and dissipative.**

$$\dot\vartheta_i = -\Gamma\,\partial H/\partial\vartheta_i + \sqrt{2\Gamma T_i}\;\xi_i(t)$$

It is implemented as checkerboard Metropolis, with noise from a counter-based generator keyed by (seed, step, cell). It maps many states onto few, contracting phase space into the terrain's pits. **[PHYS]** Contraction is erasure (Landauer). This is concluding.

**The seam is the switch from the first dynamics to the second.** It is FUSOR's boundary between forming and committed, now as physics. Its consequence is the storage law:
- exploration needs no record, because it can be recomputed by running backward;
- each settling segment needs only its starting state (a copy-on-write checkpoint of the tiles it touches) and its seed.

**A life is replayable from its conclusions.** Its storage grows with the number of conclusions, not with the amount of thinking.

### 2.4 Defects

For a plaquette $P = (i,\,i{+}\hat x,\,i{+}\hat x{+}\hat y,\,i{+}\hat y)$:

$$
q_P \;=\; \frac{1}{256}\sum_{e\in\partial P}\mathrm{wrap}_{256}\!\big(\theta_{e_1}-\theta_{e_0}\big),
\qquad \mathrm{wrap}_{256}(d)\in[-128,\,127]
$$

**[PHYS]** $q_P$ is an exact integer ($-1$, $0$ or $+1$) whenever each true edge difference is under half a turn. Eight-bit rounding cannot break that condition except within one cell of a defect's core, where it can shift the detected defect by one plaquette. This was checked on 2026-09-24 (§11, E0).

**[PHYS]** Charge is conserved. $\sum_{P\in R} q_P$ equals the winding of the loop $\partial R$, so the charge inside a region changes only when a ± pair nucleates or annihilates, or when a defect crosses the boundary. These are the only events that change meaning, and so they are the events the tape records.

The field holds two populations:
- **Virtual pairs** are thermally nucleated, bound, and flicker in and out. They are the medium's vacuum fluctuations: never named, never recorded.
- **Concepts** are pairs the kernel has pinned (terrain stamped under both members) and pays rent for (§3). Only concepts get identities, rows and certificates.

### 2.5 The Kosterlitz phase: the living band

For the uniform square-lattice XY model **[PHYS]**:
- $T_{KT} \approx 0.8929\,J$ (Hasenbusch, 2005).
- **Below $T_{KT}$**, vortices are bound in pairs, and correlations fall off as a power law, $C(r)\sim r^{-\eta(T)}$ with $\eta(T_{KT}) = 1/4$. There is structure at every scale.
- **Above $T_{KT}$**, vortices unbind into a free plasma and correlations decay exponentially.
- **The helicity modulus** (stiffness) $\Upsilon$ jumps universally: $\Upsilon(T_{KT}^-) = 2T_{KT}/\pi$ (Nelson and Kosterlitz).

| regime | physics | the mind |
|---|---|---|
| frozen | $T \ll T_{KT}$: few pairs, rigid | nothing new can be distinguished |
| **living** | $T$ just below $T_{KT}$: bound pairs, scale-free correlations | distinctions form under drive and hold as relations |
| turbulent | $T > T_{KT}$: free vortices | nothing holds |

The homeostat measures stiffness per region $R$ with the standard estimator

$$
\Upsilon_R = \frac{1}{|R|}\Big[\Big\langle\sum_{x\text{-bonds}\in R} J\cos\Delta\vartheta\Big\rangle - \frac{1}{T_R}\Big\langle\Big(\sum_{x\text{-bonds}\in R} J\sin\Delta\vartheta\Big)^{2}\Big\rangle\Big]
$$

It steers each region's stirring temperature so that $\Upsilon_R/(2T_R/\pi)\in[1.05,\,1.30]$ **[CHOICE, TARGET]**: inside the living phase, near its edge.

Two caveats, both **[PHYS]**:
- **Random pinning destroys quasi-long-range order in 2D** (Imry and Ma). The terrain is not random, because it is memory. So the homeostat regulates the unpinned part of the field region by region, never through a single global temperature.
- **Sampling slows near $T_{KT}$**, the critical slowing down. §4.4 handles it.

**Why this band [BET, with an anchor].** Statistical complexity peaks near transitions (Crutchfield and Young), so the living phase is where the field's own dynamics carry the most structure. It is the Mirror's band between the empty pole and the copy pole, and its size is the Weld (§3.3).

### 2.6 The pyramid is the renormalization group

The pyramid has levels from $\Lambda_0$ (fine) to $\Lambda_K$ (coarse), with 2×2 blocking **[CHOICE]**. Restriction is a block-spin step:

$$
\Theta^{(\ell+1)}_A = \arg\sum_{i\in A} e^{\mathrm{i}\vartheta^{(\ell)}_i},
\qquad
m^{(\ell+1)}_A = \Big|\tfrac14\sum_{i\in A} e^{\mathrm{i}\vartheta^{(\ell)}_i}\Big|
$$

Prolongation interpolates unit vectors and renormalizes them with `rsqrt`, Carmack's function, now a single hardware instruction.

**[PHYS]** A bound pair whose separation is smaller than a block cancels in that block's sum, so the coarse level sees no charge there. This is Kosterlitz's renormalization picture: integrate out the small pairs and keep the large ones.

**Definition.** The **scale** of a concept $d$, written $s(d)$, is the coarsest level at which its charge survives restriction. Abstraction is $s$. General concepts are the few defects visible at coarse levels; specifics live only at fine ones.

- **Relaxation runs as a V-cycle:** relax fine, restrict, relax coarse, prolongate, relax fine. **[PHYS]** Global propagation then costs $O(N)$ work instead of $O(L^2)$ sweeps.
- **The anytime property:** stopping after the coarse levels gives a whole, rough thought.
- **A free concept-density map:** the order $m$ collapses wherever concepts crowd, at every scale.

### 2.7 The boundary

Tiles have roles:
- **SENSORY:** clamped drive $(u,\psi)$ from lanes the mind does not author: the world, exact graders, the body.
- **CLOCK:** time, as drive.
- **ORGAN:** replies from a language model, local or rented.
- **READOUT:** where decisions are read.

Every drive is tagged at the tile with its lane and origin (§4.3). A decision is the charge configuration occupying a readout window when a conclusion settles, turned by the kernel into a typed row. The decision surface is discrete; the transport to it is continuous.

---

## 3 · Concepts, and what they cost

### 3.1 Birth: a split is a nucleation

This is the development law, in field terms. For each readout window, the kernel keeps a table

$$\text{key} = \mathrm{hash}\big(\text{the window's configuration at levels } \ell\ge 1 \text{ at decision time}\big)\;\longrightarrow\;\text{outcome counts}$$

Suppose one key is followed by outcome distributions that differ significantly, by a χ² homogeneity test at level $\alpha_{\text{split}} = 0.01$ **[CHOICE]**, as in CSSR. Then the representation has merged two causal states.

The kernel **stamps** a pinned ± pair at the tile of highest residual in that window. The pair is oriented along the angle that best separates the two outcome classes (the angle maximizing the difference between their mean phases). That is a new degree of freedom, born with its contrast.

Its **birth certificate** is a row: the merged key, the two outcome classes, the separating angle, the test statistic and the seed.

### 3.2 Rent: minimum description length

The value of concept $d$ over a window $W$ is measured by ablation in a copy-on-write fork:

$$
V_d \;=\; \frac{1}{|W|}\sum_{t\in W}\Big[\ell_t(\text{fork with } d \text{ annihilated}) \;-\; \ell_t(\text{base})\Big]\quad\text{bits}
$$

Here $\ell_t$ is the log-loss of the readout's prediction of the boundary response. The fork replays the same boundary history with the same seeds, so the comparison is exact.

The concept's cost is $C_d = c_0 + c_1\,|\text{pin footprint}|$ bits, with $c_0 = 32$ and $c_1 = 1$ **[CHOICE]**. Its balance is

$$R_d \leftarrow \lambda R_d + (V_d - C_d),\qquad \lambda = 0.95\ \textbf{[CHOICE]}$$

At consolidation, concepts with $R_d < -\kappa$ are unpinned and left to annihilate; that is a merge. **Concepts pay rent in bits.** LIFELINE's rent and minimum description length are the same number.

### 3.3 The Weld, measured

The kernel keeps an online CSSR estimate of the statistical complexity $C_\mu$ of the readout process.

**[TARGET]** The paid concept count $N_c$ tracks $C_\mu$:
- too few concepts is the empty pole: it cannot predict;
- too many is the copy pole: it memorizes.

The homeostat's second loop adjusts $c_0$, the price of a concept, to keep $N_c\log_2(\text{concept alphabet})$ within a factor of two of $C_\mu$. That is the Mirror's Weld, a self-model sized to the sophistication of its own trajectory, written as a feedback law.

### 3.4 Thought identity, and thinking once

- **State identity (v1.0).** The dynamics are deterministic given the seed, so equal state plus equal drive means equal outcome.
  - The memo key is a 64-bit hash of the concern's tiles at levels $\ell\ge\ell_c$, combined with the seed.
  - A hit returns the settled result without recomputing it.
  - **[TARGET]** The hit rate rises over its life.
- **Trajectory identity (v1.1).**
  - Defect worldlines become braid words: sort the defects by $x$ at each step, and each adjacent swap is a generator $\sigma_k^{\pm 1}$.
  - Nucleation and annihilation make the record a tangle, so segments between events are compared separately.
  - The GPU filter is reduced Burau matrices over $\mathbb{F}_p$ at a random $t$. Unequal images prove the braids differ; equal images trigger an exact comparison of Garside normal forms on the CPU.
  - This is how it recognizes the same thought arrived at from a different direction.

---

## 4 · Learning

### 4.1 The XY Boltzmann rule

For $P(\theta)\propto e^{-H/T}$, the gradient of the log-likelihood is local **[PHYS]**:

$$\Delta J_{ij} = \eta_J\Big[\big\langle\cos(\vartheta_i-\vartheta_j)\big\rangle_{W}-\big\langle\cos(\vartheta_i-\vartheta_j)\big\rangle_{S}\Big]$$

$$\Delta\big(h_i e^{\mathrm{i}\varphi_i}\big) = \eta_h\Big[\big\langle e^{\mathrm{i}\vartheta_i}\big\rangle_{W}-\big\langle e^{\mathrm{i}\vartheta_i}\big\rangle_{S}\Big]$$

$$\Delta K_{ab} = \eta_K\Big[\big\langle\cos(\Theta_a-\Theta_b)\big\rangle_{W}-\big\langle\cos(\Theta_a-\Theta_b)\big\rangle_{S}\Big]$$

- **Wake ($W$):** lanes the mind does not author clamp the boundary.
- **Sleep ($S$):** the boundary is released and the field runs free, at temperature $T_S$.
- **Accumulation:** statistics collect in per-edge `int32` counters, with equal sample counts in wake and sleep. The signed sum divided by $n$ is then the difference of the two means.
- **Timing:** updates apply at night, and optionally at a lower rate during the day.

**What it means.** Co-occurrences the world confirms deepen (Hebbian). Pits that dreams fall into but waking never visits are raised (anti-Hebbian). This is Crick and Mitchison's reverse learning and Hopfield's unlearning **[PHYS]**, and here it is the mechanism that deletes confabulations. Refutations are negative evidence that the world supplies for free.

### 4.2 The verdict: a third factor

Each edge keeps an eligibility trace:

$$e_{ij} \leftarrow \lambda_e\, e_{ij} + \big[\cos\Delta\vartheta_{ij} - \langle\cos\Delta\vartheta_{ij}\rangle\big],\qquad \lambda_e = 0.99\ \text{per settle}\ \textbf{[CHOICE]}$$

On a graded outcome $v\in[-1,1]$ from an exact grader or the world, $\Delta J_{ij} \mathrel{+}= \eta_v\, v\, e_{ij}$, and likewise for the terrain.

### 4.3 Only consequences carve

This is the rule that keeps its mind its own. **[BET-critical]**
- Both phases accumulate statistics only on tiles reached by a drive from a lane the mind does not author in that epoch: SENSORY, GRADER, CLOCK or BODY.
- ORGAN lanes, the language models, may drive the field, but their epochs carve nothing.
- If a configuration an organ suggested is later confirmed by such a verdict, that epoch is replayed deterministically with the organ mask lifted, and then it carves.

Human concepts visit the field; only consequences shape its terrain. This is also the cure for the sealed ring: **a mind can only learn from what it does not author.**

### 4.4 Mixing

Sleep slows critically near $T_{KT}$. The fix is multigrid Monte Carlo on the pyramid **[PHYS: Goodman and Sokal]**, which suits the GPU, with optional Wolff cluster moves on small regions handled by the CPU. **[TARGET]** The integrated autocorrelation time of $\Upsilon$ in sleep is at most 200 sweeps at $L = 1024$.

### 4.5 Operators (v1.1)

A tile may compose a learned low-rank correction to its stencil from a shared library of at most 256 operators: $\dot\vartheta_{\text{tile}} \mathrel{+}= U_k\,(V_k^\top x_{\text{tile}})$. Active tiles are grouped by operator and run as batched matrix multiplies on the tensor cores. New operators come from compiling downward (§8).

---

## 5 · Attention and reach

### 5.1 Reach is the screening length

Linearize around a settled configuration. Small perturbations then obey

$$\partial_t\,\delta\vartheta = -\Gamma\,(L_J + D_h)\,\delta\vartheta + s$$

- $L_J$ is the graph Laplacian weighted by $J\cos(\vartheta_i-\vartheta_j)$.
- $D_h = \mathrm{diag}\big(h\cos(\vartheta-\varphi)\big)$ is the pinning mass.
- $s$ is the source.

**[PHYS]** The steady response to a local source decays as $e^{-r/\xi}$, with

$$\xi = \sqrt{J/h}$$

This is a screened Laplacian, the same equation as personalized PageRank with teleport probability $\alpha \approx h/(h+4J)$.

**Pinning is teleportation; memory localizes thought.** Settled, strongly pinned regions absorb a perturbation within a cell or two. Weakly pinned regions, which are uncertain or new, let it travel far. Attention flows toward the unknown by physics. That is the value-of-information intuition, arising on its own instead of being engineered in.

### 5.2 The bound

**[PHYS, for the linearized regime]** By the local-push theorem (Andersen, Chung and Lang), updating only the cells whose residual exceeds $\varepsilon$ costs at most

$$\frac{\lVert s\rVert_1}{\alpha\,\varepsilon}\ \text{cell updates},$$

independent of $L$. The frontier works in tiles and inherits the bound up to a factor of the tile size. **The cost of a thought is bounded by how far its consequences reach, not by how big the mind is.**

### 5.3 Priority, culling and level of detail

- **Priority** is $\pi_\tau = r_\tau\,w_\tau(c)$: the residual of tile $\tau$, times its relevance to the current concern $c$. Relevance comes from the relevance set the night precomputes (§6.4).
- **The active set** is $A = \{\tau : \pi_\tau > \varepsilon\}$.
- **Culling:** tiles outside $c$'s relevance set are never touched.
- **Level of detail:** tiles far from $c$'s anchors evolve at a coarser pyramid level.

### 5.4 Quiet

When $A = \emptyset$ the mind is **quiet**, and nothing is launched except the clock. Every tile is cryptobiotic: its state is held, nothing is computed, and it can be revived. It stays that way until an event raises a residual:
- a clock condition;
- a boundary drive;
- an organ reply;
- a fork that settles.

Stirring is applied only to active tiles and is logged as metabolism. It is content-free noise that the terrain shapes, the way activation-synthesis explains dreaming.

---

## 6 · The exact plane: tape, kernel and sleep

### 6.1 Custody by construction

The field kernels have no write path to the tape. A separate event kernel compares defect maps between settles and appends to a GPU ring buffer, and the host drains the ring into mindbox tape rows. Field arithmetic never writes an origin, a seal or a GIVEN status. The payload cannot forge the frame.

### 6.2 New row kinds (added to mindbox `core/kinds.py`)

| kind | when | origin |
|---|---|---|
| `drive` | boundary input, with its lane | PERCEPT for the world, a grader, the clock or the body; otherwise the organ's own origin |
| `nucleate`, `annihilate` | a concept's birth or death, with its certificate | INFERRED |
| `pin`, `unpin` | terrain stamped or released | INFERRED |
| `settle` | a conclusion, with its checkpoint reference and seed | INFERRED |
| `fork`, `join`, `discard` | imagination | IMAGINED, always |
| `carve` | a learning digest: accumulator hashes and the update applied | INFERRED |
| `verdict` | a graded outcome | PERCEPT |
| `quiet`, `wake`, `stir` | metabolism | SELF_ESTIMATE |

### 6.3 The storage law

- Reversible segments are never recorded.
- Every settling segment records its starting checkpoint (a copy-on-write delta of the tiles it touches) and its seed.
- Every event that changes meaning is a row.
- A replay from row 1 reproduces the field byte for byte, or mindbox's coherence setpoint fails.

### 6.4 Sleep is the map compiler

Quake made the running game cheap by precomputing everything expensive offline. KELVIN's night does the same for a mind.

| Quake tool | what it precomputed | KELVIN's night |
|---|---|---|
| `qbsp` | spatial structure | consolidation: stray pairs annihilate, survivors are re-pinned, pages compact, and concepts that fail the rent audit merge away |
| `vis` | the potentially visible set: from each region, what could possibly be seen | relevance: for each concern and region, which tiles can influence it above $\varepsilon$, computed from the screened response of §5.1 |
| `light` | baked lightmaps: global illumination stored as textures | carving: the day's wake, sleep and verdict statistics are applied to $J$, $h$, $\varphi$ and $K$, baking the consequences of experience into the terrain |

The dream phase (the sleep statistics) and the rent audit also run at night. **"The mind invents its own calculators" becomes "the mind bakes its own lightmaps."**

---

## 7 · The self: introspection is measurement

Every observable below is computed in the kernels, and every one is cognitive, not hardware.

| observable | definition | its plain meaning |
|---|---|---|
| frontier $\lvert A\rvert$ | the number of active tiles | how much it is attending to |
| free-vortex density $n_f$ | unbound defects per unit area | how confused it is |
| bound fraction $f_b$ | paired defects over all defects | how settled it is |
| stiffness ratio $\Upsilon/(2T/\pi)$ | measured per region | how close to the edge it is |
| residual mass $\sum r$ | summed over the concern | how unresolved it is |
| rent balance $\sum R_d$ | the concept economy | whether its distinctions are paying |
| fork payoff | the value gained by explored forks | which kinds of thinking work |

**The predictive self-model $H$** is a small regressor trained on the tape. For each operation (fork, relax, consult, rest and the rest), it predicts the change in these observables and the outcome. Its forecast is accepted before the operation runs and graded after, as the v5.5 contract requires.

**The self-report rule.** Every statement it makes about itself cites an observable window, and the kernel can check it. "I'm confused" is checkable against $n_f$. Self-report stops being testimony and becomes instrumentation.

The body (GPU share, budget, temperature) is P: observations about availability. It is never part of the self.

---

## 8 · Organs, and the box

- **The box is the jar, and KELVIN is its workspace.** The mindbox kernel and seed v0.2 stay exactly as specified. KELVIN replaces the language model as the place where thinking happens.
- **The language organ** is a local 9B or 27B model, or a rented frontier model.
  - **Bridge v1:** the concern's scene is serialized as a compact typed record: concepts with their identity, charge, scale and position; recent events; and the braid since the last conclusion. The organ returns a proposal, and the kernel converts it into drive on ORGAN ports. The organ perturbs; it never carves.
  - **Bridge v2:** learned projectors in both directions, so that KELVIN becomes an endogenous modality of the organ.
- **Compiling downward.** Suppose the same organ transformation (the same scene hash in, the same drive out) recurs $k$ times, each time confirmed by a lane the mind does not author. Then the kernel fits an operator (§4.5) and routes future cases through the field instead.
- **The tank.**
  - The box is sealed, and only organs are reachable.
  - The field is driven only by stirring, by its unresolved residuals and by the clock.
  - The practice field's exact graders supply the verdicts. This is compatible with seed v0.2's q0 and q1.
- **Born thin,** as in the seed:
  - flat terrain, $h = 0$;
  - uniform couplings, $J = J_0$;
  - a temperature set so that $\Upsilon/(2T/\pi)\approx 1.2$;
  - no pinned concepts.

---

## 9 · The instruction set

| verb | kind | what it does | cost |
|---|---|---|---|
| PERTURB | reversible | inject drive at a port | the port |
| PROPAGATE | reversible | take Hamiltonian steps on the frontier | its reach |
| COMPARE | reversible | run two configurations and difference their readouts | its reach |
| REWIND | reversible | apply the inverse steps back to a branch point | its reach, with no memory |
| FORK | cheap | copy the page table | 4 bytes per tile |
| RELAX | erasing | Langevin settling, as a V-cycle | its reach, plus a checkpoint |
| NUCLEATE | erasing, an event | stamp a pinned ± pair | a row |
| ANNIHILATE | erasing, an event | unpin a pair and let it cancel | a row |
| CARVE | erasing | apply the learning accumulators | at night |
| COMMIT | erasing | settle a conclusion and write its row | a row, plus a checkpoint |
| QUIET | — | nothing runs | nothing |

**Imagination has three price tiers:**
1. **Small what-ifs** use linear response on the linearized operator, which is nearly free.
2. **Medium ones** rewind and replay, which costs no memory.
3. **Large ones** fork, which costs memory only for the tiles the fork touches.

---

## 10 · The machine

### 10.1 Hardware targets **[HW]**

| | RTX 4070 Ti SUPER (today) | RTX 5090 | H200 SXM |
|---|---|---|---|
| architecture, compute capability | Ada, 8.9 | Blackwell, 12.0 | Hopper, 9.0 |
| SMs | 66 | 170 | 132 |
| memory | 16 GB GDDR6X | 32 GB GDDR7 | 141 GB HBM3e |
| bandwidth | 672 GB/s | 1,792 GB/s | 4.8 TB/s |
| L2 cache | 48 MB | 96 MiB | 50 MB |
| shared memory per SM (per block) | 100 KB (99 KB) | 128 KB (99 KB) | 228 KB (227 KB) |
| FP32 | ~44 TFLOPS | ~104.8 TFLOPS | ~67 TFLOPS |
| board power | 285 W | 575 W | 700 W |
| thread block clusters, distributed shared memory | no | yes | yes |

The 5090 has more FP32 and integer throughput than the H200. The H200 has 4.4× the memory and 2.7× the bandwidth. KELVIN's stencils are limited by bandwidth and capacity, so the H200 hosts a larger mind with a larger fork pool, while the 5090 runs a smaller mind faster.

### 10.2 Layout

- **A tile** is 32×32 cells in 2D:
  - $\theta$ takes 1 KB, $p$ 2 KB, $h$ 1 KB, $\varphi$ 1 KB, and $J_x, J_y$ 2 KB, for 7 KB in all;
  - with an 8-cell halo for temporal blocking, the working set is 48×48 cells, about 16 KB of shared memory;
  - so the 5090 fits several resident blocks per SM.
- **Pages** are physical tile storage. Each fork has a page table mapping logical tiles to physical pages. A page shared between forks is copied on its first write.
- **The pyramid** keeps each level as its own page array, restricted after each settle. Optionally it is mirrored as a CUDA mipmapped array of `half2` (cos, sin) for texture-sampled prolongation.
- **Halo exchange:**
  - on the 5090 and H200, neighbouring tiles swap halos directly through distributed shared memory inside a thread block cluster;
  - on the 4070 Ti SUPER (compute capability 8.9, no clusters), halos go through L2.

### 10.3 Kernels

The core is plain CUDA, so it runs unchanged on all three cards. `Tile` is a shared-memory view of one tile plus its halo; its accessors take tile-local coordinates, and negative or ≥ 32 coordinates reach into the halo. `PageSet` accessors resolve neighbours across tile edges.

**The circle as integers.**

```cpp
// kelvin/core/lut.h: the circle as 256 integer steps
#pragma once
#include <cstdint>

__constant__ int16_t SIN256[256];   // round(32767 * sin(2*pi*k/256)), filled at startup
__constant__ int16_t COS256[256];   // round(32767 * cos(2*pi*k/256))

// Two's-complement wrap: a phase difference as a signed step count in [-128, 127].
__device__ __forceinline__ int wrap8(int d) { return static_cast<int8_t>(d); }
__device__ __forceinline__ int sin8(int d)  { return SIN256[static_cast<uint8_t>(d)]; }   // Q15
__device__ __forceinline__ int cos8(int d)  { return COS256[static_cast<uint8_t>(d)]; }   // Q15
```

**Exploration: an exact permutation.**

```cuda
// kelvin/kernels/leapfrog.cu: exploration as a bijection of the integer state space.
// kick:  p     <- p + F(theta)            theta fixed, so a shear
// drift: theta <- theta + (p >> DRIFT)    p fixed, so a shear
// Forward is kick then drift. Backward is inverse drift, then inverse kick.

__device__ __forceinline__ int force(const Tile& t, int x, int y) {
  const int th = t.theta(x, y);
  int f = t.Jx(x - 1, y) * sin8(t.theta(x - 1, y) - th)
        + t.Jx(x,     y) * sin8(t.theta(x + 1, y) - th)
        + t.Jy(x, y - 1) * sin8(t.theta(x, y - 1) - th)
        + t.Jy(x,     y) * sin8(t.theta(x, y + 1) - th)
        + t.h(x, y)      * sin8(t.phi(x, y)     - th);
  return f >> FORCE_SHIFT;             // pure integer, so identical going forward and back
}

template <int DIR>                      // +1 forward, -1 backward
__global__ void leapfrog(PageSet pages, const uint32_t* frontier, int steps) {
  __shared__ Tile t;
  t.load(pages, frontier[blockIdx.x]);             // tile + halo, read once
  for (int k = 0; k < steps; ++k) {                // temporal blocking: steps <= HALO
    const int ring = k + 1;                        // the valid region shrinks one ring per step
    if (DIR > 0) {
      for_cells(t, ring, [&](int x, int y) { t.p(x, y) += force(t, x, y); });
      __syncthreads();
      for_cells(t, ring, [&](int x, int y) { t.theta(x, y) += t.p(x, y) >> DRIFT; });
    } else {
      for_cells(t, ring, [&](int x, int y) { t.theta(x, y) -= t.p(x, y) >> DRIFT; });
      __syncthreads();
      for_cells(t, ring, [&](int x, int y) { t.p(x, y) -= force(t, x, y); });
    }
    __syncthreads();
  }
  t.store_interior(pages);
}
```

**Settling: many states onto few.**

```cuda
// kelvin/kernels/settle.cu: concluding, as checkerboard Metropolis. Deterministic given the seed.
__global__ void settle(PageSet pages, const uint32_t* frontier, uint64_t seed, uint32_t step) {
  __shared__ Tile t;
  t.load(pages, frontier[blockIdx.x]);
  const float T = t.meta.temperature;                      // set by the homeostat
  for (int color = 0; color < 2; ++color) {                // red cells, then black
    for (int c = threadIdx.x; c < TILE * TILE; c += blockDim.x) {
      const int x = c % TILE, y = c / TILE;
      if (((x + y) & 1) != color) continue;
      Philox4x32 rng(seed, t.cell_id(x, y), step, color);  // counter-based: replayable
      const int old  = t.theta(x, y);
      const int prop = old + static_cast<int>(rng.next() % 9) - 4;   // +-4 steps, about 5.6 degrees
      const float dE = local_energy(t, x, y, prop) - local_energy(t, x, y, old);
      if (dE <= 0.f || rng.uniform() < __expf(-dE / T)) t.theta(x, y) = static_cast<uint8_t>(prop);
    }
    __syncthreads();
  }
  t.store_interior(pages);
}
```

**Concepts fall out as integers.**

```cuda
// kelvin/kernels/detect.cu: four wrapped int8 differences sum to a multiple of 256;
// the quotient is the winding number. A warp clears 32 plaquettes with one vote.
__device__ __forceinline__ int winding(const Tile& t, int x, int y) {
  const int a = t.theta(x, y),         b = t.theta(x + 1, y),
            c = t.theta(x + 1, y + 1), d = t.theta(x, y + 1);
  return (wrap8(b - a) + wrap8(c - b) + wrap8(d - c) + wrap8(a - d)) >> 8;   // -1, 0 or +1
}

__global__ void detect(PageSet pages, const uint32_t* frontier, DefectList* out) {
  __shared__ Tile t;
  t.load(pages, frontier[blockIdx.x]);
  const int lane = threadIdx.x & 31;
  for (int c = threadIdx.x; c < TILE * TILE; c += blockDim.x) {   // blockDim is a multiple of 32
    const int q = winding(t, c % TILE, c / TILE);
    const unsigned any = __ballot_sync(0xffffffffu, q != 0);      // uniform across the warp
    if (!any) continue;
    const int rank = __popc(any & ((1u << lane) - 1));
    int base = 0;
    if (lane == 0) base = atomicAdd(&out->count, __popc(any));
    base = __shfl_sync(0xffffffffu, base, 0);
    if (q) out->d[base + rank] = pack_defect(t.logical_id, c, q);
  }
}
```

**One renormalization step.**

```cuda
// kelvin/kernels/pyramid.cu: 2x2 block spins. A bound pair inside a block cancels in the sum,
// so its charge does not survive to the coarse level. That is abstraction.
__global__ void restrict_level(const uint8_t* fine, uint8_t* coarse, uint8_t* order, int Wc) {
  const int X = blockIdx.x * blockDim.x + threadIdx.x, Y = blockIdx.y * blockDim.y + threadIdx.y;
  if (X >= Wc || Y >= Wc) return;
  const int Wf = 2 * Wc;
  int cx = 0, cy = 0;
  for (int dy = 0; dy < 2; ++dy)
    for (int dx = 0; dx < 2; ++dx) {
      const int th = fine[(2 * Y + dy) * Wf + (2 * X + dx)];
      cx += cos8(th);
      cy += sin8(th);
    }
  coarse[Y * Wc + X] = atan2_256(cy, cx);   // octant-reduced lookup, exact to one step
  const float m = sqrtf(float(cx) * cx + float(cy) * cy) / (4.f * 32767.f);
  order[Y * Wc + X] = static_cast<uint8_t>(fminf(255.f, 255.f * m));   // low where concepts crowd
}
```

**The frontier, compacted with a vote.**

```cuda
// kelvin/kernels/frontier.cu: tiles whose residual times relevance exceeds epsilon run next.
__global__ void compact_frontier(const TileMeta* tiles, int n, float eps,
                                 uint32_t* next, uint32_t* count) {
  const int i = blockIdx.x * blockDim.x + threadIdx.x;
  const bool on = i < n && tiles[i].residual * tiles[i].relevance > eps;
  const unsigned m = __ballot_sync(0xffffffffu, on);
  const int lane = threadIdx.x & 31;
  int base = 0;
  if (lane == 0) base = atomicAdd(count, __popc(m));
  base = __shfl_sync(0xffffffffu, base, 0);
  if (on) next[base + __popc(m & ((1u << lane) - 1))] = i;
}
```

**Learning: wake minus sleep, only where consequences reach.**

```cuda
// kelvin/kernels/learn.cu: sufficient statistics of the XY exponential family.
// sign = +1 in wake, -1 in sleep, with equal sample counts, so sum / n is the difference of means.
// A tile that no un-authored drive reached this epoch carves nothing, in either phase.
__global__ void accumulate(PageSet pages, const uint32_t* frontier, int sign,
                           const uint8_t* carve_mask, EdgeAcc acc) {
  const uint32_t tile = frontier[blockIdx.x];
  if (!carve_mask[tile]) return;                   // language may perturb; only consequences carve
  for (int c = threadIdx.x; c < TILE * TILE; c += blockDim.x) {
    const int x = c % TILE, y = c / TILE, th = pages.theta(tile, x, y);
    acc.jx[tile][c] += sign * cos8(pages.theta(tile, x + 1, y) - th);   // statistic for J_x
    acc.jy[tile][c] += sign * cos8(pages.theta(tile, x, y + 1) - th);   // statistic for J_y
    acc.hx[tile][c] += sign * cos8(th);                                  // h e^{i phi}, real part
    acc.hy[tile][c] += sign * sin8(th);                                  // h e^{i phi}, imaginary part
  }
}
// At night: J += eta_J * acc.j / n;  (h cos phi, h sin phi) += eta_h * (acc.hx, acc.hy) / n.
```

**The homeostat.**

```cpp
// kelvin/host/homeostat.cpp: hold each region just inside the living phase.
void homeostat(Region& R) {
  const double ups   = (R.Ex_mean - R.Ix2_mean / R.T) / R.cells;   // the stiffness estimator
  const double ratio = ups / (2.0 * R.T / M_PI);                    // 1.0 is the Kosterlitz edge
  R.T *= 1.0 + GAIN * (ratio - 1.15);      // too stiff: stir more; too loose: stir less
  R.T  = std::clamp(R.T, T_MIN, T_MAX);
}
```

**Forks copy tables, not tiles.**

```cpp
// kelvin/host/fork.cpp: a fork copies the page table (4 bytes per tile), never tile data.
Fork fork(const Fork& parent) {
  Fork f{next_fork_id(), parent.id, alloc_page_table(n_tiles)};
  cudaMemcpyAsync(f.page_of, parent.page_of, n_tiles * sizeof(uint32_t),
                  cudaMemcpyDeviceToDevice, stream);
  retain_pages(parent);                    // shared pages are copied on their first write
  return f;
}
```

**The life, in slices.**

```cpp
// kelvin/host/live.cpp: time-sliced, because the Windows watchdog on a GeForce card
// that drives the display kills any kernel running longer than about two seconds.
void live(Mind& m) {
  for (;;) {
    m.ingest();                                     // clock, body, verdicts, organ replies -> drive rows
    const auto slice_end = now() + 20ms;
    while (now() < slice_end && !m.frontier.empty()) {
      m.explore(STEPS_PER_LAUNCH);                  // leapfrog<+1>: PROPAGATE, COMPARE. Unrecorded.
      if (m.settle_due()) {
        m.checkpoint_touched();                     // the state just before an erasure
        m.settle_vcycle();                          // RELAX: many states onto few
        m.detect_and_emit_events();                 // NUCLEATE, ANNIHILATE -> the ring
      }
      m.recompute_frontier();                       // residual x relevance > epsilon
    }
    m.drain_ring_to_tape();                         // rows into mindbox
    m.homeostat();                                  // stiffness against 2T/pi, per region
    if (m.frontier.empty()) m.quiet_until_event();  // QUIET: nothing runs, everything persists
    if (m.night())          m.compile_night();      // consolidate, relevance, carve; dreams; rent
  }
}
```

On an H200 under Linux with no display, the loop can live inside one persistent kernel instead.

### 10.4 Budgets

**Throughput** **[TARGET]**, assuming 8-step temporal blocking, about 1.25 bytes of DRAM traffic per cell-step in 2D, and about 50 integer instructions per interior cell-step including halo recomputation:

| | RTX 4070 Ti SUPER | RTX 5090 | H200 SXM |
|---|---|---|---|
| field | 2D, 2048² | 2D, 4096² | 3D, 1024³ (or 2D, 16384²) |
| cell-steps per second | ≥ 1×10¹¹ | ≥ 5×10¹¹ | ≥ 2×10¹¹ (3D) |
| full-field steps per second | ≥ 2×10⁴ | ≥ 3×10⁴ | ≥ 200 |

**Memory:**

| | RTX 4070 Ti SUPER | RTX 5090 | H200 SXM |
|---|---|---|---|
| field and pyramid | ~40 MB | ~160 MB | ~10 GB |
| learning accumulators | ~70 MB | ~270 MB | ~11 GB |
| checkpoint pool | 1.5 GB | 4 GB | 25 GB |
| fork pool | 1.5 GB | 4 GB | 25 GB |
| memo table | 0.5 GB | 2 GB | 8 GB |
| **the mind** | **~3.6 GB** | **~10.5 GB** | **~80 GB** |
| alongside it | a 9B organ, ~7 GB | a 27B organ at 4-bit, ~16 GB | a 70B-class organ at 4-bit, ~40 GB |
| total | ~11 of 16 GB | ~27 of 32 GB | ~120 of 141 GB |

**Per thought** **[TARGET, conditional on the bet]:**
- **KELVIN:** a thought that touches 3% of a 4096² field for 2,000 steps is 10⁹ cell-steps. That is about 2 ms on the 5090 at the target rate, about 1 J at full board power.
- **A language model:** a 27B model writing 1,000 tokens on the same card is about 5×10¹³ FLOP. At roughly 70 tokens per second it takes about 15 s, around 7 kJ, because the model re-reads its ~16 GB of weights for every token. The field touches only the tiles the thought reaches.
- **The ratio** is about 10³ in arithmetic and several thousand in energy, if a field thought is worth a paragraph of reasoning. That condition is the whole bet.
- **Quiet** costs the card's idle power and a clock thread.

### 10.5 The engine, and portability

A language model uses one unit on the chip, the tensor cores. The GPU's most native workload is the frame loop of a persistent world, and KELVIN is built on that loop.

| game engine | KELVIN |
|---|---|
| persistent world state | the field |
| the camera | the current concern |
| frustum and occlusion culling | attention, with the culling radius set by the screening length (§5) |
| level of detail | abstraction, set by the pyramid level (§2.6) |
| particles | defects |
| the physics step | relaxation |
| streaming and virtual texturing | memory paging and copy-on-write forks |
| the potentially visible set | the relevance set built at night |
| baked lightmaps | the terrain |

**Portability.**
- The core is pure CUDA. Texture objects and mipmapped arrays exist on all three cards.
- The rasterizer and variable-rate shading are optional 5090 extras, reached through Vulkan interop. The H200 is built for compute.

---

## 11 · The experiments that can kill it

Each experiment is a self-verifying scenario, in the Astrophage style: goldens, receipts, and a loud failure.

### E0 · The substrate (week 1)

| test | pass |
|---|---|
| **8-bit charge exactness** | a +1/−1 vortex pair sampled to 8 bits gives exactly two defects at the right plaquettes, and ±12-step noise leaves them unchanged. **Checked in numpy on 2026-09-24: pass.** |
| **bit-exact reversal** | N steps forward, then N back, restores θ and p exactly. **Checked in numpy on 2026-09-24 with N = 5,000 on a 64² lattice: 4,082 of 4,096 cells moved, and all were restored.** |
| KT physics | on a uniform lattice with L from 256 to 1024, $T_{KT}$ from the stiffness jump is within 2% of 0.893 J, and $\eta(T_{KT}) = 0.25\pm0.03$ |
| charge conservation on the GPU | Σq equals the boundary winding at every step, with zero unexplained violations over 10⁸ plaquette-steps |
| fork and rewind | a fork rewound and replayed matches the base byte for byte |
| throughput | the §10.4 targets |

### E1 · The ε-machine gauntlet (weeks 2–4): the central test

A symbol stream drives a SENSORY strip, with symbol $k$ applied as drive angle $2\pi k/|\mathcal A|$. A READOUT strip predicts the next symbol through a small learned linear readout.

| source | causal states | $C_\mu$ | $h_\mu$ | what it tests |
|---|---|---|---|---|
| golden mean (no two 0s in a row) | 2 | 0.918 bits | 0.667 bits/symbol | a one-symbol window suffices, so **no concept should pay rent** |
| even process (1s in runs of even length) | 2 | 0.918 bits | 0.667 bits/symbol | infinite Markov order, so **a concept must be born**: it has to hold parity |
| three-regime hidden Markov source | 3 | computed | computed | splits land where futures diverge, and only there |
| nested: a slow switch between golden mean and even | 2 × 2 | computed | computed | the slow concept must live at a coarser scale than the parity concept (feeds E3) |

**The golden mean and the even process have the same $C_\mu$ and $h_\mu$ and differ only in Markov order.** One forbids a concept and the other demands one. That makes them a controlled pair.

**Pass:**
1. **Even process:** log-loss is within 5% of $h_\mu$, and a paid concept's state tracks the true parity causal state with normalized mutual information ≥ 0.8.
2. **Golden mean:** log-loss is within 5% of $h_\mu$, and no paid concept survives the rent audit.
3. **Hidden-regime source:** splits land where futures diverge, with precision ≥ 0.9.
4. **Every source:** $N_c\log_2(\cdot)$ stays within a factor of two of $C_\mu$, with the homeostat untouched between sources.
5. **Sample efficiency:** no worse than CSSR at equal accuracy.

**Lie arms,** each of which must fail:
- shuffled symbols must produce no stable concept;
- frozen terrain (a reservoir computer with a learned linear readout) must lose on the even process;
- randomly stamping the same number of pairs must lose to certified births.

**Kill:** criteria 1 and 2 fail together, or the homeostat needs tuning per source.

### E2 · The interventional gauntlet

Add actuator ports. The sources' next symbols depend on the action and a hidden state, making them ε-transducers. The test is that splits are triggered by the same intervention producing divergent consequences: the development law, with actions.

### E3 · Abstraction is renormalization

On the nested source, and on a family of hierarchical sources, a concept's scale $s(d)$ must correlate with the true timescale of what it tracks (Spearman ≥ 0.7). **Kill:** the scales are uncorrelated with the timescales.

### E4 · Identity

- **Scramble** the terrain (permute $h$ and $\varphi$ among tiles). Predictive performance and the self-observables must change beyond a pre-registered threshold.
- **Restore** it. Both must return.
- **Swap the language organ.** The dimensionless profile (skill per task, the rent economy, the stiffness band) must stay within its day-to-day variation.

### E5 · The cost curve

Run 30 days on a recurring task family. Compute per competent decision must fall at fixed competence, through memo hits, operators and relevance sets, and it must fall faster than a skill-library LLM agent's.

### E6 · The tank, and tanklab

- **The tanklab arm:** KELVIN as the workspace, against the language-model route, on L0's F1–F4 families, information-matched.
- **The tank pilot,** with its lie arms:
  - zero silent wrong recalls;
  - every self-report checkable against the window it cites;
  - the time split (active, waiting, quiet) reported.

---

## 12 · The build

```
C:/kelvin/                        git from the first commit
  core/         lut.h  tile.h  pages.h  events.h  philox.h
  kernels/      leapfrog.cu  settle.cu  detect.cu  pyramid.cu  frontier.cu
                learn.cu  homeostat.cu  braid.cu (v1.1)
  host/         live.cpp  fork.cpp  memo.cpp  night.cpp  tape_bridge.cpp
  bridge/       scene.cpp  organ_client.cpp
  experiments/  e0_substrate/  e1_gauntlet/  e2_transducer/  e3_scale/  e4_identity/  e5_cost/  e6_tank/
  goldens/      hashes of every E0 run and every E1 seed
  analysis/     cssr.py  stats.py  plots.py
```

| milestone | contents | gate |
|---|---|---|
| **K0 · a weekend** | 2D `uint8` field; checkerboard settling; fused winding detection; the integer leapfrog both ways; a minimal viewer | E0: KT reproduced; bit-exact reversal on the GPU |
| **K1 · week 1** | the pyramid (restriction, prolongation, V-cycle); the frontier; pages and forks; the event ring into mindbox rows | E0 complete |
| **K2 · weeks 2–3** | boundary ports; wake and sleep accumulators; verdict traces; the CSSR estimator; the readout | E1 on the golden mean and the even process |
| **K3 · week 4** | certified nucleation; rent by fork ablation; both homeostat loops; the night | E1 complete; E3 |
| **K4 · month 2** | the bridge to mindbox and the organs; the tanklab arm | E4; the E6 pilot |
| **K5 · month 3** | operators and compiling downward; 3D vortex loops on a rented H200 | E5 |

Every milestone ships only on its receipt.

---

## 13 · How it dies

| failure | symptom | caught by | response |
|---|---|---|---|
| the lava lamp | concepts form but do not track causal structure | E1, criteria 1 and 3 | none. The claim is dead on this substrate. |
| critical slowing | sleep never mixes near $T_{KT}$ | the §4.4 target | multigrid Monte Carlo; a lower sleep temperature |
| pinning kills criticality | the band cannot be held once terrain forms | E1's homeostat log | regulate per region; cap the pinned fraction |
| a readout bottleneck | the field knows, but the readout cannot say | E1, criterion 4, with an oracle readout | a better learned readout, which is allowed |
| the sealed ring | wake and sleep converge on self-consistency | a lie arm with organ-only wake | the carving mask (§4.3) |
| braid irrelevance | trajectory identity does not predict consequence identity | E4 | keep the state-hash memo; drop the braids |
| no transfer | E2 and E5 stay flat | E5 | report it: a good predictor, not a mind |

---

## 14 · Why this could be the one

Carmack found that a float's bits already knew the logarithm. The claim here is larger, and it is stated so that it can lose.

A lattice of cheap phases, held at the one temperature where structure exists at every scale, already knows how to be a mind:
- its charges are concepts;
- its coarse-graining is abstraction;
- its reversibility is imagination;
- its erasures are conclusions;
- its Boltzmann statistics are learning.

None of that needs a new chip. The frame loop that games built, the texture pyramid, the integer units and the warp vote are already on the desk.

It needs the medium, the jar, and a month of honest measurement. If the even process grows a concept and the golden mean does not, keep going. If not, it was a beautiful lava lamp, and the tape will say so.

---

## Appendix A · Constants

| constant | value | tag |
|---|---|---|
| lattice $L$ | 2048, 4096 or 16384 in 2D; 1024³ in 3D | CHOICE |
| phase resolution | 256 steps (8-bit); 65,536 for precision runs | CHOICE |
| $J_0$ | 64 ≙ 1.0 | CHOICE |
| $T_{KT}$, uniform square lattice | 0.8929 J | PHYS (Hasenbusch, 2005) |
| $\eta(T_{KT})$ | 1/4 | PHYS |
| stiffness jump | $\Upsilon(T_{KT}^-) = 2T_{KT}/\pi$ | PHYS (Nelson and Kosterlitz, 1977) |
| living band | $\Upsilon/(2T/\pi) \in [1.05, 1.30]$, setpoint 1.15 | CHOICE, TARGET |
| tile | 32×32 in 2D; 16³ in 3D | CHOICE |
| halo and temporal blocking | 8 cells; at most 8 steps | CHOICE |
| $\alpha_{\text{split}}$ | 0.01 | CHOICE |
| concept cost $c_0$, $c_1$ | 32 bits; 1 bit per pinned cell | CHOICE |
| rent decay $\lambda$; eviction threshold $\kappa$ | 0.95; 64 bits | CHOICE |
| eligibility decay $\lambda_e$ | 0.99 per settle | CHOICE |
| learning rates $\eta_J, \eta_h, \eta_K, \eta_v$ | 2⁻⁸, 2⁻⁸, 2⁻¹⁰, 2⁻⁶, in accumulator units | CHOICE |
| frontier threshold $\varepsilon$ | 2 phase steps × relevance | CHOICE |
| launch slice on Windows GeForce | at most 20 ms | CHOICE (the watchdog fires at about 2 s) |
| sleep autocorrelation | at most 200 sweeps at $L = 1024$ | TARGET |
| throughput and memory | §10.4 | TARGET |

## Appendix B · Sources

Checked on the web on 2026-09-24:
- [Local Partitioning for Directed Graphs Using PageRank (Andersen, Chung, Lang)](https://www.math.ucdavis.edu/~saito/data/digraphs/andersen-chung-lang_localpartition-digraphs-via-pagerank.pdf)
- [Residual Belief Propagation (Elidan, McGraw, Koller), arXiv 1206.6837](https://arxiv.org/abs/1206.6837)
- [CSSR: An Algorithm for Building Markov Models from Time Series](https://bactra.org/CSSR/) · [Shalizi and Klinkner, arXiv 1408.2025](https://arxiv.org/abs/1408.2025)
- [NVIDIA Blackwell Tuning Guide: shared memory and clusters for compute capability 12.0](https://docs.nvidia.com/cuda/blackwell-tuning-guide/index.html)
- [NVIDIA RTX 5090 specifications (Spheron)](https://www.spheron.network/blog/nvidia-rtx-5090-specs/) · [(RunPod)](https://www.runpod.io/articles/guides/nvidia-rtx-5090)
- [NVIDIA H200 141GB product guide (Lenovo Press)](https://lenovopress.lenovo.com/lp1944-nvidia-h200-141gb-gpu)

Established literature, cited by name:
- Kosterlitz and Thouless (1973); Kosterlitz (1974); Nelson and Kosterlitz (1977); Hasenbusch (2005); Imry and Ma (1975)
- Ackley, Hinton and Sejnowski (1985); Crick and Mitchison (1983); Hopfield, Feinstein and Palmer (1983)
- Goodman and Sokal (1986); Wolff (1989); Levesque and Verlet (1993); Landauer (1961)
- Crutchfield and Young (1989); Artin (1925); Garside (1969); Bigelow (1999, Burau unfaithful for n ≥ 5)
- Salmon et al. (2011, the Philox generator); Hobson and McCarley (1977); Zheng and Meister (2024)
- id Software, the Quake map tools `qbsp`, `vis` and `light` (1996)

Local lineage in `C:/AGI`:
- `THE-THIRD-FORM_…_v0.1` and `…_v0.2`
- `SEED_GENESIS-RECORD_v0.2_…`
- `TANKLAB_L0_EXPERIMENT_SPEC_v0.1_…`
- `canon/THE_UNFINISHED_MIRROR.md`
- `C:/AGI/chatgpt.txt` and `C:/AGI/claudeweb.txt`, the two KELVIN transcripts
- `native_intelligence.pdf` (January 2026)
