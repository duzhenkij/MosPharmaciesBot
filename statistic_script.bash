#!/bin/bash

FILENAME=$(date +"report_on_%A%d%B.txt")
date > $FILENAME

echo Количество уникальных пользователей >> $FILENAME
sqlite3 db.db "SELECT COUNT(DISTINCT user) AS Всего_пользователей FROM statistic;" >> $FILENAME

echo Количество запросов по уникальным лекарствам >> $FILENAME
sqlite3 db.db "SELECT medicine, COUNT(medicine) AS Количество_запросов  FROM statistic GROUP BY medicine ORDER BY Количество_запросов DESC;" >> $FILENAME
