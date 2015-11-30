from bs4 import BeautifulSoup
import requests
from hmc_urllib import getHTML
from scraping_functions import *
from urllib.request import http


def scrape_tournament(filename, url_list):
    """Scrape all the urls in a file and write the corresponding tournament's matches to a text file."""
    for url in url_list:
        print(url)
        if "challonge" in url:
            write_txt_from_challonge(url, filename)
        elif "teamliquid" in url:
            write_txt_from_liquipedia(url, filename)
        elif "smash.gg" in url:
            write_txt_from_smashgg(url, filename)


def write_txt_from_challonge(url, file):
    """Writes the results from a Challonge URL to TxtFile.
Challonge: a string; the URL for a Challonge.
TxtFile: a string; the name of the file to be written.
Example: WriteTxtFromChallonge('http://apex2015melee.challonge.com/singles', 'Apex 2015')"""
    file = add_txt(file)
    webpage = getHTML(url)[0].replace('Mark as In Progress\n\n\nUnmark as In Progress\n\n\n\n', '') \
        .replace('\n\n\n\n\n\nEdit\n\n\nReopen', '').split('\n\n\n\nMatch Details\n\n\n\n\n\n\n')[1:]

    parsed_matches = ""

    for item in webpage:
        item = item.splitlines()
        if item[2] == "" or item[7] == "":
            continue
        try:
            if int(item[24]) < 0:
                continue
        except:
            pass
        try:
            if int(item[27]) < 0:
                continue
        except:
            pass

        line = item[2] + "," + item[24] + "," + item[7] + "," + item[27]
        line = strip_match(line)
        if line is not None and parse_match(line) != "":
            parsed_matches += parse_match(line) + "\n"

    with open(file, 'a') as file:
        file.write(parsed_matches)


def format_liquipedia_url(url):
    """Converts bracket url to source url, if necessary."""
    if not "&action=edit" in url:
        url = re.sub("(wiki\.teamliquid\.net/smash/)(.*)", r"\1index.php?title=\2&action=edit", url)
    return url


def write_txt_from_liquipedia(url, filename):
    """Returns match data from a Liquipedia link."""
    url = format_liquipedia_url(url)

    try:
        soup = BeautifulSoup(requests.get(url).content)
    except http.client.IncompleteRead as e:
        soup = BeautifulSoup(e.partial)

    match_data = str(soup.find("textarea"))

    matches = ""
    prev_line_start = "xxxx"
    for line in match_data.split("\n"):
        if re.match('^\|[rl]\d+m\d+', line):
            if line.startswith(prev_line_start):
                matches += " " + line
            else:
                matches += "\n" + line
                prev_line_start = re.sub('^(\|[rl]\d+m\d+).*', r'\1', line)

    parsed_matches = ""
    for line in matches.split("\n"):
        stripped_line = strip_match(line)
        if stripped_line is not None and match_played(url, line):
            parsed_match = parse_match(stripped_line)
            if parsed_match != "":
                parsed_matches += parsed_match + "\n"

    with open(filename, 'a', encoding="utf8") as file:
        file.write(parsed_matches)


def format_smashgg_url(url):
    """Converts bracket url to api url, if necessary."""
    if not "api.smash.gg" in url:
        url = "http://api.smash.gg/phase_group/" + url.split("/")[-1] + "?expand[0]=sets&expand[1]=entrants"
    return url


def parse_smashgg_set(set, entrant_dict):
    """Returns the winner and loser of a smash.gg set."""
    winnerId = set["winnerId"]
    entrant1Id = set["entrant1Id"]
    entrant1Score = set["entrant1Score"]
    entrant2Id = set["entrant2Id"]
    entrant2Score = set["entrant2Score"]

    if set["completedAt"]:
        entrant1Name = normalize_name(entrant_dict[entrant1Id])
        entrant2Name = normalize_name(entrant_dict[entrant2Id])

        if type(entrant1Score) is int and type(entrant2Score) is int:
            if entrant1Score > -1 and entrant2Score > -1:
                if entrant1Id == winnerId:
                    return(entrant1Name + "," + entrant2Name)
                else:
                    return(entrant2Name + "," + entrant1Name)
        else:
            if entrant1Id == winnerId:
                return(entrant1Name + "," + entrant2Name)
            else:
                return(entrant2Name + "," + entrant1Name)


def write_txt_from_smashgg(url, filename):
    """Writes smash.gg bracket data to a file."""
    url = format_smashgg_url(url)
    data = requests.get(url).json()

    entrants = data["entities"]["entrants"]
    entrant_dict = {}
    for entrant in entrants:
        entrant_dict[entrant["id"]] = entrant["name"]

    sets = data["entities"]["sets"]
    set_data = []
    grand_finals = []
    for set in sets:
        parsed_set = parse_smashgg_set(set, entrant_dict)
        if parsed_set:
            if set["isGF"]:
                grand_finals.append(parsed_set)
            else:
                set_data.append(parsed_set)
    parsed_matches = set_data + grand_finals
    with open(filename, 'a', encoding="utf8") as file:
        file.write(parsed_matches)
