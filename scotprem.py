import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
from mplsoccer.pitch import VerticalPitch


textc='#1d3557'
linec='#808080'
font='Arial'
bgcolor="#FAF9F6"
color1='#e63946'
color2='#a8dadc'
color3='#457b9d'
color4='#B2B3A9'
color5='#1d3557'
color6="#006daa"
pathcolor="#C4D5CB"
arrowedge=bgcolor

plt.rcParams["font.family"] = font
plt.rcParams['text.color'] = textc

# Data import & columns
df=pd.read_csv('/Users/jaymesmonte/Desktop/Analytics/ScotPremData/2122AllScotPrem_prog.csv')
df['team'] = np.where(df.teamId==df.hometeamid,df.hometeam,
                      df.awayteam)
df['fixture']= df['hometeam'] + " v " +df["awayteam"]

df = df.loc[(df['Throw In'] ==0)]
df = df.loc[(df['type_displayName'] =="Pass")]

conditions =[(df['endX']>=80) & (df['x']<=80)]
values =[1]
df['Final 3rd']=np.select(conditions, values)


df["KP"].replace({0: "No", 1: "Yes"}, inplace=True)
df["Corner"].replace({0: "No", 1: "Yes"}, inplace=True)
df["GK"].replace({0: "No", 1: "Yes"}, inplace=True)
df["Final 3rd"].replace({0: "No", 1: "Yes"}, inplace=True)
df["Cross"].replace({0: "No", 1: "Yes"}, inplace=True)
df["progressive"].replace({False: "No", True: "Yes"}, inplace=True)

values={"receiver":"Incomplete"}
df=df.fillna(value=values)


# Sidebar - title & filters
st.sidebar.markdown('### Data Filters')

teams = list(df['team'].drop_duplicates())
teams=sorted(teams)
#teams.append("All")
team_choice = st.sidebar.selectbox(
    "Select a team:", teams, index=0)
df=df.loc[(df['team'] == team_choice)]

fixtures = list(df['fixture'].drop_duplicates())
fixtures.insert(0,"All")
#fixtures.append("All")
fixture_choice = st.sidebar.selectbox(
    "Filter by Fixture:", fixtures,index=0)
if fixture_choice == "All":
    df=df
else:
    df=df.loc[(df['fixture'] == fixture_choice)]

players = list(df['name'].drop_duplicates())
players=sorted(players)
players.insert(0,"All")
#players.append("All")
player_choice = st.sidebar.selectbox(
    "Filter by Passer:", players,index=0)
if player_choice == "All":
    df=df
else:
    df=df.loc[(df['name'] == player_choice)]

recipient = list(df['receiver'].drop_duplicates())
recipient=sorted(recipient)
recipient.insert(0,"All")
#recipient.append("All")
receiver_choice = st.sidebar.selectbox(
    "Filter by Receiver:", recipient,index=0)
if receiver_choice == "All":
    df=df
else:
    df=df.loc[(df['receiver'] == receiver_choice)]
    
pass_type = list(df['progressive'].drop_duplicates())
pass_type.insert(0,"All")
pass_select = st.sidebar.radio("Progressive Pass?",pass_type,
                               index=0,help="A progressive pass is defined as a pass that moves the ball 25% of the remaining distance towards goal")
if pass_select == "All":
    df=df
else:
    df=df.loc[(df['progressive'] == pass_select)]
    
cross = list(df['Cross'].drop_duplicates())
cross.insert(0,"All")
cross_select = st.sidebar.radio("Cross?",cross,
                               index=0)
if cross_select == "All":
    df=df
else:
    df=df.loc[(df['Cross'] == cross_select)]
    
key_pass = list(df['KP'].drop_duplicates())
key_pass.insert(0,"All")
kpass_select = st.sidebar.radio("Key Pass?",key_pass,
                               index=0,help="A key pass is a pass that leads to a shot on goal")
if kpass_select == "All":
    df=df
else:
    df=df.loc[(df['KP'] == kpass_select)]
    
corner_list = list(df['Corner'].drop_duplicates())
corner_list.insert(0,"All")
corner_select = st.sidebar.radio("Corner?",corner_list,
                               index=0)
if corner_select == "All":
    df=df
else:
    df=df.loc[(df['Corner'] == corner_select)]
    
gk_list = list(df['GK'].drop_duplicates())
gk_list.insert(0,"All")
gk_select = st.sidebar.radio("Goal Kick?",gk_list,
                               index=0)
if gk_select == "All":
    df=df
else:
    df=df.loc[(df['GK'] == gk_select)]
    
final3_list = list(df['Final 3rd'].drop_duplicates())
final3_list.insert(0,"All")
final3_select = st.sidebar.radio("Pass into final 3rd?",final3_list,
                               index=0)
if final3_select == "All":
    df=df
else:
    df=df.loc[(df['Final 3rd'] == final3_select)]

#plot
pitch = VerticalPitch(half=False,pitch_type='statsbomb',
              pitch_color=bgcolor, line_color=linec,pad_top=10,line_zorder=2)

fig, ax = pitch.draw(figsize=(16, 11), constrained_layout=True, tight_layout=False)

df_S=df.loc[(df["outcomeType_displayName"] == "Successful")]
pitch1= pitch.arrows(df_S.x, df_S.y,
                     df_S.endX, df_S.endY,
                     color=color2,width=2, headwidth=7,alpha=1, headlength=6, ax=ax,zorder=5,lw=0.2,label="Completed passes")

df_U=df.loc[(df["outcomeType_displayName"] == "Unsuccessful")]
pitch1= pitch.arrows(df_U.x, df_U.y,
                     df_U.endX, df_U.endY,
                     color=color1,width=2, headwidth=7,alpha=0.5, headlength=6, ax=ax,zorder=5,lw=0.2,label="Incomplete passes")

ax.legend(facecolor=bgcolor, handlelength=4, edgecolor='None', fontsize=14, loc='lower left')


# Main
st.title(f"Scottish Premiership - 2021/22 Season")

# Main - dataframes
st.markdown('### Pass map')

st.pyplot(fig)
