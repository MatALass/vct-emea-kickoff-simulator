import random

import streamlit as st

st.set_page_config(page_title="VCT EMEA Worst -> Best Ranker", layout="centered")

# VCT EMEA 2026 (12 teams)
# Sources: Riot Kickoff primer + Esports Insider list
TEAMS_2026 = [
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

st.title("VCT EMEA — prédiction Kick-off")
st.caption(
    "Tu choisis les gagnants, et chaque gagnant est retiré. Le dernier restant = le plus mauvais de la passe."
)


# ---------------------------
# Session state init
# ---------------------------
def init_state():
    st.session_state.pool = TEAMS_2026.copy()  # équipes pas encore classées
    st.session_state.remaining = (
        st.session_state.pool.copy()
    )  # équipes encore en lice pour trouver la pire
    st.session_state.ranking = []  # du pire -> meilleur (on ajoute au fur et à mesure)
    st.session_state.round_matches = []  # liste de tuples (a,b) où b peut être None (bye)
    st.session_state.round_id = 1
    st.session_state.phase_id = 1  # "passe" courante pour trouver la prochaine pire équipe
    st.session_state.seed = None


if "pool" not in st.session_state:
    init_state()

# ---------------------------
# Controls
# ---------------------------
with st.sidebar:
    st.header("Contrôles")
    if st.button("🔄 Reset total", use_container_width=True):
        init_state()
        st.rerun()

    seed_input = st.text_input(
        "Seed (optionnel, pour reproduire l'aléatoire)", value=str(st.session_state.seed or "")
    )
    if seed_input.strip() == "":
        st.session_state.seed = None
    else:
        # accepte nombres, sinon hash string
        try:
            st.session_state.seed = int(seed_input)
        except ValueError:
            st.session_state.seed = abs(hash(seed_input)) % (2**31)


# ---------------------------
# Helpers
# ---------------------------
def make_matches(teams: list[str], seed=None):
    rnd = random.Random(seed)
    t = teams.copy()
    rnd.shuffle(t)

    matches = []
    i = 0
    while i + 1 < len(t):
        matches.append((t[i], t[i + 1]))
        i += 2

    if i < len(t):
        # bye => l'équipe reste (elle ne "gagne" pas gratuitement, sinon ça biaiserait le "pire finder")
        matches.append((t[i], None))
    return matches


def start_new_phase():
    """On a trouvé une 'pire' équipe; on relance une passe avec le pool restant."""
    st.session_state.remaining = st.session_state.pool.copy()
    st.session_state.round_matches = []
    st.session_state.round_id = 1
    st.session_state.phase_id += 1


def confirm_round_results(winners: dict[int, str]):
    """Retire les gagnants, garde les perdants."""
    to_remove = set()
    for idx, (a, b) in enumerate(st.session_state.round_matches):
        if b is None:
            continue  # bye => reste
        winner = winners.get(idx)
        if winner in (a, b):
            to_remove.add(winner)

    st.session_state.remaining = [t for t in st.session_state.remaining if t not in to_remove]
    st.session_state.round_matches = []
    st.session_state.round_id += 1


def finalize_if_done():
    """Si 1 seule équipe reste, c'est la pire de cette passe."""
    if len(st.session_state.remaining) == 1:
        worst = st.session_state.remaining[0]
        st.session_state.ranking.append(worst)  # classement du pire -> meilleur
        st.session_state.pool = [t for t in st.session_state.pool if t != worst]

        # si plus qu'une équipe dans le pool, on recommence une passe
        if len(st.session_state.pool) >= 2:
            start_new_phase()
        # si 1 équipe restante, c'est la meilleure (à ajouter à la fin)
        elif len(st.session_state.pool) == 1:
            st.session_state.ranking.append(st.session_state.pool[0])
            st.session_state.pool = []
            st.session_state.remaining = []
            st.session_state.round_matches = []


# ---------------------------
# UI status
# ---------------------------
col1, col2, col3 = st.columns(3)
col1.metric("Équipes encore à classer", len(st.session_state.pool))
col2.metric("En lice (passe actuelle)", len(st.session_state.remaining))
col3.metric("Déjà classées (pire → ...)", len(st.session_state.ranking))

if st.session_state.ranking:
    st.subheader("Classement en cours (du pire vers le meilleur)")
    st.write("\n".join([f"{i + 1}. {team}" for i, team in enumerate(st.session_state.ranking)]))

st.divider()

# Si terminé
if len(st.session_state.pool) == 0 and len(st.session_state.remaining) == 0:
    st.success("Classement terminé ✅")
    st.stop()

st.subheader(f"Passe #{st.session_state.phase_id} — Trouver la prochaine pire équipe")
st.write("Équipes encore en lice :")
st.write(", ".join(st.session_state.remaining) if st.session_state.remaining else "—")

# ---------------------------
# Round generation / selection
# ---------------------------
if not st.session_state.round_matches and len(st.session_state.remaining) >= 2:
    if st.button("🎲 Générer des matchs aléatoires", use_container_width=True):
        # seed évolue par round pour varier tout en gardant reproductible si seed fournie
        derived_seed = (
            None
            if st.session_state.seed is None
            else (
                st.session_state.seed + st.session_state.phase_id * 1000 + st.session_state.round_id
            )
        )
        st.session_state.round_matches = make_matches(st.session_state.remaining, seed=derived_seed)
        st.rerun()

# Affiche les matchs si présents
if st.session_state.round_matches:
    st.markdown(f"### Round {st.session_state.round_id}")
    winners = {}

    for idx, (a, b) in enumerate(st.session_state.round_matches):
        if b is None:
            st.info(f"**Bye : {a}** (reste en lice, pas de gagnant à choisir)")
            continue

        winners[idx] = st.radio(
            label=f"Match {idx + 1}",
            options=[a, b],
            horizontal=True,
            key=f"winner_{st.session_state.phase_id}_{st.session_state.round_id}_{idx}",
        )

    c1, c2 = st.columns(2)
    with c1:
        if st.button("✅ Confirmer les gagnants (retirer les gagnants)", use_container_width=True):
            confirm_round_results(winners)
            finalize_if_done()
            st.rerun()
    with c2:
        if st.button("🗑️ Annuler ce round (regénérer)", use_container_width=True):
            st.session_state.round_matches = []
            st.rerun()

# Si plus qu'1 équipe, finaliser
finalize_if_done()

if len(st.session_state.remaining) == 1:
    st.warning(
        f"Il ne reste qu'une équipe : **{st.session_state.remaining[0]}** (pire de cette passe)."
    )
elif len(st.session_state.remaining) == 0 and len(st.session_state.pool) > 0:
    st.warning("Plus d'équipes en lice — tu peux reset si besoin.")
