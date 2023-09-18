# OANDA-Trade-Bot
A forex trading bot designed to trade three currency pairs (EUR/USD, GBP/USD, and USD/JPY) using the Opening Range Breakout (ORB) strategy on 15-minute candlestick charts. 
Utilizing Oanda's API, the bot fetches the most recent trading prices and calculates the ORB levels. 
If the last traded price breaches these levels, a "BUY" or "SELL" signal is generated. 
The bot then places the corresponding market order, ensuring not to place duplicate orders. 
The whole process for each currency pair runs independently and concurrently using threading, allowing the bot to analyze and trade multiple pairs simultaneously.
