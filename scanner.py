"""
Read domain list and export data to file
"""
import requests as r
from argparse import ArgumentParser
from concurrent.futures import ProcessPoolExecutor
parser = ArgumentParser()
parser.add_argument('infile', help='File to read url from')
args = parser.parse_args()

# TODO: tags are in file: make dictionary? position = index of line tag comes from?
# Read tags and create encoding dict

# TODO: figure out how to convert to integer consistently, or don't. Maybe same as tags
# Read mimes and create mime dict

# Read domains from file
with open(args.infile, 'r') as f:
    domains = [l.strip().split(',') for l in f.readlines()][1::]


tag_dict = {}
index = 0
with open("tagslist.txt", 'r') as f:
    line = f.readline()
    tag_dict[line] = index
    index += 1

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
    soup = BeautifulSoup(html, "html.parser")
    tags = [tag.name for tag in soup.find_all()]
    for i in tags:
        res.append(find_n_replace(i))
    # TODO
    pass

def analyze_url(url):
    """
    assemble feature data for url
    """
    # Feature list: url entropy, number of redirects, html skeleton vector
    r = requests.get(url[0])

    # If request failed, return False
    if not r.ok:
        return False

    # Extract Feature Data
    url_entropy = url[1]
    number of redirects = len(r.history)
    mime_type = r.headers.get('Content-Type').split(';')[0]

    if 'html' in mime_type:
        vector, links = analyze_html(r.text)
    else:
        vector, links = "", ""

    html_skeleton_vector = vector
    links_on_page = links
    
    # Export data to database
    # TODO: do the sqlalchemy

    return True

#with concurrent.futures.ThreadPoolExecutor() as executor:
#    # Make requests to all domains
#    for url, result in zip(domains, executor.map(analyze_url, domains))
#        print(f'{url[0]} scanned and added: {result}')
debug = True
if __name__ == "__main__":
    if debug = True:
        test_html

