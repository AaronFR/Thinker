"""
This is, to be frank, a huge pot of worms.
For the record: All I want to do is to be able to process information the user can freely access online and make it
available to said user,

1: as context for their requested prompt
2: as a clickable link for reference

There are a couple of possibilities that may need to be implemented to mitigate the myriad issues of AI with internet
search:
Running requests client side, Running a 3rd party search function, creating a system for interacting with various common
website APIs instead of page requests, etc.

Additionally, if you own a website and don't want our user agent to make requests add it to your robots.txt and our
program should be automatically disabled from searching instantly, please contact us if there's any further issue.
"""


import logging
from typing import List
from urllib.parse import quote_plus, urlparse
import urllib.robotparser

import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS

from AiOrchestration.AiOrchestrator import AiOrchestrator
from Constants.Instructions import EXTRACT_SEARCH_TERMS_SYSTEM_MESSAGE, EXTRACT_SEARCH_TERMS_PROMPT
from Utilities.Decorators import return_for_error
from Utilities.PaymentDecorators import specify_functionality_context
from Utilities.Utility import Utility

USER_AGENT = 'TheThinkerAiBot'


class DuckDuckGoSearchAPI:
    """
    A class to interact with the DuckDuckGo Instant API for performing searches.
    """

    @return_for_error({})
    def search(self, query: str) -> list[dict]:
        """
        Perform a search using the DuckDuckGo API.
        ToDo: Automatically search each result website to

        :param query: The search query string.
        :return: JSON response from the DuckDuckGo API.
        """
        search_query = quote_plus(query)

        response = DDGS().text(
            keywords=search_query,
            region='wt-wt',
            safesearch='off',
            max_results=3
        )
        logging.info(f"DuckDuckGo search request successful: Response:\n {response}")
        return response


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

    @return_for_error([], debug_logging=True)
    @specify_functionality_context('internet_search')
    def extract_search_terms(self, user_prompt: str) -> List[str]:
        """
        Extract keywords from the user prompt using AI.

        :param user_prompt: The input prompt from the user.
        :return: A list of extracted keywords.
        """
        response = AiOrchestrator().execute(
            [EXTRACT_SEARCH_TERMS_SYSTEM_MESSAGE],
            [
                EXTRACT_SEARCH_TERMS_PROMPT,  # ToDo: Might not actually need this line
                user_prompt
            ],
        )

        keywords = self.parse_keywords(response)
        return keywords

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
        search_results = self.search_api.search(search_query)

        responses: List[str] = []
        for search_result in search_results:
            response_url = search_result.get("href")
            logging.info(f"Reading content from - {response_url}")

            website_content = self.read_website_content(response_url)
            responses.append(Utility.encapsulate_in_tag(website_content, response_url))

        return responses


    @staticmethod
    def read_website_content(url):
        """
        A bit of a grayzone, we *will* check the robots.txt and if a site doesn't want automated bot, we won't go there.
        Ideally the user will be notified, and they can go there in person.
        """
        headers = {'User-Agent': USER_AGENT}
        res = requests.get(url, headers=headers)
        html_page = res.content
        soup = BeautifulSoup(html_page, 'html.parser')
        text = soup.find_all(text=True)

        output = ''
        blacklist = [
            '[document]',
            'noscript',
            'header',
            'html',
            'meta',
            'head',
            'input',
            'script',
            'source',
            'style',
            'link',
            'img',
            'svg',
            'button',
            'iframe'
        ]
        for t in text:
            if t.parent.name not in blacklist:
                output += '{} '.format(t)

        # character limit - first 50000 characters
        output = output[:50000]

        return output

    @staticmethod
    def can_fetch(url: str, user_agent: str = USER_AGENT):
        """
        Checks if a given user agent is allowed to fetch a URL based on the site's robots.txt.

        @param url: The URL to check.
        @param user_agent: The user agent string to simulate (e.g., 'MyBot/1.0').
        @return: True if the user agent is allowed to fetch the URL, False otherwise.
        """
        try:
            parsed_uri = urlparse(url)
            base_url = f'{parsed_uri.scheme}://{parsed_uri.netloc}'
            robots_url = f'{base_url}/robots.txt'

            rp = urllib.robotparser.RobotFileParser()
            rp.set_url(robots_url)
            rp.read()

            return rp.can_fetch(user_agent, url)

        except Exception as e:
            logging.exception(f"Error checking robots.txt: {e}")
            # If there's an error (e.g., robots.txt doesn't exist, network issue),
            # you might want to assume you *can* fetch (be optimistic) or *cannot*
            # fetch (be conservative).  The choice depends on your risk tolerance
            # and the website's terms of service. Here, we default to "cannot fetch"
            return False


# Example usage
if __name__ == "__main__":
    duckduckgo_api = DuckDuckGoSearchAPI()
    internet_search = InternetSearch(search_api=duckduckgo_api)

    print(internet_search.can_fetch("https://www.example.com"))
