rm plots/*.png

# Google
./stock-viewer.py -n GOOG.US -Y -r -g
mv plots/GOOG.US_*_1.png doc/GOOG.US_1.png
mv plots/GOOG.US_*_2.png doc/GOOG.US_2.png
mv plots/GOOG.US_*_3.png doc/GOOG.US_3.png

# Bitcoin to USD
./stock-viewer.py -n BTCUSD.pl -6M  -g
mv plots/BTCUSD.pl_*_1.png doc/BTCUSD.pl_1.png
mv plots/BTCUSD.pl_*_2.png doc/BTCUSD.pl_2.png
mv plots/BTCUSD.pl_*_3.png doc/BTCUSD.pl_3.png

# Apple
./stock-viewer.py -n AAPL.US -6M -g
mv plots/AAPL.US_*_1.png doc/AAPL.US_1.png
mv plots/AAPL.US_*_2.png doc/AAPL.US_2.png
mv plots/AAPL.US_*_3.png doc/AAPL.US_3.png

# CDR
./stock-viewer.py -n CDR.pl -Y -r -g
mv plots/CDR.pl_*_1.png doc/CDR.pl_1.png
mv plots/CDR.pl_*_2.png doc/CDR.pl_2.png
mv plots/CDR.pl_*_3.png doc/CDR.pl_3.png
