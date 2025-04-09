import whisper
import os
import warnings
import re

warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")

# Load Whisper model
model = whisper.load_model("medium")

# Mapping spoken words to code
spoken_to_code = {
    "open bracket": "(",
    "close bracket": ")",
    "closed bracket": ")",
    "open parenthesis": "(",
    "close parenthesis": ")",
    "open square bracket": "[",
    "close square bracket": "]",
    "closed square bracket": "]",
    "colon": ":",
    "comma": ",",
    "dot": ".",
    "equal to": "=",
    "equals to": "=",
    "equal": "=",
    "double equal to": "==",
    "double equals to": "==",
    "not equal to": "!=",
    "greater than": ">",
    "less than": "<",
    "greater than or equal to": ">=",
    "less than or equal to": "<=",
    "plus": "+",
    "minus": "-",
    "star": "*",
    "slash": "/",
    "modulus": "%",
    "percent": "%",
    "power": "**",
    "not": "not ",
    "and": "and ",
    "or": "or ",
    "double quote": "\"",
    "single quote": "'",
    "double quotes": "\"",
    "single quotes": "'",
    "underscore": "_",
    "hash": "#",
    "space": " ",
    "new line": "\n",
    "indent": "    ",
}

corrections = {
    "diff ": "def ",
    "deaf ": "def ",
    "death ": "def ",
    "prince ": "print ",
    "fr ": "for ",
    "wild ": "while ",
    "loop ": "for ",
}

function_keywords = ["print", "range", "input", "len", "int", "float", "str", "while", "if"]

def convert_speech_to_code(text):
    text = text.lower()

    # Apply corrections
    for wrong, right in corrections.items():
        text = text.replace(wrong, right)

    # Convert spoken phrases to code using regex word boundaries
    for spoken, code in spoken_to_code.items():
        pattern = rf"\b{re.escape(spoken)}\b"
        text = re.sub(pattern, code, text)

    # Clean ending dots on words like "print."
    words = text.split()
    cleaned_words = []
    for w in words:
        if w.endswith('.') and not w.replace('.', '', 1).isdigit():
            cleaned_words.append(w[:-1])
        else:
            cleaned_words.append(w)
    text = ' '.join(cleaned_words)

    # Wrap function arguments in parentheses
    for keyword in function_keywords:
        pattern = rf"\b{keyword}\s+((?:[a-zA-Z0-9_+\-*/<>= ]+,?\s*)+)"
        match = re.search(pattern, text)
        if match:
            content = match.group(1).strip()
            if not content.startswith("("):
                wrapped = f"{keyword}({content})"
                text = re.sub(pattern, wrapped, text, count=1)

    # Handle indentation for control structures
    lines = []
    blocks = re.split(r"(if .*?:|elif .*?:|else:)", text)
    current_indent = ""

    for i, block in enumerate(blocks):
        block = block.strip()
        if not block:
            continue
        if block.startswith(("if", "elif", "else")):
            current_indent = ""
            lines.append(f"{block}")
        else:
            lines.append(f"    {block}")

    if len(lines) > 1:
        return "\n".join(lines)

    # Fallback indentation for single-line code blocks
    if ":" in text:
        before, after = text.split(":", 1)
        return f"{before.strip()}:\n    {after.strip()}"

    return text

def get_converted_code(audio_path, save_output=False, return_transcript=False):
    audio_path = os.path.abspath(audio_path)

    if os.path.exists(audio_path):
        print(f"✅ File exists! Transcribing from: {audio_path}")
        try:
            result = model.transcribe(audio_path, language="en")
            transcription = result["text"].strip()
            print(f"🎤 Transcribed Sentence: {transcription}")

            converted_code = convert_speech_to_code(transcription)

            if save_output:
                with open("output_code.py", "w") as f:
                    f.write(converted_code)
                print("\n💾 Code saved to output_code.py")

            if return_transcript:
                return converted_code, transcription
            return converted_code

        except Exception as e:
            print("❌ Error during transcription:", e)
            return (None, None) if return_transcript else None
    else:
        print(f"❌ File NOT found at: {audio_path}")
        print("📁 Available files in directory:")
        print(os.listdir(os.path.dirname(audio_path)))
        return (None, None) if return_transcript else None