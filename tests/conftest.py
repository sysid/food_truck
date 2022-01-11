import logging

import pytest

from food_truck.backend.domain.events import StockPriceUpdated, StockBought
from food_truck.backend.eventstore.event_store import DummyEventStore, EventsToRecord

_log = logging.getLogger(__name__)
log_fmt = r"%(asctime)-15s %(levelname)s %(name)s %(funcName)s:%(lineno)d %(message)s"
datefmt = "%Y-%m-%d %H:%M:%S"
logging.basicConfig(format=log_fmt, level=logging.DEBUG, datefmt=datefmt)

MSFT_STOCK = {
    "1. symbol": "MSFT",
    "2. name": "Microsoft Corporation",
    "3. type": "Equity",
    "4. region": "United States",
    "5. marketOpen": "09:30",
    "6. marketClose": "16:00",
    "7. timezone": "UTC-04",
    "8. currency": "USD",
    "9. matchScore": "1.0000",
}

STOCKS = [
    {
        "1. symbol": "AF.PAR",
        "2. name": "Air France-KLM SA",
        "3. type": "Equity",
        "4. region": "Paris",
        "5. marketOpen": "09:00",
        "6. marketClose": "17:30",
        "7. timezone": "UTC+01",
        "8. currency": "EUR",
        "9. matchScore": "0.5714",
    },
    {
        "1. symbol": "AF4.FRK",
        "2. name": "The Hanover Insurance Group Inc",
        "3. type": "Equity",
        "4. region": "Frankfurt",
        "5. marketOpen": "08:00",
        "6. marketClose": "20:00",
        "7. timezone": "UTC+01",
        "8. currency": "EUR",
        "9. matchScore": "0.5714",
    },
    {
        "1. symbol": "AF5.FRK",
        "2. name": "AKKA Technologies SE",
        "3. type": "Equity",
        "4. region": "Frankfurt",
        "5. marketOpen": "08:00",
        "6. marketClose": "20:00",
        "7. timezone": "UTC+01",
        "8. currency": "EUR",
        "9. matchScore": "0.5714",
    },
    {
        "1. symbol": "AF8.FRK",
        "2. name": "AF Gruppen ASA",
        "3. type": "Equity",
        "4. region": "Frankfurt",
        "5. marketOpen": "08:00",
        "6. marketClose": "20:00",
        "7. timezone": "UTC+01",
        "8. currency": "EUR",
        "9. matchScore": "0.5714",
    },
    {
        "1. symbol": "AFAAX",
        "2. name": "Yorktown Capital Appreciation Fd USD Class INST",
        "3. type": "Mutual Fund",
        "4. region": "United States",
        "5. marketOpen": "09:30",
        "6. marketClose": "16:00",
        "7. timezone": "UTC-04",
        "8. currency": "USD",
        "9. matchScore": "0.5714",
    },
    {
        "1. symbol": "AFACU",
        "2. name": "Arena Fortify Acquisition Corp - Units (1 Ord Share Class A & 1/2 War)",
        "3. type": "Equity",
        "4. region": "United States",
        "5. marketOpen": "09:30",
        "6. marketClose": "16:00",
        "7. timezone": "UTC-04",
        "8. currency": "USD",
        "9. matchScore": "0.5714",
    },
    {
        "1. symbol": "AFACW",
        "2. name": "Arena Fortify Acquisition Corp - Warrants (10/11/2026)",
        "3. type": "Equity",
        "4. region": "United States",
        "5. marketOpen": "09:30",
        "6. marketClose": "16:00",
        "7. timezone": "UTC-04",
        "8. currency": "USD",
        "9. matchScore": "0.5714",
    },
    {
        "1. symbol": "AFADX",
        "2. name": "Toreador International Fund Investor Shares",
        "3. type": "Mutual Fund",
        "4. region": "United States",
        "5. marketOpen": "09:30",
        "6. marketClose": "16:00",
        "7. timezone": "UTC-04",
        "8. currency": "USD",
        "9. matchScore": "0.5714",
    },
    {
        "1. symbol": "AFALX",
        "2. name": "APPLIED FINANCE CORE FUND INVESTOR CLASS",
        "3. type": "Mutual Fund",
        "4. region": "United States",
        "5. marketOpen": "09:30",
        "6. marketClose": "16:00",
        "7. timezone": "UTC-04",
        "8. currency": "USD",
        "9. matchScore": "0.5714",
    },
    {
        "1. symbol": "AF72.FRK",
        "2. name": "A.G. BARR p.l.c",
        "3. type": "Equity",
        "4. region": "Frankfurt",
        "5. marketOpen": "08:00",
        "6. marketClose": "20:00",
        "7. timezone": "UTC+01",
        "8. currency": "EUR",
        "9. matchScore": "0.5000",
    },
]


@pytest.fixture()
def eventstore():
    evtr = EventsToRecord(
        version=0,
        stream=None,
        events=[
            StockBought(
                name="Microsoft",
                symbol="MSFT",
                currency="USD",
                qty=10,
                price=300.0,
            ),
            StockPriceUpdated(
                symbol="MSFT",
                price=301.0,
            ),
            StockPriceUpdated(
                symbol="MSFT",
                price=302.0,
            ),
            StockBought(
                name="Apple",
                symbol="AAA",
                currency="USD",
                qty=10,
                price=10.0,
            ),
            StockBought(
                name="Bayerische Motorenwerke",
                symbol="BMW",
                currency="EUR",
                qty=10,
                price=2000.0,
            ),
            StockPriceUpdated(
                symbol="BMW",
                price=2001.0,
            ),
        ],
    )
    es = DummyEventStore()
    es.record(evtr=evtr)
    return es
