from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, List, Optional

from food_truck.contract.commands import UpdatePortfolio, BuyStock, SellStock
from food_truck.contract.queries import (
    PortfolioQuery,
    CandidateStocksQuery,
    PortfolioStockQuery,
    PortfolioQueryResult,
    PortfolioStockQueryResult,
    CandidateStock,
    MatchingStock,
)

Symbol = int


@dataclass
class UserInterface:
    on_portfolio_query: Callable[[PortfolioQuery], None] = field(
        default=lambda event: None
    )
    on_update_portfolio_command: Callable[[UpdatePortfolio], None] = field(
        default=lambda event: None
    )
    on_candidate_stock_query: Callable[[CandidateStocksQuery], None] = field(
        default=lambda event: None
    )
    on_portfolio_stock_query: Callable[[PortfolioStockQuery], None] = field(
        default=lambda event: None
    )

    def run(self):
        self.on_portfolio_query(PortfolioQuery())
        self.menu_loop()

    def menu_loop(self):
        while True:
            print(">>> D(isplay, B(uy, S(ell, U(pdate, eX(it?: ")
            if (ip := input()).upper() == "X":
                return
            elif ip.upper() == "D":
                self.on_portfolio_query(PortfolioQuery())
            elif ip.upper() == "U":
                print("Updating..")
                self.on_update_portfolio_command(UpdatePortfolio())
            elif ip.upper() == "B":
                self.ask_user_for_stock_identification(
                    lambda id_: self.on_candidate_stock_query(
                        CandidateStocksQuery(pattern=id_)
                    )
                )
            elif ip.upper() == "S":
                self.ask_user_for_stock_identification(
                    lambda id_: self.on_portfolio_stock_query(
                        PortfolioStockQuery(pattern=id_)
                    )
                )

    @staticmethod
    def ask_user_for_stock_identification(on_id: Callable[[str], None]) -> None:
        ip = input("Identification?: ")
        if ip == "":
            return

        print("Loading candidates...")
        on_id(ip)

    def select_stock_to_buy(
        self, candidates: List[CandidateStock]
    ) -> Optional[BuyStock]:
        self.display_buy_candidates(candidates)
        ip = input("Enter index of stock to buy: ")
        if ip == "":
            return
        idx = int(ip) - 1
        try:
            chosen_stock = candidates[idx]
        except IndexError:
            print("Index not in list.")
            return
        self.display_chosen_candidate(chosen_stock)

        ip = input("Buy qty?: ")
        if ip == "":
            return
        qty = int(ip)
        return BuyStock(
            name=chosen_stock.name,
            symbol=chosen_stock.symbol,
            currency=chosen_stock.currency,
            qty=qty,
            price=chosen_stock.price,
            bought=datetime.today(),
        )

    def select_stock_to_sell(
        self, candidates: PortfolioStockQueryResult
    ) -> Optional[SellStock]:
        self.display_sell_candidates(candidates.matching_stocks)
        ip = input("Enter index of stock to sell: ")
        if ip == "":
            return
        idx = int(ip) - 1
        chosen_stock = candidates.matching_stocks[idx]
        return SellStock(symbol=chosen_stock.symbol)

    @staticmethod
    def display_buy_candidates(candidates: List[CandidateStock]) -> None:
        for i, candidate in enumerate(candidates):
            print(
                f"{i + 1}. {candidates[i].name} ({candidates[i].symbol}): {candidates[i].price:F} {candidates[i].currency}"
            )

    @staticmethod
    def display_chosen_candidate(candidate: CandidateStock) -> None:
        print(f"{candidate.name} ({candidate.symbol})")
        print(f"{candidate.price} {candidate.currency}")

    @staticmethod
    def display_sell_candidates(
        candidates_matching_stocks: List[MatchingStock],
    ):
        for i, candidate in enumerate(candidates_matching_stocks):
            print(
                f"{i + 1}. {candidates_matching_stocks[i].name} ({candidates_matching_stocks[i].symbol})"
            )

    @staticmethod
    def display(pofo: PortfolioQueryResult) -> None:
        if len(pofo.stocks) == 0:
            print("Empty portfolio!")
            return

        for i, s in enumerate(pofo.stocks):
            print(
                f"{i + 1}. {s.name} ({s.symbol}), bought: {s.qty}x{s.buying_price} = {s.qty * s.buying_price}, "
                f"curr.: {s.qty}x{s.current_price} = {s.qty * s.current_price:.2f} -> {s.return_:.2f}, "
                f"RoR: {s.rate_of_return:.2f}"
            )

        print(
            f"Portfolio value: {pofo.portfolio_value:.2f}, RoR: {pofo.portfolio_rate_of_return:.2f}"
        )

    @staticmethod
    def display_buy_confirmation(symbol: str, qty: int, price: float) -> None:
        print(f"Bought {qty} x {symbol} at {price} = {qty * price:.2f}")

    @staticmethod
    def display_sell_confirmation(symbol: str) -> None:
        print(f"Sold all '{symbol}'!")


if __name__ == "__main__":
    ui = UserInterface()
    ui.run()
