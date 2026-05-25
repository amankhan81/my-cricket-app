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
        return {"runs": 0, "balls": 0, "match_overs": 8, "target": 0, "history": "[]"}

def update_db(updates):
    supabase.table("match_data").update(updates).eq("id", 1).execute()

# --- APP LOGIC ---
params = st.query_params

# 1. THE DATA API (For No-Blink Overlay)
if params.get("mode") == "data":
    st.write(json.dumps(get_match()))
    st.stop()

# 2. THE OVERLAY (Ticker - Top Left)
elif params.get("mode") == "overlay":
    st.markdown("""
        <style>
            html, body, [data-testid="stAppViewContainer"], .main { background: transparent !important; }
            header, footer, #MainMenu {display: none !important;}
            .block-container {padding: 0 !important; margin: 0 !important;}
            .ticker-container { position: fixed; top: 10px; left: 10px; font-family: 'Arial Black', sans-serif; }
            .main-box { background: #1B5E20; padding: 12px 20px; border-radius: 8px; display: flex; flex-direction: column; min-width: 220px; box-shadow: 4px 4px 15px rgba(0,0,0,0.5); color: white !important; }
            .score-row { display: flex; align-items: baseline; gap: 10px; color: white !important; }
            .runs { font-size: 38px; font-weight: 900; line-height: 1; }
            .overs { font-size: 18px; font-weight: 600; opacity: 0.8; }
            .target-box { background: #000; color: white; padding: 5px 12px; border-radius: 0 0 8px 8px; font-size: 14px; font-weight: bold; width: fit-content; margin-left: 15px; margin-top: -1px; }
        </style>
        <div class="ticker-container">
            <div class="main-box">
                <div id="label" style="font-size:11px; letter-spacing:2px;">1ST INNINGS</div>
                <div class="score-row">
                    <span id="runs" class="runs">Score 0</span>
                    <span id="overs" class="overs">Overs 0.0 (0)</span>
                </div>
            </div>
            <div id="tgt_container" class="target-box" style="display:none;">Target <span id="target">0</span></div>
        </div>
        <script>
            async function updateScore() {
                try {
                    const res = await fetch(window.location.origin + window.location.pathname + '?mode=data');
                    const d = await res.json();
                    const ov = Math.floor(d.balls / 6) + "." + (d.balls % 6);
                    document.getElementById('runs').innerText = "Score " + d.runs;
                    document.getElementById('overs').innerText = "Overs " + ov + " (" + d.match_overs + ")";
                    document.getElementById('label').innerText = d.target === 0 ? "1ST INNINGS" : "2ND INNINGS";
                    if(d.target > 0) { document.getElementById('tgt_container').style.display='block'; document.getElementById('target').innerText=d.target; }
                } catch (e) {}
            }
            setInterval(updateScore, 2000); updateScore();
        </script>
    """, unsafe_allow_html=True)

# 3. MAIN APP (The Redesigned Scorer)
else:
    st.markdown("""
        <style>
        [data-testid="stAppViewContainer"] { background-color: #FEE49B !important; }
        .stMetric { text-align: center; }
        [data-testid="stMetricLabel"] { font-size: 30px !important; color: #4A90E2 !important; font-weight: bold !important; text-shadow: 1px 1px 2px #fff; }
        [data-testid="stMetricValue"] { font-size: 60px !important; color: #000 !important; font-weight: 900 !important; }
        
        /* Grid Buttons */
        .stButton>button { height: 100px; font-size: 35px !important; font-weight: bold; border-radius: 5px; border: none; }
        .run-btn button { background-color: #A3C1E8 !important; color: #000 !important; }
        .four-btn button { background-color: #00B050 !important; color: #000 !important; }
        .six-btn button { background-color: #0070C0 !important; color: #000 !important; }
        .undo-btn button { background-color: #F8B195 !important; color: #000 !important; }
        
        /* Extras Bar */
        .extra-header { background-color: #C65911; color: white; text-align: center; padding: 10px; font-size: 30px; font-weight: bold; margin-top: 10px; }
        .extra-btn button { height: 60px !important; font-size: 20px !important; background-color: #A3C1E8 !important; border: 1px solid #777 !important; color: #000 !important; }
        </style>
    """, unsafe_allow_html=True)

    d = get_match()

    # Metric Row
    m1, m2 = st.columns(2)
    m1.metric("SCORE", d['runs'])
    m2.metric("OVERS", f"{d['balls']//6}.{d['balls']%6}")

    # Main Grid
    row1 = st.columns(3)
    row2 = st.columns(3)

    with row1[0]: st.markdown('<div class="run-btn">', unsafe_allow_html=True)
    if row1[0].button("1", key="r1", use_container_width=True): update_db({"runs": d['runs']+1, "balls": d['balls']+1}); st.rerun()
    with row1[1]: st.markdown('<div class="run-btn">', unsafe_allow_html=True)
    if row1[1].button("2", key="r2", use_container_width=True): update_db({"runs": d['runs']+2, "balls": d['balls']+1}); st.rerun()
    with row1[2]: st.markdown('<div class="run-btn">', unsafe_allow_html=True)
    if row1[2].button("3", key="r3", use_container_width=True): update_db({"runs": d['runs']+3, "balls": d['balls']+1}); st.rerun()

    with row2[0]: st.markdown('<div class="four-btn">', unsafe_allow_html=True)
    if row2[0].button("4", key="r4", use_container_width=True): update_db({"runs": d['runs']+4, "balls": d['balls']+1}); st.rerun()
    with row2[1]: st.markdown('<div class="six-btn">', unsafe_allow_html=True)
    if row2[1].button("6", key="r6", use_container_width=True): update_db({"runs": d['runs']+6, "balls": d['balls']+1}); st.rerun()
    
    # UNDO Logic (Simple reset for this version)
    with row2[2]: st.markdown('<div class="undo-btn">', unsafe_allow_html=True)
    if row2[2].button("UNDO", key="undo", use_container_width=True):
        st.toast("Settings Open")
        if st.checkbox("Confirm Reset Match?"):
            update_db({"runs": 0, "balls": 0, "target": 0})
            st.rerun()

    # Wides Bar
    st.markdown('<div class="extra-header">Wides</div>', unsafe_allow_html=True)
    w_cols = st.columns(5)
    for i in range(5):
        with w_cols[i]: st.markdown('<div class="extra-btn">', unsafe_allow_html=True)
        if w_cols[i].button(f"W+{i}", key=f"w{i}", use_container_width=True):
            update_db({"runs": d['runs'] + 1 + i})
            st.rerun()

    # No Ball Bar
    st.markdown('<div class="extra-header">No Ball</div>', unsafe_allow_html=True)
    n_cols = st.columns(7)
    for i in range(7):
        with n_cols[i]: st.markdown('<div class="extra-btn">', unsafe_allow_html=True)
        if n_cols[i].button(f"N+{i}", key=f"n{i}", use_container_width=True):
            update_db({"runs": d['runs'] + 1 + i})
            st.rerun()

    # Settings Footer
    if st.button("⚙️ MATCH SETUP / OVERLAY LINK", use_container_width=True):
        st.write(f"Overlay Link: `{st.get_option('browser.gatherUsageStats') or 'https://score-easy.streamlit.app/'}?mode=overlay`")
        new_ov = st.number_input("Change Overs", value=d['match_overs'])
        new_tg = st.number_input("Change Target", value=d['target'])
        if st.button("Save Settings"):
            update_db({"match_overs": new_ov, "target": new_tg})
            st.rerun()
