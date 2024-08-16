import requests
import yaml,os,json
import pandas as pd
import streamlit as st

# to lead the config data
_config = {}

def load_config():
    """
    loads the configuration from config.yml
    """
    global _config

    yml_filepath = os.path.dirname(__file__) + '/config.yml'

    with open(yml_filepath,'r') as file:
        _config = yaml.safe_load(file)

def get_config_value(key):
    """
    returns the value of the given configuration key
    """
    global _config

    if _config.get(key) is not None:
        return _config.get(key)
    else:
        load_config()
        return _config.get(key,'key does not exist')



def retrieve_data(ticker):
    """
    returns the data from API if API responds to the request otherwise it will return the data from json files
    """

    url = get_config_value('asx_announcements_url') % ticker.upper()

    response = requests.get(url,headers=get_config_value('headers'))


    try:
        return response.json()['data']
    except:
        # st.write(f'Response Status Code: {response.status_code}')
        # st.write(f'Response from API: \n\n{response.text}')  
        json_filepath = os.path.dirname(__file__) + f'/data/{ticker}.json'
        return json.load(open(json_filepath,'r'))['data']



def main():
    # get the tickers
    tickers = sorted(get_config_value('tickers'))

    # setting up the page
    st.set_page_config(page_title = 'ASX API Data Retrieval', 
                page_icon='📰'
                )
    
    st.title('ASX Announcements')

    # radio button to switch between two tasks
    task_selected = st.radio('',['Announcements','Trading Halt Tickers'])
    
    if task_selected == 'Announcements':

        selected_ticker = st.selectbox("Tickers",tickers)
        data = retrieve_data(selected_ticker)
        
        if data is not None:
            # dictionary to store the data
            announcements = {'title':[],'url':[],'document_release_date':[]}
            for d in data:
                announcements['title'].append(d['header'])
                announcements['url'].append(d['url'])
                announcements['document_release_date'].append(d['document_release_date'])
            
            announcements = pd.DataFrame(announcements)

            # new column to have headers with hyperlink
            announcements[data[0]['issuer_full_name']] = announcements.apply(lambda row: f'<a href="{row["url"]}" target="_blank">{row["title"]}</a>', axis=1)
            announcements['document_release_date'] = pd.to_datetime(announcements['document_release_date']) 
            
            # printing the 20 announcements
            st.markdown(announcements[[data[0]['issuer_full_name'],'document_release_date']].to_html(escape=False, index=False), unsafe_allow_html=True)
    
    else:
        tickers_with_trading_halt = {'ticker':[],'ticker_full_name':[]}
        for ticker in tickers:
            data = retrieve_data(ticker)
            if data is None:
                break
            for d in data:
                if 'Trading Halt'.lower() in d['header'].lower():
                    tickers_with_trading_halt['ticker'].append(ticker)
                    tickers_with_trading_halt['ticker_full_name'].append(d['issuer_full_name'])
                    break
        # printing the tickers with trading halt
        st.write(pd.DataFrame(tickers_with_trading_halt,columns=['Tickers','Ticker\'s Full Name']))



if __name__ == "__main__":
    main()