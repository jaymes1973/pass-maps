file1="/Users/jaymesmonte/Desktop/Analytics/Data/WorldCup22/WCQs_prog.csv"
image1="/Users/jaymesmonte/Desktop/Analytics/Dufc_Analytics/scotland.png"

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

st.set_page_config(layout='wide')

st.sidebar.image(image1, use_column_width=False)

@st.cache(allow_output_mutation=True)
def get_data(file):
    df=pd.read_csv(file)
    date_new =[]
    for date in df['match_date']:
        date_new.append(date.split("T")[0])
    
    df['Date']= date_new
    df['Date']= pd.to_datetime(df.Date).dt.strftime('%Y-%m-%d')
    df['fixture']= df['hometeam'] + " v " +df["awayteam"]+ " - " + df['Date'] 
    
    df = df.sort_values(by=['Date'])
    
    df['team'] = np.where(df.teamId==df.hometeamid,df.hometeam,
                      df.awayteam)

    return (df)

df=get_data(file1)

conditions = [(df["team"]=="Denmark"),(df["team"]=="Scotland"),(df["team"]=="Israel"),
    (df["team"]=="Austria"),(df["team"]=="Faroe Islands"),(df["team"]=="Moldova")]

# create a list of the values we want to assign for each condition
values = ['#d1050c','#004b84','#0038B8','#ed2939','#ED2939','#FFD100']

# create a new column and use np.select to assign values to it using our lists as arguments
df['color'] = np.select(conditions, values)

team="Scotland"
fixtures = list(df['fixture'].drop_duplicates())
game = st.sidebar.selectbox(
    "Select a fixture:", fixtures,index=0)
df=df.loc[(df['fixture'] == game)]


opposition=list(df['team'].drop_duplicates())
opposition.remove(team)
opposition=''.join(opposition)
oppo_color=df.loc[df['team'] == opposition, 'color'].reset_index(drop=True)
oppo_color=oppo_color.iloc[0]

team_color=df.loc[df['team'] == team, 'color'].reset_index(drop=True)
team_color=team_color.iloc[0]
#find time of the team's first substitution and filter the df to only passes before that
Subs = df.loc[(df['type_displayName']=="SubstitutionOff")]
SubTimes = Subs["time_seconds"]
SubOne = SubTimes.min()
SubTwo = SubTimes.nlargest(2).iloc[-1]
SubLast = SubTimes.max()

ft_min= df["expandedMinute"].max()#.tolist()
sub1_min=int(round(SubOne/60,0)) 

min_low=0
min_high=90
min_low, min_high = st.sidebar.slider(
    'Filter by minutes:',0,ft_min,(0,sub1_min))

time_low=min_low*60
time_high=min_high*60

#SELECTED TEAM
OneTeam = df.loc[(df['team']==team)]

#filter for only passes and then successful passes
Passes = OneTeam.loc[(OneTeam['type_displayName']=="Pass")]
Completions = Passes.loc[(Passes['outcomeType_displayName']=="Successful")]

Completions = Completions.loc[(Completions['time_seconds']>time_low)&(Completions['time_seconds']<time_high)]
Passes = Passes.loc[(Passes['time_seconds']>time_low)&(Passes['time_seconds']<time_high)]
#Positions = OneTeam.loc[(OneTeam['time_seconds']>time_low)&(OneTeam['time_seconds']<time_high)]

#Find Average Locations 
average_locs_and_count = Passes.groupby(['name','shirtNo']).agg({'x': ['mean'], 'y': ['mean','count']})
average_locs_and_count.columns = ['x', 'y', 'count']
average_locs_and_count =average_locs_and_count.reset_index(level='shirtNo')

passes_between = Completions.groupby(['name', 'receiver']).size()
passes_between=passes_between.to_frame()
passes_between=passes_between.reset_index()
passes_between.rename(columns={passes_between.columns[2]: "pass_count" }, inplace = True)
passes_between=passes_between.sort_values(by='pass_count', ascending=False).reset_index(drop=True)


