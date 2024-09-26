import streamlit as st
import os
import pickle
import pandas as pd
from io import BytesIO
import tempfile
import gdown

from automate_약가파일 import generate_drug_info_sheet

@st.cache_resource
def download_pickle_from_drive(file_id, file_name):
    url = "https://drive.google.com/drive/folders/1NCNDXVfOd1HH_-YfBtSUaWJK5ZIsomJ5"
    gdown.download(url, file_name, quiet=False)

def load_pickle_data(filenames):
    variables = {}
    with tempfile.TemporaryDirectory() as tmpdirname:
        for filename in filenames:
            filename = os.path.join(f"{filename}.pkl")
            download_pickle_from_drive(filename)
            with open(filename, 'rb') as f:
                variables[filename] = pickle.load(f)
    return variables

def get_compound_list(variables):
    compound_dict = variables['dict_main_compound_infos_total_repr']
    return [f"{key} ({value['주성분이름']})" for key, value in compound_dict.items()]

def main():
    st.title("Drug Price File Automation Tool")

    # Dictionary of variable names and their corresponding Google Drive file IDs
    filenames = [
        'compound_id_and_dates_by_product_id_all_period',
        'continuous_events_by_product_id',
        'continuous_events_str_by_product_id',
        'dates_for_reimbursement_publication',
        'dict_main_compound_infos_total_repr',
        'product_ids_total_period',
        'product_info_by_id',
        'reimbursement_events_and_dates_by_product_id_all_period'
    ]

    # Load pickle data
    variables = load_pickle_data(filenames)

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
