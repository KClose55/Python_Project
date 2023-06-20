import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

###### Population datasets
dfp1 = pd.read_csv("us_city_populations2015.csv")
dfp2 = pd.read_csv("us2021census.csv", usecols=['City', 'State', 'Population'])

##### Cleanup for 2015 state name to state abbreviation
us_state_to_abbrev = {
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "Florida": "FL",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY",
    "District of Columbia": "DC",
    "American Samoa": "AS",
    "Guam": "GU",
    "Northern Mariana Islands": "MP",
    "Puerto Rico": "PR",
    "United States Minor Outlying Islands": "UM",
    "U.S. Virgin Islands": "VI",
}
# us_state_to_abbrev2 = {v: k for k,v in us_state_to_abbrev.items()}

# Transform state names to state abbreviations for dfp1 to align with other dataset
for index,row in dfp1.iterrows():
    dfp1.loc[index, 'state'] = us_state_to_abbrev[row['state']]

###### Joining the 2 population datasets
dfp = dfp2.merge(dfp1, how='left', left_on = ['City', 'State'], right_on = ['city', 'state'] )[['City', 'State', 'population_2015', 'Population']]

###### Fast food restaurants by city, longitude, latitude
dff1 = pd.read_csv("Datafiniti_Fast_Food_Restaurants.csv")
dff2 = pd.read_csv("Datafiniti_Fast_Food_Restaurants_Jun19.csv")
dff3 = pd.read_csv("FastFoodRestaurants.csv")

###### Union the fast food datasets together
dff = pd.concat([dff1,dff2,dff3])[['city', 'province', 'name', 'latitude', 'longitude']]

###### Join the fast food dataset with the population dataset
dfc = dff.merge(dfp, how='left', left_on = ['city', 'province'], right_on = ['City', 'State'])

###### Removing duplicates and rows with missing values (lost 7003 entries)
dfc
dfc = dfc.drop_duplicates().dropna()
dfc

###### Taking only the necessary columns
dfc = dfc[['City', 'State', 'name', 'latitude', 'longitude', 'population_2015', 'Population']].reset_index(drop=True)

###### Renaming columns to have consistent naming format
dfc
dfc = dfc.rename(columns={'name':'Restaurant Name', 'latitude':'Latitude', 'longitude':'Longitude', 'population_2015':'Population 2015', 'Population':'Population 2020'})
dfc

###### Order by 'State' then 'City' and resetting the index
dfc = dfc.sort_values(['State', 'City']).reset_index(drop=True)

###### Change populations to whole numbers
dfc
dfc = dfc.astype({'Population 2015':'int', 'Population 2020': 'int'})
dfc

###### Adding a column that shows the population growth percentage from 2015 to 2020
# dfc['Population Growth %'] = round((dfc['Population 2020'] - dfc['Population 2015'])/(dfc['Population 2015'])*100, 2)

###### Saving a csv to pull into bigquery
dfc.to_csv("FastFood_Population_City_round_after.csv", index=False)


###### Grouping by State and City
df_group = dfc.groupby(['State', 'City'])

###### Takes One value for each city
df_2015 = pd.DataFrame(df_group['Population 2015'].max()).reset_index()
df_2020 = pd.DataFrame(df_group['Population 2020'].max()).reset_index()
df_2015
df_2020

###### Group by State
df_2015_group = df_2015.groupby('State')['Population 2015'].sum()
df_2020_group = df_2020.groupby('State')['Population 2020'].sum()

df_2015_df = pd.DataFrame(df_2015_group)
df_2020_df = pd.DataFrame(df_2020_group)
df_2015_df
df_2020_df

df_state = pd.merge(df_2015_df, df_2020_df, on='State')
df_state


###### For US Regions
regions_df = pd.read_csv('regions.csv')
regions_df
regions_df.sort_values(by='State', inplace=True)
regions_df.set_index('State', inplace=True)
regions_df
df_state
df_regions = df_state.merge(regions_df, left_index=True, right_index=True)
df_regions = df_regions[['Region', 'Population 2015', 'Population 2020']]
df_regions.reset_index(inplace=True)
df_regions

regions_group = df_regions[['Region', 'Population 2015', 'Population 2020']].groupby('Region')
df_regions_group = pd.DataFrame(regions_group.sum())
df_regions_group
df_regions_group = df_regions_group.transform(lambda x: round(x/1000000, 6))
df_regions_group

###### Plot regions double bar
######
region_tuple = (df_regions_group.index)
pop_dict = {'Population 2015': (df_regions_group['Population 2015'].values), 'Population 2020': (df_regions_group['Population 2020'].values)}

