# NSE URLs used to fetch data 

config = {
  'live_stock_url': 'https://nseindia.com/live_market/dynaContent/live_watch/get_quote/ajaxGetQuoteJSON.jsp',
  'index_url': 'https://www.nseindia.com/live_market/dynaContent/live_watch/stock_watch/liveIndexWatchData.json',
  'all_top_gainers_url': 'https://www.nseindia.com/live_market/dynaContent/live_analysis/gainers/allTopGainers1.json',
  'nifty_top_gainers_url': 'https://www.nseindia.com/live_market/dynaContent/live_analysis/gainers/niftyGainers1.json',
  'nifty_top_losers_url': 'https://www.nseindia.com/live_market/dynaContent/live_analysis/losers/niftyLosers1.json',
  'all_top_losers_url': 'https://www.nseindia.com/live_market/dynaContent/live_analysis/losers/allTopLosers1.json'
}
error_msg = {
  "422": "Unprocessable Entity",
  "404":"Unable to fetch data",
  "400":"Bad requests",
  "204": "No content"
}
mc = {
  "autosuggest": "http://www.moneycontrol.com/mccode/common/autosuggesion.php?query={0}&type=1&format=json",
  "balancesheet": "http://www.moneycontrol.com/financials/{0}/balance-sheetVI/{1}#{1}",
  "suggest_parser" : {
    "url": "link_src",
    "info": "pdt_dis_nm",
    "no_suggest": "<B>No Matches - Search Suggestions</B>"
  }
}