from agents.currency_agent.service import analyze_currency

IMAGE_PATH = (
    r"C:\Users\aarya\OneDrive\Desktop\Ai Astra"
    r"\currency-research\datasets\test\genuine\500_s4.jpg"
)

result = analyze_currency(IMAGE_PATH)

print(result)