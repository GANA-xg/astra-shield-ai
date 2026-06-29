from .detector import detect_scam


sample = """
Hello Sir.

Your bank account has been blocked.

Please share your OTP immediately.

Otherwise your account will be permanently suspended.

Click the following link.
"""

result = detect_scam(sample)

print(result)