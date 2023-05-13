@echo off
chcp 65001
echo 开始训练聚类模型...
echo 训练时的进度不会显示，检查任务管理器中python进程在占用CPU就是在训练，一般需要5-10分钟左右
.\python38\python.exe cluster/train_cluster.py
echo 训练完成
pause