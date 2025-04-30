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
    'etfdl2': {
        'alias': 'ETF动量', # 策略的别名，显示在各种图表中，不设置别名则显示策略名称
        'styles': ['ETF', 'ETF动量']
    }, # 这里定义策略的别名和风格，只有第一种风格会统计在风格配比饼图、持仓占比饼图和风格绩效分析表格里。
    'ylxy': {
        'alias': '月历效应',
        'styles': ['ETF', '机会主义']
    },
    '8844.R.00000000001': {
        'alias': '微盘股',
        'styles': ['小市值', '果仁']
    },
    'ZH0000001': {
        'alias': '什么都不容易',
        'styles': ['白马股', '雪球']
    },
    '打板': {
        'styles': ['机会主义', '聚宽']
    }   
    # ... 其他策略配置 ...
}