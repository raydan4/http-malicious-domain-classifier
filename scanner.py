"""
Read domain list and export data to file
"""
from requests import get
from bs4 import BeautifulSoup
from argparse import ArgumentParser


parser = ArgumentParser()
parser.add_argument('infile', help='File to read url from')
parser.add_argument('outfile', help='File to write results to')
parser.add_argument('-l', '--line', type=int, default=0, help='Line of infile to start scanning on')
args = parser.parse_args()

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
    try:
        return str(tag_dict[tag])
    except KeyError:
        return str(999)


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
    if a: links = [l for l in (h.attrs.get('href') for h in a if h.attrs.get('href')) if '://' in l]
    else: links = []
    return ' '.join(res), len(links), ' '.join(links)

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

    # First Checkpoint
    print('.', end='')

    # Extract Feature Data
    url_entropy = url[1]
    print('.', end='')
    number_of_redirects = len(r.history)
    print('.', end='')
    mime_type = r.headers.get('Content-Type').split(';')[0] if r.headers.get('Content-Type') else 'None'
    print('.', end='')

    if 'html' in mime_type and r.text:
        vector, num_links, links = analyze_html(r.text)
    else:
        vector, num_links, links = "None", 0, "None"
    if num_links == 0:
        links = "None"
    print('.', end='')
    
    return f'{number_of_redirects},{vector},{mime_type},{url_entropy},{num_links},{links}\n'


for url in domains[args.line:]:
    print(f'scanning [{url[0]}]', end=': ')
    with open(args.outfile, 'a+') as f:
        data = analyze_url(url)
        if data:
            f.write(data)
            print(f'done')
        else: print('failed')

