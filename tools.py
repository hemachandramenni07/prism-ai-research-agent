from datetime import datetime
from pathlib import Path
import wikipedia
import textwrap
from langchain.tools import tool
from langchain_community.tools import (
    WikipediaQueryRun,
    DuckDuckGoSearchRun
)
from langchain_community.utilities import WikipediaAPIWrapper


# Identify your application when making Wikipedia requests
wikipedia.set_user_agent(
    "AI-Research-Agent/1.0 (hemachandramenni07@gmail.com)"
)
# IN --Your_Email_address-- add your working Email for web search...

# DuckDuckGo
search_tool = DuckDuckGoSearchRun()

# latest information:
@tool
def latest_search(query: str) -> str:
    """
    Search the web specifically for recent and current information.
    Use this tool whenever the user asks for latest, current,
    recent, today's, yesterday's, or other time-sensitive information.
    """

    search = DuckDuckGoSearchRun()

    current_year = datetime.now().year
    enhanced_query = (
    f"{query} "
    f"latest recent current {current_year}"
    )
    return search.run(enhanced_query)

# Wikipedia
api_wrapper = WikipediaAPIWrapper(
    top_k_results=2,
    doc_content_chars_max=5000
)

wiki_tool = WikipediaQueryRun(
    api_wrapper=api_wrapper
)


# this manual function stores the research in a folder :
@tool
def save_to_txt(
    data: str,
    filename: str
) -> str:
    """
    Save detailed research results as a separate text file
    inside the Researches folder.
    """

    research_folder = Path("Researches")
    research_folder.mkdir(exist_ok=True)

    # Make sure the filename is a .txt file
    if not filename.endswith(".txt"):
        filename += ".txt"

    file_path = research_folder / filename

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    # Format each paragraph
    formatted_paragraphs = []

    for paragraph in data.split("\n"):
        paragraph = paragraph.strip()

        if paragraph:
            formatted_paragraphs.append(
                textwrap.fill(
                    paragraph,
                    width=80,
                    break_long_words=False,
                    break_on_hyphens=False
                )
            )

    formatted_data = "\n\n".join(
        formatted_paragraphs
    )

    formatted_text = (
        "\n"
        + "=" * 80
        + "\n"
        + "                         RESEARCH OUTPUT"
        + "\n"
        + "=" * 80
        + "\n\n"
        + f"Date & Time: {timestamp}"
        + "\n\n"
        + formatted_data
        + "\n\n"
        + "=" * 80
        + "\n"
    )

    # Create a NEW research file
    with open(
        file_path,
        "w",
        encoding="utf-8"
    ) as f:
        f.write(formatted_text)

    return f"Research successfully saved to {file_path}"