import subprocess
import tempfile
import os
import re
import datetime
import json
import sys
from typing import Tuple
import google.generativeai as genai
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import TerminalFormatter

# === Configure Gemini ===
GEMINI_API_KEY = "AIzaSyBRzQCetzqXL9aQDcQw8T2C0rnzRxIYTTw"
genai.configure(api_key=GEMINI_API_KEY)
GEMINI_MODEL_NAME = 'models/gemini-2.0-flash-lite'

gemini_model = genai.GenerativeModel(model_name=GEMINI_MODEL_NAME)

# === Globals ===
session_history = []  # stores dicts: { 'desc': str, 'code': str, 'timestamp': datetime }
LOG_FILE = "gemini_codegen_session.log"

# === Logging ===
def log(message: str):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {message}\n"
    with open(LOG_FILE, "a") as f:
        f.write(entry)

# === Utilities ===
def syntax_highlight(code: str) -> str:
    return highlight(code, PythonLexer(), TerminalFormatter())

def ask_gemini(prompt: str, temperature=0.2, max_tokens=1500) -> str:
    system_prompt = (
        "You are a helpful Python assistant. Only return the Python code. "
        "Do not include markdown, triple backticks, or explanation. Just return code."
    )
    final_prompt = f"{system_prompt}\n\n{prompt}"
    log(f"Prompt sent to Gemini: {final_prompt[:200]}...")

    try:
        response = gemini_model.generate_content(final_prompt)
        raw_text = response.text.strip()
    except Exception as e:
        log(f"Error contacting Gemini API: {e}")
        return ""

    # Clean markdown and unwanted text
    clean_code = re.sub(r"```(?:python)?\n(.*?)```", r"\1", raw_text, flags=re.DOTALL)
    clean_code = clean_code.replace("```", "")
    clean_code = re.sub(r"^(#.*)?(Here is|Here's|Below is).*", "", clean_code, flags=re.IGNORECASE).strip()
    return clean_code

def run_code(code_str: str) -> Tuple[bool, str, str]:
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as tmp_file:
        tmp_file.write(code_str)
        filename = tmp_file.name

    try:
        result = subprocess.run(
            [sys.executable, filename],
            capture_output=True,
            text=True,
            timeout=20
        )
        return (result.returncode == 0), result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Execution timed out."
    except Exception as e:
        return False, "", f"Exception during execution: {e}"
    finally:
        os.remove(filename)

def save_code_to_file(code: str, desc: str = "generated") -> str:
    safe_desc = re.sub(r"[^\w\-]", "_", desc)[:30]
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"code_{safe_desc}_{timestamp}.py"
    with open(filename, "w") as f:
        f.write(code)
    log(f"Code saved to file: {filename}")
    return filename

def get_multiline_input(prompt: str) -> str:
    print(prompt + " (finish with a single '.' on a line):")
    lines = []
    while True:
        line = input()
        if line.strip() == ".":
            break
        lines.append(line)
    return "\n".join(lines)

