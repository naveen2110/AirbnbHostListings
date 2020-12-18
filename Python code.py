# -*- coding: utf-8 -*-
"""Code1_2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1lj52r8CDQjSgMvtIGZFHVmTBkM1ULJoG
"""

# Commented out IPython magic to ensure Python compatibility.
#Open project in Google colab
import pandas as pd
from pandas import DataFrame
from pandas.plotting import scatter_matrix
import matplotlib.pyplot as plt
from matplotlib import rcParams
import plotly.graph_objects as go
import plotly.express as px
from plotly.colors import n_colors
import numpy as np
import seaborn as sns
import pandas_profiling
# %matplotlib inline
from matplotlib import rc
import scipy.stats
import io
from sklearn.model_selection import train_test_split #for splitting the dataset.
from sklearn import preprocessing #used to scale variables
from sklearn.preprocessing import LabelEncoder # Use to assign integer values to all string values using Label Encoder for categorical variables.
from sklearn.linear_model import LinearRegression
from sklearn import metrics
from sklearn.metrics import r2_score
from sklearn.feature_selection import RFE
import statsmodels.api as sm #for making a linear regression model
from mlxtend.feature_selection import SequentialFeatureSelector as SFS #for step forward feature selection
from sklearn.tree import DecisionTreeRegressor #for making decion tree model
from sklearn import metrics #Import scikit-learn metrics module for accuracy calculation
from sklearn.tree import export_graphviz #use to visualize and classification tree - COMMENT OUT IF USING JUPYTER NOTEBOOK
from sklearn.ensemble import RandomForestRegressor

from google.colab import files 
  
  
uploaded = files.upload()

newyork = pd.read_csv(io.BytesIO(uploaded['AB_NYC_2019.csv']))  #reading the file

newyork.head(5)

newyork.shape  # Dead code

newyork.columns #Dead code

#Data Exploration
newyork.info()

newyork.describe() # only needed for numeric variables , modifying to newyork.describe(include = [np.number]).T

newyork.neighbourhood_group.unique()

newyork.room_type.unique()

newyork.neighbourhood.unique()

newyork.isnull().sum()

newyork.fillna({'name':"Null"}, inplace=True)

#percentage of empty values in last reviews
last_review = newyork.last_review
percent_last_review = (last_review.isnull().sum()/(len(newyork)*1.0))*100
percent_last_review

#percentage of empty values in reviews per month
reviews_per_month = newyork.reviews_per_month
percent_reviews_per_month = (reviews_per_month.isnull().sum()/(len(newyork)*1.0))*100
percent_reviews_per_month

# Data Cleaning Step 1
#Dropping unnecessary columns
newyork.drop(['last_review','reviews_per_month'], axis=1, inplace=True)

newyork.drop(['host_name'], axis=1, inplace=True)

newyork.isnull().sum()

#Data Cleaning Step 2
#Remove listings with price $0
newyork.drop(newyork.loc[newyork['price']==0].index, inplace=True)

newyork['price'].min()

boxplot = newyork.boxplot(column=['price'])

sns.distplot(newyork['price'])

#Data Cleaning Step 3
#Keep rows where Price is within 3 s.d 
z_score_price = np.abs(scipy.stats.zscore(newyork['price']))
price_outliers = newyork.iloc[np.where(z_score_price>3)]
price_outliers.sort_values(['price'])

newyork.drop(price_outliers.index, inplace=True)

newyork.shape

boxplot = newyork.boxplot(column=['price'])

sns.distplot(newyork['price'])

#Remove rows where availabilty_365=0 && reviews=0
newyork.drop(newyork.loc[(newyork['availability_365']==0) & (newyork['number_of_reviews']==0)].index, inplace=True)

newyork.shape

newyork.info()

sns.distplot(newyork['minimum_nights'])

boxplot = newyork.boxplot(column=['minimum_nights'])

newyork = newyork[newyork['minimum_nights'] < 999]

