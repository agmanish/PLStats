#!/usr/bin/env python3
"""
Module Docstring
"""

__author__ = "A.G. Manish"  
__version__ = "0.1.0"
__license__ = "MIT"

import requests
import pandas as pd
import argparse
from datetime import datetime

# Necessary Variables are initialized
seasons = [
    "2021/22",
    "2020/21",
    "2019/20",
    "2018/19",
    "2017/18",
    "2016/17",
    "2015/16",
    "2014/15",
    "2013/14",
    "2012/13",
    "2011/12",
    "2010/11",
    "2009/10",
    "2008/09",
    "2007/08",
    "2006/07",
    "2005/06",
    "2004/05",
    "2003/04",
    "2002/03",
    "2001/02",
    "2000/01",
    "1999/00",
    "1998/99",
    "1997/98",
    "1996/97",
    "1995/96",
    "1994/95",
    "1993/94",
    "1992/93",
]
season_ids = [
    418,
    363,
    274,
    210,
    79,
    54,
    42,
    27,
    22,
    21,
    20,
    19,
    18,
    17,
    16,
    15,
    14,
    13,
    12,
    11,
    10,
    9,
    8,
    7,
    6,
    5,
    4,
    3,
    2,
    1,
]
api_links = {
    "teams": "https://footballapi.pulselive.com/football/teams/",
    "club_stats": "https://footballapi.pulselive.com/football/stats/team/",
    "players": "https://footballapi.pulselive.com/football/players",
    "player_stats": "https://footballapi.pulselive.com/football/stats/player/",
}

# Function to generate season codes.
def season_code(year):
    season = {
        "2021/22": 418,
        "2020/21": 363,
        "2019/20": 274,
        "2018/19": 210,
        "2017/18": 79,
        "2016/17": 54,
        "2015/16": 42,
        "2014/15": 27,
        "2013/14": 22,
        "2012/13": 21,
        "2011/12": 20,
        "2010/11": 19,
        "2009/10": 18,
        "2008/09": 17,
        "2007/08": 16,
        "2006/07": 15,
        "2005/06": 14,
        "2004/05": 13,
        "2003/04": 12,
        "2002/03": 11,
        "2001/02": 10,
        "2000/01": 9,
        "1999/00": 8,
        "1998/99": 7,
        "1997/98": 6,
        "1996/97": 5,
        "1995/96": 4,
        "1994/95": 3,
        "1993/94": 2,
        "1992/93": 1,
        "All": None,
    }
    return season.get(year, None)

# Function to retrieve list of all participant teams in JSON format
def team_api_json(
    api_link,
    pageSize=100,
    compSeasons=None,
    compCodeForActivePlayer="null",
    comps=1,
    altIds="true",
    page=0,
    header_account="premierleague",
    header_origin="https://www.premierleague.com",
):
    r = requests.get(
        api_link,
        params={
            "pageSize": pageSize,
            "compSeasons": compSeasons,
            "compCodeForActivePlayer": compCodeForActivePlayer,
            "comps": comps,
            "altIds": altIds,
            "page": page,
        },
        headers={"account": header_account, "origin": header_origin},
    )
    return r.json()

# Function tp retrieve JSON of club stats
def club_api_json(
    api_link,
    pageSize=100,
    compSeasons=None,
    compCodeForActivePlayer="null",
    comps=1,
    altIds="true",
    page=0,
    header_account="premierleague",
    header_origin="https://www.premierleague.com",
):
    r = requests.get(
        api_link,
        params={
            "pageSize": pageSize,
            "compSeasons": compSeasons,
            "compCodeForActivePlayer": compCodeForActivePlayer,
            "comps": comps,
            "altIds": altIds,
            "page": page,
        },
        headers={"account": header_account, "origin": header_origin},
    )
    return r.json()

# Function that outputs basic info about clubs in pandas Data Frame
def club_basics(api_link):
    data=team_api_json(api_link)
    df=(pd.json_normalize(data,record_path=["content"]))
    df=df.drop(columns=['grounds','metadata.communities_twitter', 'metadata.club_highlights_internal_url', 'metadata.club_highlights_internal_description', 
                    'metadata.communities_facebook', 'metadata.communities_instagram', 'metadata.communities_URL', 'metadata.communities_youtube', 
                    'metadata.club_highlights_youtube_url', 'metadata.club_highlights_facebook_url'])
    return df

# Function to output DataFrame of Clubs that have participated each season
def clubs_by_year(years, club_info_DF):
    df = pd.DataFrame()
    club_names = club_info_DF["name"]
    club_id = club_info_DF["id"]
    df["club_name"] = club_names
    df["id"] = club_id
    d = []
    for idx, i in enumerate(years):
        season_id = season_code(i)
        data = team_api_json(api_links["teams"], compSeasons=season_id)
        teamlist = []
        partlist = []
        for j in data["content"]:
            teamlist.append(j["name"])
        d.append(teamlist)
        for k in club_names:
            if k in d[idx]:
                partlist.append(True)
            else:
                partlist.append(False)
        df[i] = partlist

    return df

