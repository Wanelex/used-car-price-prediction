def score_to_text(cls):
    messages = {
        0: "The car is significantly below market value. It may have issues or require major repairs.",
        1: "The car is in the low-price range. It might be a good deal, but should be inspected carefully.",
        2: "The car is in the average price range. It is fairly priced according to the market.",
        3: "The car is in a good price range. Considering its price-performance ratio, it may be worth buying.",
        4: "The car is in an excellent price range! It is below the market average — a potential opportunity."
    }
    return messages.get(cls, "Unknown class")
