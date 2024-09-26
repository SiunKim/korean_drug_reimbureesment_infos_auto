import streamlit as st
import os
import pickle
import pandas as pd
from io import BytesIO
import tempfile
import requests
from urllib.parse import urlparse, parse_qs

from automate_약가파일 import generate_drug_info_sheet

# Use Streamlit's secrets management for sensitive data
FOLDER_URL = st.secrets["google_drive_folder_url"]

def download_file_from_drive(file_id):
    url = f"https://drive.google.com/drive/folders/1NCNDXVfOd1HH_-YfBtSUaWJK5ZIsomJ5/{file_id}.pkl"
    response = requests.get(url)
    return BytesIO(response.content)

def load_pickle_data(file_ids):
    variables = {}
    for filename, file_id in file_ids.items():
        file_content = download_file_from_drive(file_id)
        variables[filename] = pickle.load(file_content)
    return variables

def get_file_id_from_url(url):
    parsed_url = urlparse(url)
    file_id = parse_qs(parsed_url.query).get('id')
    return file_id[0] if file_id else None

def get_compound_list(variables):
    compound_dict = variables['dict_main_compound_infos_total_repr']
    return [f"{key} ({value['주성분이름']})" for key, value in compound_dict.items()]

def main():
    st.title("Drug Price File Automation Tool")

    # File IDs dictionary (you should update these with your actual file IDs)
    file_ids = {
        'compound_id_and_dates_by_product_id_all_period':
            'compound_id_and_dates_by_product_id_all_period',
        'continuous_events_by_product_id': 'continuous_events_by_product_id',
        'continuous_events_str_by_product_id': 'continuous_events_str_by_product_id',
        'dates_for_reimbursement_publication': 'dates_for_reimbursement_publication',
        'dict_main_compound_infos_total_repr': 'dict_main_compound_infos_total_repr',
        'product_ids_total_period': 'product_ids_total_period',
        'product_info_by_id': 'product_info_by_id',
        'reimbursement_events_and_dates_by_product_id_all_period':
            'reimbursement_events_and_dates_by_product_id_all_period'
    }

    # Load pickle data
    variables = load_pickle_data(file_ids)

    # Get the list of compounds
    compound_list = get_compound_list(variables)

    # Provide options for users to select or input compound IDs
    id_selection_method = st.radio(
        "Compound ID Selection Method",
        ('Select from existing list', 'Direct input')
    )

    if id_selection_method == 'Select from existing list':
        selected_compounds = st.multiselect(
            "Select compound IDs",
            compound_list
        )
        selected_ids = [compound.split()[0] for compound in selected_compounds]
    else:
        user_input = st.text_area(
            "Enter compound IDs (one ID per line)",
            "\n".join(list(variables['dict_main_compound_infos_total_repr'].keys())[:5])
        )
        selected_ids = user_input.split('\n')

    if st.button("Generate Excel File"):
        if selected_ids:
            wb = generate_drug_info_sheet(selected_ids, variables)

            buffer = BytesIO()
            wb.save(buffer)
            buffer.seek(0)

            st.download_button(
                label="Download Excel File",
                data=buffer,
                file_name="drug_info_sheet_styled.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning("Please select or input at least one compound ID.")

if __name__ == "__main__":
    main()
