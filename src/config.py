from typing import Dict, Any

# 主题配置
COLORS = {
    'background': '#1f2630',
    'text': '#ffffff',
    'grid': '#2c3543',
    'line': '#00ff00',
    'pie': ['#003f5c', '#58508d', '#bc5090', '#ff6361', '#ffa600']
}

# 图表通用布局
CHART_LAYOUT = {
    'paper_bgcolor': COLORS['background'],
    'plot_bgcolor': COLORS['background'],
    'font': {'color': COLORS['text']},
    'margin': dict(l=10, r=10, t=30, b=10),
    'xaxis': {
        'showgrid': True,
        'gridcolor': COLORS['grid'],
        'gridwidth': 0.5,
        'title': {'text': '日期'}
    },
    'yaxis': {
        'showgrid': True,
        'gridcolor': COLORS['grid'],
        'gridwidth': 0.5,
        'title': {'text': '净值'}
    }
}

# 策略配置
STRATEGY_STYLES: Dict[str, Dict[str, Any]] = {
    'etfdl': {
        'alias': 'ETF动量',
        'styles': ['ETF', 'ETF动量']
    },
    'etfdl2': {
        'alias': 'ETF动量2',
        'styles': ['ETF', 'ETF动量']
    },
    'etfdl3': {
        'alias': 'ETF动量3',
        'styles': ['ETF', 'ETF动量']
    },
    'ylxy': {
        'alias': '月历效应',
        'styles': ['ETF', '机会主义']
    },
    '8844.R.326830530113226': {
        'alias': '微盘股5只',
        'styles': ['小市值', '果仁']
    },
    '8844.R.305501425337631': {
        'alias': '复合择时小市值',
        'styles': ['小市值', '果仁']
    },
    '8844.R.298227688848438': {
        'alias': '小市值不败3空1月',
        'styles': ['小市值', '果仁']
    },
    '8844.R.300656029599491': {
        'alias': '风控小市值10股',
        'styles': ['小市值', '果仁']
    },
    '8844.R.309613265818925': {
        'alias': '择时超跌反弹',
        'styles': ['超跌反弹', '小市值', '果仁']
    },
    '8844.R.310592645488656': {
        'alias': '择时超跌反弹聚宽',
        'styles': ['超跌反弹', '小市值', '果仁']
    },
    'ZH2991860': {
        'alias': '可转债10',
        'styles': ['可转债', '雪球']
    },
    'ZH2507815': {
        'alias': '三低妖债增强',
        'styles': ['可转债', '雪球']
    },
    'ZH699736': {
        'alias': 'A股市场收息组合',
        'styles': ['高股息', '雪球']
    },
    'ZH1324567': {
        'alias': 'only_you',
        'styles': ['机会主义', '雪球']
    },
    'ZH1233086': {
        'alias': '寶盛源投资',
        'styles': ['成长股', '雪球']
    },
    'ZH1223264': {
        'alias': '雄鹰新价值一号',
        'styles': ['成长股', '雪球']
    },
    'ZH1232362': {
        'alias': '2018A股',
        'styles': ['白马股', '雪球']
    },
    'ZH1350829': {
        'alias': '大匡哥',
        'styles': ['机会主义', '雪球']
    },
    'ZH2952718': {
        'alias': '转债多因子',
        'styles': ['可转债', '雪球']
    },
    'ZH3054156': {
        'alias': '刺激债',
        'styles': ['可转债', '雪球']
    },
    'ZH3068836': {
        'alias': '多因子轮动',
        'styles': ['可转债', '雪球']
    },
    'ZH2930797': {
        'alias': '可转债防守反击',
        'styles': ['可转债', '雪球']
    },
    'ZH2091747': {
        'alias': '吃股息养老',
        'styles': ['高股息','白马股', '雪球']
    },
    'ZH2349311': {
        'alias': '05自己玩',
        'styles': ['白马股', '雪球']
    },
    'ZH1741493': {
        'alias': '易斋多因子轮动',
        'styles': ['可转债', '雪球']
    },
    'ZH3185220': {
        'alias': '只做st',
        'styles': ['机会主义', '雪球']
    },
    'ZH3126148': {
        'alias': '静悄悄',
        'styles': ['白马股', '雪球']
    },
    'ZH3312874': {
        'alias': '超跌反弹',
        'styles': ['超跌反弹', '雪球']
    },
    'ZH2325126': {
        'alias': '银金地工New',
        'styles': ['白马股', '雪球']
    },
    'ZH1387155': {
        'alias': '豪座2019',
        'styles': ['成长股', '雪球']
    },
    'ZH1173996': {
        'alias': '通通锁住',
        'styles': ['成长股', '雪球']
    },
    'ZH1397802': {
        'alias': '煎大饼模拟实盘',
        'styles': ['成长股', '雪球']
    },
    'ZH1913612': {
        'alias': '看看会怎样',
        'styles': ['机会主义', '雪球']
    },
    'ZH2102101': {
        'alias': '架子投资',
        'styles': ['机会主义', '雪球']
    },
    'ZH1846169': {
        'alias': '锄禾不舍春',
        'styles': ['机会主义', '雪球']
    },
    'ZH2528619': {
        'alias': '转债随缘操作',
        'styles': ['可转债', '雪球']
    },
    'ZH2489831': {
        'alias': '葛洲坝',
        'styles': ['白马股', '雪球']
    },
    'ZH2508271': {
        'alias': '成语接龙',
        'styles': ['成长股', '雪球']
    },
    'ZH3262001': {
        'alias': '我不是韭菜',
        'styles': ['机会主义', '成长股', '雪球']
    },
    'ZH3180498': {
        'alias': '低位埋伏',
        'styles': ['超跌反弹', '雪球']
    },
    'ZH3300166': {
        'alias': '小柿子',
        'styles': ['小市值', '雪球']
    },
    'ZH3282378': {
        'alias': '满仓ETF',
        'styles': ['ETF', '雪球']
    },
    'ZH3187330': {
        'alias': '去码头整点薯条',
        'styles': ['白马股', '雪球']
    },
    '涨停低开': {
        'styles': ['机会主义', '聚宽']
    },
    'PB策略': {
        'styles': ['白马股', '聚宽']
    },
    '国九条优化': {
        'styles': ['小市值', '聚宽']
    },
    '差不多得了1_2_17': {
        'styles': ['小市值','差不多得了', '聚宽']
    },
    '差不多得了10': {
        'styles': ['小市值','差不多得了', '聚宽']
    },
    '行业宽度择时小市值': {
        'styles': ['小市值', '聚宽']
    },
    '小市值择时再优化': {
        'styles': ['小市值', '聚宽']
    }   
    # ... 其他策略配置 ...
}