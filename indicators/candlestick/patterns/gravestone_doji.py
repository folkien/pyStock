from indicators.candlestick.patterns.candlestick_finder import CandlestickFinder


class GravestoneDoji(CandlestickFinder):
    def __init__(self, target=None):
        super().__init__(self.get_class_name(), 1, target=target, type='sell')

    def logic(self, idx):
        candle = self.data.iloc[idx]
        next_candle = self.data.iloc[idx - 1 * self.multi_coeff]

        close = candle[self.close_column]
        open = candle[self.open_column]
        high = candle[self.high_column]
        low = candle[self.low_column]

        next_close = next_candle[self.close_column]
        next_open = next_candle[self.open_column]
        next_high = next_candle[self.high_column]
        next_low = next_candle[self.low_column]

        return (abs(close - open) / (high - low+0.0001) < 0.1 and
                (high - max(close, open)) > (3 * abs(close - open)) and
                (min(close, open) - low) <= abs(close - open)) and (next_close < next_open)
