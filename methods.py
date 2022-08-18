from cProfile import label
import os
import csv as c
from turtle import color
import pandas as pd
import numpy as np
from scipy.signal import find_peaks
import matplotlib as mpl
import matplotlib.pyplot as plt
from fpdf import FPDF
from io import BytesIO
import base64
import urllib
import fnmatch
mpl.use("Agg") 
## T-Peel Analysis Script 

## Requirements for T-Peel Envelope Sample Analysis 
# -Force vs. Travel plot - DONE
# -5 highest peak average excluding first peak - DONE
# -Average of all data except first peak - DONE
# -Group all graphs associated to the same serial number into 1 PDF - DONE
# -Graph title should be file name title - DONE
# -PDF file name should just be serial number - DONE
# -Show averages in red if the value is below 35.2N - DONE
# -Show on plot what peaks are used for 5 highest calculation - DONE

###############################################################
# FIND PEAKS PROMINANCE VALUE TO
set_prominance = 1

class PDF(FPDF):
    def header(self):
        # Logo
        #self.image('LtaLogo.png', 10, 8, 33)
        # Arial bold 15
        self.set_font('helvetica', 'B', 20)
        # Move to the right
        self.cell(80)
        # Title
        self.cell(30, 10, "SST086 - Envelope T-Peel - Report", 0, 0, 'C')
        # Line break
        self.ln(20)

    # Page footer
    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('helvetica', 'I', 8)
        # Page number
        self.cell(0, 10, 'Page ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')

    def load_resource(self, reason, filename):
        if reason == "image":
            if filename.startswith("http://") or filename.startswith("https://"):
                f = BytesIO(urlopen(filename).read())
            elif filename.startswith("data"):
                f = filename.split('base64,')[1]
                f = base64.b64decode(f)
                f = io.BytesIO(f)
            else:
                f = open(filename, "rb")
            return f
        else:
            self.error("Unknown resource loading reason \"%s\"" % reason)

def createpdf(fivepeaks_average_list, max_load_list, figure_list, batchtitle, num_samples,samplelist,option):
    max_page_width = 190

    
    #if option == 1

   
    # Instantiation of inherited class
    pdf = PDF()

    # Calls total page number for footer
    pdf.alias_nb_pages()

    # Adds page because there is currently no page
    pdf.add_page()

    #Set fonts for pdf
    pdf.set_font('helvetica', 'B', 10)
    pdf.set_fill_color(190,190,190)

    ##Table for data summary
    label_width = 40
    cell_height = 6
    pdf.cell(max_page_width/8 * 1, cell_height, "Batch: ", 1, align = "R", fill = True)
    pdf.cell(max_page_width/8 * 7, cell_height, batchtitle ,1, align = "C",fill = True)
    pdf.ln()

    #Headers
    num_headers = 3
    pdf.cell(max_page_width/num_headers * 1, cell_height, "Sample #",1, align = "C", fill = True)

    pdf.cell(max_page_width/num_headers * 1, cell_height, option + "  [lbs]",1, align = "C", fill = True)
    #pdf.cell(max_page_width/num_headers * 1, cell_height, "Post-Max Avg [lbs]",1, align = "C", fill = True)
    pdf.cell(max_page_width/num_headers * 1, cell_height, "Max Load [lbs]" ,1, align = "C", fill = True)
    pdf.ln()

    print("\nSamples in batch: ") 

    for sample in range(num_samples):
        sample_no = "P0" + samplelist[sample] # written into cells in report 

        #print("Sample in batch: ") 
        print(sample_no, end = " ")

        pdf.cell(max_page_width/num_headers * 1, cell_height, sample_no,1, align = "C")

        """
                if fivepeaks_average_list[sample] < 8: 
                    pdf.set_fill_color(255,153,153) # red
                    pdf.cell(max_page_width/num_headers * 1, cell_height, str(fivepeaks_average_list[sample]) ,1, align = "C",fill = True)
                else: 
                    pdf.set_fill_color(153,253,153) # green
                    pdf.cell(max_page_width/num_headers * 1, cell_height, str(fivepeaks_average_list[sample]) ,1, align = "C",fill = True)
        """
        pdf.cell(max_page_width/num_headers * 1, cell_height, str(fivepeaks_average_list[sample]) ,1, align = "C",fill = True)
        pdf.cell(max_page_width/num_headers * 1, cell_height, str(max_load_list[sample]),1, align = "C")
        pdf.ln()

    if option == "5 Peak Average":
        pdf.cell(0,5,"*ASTM D751 Standard")
    elif option == "Average Force":
        pdf.cell(0,5,"*ASTM D3330M Standard")
    elif option == "Average Load":
        pdf.cell(0,5,"*ASTM D1876 Standard")

    #Set cell for graph images
    origin_x = 12.5
    origin_y = pdf.get_y() + 5
    delta_y = 65
    picture_width = (max_page_width/2) - 10
    padding = 5
    position = 1 

    pdf.set_xy(origin_x, origin_y)

    for figure in figure_list:
        if position == 1:
            pdf.set_xy(origin_x, origin_y)
        if position == 2:
            pdf.set_xy(origin_x + picture_width + padding, origin_y)
        if position == 3: 
            pdf.set_xy(origin_x, origin_y + delta_y + padding)
        if position == 4: 
            pdf.set_xy(origin_x + picture_width + padding, origin_y + delta_y + padding)
        if position == 5: 
            pdf.set_xy(origin_x, origin_y + delta_y*2 + padding)
        if position == 6: 
            pdf.set_xy(origin_x + picture_width + padding, origin_y + delta_y*2 + padding )
        
        pdf.image(name='data://image/png;base64,' + base64.b64encode(figure.getvalue()).decode() , w=picture_width, h=65, type='png')
        position += 1


    #Saves PDF to filesystem
    pdf.output(str(batchtitle + "_" + option +".pdf"), "F")

    return None

