import langid
from opencc import OpenCC # 從 opencc-python-reimplemented 導入

# 初始化 OpenCC 轉換器
# s2t: Simplified Chinese to Traditional Chinese
# t2s: Traditional Chinese to Simplified Chinese
converter_s2t = OpenCC('s2t')
converter_t2s = OpenCC('t2s')

def detect_chinese_variant(text):
    if not text.strip():
        return "Empty or whitespace string"

    # 1. 使用 langid 初步判斷是否為中文
    lang_code, confidence = langid.classify(text)

    if lang_code != 'zh':
        return f"Not Chinese (Detected: {lang_code} with confidence {confidence:.2f})"

    # 2. 使用 opencc 進行繁簡判斷
    text_to_simplified = converter_t2s.convert(text)
    text_to_traditional = converter_s2t.convert(text)

    # 判斷邏輯：
    # is_simplified_dominant: 文本本身與轉換到簡體後的結果一致，且與轉換到繁體後的結果不一致
    # is_traditional_dominant: 文本本身與轉換到繁體後的結果一致，且與轉換到簡體後的結果不一致
    # is_common: 文本轉換到簡體和繁體後，結果都與原文一致 (即所有字元在繁簡體中寫法相同)
    # is_mixed: 文本轉換到簡體和繁體後，結果都與原文不一致 (即包含獨特的簡體字和獨特的繁體字)

    original_is_simplified_form = (text == text_to_simplified)
    original_is_traditional_form = (text == text_to_traditional)

    if original_is_simplified_form and not original_is_traditional_form:
        # 如果 text == text_to_simplified，表示文本中沒有需要從繁轉簡的字元。
        # 如果 text != text_to_traditional，表示文本中有可以從簡轉繁的字元。
        # 這意味著原文主要是簡體，或者至少包含簡體特有字元，而不包含繁體特有字元。
        return f"Simplified Chinese (信心來自 langid: {confidence:.2f})"
    elif not original_is_simplified_form and original_is_traditional_form:
        # 如果 text != text_to_simplified，表示文本中有需要從繁轉簡的字元。
        # 如果 text == text_to_traditional，表示文本中沒有需要從簡轉繁的字元。
        # 這意味著原文主要是繁體，或者至少包含繁體特有字元，而不包含簡體特有字元。
        return f"Traditional Chinese (信心來自 langid: {confidence:.2f})"
    elif original_is_simplified_form and original_is_traditional_form:
        # 如果兩種轉換都和原文一樣，說明所有字元都是繁簡體通用的
        return f"Common Chinese Characters (繁簡通用，信心來自 langid: {confidence:.2f})"
    else: # not original_is_simplified_form and not original_is_traditional_form
        # 如果兩種轉換都和原文不一樣，說明原文中既有簡體特有字，又有繁體特有字
        # 例如："软件龍頭" -> s2t -> "軟體龍頭", t2s -> "软件龙头"
        # 這種情況下，原始文本既不完全是簡體形式，也不完全是繁體形式。
        return f"Mixed Simplified and Traditional Chinese (信心來自 langid: {confidence:.2f})"


# 測試範例
test_strings_variant = [
    "台湾外观可以两个设计合并成一个申请案去申请吗?",
    "中国发明专利需在何时提出实质审查?",
    "什麼是專利權授權登記?應如何辦理?",
    "這是一段繁體中文測試文字，裡面的憂鬱的烏龜。",  # Traditional
    "这是一段简体中文测试文字，里面的忧郁的乌龟。",  # Simplified
    "你好世界",                                 # Common
    "你好世界，Hello World!",                 # Common with English
    "计算机软件工程",                           # Simplified
    "計算機軟體工程",                           # Traditional
    "臺湾与台湾",                               # Mixed (臺 is traditional, 台 is common but often preferred in simplified context for Taiwan)
    "憂郁的烏龜和软件",                         # Mixed
    "English text for testing.",              # English
    "これは日本語のテキストです。",                 # Japanese
    "",                                         # Empty
    "   "                                       # Whitespace
]

print("\n--- Testing with langid + opencc ---")
for text in test_strings_variant:
    result = detect_chinese_variant(text)
    print(f"Text: \"{text}\" -> Result: {result}")