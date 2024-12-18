"""App.py"""
import os
import pickle
from io import BytesIO
import gdown
import tempfile

import streamlit as st

from automate_약가파일 import generate_drug_info_sheet

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

def download_and_load_pickle(file_id):
    """Download pickle file from Google Drive and load it"""
    try:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            # 다운로드 URL 형식 변경
            url = f"https://drive.google.com/file/d/{file_id}/view?usp=sharing"
            
            st.write(f"파일 다운로드를 시작합니다... URL: {url}")
            
            # gdown 옵션 수정
            success = gdown.download(
                url=url, 
                output=temp_file.name, 
                quiet=False,
                fuzzy=True,
                use_cookies=False  # 쿠키 사용 비활성화
            )
            
            if not success:
                st.error("첫 번째 방법 실패, 두 번째 방법 시도...")
                direct_url = f"https://drive.google.com/uc?export=download&id={file_id}"
                success = gdown.download(
                    url=direct_url,
                    output=temp_file.name,
                    quiet=False,
                    fuzzy=True
                )
            
            if not success:
                st.error(f"파일 다운로드에 실패했습니다. \nURL: {url}\nFile ID: {file_id}")
                return None
                
            file_size = os.path.getsize(temp_file.name)
            st.write(f"다운로드된 파일 크기: {file_size} bytes")
            
            if file_size == 0:
                st.error("다운로드된 파일이 비어있습니다.")
                return None
                
            with open(temp_file.name, 'rb') as f:
                variables = pickle.load(f)
            
            os.unlink(temp_file.name)
            return variables
            
    except Exception as e:
        st.error(f"상세 오류 내용: {str(e)}")
        import traceback
        st.error(f"상세 스택 트레이스: {traceback.format_exc()}")
        return None

# @st.cache_resource
def load_variables():
    """Load variables from Google Drive"""
    file_id = st.secrets.get("pickle_file_id")
    if not file_id:
        st.error("파일 ID가 설정되지 않았습니다.")
        return None
    
    return download_and_load_pickle(file_id)

def get_compound_list(variables):
    """get_compound_list"""
    compound_dict = variables['dict_main_compound_infos_total_repr']
    return [f"{key} ({value['주성분이름']})" for key, value in compound_dict.items()]

def main():
    st.title("심평원 약제급여목록 성분명 기반 제품 정보 정리 자동화")
    variables = load_variables()

    if variables is None:
        st.error("데이터를 불러오는데 실패했습니다. 네트워크 연결을 확인해주세요.")
        return

    # Get default IDs from variables
    default_ids = list(variables['dict_main_compound_infos_total_repr'].keys())[:5]
    compound_list = get_compound_list(variables)

    # Use a container to store the current selection
    if 'selected_compounds_container' not in globals():
        global selected_compounds_container
        selected_compounds_container = [comp for comp in compound_list
                                            if comp.split()[0] in default_ids]

    id_selection_method = st.radio(
        "의약품 성분 ID 선택 방법",
        ('목록에서 선택', '직접 입력')
    )

    current_selected_ids = []

    if id_selection_method == '목록에서 선택':
        selected_compounds = st.multiselect(
            "의약품 성분 ID 선택",
            options=compound_list,
            default=selected_compounds_container
        )
        selected_compounds_container = selected_compounds  # Update the container
        current_selected_ids = [compound.split()[0] for compound in selected_compounds]
    else:
        # Convert current selection to text format
        default_text = "\n".join([comp.split()[0] for comp in selected_compounds_container])
        user_input = st.text_area(
            "의약품 성분 ID 입력 (한 줄에 하나씩)",
            value=default_text
        )
        current_selected_ids = [id.strip() for id in user_input.split('\n') if id.strip()]

    # Show current selection
    st.write("현재 선택된 성분 ID:", ", ".join(current_selected_ids))

    if st.button("엑셀 파일을 생성합니다."):
        if current_selected_ids:
            wb = generate_drug_info_sheet(current_selected_ids, variables)
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

    st.markdown("---")
    # HTML/CSS를 사용하여 footer 스타일링
    footer_html = """
    <div style="margin-top: 2rem; padding-top: 2rem; border-top: 1px solid #e5e7eb; text-align: center;">
        <div style="margin-bottom: 1.5rem;">
            <h3 style="font-size: 1.2rem; font-weight: 600; color: #1f2937; margin-bottom: 1rem;">개발자 정보</h3>
            <div style="margin-bottom: 0.5rem;">
                <a href="https://scholar.google.co.kr/citations?hl=ko&user=z0_92iQAAAAJ" target="_blank" style="color: #2563eb; text-decoration: none;">김수환</a>
                <span style="color: #4b5563; margin-left: 0.5rem;">경상국립대학교 정보통계학과</span>
            </div>
            <div>
                <a href="https://siunkim.weebly.com/" target="_blank" style="color: #2563eb; text-decoration: none;">김시언</a>
                <span style="color: #4b5563; margin-left: 0.5rem;">서울대학교병원 의생명연구원</span>
            </div>
        </div>
        <div style="font-size: 0.875rem; color: #4b5563;">
            <p>버전 0.1</p>
            <p style="margin-top: 0.5rem;">
                본 프로그램은 2003년 2월 26일부터 2024년 9월 1일까지의<br>
                건강보험심사평가원 약제급여목록 및 급여 상한 금액표 정보를 참고하였습니다.
            </p>
        </div>
    </div>
    """
    st.markdown(footer_html, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
