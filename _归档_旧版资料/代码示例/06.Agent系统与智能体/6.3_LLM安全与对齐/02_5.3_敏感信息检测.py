# PII检测模式示例
pii_patterns = {
    "phone": r'1[3-9]\d{9}',                    # 中国手机号
    "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # 邮箱
    "id_card": r'\d{17}[\dXx]',                # 身份证号
    "bank_card": r'\d{16,19}',                 # 银行卡号
}
