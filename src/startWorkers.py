import attribute
import paramiko

portList = [90,90,90,90,90,90,0,90,0,90,90,90,90,90,90]
mountCommand = "mount 10.1.35.6:/home/vikas/ /home/vikas/"
pathCommand = "cd /home/vikas/ml"
exportProgPaths = "export PATH=$PATH:/home/vikas/ml/src/"
exportCeleryCommandDict = ['export C_FORCE_ROOT=True;export PYTHONPATH="./src" ; celery multi start -A dp worker -n 1 --logfile="./celery/1.log" --pidfile="./celery/1.pid"',
                           'export C_FORCE_ROOT=True;export PYTHONPATH="./src" ; celery multi start -A dp worker -n 2 --logfile="./celery/2.log" --pidfile="./celery/2.pid"',
                           'export C_FORCE_ROOT=True;export PYTHONPATH="./src" ; celery multi start -A dp worker -n 3 --logfile="./celery/3.log" --pidfile="./celery/3.pid"',
                           'export C_FORCE_ROOT=True;export PYTHONPATH="./src" ; celery multi start -A dp worker -n 4 --logfile="./celery/4.log" --pidfile="./celery/4.pid"',
                           'export C_FORCE_ROOT=True;export PYTHONPATH="./src" ; celery multi start -A dp worker -n 5 --logfile="./celery/5.log" --pidfile="./celery/5.pid"',
                           'export C_FORCE_ROOT=True;export PYTHONPATH="./src" ; celery multi start -A dp worker -n 6_ml --logfile="./celery/%n_6_ml.log" --pidfile="./celery/%n_6_ml.pid"',
                           '',
                           'export C_FORCE_ROOT=True;export PYTHONPATH="./src" ; celery multi start -A dp worker -n 8 --logfile="./celery/%n_8.log" --pidfile="./celery/%n_8.pid"',
                           '',
                           'export C_FORCE_ROOT=True;export PYTHONPATH="./src" ; celery multi start -A dp worker -n 10 --logfile="./celery/%n_10.log" --pidfile="./celery/%n_10.pid"',
                           'export C_FORCE_ROOT=True;export PYTHONPATH="./src" ; celery multi start -A dp worker -n 11 --logfile="./celery/11.log" --pidfile="./celery/11.pid"',
                           'export C_FORCE_ROOT=True;export PYTHONPATH="./src" ; celery multi start -A dp worker -n 12 --logfile="./celery/%n_12.log" --pidfile="./celery/%n_12.pid"',
                           'export C_FORCE_ROOT=True;export PYTHONPATH="./src" ; celery multi start -A dp worker -n 13 --logfile="./celery/%n_13.log" --pidfile="./celery/%n_13.pid"',
                           'export C_FORCE_ROOT=True;export PYTHONPATH="./src" ; celery multi start -A dp worker -n 14 --logfile="./celery/%n_14.log" --pidfile="./celery/%n_14.pid"',
                           'export C_FORCE_ROOT=True;export PYTHONPATH="./src" ; celery multi start -A dp worker -n 15 --logfile="./celery/%n_15.log" --pidfile="./celery/%n_15.pid"',
                           ]