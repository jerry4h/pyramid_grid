import math
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

def kdj_to_contrast_diff(d_month, d_week):
    """
    return: 
      risk_level: str, discription
      buy_contrast
      buy_different
      sell_contrast
      sell_different
    """
    if d_month <= 0 or d_month >= 100 or d_week <= 0 or d_week >= 100:
        print(f"error: d_month:{d_month}, d_week:{d_week}")
        exit(-1)

    if d_month < 20:
        if   d_week < 20: return "巨大机会", 0.03, 0.01, 0.05, 0.03
        elif d_week < 30: return "巨大机会", 0.03, 0.013, 0.05, 0.03
        elif d_week < 70: return "巨大机会", 0.03, 0.015, 0.05, 0.03
        elif d_week < 80: return "很大机会", 0.03, 0.02, 0.04, 0.03
        else:             return "很大机会", 0.03, 0.025, 0.04, 0.03
    elif d_month < 30:
        if   d_week < 20: return "巨大机会", 0.03, 0.015, 0.05, 0.03
        elif d_week < 30: return "很大机会", 0.03, 0.018, 0.04, 0.03
        elif d_week < 70: return "很大机会", 0.03, 0.02, 0.04, 0.03
        elif d_week < 80: return "很大机会", 0.03, 0.025, 0.04, 0.025
        else:             return "风险平衡", 0.03, 0.03, 0.03, 0.02
    elif d_month < 40:
        if   d_week < 20: return "很大机会", 0.03, 0.02, 0.04, 0.03 
        else:             return "风险平衡", 0.03, 0.03, 0.03, 0.03
    elif d_month < 60:
        if   d_week < 30: return "很大机会", 0.03, 0.025, 0.04, 0.03
        elif d_week < 70: return "风险平衡", 0.03, 0.03, 0.03, 0.03
        else:             return "很大风险", 0.04, 0.03, 0.03, 0.025
    elif d_month < 70:
        if   d_week < 80: return "风险平衡", 0.03, 0.03, 0.03, 0.03
        else:             return "很大风险", 0.04, 0.03, 0.03, 0.02
    elif d_month < 80:
        if   d_week < 20: return "风险平衡", 0.03, 0.025, 0.03, 0.03
        elif d_week < 30: return "很大风险", 0.04, 0.03, 0.03, 0.025
        elif d_week < 70: return "很大风险", 0.04, 0.03, 0.03, 0.02
        elif d_week < 80: return "很大风险", 0.04, 0.03, 0.03, 0.018
        else:             return "巨大风险", 0.05, 0.03, 0.03, 0.015
    else:
        if   d_week < 20: return "很大风险", 0.04, 0.03, 0.03, 0.025
        elif d_week < 30: return "很大风险", 0.04, 0.03, 0.03, 0.02
        elif d_week < 70: return "巨大风险", 0.05, 0.03, 0.03, 0.015
        elif d_week < 80: return "巨大风险", 0.05, 0.03, 0.03, 0.013
        else:             return "巨大风险", 0.05, 0.03, 0.03, 0.01


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
    def __init__(self, p_min, p_max, pos_max, price, d_month, d_week, code=""):
        # long-term position control
        self.p_min = p_min
        self.p_max = p_max
        self.pos_max = pos_max
        self.code = code
        self.price = price
        self.d_month = d_month
        self.d_week = d_week
        self.buy_table = []
        
        # short-term trade plan
        self.p_now = -1
        self.p_last_buy = -1
        self.p_last_sell = -1
        self.p_last_buy_num = -1
        self.p_last_sell_num = -1
        self.pos_basic = (pos_max / 40) * (math.log(0.5) / math.log(p_min / p_max))
        self.pos_increase_rate = 0.1
        self.pos_decrease_rate = 0.1
        self.sell_table = []
        
        # mid-term risk and grid density
        self.kdj_d_month = -1
        self.kdj_d_week = -1
        self.risk_discription = ""
        self.buy_contrast_rate = -1
        self.buy_difference_rate = -1
        self.sell_contrast_rate = -1
        self.sell_difference_rate = -1
        
        # trade log
        self.log = None
        
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

    def cal_risk_and_grid_density(self, kdj_d_month, kdj_d_week):
        if kdj_d_month <= 0 or kdj_d_month >= 100 or kdj_d_week <= 0 or kdj_d_week >= 100:
            print(f"error: class Choice: cal_risk_and_grid_density: d_month:{kdj_d_month}, d_week:{kdj_d_week}")
            return -1
        risks_and_density = kdj_to_contrast_diff(kdj_d_month, kdj_d_week)
        assert len(risks_and_density) == 5
        self.kdj_d_month = kdj_d_month
        self.kdj_d_week = kdj_d_week
        self.risk_discription = risks_and_density[0]
        self.buy_contrast_rate = risks_and_density[1]
        self.buy_difference_rate = risks_and_density[2]
        self.sell_contrast_rate = risks_and_density[3]
        self.sell_difference_rate = risks_and_density[4]
        return risks_and_density
    
    def cal_pos_number_per_trade(self):
        return self.pos_basic
    
    def add_record(self, date, action, price, count):
        return
    
    def load_record(self, csv_path):
        return
    
    def save_record(self, csv_path):
        return