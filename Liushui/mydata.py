
"""
All the data variables:
"""
target_headers = ['交易日期', '交易时间', '本方名称', '本方账号', '本方银行', '对方名称',
                          '对方账号', '交易类型', '摘要', '流入金额', '流出金额', '交易后余额', '系统分类']

target_summary = ['开始日期', '结束日期', '货币种类', '流水条数', '流入总额', '流出总额']


keywords_dict = {
            'header_key': ['摘要', '交易类型', '交易时间', '日期', '备注', '交易日期', '对方账号'],
            'self_bank': ['本方银行'],
            'self_name': ['公司名称'],
            'self_account': ['银行帐号', '银行账号'],
            'start_date': ['查询开始日期'],
            'end_date': ['查询结束日期'],
            'init_balance': ['对帐单期初余额'],
            'gen_date': ['生成日期'],
            'currency': ['帐户币种', '账户币种'],
        }


mapping_rules = {  # 可以多对一，在后面匹配上后reverse便形成一对一，不冲突
            'type': 'base_rule',
            '交易日': '交易日期',
            '交易时间': '交易时间',
            '收/付方名称': '对方名称',
            '收/付方帐号': '对方账号',
            '交易类型': '交易类型',
            '摘要': '摘要',
            '备注': '摘要',
            '贷方金额': '流入金额',
            '借方金额': '流出金额',
            '余额': '交易后余额',
            '收取金额': '流入金额',
            '汇入金额': '流入金额',
            '汇出金额': '流出金额',
            '支出金额': '流出金额',
            '账户余额': '交易后余额',
            '对方户名': '对方名称',
            '对方账号': '对方账号',
        }


name_mapping = {  # 之后可以考虑用头四个字转拼音来生成collection名字
            '上海爱钛技术咨询有限公司': 'aitai',
            '宜昌华昊新材料科技有限公司': 'huahao',
            '浙江亿控自动化设备有限公司': 'yikong',
            '上海同普电力技术有限公司': 'tongpu',
            '爱钛': 'aitai',
            '华昊': 'huahao',
            '亿控': 'yikong',
            '同普': 'tongpu',
        }


english_mapping = {
            '交易日期': 'date',
            '交易时间': 'time',
            '本方名称': 'sender_name',
            '本方账号': 'sender_account',
            '本方银行': 'sender_bank',
            '对方名称': 'receiver_name',
            '对方账号': 'receiver_account',
            '交易类型': 'type',
            '摘要': 'abstract',
            '流入金额': 'received_amount',
            '流出金额': 'sent_amount',
            '交易后余额': 'balance',
            '系统分类': 'system_classification'
        }