"""LLM classifier via OpenRouter. Needs OPENROUTER_API_KEY in the environment; nothing is stored."""
import json
import os
import urllib.request

LABELS = ["positive", "info_request", "not_interested", "unsubscribe",
          "out_of_office", "left_company", "wrong_person", "other"]

PROMPT = """You classify replies to cold sales emails. Reply with ONE label only.

positive: wants a call or to move forward, or asks for times
info_request: asks a question (price, process, proof) without committing
not_interested: declines, already covered, not a priority, no budget
unsubscribe: wants to be removed or never contacted again (wins over not_interested)
out_of_office: automatic away message or says they are away and will reply later
left_company: person no longer works there (auto or manual)
wrong_person: not their area; points to someone else or says wrong company
other: acknowledgements, "maybe later", anything else

Reply text:
\"\"\"{text}\"\"\"

Answer with only the label."""


def classify_llm(text: str, model: str = "openai/gpt-4o-mini") -> tuple[str, None]:
    key = os.environ["OPENROUTER_API_KEY"]
    body = json.dumps({"model": model, "temperature": 0, "max_tokens": 8,
                       "messages": [{"role": "user", "content": PROMPT.format(text=text)}]}).encode()
    req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", data=body,
                                 headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        out = json.load(r)["choices"][0]["message"]["content"].strip().lower()
    label = next((l for l in LABELS if l in out), "other")
    return label, None
