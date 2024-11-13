import streamlit as st
import requests
import pandas as pd
from io import StringIO
import time
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Retrieve the API key from the environment
API_KEY = os.getenv('GOOGLE_MAPS_API')
print(API_KEY)
def find_practices(location):
    search_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    search_params = {
        "query": location,
        "key": API_KEY
    }

    practice_details = []
    while True:
        response = requests.get(search_url, params=search_params)
        data = response.json()
        places = data.get('results', [])
        
        for place in places:
            place_id = place['place_id']
            details_url = "https://maps.googleapis.com/maps/api/place/details/json"
            details_params = {
                "place_id": place_id,
                "fields": "name,formatted_address,formatted_phone_number,website,opening_hours,rating",
                "key": API_KEY
            }

            details_response = requests.get(details_url, params=details_params)
            details = details_response.json().get('result', {})

            practice_info = {
                "name": details.get("name"),
                "address": details.get("formatted_address"),
                "phone_number": details.get("formatted_phone_number"),
                "website": details.get("website"),
                "opening_hours": details.get("opening_hours", {}).get("weekday_text"),
                "rating": details.get("rating")
            }
            practice_details.append(practice_info)

        next_page_token = data.get('next_page_token')
        if not next_page_token:
            break
        
        search_params['pagetoken'] = next_page_token
        time.sleep(2)

    return practice_details

def convert_to_csv(data):
    output = StringIO()
    df = pd.DataFrame(data)
    df.to_csv(output, index=False)
    return output.getvalue()

st.title("Google maps scraper for health services")
st.write("Enter a location to find and download the data as a CSV.")

location = st.text_input("Location", "London")

if st.button("Fetch Data"):
    practices = find_practices(location)

    if practices:
        df = pd.DataFrame(practices)
        st.write("Results:")
        st.dataframe(df)

        csv_data = convert_to_csv(practices)
        st.download_button(
            label="Download data as CSV",
            data=csv_data,
            file_name="TMS_practices.csv",
            mime="text/csv"
        )
    else:
        st.write("No results found.")