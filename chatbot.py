import re
from transformers import pipeline
from context_builder import build_context
from faq_data import faq_data

# Build a single context (for fallback)
context = build_context()

# Force PyTorch to avoid TF/Keras issues
qa = pipeline("question-answering",
              model="distilbert-base-uncased-distilled-squad",
              framework="pt")

def _norm(s: str) -> str:
    """lowercase + strip punctuation to simplify matching."""
    return re.sub(r"[^a-z0-9\s]", " ", s.lower())

def _any(q: str, terms: list[str]) -> bool:
    return any(t in q for t in terms)

def answer_from_portfolio(user_q: str) -> str | None:
    q = _norm(user_q)

    # Intro / about / name / title
    if _any(q, ["who are you", "about", "introduce", "yourself", "bio", "who is harini"]):
        return faq_data["intro"]
    if _any(q, ["name"]):
        return "Harini"
    if _any(q, ["title", "role"]):
        return "AI & Data Science Student"

    # Skills
    if _any(q, ["skill", "stack", "tools", "libraries", "tech", "technologies", "expertise"]):
        return faq_data["skills"]

    # Projects
    if "project" in q or _any(q, ["show me your work", "what have you built"]):
        lines = [f"- {p}: {d}" for p, d in faq_data["projects"].items()]
        return "Here are my projects:\n" + "\n".join(lines)

    # Contact bundle
    if _any(q, ["contact", "how can i reach you", "reach you"]):
        c = faq_data["contact"]
        return f"Email: {c['email']}\nLinkedIn: {c['linkedin']}\nGitHub: {c['github']}\nPortfolio: {c['portfolio']}"

    # Individual links
    c = faq_data["contact"]
    if "email" in q or "mail" in q:
        return c["email"]
    if "linkedin" in q or "linked in" in q:
        return c["linkedin"]
    if "github" in q:
        return c["github"]
    if "resume" in q or "cv" in q:
        return c.get("resume", "Resume link not set yet.")
    if _any(q, ["portfolio", "website", "site"]):
        return c["portfolio"]

    return None

def answer(question: str) -> str:
    # 1) Deterministic lookup from your data
    direct = answer_from_portfolio(question)
    if direct:
        return direct

    # 2) Fallback to QA model when not a portfolio intent
    result = qa({"question": question, "context": context})
    return result["answer"]

if __name__ == "__main__":
    print("🤖 Harini's Portfolio Chatbot 🤖")
    print("Type 'exit' to quit.\n")
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            print("Chatbot: Goodbye! 👋")
            break
        print("Chatbot:", answer(user_input), "\n")