import re
s = "It's a good good day"
print(re.sub(r'(\b\w+\b)\1', r'\1', s))