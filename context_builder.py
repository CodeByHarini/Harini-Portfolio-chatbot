from faq_data import faq_data

def build_context():
    context = ""

    # Intro
    context += faq_data["intro"] + "\n\n"

    # Skills
    context += "Skills: " + faq_data["skills"] + "\n\n"

    # Projects
    context += "Projects:\n"
    for project, desc in faq_data["projects"].items():
        context += f"- {project}: {desc}\n"
    context += "\n"

    # Contact info
    context += "Contact Information:\n"
    context += f"Email: {faq_data['contact']['email']}\n"
    context += f"LinkedIn: {faq_data['contact']['linkedin']}\n"
    context += f"GitHub: {faq_data['contact']['github']}\n"
    context += "\n"

    # Extra info
    context += f"Education: {faq_data['extra_info']['education']}\n"
    context += f"Certifications: {faq_data['extra_info']['certifications']}\n"
    context += f"Interests: {faq_data['extra_info']['interests']}\n"

    return context

# Preview the first 500 characters
if __name__ == "__main__":
    print(build_context()[:500])
