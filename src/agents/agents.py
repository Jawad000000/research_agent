from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import ModelFallbackMiddleware
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.rate_limiters import InMemoryRateLimiter
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_nvidia_ai_endpoints import ChatNVIDIA

from tools.tools import scrape_url, web_search

load_dotenv()

limiter = InMemoryRateLimiter(requests_per_second=0.4)

# Agent models (plain, no .with_fallbacks)
search_model = ChatGroq(model="openai/gpt-oss-120b", rate_limiter=limiter)
reader_model = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite", rate_limiter=limiter
)

# Fallbacks for agents, on a different model/bucket
groq_20b = ChatGroq(model="openai/gpt-oss-20b")
groq_120b = ChatGroq(model="openai/gpt-oss-120b")

# Chain models (.with_fallbacks is fine here)
writer_llm = ChatGoogleGenerativeAI(
    model="gemini-3.8-flash", thinking_level="low"
).with_fallbacks([groq_120b])

critic_llm = ChatGroq(model="openai/gpt-oss-20b").with_fallbacks(
    [ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")]
)


def build_search_agent():
    return create_agent(
        model=search_model,
        tools=[web_search],
        system_prompt=(
            "You are a research assistant. Use the web_search tool to find recent, "
            "reliable information. Return a concise summary with source URLs."
        ),
        middleware=[ModelFallbackMiddleware(groq_20b)],  # <-- here
    )


def build_reader_agent():
    return create_agent(
        model=reader_model,
        tools=[scrape_url],
        system_prompt=(
            "You are a reader. Pick the most relevant URL from the search results, "
            "use scrape_url on it, and summarize the key facts."
        ),
        middleware=[ModelFallbackMiddleware(groq_120b)],  # <-- and here
    )


writer_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an expert research writer. Write clear, structured and insightful reports.",
        ),
        (
            "human",
            """Write a detailed research report on the topic below.

Topic: {topic}

Research Gathered:
{research}

Structure the report as:
- Introduction
- Key Findings (minimum 3 well-explained points)
- Conclusion
- Sources (list all URLs found in the research)

Be detailed, factual and professional.""",
        ),
    ]
)

writer_chain = writer_prompt | writer_llm | StrOutputParser()


critic_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a sharp and constructive research critic. Be honest and specific.",
        ),
        (
            "human",
            """Review the research report below and evaluate it strictly.

Report:
{report}

Respond in this exact format:

Score: X/10

Strengths:
- ...
- ...

Areas to Improve:
- ...
- ...

One line verdict:
...""",
        ),
    ]
)

critic_chain = critic_prompt | critic_llm | StrOutputParser()
