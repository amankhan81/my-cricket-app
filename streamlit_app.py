if params.get("mode") == "overlay":
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Oswald:wght@700&family=Roboto+Condensed:wght@700&display=swap');

            /* Force ALL backgrounds transparent */
            html, body { background: transparent !important; background-color: transparent !important; }
            .stApp { background: transparent !important; background-color: transparent !important; }
            [data-testid="stAppViewContainer"] { background: transparent !important; background-color: transparent !important; }
            [data-testid="stHeader"] { background: transparent !important; display: none !important; }
            [data-testid="stToolbar"] { display: none !important; }
            [data-testid="stDecoration"] { display: none !important; }
            [data-testid="stStatusWidget"] { display: none !important; }
            [data-testid="stMainBlockContainer"] { background: transparent !important; background-color: transparent !important; }
            [data-testid="block-container"] { background: transparent !important; background-color: transparent !important; }
            .main { background: transparent !important; background-color: transparent !important; }
            section[data-testid="stSidebar"] { display: none !important; }
            header, footer, #MainMenu { display: none !important; }

            /* Remove all padding so ticker sits flush top-left */
            .block-container {
                padding: 0 !important;
                margin: 0 !important;
                max-width: 100% !important;
            }

            .ticker {
                position: fixed;
                top: 14px;
                left: 14px;
                display: inline-flex;
                align-items: stretch;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 4px 24px rgba(0,0,0,0.5), 0 1px 4px rgba(0,0,0,0.3);
                font-family: 'Oswald', sans-serif;
            }

            .ticker-accent {
                width: 5px;
                background: linear-gradient(180deg, #f0c040, #c8960a);
                flex-shrink: 0;
            }

            .ticker-body {
                background: rgba(10, 10, 20, 0.88);
                backdrop-filter: blur(12px);
                -webkit-backdrop-filter: blur(12px);
                padding: 10px 16px 10px 12px;
                display: flex;
                align-items: center;
                gap: 10px;
            }

            .ticker-icon { font-size: 18px; line-height: 1; opacity: 0.85; }

            .ticker-score {
                font-size: 42px;
                font-weight: 700;
                color: #ffffff;
                line-height: 1;
                letter-spacing: -1px;
            }

            .ticker-sep {
                width: 1px;
                height: 36px;
                background: rgba(255,255,255,0.15);
                flex-shrink: 0;
            }

            .ticker-overs {
                display: flex;
                flex-direction: column;
                align-items: flex-start;
                gap: 1px;
            }
            .ticker-overs-lbl {
                font-family: 'Roboto Condensed', sans-serif;
                font-size: 9px;
                letter-spacing: 2px;
                color: rgba(255,255,255,0.4);
                text-transform: uppercase;
            }
            .ticker-overs-val {
                font-size: 20px;
                font-weight: 700;
                color: #f0c040;
                line-height: 1;
            }

            .ticker-innings {
                font-family: 'Roboto Condensed', sans-serif;
                font-size: 9px;
                letter-spacing: 1.5px;
                color: rgba(255,255,255,0.3);
                text-transform: uppercase;
                align-self: flex-end;
                padding-bottom: 2px;
            }
        </style>
    """, unsafe_allow_html=True)

    d = get_match()
    innings   = int(d.get("innings") or 1)
    overs_str = f"{d['balls']//6}.{d['balls']%6}"
    max_overs = int(d['match_overs'])
    innings_lbl = f"INN {innings}"

    st.markdown(f"""
        <div class="ticker">
            <div class="ticker-accent"></div>
            <div class="ticker-body">
                <div class="ticker-icon">🏏</div>
                <div class="ticker-score">{d['runs']}</div>
                <div class="ticker-sep"></div>
                <div class="ticker-overs">
                    <div class="ticker-overs-lbl">Overs</div>
                    <div class="ticker-overs-val">{overs_str}</div>
                </div>
                <div class="ticker-sep"></div>
                <div class="ticker-overs">
                    <div class="ticker-overs-lbl">Max</div>
                    <div class="ticker-overs-val">{max_overs}</div>
                </div>
                <div class="ticker-innings">{innings_lbl}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    import time; time.sleep(2); st.rerun()
