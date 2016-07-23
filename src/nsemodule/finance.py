from bs4 import BeautifulSoup
import requests
import config
import sys
import json
import six
import code
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

  def get_finance_params(self, symbol, companyName = None):
    fetch_url = self.generate_fin_data_url(symbol)
    status = fetch_url['status']
    if status != 200:
      fetch_url = self.generate_fin_data_url(symbol, companyName)
      status = fetch_url['status']
    if status == 200:
      fin_url = fetch_url['response']['mc_url']
      r = requests.get(fin_url)
      status = r.status_code
      if r.status_code == 200:
        standalone = self.parse_data_mc_company_page(r.text, "mktdet_1", "mktdet_1")
        consolidated = self.parse_data_mc_company_page(r.text, "mktdet_2", "mktdet_2")
        response = {"standalone": standalone, "consolidated": consolidated }
      else:
        response = "Unable to get reponse from MC for {0},{1}".format(symbol,companyName)
    else:
      response = "URL Generate error: {0} ".format(fetch_url['response'])
     
    return {"response": response, "status": status}

  def parse_data_mc_company_page(self, htmltext, div_id, div_name):
    target_div = BeautifulSoup(htmltext,"html.parser").find('div',attrs = {"id":div_id,"name":div_name})
    response = None
    if target_div != None:
      values_div = target_div.find_all('div',attrs={"class":"PA7 brdb"})
      params = []
      if values_div != None:
        for div in values_div:
          key_div = div.find('div',attrs={"class":"FL gL_10 UC"})
          value_div = div.find('div',attrs={"class":"FR gD_12"})
          try:
            key = key_div.contents[0].lower()
          except:
            if len(key_div.contents) == 2:
              key = key_div.contents[1].lower()
            else:
              key = None
          try:
            value = value_div.contents[0].replace(',','')
          except:
            value = None 
          params.append([key,value])
      response = self.map_fin_params_data(params)
    return response

  def map_fin_params_data(self,params):
    fparams = { 'market_cap' : None, 'p_by_e' : None, 'book_value' : None,
      'div_perc' : None, 'industry_p_by_e' : None,'eps' : None, 
      'price_by_book' : None, 'div_yield_perc' : None, 'put_by_call' : None}
    for x in xrange(len(params)):
      if re.match('market\scap[\w]*',params[x][0]) != None:
        if params[x][1] != None and re.match('[\d.]+',params[x][1]):
          fparams['market_cap'] = float(params[x][1])
      elif re.match('p\/e[\w]*',params[x][0]) != None:
        if params[x][1] != None and re.match('[\d.]+',params[x][1]):
          fparams['p_by_e'] = float(params[x][1])
      elif re.match('book\svalue[\w]*',params[x][0]) != None:
        if params[x][1] != None and re.match('[\d.]+',params[x][1]):
          fparams['book_value'] = float(params[x][1])
      elif re.match('div\s\(\%\)[\w]*',params[x][0]) != None:
        if params[x][1] != None and re.match('[\d.]+',params[x][1].replace('%','')):
          fparams['div_perc'] = float(params[x][1].replace('%',''))
      elif re.match('industry\sp\/e[\w]*',params[x][0]) != None:
        if params[x][1] != None and re.match('[\d.]+',params[x][1]):
          fparams['industry_p_by_e'] = float(params[x][1])
      elif re.match('eps[\w]*',params[x][0]) != None:
        if params[x][1] != None and re.match('[\d.]+',params[x][1]):
          fparams['eps'] = float(params[x][1])
      elif re.match('price\/book[\w]*',params[x][0]) != None:
        if params[x][1] != None and re.match('[\d.]+',params[x][1]):
          fparams['price_by_book'] = float(params[x][1])
      elif re.match('div\syield[\w]*',params[x][0]) != None:
        if params[x][1] != None and re.match('[\d.]+',params[x][1].replace('%','')):
          fparams['div_yield_perc'] = float(params[x][1].replace('%',''))
      elif re.match('p\/c[\w]*',params[x][0]) != None:
        if params[x][1] != None and re.match('[\d.]+',params[x][1]):
          fparams['put_by_call'] = float(params[x][1])
      else:
        pass
    return fparams 

  def generate_fin_data_url(self,symbol,companyName = None):
    if companyName is not None:
      company_name = companyName.replace('&','and').lower().replace('limited','').replace('ltd','')
      autosuggest_url = config.mc['autosuggest'].format(company_name)
    else:
      autosuggest_url = config.mc['autosuggest'].format(symbol)
    
    r_suggestion = requests.get(autosuggest_url)
    if r_suggestion.status_code == 200 and len(r_suggestion.text) > 1:
      suggest_dict = json.loads(r_suggestion.text[1:-1])
      if suggest_dict[0][config.mc['suggest_parser']['info']] != config.mc['suggest_parser']['no_suggest'] :
        # Company which is listed on BSE & NSE will have format of (name,nse_symbol,bse_code)
        # For those which are listed only on NSE, the format will be (name <some code>,nse_symbol)
        found = None
        for s in suggest_dict:
          # Case BSE & NSE listed companies - list will have 3 entities
          # Case NSE listed companies - list will have 2 entities
          info_text = re.sub('[^\w\&,\s]+','',BeautifulSoup(s[config.mc['suggest_parser']['info']],"html.parser").text)
          info_list = info_text.split(",")
          if len(info_list) in [ 2, 3 ]:
            if info_list[1].strip().upper() == re.sub('[^\w\&,\s]+','',symbol.upper()):
              url = urlparse(s[config.mc['suggest_parser']['url']])
              try:
                path_list = url.path.split('/')
                response = {"symbol": path_list[-1],"name":path_list[-2],'url': config.mc['balancesheet'].format(path_list[-2],path_list[-1]),'mc_url': s[config.mc['suggest_parser']['url']]}
                status = 200
                found = True
                break
              except:
                response = " Unable to parse url for {0},{1}".format(symbol, companyName)
                status = 422
        
        if found == None:
          response = "Not able to find {0}".format(symbol)
          status = 204
      else:
        response = "Unexpeceted format received for {0},{1}".format(symbol, companyName)
        status = 204
    else:
      response = "Unable to get response from Autosuggest URL for {0},{1} ".format(symbol,companyName)
      status = 404

    return {'response': response,'status': status }