passes_between = passes_between.merge(average_locs_and_count, left_on='name', right_index=True)
passes_between = passes_between.merge(average_locs_and_count, left_on='receiver', right_index=True,
                                      suffixes=['', '_end'])


#set minimum threshold for pass arrows to be plotted. So this will only plot combos which occured at least 3 times.
passes_between = passes_between.loc[(passes_between['pass_count']>1)]

MAX_LINE_WIDTH = 10
MAX_MARKER_SIZE = 2000
passes_between['width'] = (passes_between.pass_count / passes_between.pass_count.max() *
                           MAX_LINE_WIDTH)
average_locs_and_count['marker_size'] = (average_locs_and_count['count']
                                         / average_locs_and_count['count'].max() * MAX_MARKER_SIZE)

passes_between["name"]=passes_between["name"] + " (" + passes_between["shirtNo"].astype(str).replace('\.0', '', regex=True) + ")"


pivot=passes_between.iloc[:,:3]
pivotTable=pd.pivot_table(pivot,index=["name"],columns=["receiver"],values=["pass_count"])
pivotTable=pivotTable.droplevel(0, axis=1)
pivotTable=pivotTable.fillna(0).reset_index()


#OPPOSITION TEAM
#filter for only actions by the team you want
OneTeamO = df.loc[(df['team']==opposition)]


#filter for only passes and then successful passes
PassesO = OneTeamO.loc[(OneTeamO['type_displayName']=="Pass")]
CompletionsO = PassesO.loc[(PassesO['outcomeType_displayName']=="Successful")]

CompletionsO = CompletionsO.loc[(CompletionsO['time_seconds']>time_low)&(CompletionsO['time_seconds']<time_high)]
PassesO = PassesO.loc[(PassesO['time_seconds']>time_low)&(PassesO['time_seconds']<time_high)]

#Find Average Locations 
average_locs_and_countO = PassesO.groupby(['name','shirtNo']).agg({'x': ['mean'], 'y': ['mean','count']})
average_locs_and_countO.columns = ['x', 'y', 'count']
average_locs_and_countO =average_locs_and_countO.reset_index(level='shirtNo')

passes_betweenO = CompletionsO.groupby(['name', 'receiver']).size()
passes_betweenO=passes_betweenO.to_frame()
passes_betweenO=passes_betweenO.reset_index()
passes_betweenO.rename(columns={passes_betweenO.columns[2]: "pass_count" }, inplace = True)
passes_betweenO=passes_betweenO.sort_values(by='pass_count', ascending=False).reset_index(drop=True)


passes_betweenO = passes_betweenO.merge(average_locs_and_countO, left_on='name', right_index=True)
passes_betweenO = passes_betweenO.merge(average_locs_and_countO, left_on='receiver', right_index=True,
                                      suffixes=['', '_end'])


#set minimum threshold for pass arrows to be plotted. So this will only plot combos which occured at least 3 times.
passes_betweenO = passes_betweenO.loc[(passes_betweenO['pass_count']>1)]

MAX_LINE_WIDTH = 10
MAX_MARKER_SIZE = 2000
passes_betweenO['width'] = (passes_betweenO.pass_count / passes_betweenO.pass_count.max() *
                           MAX_LINE_WIDTH)
average_locs_and_countO['marker_size'] = (average_locs_and_countO['count']
                                         / average_locs_and_countO['count'].max() * MAX_MARKER_SIZE)

passes_betweenO["name"]=passes_betweenO["name"] + " (" + passes_betweenO["shirtNo"].astype(str).replace('\.0', '', regex=True) + ")"


pivotO=passes_betweenO.iloc[:,:3]
pivotTableO=pd.pivot_table(pivotO,index=["name"],columns=["receiver"],values=["pass_count"])
pivotTableO=pivotTableO.droplevel(0, axis=1)
pivotTableO=pivotTableO.fillna(0).reset_index()


fig = plt.figure(figsize=(20,20),constrained_layout=True)
gs = fig.add_gridspec(nrows=2,ncols=2)
fig.patch.set_facecolor(bgcolor)

