# 文档说明
## 目录结构 🗂
### 流水 Liushui💧

data: 流水excel原始数据🏠

garbage: 旧版本脚本

Modules: 通用脚本

    flask_api.py
    web接口集合脚本，用于在服务器上运行，使外部可以通过"ip:5101/liushui/<string:api_name>"调用脚本
    核心functions包括process_file, match, analysis, addrules, addstats等。
    服务器挂起方法：
    nohup python3 -u flask_api.py >> log/flask_api.txt &
    ps -ef --sort=ruid| grep python
    kill <进程编号>
    
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
    
nn: 神经网络🕸️

    models
    神经网络h5模型和tokenize objects（nn_train生成）
    
    plots📈
    模型图，预测标签分布图，准确率走势图
    
    xlsx_files🏠
    输入和输出excel文件，规则文件
    
    generator.py
    关键词匹配打标签脚本
    
    nn_main.py 🕸️️
    总入口。集成关键词打标签和神经网络预测标签。输入输出均为excel
    
    nn_pred.py 🕸️
    输入excel文件(test)，提取1.流入流出金额，2.tokenize摘要和对方名称，以及3.命中哪个标签为数字特征，进入神经网络预测标签，反向tokenize标签，输出excel, 并作图
    
    nn_train.py 🕸️
    输入excel文件(train)，提取1.流入流出金额，2.tokenize摘要和对方名称，以及3.命中哪个标签为数字特征，进入神经网络预测标签，反向tokenize标签，输出excel, 并作图
    神经网络结构（深度学习）
    Embedding + Dropout + RNN + Dense + Dropout + Dense
    
output: 入库输出的过程excel表格🏠

    yikongall.xlsx和tongpuall.xlsx为最终可用文件

matcher.py
    
    1. class结构
    Class Matcher为一个封装好的流程object。
    每个object可处理一个excel下的一个sheet，因为需保存其特定的表格信息'self.info'和规则模版'self.reversed_mapping'
    
    2. class流程
    处理表格有三个阶段。
    (1)第一阶段
        init()读取表格，生成原始的self.raw_df.
    (2)第二阶段
        在info_extractor(), 通过表格名和表格实体内容外的信息提取necessary_items，
        并根据命中header_key来找到实体内容的表格，生成对上位置和列名的self.target_df，并写入或替换mongo:Cache/unmapped_df的'data'
    (3)第三阶段
        (a) mapping() 尝试根据base_rule + mongo:Cache/user_rule匹配, 找到未匹配上的target_unmatched，option_list，和已匹配好的对应关系
        (b) save_info() 尝试整合self.info和mongo:Info/sheet_info库的表格基本信息数据。库数据更新表(不替换已有),表数据全部更新库，并找到未匹配的必填项
        (c) manual_mapping() 此步骤为本地运行，api运行时跳过本步，直接根据mapping和save_info返回结果来调用addrules()和addstats()。
            先询问使用规则模版，否则循环要求输入target_unmatched的每一项对应哪个option，最后addrules更新mongo里的user_rule。
            同理，循环要求输入necessary_unmatched的每一项内容，最后addstats更新mongo里的sheet_info
        (d) dataframe_generator() 根据reversed_mapping的列名匹配规则，一列一列生成我们规范化的dataframe self.generated_df
        (e) separate_col() 一列变两列。比如正负金额分割流入流出。之前流入流出对应同一列数据，所以数据内容一样，本质是做两种数据处理。
        (f) save_df() 将self.generated_df存入mongo:Cache/mapped_df
        (g.1) output_excel() 从mongo:Cache/mapped_df里提取指定公司和batch_id的数据，生成excel
        (g.2) upload_mysql() 从mongo:Cache/mapped_df里提取指定公司和batch_id的数据，上传到mysql:liushui
    
    3. 运行流程
     (1) 核心入口：process_table_api(company, file_path, table='Sheet1', rule_name='', batch_id='default', method='api')
         调取class Matcher的总流程。method可用'local' or 'api'. return 'fail' or 'success'.
     (2) 文件入口：process_file. 依次用process_table_api处理file_path里的每一张table.
     (3) 文件夹入口：process_dir. 依次用process_file处理dir_path里的每一个file.
     
    4. TODO List
    (1) 规范化日期，时间，金额等的格式和数据类型
    (2) 参照seperate_col()来写merge_col()，应对规范化的一列由原始数据两列合并的情况
    

analysis.py

    Class Analyzer为一个以公司为主体构建的object。
    
    流程
    1. run(name)为总入口。给定一个公司名，通过get_infos去mongo:Info/sheet_info里找该公司的所有表单的[file, table]作为file_path.
    2. 根据每个表单的file_path去mongo:Cache/mapped_df获取data，并依次做balance_check, benford_check, info_missing_check等。
    3. 汇总所有表单信息（已在上一步完成），并做dates_check, inner_account_check, 和cross_validation.
    4. 所有的结果按层储存在字典res里，并返回。
    
    TODO
    规范一下返回的res，全封装成字典的key:val形式。 
    
mydata.py
    
    matcher.py所需要的字典数据。
    包括目标栏目，目标数据项，数据项匹配关键词，基本规则模版，公司名匹配，中英文栏目对应等

report.py
    
    incomplete

requirements.txt
    
    当前目录下所需的python包
    生成：pipreqs . --encoding=utf8 --force
    安装：pip install -r requirements.txt
    
    
### Other

output: 生成的报表🏠

plot：生成的图表📈

report_hotpot.py

    年度报告 year_analysis(df)
    月度报告 month_analysis(df)
    大类分析 type_analysis(df)
    交易对手分析 provider_analysis(df)
    月度交易对手频次分析 provider_freq_analysis()
    新增流失交易方金额及占比分析 first_last_occur_analysis()
    
    
## MongoDB架构设计 🗄

    Mapping
        user_rule
            company: xxx
            rule_name: xxx
            A: A'
            B: B'
            ...
    Cache
        unmapped_df
            company: xxx
            file: xxx
            table: xxx
            batch_id: xxx
            data: xxx(df in json)
        mapped_df
            company: xxx
            file: xxx
            table: xxx
            batch_id: xxx
            data: xxx(df in json)
    Info
        sheet_info
            company: xxx
            file: xxx
            table: xxx
            batch_id: xxx
            ------
            self_name: 
            self_bank:
            currency:
            start_date:
            end_date:
            gen_date:
            init_balance:
            self_account:
            transactions_num: 
    