x = np.arange(len(region_tuple))  # the label locations
y = np.arange(0,50)
width = .4  # the width of the bars
multiplier = 0

# Create plot and y-axis grid
fig, ax = plt.subplots(layout='tight')
ax.yaxis.grid(color='#E5E4E4')

# Add bars to plot
for attribute, measurement in pop_dict.items():
    offset = width * multiplier
    rects = ax.bar(x + offset, measurement, width, label=attribute)
    ax.bar_label(rects, padding=3, size=8, fontweight='bold')
    multiplier += 1

# Add some text for labels, title, custom x-axis tick labels, ustom y-axis tick labels etc.
ax.set_ylabel('Population (million)')
ax.set_title('Region Populations 2015 to 2020')
ax.set_xticks(x+(width/2), region_tuple)
ax.set_yticks(y, y)
ax.legend(loc='upper left', ncols=2)
ax.set_ylim(0, 50)

# Display the plot
plt.show()
###### End plot
######



###### Create double bar for pop growth by state
######
df_state_mil = df_state.copy()
df_state_mil['Population 2015'] = round(df_state_mil['Population 2015']/1000000, 3)
df_state_mil['Population 2020'] = round(df_state_mil['Population 2020']/1000000, 3)
df_state_mil

state_tuple = (df_state_mil.index)
pop_dict = {'Population 2015': (df_state_mil['Population 2015'].values), 'Population 2020': (df_state_mil['Population 2020'].values)}

x = np.arange(len(state_tuple))  # the label locations
y = np.arange(0,35)
width = 0.4  # the width of the bars
multiplier = 0

# Create plot and y-axis grid
fig, ax = plt.subplots(layout='constrained')
ax.yaxis.grid(color='#E5E4E4')

# Add bars to plot
second_bar = False
for attribute, measurement in pop_dict.items():
    offset = width * multiplier
    rects = ax.bar(x + offset, measurement, width, label=attribute)
    if second_bar == True:
        ax.bar_label(rects, padding=3, size=8, fontweight='bold')
    multiplier += 1
    second_bar = True

# Add some text for labels, title, custom x-axis tick labels, ustom y-axis tick labels etc.
ax.set_ylabel('Population (million)')
ax.set_title('State Populations (2020 Labeled)')
ax.set_xticks(x+(width/2), state_tuple)
ax.set_yticks(y, y)
ax.legend(loc='upper left', ncols=2)
ax.set_ylim(0, 36)

# Display the plot
plt.show()
###### End plot
######


###### Region population growth
df_regions_group['Population Growth'] = df_regions_group['Population 2020'] - df_regions_group['Population 2015']
df_regions_group['Population Growth %'] = round((df_regions_group['Population 2020'] - df_regions_group['Population 2015'])/df_regions_group['Population 2015']*100, 2)
df_regions_group.sort_values(by='Population Growth %', inplace=True, ascending=False)
df_regions_group


###### State population growth
df_state['Population Growth'] = df_state['Population 2020'] - df_state['Population 2015']
df_state['Population Growth %'] = round((df_state['Population 2020'] - df_state['Population 2015'])/df_state['Population 2015']*100, 2)
df_state.sort_values(by='Population Growth %', inplace=True, ascending=False)
df_state = df_state.merge(regions_df, left_index=True, right_index=True)
df_state = df_state[['Region', 'Population 2015', 'Population 2020', 'Population Growth', 'Population Growth %']]
df_state


###### Group by City
df_city = df_2015.merge(df_2020, how='left', left_on=['City', 'State'], right_on=['City', 'State'])
df_city['Population Growth'] = df_city['Population 2020'] - df_city['Population 2015']
df_city['Population Growth %'] = round((df_city['Population 2020']-df_city['Population 2015'])/df_city['Population 2015']*100, 2)
df_city.set_index('State', inplace=True)
df_city = df_city.merge(regions_df, left_index=True, right_index=True)
df_city.reset_index(inplace=True)
df_city
df_city = df_city[['State','City', 'Region', 'Population 2015', 'Population 2020', 'Population Growth', 'Population Growth %']]
df_city.sort_values(by='Population Growth %', ascending=False, inplace=True)
df_city.head(25)
df_city['Region'].head(25).value_counts()
df_city['State'].head(25).value_counts()
df_ma_nj = df_city[df_city['State'].isin(['MA', 'NJ'])]
df_ma_nj = df_ma_nj[['State', 'City', 'Population Growth', 'Population Growth %']]
df_ma_nj.head(10)
df_ma_nj[df_ma_nj['State'] == 'MA']['Population Growth'].head(5).sum()
df_ma_nj[df_ma_nj['State'] == 'NJ']['Population Growth'].head(5).sum()
