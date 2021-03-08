import streamlit as st
import pandas as pd
import numpy as np
import altair as alt


st.set_page_config(
    page_title="Football odds data | Check how much you could've earned if you placed bets on football?",
    page_icon=":soccer",
    #layout="wide",
    #initial_sidebar_state="expanded",
    )

#We'll hide menu burgerand footer, and add our content in the bottom
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            footer {visibility: hidden;}
            footer:after {
            	content:'Made with love and Streamlit'; 
            	visibility: visible;
            	display: block;
            	position: relative;
            	#background-color: red;
            	padding: 5px;
            	top: 2px;
            }
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

st.title("How much you could've earned if you placed bets on your favourite football team?")

add_selectbox_country = st.selectbox(
    "What football league are interested in?",
    ('England', 'Spain', 'Italy', 'Germany', 'France', 'Netherlands', 'Portugal')
)

if add_selectbox_country == 'England':
    championship = 'E0'
elif add_selectbox_country == 'Spain':
    championship = 'SP1'
elif add_selectbox_country == 'Italy':
    championship = 'I1'
elif add_selectbox_country == 'Germany':
    championship = 'D1'
elif add_selectbox_country == 'France':
    championship = 'F1'
elif add_selectbox_country == 'Netherlands':
    championship = 'N1'
elif add_selectbox_country == 'Portugal':
    championship = 'P1'
else:
    championship = 'E0'

DATE_COLUMN = 'Date'
DATA_URL = ('https://www.football-data.co.uk/'
            'mmz4281/2021/'+championship+'.csv')
#https://www.football-data.co.uk/mmz4281/2021/E0.csv
#https://www.football-data.co.uk/mmz4281/2021/I1.csv

#@st.cache
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows, parse_dates=['Date'], dayfirst=True)
    lowercase = lambda x: str(x).lower()
    data.insert(5, 'Result', data['FTHG'].astype(str) + ':' + data['FTAG'].astype(str))
    
    #INSERT HOW MUCH MONEY YOU COULD'VE EARNED IF YOU BET ON WIN/D/L

    data.insert(6, 'BetAmnt', -100) #every bey is 100 USD
    data.insert(7, 'TotalGoals', data['FTHG'] + data['FTAG']) #total goals in a game    
    #data = data.drop(columns=['Div', 'Time', 'FTHG', 'FTAG', 'FTR', 'HTHG', 'HTAG', 'HTR'])
    #data.rename(lowercase, axis='columns', inplace=True)
    #data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN])
    #data = data[['Date', 'HomeTeam', 'AwayTeam', 'Result', 'FTHG', 'FTAG', 'FTR', 'AvgH', 'AvgD', 'AvgA',
                # 'Avg>2.5', 'Avg<2.5']]
    return data

data_load_state = st.text('Loading data...')
data = load_data(10000)
data_load_state.text("")


#https://stackoverflow.com/questions/33769860/pandas-apply-but-only-for-rows-where-a-condition-is-met

#Calculating what we could've won if all our bets were right
mask_home = (data['FTR'] == 'H')
z_valid = data[mask_home]
data['HomeBetWin'] = 0
data.loc[mask_home, 'HomeBetWin'] = z_valid['AvgH'].astype(float) * 100

mask_draw = (data['FTR'] == 'D')
z_valid = data[mask_draw]
data['DrawBetWin'] = 0
data.loc[mask_draw, 'DrawBetWin'] = z_valid['AvgD'].astype(float) * 100

mask_away = (data['FTR'] == 'A')
z_valid = data[mask_away]
data['AwayBetWin'] = 0
data.loc[mask_away, 'AwayBetWin'] = z_valid['AvgA'].astype(float) * 100

mask_more25 = (data['TotalGoals'].astype(int) > 2.5)
z_valid = data[mask_more25]
data['BetGoals>25'] = 0
data.loc[mask_more25, 'BetGoals>25'] = z_valid['Avg>2.5'].astype(float) * 100

mask_less25 = (data['TotalGoals'].astype(int) < 2.5)
z_valid = data[mask_less25]
data['BetGoals<25'] = 0
data.loc[mask_less25, 'BetGoals<25'] = z_valid['Avg>2.5'].astype(float) * 100


#Calculating what we could've won if we placed bets only on HomeWin and Draw
data.insert(9, 'BetWinHome', data['BetAmnt'] + data['HomeBetWin'])
data.insert(9, 'BetDraw', data['BetAmnt'] + data['DrawBetWin'])
data.insert(9, 'BetWinAway', data['BetAmnt'] + data['AwayBetWin'])
data.insert(9, 'BetMore25', data['BetAmnt'] + data['BetGoals>25'])
data.insert(9, 'BetLess25', data['BetAmnt'] + data['BetGoals<25'])

#data to work with
data = data[['Date', 'HomeTeam', 'AwayTeam', 'Result', 'BetAmnt', 'BetWinHome', 'BetDraw', 'BetWinAway', 'HomeBetWin', 'DrawBetWin', 'AwayBetWin',
             'TotalGoals', 'BetGoals>25', 'BetGoals<25', 'BetMore25', 'BetLess25', 'FTHG', 'FTAG', 'FTR', 'AvgH', 'AvgD', 'AvgA', 'Avg>2.5', 'Avg<2.5']]
