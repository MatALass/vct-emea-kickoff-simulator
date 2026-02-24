import streamlit as st

st.set_page_config(page_title="VCT EMEA Kickoff 2026 Simulator", layout="wide")

# -----------------------------
# Format (Riot official primer):
# Triple-elimination (3 lives): UB -> MB -> LB -> eliminated
# BO3 except UB Final / MB Final / LB Final are BO5
# 4 Champions 2025 reps get bye to UB Round 2: FNC, TL, GX, TH
# Opening matches drawn: NAVI-KC, FUT-GM, PCIFIC-BBL, ULF-VIT
# -----------------------------

BYE_TEAMS = ["Fnatic", "Team Liquid", "GIANTX", "Team Heretics"]
OPENING = [
    ("NAVI", "Karmine Corp"),
    ("FUT Esports", "Gentle Mates"),
    ("PCIFIC Esports", "BBL Esports"),
    ("ULF Esports", "Team Vitality"),
]

ALL_TEAMS = [
    "BBL Esports",
    "Fnatic",
    "FUT Esports",
    "Gentle Mates",
    "GIANTX",
    "Karmine Corp",
    "NAVI",
    "Team Heretics",
    "Team Liquid",
    "Team Vitality",
    "PCIFIC Esports",
    "ULF Esports",
]


# ---------- Helpers ----------
def other(team_a, team_b, winner):
    return team_b if winner == team_a else team_a


def init_state():
    st.session_state.results = {}  # match_id -> winner
    st.session_state.history = []  # list of match_id in played order (for undo)
    st.session_state.losses = {t: 0 for t in ALL_TEAMS}
    st.session_state.qualifiers = []  # [UB winner, MB winner, LB winner]
    st.session_state.eliminated = []  # in elimination order (optional)


def get_team(ref):
    """ref is either a team string or a tuple ('W'/'L', match_id)."""
    if isinstance(ref, str):
        return ref
    kind, mid = ref
    if mid not in st.session_state.results:
        return None
    w = st.session_state.results[mid]
    a, b = MATCHES[mid]["a"], MATCHES[mid]["b"]
    a = get_team(a)
    b = get_team(b)
    if a is None or b is None:
        return None
    if kind == "W":
        return w
    # loser
    return other(a, b, w)


def is_played(mid):
    return mid in st.session_state.results


def is_ready(mid):
    if is_played(mid):
        return False
    a = get_team(MATCHES[mid]["a"])
    b = get_team(MATCHES[mid]["b"])
    return a is not None and b is not None


def record_match(mid, winner):
    a = get_team(MATCHES[mid]["a"])
    b = get_team(MATCHES[mid]["b"])
    if winner not in (a, b):
        return

    st.session_state.results[mid] = winner
    st.session_state.history.append(mid)

    loser = other(a, b, winner)
    st.session_state.losses[loser] += 1

    # If loser reaches 3 losses -> eliminated
    if st.session_state.losses[loser] >= 3 and loser not in st.session_state.eliminated:
        st.session_state.eliminated.append(loser)

    # If this match is a qualifier final, store qualifier
    if MATCHES[mid].get("qualifier_slot"):
        slot = MATCHES[mid]["qualifier_slot"]
        # slot is 0=UB, 1=MB, 2=LB
        while len(st.session_state.qualifiers) < 3:
            st.session_state.qualifiers.append(None)
        st.session_state.qualifiers[slot] = winner


# NOTE: A safe undo is implemented below (undo_last_safe) by recomputing state.


def recompute_from(results_in_order, winners_map):
    init_state()
    for mid in results_in_order:
        record_match(mid, winners_map[mid])


def next_matches():
    return [mid for mid in MATCHES.keys() if is_ready(mid)]


# ---------- Bracket graph (based on Riot bracket image logic) ----------
# We name matches by bracket/round rather than Liquipedia IDs.
# Upper:
# UB_R1: 4 opening matches
# UB_R2: bye teams enter vs UB_R1 winners
# UB_R3: UB semis
# UB_F: Upper Final (BO5) -> Qualifier slot #1

# Middle:
# MB_R1: 4 matches pairing UB_R1 losers vs UB_R2 losers (cross)
# MB_R2: 2 matches among MB_R1 winners
# MB_R3: 2 matches: MB_R2 winners vs UB_R3 losers (cross)
# MB_R4: 1 match among MB_R3 winners
# MB_F: Middle Final (BO5) vs UB_F loser -> Qualifier slot #2

# Lower:
# LB_R1: 2 matches among MB_R1 losers
# LB_R2: 2 matches: LB_R1 winners vs MB_R2 losers
# LB_R3: 2 matches: LB_R2 winners vs MB_R3 losers
# LB_R4: 1 match among LB_R3 winners
# LB_R5: 1 match: LB_R4 winner vs MB_R4 loser
# LB_F: Lower Final (BO5) vs MB_F loser -> Qualifier slot #3

