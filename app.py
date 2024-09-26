import streamlit as st
import os
import pickle
import pandas as pd
from io import BytesIO
import gdown
from automate_약가파일 import generate_drug_info_sheet

FOLDER_URL = st.secrets["google_drive_folder_url"]
CACHE_DIR = ".cache"  # Permanent cache directory

# 파일 이름과 한글 번역을 매핑하는 딕셔너리
file_name_translations = {
    'compound_id_and_dates_by_product_id_all_period': '제품별 성분 ID 및 날짜 정보',
    'continuous_events_by_product_id': '제품별 연속 이벤트',
    'continuous_events_str_by_product_id': '제품별 연속 이벤트 문자열',
    'dates_for_reimbursement_publication': '급여 고시 날짜',
    'dict_main_compound_infos_total_repr': '주요 성분 정보 사전',
    'product_ids_total_period': '전체 기간 제품 ID',
    'product_info_by_id': '제품별 정보',
    'reimbursement_events_and_dates_by_product_id_all_period': '제품별 급여 이벤트 및 날짜'
}

@st.cache_resource
def download_folder_from_drive(output_path):
    print(f"Running download_folder_from_drive to {output_path}")
    if not os.path.exists(output_path):
        os.makedirs(output_path)
        print(f"Created directory: {output_path}")
    print(f"Downloading folder from Google Drive...")
    gdown.download_folder(url=FOLDER_URL, output=output_path, quiet=False)
    print(f"Download completed.")

def load_pickle_file(file_path):
    print(f"Loading pickle file: {file_path}")
    with open(file_path, 'rb') as f:
        data = pickle.load(f)
    print(f"Loaded pickle file: {file_path}")
    return data

@st.cache_data
def load_pickle_data(filenames):
    print("Running load_pickle_data...")
    download_folder_from_drive(CACHE_DIR)
    variables = {}
    progress_bar = st.progress(0)
    status_text = st.empty()
    for i, filename in enumerate(filenames):
        file_path = os.path.join(CACHE_DIR, f"{filename}.pkl")
        if os.path.exists(file_path):
            variables[filename] = load_pickle_file(file_path)
            status_text.text(f"로딩 중: {file_name_translations.get(filename, filename)}")
        else:
            print(f"Warning: File not found: {file_path}")
            st.warning(f"파일을 찾을 수 없습니다: {file_path}")
        # 진행 상황 업데이트
        progress = (i + 1) / len(filenames)
        progress_bar.progress(progress)
    progress_bar.empty()
    status_text.empty()
    print("Finished loading all pickle files.")
    return variables

def get_compound_list(variables):
    compound_dict = variables['dict_main_compound_infos_total_repr']
    return [f"{key} ({value['주성분이름']})" for key, value in compound_dict.items()]

def main():
    st.title("심평원 약제급여목록 성분명 기반 제품 정보 정리 자동화")

    # Initialize session state
    if 'selected_ids' not in st.session_state:
        st.session_state.selected_ids = []

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

    variables = load_pickle_data(filenames)
    compound_list = get_compound_list(variables)

    id_selection_method = st.radio(
        "의약품 성분 ID 선택 방법",
        ('목록에서 선택', '직접 입력')
    )

    if id_selection_method == '목록에서 선택':
        default_selections = [item for item in compound_list if item.split()[0] in st.session_state.selected_ids]
        selected_compounds = st.multiselect(
            "의약품 성분 ID 선택",
            options=compound_list,
            default=default_selections
        )
        st.session_state.selected_ids = [compound.split()[0] for compound in selected_compounds]
    else:
        user_input = st.text_area(
            "의약품 성분 ID 입력 (한 줄에 하나씩)",
            "\n".join(st.session_state.selected_ids) if st.session_state.selected_ids else "\n".join(list(variables['dict_main_compound_infos_total_repr'].keys())[:5])
        )
        st.session_state.selected_ids = [id.strip() for id in user_input.split('\n') if id.strip()]

    if st.button("엑셀 파일을 생성합니다."):
        if st.session_state.selected_ids:
            wb = generate_drug_info_sheet(st.session_state.selected_ids, variables)
            
            buffer = BytesIO()
            wb.save(buffer)
            buffer.seek(0)
            
            st.download_button(
                label="엑셀 파일 다운로드",
                data=buffer,
                file_name="drug_info_sheet_styled.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning("최소 하나의 의약품 성분 ID를 선택하거나 입력해주세요.")

if __name__ == "__main__":
    main()