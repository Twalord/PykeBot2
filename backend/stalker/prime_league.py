"""
Handles scraping of the prime league page.
:author: Jonathan Decker
"""

import asyncio
import logging
import time
import aiohttp
import bs4
from models.data_models import TeamList, Team, Player, TeamListList
from selenium.common.exceptions import ElementClickInterceptedException
import gecko_manager

logger = logging.getLogger("pb_logger")


async def stalk_prime_league_season(prime_league_season_link: str, headless=True):
    """

    :param prime_league_season_link:
    :type prime_league_season_link:
    :param headless:
    :type headless:
    :return:
    :rtype:
    """

    driver = gecko_manager.open_session(headless)

    # TODO add error handling
    driver.get(prime_league_season_link)

    # Select Gruppenphase Container
    div_button_list = driver.find_elements_by_class_name("content-subsection")
    # division 1 and 2 are expanded by default
    # with starter division it takes exactly 5 clicks
    click_counter = 5
    for div_button in reversed(div_button_list):
        if click_counter == 0:
            break
        try:
            div_button.click()
            click_counter -= 1
        except ElementClickInterceptedException:
            # footer-bottom is in the way, so execute some js to remove visibility
            footer_bottom = driver.find_element_by_xpath("//*[@id=\"footer-bottom\"]")
            driver.execute_script("arguments[0].setAttribute('style','display:none;');", footer_bottom)

            time.sleep(0.1)

            div_button.click()
            click_counter -= 1


    soup = bs4.BeautifulSoup(driver.page_source, features="html.parser")
    box_container = soup.find_all('section', class_="boxed-section")
    gruppenphase = "Gruppenphase"

    for box in box_container:
        title = box.find_all("h2")
        if len(title) > 0:
            if gruppenphase in title[0].text:
                group_stage_container = box



    # extract all group-links
    group_links = [link["href"] for link in group_stage_container.find_all("a", href=True)]

    group_links = list(dict.fromkeys(group_links))

    group_links = filter(filter_group_links, group_links)

    # close web session
    gecko_manager.quit_session(driver)

    async with aiohttp.ClientSession() as session:
        team_lists = await asyncio.gather(*(stalk_prime_league_group(link, session) for link in group_links))

    return TeamListList(team_lists)


def filter_group_links(link):
    """
    Helper function to filter out non group links
    :param link: Str, a web link
    :return: Bool, true if the link contains a keyword and leads to a group, false if not
    """
    keywords = ["gruppenphase", "group"]
    link_split = link.split("/")
    for split in link_split:
        if split in keywords:
            return True
    return False


def filter_team_links(link):
    """
    Helper function to filter out non team links
    :param link: Str, a web link
    :return: Bool, true if the link contains a teams, false if not
    """
    link_split = link.split("/")
    for split in link_split:
        if split == "teams":
            return True
    return False


async def stalk_prime_league_group(prime_league_group_link: str, session: aiohttp.ClientSession = None,
                                   headless: bool = True):
    """

    :param prime_league_group_link:
    :type prime_league_group_link:
    :param session:
    :type session:
    :param headless:
    :type headless:
    :return:
    :rtype:
    """

    if session is None:
        async with aiohttp.ClientSession() as session:
            return await stalk_prime_league_group(prime_league_group_link, session)

    async with session.get(prime_league_group_link) as response:
        # TODO add error handling
        page = await response.text()

    # Select Rangliste Container and find division name
    soup = bs4.BeautifulSoup(page, features="html.parser")
    list_container = soup.find('table', class_="table table-fixed-single table-responsive")

    # extra case for swiss starter since it uses a different table and needs selenium as far as I know
    if list_container is None:
        driver = gecko_manager.open_session(headless)

        driver.get(prime_league_group_link)

        # first make sure all tables are loaded by clicking on arrow button until no longer possible
        next_button = driver.find_element_by_xpath("//*[@id=\"league-swiss-ranking-tab-main\"]/div[2]/div[2]/a[3]")

        while next_button.get_attribute("class") == "nav-next":
            next_button.click()

        # jump back to first page
        driver.find_element_by_xpath("//*[@id=\"league-swiss-ranking-tab-main\"]/div[2]/div[2]/a[1]/i").click()

        soup = bs4.BeautifulSoup(driver.page_source, features="html.parser")

        gecko_manager.quit_session(driver)

        list_containers = soup.find_all('table', class_="table table-fixed-single")

        # extract all team-links
        team_links = []
        for list_container in list_containers:
            team_links.extend([link["href"] for link in list_container.find_all("a", href=True)])

    else:
        # extract all team-links
        team_links = [link["href"] for link in list_container.find_all("a", href=True)]

    # div_name = driver.find_element_by_xpath("//*[@id=\"container\"]/div/h1").text
    div_name = soup.select("#container > div > h1")[0].text

    team_links = list(dict.fromkeys(team_links))

    team_links = filter(filter_team_links, team_links)

    teams = await asyncio.gather(*(stalk_prime_league_team(link, session) for link in team_links))

    filter_teams = [team for team in teams if team]

    return TeamList(div_name, filter_teams)


async def stalk_prime_league_team(prime_league_team_link: str, session: aiohttp.ClientSession = None):
    """

    :param prime_league_team_link:
    :type prime_league_team_link:
    :param session:
    :type session:
    :return:
    :rtype:
    """

    if session is None:
        async with aiohttp.ClientSession() as session:
            return await stalk_prime_league_team(prime_league_team_link, session)

    async with session.get(prime_league_team_link) as response:
        # TODO add error handling
        page = await response.text()

    # Select Teammitglieder Container and find team name
    soup = bs4.BeautifulSoup(page, features="html.parser")
    player_container = soup.find('ul', class_="content-portrait-grid-l")

    # check if the team was deleted
    if player_container is None:
        return None

    team_container = soup.find('div', class_="content-portrait-head")
    team_name = team_container.find("a").text

    # extract player names
    player_boxes = player_container.find_all('li')
    tuple_list = []
    for box in player_boxes:
        confirmed = box.find('span', class_="txt-status-positive")
        player_info = box.find('span', title="League of Legends » LoL Summoner Name (EU West)")
        tuple_list.append((player_info, confirmed))

    # create Team object and filter out unconfirmed player
    player_names = []
    confirmed_check = "Bestätigter Spieler"
    for player, confirm in tuple_list:
        if confirm is not None and confirm.text == confirmed_check:
            player_obj = Player(player.text)
            player_names.append(player_obj)

    return Team(team_name, player_names)
