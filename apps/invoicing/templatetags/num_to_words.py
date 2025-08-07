from django import template
from num2words import num2words

register = template.Library()

@register.filter
def amount_words(value):
    try:
        value = float(value)
        rupees = int(value)
        paise = int(round((value - rupees) * 100))
        if paise:
            return f"{num2words(rupees, lang='en').title()} Rupees And {num2words(paise, lang='en').title()} Paise"
        else:
            return f"{num2words(rupees, lang='en').title()} Rupees Only"
    except Exception:
        return value
