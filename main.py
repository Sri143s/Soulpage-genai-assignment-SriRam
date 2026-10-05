import sys
import os
import io
import subprocess

# Ensure repo root is in python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure Windows console encoding for UTF-8 compatibility
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from common.logging_config import logger

def run_server():
    """Starts the FastAPI Backend Server."""
    from backend.server import start_server
    logger.info("Launching FastAPI Backend Server...")
    start_server()

def run_ui():
    """Launches the Streamlit Frontend UI."""
    app_path = os.path.join(os.path.dirname(__file__), "frontend", "app.py")
    logger.info(f"Launching Streamlit App from: {app_path}")
    subprocess.run([sys.executable, "-m", "streamlit", "run", app_path])

def run_tests():
    """Runs the pytest test suite."""
    logger.info("Executing Pytest test suite...")
    subprocess.run([sys.executable, "-m", "pytest", "-v"])

def run_demo():
    """Runs a quick CLI demonstration of Task 1 and Task 2."""
    from task1_company_intelligence.workflow import run_company_intelligence_workflow
    from task2_knowledge_bot.bot import knowledge_bot

    print("\n=======================================================")
    print("SOULPAGE GENAI ASSIGNMENT - CLI DEMONSTRATION")
    print("=======================================================\n")

    print("--- TASK 1: MULTI-AGENT COMPANY INTELLIGENCE ---")
    print("Analyzing NVIDIA...")
    res = run_company_intelligence_workflow("NVIDIA", session_id="cli-demo")
    print("\nREPORT PREVIEW:")
    print(res.get("final_report", "")[:600])
    print("...\n")

    print("--- TASK 2: CONVERSATIONAL KNOWLEDGE BOT ---")
    print("Query 1: Who is the CEO of OpenAI?")
    bot_res1 = knowledge_bot.ask("Who is the CEO of OpenAI?", session_id="cli-demo")
    print(f"Bot Response: {bot_res1['response'][:300]}...\n")

    print("Query 2 (Follow-up with pronoun 'he'): Where did he study?")
    bot_res2 = knowledge_bot.ask("Where did he study?", session_id="cli-demo")
    print(f"Context Resolution: Query rewritten to -> '{bot_res2.get('resolved_query')}'")
    print(f"Bot Response: {bot_res2['response'][:300]}...\n")

    print("=======================================================")
    print("[SUCCESS] DEMO COMPLETED SUCCESSFULLY!")
    print("=======================================================\n")

def print_help():
    print("""
Soulpage GenAI Technical Assignment CLI Launcher

Usage:
  python main.py [command]

Commands:
  server   Starts the FastAPI Backend Server on port 8000
  ui       Launches the Streamlit Frontend Web App
  test     Runs the Pytest test suite
  demo     Executes CLI end-to-end demonstration
  help     Displays this help message
""")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        run_demo()
    else:
        cmd = sys.argv[1].lower()
        if cmd == "server":
            run_server()
        elif cmd == "ui":
            run_ui()
        elif cmd == "test":
            run_tests()
        elif cmd == "demo":
            run_demo()
        else:
            print_help()