# Opening matchups fixed (from draw).
# We also fix which bye team faces which opening winner (typical seed mapping).
UB_R1 = ["UB_R1_M1", "UB_R1_M2", "UB_R1_M3", "UB_R1_M4"]
UB_R2 = ["UB_R2_M1", "UB_R2_M2", "UB_R2_M3", "UB_R2_M4"]
UB_R3 = ["UB_R3_M1", "UB_R3_M2"]
UB_F = ["UB_FINAL"]

MB_R1 = ["MB_R1_M1", "MB_R1_M2", "MB_R1_M3", "MB_R1_M4"]
MB_R2 = ["MB_R2_M1", "MB_R2_M2"]
MB_R3 = ["MB_R3_M1", "MB_R3_M2"]
MB_R4 = ["MB_R4_M1"]
MB_F = ["MB_FINAL"]

LB_R1 = ["LB_R1_M1", "LB_R1_M2"]
LB_R2 = ["LB_R2_M1", "LB_R2_M2"]
LB_R3 = ["LB_R3_M1", "LB_R3_M2"]
LB_R4 = ["LB_R4_M1"]
LB_R5 = ["LB_R5_M1"]
LB_F = ["LB_FINAL"]

MATCHES = {
    # Upper Round 1 (opening)
    "UB_R1_M1": {"a": OPENING[0][0], "b": OPENING[0][1], "bo": 3, "label": "Upper R1 — Match 1"},
    "UB_R1_M2": {"a": OPENING[1][0], "b": OPENING[1][1], "bo": 3, "label": "Upper R1 — Match 2"},
    "UB_R1_M3": {"a": OPENING[2][0], "b": OPENING[2][1], "bo": 3, "label": "Upper R1 — Match 3"},
    "UB_R1_M4": {"a": OPENING[3][0], "b": OPENING[3][1], "bo": 3, "label": "Upper R1 — Match 4"},
    # Upper Round 2 (bye teams enter)
    "UB_R2_M1": {
        "a": BYE_TEAMS[0],
        "b": ("W", "UB_R1_M1"),
        "bo": 3,
        "label": "Upper R2 — Fnatic vs Winner(UB R1 M1)",
    },
    "UB_R2_M2": {
        "a": BYE_TEAMS[1],
        "b": ("W", "UB_R1_M2"),
        "bo": 3,
        "label": "Upper R2 — Team Liquid vs Winner(UB R1 M2)",
    },
    "UB_R2_M3": {
        "a": BYE_TEAMS[2],
        "b": ("W", "UB_R1_M3"),
        "bo": 3,
        "label": "Upper R2 — GIANTX vs Winner(UB R1 M3)",
    },
    "UB_R2_M4": {
        "a": BYE_TEAMS[3],
        "b": ("W", "UB_R1_M4"),
        "bo": 3,
        "label": "Upper R2 — Team Heretics vs Winner(UB R1 M4)",
    },
    # Upper semis
    "UB_R3_M1": {
        "a": ("W", "UB_R2_M1"),
        "b": ("W", "UB_R2_M2"),
        "bo": 3,
        "label": "Upper Semifinal 1",
    },
    "UB_R3_M2": {
        "a": ("W", "UB_R2_M3"),
        "b": ("W", "UB_R2_M4"),
        "bo": 3,
        "label": "Upper Semifinal 2",
    },
    # Upper Final (qualifier #1)
    "UB_FINAL": {
        "a": ("W", "UB_R3_M1"),
        "b": ("W", "UB_R3_M2"),
        "bo": 5,
        "label": "UPPER FINAL (BO5) — Qualifier #1",
        "qualifier_slot": 0,
    },
    # Middle R1: cross UB_R1 losers with UB_R2 losers (as in Riot bracket)
    "MB_R1_M1": {
        "a": ("L", "UB_R1_M1"),
        "b": ("L", "UB_R2_M4"),
        "bo": 3,
        "label": "Middle R1 — Loser(UB R1 M1) vs Loser(UB R2 M4)",
    },
    "MB_R1_M2": {
        "a": ("L", "UB_R1_M2"),
        "b": ("L", "UB_R2_M3"),
        "bo": 3,
        "label": "Middle R1 — Loser(UB R1 M2) vs Loser(UB R2 M3)",
    },
    "MB_R1_M3": {
        "a": ("L", "UB_R1_M3"),
        "b": ("L", "UB_R2_M2"),
        "bo": 3,
        "label": "Middle R1 — Loser(UB R1 M3) vs Loser(UB R2 M2)",
    },
    "MB_R1_M4": {
        "a": ("L", "UB_R1_M4"),
        "b": ("L", "UB_R2_M1"),
        "bo": 3,
        "label": "Middle R1 — Loser(UB R1 M4) vs Loser(UB R2 M1)",
    },
    # Middle R2
    "MB_R2_M1": {
        "a": ("W", "MB_R1_M1"),
        "b": ("W", "MB_R1_M2"),
        "bo": 3,
        "label": "Middle R2 — Winners(MB R1 M1/M2)",
    },
    "MB_R2_M2": {
        "a": ("W", "MB_R1_M3"),
        "b": ("W", "MB_R1_M4"),
        "bo": 3,
        "label": "Middle R2 — Winners(MB R1 M3/M4)",
    },
    # Middle R3: vs UB semis losers
    "MB_R3_M1": {
        "a": ("W", "MB_R2_M1"),
        "b": ("L", "UB_R3_M2"),
        "bo": 3,
        "label": "Middle R3 — Winner(MB R2 M1) vs Loser(Upper SF2)",
    },
    "MB_R3_M2": {
        "a": ("W", "MB_R2_M2"),
        "b": ("L", "UB_R3_M1"),
        "bo": 3,
        "label": "Middle R3 — Winner(MB R2 M2) vs Loser(Upper SF1)",
    },
    # Middle R4
    "MB_R4_M1": {
        "a": ("W", "MB_R3_M1"),
        "b": ("W", "MB_R3_M2"),
        "bo": 3,
        "label": "Middle R4 — Winners(MB R3)",
    },
    # Middle Final (qualifier #2): vs Upper Final loser
    "MB_FINAL": {
        "a": ("W", "MB_R4_M1"),
        "b": ("L", "UB_FINAL"),
        "bo": 5,
        "label": "MIDDLE FINAL (BO5) — Qualifier #2",
        "qualifier_slot": 1,
    },
    # Lower R1: MB_R1 losers face each other
    "LB_R1_M1": {
        "a": ("L", "MB_R1_M1"),
        "b": ("L", "MB_R1_M2"),
        "bo": 3,
        "label": "Lower R1 — Losers(MB R1 M1/M2)",
    },
    "LB_R1_M2": {
        "a": ("L", "MB_R1_M3"),
        "b": ("L", "MB_R1_M4"),
        "bo": 3,
        "label": "Lower R1 — Losers(MB R1 M3/M4)",
    },
    # Lower R2: vs MB_R2 losers
    "LB_R2_M1": {
        "a": ("W", "LB_R1_M1"),
        "b": ("L", "MB_R2_M1"),
        "bo": 3,
        "label": "Lower R2 — Winner(LB R1 M1) vs Loser(MB R2 M1)",
    },
    "LB_R2_M2": {
        "a": ("W", "LB_R1_M2"),
        "b": ("L", "MB_R2_M2"),
        "bo": 3,
        "label": "Lower R2 — Winner(LB R1 M2) vs Loser(MB R2 M2)",
    },
    # Lower R3: vs MB_R3 losers
    "LB_R3_M1": {
        "a": ("W", "LB_R2_M1"),
        "b": ("L", "MB_R3_M1"),
        "bo": 3,
        "label": "Lower R3 — Winner(LB R2 M1) vs Loser(MB R3 M1)",
    },
    "LB_R3_M2": {
        "a": ("W", "LB_R2_M2"),
        "b": ("L", "MB_R3_M2"),
        "bo": 3,
        "label": "Lower R3 — Winner(LB R2 M2) vs Loser(MB R3 M2)",
    },
    # Lower R4
    "LB_R4_M1": {
        "a": ("W", "LB_R3_M1"),
        "b": ("W", "LB_R3_M2"),
        "bo": 3,
        "label": "Lower R4 — Winners(LB R3)",
    },
    # Lower R5: vs MB_R4 loser
    "LB_R5_M1": {
        "a": ("W", "LB_R4_M1"),
        "b": ("L", "MB_R4_M1"),
        "bo": 3,
        "label": "Lower R5 — Winner(LB R4) vs Loser(MB R4)",
    },
    # Lower Final (qualifier #3): vs Middle Final loser
    "LB_FINAL": {
        "a": ("W", "LB_R5_M1"),
        "b": ("L", "MB_FINAL"),
        "bo": 5,
        "label": "LOWER FINAL (BO5) — Qualifier #3",
        "qualifier_slot": 2,
    },
}


