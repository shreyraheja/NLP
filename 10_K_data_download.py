# %% [markdown]
# <b>Import SEC filings from wiki page</b>

# %%
import os
import pickle
import requests
from bs4 import BeautifulSoup

# %%
response = requests.get('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
wiki_soup = BeautifulSoup(response.content, 'lxml')
s = requests.Session()
# %% [markdown]
# <b>Saving Txt files

# %%
if os.path.exists("done_tickers.pickle"):
    with open("done_tickers.pickle", "rb") as fp:
        done_tickers = pickle.load(fp)
else:
    done_tickers = []

# %%
for wikirow in wiki_soup.find('table').find_all('tr'):
    cols_wiki = wikirow.find_all('td')
    if cols_wiki:
        ticker = cols_wiki[0].text.strip()
        print(ticker)
        if ticker in done_tickers:
            continue
        sec_soup = BeautifulSoup(s.get(cols_wiki[2].a['href']+'&type=10-k').content, 'html.parser')
        ten_k_list_table = sec_soup.find_all('table')[2]
        for sec_row in ten_k_list_table.find_all('tr'):
            cols_sec = sec_row.find_all('td')
            if cols_sec:
                date = cols_sec[3].text
                print(f"{ticker}@{date}")
                if os.path.exists(f"{ticker}@{date}.txt"):
                    continue
                filing_soup = BeautifulSoup(s.get('https://www.sec.gov/' + cols_sec[1].find('a', {'href':True, 'id':'documentsbutton'})['href']).content, 'html.parser')
                doc_list_table = filing_soup.find('table')
                txt_url = None
                if ('10-K' in doc_list_table.find_all('tr')[1].find_all('td')[3].get_text()):
                    txt_url = doc_list_table.find_all('tr')[1].find_all('td')[2].find('a')['href']
                else:
                    txt_url = doc_list_table.find_all('tr')[-1].find_all('td')[2].find('a')['href']
                with open(f"{ticker} @{date}.txt", "wb") as f:
                    f.write(s.get('https://www.sec.gov/'+txt_url).content)
        done_tickers.append(ticker)

# %%
with open("done_tickers.pickle", "wb") as fp:
    pickle.dump(done_tickers, fp)

# %% [markdown]
# <b> Using CIKS for files other than wiki

# %%
with open("cik.txt", "rb") as fp:
    cik_list = pickle.load(fp)

with open("ticker.txt", "rb") as fp:
    ticker_list = pickle.load(fp)

mapping = dict(zip(cik_list, ticker_list))

# %%
if os.path.exists("done_ciks.pickle"):
    with open("done_ciks.pickle", "rb") as fp:
        done_ciks = pickle.load(fp)
else:
    done_ciks = []

# %%
for cik in cik_list:
    ticker = mapping[cik]
    print(ticker)
    if ticker in done_ciks:
        continue
    sec_soup = BeautifulSoup(s.get(f'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&type=10-k').content, 'html.parser')
    sec_soup_tables = sec_soup.find_all('table')
    if len(sec_soup_tables) > 2:
        ten_k_list_table = sec_soup_tables[2]
        for sec_row in ten_k_list_table.find_all('tr'):
            cols_j = sec_row.find_all('td')
            if cols_j:
                date = cols_j[3].text
                print(f"{ticker}@{date}")
                if os.path.exists(f"{ticker}@{date}.txt"):
                    continue
                filing_soup = BeautifulSoup(requests.get('https://www.sec.gov/' + cols_j[1].find('a', {'href':True, 'id':'documentsbutton'})['href']).content, 'html.parser')
                doc_list_table = filing_soup.find('table')
                if ('10-K' in doc_list_table.find_all('tr')[1].find_all('td')[3].get_text()):
                    txt_url=doc_list_table.find_all('tr')[1].find_all('td')[2].find('a')['href']
                else:
                    txt_url=doc_list_table.find_all('tr')[-1].find_all('td')[2].find('a')['href']
                with open(f"{ticker}@{date}.txt", "wb") as f:
                    f.write(requests.get('https://www.sec.gov/'+txt_url).content)
    done_ciks.append(cik)

# %%
with open("done_ciks.pickle", "wb") as fp:
    pickle.dump(done_ciks, fp)


# %%
