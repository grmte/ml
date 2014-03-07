1. Add src folder to the path variable.
export PATH="$HOME/ml/src:$PATH"

2. To generate features see:
fGen.py -h

3. To generate targets see:
tGen.py -h

4. To generate train.r see:
mGen.py -h

5. To generate predict.r see:
pGen.py -h

6. To do training
train.r -d [dirname]

7. To do predictions
predict.r [dirname]