final_dataset=newyork
#Pre-Processing step
#Assign integer values to all string values using Label Encoder for categorical variables.
le = LabelEncoder()
final_dataset['neighbourhood_group'] = le.fit_transform(final_dataset['neighbourhood_group'])
final_dataset['neighbourhood'] = le.fit_transform(final_dataset['neighbourhood'])
final_dataset['room_type'] = le.fit_transform(final_dataset['room_type'])

final_dataset.head()

from google.colab import files
final_dataset.to_csv('filename.csv') 
files.download('filename.csv')

#Splitting the data set in to training and test data sets
feature_cols = ['neighbourhood_group','neighbourhood','room_type','minimum_nights','number_of_reviews',
                                                 'calculated_host_listings_count','availability_365']
x = final_dataset[feature_cols]
y = final_dataset.price # Target variable

# Split dataset into training set and test set
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=1) # 70% training and 30% test

#view number of training and testing data
print('Our training prediction set contains :',len(y_train) ,'rows')
print('Our training independent set contains :',len(x_train) ,'rows')
print('Our testing prediction set contains :',len(y_test) ,'rows')
print('Our testing independent set contains :',len(x_test) ,'rows')

reg_model_p = LinearRegression(normalize=False)
#fitting the training data to the model,
reg_model_p.fit(x_train, y_train)
#outputs the coefficients
print('Intercept :', reg_model_p.intercept_, '\n')
print(pd.DataFrame({'features':x_train.columns,'coefficients':reg_model_p.coef_}))

#prediction
lr_pred_p = reg_model_p.predict(x_test)
print('Mean Absolute Error:', metrics.mean_absolute_error(y_test, lr_pred_p))
print('Mean Squared Error:', metrics.mean_squared_error(y_test, lr_pred_p))
print('Root Mean Squared Error:', np.sqrt(metrics.mean_squared_error(y_test, lr_pred_p)))
score = r2_score(y_test, lr_pred_p)
print('Score:',score)

features = final_dataset[feature_cols]
target = final_dataset['price']

#Adding constant column of ones, mandatory for sm.OLS model
X_1 = sm.add_constant(features)
X_1
#Fitting sm.OLS model
model = sm.OLS(target,X_1).fit()
model.pvalues

#Backward Elimination
cols = list(features.columns)
pmax = 1
while (len(cols)>0):
    p= []
    X_1 = features[cols]
    X_1 = sm.add_constant(X_1)
    model = sm.OLS(target,X_1).fit()
    p = pd.Series(model.pvalues.values[1:],index = cols)      
    pmax = max(p)
    feature_with_p_max = p.idxmax()
    if(pmax>0.05):
        cols.remove(feature_with_p_max)
    else:
        break
selected_features_BE = cols
print(selected_features_BE)

#Recurvsive feature selection - no of features
nof_list=np.arange(1,7)            
high_score=0
#Variable to store the optimum features
nof=0           
score_list =[]
for n in range(len(nof_list)):
    X_train, X_test, y_train, y_test = train_test_split(features,target, test_size = 0.25, random_state = 0)
    model = LinearRegression()
    rfe = RFE(model,nof_list[n])
    X_train_rfe = rfe.fit_transform(X_train,y_train.values.ravel())
    X_test_rfe = rfe.transform(X_test)
    model.fit(X_train_rfe,y_train.values.ravel())
    score = model.score(X_test_rfe,y_test)
    score_list.append(score)
    if(score>high_score):
        high_score = score
        nof = nof_list[n]
print("Optimum number of features: %d" %nof)
print("Score with %d features: %f" % (nof, high_score))

cols = list(features.columns)
model = LinearRegression()
#Initializing RFE model
rfe = RFE(model, 12)             
#Transforming data using RFE
X_rfe = rfe.fit_transform(features,target.values.ravel())  
#Fitting the data to model
model.fit(X_rfe,target)              
temp = pd.Series(rfe.support_,index = cols)
selected_features_rfe = temp[temp==True].index
print(selected_features_rfe)

