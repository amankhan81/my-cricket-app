import streamlit as st
from supabase import create_client
import json

# --- DB CONNECTION ---
URL = "https://wkwxtnzdisclwbrygpez.supabase.co"
KEY = "sb_publishable_hQXQy84zDzyyT6Q2cvVIQA_6qqwY_uA"
supabase = create_client(URL, KEY)

# --- DATA HELPERS ---
def get_match():
    try:
        return supabase.table("match_data").select("*").eq("id", 1).single().execute().data
    except:
        return {"runs": 0, "balls": 0, "match_overs": 8, "target": 0}

def update_db(runs_inc, balls_inc):
    d = get_match()
    supabase.table("match_data").update({
        "runs": d['runs'] + runs_inc,
        "balls": d['balls'] + balls_inc
    }).eq("id", 1).execute()

# --- APP LOGIC ---
params = st.query_params

# 1. DATA API (Hidden: This feeds the Scoreticker)
if params.get("mode") == "data":
    st.write(json.dumps(get_match()))
    st.stop()

# 2. OVERLAY TICKER (Top Left, Transparent, Auto-updating)
elif params.get("mode") == "overlay":
    st.markdown("""
        <style>
            html, body, [data-testid="stAppViewContainer"], .main { background: transparent !important; }
            header, footer, #MainMenu {display: none !important;}
            .block-container {padding: 0 !important; margin: 0 !important;}
            .ticker-box {
                position: fixed; top: 15px; left: 15px;
                background: #1B5E20; color: white; padding: 12px 20px;
                border-radius: 10px; font-family: 'Arial', sans-serif;
                min-width: 220px; box-shadow: 0 4px 10px rgba(0,0,0,0.5);
            }
            .runs-val { font-size: 36px; font-weight: 900; line-height: 1; color: white !important; }
            .target-tag { background: black; color: white; padding: 3px 10px; border-radius: 0 0 5px 5px; font-size: 13px; font-weight: bold; width: fit-content; margin-top: 5px; }
        </style>
        <div class="ticker-box">
            <div id="status" style="font-size: 10px; font-weight: bold; color: white;">LIVE MATCH</div>
            <div class="runs-val">
                <span id="r">0</span> <span style="font-size:18px; opacity:0.8;" id="ov">(0.0)</span>
            </div>
            <div id="tgt_tag" class="target-tag" style="display:none;">TARGET: <span id="t">0</span></div>
        </div>
        <script>
            async function fetchData() {
                try {
                    const res = await fetch(window.location.origin + window.location.pathname + '?mode=data');
                    const d = await res.json();
                    document.getElementById('r').innerText = d.runs;
                    document.getElementById('ov').innerText = "(" + Math.floor(d.balls/6) + "." + (d.balls%6) + ")";
                    if(d.target > 0) {
                        document.getElementById('tgt_tag').style.display = 'block';
                        document.getElementById('t').innerText = d.target;
                    } else { document.getElementById('tgt_tag').style.display = 'none'; }
                } catch (e) {}
            }
            setInterval(fetchData, 2000); fetchData();
        </script>
    """, unsafe_allow_html=True)

