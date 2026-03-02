@echo off

rem 配置Git用户信息
"C:\Program Files\Git\bin\git.exe" config --global user.name "liukai-peng"
"C:\Program Files\Git\bin\git.exe" config --global user.email "1284877660@qq.com"

rem 初始化Git仓库
"C:\Program Files\Git\bin\git.exe" init

rem 添加所有文件到暂存区
"C:\Program Files\Git\bin\git.exe" add .

rem 提交更改
"C:\Program Files\Git\bin\git.exe" commit -m "Initial commit: Local Grammar RAG System"

rem 添加远程仓库
"C:\Program Files\Git\bin\git.exe" remote add origin https://github.com/liukai-peng/local_grammar-RAG-system.git

rem 推送到GitHub
"C:\Program Files\Git\bin\git.exe" push -u origin main

echo 执行完成！
pause