#data to show
data_show = data[['Date', 'HomeTeam', 'AwayTeam', 'Result', 'AvgH', 'AvgD', 'AvgA', 'Avg>2.5', 'Avg<2.5']]

teams = []
for i in data['HomeTeam']:
    if i not in(teams):
        teams.append(i)
teams.append('--- all teams ---')
teams.sort()

add_selectbox = st.selectbox(
    "What team are you interested in?",
    (teams)
)

if add_selectbox != '--- all teams ---':
    #this df will be used for charting later
    filtered_data_home = data[data['HomeTeam'] == add_selectbox]
    filtered_data_away = data[data['AwayTeam'] == add_selectbox]
    filtered_data_final = filtered_data_home.append(filtered_data_away)
    #this df is for displaying raw data (limited)
    data_show_selected_team_home = data[data['HomeTeam'] == add_selectbox]
    data_show_selected_team_away = data[data['AwayTeam'] == add_selectbox]
    data_show_selected_team = data_show_selected_team_home.append(data_show_selected_team_away)
    data_show_selected_team = data_show_selected_team[['Date', 'HomeTeam', 'AwayTeam', 'Result', 'AvgH', 'AvgD', 'AvgA', 'Avg>2.5', 'Avg<2.5']]
    if st.checkbox("Show raw data on games and odds in table format"): 
        st.write(data_show_selected_team.sort_values(by=['Date']))
        st.text('You may sort table results by clicking the relevant column name')
        st.text('*AvgH = Market average home win odds')
        st.text('*AvgD = Market average draw win odds')
        st.text('*AvgA = Market average away win odds')
        st.text('*Avg>2.5 = Market average over 2.5 goals')
        st.text('*Avg<2.5 = Market average under 2.5 goals')
else:
    st.write(data_show)
    st.text('You may sort table results by clicking the relevant column name')
    st.text('*AvgH = Market average home win odds')
    st.text('*AvgD = Market average draw win odds')
    st.text('*AvgA = Market average away win odds')
    st.text('*Avg>2.5 = Market average over 2.5 goals')
    st.text('*Avg<2.5 = Market average under 2.5 goals')



