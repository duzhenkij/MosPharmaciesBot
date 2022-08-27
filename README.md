# MosPharmaciesBot

MosPharmaciesBot – is the Telegram Bot, which can be used for searching medicines among top pharmacies of Moscow (such as «Аптека 36,6», «Горздрав», «Самсон-Фарма», «Здоров.ру» and «Аптеки Столички») by the best price.

Bot has a simple working principle: a user sends a request with the name of a medicine and bot returns a list of such medicines from different pharmacies sorted by price ascending (max 25 lines).

Bot was written in Python. It consists of: 
- class Parser scrapes pharmacies using different methods for each pharmacy separately by user query. Methods from the class return tuples with lists of titles, dosages and prices for each pharmacy;
- functions from the main.py create a data frame, clean and sort it with Pandas and prettify the data frame to string in order to send it to user;
- there is also a database with a statistic table of user queries in order to count number of users.

The bot is located here <b>[@MosPharmaciesBot](https://t.me/MosPharmaciesBot)</b>)