"""
LangChain Agent Demo: Anthropic Advanced Tool Use Concepts
===========================================================

This demo implements the 3 key patterns from Anthropic's blog post:
https://www.anthropic.com/engineering/advanced-tool-use

CONCEPT 1: Tool Search Tool (defer_loading)
--------------------------------------------
Problem: Loading 100s of tools upfront consumes 50K+ tokens before work begins.
Solution: Keep only essential tools loaded; discover others on-demand via search.

Implementation:
- `defer_loading=False` → Always loaded (DuckDuckGo, Wikipedia)
- `defer_loading=True`  → Only loaded when matching query (weather, GitHub, etc.)
- `select_tools()` → Similarity search to find relevant deferred tools

CONCEPT 2: Programmatic Tool Calling  
-------------------------------------
Problem: Each tool call requires inference pass; intermediate results bloat context.
Solution: Let the model write Python code to orchestrate multi-tool workflows.

Implementation:
- `run_python` tool allows model to write code calling other tools
- Filter/aggregate data in code → only final result enters context
- Example: Loop over 20 team members, sum expenses, return only violations

CONCEPT 3: Tool Use Examples
----------------------------
Problem: JSON schemas can't express usage patterns (date formats, ID conventions).
Solution: Provide example invocations showing correct parameter usage.

Implementation:
- `examples` field in ToolSpec shows typical tool usage
- Helps model understand: formats, optional param patterns, correlations

Run:
    python demo_agent.py --query "Find highly starred GitHub repos about RAG" --top-k 3
"""
from __future__ import annotations

import argparse
import difflib
import json
import os
from dataclasses import dataclass, field
from typing import Callable, List

import requests
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_community.tools import WikipediaQueryRun


# =============================================================================
# CONCEPT 3: Tool Use Examples
# =============================================================================
# The ToolSpec dataclass includes an `examples` field that demonstrates
# correct tool usage patterns. This helps the model understand:
# - Parameter formats (date strings, ID conventions, etc.)
# - When to use optional parameters
# - Correlations between parameters

@dataclass
class ToolSpec:
    """
    Metadata wrapper for tools that supports:
    - defer_loading: Tool Search Tool pattern (Concept 1)
    - examples: Tool Use Examples pattern (Concept 3)
    """
    name: str
    description: str
    tool: Callable  # The actual tool (decorated function or BaseTool instance)
    defer_loading: bool = True  # CONCEPT 1: If True, only load when query matches
    examples: List[str] = field(default_factory=list)  # CONCEPT 3: Usage examples


# =============================================================================
# CONCEPT 1: Tool Search Tool
# =============================================================================
# Instead of loading all tools (consuming 50K+ tokens), we:
# 1. Always load critical tools (defer_loading=False)
# 2. Use similarity search to find relevant deferred tools
# 3. Only load matched tools into context

def _score(query: str, spec: ToolSpec) -> float:
    """
    Compute similarity between user query and tool metadata.
    
    In production, you'd use embeddings or BM25 for better matching.
    This uses SequenceMatcher as a simple baseline.
    """
    target = f"{spec.name} {spec.description}".lower()
    return difflib.SequenceMatcher(None, query.lower(), target).ratio()


def select_tools(query: str, catalog: List[ToolSpec], top_k: int = 3) -> List[ToolSpec]:
    """
    CONCEPT 1: Tool Search Tool Implementation
    
    - Always-loaded tools (defer_loading=False) are always included
    - Deferred tools (defer_loading=True) are ranked by query similarity
    - Only top-k most relevant deferred tools are loaded
    
    Anthropic's stats: This reduces context from ~77K to ~8.7K tokens (85% savings)
    """
    always = [t for t in catalog if not t.defer_loading]
    deferred = [t for t in catalog if t.defer_loading]
    scored = sorted(deferred, key=lambda spec: _score(query, spec), reverse=True)
    chosen = scored[:top_k]
    return always + chosen


# =============================================================================
# TOOL DEFINITIONS
# =============================================================================
# Each tool uses the @tool decorator (LangChain v1 pattern)
# Examples show correct invocation patterns (Concept 3)

@tool
def get_weather(city: str) -> str:
    """
    Get tomorrow's weather summary for a city via Open-Meteo APIs.
    
    Args:
        city: City name (e.g., "San Francisco", "Tokyo", "London")
    
    Returns:
        Weather summary with avg/max temperature and precipitation probability
        
    Example:
        get_weather("San Francisco") -> "Weather for San Francisco: avg temp 15.2C, high 19.8C, max precip prob 10%"
    """
    geo_resp = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": city, "count": 1, "language": "en", "format": "json"},
        timeout=10,
    )
    geo_resp.raise_for_status()
    geo = geo_resp.json()
    if not geo.get("results"):
        return f"No geocoding results for {city}."

    first = geo["results"][0]
    lat, lon = first["latitude"], first["longitude"]
    forecast = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": lat,
            "longitude": lon,
            "hourly": "temperature_2m,precipitation_probability",
            "forecast_days": 1,
            "timezone": "auto",
        },
        timeout=10,
    )
    forecast.raise_for_status()
    data = forecast.json()
    temps = data.get("hourly", {}).get("temperature_2m", [])
    precip = data.get("hourly", {}).get("precipitation_probability", [])
    if not temps:
        return f"Could not fetch forecast for {city}."

    avg_temp = round(sum(temps) / len(temps), 1)
    max_temp = round(max(temps), 1)
    max_precip = max(precip) if precip else 0
    return (
        f"Weather for {city}: avg temp {avg_temp}C, high {max_temp}C, max precip prob {max_precip}%"
    )


