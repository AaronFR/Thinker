import logging
import os
from typing import Dict, Optional, List

import requests
import regex as re
import wikipediaapi
import yaml

from Data.FileManagement import FileManagement
from Utilities.Constants import DEFAULT_ENCODING


class MyDumper(yaml.Dumper):
    """
    Custom YAML dumper that formats multi-line strings using block style.
    """
    def represent_scalar(self, tag, value: str, style=None) -> yaml.nodes.ScalarNode:
        if '\n' in value or isinstance(value, str):
            return super().represent_scalar(tag, value, style='|')
        return super().represent_scalar(tag, value, style)


data_path = os.path.join(os.path.dirname(__file__), 'DataStores')


def section_to_dict(section) -> Dict[str, object]:
    """
    Recursively convert section and its subsections to a dictionary.
    """
    section_dict = {'content': section.text}

    if section.sections:
        section_dict['subsections'] = {
            subsection.title: section_to_dict(subsection) for subsection in section.sections
        }
    return section_dict


def wikipedia_page_to_yaml(term: str, file_name="Encyclopedia"):
    """
    Fetches a Wikipedia page for the given term and stores the content in a YAML file.

    If the page content already exists, it skips the fetch and logs a message.

    :param term: The title of the Wikipedia page to fetch.
    :param file_name: The base name (without extension) for the output YAML file.
    """
    yaml_filename = f"{file_name}.yaml"
    yaml_path = os.path.join(data_path, yaml_filename)

    existing_data = load_existing_yaml(yaml_path)
    if term in existing_data:
        logging.info(f"Data for '{term}' is already present in {yaml_filename}. Skipping fetch.")
        return

    wiki_wiki = wikipediaapi.Wikipedia('ThinkerBot (https://github.com/AaronFR/Thinker)', 'en')
    page = wiki_wiki.page(term)

    if page.exists():
        logging.info(f"Processing page: {page.title}")
        page_dict = build_page_dict(page)

        existing_data.update(page_dict)
        write_to_yaml(existing_data, yaml_path)
        append_redirects_to_yaml(page.title, f"{file_name}Redirects.csv")
        logging.info(f"Page content written to {yaml_filename}")
    else:
        logging.warning(f"No page found for '{term}'.")


def load_existing_yaml(yaml_path: str) -> Dict[str, object]:
    """
    Loads existing data from a YAML file if available.

    :param yaml_path: The path to the YAML file.
    :return: A dictionary containing the loaded data or an empty dictionary.
    """
    existing_data = {}

    if os.path.isfile(yaml_path) and os.path.getsize(yaml_path) > 0:
        try:
            with open(yaml_path, 'r', encoding=DEFAULT_ENCODING) as yaml_file:
                existing_data = yaml.safe_load(yaml_file) or {}
        except (FileNotFoundError, yaml.YAMLError) as e:
            logging.error(f"Error reading YAML file: {e}")
    else:
        logging.info(f"No existing data file found at {yaml_path}.")

    return existing_data


def build_page_dict(page) -> Dict[str, object]:
    """
    Constructs a dictionary representation of the Wikipedia page content.

    :param page: A Wikipedia page object.
    :return: A dictionary representing the summary and sections of the page.
    """
    infobox = get_wikipedia_infobox(page.title)
    page_dict = {
        page.title.lower(): {
            'summary': page.summary,
            'sections': {section.title: section_to_dict(section) for section in page.sections}
        }
    }

    if infobox:
        page_dict[page.title]['infobox'] = infobox_to_dict(infobox)

    return page_dict


def write_to_yaml(data: Dict[str, object], yaml_path: str) -> None:
    """
    Writes the combined page data to a YAML file.

    :param data: The data to write to the YAML file.
    :param yaml_path: The path where the YAML file will be saved.
    """
    try:
        with open(yaml_path, 'w', encoding=DEFAULT_ENCODING) as yaml_file:
            yaml.dump(data, yaml_file, default_flow_style=False, Dumper=MyDumper, allow_unicode=True)
    except Exception as e:
        logging.error(f"Failed to write to YAML file: {e}")


