import requests
import pandas as pd
from bs4 import BeautifulSoup
import re

wiki_page_url = 'https://en.wikipedia.org/wiki/List_of_animal_names'
table_id = 'Terms_by_species_or_taxon'
table_class = 'wikitable sortable'
html_parser = 'html.parser'


def get_animals_without_collective_nouns(wiki_page_url):
    # Make a request to the Wikipedia page
    wiki_page_response = requests.get(wiki_page_url)

    # Get the HTML content from the response
    html_content = wiki_page_response.text

    # Create a BeautifulSoup object to parse the HTML
    soup = BeautifulSoup(html_content, html_parser)

    # Find the span tag with the id "Terms_by_species_or_taxon"
    span_tag = soup.find('span', {'id': table_id})

    # Find the table within the span tag
    if span_tag:
        table = span_tag.find_next('table', {'class': table_class})

        if table:
            # Extract table data into a list of lists
            rows = []
            for row in table.find_all('tr'):
                cells = row.find_all(['td', 'th'])
                row_data = [cell.text.strip() for cell in cells]
                rows.append(row_data)

            # Create a DataFrame from the list of lists
            df = pd.DataFrame(rows[1:], columns=rows[0])

            results = []

            # Iterate over rows in the DataFrame
            for index, row in df.iterrows():
                # Check if "Collective noun" is represented by a dash "-"
                if row["Collective noun"] == "—":
                    result = f'"{row["Animal"]} - {row["Collateral adjective"]}"'
                    results.append(result)

                # Print the results as a single line
            print(", ".join(results))

        else:
            print("Table not found within the specified span tag.")
    else:
        print("Span tag not found with the specified id.")


def get_animals_with_multiple_collective_nouns(wiki_page_url):
    # Make a request to the Wikipedia page
    wiki_page_response = requests.get(wiki_page_url)

    # Parse the HTML content
    html_content = wiki_page_response.text
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the span tag with the id "Terms_by_species_or_taxon"
    span_tag = soup.find('span', {'id': 'Terms_by_species_or_taxon'})

    # Find the table within the span tag
    if span_tag:
        table = span_tag.find_next('table', {'class': 'wikitable'})

        if table:
            # Extract table data into a list of lists
            rows = []
            for row in table.find_all('tr'):
                cells = row.find_all(['td', 'th'])
                row_data = []

                for cell in cells:
                    # Exclude unwanted characters and words
                    cell_text = ', '.join(part.strip() for part in cell.stripped_strings if not (re.match(r'\[\w+\]',
                                        part) or part.startswith('(') or part.endswith(')') or part.startswith('/')))
                    row_data.append(cell_text)

                rows.append(row_data)

            # Create a DataFrame from the list of lists, excluding rows where 'Collective noun' is '—'
            df = pd.DataFrame(rows[1:], columns=rows[0]).replace('—', pd.NA).dropna(subset=['Collective noun'])

            # Create a dictionary to store collective nouns for each animal
            animal_nouns_dict = {}

            # Iterate through the DataFrame and store collective nouns for each animal
            for index, row in df.iterrows():
                animal_name = re.sub(r'\(.*?\)', '', row['Animal']).strip()
                collective_nouns = [noun.strip() for noun in row['Collective noun'].split(',')]

                if animal_name in animal_nouns_dict:
                    animal_nouns_dict[animal_name].extend(collective_nouns)
                else:
                    animal_nouns_dict[animal_name] = collective_nouns

            # Iterate through the dictionary and print results
            for animal, nouns in animal_nouns_dict.items():
                if len(set(nouns)) > 1:
                    output_str = ', '.join([f'"{animal} - {noun}"' for noun in set(nouns)])
                    print(output_str)


print('Output task 1:\n')
get_animals_without_collective_nouns(wiki_page_url)
print('\nOutput task 2:\n')
get_animals_with_multiple_collective_nouns(wiki_page_url)

