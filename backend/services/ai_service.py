import json
from groq import Groq
from utils.config import settings

# Model name - Groq's current fast Llama model
MODEL_NAME = "llama-3.3-70b-versatile"


def get_client() -> Groq:
    return Groq(api_key=settings.GROQ_API_KEY)


def qualify_lead(industry: str, company_size: str, budget: float, description: str) -> dict:
    """
    Sends lead details to the AI and asks it to return a structured
    qualification result: score, temperature, confidence, reasoning, next_action.

    Returns a dict. If the AI call fails for any reason, returns a safe
    fallback so the rest of the app doesn't break.
    """

    prompt = f"""You are a B2B sales qualification expert. Analyze this lead and score it.

Lead details:
- Industry: {industry}
- Company Size: {company_size}
- Estimated Budget: {budget}
- Project Description: {description}

Based on this information, evaluate how good a fit this lead is for a digital agency
that builds websites, software, and AI solutions.

Respond with ONLY a valid JSON object in exactly this format, with no extra text,
no markdown formatting, no code fences:

{{
  "score": <integer 0-100>,
  "temperature": "<Hot, Warm, or Cold>",
  "confidence": <integer 0-100, how confident you are in this assessment>,
  "reasoning": "<one or two sentence explanation of the score>",
  "next_action": "<one sentence recommended next step for the sales team>"
}}"""

    try:
        response = get_client().chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=400,
        )

        raw_text = response.choices[0].message.content.strip()

        # Safety: strip markdown code fences if the model adds them anyway
        if raw_text.startswith("```"):
            raw_text = raw_text.strip("`")
            raw_text = raw_text.replace("json", "", 1).strip()

        result = json.loads(raw_text)

        # Basic validation / clamping
        result["score"] = max(0, min(100, int(result.get("score", 50))))
        result["confidence"] = max(0, min(100, int(result.get("confidence", 50))))
        if result.get("temperature") not in ["Hot", "Warm", "Cold"]:
            result["temperature"] = "Warm"

        return result

    except Exception as e:
        # Fallback so the API never breaks even if Groq fails
        return {
            "score": 50,
            "temperature": "Warm",
            "confidence": 30,
            "reasoning": f"AI scoring failed, using default values. Error: {str(e)}",
            "next_action": "Manually review this lead.",
        }


def personalize_email(name: str, industry: str, description: str) -> str:
    """
    Optional bonus feature: asks the AI to write a short personalized
    acknowledgement email body based on the lead's industry and project.
    """
    prompt = f"""Write a short, warm, professional acknowledgement email (3-4 sentences)
to a potential client named {name} who works in the {industry} industry and is
interested in: {description}

The email is from a digital agency thanking them for their inquiry and saying
the team will reach out soon. Do not include a subject line. Do not use placeholders.
Return only the email body text, no extra formatting."""

    try:
        response = get_client().chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            max_tokens=200,
        )
        return response.choices[0].message.content.strip()
    except Exception:
        # Fallback generic message if AI personalization fails
        return (
            f"Hi {name}, thank you for reaching out to us! "
            f"We've received your inquiry and our team will get back to you shortly."
        )
