import os
from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
from openpyxl.workbook import Workbook

#______________________________________________________________________________________________________________________
#_____START OF DATA EXTRACTION_____#

def get_football_season_links(country):
    countries = ['england', 'germany', 'italy', 'spain', 'france', 'netherlands', 'belgium', 'portugal', 'turkey']
    if country in countries:
        webpage_res = requests.get(f'https://www.football-data.co.uk/{country}m.php')
        webpage = webpage_res.content
        soup = BeautifulSoup(webpage, 'html.parser')
        data_table = soup.find_all('tr')
        data_table_links = soup.find_all('a', )
        for link in data_table_links:
            if 'csv' in str(link):
                print(link)
    else:
        country = input(f"Please select a country from the following list: {countries}")




# Get football results into a data frame
def football_results_df(country, year):
    country.lower()
    countries = {'germany': '/D1', 'spain': '/SP1', 'england': '/E0', 'italy': '/I1'}
    years = ['2021', '1920', '1819', '1718']
    if country in countries and year in years:
        return pd.read_csv(
            f'https://www.football-data.co.uk/mmz4281/{year}{countries.get(country)}.csv'
        )

    else:
        country = input(f"Please select a country from the following list: {countries.keys()}")

#_____END OF DATA EXTRACTION_____#
#_____________________________________________________________________________________________________________________

#_____START OF DATA MANIPULATION_____#
#_____________________________________________________________________________________________________________________

###START OF NOTES TO DICTIONARY###
# Helper functions - Start
def read_file(filename):
    path = os.path.join(os.path.dirname(__file__), filename)
    return open(path, 'r')


def make_dict(lst):
    my_dict = {}
    for text in lst:
        keys = text.split(":")[0]
        values = text.split(":")[1]
        my_dict[keys] = values
    return my_dict

def match_results(result):
    if result in ['A', 'H']:
        return "Away Team Win"
    elif result == 'D':
        return "Draw"
# Helper functions - End

results_data = [w.replace(' = ', ':').replace('\n', '') for w in
                read_file('notes.txt').readlines()[6:16]]

match_statistics = [w.replace(' = ', ':').replace('\n', '') for w in
                    read_file('notes.txt').readlines()[19:41]]

betting_odds = [w.replace(' = ', ':').replace('\n', '') for w in
                read_file('notes.txt').readlines()[49:101]]

goals_betting_odds = [w.replace(' = ', ':').replace('\n', '') for w in
                      read_file('notes.txt').readlines()[106:121]]

result_df = pd.DataFrame.from_dict(make_dict(results_data), orient='index', columns=["Descriptions"])
match_statistics_df = pd.DataFrame.from_dict(make_dict(match_statistics), orient='index', columns=["Descriptions"])
betting_odds_df = pd.DataFrame.from_dict(make_dict(betting_odds), orient='index', columns=["Descriptions"])
goals_betting_odds_df = pd.DataFrame.from_dict(make_dict(goals_betting_odds), orient='index', columns=["Descriptions"])

glossary = pd.concat([result_df, match_statistics_df, betting_odds_df, goals_betting_odds_df]).reset_index()
glossary.rename(columns={'index':'Code'}, inplace=True)

###END OF NOTES TO DICTIONARY###

###RAW DATA###
bundesliga = football_results_df('germany', '2021')
la_liga = football_results_df('spain', '2021')
serie_a = football_results_df('italy', '2021')
premier_league = football_results_df('england', '2021')

main_table = pd.concat([bundesliga, la_liga, serie_a, premier_league])
main_table['id'] = main_table['Div'] + "_" + main_table['HomeTeam'] + "_" + main_table['AwayTeam'] + "_" + main_table['Date']
main_table['total_goal_difference'] = main_table['FTHG'] - main_table['FTAG']
main_table['is_draw'] = main_table['FTR'].apply(lambda x: 1 if x == 'D' else 0)
columns = [x for x in main_table.columns][:23]
granular_table = main_table.loc[:, columns]
granular_table = granular_table.replace({'D1': 'Bundesliga', 'E0': 'Premier League', "I1": 'Serie A', 'SP1': 'La Liga'})
granular_table['FTR'] = granular_table['FTR'].apply(lambda x: match_results(x))
###END RAW DATA###

###START OF GRANULAR TABLE FOR DASH###
columns = [column for column in main_table.columns][:23]
granular_table = main_table.loc[:, columns]
###END OF GRANULAR TABLE FOR DASH###

###DRAWS BY LEAGUE AGGREGATE###
draws_by_league = main_table.groupby("Div", as_index=False)['is_draw'].sum() \
    .rename(columns={'Div': 'European_leagues', 'is_draw': 'total_draws'}) \
    .replace({'D1': 'Bundesliga (DE)', 'E0': 'Premier League (EN)', "I1": 'Serie A (IT)', 'SP1': 'La Liga (ES)'})
###END DRAWS BY LEAGUE AGGREGATE###

###DRAWS BY HOME TEAM AGGREGATE###
draws_by_home_team = main_table.groupby(["HomeTeam"], as_index=False)[['is_draw', "FTHG", 'FTAG']].sum()\
    .rename(columns={'HomeTeam': 'teams', 'is_draw': 'total_draws', 'FTHG': 'goals_scored', 'FTAG': 'goals_conceded'})\
    .sort_values(by='total_draws', ascending=False)
