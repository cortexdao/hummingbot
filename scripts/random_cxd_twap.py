import logging
import random

from hummingbot.core.event.events import (
    BuyOrderCompletedEvent,
    BuyOrderCreatedEvent,
    MarketOrderFailureEvent,
    OrderCancelledEvent,
    OrderFilledEvent,
    SellOrderCompletedEvent,
    SellOrderCreatedEvent,
)
from hummingbot.strategy.script_strategy_base import Decimal, OrderType, ScriptStrategyBase


class CXDTwap(ScriptStrategyBase):
    """
    This example shows how to set up a simple strategy to buy and sell a token on fixed (dollar) amount on a regular basis
    """
    #: Define markets to instruct Hummingbot to create connectors on the exchanges and markets you need
    exchange = "mexc"
    trading_pair = "CXD-USDT"

    markets = {"mexc": {"CXD-USDT"}}

    #: The last time the strategy places a buy order
    last_ordered_ts = 0.
    #: Trade interval (in seconds)
    trade_interval = 180
    trade_interval_range = 60
    next_trade_interval = 180.
    #: Trade amount (in dollars - USDT)
    quote_amount = 10
    quote_amount_range = 5

    trade_sequence = [True, True, True, True, True]

    def on_tick(self):
        if not self.trade_sequence:
            sequence_count = random.randrange(15, 30)
            is_buy = random.choice([True, False])
            self.trade_sequence = [is_buy for step in range(sequence_count)]

        # Check if it is time to trade
        if self.last_ordered_ts < (self.current_timestamp - self.next_trade_interval):
            self.cancel_all_orders()

            # Decide to buy or sell
            current_step = self.trade_sequence.pop()

            price = self.connectors[self.exchange].get_price(self.trading_pair, current_step)

            low_amount_range = self.quote_amount - self.quote_amount_range
            high_amount_range = self.quote_amount + self.quote_amount_range
            random_quote_amount = Decimal(random.randrange(low_amount_range, high_amount_range))

            amount = random_quote_amount / price

            try:
                if current_step:
                    self.buy(self.exchange, self.trading_pair, amount, OrderType.LIMIT, price)
                else:
                    self.sell(self.exchange, self.trading_pair, amount, OrderType.LIMIT, price)
            except Exception:
                return

            self.last_ordered_ts = self.current_timestamp

            low_interval_range = self.trade_interval - self.trade_interval_range
            high_interval_range = self.trade_interval + self.trade_interval_range
            self.next_trade_interval = float(random.randrange(low_interval_range, high_interval_range))

    def cancel_all_orders(self):
        for order in self.get_active_orders(connector_name=self.exchange):
            self.cancel(self.exchange, order.trading_pair, order.client_order_id)

    def did_create_buy_order(self, event: BuyOrderCreatedEvent):
        """
        Method called when the connector notifies a buy order has been created
        """
        self.logger().info(logging.INFO, f"The buy order {event.order_id} has been created")

    def did_create_sell_order(self, event: SellOrderCreatedEvent):
        """
        Method called when the connector notifies a sell order has been created
        """
        self.logger().info(logging.INFO, f"The sell order {event.order_id} has been created")

    def did_fill_order(self, event: OrderFilledEvent):
        """
        Method called when the connector notifies that an order has been partially or totally filled (a trade happened)
        """
        self.logger().info(logging.INFO, f"The order {event.order_id} has been filled")

    def did_fail_order(self, event: MarketOrderFailureEvent):
        """
        Method called when the connector notifies an order has failed
        """
        self.logger().info(logging.INFO, f"The order {event.order_id} failed")

    def did_cancel_order(self, event: OrderCancelledEvent):
        """
        Method called when the connector notifies an order has been cancelled
        """
        self.logger().info(f"The order {event.order_id} has been cancelled")

    def did_complete_buy_order(self, event: BuyOrderCompletedEvent):
        """
        Method called when the connector notifies a buy order has been completed (fully filled)
        """
        self.logger().info(f"The buy order {event.order_id} has been completed")

    def did_complete_sell_order(self, event: SellOrderCompletedEvent):
        """
        Method called when the connector notifies a sell order has been completed (fully filled)
        """
        self.logger().info(f"The sell order {event.order_id} has been completed")
