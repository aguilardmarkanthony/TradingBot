from abc import ABC, abstractclassmethod

class TradingPlugin(ABC):
    @abstractclassmethod
    def plug(self, df, signal):
        pass
    