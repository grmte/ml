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

10. For Distributed Parallel (dp) we need the following:
i. rabbitmq: The broker queue and ther backend queue. The broker queue is for tasks and backend queue is for results.
ii. celery: This can be run in 2 modes. The celery server and the celery client. The celery server submits tasks to the queue and celery worker takes tasks out of the queue and executes tasks
iii. flower: Web interface to celery
iv. nfs to get a common file system across multiple machines.
v. drbl: This is used to make the celery worker run on a different computer.

11. How to install rabbitmq?
osx:
===
sudo brew install rabbitmq
ln -sfv /usr/local/opt/rabbitmq/*.plist ~/Library/LaunchAgents
launchctl load ~/Library/LaunchAgents/homebrew.mxcl.rabbitmq.plist
sudo /usr/local/sbin/rabbitmq-server 
linux:
=====
https://www.rabbitmq.com/install-rpm.html
wget https://www.rabbitmq.com/releases/rabbitmq-server/v3.3.1/rabbitmq-server-3.3.1-1.noarch.rpm
yum install rabbitmq-server-3.3.1-1.noarch.rpm # This will install erlang since erlang is a dependency
make sure that the epmd deamon is running by giving the command:  telnet 127.0.0.1 4369
make sure that the host file entry is correct. On 26th may 2014 I had to enter scp1 inside /etc/hosts
service rabbitmq-server start
service rabbitmq-server status
To enable the web interface: rabbitmq-plugins enable rabbitmq_management
The web interface to the rabbitmq is available at:
http://127.0.0.1:15672/
To allow the guest user login from the web interface:
Start rabbitmq using /ml/config/rabbitmq/rabbitmq.config
root@scp1.ao:/home/vikas/ml> rm -rf /etc/rabbitmq/
root@scp1.ao:/home/vikas/ml> ln -sf /home/vikas/ml/config/rabbitmq/ /etc/rabbitmq

12. Python packages that are needed: 
    easy_install celery flower termcolor argparse
    
13. to start the celery worker
a)Ensure the clock of new machine is synced with server machine using the follwing command
       ntpdate pool.ntp.org && hwclock --systohc && hwclock --adjust
b)Give the following command :- 
       export C_FORCE_ROOT=True;export PYTHONPATH="./src" ; celery -A dp worker --loglevel=INFO -n worker1 --concurrency 1
       	      			       			  OR
       export C_FORCE_ROOT=True;export PYTHONPATH="./src" ; celery multi start -A dp worker -n 9 --logfile="./celery/%n.log" --pidfile="./celery/%n.pid"
we do export PYTHONPATH="./src" since dp.py is inside the src folder
the -A dp tells to open the file dp.py and get the connection params from there
The worker param tells to start celery program in worker mode.
the -n worker1 is used to give the name "worker1" to this worker.
The above command starts a worker ready to accept tasks

14. Flower (This is the web interface to the task computers)
to start 
>flower --port=81
To see the web interface: In the browser enter http://10.105.1.194:81/

15. To test that the worker is able to execute a simple task:
ml/src/> python
>>> from dp import add # add is a python function
>>> from celery import Celery
>>> app = Celery('dp', broker='amqp://guest@10.1.35.6//',backend='amqp://guest@10.1.35.6//')
>>> result = add.delay(4, 4) # we are submitting the add function as a task to the celery server. The 4,4 are the params to the add function
>>> print result.get()

16. How to install the nfs server:
on scp1
======
service nfs start
service rpcbind start
the content of /etc/exports file:
/home/vikas   10.1.31.0/255.255.255.0(rw,sync,no_root_squash)  
The conent of /etc/hosts.allow file:
rpcbind:10.1.0.0/255.255.0.0

On the client computer
=====================
service rpcbind start
mount 10.1.35.6:/home/vikas vikas

16. If you are using drbl then install drbl with the steps at:
http://drbl.org/installation/

17. Other good to have software:
multitail

18. What are synthetic columns ?
Features are treated as synthetic columns.

19. What are the different short forms used?
ro => read only files
wf => working files
rs => results
t => target in ob/data/wf/ folder name and t for trade logs directories in ob/data/rs/ folder
f => features
p => prediction
c => confusionMatrix
r => R program in program name and results directory in data folders name
m => model prepared



20. Installation required to get ml codes in a machine and start using the ml structure

a. easy_install configobj
b. yum install git* # We require git for numpy instalation with checkout the ml codes
c. easy_install argparse
d. yum install yum-conf-epel
e. yum install R-core*
f. yum install R*
g. yum install pypy
h. git clone https://bitbucket.org/pypy/numpy.git
i. cd numpy/
j. ls
k. pypy setup.py install
l. cd ..
m. rm -rf numpy
n. yum install libffi*
o. easy_install cffi
p. easy_install importlib
q. git clone https://github.com/grmte/ml.git #This will checkout codes in our local machine . 
(Note it will create ml folder inside wherever you given this command . So dont gove this command inside ml folder . it will then result into ml/ml .)
r. ln -sf /usr/bin/python /usr/local/bin/pypy
s. Then go inside R program by typing R
   >install.packages('glmnet')
(if easy install is not installed in machine then  wget https://bootstrap.pypa.io/ez_setup.py -O - | python to install it)
