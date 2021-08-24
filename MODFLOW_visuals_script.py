#import packages
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime as dt
from datetime import timedelta as td
import numpy as np
from pandas import Timestamp
import seaborn as sns
from PIL import Image
import glob
from numpy.random import randint
import matplotlib as mpl
import os
import math

#import relevant .xlsx or .csv file; create a dataframe
file_path = r'./l210621trh_S1_targets.csv'   #file_path should be adjusted for each the specified input dataset
df_raw = pd.read_csv(file_path)              #determine if pd.read_csv() or pd.read_excel() required
reducer = len(df_raw) -13
df = df_raw[:reducer]

#create subfolder for Head Vs. Time Figures
os.mkdir("Head_Vs_Time_Figures")
os.mkdir("ScatterPlots")
os.mkdir("Head_Vs_Time_3x2")

#define a reference date; convert to a "Date" column
refDate = dt(1972, 6, 1)                    #determine specified reference date
maxDate = dt(2021,6,1)                      #determine specified maximum date

#add column "Date" relative to days past refDate
df['Date'] = refDate + pd.TimedeltaIndex(df['Time'], unit='D')

#define series for graphing: observed, computed, layers, residual
observed = df['Observed']
computed = df['Computed']
residual = df['Residual']

#define different markers for graphing
valid_markers = ([item[0] for item in mpl.markers.MarkerStyle.markers.items() if
item[1] != 'nothing' and not item[1].startswith('tick') and not item[1].startswith('caret')])

#function to create,call,save scatterplot: "Observed_vs_Computed"
def obs_comp_scatter():
    fig, ax = plt.subplots()

    layers = df.groupby("Layer")
    markers = np.random.choice(valid_markers, len(layers), replace=False)

    for marker, layer in zip(markers, range(len(layers))):
        group = layer+1
        data = layers.get_group(group)
        xAxis = data["Observed"]
        yAxis = data["Computed"]
        ax.scatter(xAxis, yAxis, marker=marker,
                   label="Layer {0}".format(group), cmap='tab20',alpha=0.3)
    ax.legend(title="Layers", bbox_to_anchor=(1.0, 1.05))
    plt.title("Observed vs. Computed Target Value")
    plt.xlabel("Observed Value")
    plt.ylabel("Model Value")
    plt.grid()
    plt.tight_layout()
    plt.savefig("ScatterPlots/Observed_vs_Computed.png")
    plt.show 
    
def obs_resid_scatter():
    fig, ax = plt.subplots()

    layers = df.groupby("Layer")
    markers = np.random.choice(valid_markers, len(layers), replace=False)
    
    for marker, layer in zip(markers, range(len(layers))):
        group = layer+1
        data = layers.get_group(group)
        xAxis = data["Observed"]
        yAxis = data["Residual"]
        ax.scatter(xAxis, yAxis, marker=marker,
                   label="Layer {0}".format(group),cmap='tab20', alpha=0.3)
    ax.legend(title="Layers", bbox_to_anchor=(1.0, 1.05))
    plt.title("Observed vs. Residuals")
    plt.xlabel("Observed Value")
    plt.ylabel("Residual")
    plt.grid()
    plt.tight_layout()
    plt.savefig("ScatterPlots/Observed_vs_Residuals.png")
    plt.show()
    
#call the previous 2 functions to create and save scatterplots
obs_comp_scatter()
obs_resid_scatter()

#######


#Create head vs time plots
UniqueNames = df.Name.unique()

df_dict = {elem : pd.DataFrame for elem in UniqueNames}

for key in df_dict.keys():
    df_dict[key] = df[:][df.Name == key]
    
# iterate through dictionary and plot
fig, ax1 = plt.subplots()

#x_min, x_max = refDate, df.Date.max()
#y_min, y_max = df.Observed.min(), df.Observed.max()

for i,val in df_dict.items():
    #plt.figure()
    ax1 = df_dict[i].plot(x='Date',y='Observed',marker = 'o') 
    #ax = "Time", y="Computed", marker = 'o', color="r")
    ax1 = df_dict[i].plot(x="Date", y="Computed",ax=ax1, marker = 'o', color="r")
    plt.xlim([refDate, maxDate])
    plt.ylim([df.Observed.min(), df.Observed.max()])
    ax1.set_ylabel("Head")
    #plt.legend()
    #plt.xlabel("Time")
    #plt.ylabel("Head")
    #plt.savefig("...")
    #scatter_directory = 
    ax1.set_title(i)
    plt.savefig(r'Head_Vs_Time_Figures/{}.png'.format(i), dpi=300)
    plt.close()
    
FOLDER_PATH = "Head_Vs_Time_Figures"
GROUP_BY = 6

def paste_images_in_PDF(page, groups): 
    width, height = int(8.27 * 450), int(11.7 * 375) # A4 at 300dpi
    pdf = Image.new('RGB', (width, height), 'white')
    for imgIndex, img in enumerate(groups):
        #There is a nicer way mathmatical formula way of doing this - but my brain is fried.
        if imgIndex == 0:
            pdf.paste(Image.open(img), box=(0, 0))
        if imgIndex == 1:
            pdf.paste(Image.open(img), box=(int(width/2. +0.5), 0))
        if imgIndex == 2:
            pdf.paste(Image.open(img), box=(0, int(height/3. + 0.5)))
        if imgIndex == 3:
            pdf.paste(Image.open(img), box=(int(width/2.+0.5), int(height/3.+0.5))) 
        if imgIndex == 4:
            pdf.paste(Image.open(img), box=(0, int(height/3.+0.5)*2))
        if imgIndex == 5:
            pdf.paste(Image.open(img), box=(int(width/2.+0.5), int(height/3.+0.5)*2))  
    pdf.save('Head_Vs_Time_3x2/page_{0}.pdf'.format(page+1))

def group_images_generator(images):
    total_images = len(images)
    for i in range(0,math.ceil(total_images/GROUP_BY)):
        yield images[i*GROUP_BY:i*GROUP_BY+GROUP_BY]
    
def main():
    images = glob.glob("{0}/*.png".format(FOLDER_PATH)) 
    for image in images:
        with open(image, 'rb') as file:
            img = Image.open(file)
    groups = group_images_generator(images)
    [paste_images_in_PDF(page, group) for page, group in enumerate(groups) ]
    
if __name__ == "__main__":
    main()
    
print("Scipt complete. Review output files.")