@tool
def search_github_repos(topic: str) -> str:
    """
    Search GitHub repositories by topic keyword and return top starred results.
    
    Args:
        topic: Search keyword (e.g., "retrieval augmented generation", "vector database")
    
    Returns:
        JSON array of top 5 repos with name, stars, URL, and description
        
    Example:
        search_github_repos("langchain") -> '[{"name": "langchain-ai/langchain", "stars": 95000, ...}]'
    """
    resp = requests.get(
        "https://api.github.com/search/repositories",
        params={"q": topic, "sort": "stars", "order": "desc", "per_page": 5},
        headers={"Accept": "application/vnd.github+json"},
        timeout=10,
    )
    resp.raise_for_status()
    payload = resp.json()
    repos = payload.get("items", [])
    if not repos:
        return f"No repositories found for '{topic}'."

    summary = [
        {
            "name": repo.get("full_name"),
            "stars": repo.get("stargazers_count"),
            "url": repo.get("html_url"),
            "description": repo.get("description"),
        }
        for repo in repos
    ]
    return json.dumps(summary, indent=2)


@tool
def fx_rate(pair: str) -> str:
    """
    Convert 1 unit from base to quote currency.
    
    Args:
        pair: Currency pair like "USD to EUR" or "USD/JPY"
    
    Returns:
        Conversion rate string
        
    Example:
        fx_rate("USD to EUR") -> "1 USD = 0.9234 EUR"
    """
    parts = pair.replace(" to ", " ").replace("/", " ").split()
    if len(parts) < 2:
        return "Please provide a pair like 'USD to EUR'."
    base, quote = parts[0].upper(), parts[1].upper()
    resp = requests.get(
        "https://api.exchangerate.host/convert",
        params={"from": base, "to": quote, "amount": 1},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()
    rate = data.get("result")
    if rate is None:
        return f"Could not fetch rate for {base}->{quote}."
    return f"1 {base} = {rate:.4f} {quote}"


@tool
def http_get(url: str) -> str:
    """
    Fetch content from a URL via HTTP GET request.
    
    Args:
        url: Full URL to fetch (must include https://)
    
    Returns:
        First 5000 characters of response text
        
    Example:
        http_get("https://api.github.com/rate_limit") -> '{"resources": ...}'
    """
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return resp.text[:5000]


# =============================================================================
# CONCEPT 2: Programmatic Tool Calling
# =============================================================================
# This tool allows the model to write Python code that orchestrates workflows.
# Instead of making 20 separate tool calls (each hitting context), the model
# can write a loop that processes data and returns only the final result.
#
# Example from Anthropic:
#   - Task: "Which team members exceeded Q3 travel budget?"
#   - Without PTC: 20 tool calls, 2000+ expense items in context
#   - With PTC: One code block, only 3 exceeding names returned

@tool
def run_python(code: str) -> str:
    """
    CONCEPT 2: Programmatic Tool Calling
    
    Execute Python code for data transformations, loops, and orchestration.
    Use this when you need to:
    - Process multiple items in a loop
    - Aggregate/filter data before returning
    - Perform math or data transformations
    - Keep intermediate results OUT of context
    
    Args:
        code: Python code to execute. Use print() to output results.
    
    Returns:
        stdout from code execution, or error message
        
    Example:
        run_python('''
        data = [1, 2, 3, 4, 5]
        print(f"Sum: {sum(data)}, Average: {sum(data)/len(data)}")
        ''')
        -> "Sum: 15, Average: 3.0"
    """
    import io
    import contextlib
    
    output = io.StringIO()
    try:
        with contextlib.redirect_stdout(output):
            exec(code, {"__builtins__": __builtins__})
        result = output.getvalue()
        return result if result else "Code executed successfully (no output)"
    except Exception as e:
        return f"Error: {str(e)}"


def build_catalog() -> List[ToolSpec]:
    """
    Build the catalog of available tools with Anthropic's patterns:
    
    - defer_loading controls Tool Search Tool behavior (Concept 1)
    - examples provide usage patterns (Concept 3)
    """
    
    # =========================================================================
    # ALWAYS-LOADED TOOLS (defer_loading=False)
    # These are your most-used tools, always available without search
    # =========================================================================
    
    duck_tool = DuckDuckGoSearchRun()
    duck = ToolSpec(
        name="duckduckgo_search",
        description="Web search for fresh results using DuckDuckGo (returns snippets).",
        tool=duck_tool,
        defer_loading=False,  # Always loaded - essential for general queries
        examples=[
            "duckduckgo_search('latest news about vector databases')",
            "duckduckgo_search('LangChain vs LlamaIndex comparison 2024')"
        ]
    )

    wiki_api = WikipediaAPIWrapper()
    wiki_tool = WikipediaQueryRun(api_wrapper=wiki_api)
    wiki = ToolSpec(
        name="wikipedia",
        description="Wikipedia lookup for concise encyclopedic summaries.",
        tool=wiki_tool,
        defer_loading=False,  # Always loaded - essential for factual lookups
        examples=[
            "wikipedia('Transformer neural network architecture')",
            "wikipedia('Retrieval augmented generation')"
        ]
    )

    # =========================================================================
    # DEFERRED TOOLS (defer_loading=True)
    # Only loaded when query matches - saves context tokens
    # =========================================================================
    
    http_get_spec = ToolSpec(
        name="http_get",
        description="Generic HTTP GET for JSON/text APIs.",
        tool=http_get,
        defer_loading=True,
        examples=[
            "http_get('https://api.github.com/rate_limit')",
            "http_get('https://jsonplaceholder.typicode.com/todos/1')"
        ]
    )

    # CONCEPT 2: Programmatic Tool Calling tool
    python_repl = ToolSpec(
        name="python_repl",
        description="Run Python code for data processing, loops, aggregations, and orchestration. Use when you need to transform data or keep intermediate results out of context.",
        tool=run_python,
        defer_loading=True,
        examples=[
            "run_python('numbers = [1,2,3,4,5]\\nprint(sum(numbers))')",
            "run_python('import json\\ndata = {\"a\": 1}\\nprint(json.dumps(data))')"
        ]
    )

    weather = ToolSpec(
        name="open_meteo_weather",
        description="Get a 1-day forecast using Open-Meteo geocoding + forecast APIs by city name.",
        tool=get_weather,
        defer_loading=True,
        examples=[
            "get_weather('San Francisco')",
            "get_weather('Tokyo')",
            "get_weather('London')"
        ]
    )

    github_search = ToolSpec(
        name="github_repo_search",
        description="Search GitHub repositories by topic keyword, sorted by stars.",
        tool=search_github_repos,
        defer_loading=True,
        examples=[
            "search_github_repos('retrieval augmented generation')",
            "search_github_repos('LLM agent framework')"
        ]
    )

    fx = ToolSpec(
        name="fx_rate",
        description="Fetch FX conversion rate (e.g., USD to EUR).",
        tool=fx_rate,
        defer_loading=True,
        examples=[
            "fx_rate('USD to EUR')",
            "fx_rate('GBP/JPY')"
        ]
    )

    return [duck, wiki, http_get_spec, python_repl, weather, github_search, fx]


def build_agent(query: str, top_k: int, model_name: str, temperature: float):
    """
    Build agent with dynamically selected tools.
    
    This implements CONCEPT 1: Tool Search Tool by:
    1. Building full catalog of all available tools
    2. Running select_tools() to find relevant tools for this query
    3. Only loading matched tools into the agent
    """
    catalog = build_catalog()
    
    # CONCEPT 1: Select only relevant tools based on query
    chosen_specs = select_tools(query, catalog, top_k)
    tools = [spec.tool for spec in chosen_specs]

    # Create agent using LangChain v1 API
    agent = create_agent(
        model=model_name,
        tools=tools,
    )
    return agent, chosen_specs


def main():
    load_dotenv()
    parser = argparse.ArgumentParser(
        description="LangChain demo of Anthropic's advanced tool use patterns"
    )
    parser.add_argument("--query", required=True, help="User request to handle")
    parser.add_argument("--top-k", type=int, default=3, help="Max deferred tools to load (Concept 1)")
    parser.add_argument("--model", default="gpt-4o-mini", help="OpenAI chat model name")
    parser.add_argument("--temperature", type=float, default=0.0, help="Sampling temperature")
    args = parser.parse_args()

    if not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError("Set OPENAI_API_KEY before running.")

    agent, specs = build_agent(args.query, args.top_k, args.model, args.temperature)
    
    # Show which tools were selected (demonstrating Concept 1)
    print("\n" + "="*60)
    print("CONCEPT 1: Tool Search Tool - Selected tools for this query:")
    print("="*60)
    for spec in specs:
        tag = "ALWAYS" if not spec.defer_loading else "MATCHED"
        print(f"  [{tag}] {spec.name}")
        if spec.examples:
            print(f"           Example: {spec.examples[0]}")
    print()

    # Invoke agent
    print("Agent response:\n")
    result = agent.invoke({
        "messages": [{"role": "user", "content": args.query}]
    })
    
    final_message = result["messages"][-1]
    print(final_message.content)


if __name__ == "__main__":
    main()
