from bs4 import BeautifulSoup
import requests
import config
import sys
import json
import six
import re
if six.PY2:
    from urlparse import urlparse
elif six.PY3:
    from urllib import parse as urlparse

class FinanceData():
  """docstring for FinanceData"""
  def __init__(self):
    pass
    
  def fetchBalanceSheet(self,symbol):
    fetch_url = self.generate_fin_data_url(symbol)
    status = fetch_url['status']
    if status == 200:
      fin_url = fetch_url['response']['url']
      r = requests.get(fin_url)
      if r.status_code == 200:
        try:
          target_div = BeautifulSoup(r.text,"html.parser").find('div',attrs = {'class':"boxBg1"})
          tables = target_div.find_all('table',attrs = {'class': "table4"})
          response = tables[1]
        except:
          print("Unexpected error:", sys.exc_info()[0])
          status = 422
      else:
        status = r.status_code
    if status != 200:
      response = config.error_msg[str(status)]   
    return {"response": response, "status": status}

  def makelist(self,table):
    result = []
    allrows = table.findAll('tr')
    for row in allrows:
      result.append([])
      allcols = row.findAll('td')
      for col in allcols:
        thestrings = [unicode(s) for s in col.findAll(text=True)]
        thetext = ''.join(thestrings)
        result[-1].append(thetext)
    return result

  def get_finance_params(self, symbol):
    fetch_url = self.generate_fin_data_url(symbol)
    status = fetch_url['status']
    if status == 200:
      fin_url = fetch_url['response']['mc_url']
      r = requests.get(fin_url)
      if r.status_code == 200:
        try:
          target_div = BeautifulSoup(r.text,"html.parser").find('div',attrs = {"id":"mktdet_1","name":"mktdet_1"})
          values_div = target_div.find_all('div',attrs={"class":"PA7 brdb"})
          params = []
          for div in values_div:
            key_div = div.find('div',attrs={"class":"FL gL_10 UC"})
            value_div = div.find('div',attrs={"class":"FR gD_12"})
            try:
              key = key_div.contents[0].lower()
            except:
              key = None
            try:
              value = value_div.contents[0].replace(',','')
            except:
              value = None 
            params.append([key,value])
          response = self.map_fin_params_data(params)
        except:
          print("Unexpected error:", sys.exc_info()[0])
          status = 422
      else:
        status = r.status_code
    if status != 200:
      response = config.error_msg[str(status)]   
    return {"response": response, "status": status}

  def map_fin_params_data(self,params):
    fparams = { 'market_cap' : None, 'p_by_e' : None, 'book_value' : None,
      'div_perc' : None, 'industry_p_by_e' : None,'eps' : None, 
      'price_by_book' : None, 'div_yield_perc' : None, 'put_by_call' : None}
    for x in xrange(len(params)):
      if re.match('market\scap[\w]*',params[x][0]) != None:
        if re.match('[\d.]+',params[x][1]):
          fparams['market_cap'] = float(params[x][1])
      elif re.match('p\/e[\w]*',params[x][0]) != None:
        if re.match('[\d.]+',params[x][1]):
          fparams['p_by_e'] = float(params[x][1])
      elif re.match('book\svalue[\w]*',params[x][0]) != None:
        if re.match('[\d.]+',params[x][1]):
          fparams['book_value'] = float(params[x][1])
      elif re.match('div\s\(\%\)[\w]*',params[x][0]) != None:
        if re.match('[\d.]+',params[x][1].replace('%','')):
          fparams['div_perc'] = float(params[x][1].replace('%',''))
      elif re.match('industry\sp\/e[\w]*',params[x][0]) != None:
        if re.match('[\d.]+',params[x][1]):
          fparams['industry_p_by_e'] = float(params[x][1])
      elif re.match('eps[\w]*',params[x][0]) != None:
        if re.match('[\d.]+',params[x][1]):
          fparams['eps'] = float(params[x][1])
      elif re.match('price\/book[\w]*',params[x][0]) != None:
        if re.match('[\d.]+',params[x][1]):
          fparams['price_by_book'] = float(params[x][1])
      elif re.match('div\syield[\w]*',params[x][0]) != None:
        if re.match('[\d.]+',params[x][1].replace('%','')):
          fparams['div_yield_perc'] = float(params[x][1].replace('%',''))
      elif re.match('p\/c[\w]*',params[x][0]) != None:
        if re.match('[\d.]+',params[x][1]):
          fparams['put_by_call'] = float(params[x][1])
      else:
        pass
    return fparams 

  def generate_fin_data_url(self,symbol):
    autosuggest_url = config.mc['autosuggest'].format(symbol)
    try:
      r_suggestion = requests.get(autosuggest_url)
      if r_suggestion.status_code == 200:
        suggest_dict = json.loads(r_suggestion.text[1:-1])
        if suggest_dict[0][config.mc['suggest_parser']['info']] != config.mc['suggest_parser']['no_suggest'] :
          # Company which is listed on BSE & NSE will have format of (name,nse_symbol,bse_code)
          # For those which are listed only on NSE, the format will be (name <some code>,nse_symbol)
          found = None
          for s in suggest_dict:
            info_list = s[config.mc['suggest_parser']['info']].split(",")
            # Case BSE & NSE listed companies - list will have 3 entities
            # Case NSE listed companies - list will have 2 entities
            if len(info_list) in [ 2, 3 ] and BeautifulSoup(info_list[1],"html.parser").text.strip().upper() == symbol.upper():
              url = urlparse(s[config.mc['suggest_parser']['url']])
              try:
                path_list = url.path.split('/')
                response = {"symbol": path_list[-1],"name":path_list[-2],'url': config.mc['balancesheet'].format(path_list[-2],path_list[-1]),'mc_url': s[config.mc['suggest_parser']['url']]}
                status = 200
                found = True
                break
              except:
                status = 422
          
          if found == None:
            status = 204
        else:
          status = 204
      else:
        status = 404
    except:
      print("Unexpected error:", sys.exc_info()[0])
      status = 422
    if status != 200:
        response = config.error_msg[str(status)]
    return {'response': response,'status': status }