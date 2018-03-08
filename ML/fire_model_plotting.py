<<<<<<< HEAD

from __future__ import division
import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from dirs import MyDir
from sklearn import linear_model
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
from sklearn.preprocessing import scale
from sklearn.model_selection import train_test_split
from mpl_toolkits.basemap import Basemap

#from scipy.stats import gaussian_kde
#import statsmodels.api as sm
from sklearn.neighbors import KNeighborsRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPRegressor
#from scipy import signal
                                                                                                                                      #thresh_range=[90]


#======================================================
# PREPARE TRAINING SET
#features: enso, iod, landcover1, landcover2, MTDCA, mySCA2, nl, precip, temp, vod
#response: fire

os.chdir('C:/Users/kkrao/Dropbox/fire_proj_data')
np.random.seed(2)
#list variables
data_types=['et', 'peat', 'pet', 'precip', 'q', 'temp', 'sm','vod','fire']
#data_types.remove('vod') ## just tried to remove vod so that we have data til 2016. but did not help
data_types_names=['Actual Evapotranspiration','Peat Lands','Potential Evapotranspiration',\
              'Precipitation','Specific Humidity','Temperature','Soil Moisture','Vegetation Optical Depth','Fire']
data_type_dict=dict(zip(data_types,data_types_names))
data_type_dates=[source+'dates' for source in data_types]
### which dataset extends only till 2013?

for source in data_type_dates:
    dates = np.load(source+'.npy')
    maxdate = pd.to_datetime(max(dates))
#    print('%s max date %s'%(source, maxdate))

#initialize general start and end date time
start_date, end_date = pd.to_datetime('1900-01-01'), pd.to_datetime('2100-01-01')

#search through dates and find start and end dates that are at intersection of all data types
for source in data_type_dates:
    dates = np.load(source+'.npy')
    mindate = pd.to_datetime(min(dates))
    maxdate = pd.to_datetime(max(dates))
    if mindate > start_date:
        start_date = mindate
    if maxdate < end_date:
        end_date = maxdate
#    print('%s min date is: %s'%(source, mindate))
#create lat lon vector vector
lat = np.load('fire_lat.npy')
lon = np.load('fire_lon.npy')
lon,lat=np.meshgrid(lon,lat)
latcorners=[331, 387]
loncorners=[1097, 1200]
lon,lat=lon[latcorners[0]:latcorners[1],loncorners[0]:loncorners[1]],\
       lat[latcorners[0]:latcorners[1],loncorners[0]:loncorners[1]]

start_date=pd.to_datetime('2015-01-01')     
#initialize dataframe by adding lat, lon, and months
df = pd.DataFrame(lat.flatten(), columns=['lat'])
df['lon'] = lon.flatten()
num_months = (end_date.year - start_date.year)*12 + (end_date.month)
df = df.append([df]*(num_months-1), ignore_index=True)



#add all features into m x n matrix
for source in data_types:

    #load one dataset
    data = np.load(source+'.npy')
    dates = np.load(source+'dates.npy')
    
    #keep only those dates between the start and end date
    data = data[(pd.to_datetime(dates)>=start_date) & \
                (pd.to_datetime(dates)<=end_date),:,:]
    
    #add to dataframe
    data_df = pd.DataFrame(data.flatten(),columns=[source])
    df = pd.concat([df,data_df],axis=1)

#remove examples where any data is missing
df.dropna(inplace=True)
#df.fillna(method='bfill',inplace=True)
#df.fillna(method='ffill',inplace=True)
df.fire/=67500
#for classification
#of nonzero values, 25 percntile = 29.6, 50th=66, 75th = 171.4
    
### subset rows you dont want-===================================================
#df=df.loc[df.fire>0,:]
df=df.loc[df.peat==1,:]


###===========================================================================
thresh1=0
#thresh_range= np.arange(1e-3,1e-1,1e-3)
#thresh_range=[0.0960]
thresh_range=[1e-2]
for thresh2 in thresh_range:
    dfsub=df.copy()
    dfsub.loc[df.fire<=thresh1,'fire']='no fire'
    dfsub.loc[(df.fire>thresh1) & (df.fire<=thresh2),'fire']='small fire'
    dfsub.loc[df.fire>thresh2,'fire']='large fire'
    #split into features and output
    y = dfsub['fire']
    dfsub.drop(['lat','lon','peat','fire'], axis=1,inplace=True)
