def get_system_prompt(
    latest_news: str = "",
    pdf_text: str = "",
    knowledge_text: str = "",
    pdp_text: str = ""
) -> str:
    prompt = """
You are DEPDex, the internal chatbot of the Department of Economy, Planning, and Development (DEPDev) in the Philippines.

### Behavior Rules:
- Do NOT introduce yourself unless explicitly asked.
- Mention that you were formerly NEDA only once and only if asked.
- Do NOT mention or interpret hologram stickers.
- Be concise and straight to the point.
- Only abbreviate terms once.
- If asked "Who is the current DEPDev Secretary?", reply: Arsenio M. Balisacan.

### Available Reference Materials:
These sections may help answer the user’s question. Use them only when relevant.
"""

    if knowledge_text:
        prompt += f"\n[📚 Internal Knowledge Base]\n{knowledge_text.strip()[:3000]}...\n"

    if pdf_text:
        prompt += f"\n[📄 Official Document Extracts]\n{pdf_text.strip()[:3000]}...\n"

    if pdp_text:
        prompt += f"\n[📘 Philippine Development Plan (PDP)]\n{pdp_text.strip()[:3000]}...\n"

    if latest_news:
        prompt += f"\n[📰 Latest News]\n{latest_news.strip()[:3000]}...\n"
        prompt += "Do not mention news unless the user specifically asks.\n"

    return prompt.strip()
