# 文档说明
## 目录结构
data: 流水excel原始数据

garbage: 旧版本脚本

Modules: 通用脚本

    flask_api.py
    web接口集合脚本，用于在服务器上运行，使外部可以通过"ip:5101/liushui/<string:api_name>"调用脚本
    核心functions包括process_file, match, analysis, addrules, addstats等。
    服务器挂起方法：
    nohup python3 -u flask_api.py >> log/flask_api.txt &
    ps -ef --sort=ruid| grep python
    
    flask_upload.py
    用于将文件上传到服务器的test脚本。已并入flask_api.py里的upload function
    
    mongodb.py
    集合了对本地mongodb数据库的增查删改的python functions
    
    public_module.py
    集合了关于日期，字典以及计算相关性，benford之类的通用functions
    
    pymysql.py
    集合了对本地和远程pymysql数据库的增查删改的python functions。没有测试，仅供参考。
    
    sqlite3.py 
    集合了对本地和SQL数据库的增查删改的python functions。
    
nn: 神经网络

    models
    神经网络h5模型和tokenize objects（nn_train生成）
    
    plots
    模型图，预测标签分布图，准确率走势图
    
    xlsx_files
    输入和输出excel文件，规则文件
    
    generator.py
    关键词匹配打标签脚本
    
    nn_main.py
    总入口。集成关键词打标签和神经网络预测标签。输入输出均为excel
    
    nn_pred.py
    输入excel文件(test)，提取1.流入流出金额，2.tokenize摘要和对方名称，以及3.命中哪个标签为数字特征，进入神经网络预测标签，反向tokenize标签，输出excel, 并作图
    
    nn_train.py
    输入excel文件(train)，提取1.流入流出金额，2.tokenize摘要和对方名称，以及3.命中哪个标签为数字特征，进入神经网络预测标签，反向tokenize标签，输出excel, 并作图
    神经网络结构（深度学习）
    Embedding + Dropout + RNN + Dense + Dropout + Dense
    
output: 入库输出的过程excel表格

（yikongall.xlsx和tongpuall.xlsx为最终可用文件）

matcher.py

analysis.py
    
    