#    dfsub.apply(lambda x: (x - np.min(x)) / (np.max(x) - np.min(x)))
    dfsub=(dfsub-dfsub.min())/(dfsub.max()-dfsub.min())
    dfsub['fire']=y
    X = dfsub.drop(['fire'],axis=1)

    #split into training and test
    
    X_train, X_test, y_train, y_test = train_test_split(X,y)
    
    # Fitting a logistic regression model
    log_model = LogisticRegression(penalty='l2',C=1)
    log_model.fit(X_train,y_train)
    
    # Checking the model's accuracy
    y_pred=log_model.predict(X_test)
    score = accuracy_score(y_test,y_pred)
    print('For thresh = %0.4f, accuracy = %0.2f'%(thresh2, score))



zoom=6
matplotlib.rcParams.update({'font.size': 28})
#for plotting
#dfsub['fire'].plot(kind='hist')



##PLOT info on data
#info = df.drop(['lat','lon'], axis=1)
#ax=info.hist(figsize=(10,8),xlabelsize=12,ylabelsize=12)
#ax = info.boxplot(return_type='axes')
#ax.set_ylim((-2,4))
cmap = sns.color_palette('inferno', 3)
# classification plots
sns.set_style('ticks')
dftest=pd.concat([X_test,y_test],axis=1)
g=sns.pairplot(dftest,hue='fire',size=zoom/4,plot_kws={'s':3,'alpha':1,\
         'edgecolor':'none'},palette=cmap)
### trying to plot decision boundary
#xx, yy = np.mgrid[0:1:.01, 0:1:.01]
#grid = np.c_[xx.ravel(), yy.ravel()]
#probs = log_model.predict_proba(grid)[:, 1].reshape(xx.shape)
#axs=g.axes
#handles= g._legend_data.values()
#labels=g._legend_data.keys()
#for i in range(len(handles)):
#    handles[i]._sizes = 10
##g.fig.legend(handles,labels)
#plt.show()
## confusion matrix


labels=['no fire', 'small fire','large fire']
fig, ax= plt.subplots(figsize=(1*zoom,1*zoom))
cbaxes = fig.add_axes([1, 0.2, 0.15, 0.772])
sns.heatmap(confusion_matrix(y_test,y_pred,labels=labels\
         ), \
        annot=True, fmt='d',square=True,ax=ax,cbar_ax=cbaxes)
ax.set_xticklabels(labels,rotation=45)
ax.set_yticklabels(labels[::-1],rotation=0)
    
### plotting maps of fire and predictions
month=1
def classify(data,thresh1=0,thresh2=1e-2):
    df=pd.DataFrame(data)
    df[df<=thresh1]=0
    df[(df>thresh1) & (df<=thresh2)]=1
    df[df>thresh2]=2
    return df

def color(df,cmap=cmap):
    df.replace('large fire',cmap[0])

def plot_timeseries_maps(proj='cyl'):
    data=np.load('fire.npy')[-24+month:-23+month,:,:][0]
    df=classify(data)
    mask=np.load('peat.npy')[0,:,:]==1
#    df=df[mask]
#    sns.set(font_scale=1.2)
    fig, axs = plt.subplots(nrows=2,ncols=1   ,\
                            sharey='row',figsize=(8,8))
    marker_size=3
    plt.subplots_adjust(wspace=0.04,hspace=0.04,top=0.83)
    ax=axs[0]
    m = Basemap(projection=proj,lat_0=45,lon_0=0,resolution='l',\
            llcrnrlat=lat[-1,0],urcrnrlat=lat[0,-1],\
            llcrnrlon=lon[-1,0],urcrnrlon=lon[0,-1],\
            ax=ax)
    m.drawcoastlines()
    m.scatter(lon, lat,s=marker_size,c=df,\
                        marker='s',cmap='inferno')
    plt.show()
        #---------------------------------------------------------------
