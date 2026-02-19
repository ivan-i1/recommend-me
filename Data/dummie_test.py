from config.settings import START_DATE_EXTRACTION, END_DATE_EXTRACTION, INTERNAL_IMG_SAVE_PATH
from tmdb import helper
from datetime import datetime, timedelta

def generate_dateList(start_date: str, end_date: str):
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    
    year_dict = {}
    current_date = start
    
    while current_date <= end:
        year_key = current_date.strftime("%Y")
        
        if year_key not in year_dict:
            year_dict[year_key] = []
            
        year_dict[year_key].append(current_date.strftime("%Y-%m-%d"))
        current_date += timedelta(days=1)
    
    return year_dict

yearsList = generate_dateList(START_DATE_EXTRACTION, END_DATE_EXTRACTION)
print(yearsList)

for year in yearsList:
    print("----------------------")
    for date in yearsList[year]:
        print(date)