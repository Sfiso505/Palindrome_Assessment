from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional


app = FastAPI(
    title="Palindrome Interview – HIV & Mental Health Risk API (Prototype)",
    description=(
        "Rule-based prototype for HIV and mental health risk scoring, "
        "built for the Palindrome AI Solutions Engineer assessment. "
        "Not for clinical use."
    ),
    version="1.0.0",
)


# ------------------------------
# DATA MODELS
# ------------------------------

class ConversationRequest(BaseModel):
    conversation_id: Optional[int] = None
    conversation_text: str


class RiskResponse(BaseModel):
    hiv_score: float
    hiv_level: str
    mental_score: float
    mental_level: str
    treatment_plan: str
    hiv_recommendation: str
    mental_recommendation: str
    general_note: str


# ------------------------------
# HELPERS
# ------------------------------

def keyword_count(text: str, keywords) -> int:
    text_lower = text.lower()
    return sum(text_lower.count(k.lower()) for k in keywords)


def hiv_risk_model(user_text: str):
    text = user_text.lower()
    score = 0.0

    high_risk_terms = [
        "no condom", "without a condom", "unprotected",
        "didn't use protection", "raw sex", "multiple partners",
        "new partner", "sex worker", "needle", "inject"
    ]

    medium_risk_terms = [
        "partner tested positive", "partner has hiv", "sti",
        "discharge", "sores", "bleeding", "condom broke",
        "condom slipped", "one-night stand"
    ]

    low_risk_terms = ["kiss", "hug", "sharing utensils"]

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

    rec_lines = [
        "This is not a medical diagnosis. A healthcare professional should always make clinical decisions.",
        f"Based on what you've shared, your HIV acquisition risk is assessed as **{level}** within this simple rule-based model.",
        "General HIV-prevention guidance includes:",
        "- Everyone who is sexually active should know their HIV status. Testing at a clinic or mobile site is strongly encouraged.",
        "- If there has been any possibility of exposure, get an HIV test and ask about tests for other sexually transmitted infections (STIs).",
        "- Consistent condom use and reducing the number of sexual partners help lower future risk.",
        "- If you have ongoing risk, ask a nurse or doctor about HIV pre-exposure prophylaxis (PrEP)."
    ]

    return score, level, "\n".join(rec_lines)


def mental_health_risk_model(user_text: str):
    text = user_text.lower()
    score = 0.0

    stress_terms = ["stressed", "overwhelmed",
                    "worried", "anxious", "can't sleep", "insomnia"]
    depression_terms = [
        "hopeless", "no hope", "empty", "can't go on",
        "no energy", "tired all the time", "lost interest",
        "don't enjoy anything", "crying a lot", "worthless"
    ]
    crisis_terms = [
        "hurt myself", "kill myself", "suicidal",
        "end my life", "self-harm", "cutting"
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

    rec_lines = [
        "This is not a mental health diagnosis. Only a qualified professional can assess and diagnose mental health conditions.",
        f"Based on your messages, emotional/mental health risk is assessed as **{level}** within this simple rule-based model.",
        "General guidance:",
        "- If distress is affecting your sleep, work, studies, or relationships, speak to a healthcare worker or counsellor.",
        "- Public clinics can provide an initial assessment and refer you to counselling or mental health services where needed.",
        "- Trusted helplines and NGOs can offer free phone or WhatsApp support if in-person help is hard to access.",
    ]

    if crisis_flag:
        rec_lines.append(
            "- If you ever feel at risk of harming yourself or others, please seek emergency help immediately at your nearest hospital emergency unit or call an emergency helpline."
        )

    return score, level, "\n".join(rec_lines)


def build_treatment_plan(hiv_level: str, mh_level: str) -> str:
    lines = [f"HIV risk level: {hiv_level}"]

    if hiv_level == "Low":
        lines.append(
            "- Encourage routine HIV testing and reinforce safer-sex practices.")
    elif hiv_level == "Moderate":
        lines.append("- Recommend HIV testing ASAP with STI screening.")
        lines.append("- Discuss PrEP if ongoing risk exists.")
    else:
        lines.append("- Prioritise same-week HIV testing and clinical review.")
        lines.append("- Ensure linkage to prevention/treatment services.")

    lines.append("")
    lines.append(f"Mental health risk level: {mh_level}")

    if mh_level == "Low":
        lines.append(
            "- Provide basic psychoeducation about stress and coping.")
    elif mh_level == "Moderate":
        lines.append("- Recommend assessment by a clinician or counsellor.")
        lines.append("- Consider referral for support services.")
    else:
        lines.append("- Prioritise urgent mental health assessment.")
        lines.append("- Screen for self-harm or suicidal thoughts.")

    lines.append("")
    lines.append(
        "Important: This plan is generated by a prototype model for demonstration only. "
        "Clinical decisions must always be made by qualified healthcare professionals."
    )

    return "\n".join(lines)


# ------------------------------
# ROUTES
# ------------------------------

@app.get("/")
def root():
    return {
        "message": "Palindrome Assessment API running",
        "docs": "Visit /docs for Swagger UI",
    }


@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Service healthy"}


@app.post("/assess", response_model=RiskResponse)
def assess_conversation(payload: ConversationRequest):
    user_text = payload.conversation_text

    hiv_score, hiv_level, hiv_rec = hiv_risk_model(user_text)
    mh_score, mh_level, mh_rec = mental_health_risk_model(user_text)
    plan = build_treatment_plan(hiv_level, mh_level)

    return RiskResponse(
        hiv_score=hiv_score,
        hiv_level=hiv_level,
        mental_score=mh_score,
        mental_level=mh_level,
        treatment_plan=plan,
        hiv_recommendation=hiv_rec,
        mental_recommendation=mh_rec,
        general_note=(
            "This API is a rule-based prototype for an interview assessment. "
            "Not for clinical decision-making."
        ),
    )
