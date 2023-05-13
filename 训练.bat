@echo off
chcp 65001
echo 即将开始训练...
.\python38\python.exe train.py -c configs/config.json -m 44k
pause