#        data_plot=pred_mort[pred_mort.index.year==year]
#        ax=axs[1,year-year_range[0]]
##        ax.annotate(str(year), xy=(0.96, 0.95), xycoords='axes fraction',\
##                ha='right',va='top')
#        m = Basemap(projection=proj,lat_0=45,lon_0=0,resolution='l',\
#                llcrnrlat=latcorners[0],urcrnrlat=latcorners[1],\
#                llcrnrlon=loncorners[0],urcrnrlon=loncorners[1],\
#                ax=ax)
#        m.readshapefile(Dir_CA+'/CA','CA',drawbounds=True, color='black')
#        plot_data=m.scatter(lats, lons,s=marker_size,c=data_plot,cmap=cmap2\
#                           ,marker='s',vmin=var2_range[0],vmax=var2_range[1],\
#                           norm=mpl.colors.PowerNorm(gamma=1./2.)\
#                                                  )
##        m.drawparallels(parallels,labels=[1,0,0,0], dashes=[1.5,900])
##        m.drawmeridians(meridians,labels=[0,0,0,1], dashes=[1.5,900])
#        #-------------------------------------------------------------------
#    cb0=fig.colorbar(plot_mort,ax=axs.ravel().tolist(), fraction=0.03,\
#                     aspect=30,pad=0.02)
##    cb0.ax.tick_params(labelsize=fs) 
#    tick_locator = ticker.MaxNLocator(nbins=ticks)
#    cb0.locator = tick_locator
#    cb0.update_ticks()
#    cb0.set_ticks(np.linspace(var1_range[0],var1_range[1] ,ticks))
#    axs[0,0].set_ylabel(mort_label)
#    axs[1,0].set_ylabel(data_label)
##    fig.suptitle(title)
##    publishable.panel_labels(fig = fig, position = 'outside', case = 'lower',
##                                                 prefix = '', suffix = '.', fontweight = 'bold')
#    scalebar = ScaleBar(100*1e3*1.05,box_alpha=0,sep=2,location='lower left') # 1 pixel = 0.2 meter
##    ax.add_artist(scalebar)
#    ax.annotate('CA State', xy=(0.1, 0), xycoords='axes fraction',\
#                    ha='left',va='bottom',size=16)
    plt.show()
#==============================================================================
=======

from __future__ import division
import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from dirs import MyDir
from sklearn import linear_model
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
from sklearn.preprocessing import scale
from sklearn.model_selection import train_test_split
from mpl_toolkits.basemap import Basemap

#from scipy.stats import gaussian_kde
#import statsmodels.api as sm
from sklearn.neighbors import KNeighborsRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPRegressor
#from scipy import signal
                                                                                                                                      #thresh_range=[90]


#======================================================
# PREPARE TRAINING SET
#features: enso, iod, landcover1, landcover2, MTDCA, mySCA2, nl, precip, temp, vod
#response: fire

os.chdir('C:/Users/kkrao/Dropbox/fire_proj_data')
np.random.seed(2)
#list variables
data_types=['et', 'peat', 'pet', 'precip', 'q', 'temp', 'sm','vod','fire']
#data_types.remove('vod') ## just tried to remove vod so that we have data til 2016. but did not help
data_types_names=['Actual Evapotranspiration','Peat Lands','Potential Evapotranspiration',\
              'Precipitation','Specific Humidity','Temperature','Soil Moisture','Vegetation Optical Depth','Fire']
data_type_dict=dict(zip(data_types,data_types_names))
data_type_dates=[source+'dates' for source in data_types]
### which dataset extends only till 2013?

for source in data_type_dates:
    dates = np.load(source+'.npy')
    maxdate = pd.to_datetime(max(dates))
#    print('%s max date %s'%(source, maxdate))

#initialize general start and end date time
start_date, end_date = pd.to_datetime('1900-01-01'), pd.to_datetime('2100-01-01')

#search through dates and find start and end dates that are at intersection of all data types
for source in data_type_dates:
    dates = np.load(source+'.npy')
    mindate = pd.to_datetime(min(dates))
    maxdate = pd.to_datetime(max(dates))
    if mindate > start_date:
        start_date = mindate
    if maxdate < end_date:
        end_date = maxdate
