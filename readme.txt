1. Add src folder to the path variable.
export PATH="$HOME/ml/src:$PATH"
replace $HOME with the path of where the file is
for e.g.
export PATH="/home/jkm/ml/src:$PATH"

2. To generate features see:
aGen.py -h

To generate all features see:
aGenForE.py

3. To generate train.r see:
mRGenForE.py -h
mRGenForAllSubE.py -h

4. To generate predict.r see:
pRGenForE.py -h
pRGenForAllSubE.py -h

To generate mGen.py and pGen.py with one command you can use:
rGenForE.py -e e1

5. To do training
./e/n/train-algo.r -d [dirname]

6. To do predictions
./e/n/predict-algo.r -d [dirname]

7. To generate the confusion matrix
cMatrixGen.py -e en -d [dirname]

8. What is the format of the confusion matrix ?
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

9. What is kept in the git repo?

design.ini for each experiment.
cmatrix in the data folders
zipped data file in the data folder
generated r scripts predict.r and train.r

The following files are not kept:
.feature 
.target 
.model 
.predictions 
.trade
.r

10. For Distributed Parallel (dp)
osx:
sudo brew install rabbitmq
ln -sfv /usr/local/opt/rabbitmq/*.plist ~/Library/LaunchAgents
launchctl load ~/Library/LaunchAgents/homebrew.mxcl.rabbitmq.plist
sudo /usr/local/sbin/rabbitmq-server 
linux:
https://www.rabbitmq.com/install-rpm.html
service rabbitmq-server start
service rabbitmq-server status

The web interface to the rabbitmq is available at:
http://127.0.0.1:15672/

11. to get a centos VM running
  655  vagrant box add centos65-x86_64-20131205 https://github.com/2creatives/vagrant-centos/releases/download/v6.5.1/centos65-x86_64-20131205.box
  656  vagrant init centos65-x86_64-20131205
  659  vagrant up
ssh vagrant@127.0.0.1 -p 2222
login: vagrant / vagrant

12. Where is the vagrant box stored:
du -h /Users/vikaskedia/.vagrant.d/

13. Python packages that are needed: 
    celery, flower, termcolor, argparse

14. to start the celery worker
ml> export PYTHONPATH="./src" ; celery -A dp worker --loglevel=INFO -n worker1

15. Flower (This is the web interface to the task computers)
to start 
>flower --port=81
To see the web interface: In the browser enter http://10.105.1.194:81/

16. Other good to have software:
multitail