#Sequential backward selection(sbs)
sbs = SFS(LinearRegression(),
         k_features=7,
         forward=False,
         floating=False,
        scoring='r2',
         cv=0)
sbs.fit(x_train, y_train)
sbs.k_feature_names_

sfs1 = SFS(LinearRegression(),
         k_features=(1,7),
         forward=True,
         floating=False,
         cv=0)
sfs1.fit(x_train, y_train)
from mlxtend.plotting import plot_sequential_feature_selection as plot_sfs
import matplotlib.pyplot as plt
fig1 = plot_sfs(sfs1.get_metric_dict(), kind='std_dev')
plt.title('Sequential Forward Selection (w. StdErr)')
plt.grid()
plt.show()

dtree = DecisionTreeRegressor()
model = dtree.fit(x_train, y_train)  #train parameters: features and target
dtree_pred = dtree.predict(x_test)

#Visualize the minimal error classification tree
#export graphviz doesn't work in Jupyter Notebook - COMMENT OUT IF USING JUPYTER NOTEBOOK 
from sklearn.externals.six import StringIO  #use to visualize and classification tree 
from IPython.display import Image  #use to visualize and classification tree
import pydotplus #use to visualize and classification tree
dot_data = StringIO()
export_graphviz(dtree, out_file=dot_data,   
                filled=True, rounded=True,
                special_characters=True,feature_names = feature_cols,class_names=['0','1']) 
graph = pydotplus.graph_from_dot_data(dot_data.getvalue())  
graph.write_png('Air BNB prices.png')
Image(graph.create_png())
files.download('Air BNB prices.png') # the tree is too large and cannot be seen in one single screen. Need to prune the tree

print('Mean Absolute Error:', metrics.mean_absolute_error(y_test, dtree_pred))
print('Mean Squared Error:', metrics.mean_squared_error(y_test, dtree_pred))
print('Root Mean Squared Error:', np.sqrt(metrics.mean_squared_error(y_test, dtree_pred)))

max_depth = []
acc_mse = []
acc_mae= []
acc_friedman_mse = []
for i in range(1,30):
    dtree = DecisionTreeRegressor(criterion='mse', max_depth=i)
    dtree.fit(x_train, y_train)
    pred = dtree.predict(x_test)
    acc_mse.append(np.sqrt(metrics.mean_squared_error(y_test, pred)))
    dtree = DecisionTreeRegressor(criterion='mae', max_depth=i)
    dtree.fit(x_train, y_train)
    pred = dtree.predict(x_test)
    acc_mae.append(np.sqrt(metrics.mean_squared_error(y_test, pred)))
    ####
    dtree = DecisionTreeRegressor(criterion='friedman_mse', max_depth=i)
    dtree.fit(x_train, y_train)
    pred = dtree.predict(x_test)
    acc_friedman_mse.append(np.sqrt(metrics.mean_squared_error(y_test, pred)))
    ####
    max_depth.append(i)
    d = pd.DataFrame({'acc_mse':pd.Series(acc_mse), 
    'acc_mae':pd.Series(acc_mae),
    'acc_friedman_mse':pd.Series(acc_friedman_mse),
    'max_depth':pd.Series(max_depth)})
                                                
# visualizing changes in parameters
plt.plot('max_depth','acc_mse', data=d, label='mse')
plt.plot('max_depth','acc_mae', data=d, label='mae')
plt.plot('max_depth','acc_friedman_mse', data=d, label='friedman_mse')
plt.xlabel('max_depth')
plt.ylabel('RMSE')
plt.legend()

#refitting with max depth 8
dtree_m = DecisionTreeRegressor(criterion='mae',max_depth = 8)
model = dtree_m.fit(x_train, y_train)  #train parameters: features and target
pred = dtree_m.predict(x_test)
print('Mean Absolute Error:', metrics.mean_absolute_error(y_test, pred))
print('Mean Squared Error:', metrics.mean_squared_error(y_test, pred))
print('Root Mean Squared Error:', np.sqrt(metrics.mean_squared_error(y_test, pred)))

