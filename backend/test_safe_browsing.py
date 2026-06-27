from agents.phishing_agent.safe_browsing import check_google_safe_browsing

# Safe URL
safe_url = "https://google.com"

print("Testing Safe URL...")
print(check_google_safe_browsing(safe_url))
print()

# Google's official phishing test URL
phishing_url = "http://testsafebrowsing.appspot.com/s/phishing.html"

print("Testing Phishing URL...")
print(check_google_safe_browsing(phishing_url))