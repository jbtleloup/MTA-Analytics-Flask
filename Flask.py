from flask import Flask, render_template, request
from stationList import stationList #import StationList as a variable
import datetime as dt
import pandas as pd
import os

 

app = Flask(__name__)
app.config["DEBUG"] = True

#clean the data 
def readMtaData(url, week):
    df=pd.read_csv(url,skiprows=2)
    df.set_index("REMOTE",inplace=True);
    df.rename(columns={" STATION":"STATION"},inplace=True)
    df.pop(df.columns[-1])
    df["SWIPE_SUM"]=df.sum(axis=1)
    df["DATE"]=week.strftime("%b_%d_%Y")
    return df

#save three plots in the static folder
def getGraph(year, month, station):
    startDate = dt.datetime(int(year),int(month),1)
    weekday=startDate.weekday()
    
    if (weekday == 2 or weekday == 3 or weekday == 4):
        if weekday == 2:
            nb_delta = 3
        elif weekday == 3:
            nb_delta = 2
        else:
            nb_delta = 1
        delta = dt.timedelta(days=nb_delta)
        startDate = startDate + delta
        
    elif(weekday == 6 or weekday == 0 or weekday == 1):
        if weekday == 6:
            nb_delta = 1
        elif weekday == 0:
            nb_delta = 2
        else:
            nb_delta = 3
        delta = dt.timedelta(days=nb_delta)
        startDate = startDate - delta
        
    oneWeek=dt.timedelta(weeks=1)
    
    nextWeek=startDate+oneWeek
    thirdWeek=nextWeek+oneWeek
    fourthWeek=nextWeek+oneWeek+oneWeek
    
    url=startDate.strftime("http://web.mta.info/developers/data/nyct/fares/fares_%y%m%d.csv")
    df1=readMtaData(url, startDate)
    
    url=nextWeek.strftime("http://web.mta.info/developers/data/nyct/fares/fares_%y%m%d.csv")
    df2=readMtaData(url, nextWeek)
    
    url=thirdWeek.strftime("http://web.mta.info/developers/data/nyct/fares/fares_%y%m%d.csv")
    df3=readMtaData(url, thirdWeek)
    
    url=fourthWeek.strftime("http://web.mta.info/developers/data/nyct/fares/fares_%y%m%d.csv")
    df4=readMtaData(url, fourthWeek)

    s1=df1.loc[station]
    s2=df2.loc[station]
    s3=df3.loc[station]
    s4=df4.loc[station]
    
    allData=pd.DataFrame([s1,s2,s3,s4])
    
    station_name = s1["STATION"]
    figureFileName="plot__"+year+"_"+month+"_"+station_name+".png"
    figureFileName=figureFileName.replace(" ", "")
    figureFileName=figureFileName.replace("/", "-")
    figureFileName=figureFileName.replace("&", "AND")
    
    #delete content of static folder before generating new graphs
    folder = 'static'
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(e)
    
    allData.plot(kind="bar",x="DATE",y="SWIPE_SUM", title=station_name, figsize=(13,11)).get_figure().savefig("static/"+figureFileName)
    allData.plot(kind="barh",x="DATE",y="SWIPE_SUM", title=station_name, figsize=(13,11)).get_figure().savefig("static/"+"H_"+figureFileName)    
    allData.plot(kind="line",x="DATE",y="SWIPE_SUM", title=station_name, figsize=(13,11)).get_figure().savefig("static/"+"L_"+figureFileName)
    
    
    return figureFileName

#index route display the home page
@app.route("/", methods=["GET","POST"])
def index():
    return render_template('main_page.html',data=stationList)

#display the bar graph through the result page
@app.route("/response", methods=["POST"])
def response():
    year=request.form["year"]
    month=request.form["month"]
    station=request.form["station"]
    startDate= dt.datetime(int(year),int(month),1)
     
    figureFileName = getGraph(year,month,station)
    
    return render_template('results_page.html',data="static/"+figureFileName, startDate=startDate, station=station)
    
#get the graph for mext month  
@app.route("/nextMonth", methods=["POST"])
def nextMonth():
    startDate = request.form["nextMonth"]
    station = request.form["station"]
    
    year = int(startDate[:4])
    month = int(startDate[5:7])
    
    if month==12:
        startDate = dt.datetime(year+1,1,1)
    else:
        startDate = dt.datetime(year,month+1,1)
    
    newMonth = startDate
    print(newMonth.year, newMonth.month)
    figureFileName = getGraph(str(newMonth.year),str(newMonth.month),station)
    
    return render_template('results_page.html', data="static/"+figureFileName, startDate=startDate,station=station)

#get the graph for previous month
@app.route("/previousMonth", methods=["POST"])
def previousMonth():
    startDate = request.form["previousMonth"]
    station = request.form["station"]
    
    year = int(startDate[:4])
    month = int(startDate[5:7])
    
    if month==1:
        startDate = dt.datetime(year-1,12,1)
    else:
        startDate = dt.datetime(year,month-1,1)
        # Note subtract one here
    newMonth = startDate
    
    figureFileName = getGraph(str(newMonth.year),str(newMonth.month),station)
    
    return render_template('results_page.html', data="static/"+figureFileName, startDate=startDate,station=station)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
