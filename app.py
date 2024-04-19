import streamlit as st
import yfinance as yf
from streamlit_option_menu import option_menu
from st_keyup import st_keyup
import json

######################################
############# OTHER SETUP ############
######################################
@st.cache
def load_config(filename:str):
    with open(filename, 'r') as f:
        return json.load(f)

attributes = load_config('attributes_config.json')

### Wording ###
wording_main_title = "Company Data Retrieval Dashboard"
wording_main_description = "Welcome we've built the Company Data Retrieval Dashboard to help get open-source public data downloaded in a normalized way. This intuitive interface empowers users to effortlessly extract vital financial information from ***SEC filings*** and ***Yahoo Finance***. To ensure seamless navigation, please adhere to the guidelines of each section."


######################################
############ GUI DASHBOARD ###########
######################################

######### GUI | IMPORT PACKAGES #########
import streamlit as st
import yfinance as yf
from streamlit_option_menu import option_menu
from st_keyup import st_keyup

######### GUI | FUNCTIONS ##############
### Group attributes by category Function
def sort_attributes_by_category(attributes):
  attributes_by_category = {}
  for attr, config in attributes.items():
      category = config['category']
      if category not in attributes_by_category:
          attributes_by_category[category] = []
      attributes_by_category[category].append(attr)
  return attributes_by_category

######### GUI | MAIN ###############
### Page Config ###
st.set_page_config(
    page_title="Dashboard • Company Data",
    page_icon="📊",
    layout="wide",
    #initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'mailto:info@blad.cloud',
        'Report a bug': "https://github.com/TheAtu/company-data-dashboard/bug",
        'About': "# This is a GUI dashboard integrating SEC filings and Yahoo Finance with Streamlit for the UI. The original intention fo the code is for trading comps, however its open to use. For more details, incluiding the licensing, visit the [Github Repo](https://github.com/TheAtu/company-data-dashboard)"
    }
)

### Main Title ###
st.sidebar.title(f'{wording_main_title}')
st.sidebar.markdown(wording_main_description)

### INPUT ###
STRING = ''
input_method_selected = ''
with st.sidebar.expander('INPUT', expanded=True):
    st.caption('Explain how this works')

    input_type_selected = option_menu(
        'Type', ['Company Names', 'Share Tickers', 'Mixed'],
        icons=['buildings','graph-up', 'shuffle'], menu_icon='input',
        default_index=2,
        orientation='horizontal'
        )

    input_method_selected = option_menu(
        'Method', ['Manual Input', 'Upload File'],
        icons=['pencil-square','upload'], menu_icon='input',
        default_index=0,
        orientation='horizontal'
        )

    if input_method_selected == 'Manual Input':
        STRING = st.text_area("Paste here the list of companies to retrieve their data (Please be consistent with your previous chosen type of input). \n They can be separated by:  comma,  vertical bar,  tab,  space", height=200, max_chars=9999 )
    
    if input_method_selected == 'Upload File':
        uploaded_file = st.file_uploader(
          "Upload the list of companies to retrieve their data (Please be consistent with your previous chosen method)",
          type = ['txt','docx','doc','xlsx','csv'],
          help = "Filtypes accepted: '.txt','.docx','.doc','.xlsx','.csv' ",
          disabled = False if input_method_selected is not None else True
          )
        if uploaded_file is not None:
            # To read file as string:
            STRING = stringio.read()
            st.write(STRING)

            # Can be used wherever a "file-like" object is accepted:
            dataframe = pd.read_csv(uploaded_file)
            st.write(dataframe)

### CONTENT ###
with st.sidebar.expander('CONTENT', expanded=True):
  # Group attributes by category
  attributes_by_category = sort_attributes_by_category(attributes)

  # Create multiselect for each category
  selected_attributes = []
  for category, attrs in attributes_by_category.items():
      selected_attrs = st.multiselect(f"{category.upper()} - select attributes for the cattegory", attrs)
      selected_attributes.extend(selected_attrs)

  # Display selected attributes
  st.write("Selected Attributes:", selected_attributes)

### OUTPUT ###

with st.sidebar.expander('OUTPUT', expanded=True):
    st.caption('A caption with _italics_ :blue[colors] and emojis :sunglasses:')

    output_col1, output_col2 = st.columns(2)
    with output_col1:
      output_filename = st_keyup("", value="Example", debounce=500 )
    with output_col2:
      output_extension = option_menu(None, ['.xlsx', '.csv','.txt'],
        default_index=1,
        orientation='horizontal',
        styles={
          "container": {"margin-top":"20px" },
          "nav": {"height":"60px","border-radius":"50%"},
          "icon":{"display":"none"},
        }
        )
#####
from streamlit_sortables import sort_items

#sorted_items = 
sorted_selected_attributes = sort_items(selected_attributes)

st.write(f'original_items: {selected_attributes}')
st.write(f'sorted_items: {sorted_selected_attributes}')
####################################
######## MAIN FUNCTIONALITY ########
####################################

######### IMPORT PACKAGES #########
import yfinance as yf
from detect_delimiter import detect
import requests
import pandas as pd

######### FUNCTIONS #########
### Company Source Separator Funciton
def separator(STRING=str):
  delimiter = detect(STRING)

  if detect(STRING) == None:
    newlines_split = STRING.split("\n")
    if len(newlines_split) > 0:
      delimiter = "\n"
    else:
      delimiter = "____There_Is_No_Delimiter_Knwon_____"

  companies = list(map(str.strip, STRING.split(delimiter)))

  return companies

### Get Stock Symbol Funciton
def get_stock_symbol(company_name):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }

        # Construct the URL for Yahoo Finance's symbol search API
        url = f"https://query1.finance.yahoo.com/v1/finance/search?q={company_name}&quotesCount=1&newsCount=0"

        # Send a GET request to the API with the user-agent header
        response = requests.get(url, headers=headers)

        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()

            # Check if there are any quotes (stock symbols) in the response
            if 'quotes' in data and len(data['quotes']) > 0:
                # Get the stock symbol from the first result
                symbol = data['quotes'][0]['symbol']
                return symbol
            else:
                print(f"No stock symbol found for '{company_name}'.")
                return None
        else:
            print("Failed to fetch data from Yahoo Finance API.")
            return None
    except Exception as e:
        print("Error:", e)
        return None

### Get Ticker Data Function
def ticker_data(symbol, selected_attributes):
  try:
    company = yf.Ticker(symbol)
    # global info
    info = company.info
    company_data = {}
    for attribute in selected_attributes:
        config = attributes.get(attribute)
        if config:
            company_data[config['column_name']] = eval(config['fetch_code'])
  except Exception as e:
    company_data = None
    print(f"Error fetching data for symbol {symbol}: {e}")
  return company_data

####### MAIN FUNCTIONALITY ########

## Input
companies = separator(STRING)

## Content
data = {}
if input_method_selected == 'Share Tickers':
    for company in companies:
      company_data = ticker_data(company, selected_attributes)
      data[company] = company_data
if input_method_selected == 'Company Names' | 'Mixed':
    for company in companies:
      company_ticker = get_stock_symbol(company)
      company_data = ticker_data(company_ticker, selected_attributes)
      data[company] = company_data
df = pd.DataFrame(data).T

## Output
#display(df)
st.dataframe(data=df[sorted_selected_attributes], use_container_width=True)