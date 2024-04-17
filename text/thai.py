import re
import unicodedata

from num2words import num2words
from pythainlp.transliterate import transliterate
from pythainlp.tokenize import word_tokenize

_ALPHASYMBOL_YOMI = {
    'a': 'เอ',
    'b':'บี',
    'c':'ซี',
    'd':'ดี',
    'e':'อี',
    'f':'เอฟ',
    'g':'จี',
    'h':'เอช',
    'i':'ไอ',
    'j':'เจ',
    'k':'เค',
    'l':'แอล',
    'm':'เอ็ม',
    'n':'เอ็น',
    'o':'โอ',
    'p':'พี',
    'q':'คิว',
    'r':'แอร์',
    's':'เอส',
    't':'ที',
    'u':'ยู',
    'v':'วี',
    'w':'ดับเบิลยู',
    'x':'เอ็กซ์',
    'y':'วาย',
    'z':'ซี'
}


_NUMBER_WITH_SEPARATOR_RX = re.compile("[0-9]{1,3}(,[0-9]{3})+")
_CURRENCY_MAP = {"$": "ดอลล่า", "¥": "เยน", "£": "ปอนด์", "€": "ยูโร", "฿": "บาท"}
_CURRENCY_RX = re.compile(r"([$¥£€])([0-9.]*[0-9])")
_NUMBER_RX = re.compile(r"[0-9]+(\.[0-9]+)?")


def thai_convert_numbers_to_words(text: str) -> str:
    res = _NUMBER_WITH_SEPARATOR_RX.sub(lambda m: m[0].replace(",", ""), text)
    res = _CURRENCY_RX.sub(lambda m: m[2] + _CURRENCY_MAP.get(m[1], m[1]), res)
    res = _NUMBER_RX.sub(lambda m: num2words(m[0], lang="th"), res)
    return res


def thai_convert_alpha_symbols_to_words(text: str) -> str:
    return "".join([_ALPHASYMBOL_YOMI.get(ch, ch) for ch in text.lower()])

def thai2phones(text: str) -> str:
    phones = ""
    if "ๆ" in text:
        words = maiyamok(text, "attacut")
    else:
        words = word_tokenize(text, engine="attacut")
    for word in words:
        result = " "
        special_characters = "\"!@#$%^&*()-+?_=,<>/\"'.:;~‘’“” "
        targetWord = remove_all_character(word.strip(), special_characters)
        if targetWord and targetWord not in special_characters:
            try:
                result = transliterate(clean_with_dict(targetWord, special_characters), "tltk_ipa")
            except:
                print(text, ":", word)
                raise Exception("Shit")
        elif word == " ":
            result = " "
        elif targetWord in special_characters:
            result = targetWord
        phones += result
    return phones

def maiyamok(sent, engine):
    if isinstance(sent, str):
        sent = word_tokenize(sent, engine=engine)
    _list_word = []
    i = 0
    for j, text in enumerate(sent):
        if text.isspace() and "ๆ" in sent[j + 1]:
            continue
        if " ๆ" in text:
            text = text.replace(" ๆ", "ๆ")
        if "ๆ" == text:
            text = _list_word[i - 1]
        elif "ๆ" in text:
            text = text.replace("ๆ", "")
            _list_word.append(text)
            i += 1
        _list_word.append(text)
        i += 1
    return _list_word

def remove_all_character(word, special_characters):
    newWorld = word
    for c in special_characters:
        newWorld = newWorld.replace(c, "")
    return newWorld

def clean_with_dict(text, special_characters):
    new_text = text
    for s in special_characters:
        new_text = new_text.replace(s, "")
    return new_text

def replace_tone(text):
    tones = {
        ("c","ç"),
        ("ᴐ","ɔ"),
        ("r","ɹ"),
        ("ɤ","g"),
        ("1", "→"),
        ("2", "↑"),
        ("3", "↓"),
        ("4", "↓↑"),
        ("5", " "),
        ("ː", "ˈ"),
        (".", "*"),
        ("ʔ", "ɑ*")
    }

    for t in tones:
        text = text.replace(t[0], t[1])
    return text

def thai_text_to_phonemes(text: str) -> str:
    """Convert thai text to phonemes."""
    # res = unicodedata.normalize("NFKC", text)
    res = text.strip()
    res = thai_convert_numbers_to_words(res)
    res = thai_convert_alpha_symbols_to_words(res)
    res = thai2phones(res)
    res = replace_tone(res)
    # res = transliterate(res, engine="icu")
    return res