#Random Forest Regressor
rf = RandomForestRegressor(random_state=1).fit(x_train, y_train.values.ravel())
rf_pred = rf.predict(x_test)
print('Mean Absolute Error:', metrics.mean_absolute_error(y_test, rf_pred))
print('Mean Squared Error:', metrics.mean_squared_error(y_test, rf_pred))
print('Root Mean Squared Error:', np.sqrt(metrics.mean_squared_error(y_test, rf_pred)))

pip install xgboost

from sklearn.ensemble import RandomForestRegressor,  GradientBoostingRegressor

GBoost = GradientBoostingRegressor(n_estimators=3000, learning_rate=0.01)

GBoost.fit(x_train,y_train)

predict = GBoost.predict(x_test)

print('Mean Absolute Error:', metrics.mean_absolute_error(y_test, predict))
print('Mean Squared Error:', metrics.mean_squared_error(y_test, predict))
print('Root Mean Squared Error:', np.sqrt(metrics.mean_squared_error(y_test, predict)))

print('r2 score is:')
r2 = r2_score(y_test,predict)
r2*100

boxplot = newyork.boxplot(column=['minimum_nights'])

newyork.shape

newyork.describe()

sub_set = newyork[['price','availability_365','minimum_nights','number_of_reviews','calculated_host_listings_count']] 
sns.pairplot(sub_set)

corrMatrix = sub_set.corr()
sns.heatmap(corrMatrix, annot=True)
plt.show()

# determine popularity based on neighbourhood_group
sns.countplot(x='neighbourhood_group',data=newyork,palette='viridis')
plt.title('neightbourhood groups')

plt.figure(figsize=(10,6))
sns.scatterplot(newyork.longitude,newyork.latitude,hue=newyork.neighbourhood_group)
plt.ioff()

#Get a count by neighbourhood group
neighbourhood_group_count = newyork.groupby('neighbourhood_group').agg('count').reset_index()

pip install geopandas

import geopandas
#Here we are using geopandas to bring in a base layer of NYC boroughs
nyc = geopandas.read_file(geopandas.datasets.get_path('nybb'))
nyc.head(5)

#Rename the column to boroname, so that we can join the data to it on a common field
nyc.rename(columns={'BoroName':'neighbourhood_group'}, inplace=True)
bc_geo = nyc.merge(neighbourhood_group_count, on='neighbourhood_group')

bc_geo

# from geopandas import GeoDataFrame
# bc_geo = GeoDataFrame(bc_geo)

# type(bc_geo)

pip install geoplot

#Plot the count by borough into a map
fig,ax = plt.subplots(1,1, figsize=(10,10))
bc_geo.plot(column= 'id', cmap='plasma', alpha=.5, ax=ax, legend=True)
bc_geo.apply(lambda x: ax.annotate(s=x.neighbourhood_group, color='black', xy=x.geometry.centroid.coords[0],ha='center'), axis=1)
plt.title("Number of Airbnb Listings by NYC neighbourhood_group")
plt.axis('off')

# We can see that Manhattan and Broklyn are popular neighbourhood to rent a hourse

# determine popularity based on room type
sns.countplot(x='room_type',data=newyork,palette='viridis')
plt.title('Different room types')

neighbourhood_roomtype = newyork.groupby(by=['neighbourhood_group','room_type'],sort=False)['id'].agg([('count','count')]).reset_index().sort_values(by='count',ascending=False)
neighbourhood_roomtype
list = ['Manhattan', 'Brooklyn', 'Queens', 'Bronx', 'Staten Island']
neightbourhoodgroup_roomtype = neighbourhood_roomtype[neighbourhood_roomtype.neighbourhood_group.str.contains('|'.join(list))]
neightbourhoodgroup_roomtype 
pivot_df = neightbourhoodgroup_roomtype.pivot(index='neighbourhood_group', columns='room_type', values='count')
pivot_df
colors = ["#8B0A50", "#EE1289","#1E90FF"]

