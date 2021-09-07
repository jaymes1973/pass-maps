
import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from mplsoccer.pitch import VerticalPitch
from scipy.ndimage import gaussian_filter
from highlight_text import ax_text, fig_text


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

cmaplist = [bgcolor,color2,color1]
cmap = LinearSegmentedColormap.from_list("", cmaplist)

plt.rcParams["font.family"] = font
plt.rcParams['text.color'] = textc

st.set_page_config(layout='wide')

# Data import & columns
file1='2122AllScotPrem_prog.csv'
file2='06-September-2021 16_14_04 xg_events.csv'

df1=pd.read_csv(file2)
df1['event_x'] = df1['event_x']*1.149
df1['event_y'] = 80-df1['event_y']*1.176

st.title(f"Scottish Premiership - 2021/22 Season")

@st.cache(allow_output_mutation=True)
def get_data(file):
    df=pd.read_csv(file)
    return (df)

df=get_data(file1)



df1 = df1.loc[(df1['event_isOwnGoal'] == False)]
df1 = df1.loc[(df1['event_situation'] != "Penalty")]


df['team'] = np.where(df.teamId==df.hometeamid,df.hometeam,
                      df.awayteam)
date_new =[]
for date in df['match_date']:
    date_new.append(date.split("T")[0])
    
df['Date']= date_new
df['Date']= pd.to_datetime(df.Date).dt.strftime('%Y-%m-%d')
df['fixture']= df['Date'] + " - " + df['hometeam'] + " v " +df["awayteam"]


df = df.loc[(df['Throw In'] ==0)]
df = df.loc[(df['type_displayName'] =="Pass")]

conditions =[(df['endX']>=80) & (df['x']<=80)]
values =[1]
df['Final 3rd']=np.select(conditions, values)

values={"receiver":"Incomplete"}
df=df.fillna(value=values)

# Sidebar - title & filters
st.sidebar.markdown('### Pass Map Filters')

teams = list(df['team'].drop_duplicates())
teams=sorted(teams)
#teams.append("All")
team_choice = st.sidebar.selectbox(
    "Select a team:", teams, index=3)
df=df.loc[(df['team'] == team_choice)]
df = df.sort_values(by=['Date'])

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

pass_types=["All","Progressive Passes","Crosses","Key Passes","Corners","Goal Kicks",
            "Passes into final 3rd"]
pass_type = st.sidebar.selectbox(
    "Choose pass type:", pass_types,index=0)

if pass_type == "All":
    df=df
elif pass_type == "Progressive Passes":
    df=df.loc[(df['progressive'] == True) & (df['Corner'] == 0)]
elif pass_type == "Crosses":
    df=df.loc[(df['Cross'] == 1) & (df['Corner'] == 0)]
elif pass_type == "Key Passes":
    df=df.loc[(df['KP'] == 1)]
elif pass_type == "Corners":
    df=df.loc[(df['Corner'] == 1)]
elif pass_type == "Goal Kicks":
    df=df.loc[(df['GK'] == 1)]
else:
    df=df.loc[(df['Final 3rd'] == 1)]
    

#plot
pitch = VerticalPitch(half=False,pitch_type='statsbomb',
              pitch_color=bgcolor, line_color=linec,pad_top=10,line_zorder=2)


fig, axs = pitch.grid(ncols=3, axis=False,figheight=12)

df_S=df.loc[(df["outcomeType_displayName"] == "Successful")]
pitch1= pitch.arrows(df_S.x, df_S.y,
                     df_S.endX, df_S.endY,
                     color=color2,width=2, headwidth=7,alpha=1, headlength=6, ax=axs['pitch'][0],zorder=5,lw=0.2,label="Completed passes")

df_U=df.loc[(df["outcomeType_displayName"] == "Unsuccessful")]
pitch1= pitch.arrows(df_U.x, df_U.y,
                     df_U.endX, df_U.endY,
                     color=color1,width=2, headwidth=7,alpha=0.5, headlength=6, ax=axs['pitch'][0],zorder=5,lw=0.2,label="Incomplete passes")

axs['pitch'][0].legend(facecolor=bgcolor, handlelength=4, edgecolor='None', fontsize=14, loc='lower left')
axs['pitch'][0].text(40, 125, "Filtered passes", color=textc,
                  va='center', ha='center', font=font, fontsize=20)

bin_statistic = pitch.bin_statistic(df.x, df.y, statistic='count', bins=(50, 35))
bin_statistic['statistic'] = gaussian_filter(bin_statistic['statistic'], 1)
pcm = pitch.heatmap(bin_statistic, ax=axs['pitch'][1], cmap=cmap, edgecolors=bgcolor)
axs['pitch'][1].text(40, 125, "Heatmap - Start point of passes", color=textc,
                  va='center', ha='center', font=font, fontsize=20)