def print_history():
    if not session_history:
        print("No history available.")
        return
    print(f"\n=== Session History ({len(session_history)} entries) ===")
    for idx, entry in enumerate(session_history, 1):
        ts = entry['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
        desc = entry['desc']
        print(f"{idx}. [{ts}] - {desc}")

def view_code_entry(index: int):
    if 0 <= index < len(session_history):
        entry = session_history[index]
        print(f"\n--- Code Entry #{index + 1} ---")
        print(f"Description: {entry['desc']}")
        print(f"Timestamp: {entry['timestamp']}\n")
        print(syntax_highlight(entry['code']))
    else:
        print("Invalid history index.")

def revert_code(index: int) -> str:
    if 0 <= index < len(session_history):
        print(f"Reverting to code version #{index + 1}")
        return session_history[index]['code']
    else:
        print("Invalid history index.")
        return ""
def user_modification(current_code: str, current_desc: str) -> tuple[str, str]:
    """
    Let the user provide natural language instructions to modify the current code.
    Sends the current code + instructions to Gemini for code update.
    Returns updated (code, description).
    Also runs the updated code and prints output/errors.
    """
    print("\nYou chose usermodification: Provide natural language instructions to modify the code.")
    print("Enter your instructions below (end input with an empty line):")

    # Gather multi-line instructions
    instructions = []
    while True:
        line = input()
        if line.strip() == "":
            break
        instructions.append(line)
    instructions = "\n".join(instructions).strip()

    if not instructions:
        print("No instructions entered, no changes made.")
        return current_code, current_desc

    prompt = (
        f"Here is the current code:\n\n{current_code}\n\n"
        f"The user wants to modify the code as follows:\n{instructions}\n\n"
        "Please update the code accordingly and return only the updated Python code without explanations."
    )

    updated_code = ask_gemini(prompt)

    if updated_code:
        new_desc = current_desc + " (modified by usermodification)"
        print("\n=== Updated Code from Gemini ===\n")
        print(syntax_highlight(updated_code))

        # Automatically run updated code and show output
        print("\n=== Running Updated Code ===\n")
        success, stdout, stderr = run_code(updated_code)
        if success:
            print("✅ Output:\n")
            print(stdout)
        else:
            print("❌ Error while running updated code:\n")
            print(stderr)

        return updated_code, new_desc
    else:
        print("Failed to get updated code from Gemini. No changes made.")
        return current_code, current_desc



def main():
    print("=== Gemini Powered Code Generator - Ultimate Edition ===")
    print("Type 'help' for commands.\n")

    current_code = ""
    current_desc = ""

    while True:
        user_request = input("\nEnter program description or command ('exit' to quit): ").strip()
        if user_request.lower() == "exit":
            print("Goodbye!")
            break

        if user_request.lower() == "help":
            print("\nCommands:")
            print("  help            - Show this help message")
            print("  history         - List all past generated codes")
            print("  view <num>      - View code from history entry number")
            print("  revert <num>    - Revert current code to history entry")
            print("  save            - Save current code to a .py file")
            print("  run             - Run current code")
            print("  clear           - Clear current code")
            print("  exit            - Exit the program\n")
            continue

        if user_request.lower() == "history":
            print_history()
            continue

        if user_request.lower().startswith("view"):
            parts = user_request.split()
            if len(parts) != 2 or not parts[1].isdigit():
                print("Usage: view <history_number>")
                continue
            idx = int(parts[1]) - 1
            view_code_entry(idx)
            continue

        if user_request.lower().startswith("revert"):
            parts = user_request.split()
            if len(parts) != 2 or not parts[1].isdigit():
                print("Usage: revert <history_number>")
                continue
            idx = int(parts[1]) - 1
            code_reverted = revert_code(idx)
            if code_reverted:
                current_code = code_reverted
                current_desc = f"Reverted from history #{idx+1}"
                print("Reverted current code. Use 'run' to execute.")
            continue

        if user_request.lower() == "save":
            if current_code:
                filename = save_code_to_file(current_code, current_desc or "saved_code")
                print(f"Code saved as {filename}")
            else:
                print("No code to save.")
            continue

        if user_request.lower() == "run":
            if not current_code:
                print("No code loaded. Please generate or revert some code first.")
                continue
            print("\n=== Running Code ===")
            success, stdout, stderr = run_code(current_code)
            if success:
                print("\n✅ Success! Output:\n")
                print(stdout)
            else:
                print("\n❌ Errors while running code:")
                print(stderr)
                print("\nAttempting automatic fix...")

                fix_prompt = (
                    f"User request:\n{current_desc}\n\n"
                    f"Current code:\n{current_code}\n\n"
                    f"Error message:\n{stderr}\n\n"
                    "Please fix the code to meet the original request without asking further questions."
                )
                fixed_code = ask_gemini(fix_prompt)
                if fixed_code:
                    current_code = fixed_code
                    current_desc += " (auto-fixed)"
                    session_history.append({
                        'desc': current_desc,
                        'code': current_code,
                        'timestamp': datetime.datetime.now()
                    })
                    print("\nFixed code generated. Use 'run' to execute again.")
                else:
                    print("Failed to fix the code automatically.")
            continue

        if user_request.lower() == "clear":
            current_code = ""
            current_desc = ""
            print("Cleared current code.")
            continuecd

        # If none of the above commands, treat input as a new code generation request
        print(f"\nGenerating code for request:\n{user_request}\nPlease wait...")
        generated_code = ask_gemini(user_request)
        if not generated_code:
            print("Failed to generate code from Gemini. Try again.")
            continue

        current_code = generated_code
        current_desc = user_request
        session_history.append({
            'desc': current_desc,
            'code': current_code,
            'timestamp': datetime.datetime.now()
        })

        # Show generated code
        print("\n=== Generated Code ===\n")
        print(syntax_highlight(current_code))

        # Automatically run the generated code and display output
        print("\n=== Running Generated Code ===\n")
        success, stdout, stderr = run_code(current_code)
        if success:
            print("✅ Output:\n")
            print(stdout)
        else:
            print("❌ Error while running code:\n")
            print(stderr)


        # Ask if user wants to run immediately or modify
        while True:
            action = input("Options: [run/modify/usermodification/save/history/clear/exit]: ").strip().lower()
            if action == "run":
                success, stdout, stderr = run_code(current_code)
                if success:
                    print("\n✅ Success! Output:\n")
                    print(stdout)
                else:
                    print("\n❌ Errors while running code:")
                    print(stderr)
                    print("\nAttempting automatic fix...")

                    fix_prompt = (
                        f"User request:\n{current_desc}\n\n"
                        f"Current code:\n{current_code}\n\n"
                        f"Error message:\n{stderr}\n\n"
                        "Please fix the code to meet the original request without asking further questions."
                    )
                    fixed_code = ask_gemini(fix_prompt)
                    if fixed_code:
                        current_code = fixed_code
                        current_desc += " (auto-fixed)"
                        session_history.append({
                            'desc': current_desc,
                            'code': current_code,
                            'timestamp': datetime.datetime.now()
                        })
                        print("\nFixed code generated. Use 'run' to execute again.")
                    else:
                        print("Failed to fix the code automatically.")
                continue

            elif action == "modify":
                new_code = get_multiline_input("Enter your modified code")
                if new_code.strip():
                    print("\nYou entered the following modified code:\n")
                    print(syntax_highlight(new_code))
                    current_code = new_code
                    current_desc += " (modified by user)"
                    session_history.append({
                        'desc': current_desc,
                        'code': current_code,
                        'timestamp': datetime.datetime.now()
                    })
                    print("Code updated.")
                else:
                    print("Modification aborted; empty input.")
                continue


            elif action == "usermodification":
                updated_code, updated_desc = user_modification(current_code, current_desc)
                if updated_code != current_code:
                    current_code = updated_code
                    current_desc = updated_desc
                    session_history.append({
                        'desc': current_desc,
                        'code': current_code,
                        'timestamp': datetime.datetime.now()
                    })
                continue


            elif action == "save":
                filename = save_code_to_file(current_code, current_desc or "saved_code")
                print(f"Code saved as {filename}")
                continue

            elif action == "history":
                print_history()
                continue

            elif action == "clear":
                current_code = ""
                current_desc = ""
                print("Cleared current code.")
                break

            elif action == "exit":
                print("Exiting current generation session.")
                return

            else:
                print("Unknown option. Please choose: run, modify, usermodification, save, history, clear, or exit.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted by user. Bye!")
        log("User exited with KeyboardInterrupt.")
