import json
import requests
from config import config,error_msg
import six
from math import ceil
import re
from bs4 import BeautifulSoup

if six.PY2:
    from urllib import urlencode
elif six.PY3:
    from urllib.parse import urlencode

class Nse():

  def __init__(self):
    pass

  def get_equity_quotes(self,stocks_symbols,fields = None):
    response = []
    status = None
    N = len(stocks_symbols)
    n_batches = int(ceil(N/5.0)) 
    for batch in xrange(n_batches):
      i,j = 5*batch, min(5*(batch+1),N) 
      r = self.get_equity_quotes_batch(stocks_symbols[i:j],fields)
      status = r['status']
      if r['status']  == 200:
        response+=r['response']  
      else:
        response = r['response']

    return {"response": response, "status": status}

  def get_equity_quotes_batch(self,stocks_symbols,fields = None):
    '''
    Warning: NSE allows fetching data of stocks only 5 at a time.
    '''
    response = None
    status = None
    keys = ['']
    try:
      # Encode Params
      symbols = ''
      for symbol in stocks_symbols:
        symbols+=symbol+','
      params = urlencode({'symbol': symbols, 'series': 'EQ'})
      url = config['live_stock_url'] + "?" + params 
      # Make requests
      r = requests.get(url)
      if r.status_code == 200:
        status = r.status_code
        quotes = []
        try:
          stocks_data = r.json()["data"]
          if fields == None:
            for data in stocks_data:
              quotes.append(self.format_data(data))
          else:
            for data in stocks_data:
              cleaned_data = {k:v for k,v in data.iteritems() if k in fields}
              quotes.append(self.format_data(cleaned_data))
          status = 200
          response = quotes[:] 
        except:
          status = 422
          response = error_msg['422']
      else:
        status = r.status_code
        response = error_msg['404']
    except:
      status = 400
      response = error_msg['400']
    
    return {"response": response, "status": status}

  def fetch_ipo_info(self, year = None):
    response = None
    status = None
    r = requests.get("https://www.nseindia.com/products/content/equities/ipos/ipo_current.htm")

    if r.status_code == 200:
      try:
        table_data = [[cell.text for cell in row('td')] for row in BeautifulSoup(r.text)("tr")]
        ipo_details = [{table_data[0][i]:issue[i] for i in xrange(len(issue))} for issue in table_data[1:]]
        response = json.dumps(ipo_details)
        status = 200
      except:
        status = 422
        response = error_msg['422']
    else:
      status = r.status_code

    return {"response": response, "status": status}

  def get_indices(self,indices = None):
    response = None
    status = None
    try: 
      # Make requests
      r = requests.get(config['index_url'])
      if r.status_code == 200:
        status = r.status_code
        indices_data = []
        try:
          data = r.json()["data"]
          if indices == None:
            for index in data:
              indices_data.append(self.format_data(index))
          else:
            for index in data:
              if index["name"] in indices:
                # Remove Image File Name key from response
                del index["imgFileName"]
                indices_data.append(self.format_data(index))
          status = 200
          response = indices_data[:] 
        except:
          status = 422
          response = error_msg['422']
      else:
        status = r.status_code
        response = error_msg['404']
    except:
      status = 400
      response = error_msg['400']
    
    return {"response": response, "status": status}

  def verify_stock_symbol(self,symbol):
    result = self.get_equity_quotes([symbol])
    if result['status'] == 200:
      if len(result['response']) == 1:
        return True
      else:
        return False
    else:
      return None

  def top_gainers(self,size = 3, fields = None):
    r_nifty = requests.get(config['nifty_top_gainers_url'])
    r_all = requests.get(config['all_top_gainers_url'])
    return self.get_data_for_top_movers(r_nifty,r_all,size,fields)
    
  def top_loosers(self,size = 3, fields = None):
    r_nifty = requests.get(config['nifty_top_losers_url'])
    r_all = requests.get(config['all_top_losers_url'])
    return self.get_data_for_top_movers(r_nifty,r_all,size,fields)

  def get_data_for_top_movers(self,r_nifty_50, r_all, size = 3, fields = None):
    response = {"nifty": None, "all": None}
    status = {"nifty": None, "all": None}

    if r_nifty_50.status_code == 200 :
      status['nifty'], response['nifty'] = self.extract_data_for_top_movers(r_nifty_50,size,fields)
    else:
      status['nifty'], response['nifty'] = 400, error_msg['400']

    if r_all.status_code == 200 :
      status['all'], response['all'] = self.extract_data_for_top_movers(r_all,size,fields)
    else:
      status['all'], response['all'] = 400, error_msg['400']

    return {"response": response, "status": status}

  def extract_data_for_top_movers(self,response_text,size = 3, fields = None):
    response = None
    status = None
    filtered_data = []
    if(type(size) != int):
      return error_msg['422'],422
    try:
      data = response_text.json()["data"]
      if fields == None:
        for entity in data[0:size]:
          filtered_data.append(entity)
      else:
        for entity in data[0:size]:
          cleaned_data = {k:v for k,v in entity.iteritems() if k in fields}
          filtered_data.append(cleaned_data)
      status = 200
      response = filtered_data[:] 
    except:
      status = 422
      response = error_msg['422']
    return response,status

  def format_data(self,input_dict):
    output_dict = {}
    for k,v in input_dict.iteritems():
      if re.match(r'^[\d]+.[\d]+$', v) == None:
        output_dict[k] = v
      else:
        output_dict[k] = float(v)
    return output_dict