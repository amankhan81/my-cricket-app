import streamlit as st
from supabase import create_client
import json

# --- DB CONNECTION ---
URL = "https://wkwxtnzdisclwbrygpez.supabase.co"
KEY = "sb_publishable_hQXQy84zDzyyT6Q2cvVIQA_6qqwY_uA"
supabase = create_client(URL, KEY)

# --- DATA HELPERS ---
def get_match():
    res = supabase.table("match_data").select("*").eq("id", 1).single().execute().data
    if not res.get("history"): res["history"] = "[]"
    return res

def update_score(runs_inc, balls_inc, is_undo=False):
    d = get_match()
    history = json.loads(d["history"])
    if is_undo:
        if len(history) > 0:
            last = history.pop()
            supabase.table("match_data").update({
                "runs": max(0, d["runs"] - last["r"]),
                "balls": max(0, d["balls"] - last["b"]),
                "history": json.dumps(history)
            }).eq("id", 1).execute()
    else:
        history.append({"r": runs_inc, "b": balls_inc})
        supabase.table("match_data").update({
            "runs": d["runs"] + runs_inc,
            "balls": d["balls"] + balls_inc,
            "history": json.dumps(history)
        }).eq("id", 1).execute()

# --- APP LOGIC ---
params = st.query_params

if params.get("mode") == "overlay":
    st.markdown("<style>html,body,[data-testid='stAppViewContainer'],.main{background:transparent !important;}header,footer,#MainMenu{display:none !important;}.ticker{position:fixed;top:15px;left:15px;background:rgba(0,0,0,0.9);padding:10px 15px;display:flex;align-items:baseline;gap:10px;color:white;border-left:4px solid #8bc34a;border-radius:4px;font-family:sans-serif;}.r-txt{font-size:38px;font-weight:900;}</style>", unsafe_allow_html=True)
    d = get_match()
    st.markdown(f'<div class="ticker"><span class="r-txt">{d["runs"]}</span><span style="font-size:18px;opacity:0.8;">({d["balls"]//6}.{d["balls"]%6}/{d["match_overs"]})</span></div>', unsafe_allow_html=True)
    import time; time.sleep(2); st.rerun()

else:
    st.markdown("""
        <style>
            .stApp { background-color: #CCCCCC !important; }
            .block-container { padding: 5px !important; }
            
            /* Header Styling */
            .score-header { display: flex; justify-content: space-around; text-align: center; margin-bottom: 10px; }
            .lbl { color: black; font-size: 26px; font-weight: bold; font-family: sans-serif; }
            .val { color: black; font-size: 80px; font-weight: 900; display: block; margin-top: -15px; }

            /* FORCE PERFECT GRID LAYOUT */
            .main-grid {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 8px;
                width: 100%;
                margin-bottom: 10px;
            }

            /* Custom Button Overrides */
            .stButton > button {
                width: 100% !important;
                height: 110px !important; /* Manually set height to look square */
                background-color: black !important;
                color: white !important;
                font-size: 35px !important;
                font-weight: bold !important;
                border: none !important;
                border-radius: 0px !important;
            }
            
            /* Undo Button specific font */
            div[data-testid="column"]:nth-of-type(3) button { font-size: 20px !important; }

            .section-hdr { background-color: black; color: white; text-align: center; font-size: 28px; font-weight: bold; padding: 10px; margin: 15px 0 5px 0; width: 100%; }

            /* Full Width Reset Button */
            .reset-container button {
                height: 65px !important;
                font-size: 24px !important;
                border-radius: 0px !important;
            }
            
            /* Minimal Gap for Extras */
            [data-testid="stHorizontalBlock"] { gap: 4px !important; }
            .extra-btn button { height: 55px !important; font-size: 16px !important; }
        </style>
    """, unsafe_allow_html=True)

    d = get_match()
    if "started" not in st.session_state: st.session_state.started = False

    if not st.session_state.started:
        st.markdown("<h1 style='color:black; text-align:center;'>Match Setup</h1>", unsafe_allow_html=True)
        ov_in = st.number_input("Match Overs", min_value=1, value=int(d['match_overs']))
        if st.button("START MATCH", use_container_width=True):
            supabase.table("match_data").update({"match_overs": ov_in, "runs": 0, "balls": 0, "history": "[]"}).eq("id", 1).execute()
            st.session_state.started = True
            st.rerun()

    else:
        # 1. SCORE DISPLAY
        st.markdown(f"""
            <div class="score-header">
                <div><span class="lbl">SCORE</span><span class="val">{d['runs']}</span></div>
                <div><span class="lbl">OVERS</span><span class="val">{d['balls']//6}.{d['balls']%6}</span></div>
            </div>
        """, unsafe_allow_html=True)

        # 2. SCORING GRID (1, 2, 3)
        c1, c2, c3 = st.columns(3)
        if c1.button("1", key="1"): update_score(1, 1); st.rerun()
        if c2.button("2", key="2"): update_score(2, 1); st.rerun()
        if c3.button("3", key="3"): update_score(3, 1); st.rerun()

        # 3. SCORING GRID (4, 6, UNDO)
        c4, c5, c6 = st.columns(3)
        if c4.button("4", key="4"): update_score(4, 1); st.rerun()
        if c5.button("6", key="6"): update_score(6, 1); st.rerun()
        if c6.button("UNDO", key="un"): update_score(0, 0, is_undo=True); st.rerun()

        # 4. WIDES
        st.markdown('<div class="section-hdr">Wides</div>', unsafe_allow_html=True)
        wcols = st.columns(5)
        for i in range(5):
            with wcols[i]: st.markdown('<div class="extra-btn">', unsafe_allow_html=True)
            if wcols[i].button(f"W+{i}", key=f"w{i}"): update_score(1+i, 0); st.rerun()

        # 5. NO BALL
        st.markdown('<div class="section-hdr">No Ball</div>', unsafe_allow_html=True)
        ncols = st.columns(7)
        for i in range(7):
            with ncols[i]: st.markdown('<div class="extra-btn">', unsafe_allow_html=True)
            if ncols[i].button(f"N+{i}", key=f"n{i}"): update_score(1+i, 0); st.rerun()

        # 6. RESET MATCH
        st.markdown('<div class="reset-container">', unsafe_allow_html=True)
        if st.button("Reset Match", key="reset", use_container_width=True):
            st.session_state.started = False
            supabase.table("match_data").update({"runs":0, "balls":0, "history":"[]"}).eq("id", 1).execute()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
