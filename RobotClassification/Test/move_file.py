import os
if __name__=="__main__":
    departure = "D:/Project/Robot Detection/RESULTS/2021-06-01/1_Cluster_Only_Small_Total_Var/"
    arrival = "D:/Project/Robot Detection/RESULTS/2021-06-01/More_Than_1_Cluster_Good/"
    list_files = os.listdir(departure)
    csv_files = [x for x in list_files if x.endswith(".csv")]
    png_files = [x for x in list_files if x.endswith(".png")]
    for csv_file in csv_files:
        prefix = csv_file.split(".")[0]
        associated_chart_fn = prefix + ".png"
        if associated_chart_fn in png_files:
            continue
        os.rename(departure + csv_file, arrival + csv_file)
    