draws_by_home_team['goal_difference'] = draws_by_home_team['goals_scored'] - draws_by_home_team['goals_conceded']
draws_by_home_team['draws_index'] = draws_by_home_team['total_draws'] / draws_by_home_team['total_draws'].max()
draws_by_home_team['goal_difference_index'] = 1-((1/draws_by_home_team['goal_difference'].abs().max())*draws_by_home_team['goal_difference'].abs())
draws_by_home_team['overall_index'] = (draws_by_home_team['draws_index'] + draws_by_home_team['goal_difference_index'])/2
draws_by_home_team['overall_rank'] = draws_by_home_team['overall_index'].rank(method='dense', ascending=False)
###END DRAWS BY HOME TEAM AGGREGATE###

###DRAWS BY AWAY TEAM AGGREGATE###
draws_by_away_team = main_table.groupby("AwayTeam", as_index=False)[['is_draw', "FTHG", 'FTAG']].sum() \
    .rename(columns={'AwayTeam': 'teams', 'is_draw': 'total_draws', 'FTAG': 'goals_scored', 'FTHG': 'goals_conceded'}) \
    .sort_values(by='total_draws', ascending=False)
draws_by_away_team['goal_difference'] = draws_by_away_team['goals_scored'] - draws_by_away_team['goals_conceded']
draws_by_away_team['draws_index'] = draws_by_away_team['total_draws'] / draws_by_away_team['total_draws'].max()
draws_by_away_team['goal_difference_index'] = 1-((1/draws_by_away_team['goal_difference'].abs().max())*draws_by_away_team['goal_difference'].abs())
draws_by_away_team['overall_index'] = (draws_by_away_team['draws_index'] + draws_by_away_team['goal_difference_index'])/2
draws_by_away_team['overall_rank'] = draws_by_away_team['overall_index'].rank(method='dense', ascending=False)
###END DRAWS BY AWAY TEAM AGGREGATE###

###ALL DATA BY TEAM###
total_draws_by_team = draws_by_home_team.merge(draws_by_away_team, on="teams", suffixes=("_home", "_away"))\
     .rename(columns={'total_draws_home': 'home_draws', 'total_draws_away': 'away_draws'})
total_draws_by_team['total_draws'] = total_draws_by_team['home_draws'] + total_draws_by_team['away_draws']
total_draws_by_team['total_goals_scored'] = total_draws_by_team['goals_scored_home'] + total_draws_by_team['goals_scored_away']
total_draws_by_team['total_goals_conceded'] = total_draws_by_team['goals_conceded_home'] + total_draws_by_team['goals_conceded_away']
total_draws_by_team['goal_difference'] = total_draws_by_team['total_goals_scored'] - total_draws_by_team['total_goals_conceded']
total_draws_by_team['draws_index'] = total_draws_by_team['total_draws']  / total_draws_by_team['total_draws'].max()
total_draws_by_team['goal_difference_index'] = 1-((1/total_draws_by_team['goal_difference'].abs().max())*total_draws_by_team['goal_difference'].abs())
total_draws_by_team['overall_index'] = (total_draws_by_team['draws_index'] + total_draws_by_team['goal_difference_index'])/2
total_draws_by_team['overall_rank'] = total_draws_by_team['overall_index'].rank(method='dense', ascending=False).astype('int64')
###END OF ALL DATA BY TEAM###

###DATA FOR SCORECARDS###
scorecards_data = pd.pivot_table(total_draws_by_team, values=['total_draws', 'away_draws', 'home_draws',
                                                              'goal_difference', 'total_goals_scored', 'total_goals_conceded',
                                                              'overall_rank','overall_rank_home', 'overall_rank_away'],
                                 index=['teams'], aggfunc=np.sum).sort_values(by='overall_rank', ascending=True)[:15]
###END OF DATA FOR SCORECARDS###
scorecards_data_test = scorecards_data.reset_index()
test_data = scorecards_data[:1]

#_____END OF DATA MANIPULATION_____#
#______________________________________________________________________________________________________________________

#_____START DATA OUTPUT TO EXCEL_____#
#______________________________________________________________________________________________________________________
glossary = pd.DataFrame(glossary)
raw_data = pd.DataFrame(main_table)
granular_table = pd.DataFrame(granular_table)
draws_by_league = pd.DataFrame(draws_by_league)
draws_by_home_team = pd.DataFrame(draws_by_home_team)
draws_by_away_team = pd.DataFrame(draws_by_away_team)
total_draws_by_team = pd.DataFrame(total_draws_by_team)
scorecards_data = pd.DataFrame(scorecards_data)
scorecards_data = scorecards_data.reindex(columns=['total_draws', 'away_draws', 'home_draws',
                                                   'goal_difference', 'total_goals_scored', 'total_goals_conceded',
                                                   'overall_rank','overall_rank_home', 'overall_rank_away', 'team'])
test_data = pd.DataFrame(test_data)


path = 'footie.xlsx'
with pd.ExcelWriter(path, engine='openpyxl') as writer:
    glossary.to_excel(writer, 'glossary')
    raw_data.to_excel(writer, 'raw_data')
    granular_table.to_excel(writer, 'granular_data')
    draws_by_league.to_excel(writer, 'draws_by_league')
    draws_by_home_team.to_excel(writer, 'draws_by_home_team')
    draws_by_away_team.to_excel(writer, 'draws_by_away_team')
    total_draws_by_team.to_excel(writer, 'total_draws_by_team')
    scorecards_data.to_excel(writer,'scorecards_data')
    test_data.to_excel(writer, 'test_data')

#_____END DATA OUTPUT TO EXCEL_____#
#______________________________________________________________________________________________________________________