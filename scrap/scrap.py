import requests
from bs4 import BeautifulSoup
import json
import pandas as pd

# Load the IMDB and Netflix data
imdb = pd.read_csv('../data/title.basics.tsv', sep='\t')
imdb = imdb[(imdb['titleType'] == 'movie') | (imdb['titleType'] == 'tvSeries')]
imdb['primaryTitle'] = imdb['primaryTitle'].str.lower()

netflix = pd.read_csv('../data/netflix_titles.csv')
netflix['type'] = netflix['type'].apply(lambda x: 'movie' if x == 'Movie' else 'tvSeries')
netflix['release_year'] = netflix['release_year'].astype(str)
netflix['title'] = netflix['title'].str.lower()

# Merge the dataframes on the title and release year
df = pd.merge(imdb, netflix, left_on=['primaryTitle', 'startYear'], right_on=['title', 'release_year'], how='inner')

header = {'User-Agent': 'Mozilla/5.0'}

s = requests.Session()
s.headers.update(header)

counter = 0

with open('../data/movie_data.json', 'a') as f:
# For every title in the dataframe, send a request to IMDB using the tconst
    for index, row in df.iloc[:10, :].iterrows():
        try:
            response = s.get(f'https://www.imdb.com/title/{row["tconst"]}/')

            # Parse the response with BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find the rating
            rating = soup.find('span', class_='sc-eb51e184-1 ljxVSS').text

            # Find the plot
            plot = soup.find('div', class_='ipc-html-content-inner-div').text

            # Find the review
            review = [r.text for r in soup.find('div', class_='ipc-html-content ipc-html-content--base').children][0]

            # Find the genres
            genres = [c.text for c in soup.find('div', class_='ipc-chip-list__scroller').children]

            # Define a dictionary to store the information
            movie_data = {
                'title': row['title'],
                'tconst': row['tconst'],
                'type': row['type'],
                'rating': rating,
                'plot': plot,
                'review': review,
                'genres': genres
            }

            # Save the data to a text file in JSON format
            f.write(json.dumps(movie_data, indent=4) + '\n')  # Append each movie as a new line of JSON

            counter += 1
            print(f"Processed {counter} of {df.shape[0]} movies.")
        except Exception as e:
            print(f"Error processing {row['title']}: {e}")

print("Movie data collection complete.")