pivot_df.loc[:,['Entire home/apt','Private room', 'Shared room']].plot.barh(stacked=True, color=colors, figsize=(10,7))

#People generally prefer Entire home/apt and private room over shared room

plt.figure(figsize=(15,8))

# The plot
sns.boxplot(x = 'neighbourhood_group',
            y = 'price', data = newyork, palette = "viridis", saturation = 1, width = 0.9, fliersize=4, linewidth=2)

# Make pretty
plt.title('Price distribution of neighbourhood_group', fontsize = 20)
plt.xlabel('Neighbourhood_group', fontsize = 15)
plt.ylabel('Price', fontsize = 15)
plt.xticks(fontsize = 15)
plt.yticks(fontsize = 15)

"""From the above box plot we can say that Manhattan has the highest range of prices with average 174 dollars, after that Brooklyn comes with average 116 dollars. Queens and Staten Island have similar distribution and Bronx has lowest average that means it is the cheapest among all. Manhattan has highest value of Q1 that means it is the most expensive place.

For more granular view on popularity let's find out top neighbourhoods for given neighbourhood group.
"""

pip install plotly --upgrade

listing_per_neighborhoodgroup = newyork.groupby(['neighbourhood_group','neighbourhood'],sort=False)['id'].agg([('count','count')]).reset_index().sort_values(by=['neighbourhood_group','count'],ascending=[True,False])
listing_per_neighborhoodgroup
top_10 = listing_per_neighborhoodgroup.groupby(['neighbourhood_group']).apply(lambda x: x.nlargest(10,'count'))
top_10['newyork'] = 'newyork' # in order to have a single root node
top_10
fig = px.treemap(top_10, path=['newyork', 'neighbourhood_group', 'neighbourhood'], values='count', color='neighbourhood',color_continuous_scale='RdBu')
fig.show()

"""Though Manhattan is the most popular neighbuorhood group in Newyork Airbnb, two neighbourhoods Williamsburg and Bedford- Stuyvesant from Brooklyn are the most rented."""

sns.set_style('darkgrid')
plt.figure(figsize=(15,7))
sns.barplot(newyork.neighbourhood_group,newyork.price,palette='magma')
plt.xlabel('Neighbourhood_group',fontsize=20)
plt.ylabel('price',fontsize=15)

pip install geopandas

import geopandas
crs = {'init':'epsg:4326'}
geometry = geopandas.points_from_xy(newyork.longitude, newyork.latitude)
geo_data = geopandas.GeoDataFrame(newyork,crs=crs,geometry=geometry)
nyc = geopandas.read_file(geopandas.datasets.get_path('nybb'))
nyc = nyc.to_crs(epsg=4326)

fig,ax = plt.subplots(figsize=(12,12))
nyc.plot(ax=ax,alpha=0.4,edgecolor='black')
geo_data.plot(column='availability_365',ax=ax,legend=True,cmap='plasma',markersize=4)

plt.title("Availability_365")
plt.axis('off')

#let's what we can do with our given longtitude and latitude columns

#let's see how scatterplot will come out 
viz_4=newyork.plot(kind='scatter', x='longitude', y='latitude', label='number_of_reviews', c='price',
                  cmap=plt.get_cmap('jet'), colorbar=True, alpha=0.4, figsize=(10,8))
viz_4.legend()

plt.figure(figsize=(10,6))
sns.scatterplot(newyork.longitude,newyork.latitude,hue=newyork.number_of_reviews)
plt.ioff()

top_reviewed_listings=newyork.nlargest(20,'number_of_reviews')

sns.set_style('darkgrid')
plt.figure(figsize=(15,7))
sns.barplot(top_reviewed_listings.neighbourhood,top_reviewed_listings.number_of_reviews,palette='magma')
plt.xlabel('Neighbourhood',fontsize=20)
plt.ylabel('Reviews',fontsize=15)

pip install wordcloud

