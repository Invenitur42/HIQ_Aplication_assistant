"""OpenAI-powered resume tailoring and cover letter generation."""

from openai import OpenAI
from app.core.config import get_settings

settings = get_settings()
client = OpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None


def _require_client() -> OpenAI:
    if not client:
        raise RuntimeError("OPENAI_API_KEY is not configured")
    return client


def tailor_resume(
    profile_text: str,
    job_description: str,
    company: str,
    role: str,
) -> str:
    """Generate tailored resume bullet points for a specific job."""
    c = _require_client()
    system = (
        "You are an expert resume writer. Rewrite and prioritize the candidate's experience "
        "to match the target job. Output concise bullet points only. Do not invent employers "
        "or degrees that are not present in the profile. Emphasize relevant skills and impact."
    )
    user = (
        f"Target role: {role} at {company}\n\n"
        f"Job description:\n{job_description}\n\n"
        f"Candidate profile:\n{profile_text}\n\n"
        "Produce 6–10 strong resume bullets tailored to this job."
    )
    resp = c.chat.completions.create(
        model=settings.CHAT_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.4,
        max_tokens=800,
    )
    return resp.choices[0].message.content or ""


def generate_cover_letter(
    profile_text: str,
    job_description: str,
    company: str,
    role: str,
) -> str:
    """Generate a short professional cover letter draft."""
    c = _require_client()
    system = (
        "You are an expert career coach. Write a concise, professional cover letter "
        "(3 short paragraphs). Be specific to the company and role. Do not invent facts "
        "not present in the profile. Avoid clichés."
    )
    user = (
        f"Role: {role}\nCompany: {company}\n\n"
        f"Job description:\n{job_description}\n\n"
        f"Candidate profile:\n{profile_text}\n\n"
        "Write the cover letter body (no postal address block)."
    )
    resp = c.chat.completions.create(
        model=settings.CHAT_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.5,
        max_tokens=700,
    )
    return resp.choices[0].message.content or ""
