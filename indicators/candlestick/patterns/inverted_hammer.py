from indicators.candlestick.patterns.candlestick_finder import CandlestickFinder


class InvertedHammer(CandlestickFinder):
    def __init__(self, target=None):
        super().__init__(self.get_class_name(), 1, target=target, type='buy')

    def logic(self, idx):
        candle = self.data.iloc[idx]
        next_candle = self.data.iloc[idx - 1 * self.multi_coeff]

        close = candle[self.close_column]
        open = candle[self.open_column]
        high = candle[self.high_column]
        low = candle[self.low_column]

        # next low
        next_close = next_candle[self.close_column]

        return (((high - low) > 3 * (open - close)) and
                ((high - close) / (.001 + high - low) > 0.6)
                and ((high - open) / (.001 + high - low) > 0.6)
                and (next_close > max(close, open)))
