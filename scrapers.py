from bs4 import BeautifulSoup
import re
import requests
from hmc_urllib import getHTML
from urllib.request import http
import scraping_functions as sf


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
    file = sf.add_txt(file)
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
        line = sf.strip_match(line)
        if line is not None and sf.parse_match(line) != "":
            parsed_matches += sf.parse_match(line) + "\n"

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
        stripped_line = sf.strip_match(line)
        if stripped_line is not None and sf.match_played(url, line):
            parsed_match = sf.parse_match(stripped_line)
            if parsed_match != "":
                parsed_matches += parsed_match + "\n"

    with open(filename, 'a', encoding="utf8") as file:
        file.write(parsed_matches)


def format_smashgg_url(url):
    """Converts bracket url to api url, if necessary."""
    if "api.smash.gg" not in url:
        url = "http://api.smash.gg/phase_group/" + url.split("/")[-1]
    api_string = "?expand[0]=sets&expand[1]=entrants"
    if api_string not in url:
        url += api_string
    return url


def parse_smashgg_set(set, entrant_dict):
    """Returns the winner and loser of a smash.gg set."""
    winnerId = set["winnerId"]
    entrant1Id = set["entrant1Id"]
    entrant1Score = set["entrant1Score"]
    entrant2Id = set["entrant2Id"]
    entrant2Score = set["entrant2Score"]

    if entrant1Id and entrant2Id:
        entrant1Name = sf.normalize_name(entrant_dict[entrant1Id])
        entrant2Name = sf.normalize_name(entrant_dict[entrant2Id])

        if type(entrant1Score) is int and type(entrant2Score) is int:
            if entrant1Score > -1 and entrant2Score > -1:
                if entrant1Id == winnerId:
                    return entrant1Name + "," + entrant2Name
                else:
                    return entrant2Name + "," + entrant1Name
        else:
            if entrant1Id == winnerId:
                return entrant1Name + "," + entrant2Name
            else:
                return entrant2Name + "," + entrant1Name


def write_txt_from_smashgg(url, filename):
    """Writes smash.gg bracket data to a file."""
    url = format_smashgg_url(url)
    data = requests.get(url).json()

    entrants = data["entities"]["entrants"]
    entrant_dict = {}
    for entrant in entrants:
        entrant_dict[entrant["id"]] = entrant["name"]

    sets = data["entities"]["sets"]
    set_data = ""
    grand_finals = ""
    for set in sets:
        parsed_set = parse_smashgg_set(set, entrant_dict)
        if parsed_set:
            if set["isGF"]:
                grand_finals += parsed_set + "\n"
            else:
                set_data += parsed_set + "\n"
    parsed_matches = set_data + grand_finals
    with open(filename, 'a', encoding="utf8") as file:
        file.write(parsed_matches)

if __name__ == "__main__":
    with open("MeleeUrls/Tipped-Off-11.txt", "r") as file:
        for line in file:
            write_txt_from_smashgg(line.strip(), "MeleeResults/Tipped-Off-11.txt")
