# keywords/keyword_registry.py
KEYWORD_MAP = {
    # keyword:        (source_class,     method_name,           targets,                         required)
    "navigate":        ("common",  "navigate",       {""},                              {"data"}),
    "setText":         ("common",  "set_text",       None,  # None = chấp nhận mọi target hợp lệ
                                                              {"target", "data"}),
    "clickElement":    ("common",  "click_element",  None,                              {"target"}),

    "verifyBmiValue":  ("bmi",     "verify_bmi_value",     {"bmi.value"},               {"target", "expected"}),
    "verifyLoginError":("login",   "verify_login_error",   {"login.error_message"},     {"target", "expected"}),
    "verifyCartTotal": ("cart",    "verify_cart_total",    {"cart.total"},              {"target", "expected"}),
}

class KeywordRegistry:
    def resolve(self, keyword):
        if keyword not in KEYWORD_MAP:
            raise KeyError(keyword)
        return KEYWORD_MAP[keyword]  # (source_class, method_name, targets, required)

registry = KeywordRegistry()

#đây chỉ là demo 