file_data = []
#array = []

# Graphs Force vs Travel Plot, finds statistical data points
# Takes in datafile (formatted CSV of peel data, specific to LTA MV) and csv file name
def process_datafile(datafile, graphtitle,standard):
    #stringr = ".csv"
    with open(datafile) as file_name:
        #array = np.loadtxt(file_name, delimiter="," , skiprows=1,unpack= True)

        #if filename is a csv file... process data file
        if ".csv" in datafile:
            #print(datafile)
            file_data = pd.read_csv(file_name)
            #some files dont have the S:load column but Ch:load, 
            # if found, rename and reassign to dataframe
            tempString = "Ch:Load (lbs)"
            if tempString in file_data.columns:
                file_data = file_data.rename(columns={"Ch:Load (lbs)": "S:Load (lbs)"})
     
            file_data=file_data[["S:Load (lbs)","S:Position (in)"]]
            file_data = file_data.loc[:,~file_data.columns.duplicated()]
    
    #print(file_data)
    load = file_data["S:Load (lbs)"].values
    position = file_data["S:Position (in)"].values

    #print(file_data)
    #Load Data Processing

    #Find all peaks + 5 peak average
    peaks, properties = find_peaks(load, prominence = set_prominance , distance= 1)   # prominence argument filters out noisy peaks
    loadpeaks = load[peaks] # peaks finds indexes - loadpeaks is the actual load value


    loadmax = np.amax(load) #Find largest peak in Load

    #maxindex = np.where(loadpeaks == loadmax) #Find index of largest peak
    
    #maxindex = maxindex[0][0]+1 #Numpy workaround / Unused
     #Graph
    fig = plt.figure()
   
    plt.title(graphtitle)
    plt.ylabel("Load [lbs]")
    plt.xlabel("Crosshead Displacement [in]")
    plt.plot(position,load , label = "Load VS Position")

    #D751 Standard
    if standard == 1:
        #print(load)
        n = 5 
        # Returns top 5 peaks in list after the first peak
        fivepeaks_idx = np.argpartition(loadpeaks[1:], -n)[-n:]
        fivepeaks_values = loadpeaks[fivepeaks_idx+1] # Print 5 peaks values
        print("######################################################################\nPrinting Peaks:")
        print(loadpeaks)
        print("Printing 5 Peak Index:")
        print(fivepeaks_idx+1)
        print("Printing 5 Peaks Values:")
        print(fivepeaks_values)


        fivepeaks_average = np.average(fivepeaks_values) #Find the 5 peak average
        #postmax_average = np.average(load[maxindex:]) #Postmax average /unused

        #Graph
        plt.plot(position[peaks] , load[peaks], "x")
        plt.plot(position[peaks[fivepeaks_idx+1]], load[peaks[fivepeaks_idx+1]], "o", color = 'r')
        plt.text(2.5,27, "Avg " + str(round(fivepeaks_average,2)))
        if loadmax < 30:
            plt.ylim([0,30])
        else: 
            plt.ylim([0,50])

        if fivepeaks_average < 7.92:
            plt.axhline(y=fivepeaks_average, color = "r", linestyle="-" , label = "5 Peak Average")
        else:
            plt.axhline(y=fivepeaks_average, color = "g", linestyle="-", label = "5 Peak Average")

    #D3330M
    elif standard == 2:

        #print(load)

        #Where 2 & 6 belong to the crosshead position of the UTM
        indexOfPosition = np.where((position >= 2) & (position <= 6))

        fivepeaks_average = np.mean(load[indexOfPosition]) # Save the average load between 1"-3" of peel
        print("Average Force: ", end = '')
        print(fivepeaks_average)

        plt.axhline(y=fivepeaks_average, color = "r", linestyle="-" , label = "Average Force")
        plt.plot(position[indexOfPosition],load[indexOfPosition], color = 'g')
    #D1876 Standard 
    elif standard == 3:
        #print(peaks[0])
        initial_position = position[peaks[0]]
        #print(initial_position)
        
        #Where 10 is the position of crosshead movement
        indexOfPosition = np.where((position >= initial_position) & (position <= initial_position + 10))
        fivepeaks_average = np.mean(load[indexOfPosition]) 

        print("Average Load: ", end = '')
        print(fivepeaks_average)
        plt.plot(position[peaks[0]] , load[peaks[0]], "x")
        plt.axhline(y=fivepeaks_average, color = "r", linestyle="-" , label = "Average Load")
        plt.plot(position[indexOfPosition],load[indexOfPosition], color = 'g')
        

    plt.grid()
    plt.legend()

    return fig, fivepeaks_average, loadmax #, averageForce, averageLoad



def menu_display():

        print("##############################")
        print("# T-Peel Data Processor Menu #")
        print("# [1] D751 Standard          #")
        print("# [2] D3330M Standard        #")
        print("# [3] D1876 Standard         #")   
        print("# Any other # Key to Exit    #")
        print("##############################")
    

