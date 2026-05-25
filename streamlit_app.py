import streamlit as st
from supabase import create_client
import json

# --- DB CONNECTION ---
URL = "https://wkwxtnzdisclwbrygpez.supabase.co"
KEY = "sb_publishable_hQXQy84zDzyyT6Q2cvVIQA_6qqwY_uA"
supabase = create_client(URL, KEY)

# --- DATA HELPERS ---
def get_match():
    # Fetching match data and history
    res = supabase.table("match_data").select("*").eq("id", 1).single().execute().data
    if "history" not in res or res["history"] is None:
        res["history"] = "[]"
    return res

def update_score(runs_inc, balls_inc, is_undo=False):
    d = get_match()
    history = json.loads(d["history"])
    
    if is_undo:
        if len(history) > 0:
            last_action = history.pop()
            new_runs = d["runs"] - last_action["r"]
            new_balls = d["balls"] - last_action["b"]
            supabase.table("match_data").update({
                "runs": max(0, new_runs),
                "balls": max(0, new_balls),
                "history": json.dumps(history)
            }).eq("id", 1).execute()
    else:
        history.append({"r": runs_inc, "b": balls_inc})
        # Keep history manageable
        if len(history) > 20: history.pop(0)
        supabase.table("match_data").update({
            "runs": d["runs"] + runs_inc,
            "balls": d["balls"] + balls_inc,
            "history": json.dumps(history)
        }).eq("id", 1).execute()

# --- APP LOGIC ---
params = st.query_params

# 1. OVERLAY VIEW
if params.get("mode") == "overlay":
    st.markdown("""
        <style>
            html, body, [data-testid="stAppViewContainer"], .main { background: transparent !important; }
            header, footer, #MainMenu {display: none !important;}
            .ticker-container { position: fixed; top: 15px; left: 15px; font-family: sans-serif; }
            .black-stripe { background: rgba(0,0,0,0.9); padding: 10px 15px; display: flex; align-items: baseline; gap: 10px; color: white !important; border-left: 4px solid #8bc34a; border-radius: 4px; }
            .runs-txt { font-size: 38px; font-weight: 900; color: white !important; }
        </style>
    """, unsafe_allow_html=True)
    d = get_match()
    ov = f"{d['balls']//6}.{d['balls']%6}"
    st.markdown(f'<div class="ticker-container"><div class="black-stripe"><span class="runs-txt">{d["runs"]}</span><span style="font-size:18px;opacity:0.8;">({ov}/{d["match_overs"]})</span></div></div>', unsafe_allow_html=True)
    import time
    time.sleep(2)
    st.rerun()

# 2. MOBILE SCORER APP
else:
    st.markdown("""
        <style>
            .stApp { background-color: #CCCCCC !important; }
            .block-container { padding: 5px !important; }

            /* Header Font Sizes */
            .score-header { display: flex; justify-content: space-around; text-align: center; margin-bottom: 20px; }
            .lbl { color: black; font-size: 28px; font-weight: bold; font-family: sans-serif; }
            .val { color: black; font-size: 80px; font-weight: 900; display: block; margin-top: -15px; }

            /* FORCED 3-COLUMN GRID FOR SQUARE BUTTONS */
            [data-testid="stHorizontalBlock"] {
                display: flex !important; flex-direction: row !important; flex-wrap: nowrap !important; gap: 8px !important;
            }
            [data-testid="stColumn"] { flex: 1 !important; min-width: 0 !important; }

            /* Buttons: Black, Sharp Edges, Perfectly Square */
            .stButton > button {
                width: 100% !important;
                aspect-ratio: 1 / 1 !important;
                background-color: black !important;
                color: white !important;
                font-size: 38px !important;
                font-weight: bold !important;
                border: none !important;
                border-radius: 0px !important;
                padding: 0px !important;
                display: flex !important; align-items: center !important; justify-content: center !important;
            }
            
            /* Section Headers */
            .section-hdr { background-color: black; color: white; text-align: center; font-size: 30px; font-weight: bold; padding: 8px; margin: 20px 0 5px 0; }
            
            /* Small Font for Undo and Extras */
            div[data-testid="stColumn"]:nth-of-type(3) button { font-size: 22px !important; }
            .extra-btn button { aspect-ratio: auto !important; height: 55px !important; font-size: 18px !important; border: 1px solid #333 !important; }

            /* Full Width Reset/Start Button */
            .full-btn button {
                aspect-ratio: auto !important; height: 70px !important; font-size: 24px !important;
                background-color: black !important; color: white !important; width: 100% !important;
                border-radius: 0px !important; border: none !important; margin-top: 15px;
            }
        </style>
    """, unsafe_allow_html=True)

    d = get_match()
    if "started" not in st.session_state: st.session_state.started = False

    # --- START SCREEN ---
    if not st.session_state.started:
        st.markdown("<h1 style='color:black; text-align:center; padding-top:20px;'>Cricket Match Setup</h1>", unsafe_allow_html=True)
        ov_in = st.number_input("Match Overs", min_value=1, value=int(d['match_overs']))
        st.markdown('<div class="full-btn">', unsafe_allow_html=True)
        if st.button("START MATCH"):
            supabase.table("match_data").update({"match_overs": ov_in, "runs": 0, "balls": 0, "target": 0, "history": "[]"}).eq("id", 1).execute()
            st.session_state.started = True
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # --- SCORING ---
    else:
        st.markdown(f"""
            <div class="score-header">
                <div><span class="lbl">SCORE</span><span class="val">{d['runs']}</span></div>
                <div><span class="lbl">OVERS</span><span class="val">{d['balls']//6}.{d['balls']%6}</span></div>
            </div>
        """, unsafe_allow_html=True)

        # Row 1: 1, 2, 3
        r1 = st.columns(3)
        if r1[0].button("1", key="1"): update_score(1, 1); st.rerun()
        if r1[1].button("2", key="2"): update_score(2, 1); st.rerun()
        if r1[2].button("3", key="3"): update_score(3, 1); st.rerun()

        # Row 2: 4, 6, UNDO
        r2 = st.columns(3)
        if r2[0].button("4", key="4"): update_score(4, 1); st.rerun()
        if r2[1].button("6", key="6"): update_score(6, 1); st.rerun()
        if r2[2].button("UNDO", key="un"): update_score(0, 0, is_undo=True); st.rerun()

        # Wides
        st.markdown('<div class="section-hdr">Wides</div>', unsafe_allow_html=True)
        wcols = st.columns(5)
        for i in range(5):
            with wcols[i]: st.markdown('<div class="extra-btn">', unsafe_allow_html=True)
            if wcols[i].button(f"W+{i}", key=f"w{i}"): update_score(1+i, 0); st.rerun()

        # No Ball
        st.markdown('<div class="section-hdr">No Ball</div>', unsafe_allow_html=True)
        ncols = st.columns(7)
        for i in range(7):
            with ncols[i]: st.markdown('<div class="extra-btn">', unsafe_allow_html=True)
            if ncols[i].button(f"N+{i}", key=f"n{i}"): update_score(1+i, 0); st.rerun()

        # Reset Match Button
        st.markdown('<div class="full-btn">', unsafe_allow_html=True)
        if st.button("Reset Match", key="reset"):
            st.session_state.started = False
            supabase.table("match_data").update({"runs":0, "balls":0, "target":0, "history":"[]"}).eq("id", 1).execute()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
