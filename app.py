from flask import Flask, render_template, request, jsonify
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import os

app = Flask(__name__)

model_id = "meta-llama/Llama-3.2-3B-Instruct"
tokenizer = AutoTokenizer.from_pretrained(model_id)
if tokenizer.pad_token_id is None:
    tokenizer.pad_token_id = tokenizer.eos_token_id

SYSTEM_PROMPT = (
    "You are Llama-3.2-3B-Instruct, a helpful and precise assistant."
    " Answer in the user's language, keep context, and be concise unless asked otherwise."
)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype=torch.float16 if device.type == "cuda" else torch.float32,
).to(device)

@app.route("/") 
def index(): 
    return render_template("index.html") 

@app.route("/generate", methods=["POST"])
def generate():
    payload = request.get_json(force=True) or {}
    messages = payload.get("messages")
    user_prompt = payload.get("prompt", "")

    if not messages:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]
    elif messages[0].get("role") != "system":
        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages

    prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
    )

    inputs = tokenizer(prompt, return_tensors="pt", padding=True).to(device)
    with torch.no_grad():  # generation does not require gradients
        outputs = model.generate(**inputs, max_new_tokens=200)

    completion_ids = outputs[:, inputs["input_ids"].shape[-1]:]
    response = tokenizer.decode(completion_ids[0], skip_special_tokens=True).strip()
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=False, use_reloader=False)
