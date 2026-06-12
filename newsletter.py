# newsletter.py

import os
from dotenv import load_dotenv
load_dotenv()

from src.collector  import collect_all
from src.summarizer import filter_and_summarize
from src.formatter  import build_email
from src.sender     import send


def main():
    print("--- ai-brief starting ---")

    items         = collect_all()
    digest        = filter_and_summarize(items)
    subject, html = build_email(digest)
    send(subject, html)

    print("--- ai-brief done ---")


if __name__ == "__main__":
    main()