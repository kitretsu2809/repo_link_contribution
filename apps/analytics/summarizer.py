"""
AI summarizer for GitHub issues using Gemini API.
"""
import os
import google.generativeai as genai

def summarize_issue(title: str, body: str, max_sentences: int = 3) -> str:
    """
    Generate a concise AI summary of a GitHub issue using Gemini API.

    Args:
        title: The issue title.
        body: The issue body (markdown).
        max_sentences: Number of sentences to include in the summary.

    Returns:
        A plain-text summary string.
    """
    if not body or len(body.strip()) < 50:
        return title.strip()

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return title.strip()

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-flash-latest')
        prompt = f"Summarize the following GitHub issue in a maximum of {max_sentences} sentences. Focus on the core problem and any proposed solution. Do not use markdown.\n\nTitle: {title}\nBody:\n{body[:3000]}"
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error summarizing issue: {e}")
        return title.strip()


def generate_learning_guide(title: str, body: str, state: str = "open", merged_code: str = None) -> str:
    """
    Generate an educational guide for a GitHub issue using Groq API.
    For open issues, suggests a step-by-step solution.
    For closed/resolved interconnected issues, explains the actual merged code.
    """
    if not body or len(body.strip()) < 50:
        return "Not enough context to generate a learning guide."

    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return "AI Learning Guide is unavailable because GROQ_API_KEY is not set."

    try:
        from groq import Groq
        client = Groq(api_key=api_key)
        
        if state == "open":
            prompt = (
                f"You are a helpful senior developer mentoring a junior developer. "
                f"The following GitHub issue was just posted. "
                f"Create a step-by-step tutorial explaining how they could potentially solve this issue. "
                f"Include code examples and explain the real-world concepts behind it.\n\n"
                f"Title: {title}\nBody:\n{body[:3000]}"
            )
        else:
            code_context = f"\nMerged Code:\n{merged_code[:2000]}" if merged_code else ""
            prompt = (
                f"You are a helpful senior developer mentoring a junior developer. "
                f"The following GitHub issue was resolved. "
                f"Explain how this issue was actually solved using the provided merged code context. "
                f"Break down the solution so they can learn deeply how the feature or bug fix works "
                f"and connect it to real-world software engineering concepts.\n\n"
                f"Title: {title}\nBody:\n{body[:2000]}{code_context}"
            )

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama-3.3-70b-versatile",
        )
        return chat_completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating learning guide: {e}")
        return "Failed to generate learning guide."