# Fix undo properly by storing winners before recompute
def undo_last_safe():
    if not st.session_state.history:
        return
    winners_map = st.session_state.results.copy()
    order = st.session_state.history.copy()

    # remove last
    last = order.pop()
    winners_map.pop(last, None)

    recompute_from(order, winners_map)


# ---------- UI ----------
if "results" not in st.session_state:
    init_state()

st.title("VCT EMEA Kickoff 2026 — Simulateur de prédictions (triple-elimination)")
st.caption(
    "Clique les gagnants, le bracket avance automatiquement. Les 3 vainqueurs des finales UB/MB/LB sont qualifiés."
)

colA, colB, colC, colD = st.columns([1, 1, 1, 1])
with colA:
    if st.button("🔄 Reset", use_container_width=True):
        init_state()
        st.rerun()
with colB:
    if st.button("↩️ Undo", use_container_width=True, disabled=(len(st.session_state.history) == 0)):
        undo_last_safe()
        st.rerun()
with colC:
    st.metric("Matchs joués", len(st.session_state.history))
with colD:
    q = [x for x in st.session_state.qualifiers if x]
    st.metric("Qualifiés", len(q))

# Sidebar status
with st.sidebar:
    st.header("Statut")
    st.subheader("Losses")
    for t in ALL_TEAMS:
        st.write(f"- {t}: {st.session_state.losses[t]}")

    st.subheader("Éliminés (3 défaites)")
    if st.session_state.eliminated:
        st.write("\n".join([f"- {t}" for t in st.session_state.eliminated]))
    else:
        st.write("—")

    st.subheader("Qualifiés (UB / MB / LB)")
    if st.session_state.qualifiers:
        labels = [
            "Qualifier #1 (Upper Final)",
            "Qualifier #2 (Middle Final)",
            "Qualifier #3 (Lower Final)",
        ]
        for i, lab in enumerate(labels):
            val = st.session_state.qualifiers[i] if i < len(st.session_state.qualifiers) else None
            st.write(f"- {lab}: **{val or '—'}**")
    else:
        st.write("—")

