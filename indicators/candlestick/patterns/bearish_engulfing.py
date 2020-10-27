from indicators.candlestick.patterns.candlestick_finder import CandlestickFinder


class BearishEngulfing(CandlestickFinder):
    def __init__(self, target=None):
        super().__init__(self.get_class_name(), 2, target=target, type='sell')

    def logic(self, idx):
        candle = self.data.iloc[idx]
        prev_candle = self.data.iloc[idx + 1 * self.multi_coeff]
        next_candle = self.data.iloc[idx - 1 * self.multi_coeff]

        close = candle[self.close_column]
        open = candle[self.open_column]
        high = candle[self.high_column]
        low = candle[self.low_column]

        prev_close = prev_candle[self.close_column]
        prev_open = prev_candle[self.open_column]
        prev_high = prev_candle[self.high_column]
        prev_low = prev_candle[self.low_column]

        # Prev and next low
        next_low = next_candle[self.low_column]

        return ((prev_open < prev_close) and (open > close) and
                (prev_open >= close) and (prev_close <= open) and
                (next_low < close))
