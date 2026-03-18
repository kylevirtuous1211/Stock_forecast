# fetch_sector_data.py

## Interval
Data Points: Since there are roughly 390 minutes in a standard US trading day (9:30 AM – 4:00 PM EST), one year of data for 11 symbols will result in roughly 100,000+ rows.

## IEX not SIP
The "IEX" Feed Constraint: You are using feed="iex". On Alpaca’s free/sandbox tier, this feed only includes data from the IEX exchange, not the full consolidated market (SIP).


# plot_metrics.py
evaulate the trained model, plot the metrics.csv file from finetune_timer.py

# finetune_timer.py
finetune the model, save the trained model to checkpoints/