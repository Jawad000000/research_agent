# main.py
from pathlib import Path

from src.pipeline.pipeline import run_research_pipeline

if __name__ == "__main__":
    topic = input("Enter a research topic: ").strip()
    if not topic:
        topic = "latest research on artificial intelligence in healthcare"

    state = run_research_pipeline(topic)

    # save the outputs
    out = Path("outputs")
    out.mkdir(exist_ok=True)
    (out / "report.md").write_text(state["report"], encoding="utf-8")
    (out / "critic.md").write_text(state["feedback"], encoding="utf-8")
    print("\nSaved to outputs/report.md and outputs/critic.md")
