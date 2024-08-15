import requests
import json
import pandas as pd
import streamlit as st

def retrieve_data(ticker):
    url = f'https://www.asx.com.au/asx/1/company/{ticker}/announcements?count=20&market_sensitive=false'
    headers = {
        'User-Agent':'Chrome/127.0.0.0 Safari/537.36',
        'Cookie':'JSESSIONID=4ZJKK-odV_4dAfqR_Yx5UUIycrYBnUhY0Gy3Epu7.node204; TS01a6083b=01856a822a79516cb7aff46aa01ccb9a8b86fbf252ebf9b299ac23df55651dbaabb0ef3a9bccd0e9b889ddceeda21b83178696b750; visid_incap_2835827=QlqLfN5iRVSEalIINR8LYQv0vWYAAAAAQUIPAAAAAAAy9FMXvMMID9B94r7UNqXT; affinity="c948963760209d11"; JSESSIONID=.node204; nlbi_2835827_2708396=x+qSQxdQa0aN9OH/2S5TNgAAAABgQaR6oE6TibmoYojbpuls; _gcl_au=1.1.435574352.1723725040; _ga=GA1.1.420937008.1723725040; OptanonAlertBoxClosed=2024-08-15T12:30:47.587Z; _hjSessionUser_3043058=eyJpZCI6Ijg1ZTNlYmU4LTBkOTYtNTdkOC05NGRkLTdmNTExMWVkZmRjMyIsImNyZWF0ZWQiOjE3MjM3MjUwNDgzMDcsImV4aXN0aW5nIjp0cnVlfQ==; __utma=51794233.420937008.1723725040.1723725063.1723725063.1; __utmc=51794233; __utmz=51794233.1723725063.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); AMCVS_FD20401053DA8A4F0A490D4C%40AdobeOrg=1; AMCV_FD20401053DA8A4F0A490D4C%40AdobeOrg=-1758798782%7CMCIDTS%7C19951%7CMCMID%7C60847442457161467392706589270230964248%7CMCAAMLH-1724329862%7C7%7CMCAAMB-1724329863%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1723732263s%7CNONE%7CMCAID%7C3323B8D0A3ADF485-60001E3BE5A813FE; _fbp=fb.2.1723725063364.997626631219154117; s_nr=1723725063439-New; s_cc=true; s_fid=7A5A8B36C867174B-3BDF8BFF5D1347CE; s_cmpid=%7E%7E%7E%7E; s_cpc=1; __gads=ID=97dbb63869120d6a:T=1723725063:RT=1723725063:S=ALNI_MameuldnfrTw5DR2ipPVoZVeI_FgQ; __gpi=UID=00000ecb329f5c36:T=1723725063:RT=1723725063:S=ALNI_MZFOlvcgehJWPjOm8pQ1sftqye-EA; __eoi=ID=163c24e138428b02:T=1723725063:RT=1723725063:S=AA-AfjbTCGl8g5BxDYX6-AH9AEsI; OptanonConsent=isIABGlobal=false&datestamp=Thu+Aug+15+2024+08%3A35%3A59+GMT-0400+(Eastern+Daylight+Time)&version=6.13.0&hosts=&consentId=64e041ba-5d4d-4289-b493-ff112d0b04b0&interactionCount=2&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A1&AwaitingReconsent=false&geolocation=CA%3BON; nlbi_2835827=a670bgsGH13D82Zl2S5TNgAAAAB0tIrB1b+9lTJnOzGbHtsd; _ga_J1L799T374=GS1.1.1723725042.1.1.1723725383.49.0.0; _ga_PMPRR01441=GS1.1.1723725039.1.1.1723725383.0.0.0; incap_ses_1293_2835827=Z3+SUTCDIAzSfNSJxKjxEVb7vWYAAAAA0ALoG5+HHV3oGf6FBkVpPQ==; TS019c39fc=01856a822a786353337bd3164b1e7818f1c1acc56a076e613ff05d2b1b8a8eaae082b11ab7812e1269fbdc7f4418d8c6e14ae5cac7'
    }

    response = requests.get(url,headers=headers)

    if response.status_code == 200:
        st.write(response.text)
        data = response.json()['data']
        return data
    else:
        print(f'request status code: {response.status_code}')


def main():
    tickers = sorted(['AEE','REZ','1AE','1MC','NRZ'])

    st.set_page_config(page_title = 'ASX API Data Retrieval', 
                page_icon='📰'
                )
    
    st.title('ASX Announcements')

    task_selected = st.radio('',['Announcements','Trading Halt Tickers'])

    if task_selected == 'Announcements':

        selected_ticker = st.selectbox("Tickers",tickers)

        data = retrieve_data(selected_ticker)
        ticker_full_name = data[0]['issuer_full_name']
        
        announcements = {'title':[],'url':[],'document_release_date':[],'market_sensitive':[]}
        for d in data:
            announcements['title'].append(d['header'])
            announcements['url'].append(d['url'])
            announcements['document_release_date'].append(d['document_release_date'])
            announcements['market_sensitive'].append(d['market_sensitive'])
        
        announcements = pd.DataFrame(announcements)
        announcements[data[0]['issuer_full_name']] = announcements.apply(lambda row: f'<a href="{row["url"]}" target="_blank">{row["title"]}</a>', axis=1)
        announcements['document_release_date'] = pd.to_datetime(announcements['document_release_date']) 
        st.markdown(announcements[[data[0]['issuer_full_name'],'document_release_date','market_sensitive']].to_html(escape=False, index=False), unsafe_allow_html=True)
    
    else:
        tickers_with_trading_halt = {'ticker':[],'ticker_full_name':[]}
        for ticker in tickers:
            data = retrieve_data(ticker)
            for d in data:
                if 'Trading Halt'.lower() in d['header'].lower():
                    tickers_with_trading_halt['ticker'].append(ticker)
                    tickers_with_trading_halt['ticker_full_name'].append(d['issuer_full_name'])
                    break
        st.write(pd.DataFrame(tickers_with_trading_halt,columns=['Tickers','Ticker\'s Full Name']))



if __name__ == "__main__":
    main()