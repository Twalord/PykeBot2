"""
Handles scraping of the prime league page.
:author: Jonathan Decker
"""

import asyncio
import logging
import time
import aiohttp
import bs4
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from PykeBot2.models.data_models import TeamList, Team, Player, TeamListList
from selenium.common.exceptions import ElementClickInterceptedException
from PykeBot2 import gecko_manager

logger = logging.getLogger("pb_logger")


async def stalk_prime_league_season(prime_league_season_link: str, headless=True):
    """
    :description: Uses Selenium to open the link and gather all group links from it,
    further calls stalk prime league group on all groups.
    :param prime_league_season_link: A valid link to a prime league season.
    :type prime_league_season_link: str
    :param headless: Whether the browser should be headless or not. Use head for debugging purposes.
    :type headless: bool
    :return: TeamListList object containing all gathered information.
    :rtype: TeamListList
    """

    driver = gecko_manager.open_session(headless)

    # TODO add error handling
    driver.get(prime_league_season_link)

    # Select Gruppenphase Container
    div_button_list = driver.find_elements(By.CLASS_NAME, "content-subsection")
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
            footer_bottom = driver.find_element(By.XPATH, '//*[@id="footer-bottom"]')
            driver.execute_script(
                "arguments[0].setAttribute('style','display:none;');", footer_bottom
            )

            time.sleep(0.1)

            div_button.click()
            click_counter -= 1

    soup = bs4.BeautifulSoup(driver.page_source, features="html.parser")
    box_container = soup.find_all("section", class_="boxed-section")
    gruppenphase = "Gruppenphase"

    for box in box_container:
        title = box.find_all("h2")
        if len(title) > 0:
            if gruppenphase in title[0].text:
                group_stage_container = box

    # extract all group-links
    group_links = [
        link["href"] for link in group_stage_container.find_all("a", href=True)
    ]

    group_links = list(dict.fromkeys(group_links))

    group_links = filter(filter_group_links, group_links)

    # close web session
    gecko_manager.quit_session(driver)

    # custom connector to limit parallel connection pool, to avoid crashes
    conn = aiohttp.TCPConnector(limit=20)
    async with aiohttp.ClientSession(connector=conn) as session:
        team_lists = []
        for link in group_links:
            team_lists.append(await stalk_prime_league_group(link, session))
        # calling gather here causes instability. Due to too many calls?
        # team_lists = await asyncio.gather(*(stalk_prime_league_group(link, session) for link in group_links))

    return TeamListList(team_lists)


def filter_group_links(link):
    """
    Helper function to filter out non group links.
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
    Helper function to filter out non team links.
    :param link: Str, a web link
    :return: Bool, true if the link contains a teams, false if not
    """
    link_split = link.split("/")
    for split in link_split:
        if split == "teams":
            return True
    return False


