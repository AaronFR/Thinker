import logging
import requests
from typing import List
from urllib.parse import quote_plus

from duckduckgo_search import DDGS

from AiOrchestration.AiOrchestrator import AiOrchestrator
from Utilities.Instructions import EXTRACT_SEARCH_TERMS_SYSTEM_MESSAGE, EXTRACT_SEARCH_TERMS_PROMPT


class DuckDuckGoSearchAPI:
    """
    A class to interact with the DuckDuckGo Instant API for performing searches.
    """

    def search(self, query: str) -> dict:
        """
        Perform a search using the DuckDuckGo API.
        ToDo: Automatically search each result website to

        :param query: The search query string.
        :return: JSON response from the DuckDuckGo API.
        """
        search_query = quote_plus(query)
        try:
            response = DDGS().text(
                keywords=search_query,
                region='wt-wt',
                safesearch='off',
                max_results=3
            )
            logging.info(f"DuckDuckGo search request successful: Response:\n {response}")
            return response
        except Exception as e:
            logging.error(f"DuckDuckGo search request failed: {e}")
            return {}


class InternetSearch:
    """
    A class to perform internet searches based on keywords extracted from user prompts.
    """

    def __init__(self, search_api: DuckDuckGoSearchAPI = DuckDuckGoSearchAPI()):
        """
        Initialize the InternetSearch instance with dependencies.

        :param search_api: An instance of DuckDuckGoSearchAPI for performing searches.
        """
        self.search_api = search_api
        self.search_results: List[str] = []

    def search_internet_based_on_prompt(self, user_prompt: str):
        search_terms = self.extract_search_terms(user_prompt)
        logging.info(f"Keywords for search: {search_terms}")

        # Perform online search with extracted keywords
        results = self.search_online(search_terms)
        if not results:
            logging.warning("No search results found.")

        return results

    def extract_search_terms(self, user_prompt: str) -> List[str]:
        """
        Extract keywords from the user prompt using AI.

        :param user_prompt: The input prompt from the user.
        :return: A list of extracted keywords.
        """
        logging.info("Extracting keywords from the user prompt.")
        try:
            response = AiOrchestrator().execute(
                [EXTRACT_SEARCH_TERMS_SYSTEM_MESSAGE],
                [
                    EXTRACT_SEARCH_TERMS_PROMPT,  # ToDo: Might not actually need this line
                    user_prompt
                ],
            )

            keywords = self.parse_keywords(response)
            return keywords
        except Exception as e:
            logging.exception(f"Failed to extract keywords: {e}")
            return []

    @staticmethod
    def parse_keywords(ai_response: str) -> List[str]:
        """
        Parses the AI response to extract keywords.

        :param ai_response: The response string from the AI Executor.
        :return: A list of keywords.
        """
        if not ai_response:
            logging.warning("AI response is empty. No keywords extracted.")
            return []

        # Use regex to extract words separated by commas
        keywords = [keyword.strip() for keyword in ai_response.split(",") if keyword.strip()]
        logging.info(f"Parsed keywords: {keywords}")
        return keywords

    def search_online(self, keywords: List[str]) -> List[str]:
        """
        Perform an online search based on the provided keywords.

        :param keywords: A list of keywords to search for.
        :return: A list of relevant body texts extracted from search results.
        """
        if not keywords:
            logging.warning("No keywords provided for searching.")
            return []

        search_query = " ".join(keywords)
        responses = self.search_api.search(search_query)
        return responses


# Example usage
if __name__ == "__main__":
    duckduckgo_api = DuckDuckGoSearchAPI()
    internet_search = InternetSearch(search_api=duckduckgo_api)

    user_prompt = "Tell me about the health benefits of green tea."

    search_terms = internet_search.extract_search_terms(user_prompt)
    logging.info(f"Keywords for search: {search_terms}")

    # Perform online search with extracted keywords
    results = internet_search.search_online(search_terms)
    if results:
        print(results)
    else:
        logging.info("No search results found.")
