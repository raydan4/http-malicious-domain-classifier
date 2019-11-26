"""
Read domain list and export data to file
"""
from requests import get
from bs4 import BeautifulSoup
from argparse import ArgumentParser
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import ThreadPoolExecutor


from sqlalchemy import Column, Integer, String, BLOB, Date, ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

parser = ArgumentParser()
parser.add_argument('infile', help='File to read url from')
args = parser.parse_args()

Base = declarative_base()

engine = create_engine('sqlite:////tmp/tmpdb.sql')

Session = sessionmaker(bind=engine)
session = Session()

class Record(Base):
    __tablename__ = 'record'

    id = Column(Integer, primary_key=True)
    redirect_count = Column(Integer)
    html_vector = Column(String)
    mime_type = Column(String)
    url_entropy = Column(String)
    links_on_page = Column(String)

# Read domains from file
with open(args.infile, 'r') as f:
    domains = [l.strip().split(',') for l in f.readlines()][1::]


tag_dict = {}
index = 0
with open("tagslist.txt", 'r') as f:
    line = f.readline()
    while(line):
        tag_dict[line.strip()] = index
        index += 1
        line = f.readline()

def find_n_replace(tag):
    return tag_dict[tag]


def analyze_html(text):
    """
    Take html body
    parse with BS
        build skeleton vector based on tags from doct
        get links on page
    """
    res = []
    soup = BeautifulSoup(text, "html.parser")
    tags = [tag.name for tag in soup.find_all()]
    for i in tags:
        res.append(find_n_replace(i))
    a = soup.find_all('a')
    if a: links = [l for l in (a.attrs.get('href') for a in a) if '://' in l]
    else: links = []
    return res, len(links), ' '.join(links)

def analyze_url(url):
    """
    assemble feature data for url
    """
    # Feature list: url entropy, number of redirects, html skeleton vector
    tmp = url[0]
    if "http" not in tmp:
        tmp = "http://" + tmp

    try :
        r = get(f'http://{url[0]}')
    except:
        return False
    # If request failed, return False
    if not r.ok:
        return False

    # Extract Feature Data
    url_entropy = url[1]
    number_of_redirects = len(r.history)
    mime_type = r.headers.get('Content-Type').split(';')[0]

    if 'html' in mime_type and r.text:
        vector, num_links, links = analyze_html(r.text)
    else:
        vector, num_links, links = "None", 0, "None"
    
    return f'{number_of_redirects},{vector},{mime_type},{url_entropy},{num_links},{links}\n'

with ThreadPoolExecutor(max_workers=200) as executor:
    # Make requests to all domains
    for url, result in zip(domains, executor.map(analyze_url, domains)):
        with open('maldata.csv', 'a+') as f:
            if result: f.write(result)
#        myrecord = Record(redirect_count=number_of_redirects, \
#                    html_vector=html_skeleton_vector, \
#                    mime_type=mime_type, \
#                    url_entropy=url_entropy, \
#                    links_on_page=links_on_page)
#        session.add(myrecord)
#        session.commit()

