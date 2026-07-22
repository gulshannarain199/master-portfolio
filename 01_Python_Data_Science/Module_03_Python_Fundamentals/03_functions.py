# ==============================================================================
# COURSE: IBM Python for Data Science, AI & Development
# MODULE: Module 3 - Python Programming Fundamentals
# TOPIC:  Functions (Modular Code, Arguments, Return Values & Scope)
# ==============================================================================

# Global variable example
PIPELINE_NAME = "ETL_Sales_Ingest"


# --- 1. Basic Function Definition & Positional Arguments ---
def calculate_conversion_rate(clicks, conversions):
    """Calculates conversion percentage given total clicks and conversions."""
    if clicks == 0:
        return 0.0
    rate = (conversions / clicks) * 100
    return round(rate, 2)

print("--- 1. FUNCTION EXECUTION & RETURN VALUES ---")
conv_rate = calculate_conversion_rate(1250, 45)
print(f"Pipeline [{PIPELINE_NAME}] Conversion Rate: {conv_rate}%\n")


# --- 2. Default Parameters & Keyword Arguments ---
def clean_string_data(text, convert_lowercase=True, strip_whitespace=True):
    """Sanitizes incoming string inputs with configurable options."""
    if strip_whitespace:
        text = text.strip()
    if convert_lowercase:
        text = text.lower()
    return text

print("--- 2. DEFAULT & KEYWORD ARGUMENTS ---")
raw_email = "   User_Email@Domain.COM  \n"
# Using keyword arguments for explicit configuration
cleaned_email = clean_string_data(raw_email, convert_lowercase=True)
print(f"Raw Input: '{raw_email}'")
print(f"Cleaned Output: '{cleaned_email}'\n")


# --- 3. Flexible Arguments (*args & **kwargs) ---
def aggregate_metrics(*metrics, **pipeline_meta):
    """
    *args accepts variable positional arguments (tuple)
    **kwargs accepts variable keyword arguments (dictionary)
    """
    total_val = sum(metrics)
    print("--- 3. ADVANCED FUNCTION ARGUMENTS (*args, **kwargs) ---")
    print(f"Pipeline Metadata: {pipeline_meta}")
    print(f"Aggregated Metrics Total: {total_val}")
    return total_val

# Calling with arbitrary numbers of arguments and key-value metadata
total = aggregate_metrics(10.5, 20.2, 15.3, batch_id=1092, environment="Production")