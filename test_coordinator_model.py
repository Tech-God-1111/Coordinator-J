
import json
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

MODEL_DIR = (
    r"D:\PyCharmMiscProject\Coordinator-J\Models"
    r"\Coordinator-J_Inference_Model_v1"
)

SYSTEM_MESSAGE = (
    "You are Coordinator-J's tool-selection model. "
    "Choose exactly one available tool if it can handle the request. "
    "Otherwise choose null. Never invent tool names or execute tools. "
    "Return only a valid JSON object with the key 'tool'."
)

TOOLS = {
    "project_status": "Show Coordinator-J development status.",
    "help": "List supported commands and tools.",
}

print("Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(
    MODEL_DIR, local_files_only=True
)

print("Loading model into CPU memory...")
model = AutoModelForCausalLM.from_pretrained(
    MODEL_DIR,
    local_files_only=True,
    dtype=torch.float32,
).to("cpu")

model.eval()
print("Model loaded successfully!")

messages = [
    {"role": "system", "content": SYSTEM_MESSAGE},
    {
        "role": "user",
        "content": json.dumps({
            "request": "Show me Coordinator-J's development status.",
            "available_tools": TOOLS,
        }),
    },
]

prompt = tokenizer.apply_chat_template(
    messages,
    tokenize=False,
    add_generation_prompt=True,
)

inputs = tokenizer(
    prompt,
    return_tensors="pt",
    truncation=True,
    max_length=512,
)

print("Running test inference...")
with torch.inference_mode():
    output_ids = model.generate(
        **inputs,
        max_new_tokens=40,
        do_sample=False,
        pad_token_id=tokenizer.eos_token_id,
    )

new_tokens = output_ids[0, inputs["input_ids"].shape[1]:]
result = tokenizer.decode(
    new_tokens, skip_special_tokens=True
).strip()

print("\nRaw model response:")
print(result)
