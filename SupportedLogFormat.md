To make PyLan work properly and generate appropriate charts you have to configure your JMeter Test Plan.

First of all name your request (samples) to make future analysis less ambiguous.

Then add the Simple Data Writer listener to your Test Plan, specify output log file path and name (use .jtl extension by default) and configure listener to save particular data in CSV or XML format.

## Supported CSV log format ##

Minimal log configuration is presented at the snapshot below.

![http://wiki.pylan.googlecode.com/hg/images/csv_log.png](http://wiki.pylan.googlecode.com/hg/images/csv_log.png)

Sample log file is available [here](http://wiki.pylan.googlecode.com/hg/samples/csv_log.jtl)

## Supported XML log format ##

In order to implement transaction-oriented processing you can use XML format. Minimal log configuration is presented at the snapshot below.

![http://wiki.pylan.googlecode.com/hg/images/xml_log.png](http://wiki.pylan.googlecode.com/hg/images/xml_log.png)

It also requires the following structure of samples:

![http://wiki.pylan.googlecode.com/hg/images/transactions.png](http://wiki.pylan.googlecode.com/hg/images/transactions.png)

Sample log file is available [here](http://wiki.pylan.googlecode.com/hg/samples/xml_log.jtl)