pitch = VerticalPitch(half=False,pitch_type='statsbomb',
              pitch_color=bgcolor, line_color=linec,line_zorder=1,pad_top=5)

ax1 = fig.add_subplot(gs[0,0])
ax1.set_title(label=f"{team}",x=0.5,y=1.0,size=22,color=textc,ha='center')
pitch.draw(ax=ax1)

pass_lines = pitch.lines(passes_between.x, passes_between.y,
                         passes_between.x_end, passes_between.y_end, lw=passes_between.width,
                         color=linec, zorder=2, ax=ax1)
pass_nodes = pitch.scatter(average_locs_and_count.x, average_locs_and_count.y,
                           s=average_locs_and_count.marker_size,
                           color=team_color, edgecolors='black', linewidth=1, alpha=1, ax=ax1,zorder=3)


for index, row in average_locs_and_count.iterrows():
    pitch.annotate(row.shirtNo.astype(int), xy=(row.x, row.y), c='white', va='center',
                   ha='center', size=12, weight='bold', ax=ax1)
    
ax2 = fig.add_subplot(gs[1,0])
ax2.set_title(label=f"{opposition}",x=0.5,y=1.0,size=22,color=textc,ha='center')
pitch.draw(ax=ax2)

pass_lines = pitch.lines(passes_betweenO.x, passes_betweenO.y,
                         passes_betweenO.x_end, passes_betweenO.y_end, lw=passes_betweenO.width,
                         color=linec, zorder=2, ax=ax2)
pass_nodes = pitch.scatter(average_locs_and_countO.x, average_locs_and_countO.y,
                           s=average_locs_and_countO.marker_size,
                           color=oppo_color, edgecolors='black', linewidth=1, alpha=1, ax=ax2,zorder=3)


for index, row in average_locs_and_countO.iterrows():
    pitch.annotate(row.shirtNo.astype(int), xy=(row.x, row.y), c='white', va='center',
                   ha='center', size=12, weight='bold', ax=ax2)
    

min_low=str(min_low)
min_high=str(min_high)

ax3 = fig.add_subplot(gs[0,1])

data1=pivotTable.iloc[:, 1:].values
vals = np.around(data1, 2)

normal = (data1 / (data1.min( keepdims=True) + data1.max( keepdims=True)))
colours = plt.cm.Reds(normal)
#data1=data1.to_numpy()

table=ax3.table(rowLabels=pivotTable.name,cellText=data1.astype(int), colLabels=pivotTable.columns[1:], loc='center'
                   ,cellLoc="center",cellColours=colours)#,colColours=['white']*12,rowColours=['white']*12)

table.scale(1.5,1.5)
table.auto_set_font_size(False)
table.set_fontsize(10)

for cell in table._cells:
    if cell[0] ==0:
        table._cells[cell].get_text().set_rotation(90)
        table._cells[cell].set_height(0.2)


ax3.axis('off')

ax4 = fig.add_subplot(gs[1,1])

data2=pivotTableO.iloc[:, 1:].values
vals = np.around(data2, 2)

normal2 = (data2 / (data2.min( keepdims=True) + data2.max( keepdims=True)))
colours2 = plt.cm.Reds(normal2)
#data1=data1.to_numpy()

table=ax4.table(rowLabels=pivotTableO.name,cellText=data2.astype(int), colLabels=pivotTableO.columns[1:], loc='center'
                   ,cellLoc="center",cellColours=colours2)#,colColours=['white']*12,rowColours=['white']*12)

table.scale(1.5,1.5)
table.auto_set_font_size(False)
table.set_fontsize(10)

for cell in table._cells:
    if cell[0] ==0:
        table._cells[cell].get_text().set_rotation(90)
        table._cells[cell].set_height(0.2)


ax4.axis('off')


fig_text(s=f"Passing Networks | Average Position\n\n{game}",# ha='center',
        x=0.05, y =1.13, fontsize=30,fontfamily=font,color=textc)

fig_text(s=f"{min_low}min to {min_high}min (Default is set to time of first substitution in game.)",
        x=0.05, y =1.06, fontsize=22,fontfamily=font,color=textc)


st.pyplot(fig)