#    print('%s min date is: %s'%(source, mindate))
#create lat lon vector vector
lat = np.load('fire_lat.npy')
lon = np.load('fire_lon.npy')
lon,lat=np.meshgrid(lon,lat)
latcorners=[331, 387]
loncorners=[1097, 1200]
lon,lat=lon[latcorners[0]:latcorners[1],loncorners[0]:loncorners[1]],\
       lat[latcorners[0]:latcorners[1],loncorners[0]:loncorners[1]]

start_date=pd.to_datetime('2015-01-01')     
#initialize dataframe by adding lat, lon, and months
df = pd.DataFrame(lat.flatten(), columns=['lat'])
df['lon'] = lon.flatten()
num_months = (end_date.year - start_date.year)*12 + (end_date.month)
df = df.append([df]*(num_months-1), ignore_index=True)



#add all features into m x n matrix
for source in data_types:

    #load one dataset
    data = np.load(source+'.npy')
    dates = np.load(source+'dates.npy')
    
    #keep only those dates between the start and end date
    data = data[(pd.to_datetime(dates)>=start_date) & \
                (pd.to_datetime(dates)<=end_date),:,:]
    
    #add to dataframe
    data_df = pd.DataFrame(data.flatten(),columns=[source])
    df = pd.concat([df,data_df],axis=1)

#remove examples where any data is missing
df.dropna(inplace=True)
#df.fillna(method='bfill',inplace=True)
#df.fillna(method='ffill',inplace=True)
df.fire/=67500
#for classification
#of nonzero values, 25 percntile = 29.6, 50th=66, 75th = 171.4
    
### subset rows you dont want-===================================================
#df=df.loc[df.fire>0,:]
df=df.loc[df.peat==1,:]


###===========================================================================
thresh1=0
#thresh_range= np.arange(1e-3,1e-1,1e-3)
#thresh_range=[0.0960]
thresh_range=[1e-2]
for thresh2 in thresh_range:
    dfsub=df.copy()
    dfsub.loc[df.fire<=thresh1,'fire']='no fire'
    dfsub.loc[(df.fire>thresh1) & (df.fire<=thresh2),'fire']='small fire'
    dfsub.loc[df.fire>thresh2,'fire']='large fire'
    #split into features and output
    y = dfsub['fire']
    dfsub.drop(['lat','lon','peat','fire'], axis=1,inplace=True)
#    dfsub.apply(lambda x: (x - np.min(x)) / (np.max(x) - np.min(x)))
    dfsub=(dfsub-dfsub.min())/(dfsub.max()-dfsub.min())
    dfsub['fire']=y
    X = dfsub.drop(['fire'],axis=1)

    #split into training and test
    
    X_train, X_test, y_train, y_test = train_test_split(X,y)
    
    # Fitting a logistic regression model
    log_model = LogisticRegression(penalty='l2',C=1)
    log_model.fit(X_train,y_train)
    
    # Checking the model's accuracy
    y_pred=log_model.predict(X_test)
    score = accuracy_score(y_test,y_pred)
    print('For thresh = %0.4f, accuracy = %0.2f'%(thresh2, score))



zoom=6
matplotlib.rcParams.update({'font.size': 28})
#for plotting
#dfsub['fire'].plot(kind='hist')



##PLOT info on data
#info = df.drop(['lat','lon'], axis=1)
#ax=info.hist(figsize=(10,8),xlabelsize=12,ylabelsize=12)
#ax = info.boxplot(return_type='axes')
#ax.set_ylim((-2,4))
cmap = sns.color_palette('inferno', 3)
# classification plots
sns.set_style('ticks')
dftest=pd.concat([X_test,y_test],axis=1)
g=sns.pairplot(dftest,hue='fire',size=zoom/4,plot_kws={'s':3,'alpha':1,\
         'edgecolor':'none'},palette=cmap)
### trying to plot decision boundary
#xx, yy = np.mgrid[0:1:.01, 0:1:.01]
#grid = np.c_[xx.ravel(), yy.ravel()]
#probs = log_model.predict_proba(grid)[:, 1].reshape(xx.shape)
#axs=g.axes
#handles= g._legend_data.values()
#labels=g._legend_data.keys()
#for i in range(len(handles)):
#    handles[i]._sizes = 10
##g.fig.legend(handles,labels)
#plt.show()
## confusion matrix