# 3. MOBILE SCORER APP
else:
    st.markdown("""
        <style>
            .stApp { background-color: #FEE49B !important; }
            [data-testid="stHorizontalBlock"] { display: flex !important; flex-direction: row !important; flex-wrap: nowrap !important; gap: 8px !important; }
            [data-testid="stColumn"] { flex: 1 1 0% !important; min-width: 0 !important; }
            
            /* Buttons: White Text on Dark Colors */
            .stButton>button {
                height: 90px !important; font-size: 32px !important; font-weight: 800 !important;
                border-radius: 8px !important; border: none !important; color: white !important; background-color: #333 !important;
            }
            /* Specific Button Colors */
            div[data-testid="column"]:nth-of-type(1) button { background-color: #4A90E2 !important; }
            div[data-testid="column"]:nth-of-type(2) button { background-color: #2c3e50 !important; }
            div[data-testid="column"]:nth-of-type(3) button { background-color: #1a1a1a !important; }
            
            /* Special Buttons in Row 2 */
            .four-btn button { background-color: #00B050 !important; }
            .six-btn button { background-color: #0070C0 !important; }
            .undo-btn button { background-color: #F8B195 !important; color: black !important; font-size: 18px !important; }

            .extra-hdr { background: #C65911; color: white; text-align: center; font-weight: bold; padding: 5px; margin: 10px 0; border-radius: 4px; }
            .stMetricValue { font-size: 55px !important; font-weight: 900 !important; color: black !important; }
            
            /* Setting Text Color */
            .stExpander { color: black !important; }
            summary { color: black !important; font-weight: bold !important; }
        </style>
    """, unsafe_allow_html=True)

    if "started" not in st.session_state:
        st.session_state.started = False

    d = get_match()
    max_balls = d['match_overs'] * 6

    # --- START SCREEN ---
    if not st.session_state.started:
        st.title("🏏 Match Setup")
        ov_input = st.number_input("Enter Match Overs", min_value=1, value=int(d['match_overs']))
        if st.button("START MATCH", use_container_width=True):
            supabase.table("match_data").update({"match_overs": ov_input, "runs": 0, "balls": 0, "target": 0}).eq("id", 1).execute()
            st.session_state.started = True
            st.rerun()

    # --- INNINGS COMPLETE SCREEN ---
    elif d['balls'] >= max_balls and d['target'] == 0:
        st.header("Innings Complete!")
        st.subheader(f"Total Score: {d['runs']}")
        if st.button("START 2nd INNINGS", use_container_width=True):
            supabase.table("match_data").update({"target": d['runs'] + 1, "runs": 0, "balls": 0}).eq("id", 1).execute()
            st.rerun()

    # --- SCORING INTERFACE ---
    else:
        # Scoreboard
        m1, m2 = st.columns(2)
        m1.metric("SCORE", d['runs'])
        m2.metric("OVERS", f"{d['balls']//6}.{d['balls']%6}")
        if d['target'] > 0:
            st.info(f"**TARGET: {d['target']}** | Needed: {d['target'] - d['runs']} runs in {max_balls - d['balls']} balls")

        # Row 1: 1, 2, 3
        c1, c2, c3 = st.columns(3)
        if c1.button("1", key="b1", use_container_width=True): update_db(1, 1); st.rerun()
        if c2.button("2", key="b2", use_container_width=True): update_db(2, 1); st.rerun()
        if c3.button("3", key="b3", use_container_width=True): update_db(3, 1); st.rerun()

        # Row 2: 4, 6, UNDO
        c4, c5, c6 = st.columns(3)
        with c4: st.markdown('<div class="four-btn">', unsafe_allow_html=True)
        if c4.button("4", key="b4", use_container_width=True): update_db(4, 1); st.rerun()
        with c5: st.markdown('<div class="six-btn">', unsafe_allow_html=True)
        if c5.button("6", key="b6", use_container_width=True): update_db(6, 1); st.rerun()
        with c6: st.markdown('<div class="undo-btn">', unsafe_allow_html=True)
        if c6.button("UNDO", key="und", use_container_width=True): update_db(-1, -1); st.rerun()

        # Extras Rows
        st.markdown('<div class="extra-hdr">WIDES</div>', unsafe_allow_html=True)
        wcols = st.columns(5)
        for i in range(5):
            if wcols[i].button(f"W+{i}", key=f"w{i}", use_container_width=True): update_db(1+i, 0); st.rerun()

        st.markdown('<div class="extra-hdr">NO BALL</div>', unsafe_allow_html=True)
        ncols = st.columns(7)
        for i in range(7):
            if ncols[i].button(f"N+{i}", key=f"n{i}", use_container_width=True): update_db(1+i, 0); st.rerun()

        # Footer Settings
        with st.expander("⚙️ Settings"):
            if st.button("RESET MATCH"):
                st.session_state.started = False
                supabase.table("match_data").update({"runs":0, "balls":0, "target":0}).eq("id", 1).execute()
                st.rerun()
            st.write(f"Overlay: `https://score-easy.streamlit.app/?mode=overlay`")
