import streamlit as st
from utils.chatbot import StockChatbot

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "chatbot" not in st.session_state:
    st.session_state.chatbot = StockChatbot()

st.title("Trợ lý AI chứng khoán")


st.title("Trợ lý AI chứng khoán/cổ phiếu")
st.markdown("""
            Chào mừng bạn đến với trợ lý AI chứng khoán!
            Tôi có thể giúp bạn:
            - Phân tích dữ liệu chứng khoán/cổ phiếu
            - Trả lời những câu hỏi về thị trường
            - Đưa ra những gợi ý đầu tư""")


st.header("Chat với AI")



for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
    
if prompt := st.chat_input("Nhập câu hỏi của bạn...", max_chars=1000):
    st.session_state.chat_history.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = st.session_state.chatbot.get_response(prompt)
        st.markdown(response)

        st.session_state.chat_history.append({"role": "assistant", "content": response})


if st.button("Xóa lịch sử chat"):
    st.session_state.chat_history = []
    st.session_state.chatbot.clear_conversation()
    st.rerun()