labels=['no fire', 'small fire','large fire']
fig, ax= plt.subplots(figsize=(1*zoom,1*zoom))
cbaxes = fig.add_axes([1, 0.2, 0.15, 0.772])
sns.heatmap(confusion_matrix(y_test,y_pred,labels=labels\
         ), \
        annot=True, fmt='d',square=True,ax=ax,cbar_ax=cbaxes)
ax.set_xticklabels(labels,rotation=45)
ax.set_yticklabels(labels[::-1],rotation=0)
    
### plotting maps of fire and predictions
month=1
def classify(data,thresh1=0,thresh2=1e-2):
    df=pd.DataFrame(data)
    df[df<=thresh1]=0
    df[(df>thresh1) & (df<=thresh2)]=1
    df[df>thresh2]=2
    return df

def color(df,cmap=cmap):
    df.replace('large fire',cmap[0])

def plot_timeseries_maps(proj='cyl'):
    data=np.load('fire.npy')[-24+month:-23+month,:,:][0]
    df=classify(data)
    mask=np.load('peat.npy')[0,:,:]==1
#    df=df[mask]
#    sns.set(font_scale=1.2)
    fig, axs = plt.subplots(nrows=2,ncols=1   ,\
                            sharey='row',figsize=(8,8))
    marker_size=3
    plt.subplots_adjust(wspace=0.04,hspace=0.04,top=0.83)
    ax=axs[0]
    m = Basemap(projection=proj,lat_0=45,lon_0=0,resolution='l',\
            llcrnrlat=lat[-1,0],urcrnrlat=lat[0,-1],\
            llcrnrlon=lon[-1,0],urcrnrlon=lon[0,-1],\
            ax=ax)
    m.drawcoastlines()
    m.scatter(lon, lat,s=marker_size,c=df,\
                        marker='s',cmap='inferno')
    plt.show()
        #---------------------------------------------------------------
#        data_plot=pred_mort[pred_mort.index.year==year]
#        ax=axs[1,year-year_range[0]]
##        ax.annotate(str(year), xy=(0.96, 0.95), xycoords='axes fraction',\
##                ha='right',va='top')
#        m = Basemap(projection=proj,lat_0=45,lon_0=0,resolution='l',\
#                llcrnrlat=latcorners[0],urcrnrlat=latcorners[1],\
#                llcrnrlon=loncorners[0],urcrnrlon=loncorners[1],\
#                ax=ax)
#        m.readshapefile(Dir_CA+'/CA','CA',drawbounds=True, color='black')
#        plot_data=m.scatter(lats, lons,s=marker_size,c=data_plot,cmap=cmap2\
#                           ,marker='s',vmin=var2_range[0],vmax=var2_range[1],\
#                           norm=mpl.colors.PowerNorm(gamma=1./2.)\
#                                                  )
##        m.drawparallels(parallels,labels=[1,0,0,0], dashes=[1.5,900])
##        m.drawmeridians(meridians,labels=[0,0,0,1], dashes=[1.5,900])
#        #-------------------------------------------------------------------
#    cb0=fig.colorbar(plot_mort,ax=axs.ravel().tolist(), fraction=0.03,\
#                     aspect=30,pad=0.02)
##    cb0.ax.tick_params(labelsize=fs) 
#    tick_locator = ticker.MaxNLocator(nbins=ticks)
#    cb0.locator = tick_locator
#    cb0.update_ticks()
#    cb0.set_ticks(np.linspace(var1_range[0],var1_range[1] ,ticks))
#    axs[0,0].set_ylabel(mort_label)
#    axs[1,0].set_ylabel(data_label)
##    fig.suptitle(title)
##    publishable.panel_labels(fig = fig, position = 'outside', case = 'lower',
##                                                 prefix = '', suffix = '.', fontweight = 'bold')
#    scalebar = ScaleBar(100*1e3*1.05,box_alpha=0,sep=2,location='lower left') # 1 pixel = 0.2 meter
##    ax.add_artist(scalebar)
#    ax.annotate('CA State', xy=(0.1, 0), xycoords='axes fraction',\
#                    ha='left',va='bottom',size=16)
    plt.show()
#==============================================================================
>>>>>>> 72a9ff2f852c04a395d52ba967e884de171fdfd7