from os.path import join
from unicodedata import name
from bs4 import BeautifulSoup
import requests
import pandas as pd
from datetime import datetime

def get_urls(url_base):
    page = 2
    error = False
    pages = []
    while not error:
        url_page = join(url_base, 'page', str(page), '')
        response = requests.get(url_page)
        if response.status_code == 200:
            pages.append(url_page)
        else:
            error = True
        page += 1
    
    return pages

def get_soup(url):
    # Get the response from the blog
    response_text = requests.get(url).text
    # Create the soup
    soup = BeautifulSoup(response_text, 'html.parser')

    return soup

def read_titles(soup):
    # Find and list every post
    posts_titles = soup.select('h2.entry-title')
    # Clean the titles
    cleaned_posts_titles = [title.text for title in posts_titles]

    return cleaned_posts_titles

def read_dates(soup):
    # Read the date of the post
    posts_dates = soup.select('time', {'class' : 'entry-date published'})
    # Clean the dates
    cleaned_posts_dates = [date['datetime'] for date in posts_dates if 'entry-date' in date['class']]

    return cleaned_posts_dates

def read_content(soup):
    posts_content = soup.find_all('div', 'entry-content')
    cleaned_posts_content = []
    for tag in posts_content:
        post_text = tag.find_all('p')
        p_posts = [post.text.replace('\t', ' ') for post in post_text]
        cleaned_posts_content.append(' '.join(p_posts))

    return cleaned_posts_content

def export_dataset(df, path, name, format = 'csv'):
    final_path = join(path, f'{name}.{format}')

    if format == 'csv':
        df.to_csv(
            final_path,
            index = False,
            sep = '|',
            header = True,
            encoding = 'utf-8'
        )
    elif format == 'xlsx':
        df.to_excel(
            final_path,
            index = False
        )
    else:
        raise Exception('The format is not valid')

if __name__ == '__main__':
    url_base = 'https://carlosandresosorioblog.wordpress.com/'
    urls = [url_base] + get_urls(url_base)
    list_df_posts = []
    
    for url in urls:
        try:
            soup = get_soup(url)
            posts_titles = read_titles(soup)
            posts_dates = read_dates(soup)
            posts_content = read_content(soup) 

            df_temp = pd.DataFrame(
                data = {'title' : posts_titles,
                        'date' :  posts_dates,
                        'content' : posts_content
                }
            ) 

            list_df_posts.append(df_temp)
            print(f'The page {url} was succesfully processed')

        except Exception as e:
            print('Ops, something happened in the page:', url, e)

    df_posts = pd.concat(list_df_posts)

    # Path to export data
    path = '/Users/carlosandresosorioalcalde/Documents/GitHub/Analizandome'
    filename = 'notas_en_blanco'
    export_dataset(df_posts, path, filename)
    