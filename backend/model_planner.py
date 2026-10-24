
import json
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


PROJECT_DIR = Path(__file__).resolve().parents[1]
MODEL_DIR = (
    PROJECT_DIR
    / "Models"
    / "Coordinator-J_Inference_Model_v1"
)


SYSTEM_MESSAGE = (
    "You are Coordinator-J's tool-selection model. "
    "Choose exactly one tool from the currently available tools "
    "if it can handle the user's request. Otherwise choose null. "
    "Never invent tool names. Never execute tools. "
    "Return only a valid JSON object with the key 'tool'."
)


class ModelPlanner:
    """Loads the trained model once and safely selects registered tools."""

    def __init__(self):
        if not MODEL_DIR.is_dir():
            raise FileNotFoundError(
                f"Model directory not found: {MODEL_DIR}"
            )

        tools_file = MODEL_DIR / "registered_tools.json"
        with tools_file.open("r", encoding="utf-8") as file:
            self.trained_tools = json.load(file)

        print("Loading Coordinator-J tokenizer...")
        self.tokenizer = AutoTokenizer.from_pretrained(
            str(MODEL_DIR),
            local_files_only=True,
        )

        print("Loading Coordinator-J model on CPU...")
        self.model = AutoModelForCausalLM.from_pretrained(
            str(MODEL_DIR),
            local_files_only=True,
            dtype=torch.float32,
        ).to("cpu")

        self.model.eval()
        print("Coordinator-J model ready.")

    def select_tool(
        self,
        request: str,
        available_tools: dict[str, str],
    ) -> str | None:
        """Return a registered tool name, or None if rejected."""

        if not isinstance(request, str) or not request.strip():
            return None

        if not isinstance(available_tools, dict) or not available_tools:
            return None

        # Only offer tools that exist in both the live registry
        # and the model's exported training configuration.
        eligible_tools = {
            name: description
            for name, description in available_tools.items()
            if name in self.trained_tools
            and isinstance(description, str)
            and description.strip()
        }

        if not eligible_tools:
            return None

        messages = [
            {
                "role": "system",
                "content": SYSTEM_MESSAGE,
            },
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "request": request,
                        "available_tools": eligible_tools,
                    },
                    ensure_ascii=False,
                ),
            },
        ]

        prompt = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )

        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=512,
        )

        with torch.inference_mode():
            output_ids = self.model.generate(
                **inputs,
                max_new_tokens=40,
                do_sample=False,
                pad_token_id=self.tokenizer.eos_token_id,
            )

        new_tokens = output_ids[
            0, inputs["input_ids"].shape[1]:
        ]
        raw = self.tokenizer.decode(
            new_tokens,
            skip_special_tokens=True,
        ).strip()

        # Fail closed: invalid output never becomes a tool selection.
        try:
            result = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return None

        if not isinstance(result, dict):
            return None

        if set(result.keys()) != {"tool"}:
            return None

        selected = result["tool"]

        if selected is None:
            return None

        if not isinstance(selected, str):
            return None

        if selected not in eligible_tools:
            return None

        return selected
