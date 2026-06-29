from agents.phishing_agent.url_analyzer import analyze_url

result = analyze_url("http://testsafebrowsing.appspot.com/s/phishing.html")

from pprint import pprint
pprint(result)