def get_wikipedia_infobox(term: str) -> Optional[str]:
    """
    Fetches the infobox for the specified Wikipedia term.

    :param term: The title of the Wikipedia page from which to fetch the infobox.
    :return: A cleaned infobox string, or None if it does not exist.
    """
    url = f"https://en.wikipedia.org/w/api.php"
    params = {
        'action': 'query',
        'prop': 'revisions',
        'rvprop': 'content',
        'rvsection': 0,  # Retrieve only the top section (infobox usually is there)
        'titles': term,
        'format': 'json',
        'formatversion': 2,
        'rvslots': 'main'
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        page = data['query']['pages'][0]
        if 'revisions' in page:
            content = page['revisions'][0]['slots']['main']['content']
            infobox = get_infobox(content)
            if infobox:
                return clean_infobox(infobox)
            else:
                return None
        else:
            logging.info(f"Page '{term}' does not contain an infobox.")
            return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching infobox for '{term}': {e}")
        return None


def get_infobox(content: str) -> str | None:
    """
    Extracts an infobox from the content of a Wikipedia page. Balanced in that any braces starting braces pair with
    ending braces so only the matching brace for the infobox section is used to extract the infobox

    :param content: The complete content of the Wikipedia page.
    :return: The extracted infobox string or an error message.
    """
    infobox_start = content.find("{{Infobox")
    if infobox_start == -1:
        logging.info(f"No infobox found")
        return None

    brace_count = 0
    index = infobox_start
    while index < len(content):
        if content[index:index+2] == "{{":
            brace_count += 1
            index += 2
        elif content[index:index+2] == "}}":
            brace_count -= 1
            index += 2
            if brace_count == 0:
                return content[infobox_start:index]
        else:
            index += 1

    return "Infobox extraction failed."


def clean_infobox(infobox: str) -> str:
    """
    Cleans and formats the infobox for readability and minimising tokens for llm processing

    :param infobox: The raw infobox string.
    :return: A cleaned infobox string for easier interpretation.
    """
    # Correctly handle val and convert templates, preserving value and unit
    infobox = re.sub(r'{{(val|convert)\|([^|]+)\|([^|}]+)}}', r'\2 \3', infobox)
    infobox = re.sub(r'{{(val|convert)\|([^|]+)\|([^|}]+)\|e=([^|}]+)\|u=([^|}]+)}}', r'\2e\4 \5', infobox)

    # Remove remaining template markers {{template|...}} and plain {{...}}
    infobox = re.sub(r'{{|}}', '', infobox)  # Remove remaining {{ and }}

    # Remove internal Wikipedia links [[link|text]] or [[text]]
    infobox = re.sub(r'\[\[.*?\|', '', infobox)  # Remove link text (e.g. [[link|text]])
    infobox = re.sub(r'\[\[|\]\]', '', infobox)  # Remove remaining [[ and ]]

    # Remove references and HTML-like tags
    infobox = re.sub(r'<.*?>', '', infobox)  # Remove other HTML tags (e.g. <br />)

    # Remove pipes used for formatting but keep important data
    infobox = re.sub(r'\|', ':', infobox)  # Replace pipes with colons for readability

    # Remove extra white spaces and lines
    infobox = re.sub(r'\s*\n\s*', '\n', infobox)  # Clean up extra newlines
    infobox = infobox.strip()  # Strip leading/trailing spaces

    return infobox


def infobox_to_dict(text: str) -> Dict[str, object]:
    """
    Converts the infobox text into dictionary format for structured representation.

    :param text: The infobox text to convert.
    :return: A dictionary representation of the infobox contents.
    """
    result = {}
    current_key = None
    current_list = None

    for line in text.splitlines():
        line = line.strip()
        if not line:  # Skip empty lines
            continue

        # Check if the line starts with a key-value pair
        if line.startswith(":"):
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip().strip(":")
                key = key.strip()
                value = value.strip()

                if value == "plainlist :":
                    current_key = key
                    current_list = []
                    result[current_key] = current_list
                else:
                    result[key] = value
                    current_key = None
                    current_list = None
            else:
                # If no value but a list continuation, append to current list
                if current_list is not None:
                    current_list.append(line.strip(":").strip())
        else:
            # Add extra lines to current list if necessary
            if current_list is not None:
                current_list.append(line)

    return result


def append_redirects_to_yaml(term: str, redirect_file: str) -> None:
    """
    Fetches the redirects for a given page and appends them to a specified CSV file.

    :param term: The title of the Wikipedia page to fetch redirects for.
    :param redirect_file: The path to the CSV file where redirects will be saved.
    """
    redirects = get_redirects(term)
    logging.info(f"Redirects found: {redirects}")

    redirect_dicts = [{'redirect_term': redirect, 'target_term': term} for redirect in redirects]

    if redirect_dicts:
        fieldnames = ['redirect_term', 'target_term']
        FileManagement.write_to_csv(redirect_file, redirect_dicts, fieldnames)
    else:
        logging.info(f"No redirects found for {term}.")


def get_redirects(term: str) -> List[str]:
    """
    Uses the MediaWiki API to fetch the redirect history for the specified Wikipedia page.

    :param term: The title of the Wikipedia page to check for redirects.
    :return: A list of titles for pages that redirect to the specified page.
    """
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        'action': 'query',
        'format': 'json',
        'list': 'backlinks',
        'blfilterredir': 'redirects',
        'bltitle': term,  # Title of the page to check redirects for
        'bllimit': 'max'  # Maximum number of redirects
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()

        redirects = []
        if 'query' in data and 'backlinks' in data['query']:
            redirects = [link['title'] for link in data['query']['backlinks']]
        return redirects
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch redirects for '{term}': {e}")
        return []


if __name__ == "__main__":
    term = input("Enter a search term: ")
    wikipedia_page_to_yaml(term)

