import os
import requests
from typing import Optional, Dict, Any
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class SerperTool(BaseTool):
    name: str = "Serper Search Tool"
    description: str = "A tool to search for information using Serper API, useful for finding travel destinations, attractions, and travel-related information."

    def _run(self, query: str) -> str:
        """
        Search for information using Serper API

        Args:
            query (str): The search query

        Returns:
            str: Search results as formatted text
        """
        api_key = os.getenv("SERPER_API_KEY")
        if not api_key:
            return "Error: SERPER_API_KEY not found in environment variables"

        url = "https://google.serper.dev/search"

        payload = {
            "q": query,
            "gl": "us",
            "hl": "en"
        }

        headers = {
            "X-API-KEY": api_key,
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()

            data = response.json()

            # Format the results
            results = []

            # Add organic results
            if "organic" in data:
                results.append("Search Results:")
                for i, result in enumerate(data["organic"][:5], 1):
                    title = result.get("title", "")
                    snippet = result.get("snippet", "")
                    link = result.get("link", "")
                    results.append(f"{i}. {title}")
                    results.append(f"   {snippet}")
                    results.append(f"   Link: {link}")
                    results.append("")

            # Add knowledge graph if available
            if "knowledgeGraph" in data:
                kg = data["knowledgeGraph"]
                results.append("Knowledge Graph:")
                results.append(f"Title: {kg.get('title', '')}")
                results.append(f"Description: {kg.get('description', '')}")
                if "attributes" in kg:
                    for key, value in kg["attributes"].items():
                        results.append(f"{key}: {value}")
                results.append("")

            # Add local results if available
            if "places" in data:
                results.append("Local Places:")
                for place in data["places"][:3]:
                    results.append(f"- {place.get('title', '')}")
                    if "address" in place:
                        results.append(f"  Address: {place['address']}")
                    if "rating" in place:
                        results.append(f"  Rating: {place['rating']}")
                    results.append("")

            return "\n".join(results) if results else "No results found"

        except requests.exceptions.RequestException as e:
            return f"Error making request to Serper API: {str(e)}"
        except Exception as e:
            return f"Error processing Serper API response: {str(e)}"