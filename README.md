# crypto-trading-bot

The objective of this project was to build a proof of concept for a reinforcement learning trading bot
that makes autonomous decisions when deployed in a live trading scenario. We used a Recurrent PPO
reinforcement learning model for our trading bot owing to the LSTM layers being incorporated into
the algorithm. To train the model, we used the historical Cryptocurrency data from Kraken and did
feature engineering to extract 25 features that were a part of the state. We built a custom OpenAI gym
environment for training and testing. Finally, to deploy the model to live trading, we defined three
different classes, one to initiate the Kraken websocket and keep storing the data as per the required
state format and one to utilize the Kraken REST API to access the required data to create the state,
and finally a live trading class that encapsulates all of the trading logic. Our model performs well
during training but significant improvement is required regarding live trading performance.
