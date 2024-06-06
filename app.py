import streamlit as st
import requests
from streamlit_option_menu import option_menu

st.set_page_config(
    page_title="URL 단축 서비스",
    page_icon="🐶"
)

if "curr_page" not in st.session_state:
    st.session_state["curr_page"] = "URL단축"

st.title("URL 단축 서비스")

# Backend API url
host_url = "http://localhost:8000"
shorten_url = f"{host_url}/shorten"
redirect_url = f"{host_url}/redirect"
access_count_url = f"{host_url}/access_count"

def get_short_key(url, selected_date):
    url_info = {"url": f"{url}", "expiration_date": f"{selected_date}"}
    resp = requests.post(shorten_url, json=url_info)
    assistant_turn = resp.json()
    return assistant_turn

def get_access_count(short_key):
    resp = requests.get(access_count_url+"/"+f"{short_key}")
    return resp.json()

with st.sidebar:
    selected = option_menu("Menu", ["URL단축", 'URL조회'],
        icons=['emoji-smile', 'chat-square-dots'], menu_icon="rocket-takeoff", default_index=0)
    st.session_state["curr_page"] = selected

if st.session_state["curr_page"] == "URL단축":
    st.subheader("URL 단축하기")
    input_url = st.text_input("단축할 URL을 입력하세요.")
    selected_date = st.date_input('삭제 날짜')
    button = st.button('단축하기!')
    if button:
        if input_url != '':
            # url앞부분 https 제거 및 정제
            input_url = input_url.replace("https://","").replace("http://","")
            resp_text = get_short_key(input_url, selected_date)
            st.toast("단축 성공하였습니다!", icon='👏🏻')
            st.divider()
            st.write("단축된 URL⬇︎")
            st.write(f"{redirect_url}/{resp_text['short_key']}")
            st.divider()
            st.write("Response JSON⬇︎")
            st.caption(f"{resp_text}")
            st.divider()
            st.write(f"{selected_date}에 단축된 해당 URL이 삭제(만료)됩니다.😀")
        else:
            st.write(f"URL을 입력해주세요.")

elif st.session_state["curr_page"] == "URL조회":
    st.subheader("URL 조회 수 확인하기")
    input_url1 = st.text_input("조회 수를 확인할 URL 또는 short_key를 입력하세요")
    button1 = st.button('조회 수 확인!')
    if button1:
        if input_url1 != '':
            # url 뒷부분 short_key만 추출
            short_key = input_url1.split('/')[-1]
            access_count = get_access_count(short_key)
            if access_count == None:
                st.toast("해당 URL은 없습니다.", icon='🙁')
                st.write("해당 URL은 존재하지 않아 조회 수를 표시할 수 없습니다.")
            else:
                st.write(f"현재까지 URL조회 수 ⇨ {access_count}")
        else:
            st.write(f"URL을 입력해주세요.")