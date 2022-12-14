from methods import *


# SAMPLE NAMING CONVENTION
# AXSXXXXXXXXXXX_P0X
#Iterate through Parent Directory
#Generates Dictionary with Batches as Key, Filepaths as values
menu_display()


option = ''
try:
    option = int(input('Enter your choice: '))
        
except:
    print('Wrong input. Please enter a number ...')

if option > 4:
    print("Adios...")
    exit()

elif option < 1:
    print("Adios..")
    exit()   

# Crawl through directories and output a list of [filename,path] & a list of batches [AVS1102060003H,AVS1102060008H...]
sortedpaths,listofbatches = get_filelist()

# Using the information acquired above, build a dictionary.
# Input: a) [filename,filepaths] , b) [AVS1102060003H,AVS1102060008H...]
# Output: 'batch': [filepath1,filepath2,filepath3...]
batchdict = dictionary_builder(listofbatches,sortedpaths)

print(batchdict)
count = 0
datadict = {}
batch_samples = [] # Store samples P01,P02...PX

for batch, filepath in batchdict.items():
    #batchtitle =[]
    print("Processing: " + str(batch))

    num_samples = len(filepath)


    if "Peel" in batch:
        batchtitle = batch[7:25]

    else:

        batchtitle = batch[0:18]

    batchtitle = batchtitle[0:1] + "-" + batchtitle[1:5] + "-" + batchtitle[5:9] + "-" + batchtitle[9:13] + "-" + batchtitle[13:14]
    fivepeaks_average_list = []
    #postmax_average_list = []
    max_load_list = []
    bytes_list = []

    
    count = 1
    for sample in filepath:

        #print(sample[sample.find("P0")+2])
        #samples = sample[sample[sample.find("P0")]:len(sample)-3]
        #graphtitle = batchtitle + ": " + "P0" + str(count) # this digit is for graph
        graphtitle = batchtitle + ": " + "P0" + sample[sample.find("P0")+2] # this digit is for graph

        batch_samples.append(sample[sample.find("P0")+2])


    
        figure, fivepeaks_average, loadmax = process_datafile(sample,graphtitle,option)

        fivepeaks_average_list.append(round(fivepeaks_average,2))
        #postmax_average_list.append(round(postmax_average,2))
        max_load_list.append(round(loadmax,2))
        count += 1

        bio = BytesIO()
        figure.savefig(bio, format="png", bbox_inches='tight')
        bytes_list.append(bio)

        datadict[graphtitle] = fivepeaks_average
   
    batchcorrect = batch[0:1] + "-" + batch[1:5] + "-" + batch[5:9] + "-" + batch[9:13] + "-" + batch[13:14]
    
    #print(datadict)

    columnName = ""
    if option == 1:
        columnName = "5 Peak Average"
    elif option == 2:
        columnName = "Average Force"
    elif option == 3:
        columnName = "Average Load"

    createpdf(fivepeaks_average_list, max_load_list, bytes_list, batchtitle, num_samples,batch_samples,columnName)
    batch_samples.clear()
    plt.close("all")

    print(" ")

'''
header = ['BATCH', 'SAMPLE', "XXX"]
# Write BATCH# SAMPLE # & AVERAGES in an excel file
if option == 1:
    outputfile = "T_Peel_fivePeakAverage.csv"
    header[2] = "5 PEAK AVERAGE"

elif option == 2:
    outputfile = "T_Peel_averageForce.csv"
    header[2] = "AVERAGE FORCE"

elif option == 3:
    outputfile = "T_Peek_AverageLoad.csv"
    header[2] = "AVERAGE LOAD"


a_file = open(outputfile, "w",newline='')

final_list =[]
for x, y in datadict.items():
  temp = x.split(":")
  temp.append(y)
  final_list.append(temp)
  #print(temp)
writer = c.writer(a_file)
writer.writerow(header)
writer.writerows(final_list)
#print(type(datadict))
a_file.close()
#print(final_list)
'''













