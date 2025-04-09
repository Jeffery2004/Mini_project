import torch
import sys
import ast
import io
import contextlib
import os
import re
import builtins

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from speech_to_code.speech_engine import get_converted_code

from transformers import AutoModelForCausalLM, AutoTokenizer

torch.set_num_threads(4)
MODEL_NAME = "bigcode/starcoderbase-1b"

print("🤖 Starting AI Code Review Script...")

try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, use_fast=True)
    tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
    model.eval()
    print("✅ AI model loaded successfully.\n")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    sys.exit(1)

def auto_initialize_variables(code: str, undefined_vars: set, default_value=10) -> str:
    init_lines = []
    for var in undefined_vars:
        if var != "i" and f"{var} =" not in code:
            init_lines.append(f"{var} = {default_value}")
    return "\n".join(init_lines + [code])

def find_uninitialized_variables(code_snippet):
    try:
        tree = ast.parse(code_snippet)
        declared_vars = set()
        used_vars = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                if isinstance(node.ctx, ast.Store):
                    declared_vars.add(node.id)
                elif isinstance(node.ctx, ast.Load):
                    used_vars.add(node.id)
        return used_vars - declared_vars - set(dir(builtins))
    except Exception:
        return set()

def review_code(code_snippet):
    prompt = (
        "The following Python code may contain syntax errors or uninitialized variables. "
        "Fix any issues, assign example/default values to undefined variables, and return only the corrected code inside triple backticks.\n\n"
        f"{code_snippet}\n\nCorrected Code:"
    )
    try:
        inputs = tokenizer(prompt, return_tensors="pt", padding=True, truncation=True, max_length=512)
        with torch.no_grad():
            output = model.generate(
                input_ids=inputs["input_ids"],
                attention_mask=inputs["attention_mask"],
                max_length=200,
                do_sample=False,
                pad_token_id=tokenizer.eos_token_id
            )
        review_result = tokenizer.decode(output[0], skip_special_tokens=True)
        if "Corrected Code:" in review_result:
            review_result = review_result.split("Corrected Code:")[-1].strip()
        if ""not in review_result:
            cleaned_code = "\n".join(set(review_result.strip().splitlines()))
            review_result = f"python\n{cleaned_code}\n"
        return review_result
    except Exception as e:
        return ""

def extract_optimized_code(generated_text):
    match = re.search(r"(?:python)?\n(.*?)(?:\n)", generated_text, re.DOTALL)
    return match.group(1).strip() if match else ""

def execute_code(code_str):
    output_stream = io.StringIO()
    try:
        with contextlib.redirect_stdout(output_stream):
            exec(code_str)
    except Exception as e:
        return f"❌ Error during execution: {e}"
    return output_stream.getvalue()

def format_output_section(title, content, status_icon="🟢"):
    print(f"{status_icon} {title}\n{'-' * 20}\n{content}\n")

if __name__ == "__main__":
    audio_path = "../speech_to_code/voice3.mp3"
    user_code, transcribed_sentence = get_converted_code(audio_path, return_transcript=True)

    if not user_code:
        format_output_section("1. VOICE TO CODE", "⚠ Could not get code from speech.", "⚠")
        sys.exit()

    format_output_section("1. VOICE TO CODE", user_code)

    uninit_vars = find_uninitialized_variables(user_code)
    if uninit_vars:
        format_output_section("UNDECLARED VARIABLES", f"❌ Uninitialized Variable(s): {', '.join(uninit_vars)}", "🔍")
        user_code = auto_initialize_variables(user_code, uninit_vars)
        print("🔧 Automatically added default values...\n")
    else:
        format_output_section("UNDECLARED VARIABLES", "✅ No undeclared variables found.", "🔍")

    format_output_section("2. AI REVIEW OF THE CODE", "🔍 Reviewing...")

    ai_output = review_code(user_code)
    optimized_code = extract_optimized_code(ai_output)

    if not optimized_code.strip():
        format_output_section("2. AI REVIEW OF THE CODE", "⚠️ AI returned no usable code. Using fallback fix...", "🧠")
        optimized_code = user_code
    else:
        format_output_section("3. AI CORRECTED CODE", optimized_code, "✨")

    print("🚀 4. OUTPUT\n" + "-" * 18)
    result = execute_code(optimized_code)
    print(result)