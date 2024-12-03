import streamlit as st
import requests
import pandas as pd
from io import StringIO
import time

# Retrieve the API key from Streamlit secrets
API_KEY = st.secrets["google"]["GOOGLE_MAPS_API"]

def find_practices(location):
    search_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    search_params = {
        "query": location,
        "key": API_KEY
    }

    practice_details = []
    while True:
        response = requests.get(search_url, params=search_params)
        if response.status_code != 200:
            st.error(f"Error: Unable to fetch data from the API. Status code: {response.status_code}")
            return []

        data = response.json()
        places = data.get('results', [])
        
        for place in places:
            place_id = place['place_id']
            details_url = "https://maps.googleapis.com/maps/api/place/details/json"
            details_params = {
                "place_id": place_id,
                "fields": "name,formatted_address,formatted_phone_number,website,opening_hours,rating,user_ratings_total",
                "key": API_KEY
            }

            details_response = requests.get(details_url, params=details_params)
            if details_response.status_code != 200:
                continue

            details = details_response.json().get('result', {})
            practice_info = {
                "name": details.get("name"),
                "address": details.get("formatted_address"),
                "phone_number": details.get("formatted_phone_number"),
                "website": details.get("website"),
                "opening_hours": details.get("opening_hours", {}).get("weekday_text"),
                "rating": details.get("rating"),
                "no_of_reviews": details.get("user_ratings_total") 
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

# Streamlit UI
st.title("Google Maps Scraper for Health Services")
st.write("Enter a location to find and download the data as a CSV.")

location = st.text_input("Location", "London")

if st.button("Fetch Data"):
    if not API_KEY:
        st.error("API key is missing. Please configure it in your Streamlit secrets.")
    else:
        st.info("Fetching data. Please wait...")
        practices = find_practices(location)

        if practices:
            df = pd.DataFrame(practices)
            st.write("Results:")
            st.dataframe(df)

            csv_data = convert_to_csv(practices)
            st.download_button(
                label="Download data as CSV",
                data=csv_data,
                file_name="health_practices.csv",
                mime="text/csv"
            )
        else:
            st.write("No results found.")
