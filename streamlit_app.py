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
        # Fetches the live data from Supabase
        return supabase.table("match_data").select("*").eq("id", 1).single().execute().data
    except Exception as e:
        return {"runs": 0, "balls": 0, "match_overs": 8, "target": 0}

def update_db(runs_inc, balls_inc):
    d = get_match()
    supabase.table("match_data").update({
        "runs": d['runs'] + runs_inc,
        "balls": d['balls'] + balls_inc
    }).eq("id", 1).execute()

# --- APP LOGIC ---
params = st.query_params

# 1. DATA API (Hidden: This is what the Ticker talks to)
if params.get("mode") == "data":
    st.write(json.dumps(get_match()))
    st.stop()

# 2. OVERLAY TICKER (Transparent, Professional, Automatic Updates)
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
            .runs-val { font-size: 36px; font-weight: 900; line-height: 1; }
            .ov-val { font-size: 18px; opacity: 0.9; }
            .target-tag { background: black; padding: 3px 10px; border-radius: 0 0 5px 5px; font-size: 13px; font-weight: bold; width: fit-content; margin-top: 5px; }
        </style>

        <div class="ticker-box">
            <div id="status" style="font-size: 10px; letter-spacing: 1px; font-weight: bold;">LIVE MATCH</div>
            <div class="runs-val">
                <span id="r_val">0</span> <span class="ov-val" id="ov_val">(0.0)</span>
            </div>
            <div id="tgt_tag" class="target-tag" style="display:none;">TARGET: <span id="t_val">0</span></div>
        </div>

        <script>
            async function fetchData() {
                try {
                    // Fetch from the same URL but with mode=data
                    const url = window.location.origin + window.location.pathname + '?mode=data';
                    const response = await fetch(url);
                    const d = await response.json();
                    
                    document.getElementById('r_val').innerText = d.runs;
                    document.getElementById('ov_val').innerText = "(" + Math.floor(d.balls/6) + "." + (d.balls%6) + ")";
                    
                    if(d.target > 0) {
                        document.getElementById('tgt_tag').style.display = 'block';
                        document.getElementById('t_val').innerText = d.target;
                    }
                } catch (e) { console.error(e); }
            }
            // Update every 2 seconds
            setInterval(fetchData, 2000);
            fetchData();
        </script>
    """, unsafe_allow_html=True)

# 3. MOBILE SCORER (CricHeroes Style Grid)
else:
    st.markdown("""
        <style>
            /* Force background color */
            .stApp { background-color: #FEE49B !important; }
            
            /* Remove Streamlit padding */
            .block-container { padding: 10px !important; }

            /* Grid Layout for Mobile - 3 Columns Always */
            [data-testid="stHorizontalBlock"] {
                display: flex !important;
                flex-direction: row !important;
                flex-wrap: nowrap !important;
                gap: 8px !important;
            }
            [data-testid="stColumn"] {
                flex: 1 1 0% !important;
                min-width: 0 !important;
            }

            /* Custom Button Styling */
            .stButton>button {
                height: 90px !important;
                font-size: 32px !important;
                font-weight: 800 !important;
                border-radius: 8px !important;
                border: none !important;
                color: #2c3e50 !important;
            }
            
            /* Metric Styling */
            [data-testid="stMetricLabel"] { color: #4A90E2 !important; font-size: 20px !important; font-weight: bold !important; }
            [data-testid="stMetricValue"] { color: #000 !important; font-size: 55px !important; font-weight: 900 !important; }
            
            /* Extras styling */
            .extra-hdr { background: #C65911; color: white; text-align: center; font-weight: bold; padding: 5px; margin: 10px 0; border-radius: 4px; }
        </style>
    """, unsafe_allow_html=True)

    d = get_match()

    # Metrics
    m1, m2 = st.columns(2)
    m1.metric("SCORE", d['runs'])
    m2.metric("OVERS", f"{d['balls']//6}.{d['balls']%6}")

    # Row 1: 1, 2, 3
    c1, c2, c3 = st.columns(3)
    if c1.button("1", key="b1", use_container_width=True): update_db(1, 1); st.rerun()
    if c2.button("2", key="b2", use_container_width=True): update_db(2, 1); st.rerun()
    if c3.button("3", key="b3", use_container_width=True): update_db(3, 1); st.rerun()

    # Row 2: 4, 6, UNDO
    c4, c5, c6 = st.columns(3)
    with c4: st.markdown('<style>div[row-id="b4"] button {background:#00B050 !important;}</style>', unsafe_allow_html=True)
    if c4.button("4", key="b4", use_container_width=True): update_db(4, 1); st.rerun()
    
    with c5: st.markdown('<style>div[row-id="b6"] button {background:#0070C0 !important; color:white !important;}</style>', unsafe_allow_html=True)
    if c5.button("6", key="b6", use_container_width=True): update_db(6, 1); st.rerun()
    
    with c6: st.markdown('<style>div[row-id="bund"] button {background:#F8B195 !important; font-size:18px !important;}</style>', unsafe_allow_html=True)
    if c6.button("UNDO", key="bund", use_container_width=True):
        update_db(-1, -1) # Simple logic: subtract 1 run and 1 ball
        st.rerun()

    # Wides Row
    st.markdown('<div class="extra-hdr">WIDES</div>', unsafe_allow_html=True)
    wcols = st.columns(5)
    for i in range(5):
        if wcols[i].button(f"W+{i}", key=f"w{i}", use_container_width=True):
            update_db(1 + i, 0); st.rerun()

    # No Balls Row
    st.markdown('<div class="extra-hdr">NO BALL</div>', unsafe_allow_html=True)
    ncols = st.columns(7)
    for i in range(7):
        if ncols[i].button(f"N+{i}", key=f"n{i}", use_container_width=True):
            update_db(1 + i, 0); st.rerun()

    # Hidden settings for match setup
    with st.expander("⚙️ Settings"):
        if st.button("RESET MATCH"):
            supabase.table("match_data").update({"runs":0, "balls":0, "target":0}).eq("id", 1).execute()
            st.rerun()
        st.write(f"Overlay Link: `https://score-easy.streamlit.app/?mode=overlay`")
