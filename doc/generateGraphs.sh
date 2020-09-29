rm plots/*.svg

# Google
./stock-viewer.py -n GOOG.US -Y -r -g
mv plots/GOOG.US_*_1.svg doc/GOOG.US_1.svg
mv plots/GOOG.US_*_2.svg doc/GOOG.US_2.svg
mv plots/GOOG.US_*_3.svg doc/GOOG.US_3.svg
mv plots/GOOG.US_*_4.svg doc/GOOG.US_4.svg
mv plots/GOOG.US_*_4.svg doc/GOOG.US_4.svg
mv plots/GOOG.US_*_5.svg doc/GOOG.US_5.svg

# Bitcoin to USD
./stock-viewer.py -n BTCUSD.pl -6M  -g
mv plots/BTCUSD.pl_*_1.svg doc/BTCUSD.pl_1.svg
mv plots/BTCUSD.pl_*_2.svg doc/BTCUSD.pl_2.svg
mv plots/BTCUSD.pl_*_3.svg doc/BTCUSD.pl_3.svg
mv plots/BTCUSD.pl_*_4.svg doc/BTCUSD.pl_4.svg

# Apple
./stock-viewer.py -n AAPL.US -6M -g
mv plots/AAPL.US_*_1.svg doc/AAPL.US_1.svg
mv plots/AAPL.US_*_2.svg doc/AAPL.US_2.svg
mv plots/AAPL.US_*_3.svg doc/AAPL.US_3.svg
mv plots/AAPL.US_*_4.svg doc/AAPL.US_4.svg
mv plots/AAPL.US_*_5.svg doc/AAPL.US_5.svg

# CDR
./stock-viewer.py -n CDR.pl -Y -r -g
mv plots/CDR.pl_*_1.svg doc/CDR.pl_1.svg
mv plots/CDR.pl_*_2.svg doc/CDR.pl_2.svg
mv plots/CDR.pl_*_3.svg doc/CDR.pl_3.svg
mv plots/CDR.pl_*_4.svg doc/CDR.pl_4.svg
mv plots/CDR.pl_*_5.svg doc/CDR.pl_5.svg
