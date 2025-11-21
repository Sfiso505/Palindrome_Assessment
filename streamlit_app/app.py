import streamlit as st


# Core logic (mirrors notebook / API)

def keyword_count(text: str, keywords) -> int:
    text_lower = text.lower()
    return sum(text_lower.count(k.lower()) for k in keywords)


def hiv_risk_model(user_text: str):
    text = user_text.lower()
    score = 0.0

    high_risk_terms = [
        "no condom",
        "without a condom",
        "unprotected",
        "didn't use protection",
        "raw sex",
        "multiple partners",
        "new partner",
        "sex worker",
        "needle",
        "inject",
    ]
    medium_risk_terms = [
        "partner tested positive",
        "partner has hiv",
        "sti",
        "discharge",
        "sores",
        "bleeding",
        "condom broke",
        "condom slipped",
        "one-night stand",
    ]
    low_risk_terms = [
        "kiss",
        "hug",
        "sharing utensils",
    ]

    score += 0.25 * keyword_count(text, low_risk_terms)
    score += 0.5 * keyword_count(text, medium_risk_terms)
    score += 1.0 * keyword_count(text, high_risk_terms)

    score = min(score, 3.0) / 3.0

    if "test" in text or "testing" in text:
        score = max(score, 0.2)

    if score < 0.25:
        level = "Low"
    elif score < 0.6:
        level = "Moderate"
    else:
        level = "High"

    return score, level


def mental_health_risk_model(user_text: str):
    text = user_text.lower()
    score = 0.0

    stress_terms = ["stressed", "overwhelmed",
                    "worried", "anxious", "can't sleep", "insomnia"]
    depression_terms = [
        "hopeless",
        "no hope",
        "empty",
        "can't go on",
        "no energy",
        "tired all the time",
        "lost interest",
        "don't enjoy anything",
        "crying a lot",
        "worthless",
    ]
    crisis_terms = [
        "hurt myself",
        "kill myself",
        "suicidal",
        "end my life",
        "self-harm",
        "cutting",
    ]

    score += 0.3 * keyword_count(text, stress_terms)
    score += 0.6 * keyword_count(text, depression_terms)
    score += 1.5 * keyword_count(text, crisis_terms)

    if "stressed" in text or "worried" in text:
        score = max(score, 0.2)

    score = min(score, 3.0) / 3.0

    if score < 0.25:
        level = "Low"
    elif score < 0.6:
        level = "Moderate"
    else:
        level = "High"

    crisis_flag = any(term in text for term in crisis_terms)
    return score, level, crisis_flag


def build_recommendations(hiv_level: str, mh_level: str, crisis_flag: bool):
    hiv_lines = [f"**HIV risk level:** {hiv_level}"]
    if hiv_level == "Low":
        hiv_lines.extend(
            [
                "- Encourage routine HIV testing as part of normal care.",
                "- Reinforce safer-sex practices and consistent condom use.",
            ]
        )
    elif hiv_level == "Moderate":
        hiv_lines.extend(
            [
                "- Recommend HIV testing as soon as possible at a clinic or community testing site.",
                "- Consider screening for other STIs and discussing PrEP for ongoing risk.",
            ]
        )
    else:  # High
        hiv_lines.extend(
            [
                "- Prioritise same-week HIV testing and clinical assessment.",
                "- Ensure linkage to prevention or treatment services and arrange follow-up.",
            ]
        )

    mh_lines = [f"**Mental health risk level:** {mh_level}"]
    if mh_level == "Low":
        mh_lines.extend(
            [
                "- Provide basic psychoeducation about stress and coping.",
                "- Encourage the person to return if symptoms worsen.",
            ]
        )
    elif mh_level == "Moderate":
        mh_lines.extend(
            [
                "- Recommend assessment by a nurse, doctor or counsellor.",
                "- Consider referral for counselling or support services.",
            ]
        )
    else:  # High
        mh_lines.extend(
            [
                "- Prioritise urgent mental health assessment.",
                "- Screen carefully for self-harm or suicide risk.",
            ]
        )

    if crisis_flag:
        mh_lines.append(
            "- If there is any immediate risk of self-harm or harm to others, "
            "seek emergency care or contact an emergency helpline immediately."
        )

    disclaimer = (
        "⚠️ **Disclaimer:** This tool is a rule-based prototype built for an interview assessment. "
    )

    return "\n".join(hiv_lines), "\n".join(mh_lines), disclaimer


# ---------- Streamlit UI ----------

st.set_page_config(
    page_title="HIV & Mental Health Risk Prototype",
    layout="wide",
)

st.title("HIV & Mental Health Risk Assessment (Prototype)")
st.write(
    "This Streamlit app demonstrates a simple, rule-based model for assessing synthetic "
    "conversations about HIV risk and mental health. It was built for the Palindrome "
    "AI Solutions Engineer interview. **It is not a clinical tool.**"
)

example_text = (
    "[2024-03-10 08:15] User: Hi, I had unprotected sex with a new partner last weekend.\n"
    "[2024-03-10 08:16] User: I'm really stressed and can't sleep because I'm worried about HIV.\n"
    "[2024-03-10 08:17] User: What should I do?"
)

conversation_text = st.text_area(
    "Paste a synthetic WhatsApp-style conversation or free-text description:",
    value=example_text,
    height=220,
)

if st.button("Assess conversation"):
    if not conversation_text.strip():
        st.warning("Please paste some text first.")
    else:
        # Very simple: treat the entire input as 'user text' for this demo
        user_text_only = conversation_text

        hiv_score, hiv_level = hiv_risk_model(user_text_only)
        mh_score, mh_level, crisis_flag = mental_health_risk_model(
            user_text_only)
        hiv_rec, mh_rec, disclaimer = build_recommendations(
            hiv_level, mh_level, crisis_flag)

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("HIV Risk")
            st.metric("HIV risk level", hiv_level,
                      f"score: {hiv_score:.2f} (0–1)")
            st.markdown(hiv_rec)

        with col2:
            st.subheader("Mental Health Risk")
            st.metric("Mental health level", mh_level,
                      f"score: {mh_score:.2f} (0–1)")
            st.markdown(mh_rec)

        st.markdown("---")
        st.markdown(disclaimer)
else:
    st.info(
        "Paste a conversation and click **Assess conversation** to run the prototype.")
