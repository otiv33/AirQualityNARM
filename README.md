# AirQualityNARM

This repository is all the code that was used for the bachelor thesis <b>Finding hidden information from air quality measurement using association rule mining</b>.

Thesis link : [Bachelor thesis](https://github.com/otiv33/AirQualityNARM/blob/master/Bachelor-thesis-abeln.pdf)

## Abstract

This thesis presents a procedure for finding hidden information from air quality measurements using associtation rule mining. Association rule mining is a
technique through which interesting associations between data from large datasets can be extracted. In this thesis we show the data mining process, data
processing, explanation of the algorithms used and their implementation. We describe the Apriori, ECLAT and Fp-growth algorithms used in associative rule mining.
We also presented numerical associative rule mining which used the particle swarm optimisation algorithm. The mining results revealed different relationships
between the measurement values, which we explained and visualised using different graphs.

## Structure

`AirQualityAPI` is the folder where we created a .NET 6 API which stores all the air quality measurement data.

`AirQualityESP` is the folder where we created the code which used the ESP32 controller with SEN55 air sensor.

`NARM` is the folder where we created the script where we used different association rule mining algorithms to get hidden information from air quality measurements.