# Function to output DataFrame of Club Stats
def club_stats(year,clubs_by_season):
    season_id=season_code(year)
    statlist=[]
    club_names=clubs_by_season["club_name"]
    club_id=clubs_by_season["id"]
    if season_id==None:
        teamids=clubs_by_season["id"].tolist()
        teamnames=clubs_by_season["club_name"].tolist()
        for idx,i in enumerate(teamids):
            api_link=api_links['club_stats']+str(int(i))
            data=(club_api_json(api_link))
            stats={"name":teamnames[idx],"id":i}
            for j in data["stats"]:
                stats[j["name"]]=j["value"]
            statlist.append(stats)
    else:
        temp=clubs_by_season.loc[clubs_by_season[year] == True]
        teamids=temp["id"].tolist()
        teamnames=temp["club_name"].tolist()
        for idx,i in enumerate(teamids):
            api_link=api_links['club_stats']+str(int(i))
            data=(club_api_json(api_link,compSeasons=season_id))
            stats={"name":teamnames[idx],"id":i}
            for j in data["stats"]:
                stats[j["name"]]=j["value"]
            statlist.append(stats)
    df=pd.json_normalize(statlist)
    df.fillna(0)
    return df

# Function to calculate number of entries per request page
def player_entries(
    api_link,
    pageSize=100,
    compSeasons=None,
    altIds="true",
    page=0,
    header_account="premierleague",
    header_origin="https://www.premierleague.com",
    dtype="player",
    id=-1,
    compSeasonId=None,
):
    r = requests.get(
        api_link,
        params={
            "pageSize": pageSize,
            "compSeasons": compSeasons,
            "altIds": altIds,
            "page": page,
            "type": dtype,
            "id": id,
            "compSeasonId": compSeasonId,
        },
        headers={"account": header_account, "origin": header_origin},
    )
    data = r.json()
    return data["pageInfo"]["numEntries"]

# Function to retrieve list of players for given season in JSON format
def player_api_json(
    api_link,
    pageSize=100,
    compSeasons=None,
    altIds="true",
    page=0,
    header_account="premierleague",
    header_origin="https://www.premierleague.com",
    dtype="player",
    id=-1,
    compSeasonId=None,
):
    r = requests.get(
        api_link,
        params={
            "pageSize": pageSize,
            "compSeasons": compSeasons,
            "altIds": altIds,
            "page": page,
            "type": dtype,
            "id": id,
            "compSeasonId": compSeasonId,
        },
        headers={"account": header_account, "origin": header_origin},
    )
    return r.json()

# Function to output DataFrame of Player Overview Stats
def player_overview(api_link, year):
    season_id=season_code(year)
    entries = player_entries(
        api_link=api_link, compSeasons=season_id, compSeasonId=season_id
    )
    page_size = 1000 #if function is crashing due to long execution time lower page size
    pages=int(entries/page_size)+1 
    temp = []
    for i in range(0, pages):
        data = player_api_json(
            api_links["players"],
            pageSize=page_size,
            page=i,
            compSeasons=season_id,
            compSeasonId=season_id,
        )
        temp.append(pd.json_normalize(data, record_path=["content"]))
    df = pd.concat(temp)
    return df

# Function to retrieve JSON of player stats
def player_stat_api(
    api_link,
    pageSize=100,
    compSeasons=None,
    altIds="true",
    page=0,
    header_account="premierleague",
    header_origin="https://www.premierleague.com",
):
    r = requests.get(
        api_link,
        params={
            "pageSize": pageSize,
            "compSeasons": compSeasons,
            "altIds": altIds,
            "page": page,
        },
        headers={"account": header_account, "origin": header_origin},
    )
    return r.json()

# Function to return JSON for an individual players stats
def player_stats(year, player_id):
    season_id = season_code(year)
    api_link=api_links["player_stats"]+str(int(player_id))
    data = player_stat_api(api_link, compSeasons=season_id)
    stats = {"name": data["entity"]["name"]["display"], "id": data["entity"]["id"]}
    for j in data["stats"]:
        stats[j["name"]] = j["value"]
    return stats

# Function to output DataFrame of Player Stats
def playerStatList(year,player_overview):
    player_id=player_overview["id"]
    statlist=[]
    for i in player_id:
        statlist.append(player_stats(year,i))
    df=pd.json_normalize(statlist)
    return df

def initialize():
    date = datetime.now().strftime("%Y_%m_%d")
    club_overview=club_basics(api_link=api_links["teams"])
    club_overview.to_csv("all_club_basic_info__"+date+".csv")
    clubs_by_season=clubs_by_year(years=seasons,club_info_DF= club_overview)
    clubs_by_season.to_csv("participant_table_"+date+".csv")
    club_stat_list=club_stats(year=None,clubs_by_season=clubs_by_season)
    club_stat_list.to_csv("club_stats_"+date+".csv")
    for i in seasons[0:14]:
        playov=player_overview(api_link=api_links["players"],year=i)
        playov.to_csv("player_overview_season_"+i+"_"+date+".csv")
        player_stat=playerStatList(year=i,player_overview=playov)
        player_stat.to_csv("player_stats_"+i+"_"+date+".csv")00


def main():
    """ Main entry point of the app """
    print("hello world")
    initialize()

if __name__ == "__main__":
    """ This is executed when run from the command line """
    main()
