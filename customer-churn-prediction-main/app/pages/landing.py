"""
ChurnGuard AI — Futuristic Landing & Authentication View

Keeps the existing SQLite-backed authentication functions while refreshing
the unauthenticated landing page with a dark neon-purple visual style.
"""

import os
import sys
import textwrap

import streamlit as st

# Ensure src is in sys.path
SRC_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "src",
)
if SRC_DIR not in sys.path:
    sys.path.append(SRC_DIR)

from auth import authenticate_user, register_user
from components.ui import render_footer, apply_custom_css



def _render_html(markup, unsafe_allow_html=True):
    """Render HTML without Markdown interpreting indented lines as code."""
    cleaned = textwrap.dedent(markup).strip()
    # Markdown treats lines indented by four spaces as code blocks.
    # HTML indentation is not meaningful, so remove it from every line.
    cleaned = "\n".join(line.lstrip() for line in cleaned.splitlines())
    st.markdown(cleaned, unsafe_allow_html=unsafe_allow_html)


def _render_visual_panel():
    """Render the left-side brand and product preview."""

    _render_html(
        """
        <div class="cg-landing-visual">
            <div class="cg-landing-brand">
                <div class="cg-brand-mark">✦</div>
                <div>
                    <div class="cg-brand-name">ChurnGuard<span> AI</span></div>
                    <div class="cg-brand-caption">CUSTOMER INTELLIGENCE</div>
                </div>
            </div>

            <div class="cg-landing-copy">
                <div class="cg-eyebrow">
                    <span class="cg-eyebrow-dot"></span>
                    AI-POWERED RETENTION PLATFORM
                </div>

                <h1>See churn<br/>before it <span>happens.</span></h1>

                <p>
                    Turn customer signals into smarter decisions.
                    Predict risk, understand behavior, and take action
                    with confidence.
                </p>
            </div>

            <div class="cg-orb-stage">
                <div class="cg-orb-glow"></div>
                <div class="cg-orb"></div>
                <div class="cg-orb-ring cg-ring-one"></div>
                <div class="cg-orb-ring cg-ring-two"></div>
                <div class="cg-orb-spark cg-spark-one"></div>
                <div class="cg-orb-spark cg-spark-two"></div>
                <div class="cg-orb-spark cg-spark-three"></div>
            </div>

            <div class="cg-preview-panel">
                <div class="cg-preview-heading">
                    <span>RETENTION OVERVIEW</span>
                    <span class="cg-live-label">● LIVE PREVIEW</span>
                </div>
                <div class="cg-preview-stats">
                    <div>
                        <div class="cg-preview-value">7,043</div>
                        <div class="cg-preview-label">Customer profiles</div>
                    </div>
                    <div>
                        <div class="cg-preview-value cg-cyan">84.8%</div>
                        <div class="cg-preview-label">Model ROC-AUC</div>
                    </div>
                    <div>
                        <div class="cg-preview-value cg-pink">26.5%</div>
                        <div class="cg-preview-label">Historical churn</div>
                    </div>
                </div>
                <div class="cg-preview-bars">
                    <span style="height:30%"></span>
                    <span style="height:48%"></span>
                    <span style="height:38%"></span>
                    <span style="height:65%"></span>
                    <span style="height:54%"></span>
                    <span style="height:82%"></span>
                    <span style="height:70%"></span>
                    <span style="height:96%"></span>
                    <span style="height:75%"></span>
                    <span style="height:88%"></span>
                    <span style="height:60%"></span>
                    <span style="height:78%"></span>
                </div>
            </div>

            <div class="cg-landing-footnote">
                <span>Predict.</span>
                <span>Prevent.</span>
                <span>Retain.</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_auth_panel():
    """Render login and registration forms using Streamlit controls."""

    _render_html(
        """
        <div class="cg-auth-heading">
            <div class="cg-auth-kicker">YOUR WORKSPACE AWAITS</div>
            <h2>Welcome back<span>.</span></h2>
            <p>Sign in to your account or create a workspace to get started.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab_login, tab_register = st.tabs(["Sign In", "Create Account"])

    with tab_login:
        with st.form("cg_login_form", clear_on_submit=False):
            login_email = st.text_input(
                "Work Email",
                placeholder="name@company.com",
                key="in_login_email",
            )
            login_pwd = st.text_input(
                "Password",
                type="password",
                placeholder="Enter your password",
                key="in_login_pwd",
            )
            login_submit = st.form_submit_button(
                "Sign in to ChurnGuard  →",
                use_container_width=True,
            )

        if login_submit:
            if not login_email.strip() or not login_pwd:
                st.error("Please enter both email and password.")
            else:
                user, msg = authenticate_user(
                    login_email.strip(),
                    login_pwd,
                )
                if user:
                    st.session_state["authenticated"] = True
                    st.session_state["user"] = user
                    st.session_state["current_page"] = "Dashboard"
                    st.success("Sign in successful. Opening your workspace...")
                    st.rerun()
                else:
                    st.error(msg)

        st.markdown(
            """
            <div class="cg-auth-note">
                Protected workspace access
                <span>·</span>
                Customer intelligence dashboard
            </div>
            """,
            unsafe_allow_html=True,
        )

    with tab_register:
        with st.form("cg_register_form", clear_on_submit=False):
            reg_name = st.text_input(
                "Full Name",
                placeholder="e.g. Sarah Connor",
                key="reg_name",
            )
            reg_email = st.text_input(
                "Work Email",
                placeholder="name@company.com",
                key="reg_email",
            )
            reg_org = st.text_input(
                "Organization",
                placeholder="e.g. Metro Telecom",
                key="reg_org",
            )
            reg_role = st.text_input(
                "Role",
                placeholder="e.g. Retention Manager",
                key="reg_role",
            )
            reg_p1 = st.text_input(
                "Password",
                type="password",
                placeholder="Create a password",
                key="reg_p1",
            )
            reg_p2 = st.text_input(
                "Confirm Password",
                type="password",
                placeholder="Re-enter your password",
                key="reg_p2",
            )

            register_submit = st.form_submit_button(
                "Create workspace account  →",
                use_container_width=True,
            )

        if register_submit:
            success, msg = register_user(
                reg_name.strip(),
                reg_email.strip(),
                reg_org.strip(),
                reg_role.strip(),
                reg_p1,
                reg_p2,
            )
            if success:
                st.success(msg)
            else:
                st.error(msg)


def render_landing_page():
    """Render the refreshed landing and authentication screen."""

    st.markdown(
        textwrap.dedent("""
        <style>
        /* Landing-only layout and theme */
        .block-container {
            max-width: 1420px !important;
            padding-top: 2rem !important;
            padding-bottom: 1.5rem !important;
        }

        .cg-landing-visual {
            position: relative;
            min-height: 690px;
            overflow: hidden;
            padding: 34px 36px 26px;
            border: 1px solid rgba(151, 91, 255, 0.24);
            border-radius: 26px;
            background:
                radial-gradient(ellipse at 52% 48%, rgba(111, 35, 218, .18), transparent 40%),
                radial-gradient(ellipse at 10% 5%, rgba(48, 207, 255, .07), transparent 35%),
                linear-gradient(145deg, rgba(19, 9, 48, .98), rgba(7, 5, 25, .98));
            box-shadow: 0 24px 80px rgba(0, 0, 0, .24);
        }

        .cg-landing-brand {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .cg-brand-mark {
            display: flex;
            align-items: center;
            justify-content: center;
            width: 42px;
            height: 42px;
            border-radius: 13px;
            color: white;
            font-size: 25px;
            background: linear-gradient(135deg, #9B38FF, #34DFFF);
            box-shadow: 0 0 25px rgba(139, 46, 255, .35);
        }

        .cg-brand-name {
            color: #F7F4FF;
            font-size: 1.12rem;
            font-weight: 800;
            letter-spacing: -.03em;
        }

        .cg-brand-name span {
            color: #45DFFF;
        }

        .cg-brand-caption {
            color: #9288BA;
            font-size: .58rem;
            letter-spacing: .18em;
            margin-top: 2px;
        }

        .cg-landing-copy {
            position: relative;
            z-index: 2;
            margin-top: 62px;
            max-width: 530px;
        }

        .cg-eyebrow {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            color: #BCA0FF;
            font-size: .68rem;
            font-weight: 700;
            letter-spacing: .13em;
        }

        .cg-eyebrow-dot {
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background: #3FE4FF;
            box-shadow: 0 0 12px #3FE4FF;
        }

        .cg-landing-copy h1 {
            color: #F7F4FF;
            font-size: clamp(2.4rem, 4vw, 4.2rem);
            font-weight: 850;
            line-height: 1.05;
            letter-spacing: -.055em;
            margin: 18px 0 16px;
        }

        .cg-landing-copy h1 span {
            color: #C16BFF;
            background: linear-gradient(90deg, #B95CFF, #42E2FF);
            -webkit-background-clip: text;
            background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .cg-landing-copy p {
            max-width: 460px;
            color: #B5ACD2;
            font-size: .94rem;
            line-height: 1.8;
        }

        .cg-orb-stage {
            position: relative;
            height: 250px;
            margin-top: -2px;
        }

        .cg-orb-glow {
            position: absolute;
            width: 300px;
            height: 175px;
            left: 50%;
            top: 50%;
            transform: translate(-50%, -42%);
            border-radius: 50%;
            background: radial-gradient(ellipse, rgba(137, 44, 255, .35), rgba(41, 205, 255, .12) 45%, transparent 72%);
            filter: blur(20px);
        }

        .cg-orb {
            position: absolute;
            left: 50%;
            top: 50%;
            width: 165px;
            height: 165px;
            transform: translate(-50%, -48%) rotate(-20deg);
            border-radius: 43% 57% 60% 40% / 42% 42% 58% 58%;
            background:
                radial-gradient(circle at 28% 23%, rgba(255,255,255,.92), transparent 13%),
                radial-gradient(circle at 35% 30%, #FF8AF4, transparent 34%),
                radial-gradient(circle at 68% 68%, #23DFFF, transparent 43%),
                linear-gradient(135deg, #7D28F4 5%, #E65DFF 42%, #27CFFF 80%);
            box-shadow:
                inset -18px -20px 32px rgba(14, 4, 51, .45),
                inset 12px 10px 25px rgba(255,255,255,.22),
                0 0 55px rgba(155, 50, 255, .35);
            animation: cg-float 7s ease-in-out infinite;
        }

        .cg-orb-ring {
            position: absolute;
            left: 50%;
            top: 50%;
            width: 260px;
            height: 100px;
            border: 1px solid rgba(95, 220, 255, .28);
            border-radius: 50%;
            transform: translate(-50%, -42%) rotate(-24deg);
        }

        .cg-ring-two {
            width: 300px;
            height: 125px;
            border-color: rgba(192, 91, 255, .23);
            transform: translate(-50%, -42%) rotate(24deg);
        }

        .cg-orb-spark {
            position: absolute;
            width: 11px;
            height: 11px;
            border-radius: 50%;
            background: #46E5FF;
            box-shadow: 0 0 18px #46E5FF;
        }

        .cg-spark-one { left: 20%; top: 34%; }
        .cg-spark-two { right: 20%; top: 25%; background:#F57BFF; box-shadow:0 0 18px #F57BFF; }
        .cg-spark-three { right: 28%; bottom: 16%; width:6px; height:6px; }

        @keyframes cg-float {
            0%, 100% { transform: translate(-50%, -48%) rotate(-20deg); }
            50% { transform: translate(-50%, -54%) rotate(-8deg); }
        }

        .cg-preview-panel {
            position: relative;
            z-index: 2;
            padding: 15px 17px 13px;
            border: 1px solid rgba(155, 109, 255, .22);
            border-radius: 16px;
            background: rgba(12, 7, 34, .72);
            backdrop-filter: blur(12px);
        }

        .cg-preview-heading {
            display: flex;
            justify-content: space-between;
            color: #AFA3D2;
            font-size: .62rem;
            font-weight: 700;
            letter-spacing: .1em;
        }

        .cg-live-label {
            color: #50E3C2;
            letter-spacing: .04em;
        }

        .cg-preview-stats {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
            margin-top: 13px;
        }

        .cg-preview-value {
            color: #F7F4FF;
            font-size: 1.2rem;
            font-weight: 800;
        }

        .cg-cyan { color: #42E2FF; }
        .cg-pink { color: #F17AFF; }

        .cg-preview-label {
            color: #9288BA;
            font-size: .62rem;
            margin-top: 3px;
        }

        .cg-preview-bars {
            display: flex;
            align-items: end;
            gap: 7px;
            height: 42px;
            margin-top: 13px;
            padding-top: 7px;
            border-top: 1px solid rgba(160, 130, 220, .12);
        }

        .cg-preview-bars span {
            flex: 1;
            border-radius: 4px 4px 1px 1px;
            background: linear-gradient(180deg, #42E2FF, #8137FF 70%, rgba(129,55,255,.22));
            opacity: .78;
        }

        .cg-landing-footnote {
            display: flex;
            gap: 7px;
            margin-top: 18px;
            color: #A99BCB;
            font-size: .7rem;
            letter-spacing: .06em;
        }

        .cg-landing-footnote span:nth-child(2) { color: #C17AFF; }
        .cg-landing-footnote span:nth-child(3) { color: #42E2FF; }

        .cg-auth-heading {
            padding: 14px 5px 22px;
        }

        .cg-auth-kicker {
            color: #9D7CFF;
            font-size: .68rem;
            font-weight: 800;
            letter-spacing: .16em;
        }

        .cg-auth-heading h2 {
            margin: 9px 0 7px;
            color: #F7F4FF;
            font-size: 2.15rem;
            font-weight: 800;
            letter-spacing: -.045em;
        }

        .cg-auth-heading h2 span { color: #42E2FF; }

        .cg-auth-heading p {
            color: #AFA6CE;
            font-size: .88rem;
            line-height: 1.65;
        }

        div[data-baseweb="tab-list"] {
            gap: 8px;
            border-bottom: 1px solid rgba(155, 109, 255, .18);
        }

        button[data-baseweb="tab"] {
            color: #AFA6CE;
            font-weight: 700;
        }

        button[data-baseweb="tab"][aria-selected="true"] {
            color: #F7F4FF;
            border-bottom-color: #42E2FF;
        }

        div[data-testid="stForm"] {
            padding: 18px 19px 16px;
            border: 1px solid rgba(155, 109, 255, .22);
            border-radius: 18px;
            background: linear-gradient(145deg, rgba(20, 11, 49, .85), rgba(9, 6, 27, .92));
            box-shadow: 0 16px 42px rgba(0, 0, 0, .22);
        }

        div[data-testid="stForm"] label {
            color: #D8D0F1 !important;
            font-size: .78rem !important;
            font-weight: 600 !important;
        }

        div[data-testid="stForm"] input {
            border-radius: 9px !important;
            background: #140B35 !important;
            border-color: rgba(155, 109, 255, .22) !important;
        }

        div[data-testid="stForm"] input:focus {
            border-color: #42E2FF !important;
            box-shadow: 0 0 0 1px rgba(66, 226, 255, .18) !important;
        }

        div[data-testid="stForm"] button[kind="primaryFormSubmit"],
        div[data-testid="stForm"] button[type="submit"] {
            min-height: 43px;
            border: 1px solid rgba(200, 145, 255, .45) !important;
            border-radius: 10px !important;
            color: white !important;
            font-weight: 750 !important;
            background: linear-gradient(100deg, #8B2EFF, #6420D8) !important;
            box-shadow: 0 6px 22px rgba(139, 46, 255, .22) !important;
        }

        div[data-testid="stForm"] button:hover {
            border-color: #42E2FF !important;
            background: linear-gradient(100deg, #A33DFF, #7130E8) !important;
        }

        .cg-auth-note {
            margin-top: 17px;
            color: #8277A8;
            text-align: center;
            font-size: .68rem;
        }

        .cg-auth-note span {
            color: #42E2FF;
            padding: 0 5px;
        }

        @media (max-width: 900px) {
            .cg-landing-visual {
                min-height: auto;
                padding: 25px 22px;
                margin-bottom: 24px;
            }

            .cg-landing-copy {
                margin-top: 38px;
            }

            .cg-orb-stage {
                height: 205px;
            }

            .cg-preview-stats {
                gap: 6px;
            }
        }

        @media (prefers-reduced-motion: reduce) {
            .cg-orb { animation: none; }
        }
        </style>
        """).strip(),
        unsafe_allow_html=True,
    )

    left_col, right_col = st.columns(
        [1.08, 0.92],
        gap="large",
        vertical_alignment="center",
    )

    with left_col:
        _render_visual_panel()

    with right_col:
        _render_auth_panel()

    render_footer()


if __name__ == "__main__":
    apply_custom_css()
    render_landing_page()
