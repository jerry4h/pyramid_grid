
def cal_linear(p_min, p_max, p_now):
    price_ratio = (p_now - p_min) / (p_max - p_min)
    return price_ratio

def predict_linear(p_min, p_max, ratio):
    return p_min + (p_max - p_min) * ratio

standard_buy_price_position = [
    [1.00, 0.00],
    [0.61, 0.10],
    [0.37, 0.30],
    [0.17, 0.60],
    [0.00, 1.00]
]

def show_price_position(p_min, p_max, price_table):
    print("show_price_position:")
    for (price_ratio, position) in price_table:
        price = predict_linear(p_min, p_max, price_ratio)
        print(f"\tprice: {price:.3f}, position: {position:.3f}")

def cal_buy_position(p_min, p_max, p_now):
    show_price_position(p_min, p_max, standard_buy_price_position)
    price_ratio = cal_linear(p_min, p_max, p_now)
    print(f"price_ratio: {price_ratio:.3f}")
    index = 0
    
    for price_position in standard_buy_price_position:
        price, position = price_position
        if price_ratio > price:
            break
        index += 1
    
    sub_price_ratio = cal_linear(
        standard_buy_price_position[index-1][0],
        standard_buy_price_position[index][0],
        price_ratio
    )
    print(f"sub_price_ratio: {sub_price_ratio:.3f}")
    position = predict_linear(
        standard_buy_price_position[index-1][1],
        standard_buy_price_position[index][1],
        sub_price_ratio
    )
    print(f"position: {position:.3f}")
    return position

if __name__ == "__main__":
    buy_position_ratio = cal_buy_position(4.80, 7.06, 5.02)
