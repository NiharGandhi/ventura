import streamlit as st
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

# Check if the Firebase app is already initialized
if not firebase_admin._apps:
    # Initialize Firebase app
    cred = credentials.Certificate('ventura-5d1fe-firebase-adminsdk-q6x4i-2a488de72f.json')  # Replace with your service account key file
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://ventura-5d1fe-default-rtdb.asia-southeast1.firebasedatabase.app/'  # Replace with your Firebase project's URL
    })

# Rest of the code for Streamlit web app
def main():
    st.title('Attendance Viewer')

    # Function to fetch attendance data from Firebase based on filters
    def get_attendance_data(filter_year, filter_month, filter_day, search_name):
        ref = db.reference('/attendance')
        attendance_data = ref.get()

        if attendance_data is None:
            return []

        filtered_data = []
        for year, year_data in attendance_data.items():
            if year != filter_year:
                continue

            for month, month_data in year_data.items():
                if month.lower() != filter_month.lower():
                    continue

                if month_data is None:
                    continue

                if filter_day != 'All' and filter_day.capitalize() not in month_data.keys():
                    continue

                day_data = month_data.get(filter_day.capitalize())
                if day_data is None:
                    continue

                for record_key, record in day_data.items():
                    if search_name and search_name.lower() not in record['name'].lower():
                        continue

                    filtered_data.append(record)

        return filtered_data

    # Get distinct years, months, and days from the database
    ref = db.reference('/attendance')
    attendance_data = ref.get()
    if attendance_data is not None:
        years = sorted(list(attendance_data.keys()))
        months = sorted(list(set(month.lower() for year in attendance_data.values() for month in year.keys())))
    else:
        years = []
        months = []

    # Display filters
    filter_year = st.selectbox('Filter by Year', ['All'] + years)
    if filter_year != 'All':
        ref = db.reference(f'/attendance/{filter_year}')
        year_data = ref.get()
        if year_data is not None:
            months = sorted(list(year_data.keys()))
        else:
            months = []
        filter_month = st.selectbox('Filter by Month', ['All'] + months)
    else:
        filter_month = 'All'

    if filter_month != 'All':
        ref = db.reference(f'/attendance/{filter_year}/{filter_month.capitalize()}')
        month_data = ref.get()
        if month_data is not None:
            days = sorted(list(month_data.keys()))
        else:
            days = []
        filter_day = st.selectbox('Filter by Day', ['All'] + days)
    else:
        filter_day = 'All'

    search_name = st.text_input('Search by Name')

    if st.button('Get Attendance'):
        attendance_data = get_attendance_data(filter_year, filter_month, filter_day, search_name)
        if len(attendance_data) == 0:
            st.info('No attendance records found.')
        else:
            st.table(attendance_data)

if __name__ == '__main__':
    main()