# Show played matches recap
st.subheader("Historique")
if st.session_state.history:
    for mid in st.session_state.history[::-1]:
        a = get_team(MATCHES[mid]["a"])
        b = get_team(MATCHES[mid]["b"])
        w = st.session_state.results[mid]
        bo = MATCHES[mid]["bo"]
        st.write(f"**{MATCHES[mid]['label']}** (BO{bo}) — {a} vs {b} → ✅ **{w}**")
else:
    st.write("Aucun match joué pour le moment.")

st.divider()

# Next match picker
ready = next_matches()

# Optional: prioritize "earlier bracket" order for nicer flow
ORDER = (
    UB_R1
    + UB_R2
    + UB_R3
    + UB_F
    + MB_R1
    + MB_R2
    + MB_R3
    + MB_R4
    + MB_F
    + LB_R1
    + LB_R2
    + LB_R3
    + LB_R4
    + LB_R5
    + LB_F
)
ready_sorted = [m for m in ORDER if m in ready]

st.subheader("Prochain(s) match(s) disponible(s)")
if not ready_sorted:
    # could be finished
    qualifiers_done = len([x for x in st.session_state.qualifiers if x]) == 3
    if qualifiers_done:
        st.success("Simulation terminée ✅ Les 3 qualifiés sont définis.")
    else:
        st.info("Pas de match jouable pour l’instant (il faut finir des matchs en amont).")
else:
    mid = st.selectbox(
        "Choisis un match à jouer", ready_sorted, format_func=lambda x: MATCHES[x]["label"]
    )
    a = get_team(MATCHES[mid]["a"])
    b = get_team(MATCHES[mid]["b"])
    bo = MATCHES[mid]["bo"]

    st.markdown(f"### {MATCHES[mid]['label']}")
    st.write(f"**Série : BO{bo}**")
    c1, c2 = st.columns(2)
    with c1:
        pick = st.radio("Gagnant", options=[a, b], horizontal=True)
        if st.button("✅ Valider le gagnant", use_container_width=True):
            record_match(mid, pick)
            st.rerun()
    with c2:
        st.write("**Perdant** recevra +1 défaite (3 → éliminé).")
        st.write("Les finales UB/MB/LB donnent les 3 qualifiés.")

st.divider()

# Simple bracket snapshot (text)
st.subheader("Bracket (aperçu rapide)")


def show_block(title, ids):
    st.markdown(f"#### {title}")
    for mid in ids:
        a = get_team(MATCHES[mid]["a"])
        b = get_team(MATCHES[mid]["b"])
        w = st.session_state.results.get(mid)
        bo = MATCHES[mid]["bo"]
        if a is None or b is None:
            st.write(f"- {MATCHES[mid]['label']} (BO{bo}) — en attente")
        else:
            st.write(
                f"- {MATCHES[mid]['label']} (BO{bo}) — {a} vs {b} " + (f"→ ✅ {w}" if w else "")
            )


col1, col2, col3 = st.columns(3)
with col1:
    show_block("Upper Bracket", UB_R1 + UB_R2 + UB_R3 + UB_F)
with col2:
    show_block("Middle Bracket", MB_R1 + MB_R2 + MB_R3 + MB_R4 + MB_F)
with col3:
    show_block("Lower Bracket", LB_R1 + LB_R2 + LB_R3 + LB_R4 + LB_R5 + LB_F)