from wordcloud import WordCloud
plt.subplots(figsize=(20,15))
wordcloud = WordCloud(
                          background_color='white',
                          width=1920,
                          height=1080
                         ).generate(" ".join(newyork.name))
plt.imshow(wordcloud)
plt.axis('off')
plt.savefig('neighbourhood.png')
plt.show()

from wordcloud import WordCloud

# Visualizing the most used words in the names of the most expensive Airbnbs in Brooklyn
airbnb_brooklyn = newyork[newyork['neighbourhood_group'] == 'Brooklyn']
word_cloud = WordCloud(width = 1000,
                       height = 800,
                       colormap = 'crest', 
                       margin = 0,
                       max_words = 200,  
                       max_font_size = 120, min_font_size = 15,  
                       background_color = "white").generate(" ".join(airbnb_brooklyn['name']))

plt.figure(figsize = (20, 15))
plt.imshow(word_cloud, interpolation = "gaussian")
plt.axis("off")
plt.show()

from wordcloud import WordCloud

# Visualizing the most used words in the names of the most expensive Airbnbs in Brooklyn
airbnb_Manhattan = newyork[newyork['neighbourhood_group'] == 'Manhattan']
word_cloud = WordCloud(width = 1000,
                       height = 800,
                       colormap = 'magma', 
                       margin = 0,
                       max_words = 200,  
                       max_font_size = 120, min_font_size = 15,  
                       background_color = "white").generate(" ".join(airbnb_Manhattan['name']))

plt.figure(figsize = (20, 15))
plt.imshow(word_cloud, interpolation = "gaussian")
plt.axis("off")
plt.show()

from wordcloud import WordCloud

# Visualizing the most used words in the names of the most expensive Airbnbs in Brooklyn
airbnb_bronx = newyork[newyork['neighbourhood_group'] == 'Bronx']
word_cloud = WordCloud(width = 1000,
                       height = 800,
                       colormap = 'GnBu', 
                       margin = 0,
                       max_words = 200,  
                       max_font_size = 120, min_font_size = 15,  
                       background_color = "white").generate(" ".join(airbnb_bronx['name']))

plt.figure(figsize = (20, 15))
plt.imshow(word_cloud, interpolation = "gaussian")
plt.axis("off")
plt.show()

from wordcloud import WordCloud

# Visualizing the most used words in the names of the most expensive Airbnbs in Brooklyn
airbnb_Staten_Island = newyork[newyork['neighbourhood_group'] == 'Staten Island']
word_cloud = WordCloud(width = 1000,
                       height = 800,
                       colormap = 'viridis', 
                       margin = 0,
                       max_words = 200,  
                       max_font_size = 120, min_font_size = 15,  
                       background_color = "white").generate(" ".join(airbnb_Staten_Island['name']))

plt.figure(figsize = (20, 15))
plt.imshow(word_cloud, interpolation = "gaussian")
plt.axis("off")
plt.show()

from wordcloud import WordCloud

# Visualizing the most used words in the names of the most expensive Airbnbs in Brooklyn
airbnb_queens = newyork[newyork['neighbourhood_group'] == 'Queens']
word_cloud = WordCloud(width = 1000,
                       height = 800,
                       colormap = 'twilight_shifted', 
                       margin = 0,
                       max_words = 200,  
                       max_font_size = 120, min_font_size = 15,  
                       background_color = "white").generate(" ".join(airbnb_queens['name']))

plt.figure(figsize = (20, 15))
plt.imshow(word_cloud, interpolation = "gaussian")
plt.axis("off")
plt.show()

most_reviews = newyork.sort_values(by = 'number_of_reviews', ascending = False)
from wordcloud import WordCloud
plt.subplots(figsize=(25,15))
wordcloud = WordCloud(
                          background_color='white',
                          width=1920,
                          height=1080
                         ).generate(" ".join(most_reviews['neighbourhood']))
plt.imshow(wordcloud)
plt.axis('off')
plt.savefig('neighbourhood.png')
plt.show()