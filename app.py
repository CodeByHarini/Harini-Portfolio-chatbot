import gradio as gr
from transformers import pipeline
from context_builder import build_context
from faq_data import faq_data
import re
import time

# ----------------------------
# Load QA Model & Context
# ----------------------------
context = build_context()
qa = pipeline("question-answering", model="distilbert-base-uncased-distilled-squad", framework="pt")

# ----------------------------
# Utility Functions
# ----------------------------
def _norm(s: str):
    return re.sub(r"[^a-z0-9\s]", " ", s.lower())

def _any(q: str, terms: list[str]):
    return any(t in q for t in terms)

def answer_from_portfolio(user_q: str):
    q = _norm(user_q)
    greetings = ["hi", "hello", "hey", "hii", "heyy", "good morning", "good afternoon", "good evening"]

    if any(word in q for word in greetings):
        return "👋 Hey there! I'm Harini's AI assistant. How can I help you today?"

    # Intro
    if _any(q, ["about", "introduce", "yourself", "who are you", "who is harini", "bio"]):
        return faq_data["intro"]

    # Skills
    if _any(q, ["skills", "stack", "tools", "technologies", "expertise"]):
        return faq_data["skills"]

    # Projects
    if "project" in q or "built" in q:
        return "\n".join([f"- {p}: {d}" for p, d in faq_data["projects"].items()])

    # Contact Info
    c = faq_data["contact"]
    if _any(q, ["contact", "reach you", "connect"]):
        return f"📧 Email: {c['email']}\n🔗 LinkedIn: {c['linkedin']}\n💻 GitHub: {c['github']}\n🌐 Portfolio: {c['portfolio']}"
    if "email" in q or "mail" in q:
        return c["email"]
    if "linkedin" in q:
        return c["linkedin"]
    if "github" in q:
        return c["github"]
    if "resume" in q or "cv" in q:
        return c.get("resume", "Resume link not set.")
    if "portfolio" in q or "website" in q:
        return c["portfolio"]

    return None

# ----------------------------
# Chatbot Response
# ----------------------------
def chatbot_response(message, history):
    # Add user message
    history.append({"role": "user", "content": message})

    # Exit condition
    if message.strip().lower() in ["exit", "quit", "bye"]:
        history.append({"role": "assistant", "content": "👋 It was good chatting with you, goodbye!"})
        yield history, gr.update(interactive=False, placeholder="Chat ended. Click Clear Chat to start again.")
        return

    # Typing animation simulation
    yield history + [{"role": "assistant", "content": "💭 Harini's AI is typing…"}], gr.update()
    time.sleep(1.2)

    # Get answer
    ans = answer_from_portfolio(message)
    if not ans:
        ans = qa({"question": message, "context": context})["answer"]

    history.append({"role": "assistant", "content": ans})
    yield history, gr.update()

# ----------------------------
# Reset Chat
# ----------------------------
def reset_chat():
    return (
        [{"role": "assistant", "content": "👋 Hey! I'm Harini's AI assistant. Ask me anything about her portfolio!"}],
        gr.update(interactive=True, placeholder="Ask me anything about Harini...")
    )

# ----------------------------
# Custom CSS
# ----------------------------
custom_css = """
/* Background with subtle animated gradient */
body {
    background: linear-gradient(-45deg, #0f0f0f, #1a1a2e, #2a1f4a, #3b1c73);
    background-size: 400% 400%;
    animation: gradientMove 18s ease infinite;
    font-family: 'Poppins', sans-serif;
    overflow-x: hidden;
}
@keyframes gradientMove {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* Main Container */
.gradio-container {
    background: rgba(255, 255, 255, 0.06);
    backdrop-filter: blur(12px);
    border-radius: 20px;
    padding: 15px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.25);
    position: relative;
}

/* Chat Header */
#chat-header {
    text-align: center;
    font-size: 24px;
    font-weight: 600;
    background: rgba(255, 255, 255, 0.08);
    backdrop-filter: blur(20px);
    color: white;
    padding: 12px;
    border-radius: 16px;
    margin-bottom: 10px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

/* Chat Bubbles */
.gr-chatbot .message {
    border-radius: 18px;
    padding: 12px 16px;
    margin: 6px 0;
    display: flex;
    align-items: center;
    max-width: 75%;
    font-size: 15px;
    line-height: 1.4;
}

/* User messages */
.gr-chatbot .message.user {
    background-color: #25D366;
    color: white;
    margin-left: auto;
    border-bottom-right-radius: 5px;
}

/* Assistant messages */
.gr-chatbot .message.assistant {
    background: linear-gradient(135deg, #ff6ec7, #ff3cac, #784ba0);
    color: white;
    margin-right: auto;
    border-bottom-left-radius: 5px;
}

/* Remove avatars */
.gr-chatbot .message.user::before,
.gr-chatbot .message.assistant::before {
    display: none;
}

/* Input Area */
#input-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
    margin-top: 12px;
    position: sticky;
    bottom: 0;
    padding: 12px;
    background: rgba(0, 0, 0, 0.6);
    backdrop-filter: blur(12px);
    border-radius: 14px;
}

/* Input Box */
textarea {
    background: rgba(255, 255, 255, 0.1);
    color: white !important;
    border: none;
    border-radius: 25px;
    padding: 12px 16px;
    font-size: 15px;
    outline: none;
    flex-grow: 1;
    margin: 0;
}

/* Clear Chat Button */
.clear-btn {
    border-radius: 12px;
    font-weight: bold;
    background: #ff3cac;
    color: white;
    border: none;
    transition: 0.3s ease;
    padding: 12px 20px;
    margin: 0;
}
.clear-btn:hover {
    background: #ff6ec7;
}
"""

# ----------------------------
# Gradio UI
# ----------------------------
with gr.Blocks(css=custom_css, theme=gr.themes.Soft()) as demo:
    gr.Markdown("<div id='chat-header'>💬 Harini's AI Portfolio Chatbot</div>")

    chatbot = gr.Chatbot(
        type="messages",
        label="",
        height=450,
        value=[{"role": "assistant", "content": "👋 Hey! I'm Harini's AI assistant. Ask me anything about her portfolio!"}]
    )

    with gr.Row(elem_id="input-row"):
        msg = gr.Textbox(placeholder="Ask me anything about Harini...", show_label=False)
        clear_btn = gr.Button("🧹 Clear Chat", elem_classes="clear-btn")

    # Submit message via Enter
    msg.submit(chatbot_response, [msg, chatbot], [chatbot, msg], queue=True)
    msg.submit(lambda: "", None, msg)

    # Clear chat button (resets + re-enables textbox)
    clear_btn.click(reset_chat, outputs=[chatbot, msg])

# ----------------------------
# Launch App
# ----------------------------
if __name__ == "__main__":
    demo.launch(share=True)
