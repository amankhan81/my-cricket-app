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

def update_db(updates):
    supabase.table("match_data").update(updates).eq("id", 1).execute()

# --- APP LOGIC ---
params = st.query_params

# 1. THE DATA API (Hidden page that just sends numbers to the overlay)
if params.get("mode") == "data":
    d = get_match()
    st.write(json.dumps(d))
    st.stop()

# 2. THE OVERLAY (The Ticker that never blinks)
elif params.get("mode") == "overlay":
    st.markdown("""
        <style>
            html, body, [data-testid="stAppViewContainer"], .main {
                background: transparent !important;
                background-color: transparent !important;
            }
            header, footer, #MainMenu {display: none !important;}
            .block-container {padding: 0 !important; margin: 0 !important;}

            .ticker-container {
                position: fixed;
                top: 10px;
                left: 10px;
                font-family: 'Arial Black', sans-serif;
            }

            .main-box {
                background: #1B5E20; /* DARK GREEN */
                padding: 12px 20px;
                border-radius: 8px;
                display: flex;
                flex-direction: column;
                min-width: 220px;
                box-shadow: 4px 4px 15px rgba(0,0,0,0.5);
                color: white !important;
            }

            .innings-label { font-size: 11px; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 2px; }
            .score-row { display: flex; align-items: baseline; gap: 10px; }
            .runs { font-size: 38px; font-weight: 900; line-height: 1; }
            .overs { font-size: 18px; font-weight: 600; opacity: 0.8; }
            .target-box {
                background: #000; color: white; padding: 5px 12px;
                border-radius: 0 0 8px 8px; font-size: 14px; font-weight: bold;
                width: fit-content; margin-left: 15px; margin-top: -1px;
            }
        </style>

        <div class="ticker-container">
            <div class="main-box">
                <div id="label" class="innings-label">LOADING...</div>
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
                    // Fetch data from the hidden data page
                    const response = await fetch(window.location.origin + window.location.pathname + '?mode=data');
                    const data = await response.json();
                    
                    const balls = data.balls;
                    const ov = Math.floor(balls / 6) + "." + (balls % 6);
                    
                    document.getElementById('runs').innerText = "Score " + data.runs;
                    document.getElementById('overs').innerText = "Overs " + ov + " (" + data.match_overs + ")";
                    document.getElementById('label').innerText = data.target === 0 ? "1ST INNINGS" : "2ND INNINGS";
                    
                    if(data.target > 0) {
                        document.getElementById('tgt_container').style.display = 'block';
                        document.getElementById('target').innerText = data.target;
                    } else {
                        document.getElementById('tgt_container').style.display = 'none';
                    }
                } catch (e) { console.log("Update failed", e); }
            }
            // Update every 2 seconds without reloading the page
            setInterval(updateScore, 2000);
            updateScore();
        </script>
    """, unsafe_allow_html=True)

# 3. MAIN APP (The Phone Scorer)
else:
    st.markdown("""<style>
        .stButton>button { height: 80px; font-size: 22px !important; font-weight: bold; border-radius: 10px; }
        div[data-testid="column"]:nth-of-type(2) .stButton>button, 
        div[data-testid="column"]:nth-of-type(3) .stButton>button { border-bottom: 5px solid #1B5E20; }
    </style>""", unsafe_allow_html=True)

    if "started" not in st.session_state: st.session_state.started = False
    d = get_match()
    max_balls = d['match_overs'] * 6

    if d['balls'] >= max_balls and d['target'] == 0:
        st.success(f"Innings Over! Score: {d['runs']}")
        if st.button("START 2nd INNINGS", use_container_width=True, type="primary"):
            update_db({"target": d['runs'] + 1, "runs": 0, "balls": 0})
            st.rerun()

    elif not st.session_state.started:
        st.title("🏏 Match Setup")
        overs = st.number_input("Match Overs", min_value=1, value=int(d['match_overs']))
        target = st.number_input("Target", min_value=0, value=int(d['target']))
        if st.button("START MATCH", use_container_width=True, type="primary"):
            update_db({"match_overs": overs, "target": target, "runs": 0, "balls": 0})
            st.session_state.started = True
            st.rerun()
    else:
        m1, m2 = st.columns(2); ov_disp = f"{d['balls']//6}.{d['balls']%6}"
        m1.metric("RUNS", d['runs']); m2.metric("OVERS", f"{ov_disp} / {d['match_overs']}")
        c1, c2, c3 = st.columns(3)
        if c1.button("0", use_container_width=True): update_db({"runs": d['runs'], "balls": d['balls']+1}); st.rerun()
        if c2.button("1", use_container_width=True): update_db({"runs": d['runs']+1, "balls": d['balls']+1}); st.rerun()
        if c3.button("2", use_container_width=True): update_db({"runs": d['runs']+2, "balls": d['balls']+1}); st.rerun()
        c4, c5, c6 = st.columns(3)
        if c4.button("3", use_container_width=True): update_db({"runs": d['runs']+3, "balls": d['balls']+1}); st.rerun()
        if c5.button("4\nBNDRY", use_container_width=True): update_db({"runs": d['runs']+4, "balls": d['balls']+1}); st.rerun()
        if c6.button("6\nBNDRY", use_container_width=True): update_db({"runs": d['runs']+6, "balls": d['balls']+1}); st.rerun()
        c7, c8, c9 = st.columns(3)
        with c7:
            with st.popover("WD", use_container_width=True):
                ex_wd = st.selectbox("Plus Runs", [0,1,2,3,4,6], key="wd")
                if st.button("OK", key="ok_wd", use_container_width=True):
                    update_db({"runs": d['runs'] + 1 + ex_wd}); st.rerun()
        with c8:
            with st.popover("NB", use_container_width=True):
                ex_nb = st.selectbox("Plus Runs", [0,1,2,3,4,6], key="nb")
                if st.button("OK", key="ok_nb", use_container_width=True):
                    update_db({"runs": d['runs'] + 1 + ex_nb}); st.rerun()
        if c9.button("⚙️", use_container_width=True):
            st.session_state.started = False; st.rerun()
