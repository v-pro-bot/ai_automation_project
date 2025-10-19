import google.generativeai as genai

def generate_summary(df, api_key, summary_style="formal"):
    # --- Configure Gemini ---
    genai.configure(api_key=api_key)

    # Use the latest supported model name
    model = genai.GenerativeModel("models/gemini-2.5-flash")

    # Build prompt
    prompt = f"""
    You are an assistant summarizing data in a {summary_style} tone.
    Given the following task data in tabular format, write a concise summary of insights or status updates.
    Data:
    {df.to_string(index=False)}
    """

    # Generate the summary
    response = model.generate_content(prompt)

    return response.text if response and response.text else "No summary generated."
