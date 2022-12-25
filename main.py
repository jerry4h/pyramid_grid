import pandas as pd


def cal_linear(p_min, p_max, p_now):
    price_ratio = (p_now - p_min) / (p_max - p_min)
    return price_ratio

def predict_linear(p_min, p_max, ratio):
    return p_min + (p_max - p_min) * ratio

standard_buy_price_position = [
    [1.000, 0.00],
    [0.800, 0.10],
    [0.680, 0.30],
    [0.578, 0.60],
    [0.491, 1.00]
]

standard_sell_price_position = [
    [1.037, 0.00],
    [0.864, 0.40],
    [0.720, 0.70],
    [0.600, 0.90],
    [0.500, 1.00]
]

def cal_buy_price_position(p_min, p_max, buy_price_table, out_table):
    """
    p_min: 0.5, p_max: 1.0
    """
    # standard price to real price translator
    scale = (p_max - p_min) / (1 - 0.5)
    for (price_std, position) in buy_price_table:
        price = p_max - (1.0 - price_std) * scale
        out_table.append([price, position])

def cal_sell_price_position(p_min, p_max, sell_price_table, out_table):
    """
    p_min: 0.5, p_max: 1.0
    """
    # standard price to real price translator
    scale = (p_max - p_min) / (1 - 0.5)
    for (price_std, position) in sell_price_table:
        price = p_min + (price_std - 0.5) * scale
        out_table.append([price, position])


class Choice:
    def __init__(self, p_min, p_max, pos_max, code=""):
        self.p_min = p_min
        self.p_max = p_max
        self.pos_max = pos_max
        self.code = code
        self.buy_table = []
        self.sell_table = []
        cal_buy_price_position(p_min, p_max, standard_buy_price_position, self.buy_table)
        cal_sell_price_position(p_min, p_max, standard_sell_price_position, self.sell_table)
        print(f"{self.code}: buy_price_position")
        for (price, position) in self.buy_table:
            print(f"\tprice: {price:.3f}, position: {position:.3f}")
        print(f"{self.code}: sell_price_position")
        for (price, position) in self.sell_table:
            print(f"\tprice: {price:.3f}, position: {position:.3f}")
    
    def cal_position(self, price, is_buy=True):
        table = self.buy_table if is_buy else self.sell_table
        if price > table[0][0] or price < table[-1][0]:
            print(f"{self.code} price {price:.3f} out range: [{table[-1][0]:.3f}, {table[0][0]:.3f}]")
            exit(-1)
        
        index = 0
        for price_unique, position in table:
            # TODO: bug exist, for price = self.p_min, index out of range
            if price > price_unique:
                break
            index += 1
        sub_price_ratio = cal_linear(table[index-1][0], table[index][0], price)
        position = predict_linear(table[index-1][1], table[index][1], sub_price_ratio)

        return position
        
    def cal_price_position_distribute(self):
        prices = []
        pos_rate_long = []
        pos_rate_short = []
        pos_long = []
        pos_short = []
        price = self.p_min+0.001
        while price <= self.p_max:
            prices.append(price)

            long_rate = self.cal_position(price, is_buy=True)
            pos_rate_long.append(long_rate)
            pos_long.append(int(long_rate * self.pos_max))

            short_rate = self.cal_position(price, is_buy=False)
            pos_rate_short.append(short_rate)
            pos_short.append(int(short_rate * self.pos_max))
            
            price += 0.001
        pd_frame = pd.DataFrame(
            {"rate_long": pos_rate_long, "rate_short": pos_rate_short, "pos_long": pos_long, "pos_short": pos_short},
            index=prices)
        return pd_frame

