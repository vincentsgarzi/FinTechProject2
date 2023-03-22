import streamlit as st

with st.sidebar:
    st.write('Portfolio Builder')

tab1, tab2, tab3 = st.tabs(['About','Portfolios Dashboard','Future Projected Returns'])


with tab1:
    st.title('About')

with tab2:
    st.title('Portfolio Dashboard')

with tab3:
    st.title('Future Projected Returns')