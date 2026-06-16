import re

def check_password(password):
    if len(password) < 6 or len(password) > 12:
        return False
    
    if not re.search(r'[a-z]', password):
        return False
    
    if not re.search(r'[A-Z]', password):
        return False
    
    if not re.search(r'[0-9]', password):
        return False
    
    if not re.search(r'[$#@]', password):
        return False
    
    return True

user_input = input("请输入要验证的密码（用逗号分隔）：")
passwords = [p for p in user_input.split(',')]
valid_passwords = [p for p in passwords if check_password(p)]
print("有效密码：" + ','.join(valid_passwords))  