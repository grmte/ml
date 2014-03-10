1. Add src folder to the path variable.
export PATH="$HOME/ml/src:$PATH"

2. To generate features see:
fGen.py -h

To general all features see:
fGenAll.py

3. To generate targets see:
tGen.py -h

4. To generate train.r see:
mGen.py -h

5. To generate predict.r see:
pGen.py -h

6. To do training
./en/train.r -d -d [dirname]

7. To do predictions
./en/predict.r -d [dirname]

8. To generate the confusion matrix
cMatrixGen.py -e en -d [dirname]

9. What is the format of the confusion matrix ?
When printed on the screen:
-------------------------------
actual=0       | actual = 0   |
predicted=0    | predicted = 1|
-------------------------------
actual=1       | actual = 1   |
predicted=0    | predicted = 1|
-------------------------------
When in the file:
--------------------------------------------------------------
actual=0       | actual = 0   |actual=1       | actual = 1   |
predicted=0    | predicted = 1|predicted=0    | predicted = 1|
--------------------------------------------------------------