async def stalk_prime_league_group(
    prime_league_group_link: str,
    session: aiohttp.ClientSession = None,
    headless: bool = True,
):
    """
    :description: Uses aiohttp requests to stalk a prime league group.
    Also contains an extra case for the swiss starter group.
    :param prime_league_group_link: A valid link to a prime league group.
    :type prime_league_group_link: str
    :param session: When a session already exits, it should be reused as much as possible for better performance.
    :type session: aiohttp.ClientSession
    :param headless: The swiss starter group regroup requires the selenium webriver. Use for debugging.
    :type headless: bool
    :return: TeamList object containing all gathered information.
    :rtype: TeamList
    """

    if session is None:
        async with aiohttp.ClientSession() as session:
            return await stalk_prime_league_group(prime_league_group_link, session)

    async with session.get(prime_league_group_link) as response:
        # TODO add error handling
        page = await response.text()

    # Select Rangliste Container and find division name
    soup = bs4.BeautifulSoup(page, features="html.parser")
    list_container = soup.find(
        "table", class_="table table-ranking"
    )

    # extra case for swiss starter since it uses a different table and needs selenium as far as I know
    if list_container is None:
        driver = gecko_manager.open_session(headless)

        driver.get(prime_league_group_link)

        # wait a moment for the full page to load
        time.sleep(1)

        # click away cookie banner
        try:
            cookie_no_button = driver.find_element(By.XPATH, '//*[@id="uc-btn-deny-banner"]')
            cookie_no_button.click()
        except NoSuchElementException as e:
            # if there is no cookie banner just proceed
            pass

        # first make sure all tables are loaded by clicking on arrow button until no longer possible
        try:
            next_button = driver.find_element(By.XPATH, '//*[@id="league-swiss-ranking-tab-main"]/div[2]/div[2]/a[3]')

            while next_button.get_attribute("class") == "nav-next":
                next_button.click()

            # jump back to first page
            driver.find_element(By.XPATH, '//*[@id="league-swiss-ranking-tab-main"]/div[2]/div[2]/a[1]/i').click()
        except NoSuchElementException as e:
            # if there is no next button then all elements must be already loaded
            pass

        soup = bs4.BeautifulSoup(driver.page_source, features="html.parser")

        gecko_manager.quit_session(driver)

        list_containers = soup.find_all("table", class_="table table-fixed-single")

        # extract all team-links
        team_links = []
        for list_container in list_containers:
            team_links.extend(
                [link["href"] for link in list_container.find_all("a", href=True)]
            )

    else:
        # extract all team-links
        team_links = [link["href"] for link in list_container.find_all("a", href=True)]

    # if finding team links fails, try a work around
    if len(team_links) == 0:
        team_links = [link["href"] for link in soup.find_all("a", href=True)]
        team_links = filter(filter_team_links, team_links)

    div_name = soup.select(".page-title > h1:nth-child(1)")[0].text

    team_links = list(dict.fromkeys(team_links))

    team_links = filter(filter_team_links, team_links)

    teams = await asyncio.gather(
        *(stalk_prime_league_team(link, session) for link in team_links)
    )

    filter_teams = [team for team in teams if team]

    return TeamList(div_name, filter_teams)


async def stalk_prime_league_team(
    prime_league_team_link: str, session: aiohttp.ClientSession = None
):
    """
    :description: Uses aiohttp requests to stalk a prime league team.
    :param prime_league_team_link:
    :type prime_league_team_link:
    :param session: When a session already exits, it should be reused as much as possible for better performance.
    :type session: aiohttp.ClientSession
    :return: Team object containing all the gathered information.
    :rtype: Team
    """

    if session is None:
        async with aiohttp.ClientSession() as session:
            return await stalk_prime_league_team(prime_league_team_link, session)

    async with session.get(prime_league_team_link) as response:
        # TODO add error handling
        page = await response.text()

    # Select Teammitglieder Container and find team name
    soup = bs4.BeautifulSoup(page, features="html.parser")
    player_container = soup.find("ul", class_="content-portrait-grid-l")

    # check if the team was deleted
    if player_container is None:
        return None

    team_container = soup.find("div", class_="content-portrait-head")
    # behind the team name is always " « League Teams « Prime League", which needs to be removed
    # this solution will fail if a team uses « in their name
    team_name = soup.title.text.split("«")[0].strip()

    # extract player names
    player_boxes = player_container.find_all("li")
    tuple_list = []
    for box in player_boxes:
        confirmed = box.find("span", class_="txt-status-positive")
        player_info = box.find(
            "span", title="League of Legends » LoL Summoner Name (EU West)"
        )
        tuple_list.append((player_info, confirmed))

    # create Team object and filter out unconfirmed player
    player_names = []
    confirmed_check = "Bestätigter Spieler"
    for player, confirm in tuple_list:
        if confirm is not None and confirm.text == confirmed_check:
            player_obj = Player(player.text)
            player_names.append(player_obj)

    return Team(team_name, player_names)