if add_selectbox != '--- all teams ---':
    selected_team_home = filtered_data_final[filtered_data_final['HomeTeam'] == add_selectbox]
    selected_team_draw = filtered_data_final
    selected_team_away = filtered_data_final[filtered_data_final['AwayTeam'] == add_selectbox]


    #--------------------------------------------------------------------------

    with st.beta_expander("Home wins, draws and away wins bets"):
        
    
        chart_home_selected = alt.Chart(selected_team_home).mark_bar(size=10).encode(
            x='Date',
            y='BetWinHome',
            color=alt.condition(
                alt.datum.BetWinHome > 0,
                alt.value("green"),  # The positive color
                alt.value("red")  # The negative color
            #color='animal',
            # legend=alt.Legend(title='Animals by year')
        ))
        st.subheader('What if you bet $100 on home team wins in all ' + add_selectbox + ' home games?')
        st.text('You would got ' + str(selected_team_home['BetWinHome'].sum().astype(int)) + ' USD') 
        st.altair_chart(chart_home_selected, use_container_width=True)
     
    
        # Basic Altair line chart where it picks automatically the colors for the lines
        chart_draw_selected = alt.Chart(selected_team_draw).mark_bar(size=10).encode(
            x='Date',
            y='BetDraw',
            color=alt.condition(
                alt.datum.BetDraw > 0,
                alt.value("green"),  # The positive color
                alt.value("red")  # The negative color
            #color='animal',
            # legend=alt.Legend(title='Animals by year')
        ))
        st.subheader('What if you bet $100 on draws in all ' + add_selectbox + ' games?')
        st.text('You would got ' + str(selected_team_draw['BetDraw'].sum().astype(int)) + ' USD')   
        st.altair_chart(chart_draw_selected, use_container_width=True)
    
    
        chart_away_selected = alt.Chart(selected_team_away).mark_bar(size=10).encode(
            x='Date',
            y='BetWinAway',
            color=alt.condition(
                alt.datum.BetWinAway > 0,
                alt.value("green"),  # The positive color
                alt.value("red")  # The negative color
            #color='animal',
            # legend=alt.Legend(title='Animals by year')
        ))
        st.subheader('What if you bet $100 on away team wins in all ' + add_selectbox + ' away games?')
        st.text('You would got ' + str(selected_team_away['BetWinAway'].sum().astype(int)) + ' USD') 
        st.altair_chart(chart_away_selected, use_container_width=True)


    #--------------------------------------------------------------------------

    with st.beta_expander("Total Goals Bets with 2.5 goals threshold"):
        
        #st.header('Total Goals')
    
        chart_home_selected = alt.Chart(selected_team_home).mark_bar(size=10).encode(
            x='Date',
            y='BetLess25',
            color=alt.condition(
                alt.datum.BetLess25 > 0,
                alt.value("green"),  # The positive color
                alt.value("red")  # The negative color
            #color='animal',
            # legend=alt.Legend(title='Animals by year')
        ))
        st.subheader('What if you bet $100 on total goals of < 2.5 in all ' + add_selectbox + ' home games?')
        st.text('You would got ' + str(selected_team_home['BetLess25'].sum().astype(int)) + ' USD') 
        st.altair_chart(chart_home_selected, use_container_width=True)
    
    
        chart_home_selected = alt.Chart(selected_team_home).mark_bar(size=10).encode(
            x='Date',
            y='BetMore25',
            color=alt.condition(
                alt.datum.BetMore25 > 0,
                alt.value("green"),  # The positive color
                alt.value("red")  # The negative color
            #color='animal',
            # legend=alt.Legend(title='Animals by year')
        ))
        st.subheader('What if you bet $100 on total goals of > 2.5 in all ' + add_selectbox + ' home games?')
        st.text('You would got ' + str(selected_team_home['BetMore25'].sum().astype(int)) + ' USD') 
        st.altair_chart(chart_home_selected, use_container_width=True)
    
    
        chart_away_selected = alt.Chart(selected_team_away).mark_bar(size=10).encode(
            x='Date',
            y='BetLess25',
            color=alt.condition(
                alt.datum.BetLess25 > 0,
                alt.value("green"),  # The positive color
                alt.value("red")  # The negative color
            #color='animal',
            # legend=alt.Legend(title='Animals by year')
        ))
        st.subheader('What if you bet $100 on total goals of < 2.5 in all ' + add_selectbox + ' away games?')
        st.text('You would got ' + str(selected_team_away['BetLess25'].sum().astype(int)) + ' USD') 
        st.altair_chart(chart_away_selected, use_container_width=True)
        
    
        chart_away_selected = alt.Chart(selected_team_away).mark_bar(size=10).encode(
            x='Date',
            y='BetMore25',
            color=alt.condition(
                alt.datum.BetMore25 > 0,
                alt.value("green"),  # The positive color
                alt.value("red")  # The negative color
            #color='animal',
            # legend=alt.Legend(title='Animals by year')
        ))
        st.subheader('What if you bet $100 on total goals of > 2.5 in all ' + add_selectbox + ' away games?')
        st.text('You would got ' + str(selected_team_away['BetMore25'].sum().astype(int)) + ' USD') 
        st.altair_chart(chart_away_selected, use_container_width=True)

    #--------------------------------------------------------------------------

    with st.beta_expander("See total goals statistics"):
    
        #Goals at home games
        chart_home_selected = alt.Chart(selected_team_home).mark_bar(size=10).encode(
            x='Date',
            y='TotalGoals')
        rule = alt.Chart(selected_team_home).mark_rule(color='red').encode(y='mean(TotalGoals)')
        st.subheader('Total goals in ' + add_selectbox + ' home games')
        st.text('Red line shows the average (' + str(selected_team_home['TotalGoals'].mean()) + ' goals per game)') 
        st.altair_chart(chart_home_selected + rule, use_container_width=True)
    
        #Goals at away games
        chart_away_selected = alt.Chart(selected_team_away).mark_bar(size=10).encode(
            x='Date',
            y='TotalGoals')
        rule = alt.Chart(selected_team_away).mark_rule(color='red').encode(y='mean(TotalGoals)')
        st.subheader('Total goals in ' + add_selectbox + ' away games')
        st.text('Red line shows the average (' + str(selected_team_away['TotalGoals'].mean()) + ' goals per game)') 
        st.altair_chart(chart_away_selected + rule, use_container_width=True)
 
    #--------------------------------------------------------------------------

    with st.beta_expander("Would you like to get football games predictions from smartscout?"):
    
        st.title('Football games predictions from smartscout')
        
        DATE_COLUMN = 'date/time'
        DATA_URL = ('https://smarterscout.com/matchguidance/'
                    'smarterscout_match_guidance_probabilities.csv')
        
        #https://smarterscout.com/matchguidance/smarterscout_match_guidance_probabilities.csv
        
        #@st.cache
        def load_data(nrows):
            data = pd.read_csv(DATA_URL, nrows=nrows)
            lowercase = lambda x: str(x).lower()
            #data.rename(lowercase, axis='columns', inplace=True)
            #data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN])
            return data
        
        data_load_state = st.text('Loading data...')
        data = load_data(10000)
        data_load_state.text("")
        
        #hour_to_filter = st.checkbox('ENG1')
        
        
        st.subheader('Choose the league:')
        
        option = st.selectbox(
             '', ('ENG1', 'SPA1', 'ITA1', 'GER1', 'FRA1', 'POR1', 'NED1', 'SCO1', 'RUS1'),
             index=0)
        filtered_data = data[data['League'] == option]
        st.write(filtered_data)
        
        st.write('Please read [the Disclaimer](https://smarterscout.com/matchguidance/Information_and_Disclaimer_PLEASE_READ.txt)')