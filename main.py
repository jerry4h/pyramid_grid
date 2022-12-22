
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
    def __init__(self, p_min, p_max, code=""):
        self.p_min = p_min
        self.p_max = p_max
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
            if price > price_unique:
                break
            index += 1
        sub_price_ratio = cal_linear(table[index-1][0], table[index][0], price)
        position = predict_linear(table[index-1][1], table[index][1], sub_price_ratio)

        return position
        

if __name__ == "__main__":
    zz1000 = Choice(2.073, 3.247, "SH:512100")
    kc50 = Choice(0.848, 1.696, "SH:588000")
    gqhl = Choice(1.820, 2.215, "SH:501059")
    jyyh = Choice(3.67, 5.38, "SZ:002807")
    wxyh = Choice(4.80, 7.06, "SH:600908")
    yyetf = Choice(0.454, 0.907, "SH:512010")
    for choice, price in zip([zz1000, kc50, gqhl, jyyh, wxyh, yyetf], [2.478, 0.971, 1.890, 3.88, 5.02, 0.460]):
        print(f"{choice.code}: price: {price:.3f},\n\t"
              f"buy position: {choice.cal_position(price, True):.3f},\n\t"
              f"sell position: {choice.cal_position(price, False):.3f}")