bin_statistic = pitch.bin_statistic(df.endX, df.endY, statistic='count', bins=(50, 35))
bin_statistic['statistic'] = gaussian_filter(bin_statistic['statistic'], 1)
pcm = pitch.heatmap(bin_statistic, ax=axs['pitch'][2], cmap=cmap, edgecolors=bgcolor)
axs['pitch'][2].text(40, 125, "Heatmap - End point of passes", color=textc,
                  va='center', ha='center', font=font, fontsize=20)


st.sidebar.markdown('### Shot Map Filters')


df1 = df1.loc[(df1['event_teamName'] == team_choice)]

players2 = list(df1['event_playerName'].drop_duplicates())
players2=sorted(players2)
players2.append("All Players")
player = st.sidebar.selectbox(
    "Select a player:", players2, index=len(players2)-1)

if player != "All Players":
    df1 = df1.loc[(df1['event_playerName'] == player)]
else:
    df1=df1

stypes = list(df1['event_situation'].drop_duplicates())
stypes=sorted(stypes)
stypes.append("All Chances")
stype = st.sidebar.selectbox(
    "Select chance type:", stypes, index=len(stypes)-1)

if stype != "All Chances":
    df1 = df1.loc[(df1['event_situation'] == stype)]
else:
    df1=df1




goals=df1.loc[(df1['event_eventType'] == 'Goal')]
shots=df1.loc[(df1['event_eventType'] == 'AttemptSaved')]
misses=df1.loc[(df1['event_eventType'] == 'Miss')]

total_xg=df1["event_expectedGoals"].sum()
total_xgOT=df1["event_expectedGoalsOnTarget"].sum()
total_xgOT=round(total_xgOT,2)
total_shots=len(df1)
total_goals=len(goals)
on_target=len(goals)+len(shots)

xg_per_shot=round(total_xg/total_shots,3)
on_target_per=round(on_target/total_shots*100,2)


pitchG = VerticalPitch(half=True,pitch_type='statsbomb',
              pitch_color=bgcolor, line_color=linec,line_zorder=1,pad_top=0)

fig1, ax1 = pitchG.draw(figsize=(12, 10))

# plot goal shots with a color
sc1 = pitchG.scatter(goals.event_x, goals.event_y,
                    # size varies between 100 and 1900 (points squared)
                    s=goals.event_expectedGoals*1000,
                    edgecolors=color1,  # give the markers a charcoal border
                    c=bgcolor,  # color for scatter in hex format
                    # for other markers types see: https://matplotlib.org/api/markers_api.html
                    marker='football',
                    ax=ax1,label="Goal",zorder=4)
# plot non-goal shots with hatch
sc2 = pitchG.scatter(shots.event_x, shots.event_y,
                    # size varies between 100 and 1900 (points squared)
                    s=shots.event_expectedGoals*1000,
                    edgecolors=color1,  # give the markers a charcoal border
                    c=color3,  # no facecolor for the markers
                    hatch='///',  # the all important hatch (triple diagonal lines)
                    # for other markers types see: https://matplotlib.org/api/markers_api.html
                    marker='o',
                    ax=ax1,label="Shot on Target",zorder=3)


sc3 = pitchG.scatter(misses.event_x, misses.event_y,
                    # size varies between 100 and 1900 (points squared)
                    s=misses.event_expectedGoals*1000,
                    edgecolors=color5,  # give the markers a charcoal border
                    c=color2,  # color for scatter in hex format
                    # for other markers types see: https://matplotlib.org/api/markers_api.html
                    marker='s',
                    ax=ax1,label="Missed Target",zorder=2)

ax1.legend(facecolor=bgcolor, handlelength=4, edgecolor='None', fontsize=14, loc='lower left')    

fig1.patch.set_facecolor(bgcolor)

fig_text(s=f"{team_choice} | {player} | {stype}", ha='center',
        x=0.5, y =1.13, fontsize=22,fontfamily=font,color=textc)

fig_text(s=f"Total Shots: {total_shots} | Goals: {total_goals} | On Target: {on_target}", ha='center',
        x=0.5, y =1.06, fontsize=18,fontfamily=font,color=textc)

fig_text(s=f"xG per Shot: {xg_per_shot} | xG on Target: {total_xgOT} | On Target: {on_target_per} %", ha='center',
        x=0.5, y =1.0, fontsize=18,fontfamily=font,color=textc)


#fig_text(s=f"Penalties are excluded.",#ha='center',
  #      x=0.15, y =0.76, fontsize=16,fontfamily=font,color=textc)
#
st.pyplot(fig)

st.pyplot(fig1)

