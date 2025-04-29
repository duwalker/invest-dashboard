from dash import Dash, html, dcc, dash_table, Input, Output, State
import dash_bootstrap_components as dbc  # 添加这行
import os  # 添加这行
import json  # 添加这行
from src.data_processor import DataProcessor
from src.chart_factory import ChartFactory
from src.config import COLORS
import pandas as pd
import plotly.graph_objects as go
import dash
from portfolio import get_stock_prices  # 添加这行

# 初始化应用
app = Dash(
    __name__, 
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.DARKLY],  # 添加深色主题
    title='风险投资驾驶舱',
)

# 初始化数据处理器和图表工厂    
data_processor = DataProcessor('portfolio_market_value.csv')
chart_factory = ChartFactory(data_processor)

# 定义统一的选项卡样式
tab_style = {
    'backgroundColor': COLORS['background'],
    'color': COLORS['text'],  # 未选中状态的文字颜色
    'padding': '10px',
    'margin': '5px',
    'borderRadius': '5px',
    'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)' 
}

selected_tab_style = {
    'backgroundColor': '#007bff',  # 选中状态的背景颜色
    'color': 'white',  # 选中状态的文字颜色
    'padding': '10px',
    'margin': '5px',
    'borderRadius': '5px',
    'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)' 
}

# 创建布局
app.layout = html.Div([
    html.Div([
        html.Div([
            # 添加隐形组件
            html.Div(style={'width': '200px', 'display': 'inline-block'}),  # 根据日期选择器的宽度调整此值
            
            html.H1('风险投资驾驶舱', 
                id='dashboard-title',
                style={
                    'textAlign': 'center',
                    'color': COLORS['text'],
                    'padding': '20px',
                    'margin': '0',
                    'backgroundColor': COLORS['background'],
                    'flexGrow': 1
                }
            ),
            dcc.DatePickerSingle(
                id='date-picker',
                min_date_allowed=data_processor.df['Date'].min(),
                initial_visible_month=data_processor.df['Date'].max(),
                date=data_processor.df['Date'].max(),
                style={
                    'backgroundColor': COLORS['background'],
                    'color': COLORS['text'],  # 日期选择器文字颜色改为白色
                    'border': 'none',  # 去掉边框
                    'padding': '10px',
                    'margin': '5px',
                    'borderRadius': '5px',
                    'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)' 
                }
            ),
        ], style={
            'display': 'flex',
            'alignItems': 'center',  # 垂直居中对齐
            'justifyContent': 'space-between',  # 左右对齐
            'width': '100%',
            'backgroundColor': COLORS['background'],
        }),
    ], style={
        'display': 'flex',
        'alignItems': 'center',  # 垂直居中对齐
        'justifyContent': 'flex-start',  # 左对齐
        'width': '100%',
        'backgroundColor': COLORS['background'],
    }),
    html.Div([
        html.Div([
            html.Div([
                html.H3('当日盈亏金额', 
                    id='profit-loss-header',
                    style={
                        'color': COLORS['text'], 
                        'textAlign': 'center', 
                        'cursor': 'pointer',
                        'fontSize': '16px'  # 添加字体大小
                    }
                ),
                html.P(
                    id='daily-profit-loss',
                    children=f"{data_processor.daily_profit_loss:.2f}元" if data_processor.daily_profit_loss is not None else "N/A",
                    style={
                        'color': 'red' if data_processor.daily_profit_loss > 0 else 'green' if data_processor.daily_profit_loss < 0 else COLORS['text'],
                        'textAlign': 'center',
                        'cursor': 'pointer',
                        'fontSize': '14px'  # 添加字体大小
                    }
                ),
            ], style={'width': '17%', 'display': 'inline-block'}),
            
            html.Div([
                html.H3('当日收益率', 
                    style={
                        'color': COLORS['text'], 
                        'textAlign': 'center',
                        'fontSize': '16px'  # 添加字体大小
                    }
                ),
                html.P(
                    id='daily-return',
                    children=f"{data_processor.daily_return:.2%}" if data_processor.daily_return is not None else "N/A",
                    style={
                        'color': COLORS['text'], 
                        'textAlign': 'center',
                        'fontSize': '14px'  # 添加字体大小
                    }
                )
            ], style={'width': '8%', 'display': 'inline-block'}),

            html.Div([
                html.H3('当前净值', 
                    id='net-value-header',
                    style={
                        'color': COLORS['text'], 
                        'textAlign': 'center', 
                        'cursor': 'pointer',
                        'fontSize': '16px'  # 添加字体大小
                    }
                ),
                html.P(
                    id='daily-net-value',
                    children=f"{data_processor.daily_net_value.values[0]:.4f}" if not data_processor.daily_net_value.empty else "N/A",
                    style={
                        'color': COLORS['text'], 
                        'textAlign': 'center', 
                        'cursor': 'pointer',
                        'fontSize': '14px'  # 添加字体大小
                    }
                )
            ], style={'width': '52%', 'display': 'inline-block'}),
            
            html.Div([
                html.H3('最大回撤', 
                    style={
                        'color': COLORS['text'], 
                        'textAlign': 'center',
                        'fontSize': '16px'  # 添加字体大小
                    }
                ),
                html.P(
                    children=f"{data_processor.max_drawdown:.2%}", 
                    style={
                        'color': COLORS['text'], 
                        'textAlign': 'center',
                        'fontSize': '14px'  # 添加字体大小
                    }
                ),
            ], style={'width': '8%', 'display': 'inline-block'}),
            
            html.Div([
                html.H3('当前回撤', 
                    style={
                        'color': COLORS['text'], 
                        'textAlign': 'center',
                        'fontSize': '16px'  # 添加字体大小
                    }
                ),
                html.P(
                    children=f"{data_processor.current_drawdown:.2%}",
                    style={
                        'color': COLORS['text'], 
                        'textAlign': 'center',
                        'fontSize': '14px'  # 添加字体大小
                    }
                )
            ], style={'width': '15%', 'display': 'inline-block'})
        ], style={
            'width': '100%',
            'display': 'flex',
            'alignItems': 'center',
            'borderBottom': 'none'  # 去掉上面的灰色线条
        })
    ], style={
        'width': '100%',
        'backgroundColor': COLORS['background'],
        'padding': '0px',
        'margin': '0px',
        'borderRadius': '5px',
        'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)', 
        'display': 'flex',  # 添加 flex 布局
        'justifyContent': 'flex-start'  # 将内容推到最左边
    }),
    
    # 第一行：三列布局
    html.Div([
        html.Div([
            html.H3('当日收益率红黑榜', 
                style={
                    'color': COLORS['text'], 
                    'textAlign': 'center',
                    'fontSize': '16px',  # 减小标题字体大小
                    'margin': '0px',  # 减小标题边距
                    'padding': '5px 0'  # 只保留上下padding
                }
            ),
            dcc.Graph(
                id='returns-chart', 
                figure=chart_factory.fig_returns, 
                config={'displayModeBar': False},
                style={
                    'height': '300px',
                    'margin': '0px',  # 去掉图表边距
                    'padding': '0px'  # 去掉图表内边距
                }
            )
        ], style={
            'width': '35%',
            'display': 'inline-block',
            'backgroundColor': COLORS['background'],
            'padding': '0px',  # 减小内边距
            'margin': '0px 5px 0px 0px',  # 只保留右边距
            'borderRadius': '5px',
            'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)' 
        }),
        
        html.Div([
            dcc.Tabs([
                dcc.Tab(
                    label='总净值趋势',
                    children=[
                        dcc.Graph(
                            figure=chart_factory.fig_total, 
                            config={'displayModeBar': False},
                            style={
                                'height': '300px',
                                'margin': '0px',  # 去掉图表边距
                                'padding': '0px'  # 去掉图表内边距
                            }
                        )
                    ],
                    style=tab_style,
                    selected_style=selected_tab_style
                ),
                dcc.Tab(
                    label='策略净值趋势',
                    children=[
                        dcc.Graph(
                            figure=chart_factory.fig_nav, 
                            config={'displayModeBar': False},
                            style={
                                'height': '300px',
                                'margin': '0px',
                                'padding': '0px'
                            }
                        )
                    ],
                    style=tab_style,
                    selected_style=selected_tab_style
                ),
                dcc.Tab(
                    label='风格净值趋势',
                    children=[
                        dcc.Graph(
                            figure=chart_factory.fig_style_nav, 
                            config={'displayModeBar': False},
                            style={
                                'height': '300px',
                                'margin': '0px',
                                'padding': '0px'
                            }
                        )
                    ],
                    style=tab_style,
                    selected_style=selected_tab_style
                ),
            ])
        ], style={
            'width': '64%',
            'display': 'inline-block',
            'backgroundColor': COLORS['background'],
            'padding': '0px',  # 减小内边距
            'margin': '0px',  # 去掉所有外边距
            'borderRadius': '5px',
            'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)' 
        })
    ], style={
        'backgroundColor': '#161a1d',
        'padding': '0px',  # 减小上下间距
        'textAlign': 'center',
        'display': 'flex',
        'justifyContent': 'flex-start',
        'alignItems': 'stretch',
        'gap': '5px',  # 保持元素之间的间距
        'margin': '0px'  # 去掉外边距
    }),
    
    # 第二行：两列布局（饼图和回撤分析）
    html.Div([
        html.Div(
            dcc.Tabs(
                id='pie-tabs',
                children=[
                    dcc.Tab(
                        label='策略配比',
                        children=[
                            dcc.Graph(
                                id='fig-pie', 
                                figure=chart_factory.create_style_pie_chart(), 
                                config={'displayModeBar': False},
                                style={'height': '450px'}  # 调整饼图高度与表格一致
                            )
                        ],
                        style=tab_style,
                        selected_style=selected_tab_style
                    ),
                    dcc.Tab(
                        label='风格配比',
                        children=[
                            dcc.Graph(
                                id='style-pie', 
                                figure=chart_factory.create_style_pie_chart(), 
                                config={'displayModeBar': False},
                                style={'height': '450px'}  # 调整饼图高度与表格一致
                            )
                        ],
                        style=tab_style,
                        selected_style=selected_tab_style
                    ),
                    dcc.Tab(
                        label='持仓占比',
                        children=[
                            dcc.Graph(
                                id='style-position-pie', 
                                figure=chart_factory.create_style_position_pie_chart(), 
                                config={'displayModeBar': False},
                                style={'height': '450px'}  # 调整饼图高度与表格一致
                            )
                        ],
                        style=tab_style,
                        selected_style=selected_tab_style
                    )
                ]
            ),
            style={'width': '35%', 'display': 'inline-block', 'verticalAlign': 'top', 'margin': '0px 5px 0px 0px'}  # 调整外边距
        ),
        
        html.Div(
            dcc.Tabs(
                id='drawdown-tabs',
                children=[
                    dcc.Tab(
                        label='策略绩效分析',
                        children=[
                            dash_table.DataTable(
                                id='strategy-drawdown-table',
                                data=data_processor.display_df.to_dict('records'),
                                columns=[
                                    {'name': '策略', 'id': '策略'},
                                    {'name': '总市值', 'id': '总市值', 'type': 'numeric', 'format': {'specifier': ',.2f'}},
                                    {'name': '持仓市值', 'id': '持仓市值', 'type': 'numeric', 'format': {'specifier': ',.2f'}},
                                    {'name': '仓位', 'id': '仓位', 'type': 'numeric', 'format': {'specifier': '.2%'}},
                                    {'name': '年化收益率', 'id': '年化收益率', 'type': 'numeric', 'format': {'specifier': '.2%'}},
                                    {'name': '最大回撤', 'id': '最大回撤', 'type': 'numeric', 'format': {'specifier': '.2%'}},
                                    {'name': '当前回撤', 'id': '当前回撤', 'type': 'numeric', 'format': {'specifier': '.2%'}}
                                ],
                                style_data_conditional=[
                                    {
                                        'if': {'row_index': 'odd'},
                                        'backgroundColor': '#252e3f'
                                    },
                                    {
                                        'if': {
                                            'filter_query': '{当前回撤} < -0.1',
                                            'column_id': '当前回撤'
                                        },
                                        'color': 'red'
                                    },
                                    {
                                        'if': {
                                            'filter_query': '{最大回撤} < -0.15',
                                            'column_id': '最大回撤'
                                        },
                                        'color': 'red'
                                    },
                                    {
                                        'if': {
                                            'filter_query': '{仓位} > 0.95',
                                            'column_id': '仓位'
                                        },
                                        'color': 'red'
                                    }
                                ],
                                style_table={
                                    'height': '450px',
                                    'overflowY': 'auto'
                                },
                                style_cell={
                                    'backgroundColor': COLORS['background'],
                                    'color': COLORS['text'],
                                    'border': f'1px solid {COLORS["grid"]}',
                                    'padding': '10px',
                                    'textAlign': 'left'
                                },
                                style_header={
                                    'backgroundColor': COLORS['grid'],
                                    'fontWeight': 'bold',
                                    'border': f'1px solid {COLORS["grid"]}'
                                },
                                sort_action='native'  # 添加排序功能
                            )
                        ],
                        style=tab_style,
                        selected_style=selected_tab_style
                    ),
                    dcc.Tab(
                        label='风格绩效分析',
                        children=[
                            dash_table.DataTable(
                                id='style-drawdown-table',
                                data=data_processor.get_style_drawdowns().to_dict('records'),
                                columns=[
                                    {'name': '风格', 'id': '风格'},
                                    {'name': '总市值', 'id': '总市值', 'type': 'numeric', 'format': {'specifier': ',.2f'}},
                                    {'name': '持仓市值', 'id': '持仓市值', 'type': 'numeric', 'format': {'specifier': ',.2f'}},
                                    {'name': '配置比例', 'id': '配置比例', 'type': 'numeric', 'format': {'specifier': '.2%'}},
                                    {'name': '年化收益率', 'id': '年化收益率', 'type': 'numeric', 'format': {'specifier': '.2%'}},
                                    {'name': '最大回撤', 'id': '最大回撤', 'type': 'numeric', 'format': {'specifier': '.2%'}},
                                    {'name': '当前回撤', 'id': '当前回撤', 'type': 'numeric', 'format': {'specifier': '.2%'}}
                                ],
                                style_data_conditional=[
                                    {
                                        'if': {'row_index': 'odd'},
                                        'backgroundColor': '#252e3f'
                                    },
                                    {
                                        'if': {
                                            'filter_query': '{当前回撤} < -0.1',
                                            'column_id': '当前回撤'
                                        },
                                        'color': 'red'
                                    },
                                    {
                                        'if': {
                                            'filter_query': '{最大回撤} < -0.15',
                                            'column_id': '最大回撤'
                                        },
                                        'color': 'red'
                                    },
                                    {
                                        'if': {
                                            'filter_query': '{配置比例} > 0.3',
                                            'column_id': '配置比例'
                                        },
                                        'color': 'red'
                                    }
                                ],
                                style_table={
                                    'height': '450px',
                                    'overflowY': 'auto'
                                },
                                style_cell={
                                    'backgroundColor': COLORS['background'],
                                    'color': COLORS['text'],
                                    'border': f'1px solid {COLORS["grid"]}',
                                    'padding': '10px',
                                    'textAlign': 'left'
                                },
                                style_header={
                                    'backgroundColor': COLORS['grid'],
                                    'fontWeight': 'bold',
                                    'border': f'1px solid {COLORS["grid"]}'
                                },
                                sort_action='native'  # 添加排序功能
                            )
                        ],
                        style=tab_style,
                        selected_style=selected_tab_style
                    ),
                    dcc.Tab(
                        label='账户持仓明细',
                        children=[
                            dash_table.DataTable(
                                id='holdings-table',
                                data=[],  # 初始为空，通过回调更新
                                columns=[
                                    {'name': '证券代码', 'id': '股票代码'},
                                    {'name': '证券名称', 'id': '股票名称'},  
                                    {'name': '持仓数量', 'id': '持仓数量', 'type': 'numeric'},
                                    {'name': '当前价', 'id': '当前价', 'type': 'numeric', 'format': {'specifier': ',.2f'}},
                                    {'name': '持股市值', 'id': '持股市值', 'type': 'numeric', 'format': {'specifier': ',.3f'}},
                                    {'name': '当日涨幅', 'id': '当日涨幅', 'type': 'numeric', 'format': {'specifier': '.2%'}}
                                ],
                                style_table={
                                    'height': '450px',
                                    'overflowY': 'auto'
                                },
                                style_cell={
                                    'backgroundColor': COLORS['background'],
                                    'color': COLORS['text'],
                                    'border': f'1px solid {COLORS["grid"]}',
                                    'padding': '10px',
                                    'textAlign': 'left'
                                },
                                style_header={
                                    'backgroundColor': COLORS['grid'],
                                    'fontWeight': 'bold',
                                    'border': f'1px solid {COLORS["grid"]}'
                                },
                                style_data_conditional=[
                                    {
                                        'if': {'row_index': 'odd'},
                                        'backgroundColor': '#252e3f'
                                    },
                                    {
                                        'if': {
                                            'filter_query': '{当日涨幅} > 0',
                                            'column_id': '当日涨幅'
                                        },
                                        'color': 'red'
                                    },
                                    {
                                        'if': {
                                            'filter_query': '{当日涨幅} < 0',
                                            'column_id': '当日涨幅'
                                        },
                                        'color': 'green'
                                    }
                                ],
                                sort_action='native'  # 添加排序功能
                            )
                        ],
                        style=tab_style,
                        selected_style=selected_tab_style
                    ),
                    # 新增持仓对比Tab
                    dcc.Tab(
                        label='持仓对比',
                        children=[
                            dash_table.DataTable(
                                id='holdings-compare-table',
                                data=[],  # 初始为空，通过回调更新
                                columns=[
                                    {'name': '股票代码', 'id': '股票代码'},
                                    {'name': '股票名称', 'id': '股票名称'},  # 添加股票名称列
                                    {'name': '账户持仓', 'id': '账户持仓', 'type': 'numeric'},
                                    {'name': '实际持仓', 'id': '实际持仓', 'type': 'numeric'},
                                    {'name': '差异', 'id': '差异', 'type': 'numeric'}
                                ],
                                style_table={
                                    'height': '450px',
                                    'overflowY': 'auto'
                                },
                                style_cell={
                                    'backgroundColor': COLORS['background'],
                                    'color': COLORS['text'],
                                    'border': f'1px solid {COLORS["grid"]}',
                                    'padding': '10px',
                                    'textAlign': 'left'
                                },
                                style_header={
                                    'backgroundColor': COLORS['grid'],
                                    'fontWeight': 'bold',
                                    'border': f'1px solid {COLORS["grid"]}'
                                },
                                style_data_conditional=[
                                    {
                                        'if': {'row_index': 'odd'},
                                        'backgroundColor': '#252e3f'
                                    },
                                    {
                                        'if': {
                                            'filter_query': '{差异} != 0',
                                            'column_id': '差异'
                                        },
                                        'color': 'red'
                                    }
                                ]
                            )
                        ],
                        style=tab_style,
                        selected_style=selected_tab_style
                    ),
                ]
            ),
            style={'width': '64%', 'display': 'inline-block', 'backgroundColor': COLORS['background'], 'padding': '5px', 'margin': '0px', 'borderRadius': '5px', 'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)', 'verticalAlign': 'top'}
        )
    ], style={
        'backgroundColor': '#161a1d',
        'padding': '0px',  # 减小上下间距
        'textAlign': 'center',
        'display': 'flex',
        'justifyContent': 'flex-start',
        'alignItems': 'stretch',
        'gap': '5px',
        'marginTop': '5px'  # 减小与上面一行的间距
    }),

    # 添加弹出框组件
    dbc.Modal(  # 修改这里
        id='daily-details-modal',
        children=[
            dbc.ModalHeader("策略盈亏详情"),
            dbc.ModalBody(
                dash_table.DataTable(
                    id='daily-details-table',
                    style_table={'height': '400px', 'overflowY': 'auto'},
                    style_cell={
                        'backgroundColor': COLORS['background'],
                        'color': COLORS['text'],
                        'border': f'1px solid {COLORS["grid"]}',
                        'padding': '10px',
                        'textAlign': 'left'
                    },
                    style_header={
                        'backgroundColor': COLORS['grid'],
                        'fontWeight': 'bold'
                    },
                    style_data_conditional=[{
                        'if': {'row_index': 'odd'},
                        'backgroundColor': '#252e3f'
                    }]
                )
            )
        ],
        centered=True,
        style={'backgroundColor': COLORS['background']}
    ),
    
    dbc.Modal(  # 这里也要修改
        id='nav-contribution-modal',
        children=[
            dbc.ModalHeader("策略净值贡献"),
            dbc.ModalBody(
                dash_table.DataTable(
                    id='nav-contribution-table',
                    style_table={'height': '400px', 'overflowY': 'auto'},
                    style_cell={
                        'backgroundColor': COLORS['background'],
                        'color': COLORS['text'],
                        'border': f'1px solid {COLORS["grid"]}',
                        'padding': '10px',
                        'textAlign': 'left'
                    },
                    style_header={
                        'backgroundColor': COLORS['grid'],
                        'fontWeight': 'bold'
                    },
                    style_data_conditional=[{
                        'if': {'row_index': 'odd'},
                        'backgroundColor': '#252e3f'
                    }]
                )
            )
        ],
        centered=True,
        style={'backgroundColor': COLORS['background']}
    ),

    # 新增风格策略详情模态框
    dbc.Modal(
        id='style-details-modal',
        children=[
            dbc.ModalHeader(id='style-details-header'),
            dbc.ModalBody([
                # 添加两列布局
                dbc.Row([
                    # 左侧表格
                    dbc.Col(
                        dash_table.DataTable(
                            id='style-details-table',
                            style_table={'height': '400px', 'overflowY': 'auto'},
                            style_cell={
                                'backgroundColor': COLORS['background'],
                                'color': COLORS['text'],
                                'border': f'1px solid {COLORS["grid"]}',
                                'padding': '10px',
                                'textAlign': 'left'
                            },
                            style_header={
                                'backgroundColor': COLORS['grid'],
                                'fontWeight': 'bold'
                            },
                            style_data_conditional=[{
                                'if': {'row_index': 'odd'},
                                'backgroundColor': '#252e3f'
                            }],
                            sort_action='native'  # 启用排序功能
                        ),
                        width=8
                    ),
                    # 右侧饼图
                    dbc.Col(
                        dcc.Graph(
                            id='style-details-pie',
                            config={'displayModeBar': False},
                            style={'height': '400px'}
                        ),
                        width=4
                    )
                ])
            ])
        ],
        centered=True,
        size='xl',  # 使用更大的模态框
        style={'backgroundColor': COLORS['background']}
    ),

    # 新增策略持仓明细模态框
    dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("策略持仓明细")),
            dbc.ModalBody([
                dash_table.DataTable(
                    id='strategy-holdings-table',
                    columns=[
                        {'name': '证券代码', 'id': 'code'},
                        {'name': '证券名称', 'id': 'name'},
                        {'name': '持仓数量', 'id': 'amount', 'type': 'numeric'},
                        {'name': '持仓市值', 'id': 'value', 'type': 'numeric', 'format': {'specifier': ',.2f'}},
                        {'name': '当前价', 'id': 'price', 'type': 'numeric', 'format': {'specifier': '.3f'}},
                        {'name': '当日涨幅', 'id': 'day_change', 'type': 'numeric', 'format': {'specifier': '.2%'}}
                    ],
                    style_table={'height': '400px', 'overflowY': 'auto'},
                    style_cell={
                        'backgroundColor': COLORS['background'],
                        'color': COLORS['text'],
                        'border': f'1px solid {COLORS["grid"]}',
                        'padding': '10px',
                        'textAlign': 'left'
                    },
                    style_header={
                        'backgroundColor': COLORS['grid'],
                        'fontWeight': 'bold',
                        'border': f'1px solid {COLORS["grid"]}'
                    },
                    style_data_conditional=[
                        {
                            'if': {'row_index': 'odd'},
                            'backgroundColor': '#252e3f'
                        },
                        {
                            'if': {
                                'filter_query': '{profit_ratio} > 0',
                                'column_id': 'profit_ratio'
                            },
                            'color': 'red'
                        },
                        {
                            'if': {
                                'filter_query': '{profit_ratio} < 0',
                                'column_id': 'profit_ratio'
                            },
                            'color': 'green'
                        },
                        {
                            'if': {
                                'filter_query': '{day_change} > 0',
                                'column_id': 'day_change'
                            },
                            'color': 'red'
                        },
                        {
                            'if': {
                                'filter_query': '{day_change} < 0',
                                'column_id': 'day_change'
                            },
                            'color': 'green'
                        }
                    ],
                    sort_action='native'  # 添加排序功能
                )
            ]),
            dbc.ModalFooter(
                dbc.Button("关闭", id="close-strategy-holdings", className="ms-auto")
            ),
        ],
        id="strategy-holdings-modal",
        size="lg",
    ),
], style={
    'backgroundColor': '#161a1d',
    'minHeight': '100vh',
    'margin': '0'
})

# 回调函数
@app.callback(
    [Output('returns-chart', 'figure'),
     Output('daily-return', 'children'),
     Output('daily-net-value', 'children'),
     Output('daily-profit-loss', 'children')],
    [Input('date-picker', 'date')]
)
def update_charts(selected_date):
    if selected_date:
        selected_date = pd.to_datetime(selected_date)
        
        # 获取选定日期数据
        selected_data = data_processor.df[data_processor.df['Date'] == selected_date]
        if selected_data.empty:
            return chart_factory.fig_returns, "N/A", "N/A", "N/A"
        
        # 计算当日收益率
        daily_return = (
            selected_data['MarketValue_close'] * selected_data['收益率']
        ).sum() / selected_data['MarketValue_close'].sum()
        
        # 更新收益率排名图（使用别名）
        selected_data = selected_data.copy()  # 创建副本再修改
        selected_data.loc[:, 'Strategy_Alias'] = selected_data['Strategy'].map(data_processor.get_strategy_alias)
        returns_sorted = selected_data.sort_values('收益率', ascending=False)
        top_5 = returns_sorted.head()
        bottom_5 = returns_sorted.tail()
        
        fig_returns = go.Figure()
        fig_returns.add_trace(go.Bar(
            x=top_5['Strategy_Alias'],
            y=top_5['收益率'],
            marker_color='#ff0000',
            text=[f"{val:.2%}" for val in top_5['收益率']],
            textposition='auto'
        ))
        fig_returns.add_trace(go.Bar(
            x=bottom_5['Strategy_Alias'],
            y=bottom_5['收益率'],
            marker_color='#00ff00',
            text=[f"{val:.2%}" for val in bottom_5['收益率']],
            textposition='auto'
        ))
        
        # 更新布局以去掉 X 轴和 Y 轴标签
        fig_returns.update_layout(
            **chart_factory.CHART_LAYOUT,
            showlegend=False,
            xaxis_title='',
            yaxis_title=''
        )
        
        # 计算净值，添加 include_groups=False 参数来修复废弃警告
        historical_data = data_processor.df[data_processor.df['Date'] <= selected_date]
        daily_returns = historical_data.groupby('Date', group_keys=False).apply(
            lambda x: (x['MarketValue_close'] * x['收益率']).sum() / x['MarketValue_close'].sum(),
            include_groups=False
        )
        nav = (1 + daily_returns).cumprod().iloc[-1]
        
        # 计算当日盈亏金额
        daily_profit_loss = (selected_data['MarketValue_close'] * selected_data['收益率']).sum().round(2)
        
        # 更新净值趋势图的布局以去掉 X 轴和 Y 轴标签
        chart_factory.fig_style_nav.update_layout(
            xaxis_title='',  # 去掉 X 轴标签
            yaxis_title=''   # 去掉 Y 轴标签
        )
        
        chart_factory.fig_nav.update_layout(
            xaxis_title='',  # 去掉 X 轴标签
            yaxis_title=''   # 去掉 Y 轴标签
        )
        
        chart_factory.fig_total.update_layout(
            xaxis_title='',  # 去掉 X 轴标签
            yaxis_title=''   # 去掉 Y 轴标签
        )
        
        return fig_returns, f"{daily_return:.2%}", f"{nav:.4f}", f"{daily_profit_loss:.2f}元"
    
    return chart_factory.fig_returns, "N/A", "N/A", "N/A"

@app.callback(
    Output('style-pie', 'figure'),
    Input('date-picker', 'date')
)
def update_style_pie_chart(selected_date):
    if (selected_date):
        selected_date = pd.to_datetime(selected_date)
        selected_data = data_processor.df[data_processor.df['Date'] == selected_date]
        if not selected_data.empty:
            style_market_value = {}
            for strategy_name, strategy_info in chart_factory.STRATEGY_STYLES.items():
                if 'styles' in strategy_info:
                    strategy_data = selected_data[selected_data['Strategy'] == strategy_name]
                    if not strategy_data.empty:
                        market_value = strategy_data['MarketValue_close'].sum()
                        if strategy_info['styles'][0] in style_market_value:
                            style_market_value[strategy_info['styles'][0]] += market_value
                        else:
                            style_market_value[strategy_info['styles'][0]] = market_value
            style_df = pd.DataFrame(list(style_market_value.items()), columns=['Style', 'MarketValue'])
            fig_style_pie = chart_factory.create_pie_chart(
                style_df,
                values='MarketValue',
                names='Style'
            )
            return fig_style_pie
    return chart_factory.fig_pie

# 新增回调函数，用于根据日期选择器更新市值占比饼图
@app.callback(
    Output('fig-pie', 'figure'),
    Input('date-picker', 'date')
)
def update_pie_chart(selected_date):
    if selected_date:
        selected_date = pd.to_datetime(selected_date)
        selected_data = data_processor.df[data_processor.df['Date'] == selected_date]
        if not selected_data.empty:
            selected_data = selected_data.copy()  # 创建副本再修改
            selected_data.loc[:, 'Strategy_Alias'] = selected_data['Strategy'].map(data_processor.get_strategy_alias)
            fig_pie = chart_factory.create_pie_chart(
                selected_data,
                values='MarketValue_close',
                names='Strategy_Alias'
            )
            return fig_pie
    return chart_factory.fig_pie

@app.callback(
    Output('daily-profit-loss', 'style'),
    Input('date-picker', 'date')
)
def update_profit_loss_style(selected_date):
    if selected_date:
        selected_date = pd.to_datetime(selected_date)
        selected_data = data_processor.df[data_processor.df['Date'] == selected_date]
        
        if not selected_data.empty:
            daily_profit_loss = (selected_data['MarketValue_close'] * selected_data['收益率']).sum()
            
            return {
                'color': 'red' if daily_profit_loss > 0 else 'green' if daily_profit_loss < 0 else COLORS['text'],
                'textAlign': 'center',
                'cursor': 'pointer',  # 添加鼠标指针样式
                'fontSize': '14px'  # 保持字体大小一致
            }
    
    return {
        'color': COLORS['text'],
        'textAlign': 'center',
        'cursor': 'pointer',  # 添加鼠标指针样式
        'fontSize': '14px'  # 保持字体大小一致
    }

@app.callback(
    Output('daily-return', 'style'),
    Input('date-picker', 'date')
)
def update_return_style(selected_date):
    if selected_date:
        selected_date = pd.to_datetime(selected_date)
        selected_data = data_processor.df[data_processor.df['Date'] == selected_date]
        
        if not selected_data.empty:
            daily_return = (
                selected_data['MarketValue_close'] * selected_data['收益率']
            ).sum() / selected_data['MarketValue_close'].sum()
            
            if daily_return > 0:
                return {'color': 'red', 'textAlign': 'center'}  # 正数为红色
            elif daily_return < 0:
                return {'color': 'green', 'textAlign': 'center'}  # 负数为绿色
            else:
                return {'color': COLORS['text'], 'textAlign': 'center'}  # 为零时使用默认颜色
    
    return {'color': COLORS['text'], 'textAlign': 'center'}  # 初始状态使用默认颜色

# 添加回调函数
@app.callback(
    [Output('daily-details-modal', 'is_open'),
     Output('daily-details-table', 'data'),
     Output('daily-details-table', 'columns')],
    [Input('profit-loss-header', 'n_clicks'),
     Input('daily-profit-loss', 'n_clicks'),
     Input('date-picker', 'date')],
    prevent_initial_call=True
)
def toggle_daily_details_modal(header_clicks, value_clicks, selected_date):
    if header_clicks is None and value_clicks is None:
        return False, [], []
        
    ctx = dash.callback_context
    if not ctx.triggered:
        return False, [], []
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if trigger_id not in ['profit-loss-header', 'daily-profit-loss']:
        return False, [], []
        
    if selected_date:
        selected_date = pd.to_datetime(selected_date)
        df = data_processor.get_daily_details(selected_date)
        
        columns = [
            {'name': '策略', 'id': '策略'},
            {'name': '市值', 'id': '市值', 'type': 'numeric', 'format': {'specifier': ',.2f'}},
            {'name': '收益率', 'id': '收益率', 'type': 'numeric', 'format': {'specifier': '.2%'}},
            {'name': '盈亏金额', 'id': '盈亏金额', 'type': 'numeric', 'format': {'specifier': ',.2f'}}
        ]
        
        return True, df.to_dict('records'), columns
    
    return False, [], []

@app.callback(
    [Output('nav-contribution-modal', 'is_open'),
     Output('nav-contribution-table', 'data'),
     Output('nav-contribution-table', 'columns')],
    [Input('net-value-header', 'n_clicks'),
     Input('daily-net-value', 'n_clicks')],
    prevent_initial_call=True
)
def toggle_nav_contribution_modal(header_clicks, value_clicks):
    if header_clicks is None and value_clicks is None:
        return False, [], []
    
    ctx = dash.callback_context
    if not ctx.triggered:
        return False, [], []
        
    df = data_processor.get_nav_contribution()
    columns = [
        {'name': '策略', 'id': '策略'},
        {'name': '净值贡献', 'id': '净值贡献', 'type': 'numeric', 'format': {'specifier': '.2%'}}
    ]
    
    return True, df.to_dict('records'), columns
    
@app.callback(
    Output('style-drawdown-table', 'data'),
    Input('date-picker', 'date')
)
def update_style_drawdown_table(selected_date):
    if selected_date:
        df = data_processor.get_style_drawdowns()
        # 计算总市值和持仓市值的总和
        total_row = {
            '风格': '总计',
            '总市值': df['总市值'].sum(),
            '持仓市值': df['持仓市值'].sum(),
            '配置比例': '',
            '年化收益率': '',
            '最大回撤': '',
            '当前回撤': ''
        }
        # 将总计行添加到数据中
        df_dict = df.to_dict('records')
        df_dict.append(total_row)
        return df_dict
    return []

@app.callback(
    Output('style-position-pie', 'figure'),
    Input('date-picker', 'date')
)
def update_style_position_pie_chart(selected_date):
    if selected_date:
        selected_date = pd.to_datetime(selected_date)
        selected_data = data_processor.df[data_processor.df['Date'] == selected_date]
        if not selected_data.empty:
            style_market_value = {}
            for strategy_name, strategy_info in chart_factory.STRATEGY_STYLES.items():
                if 'styles' in strategy_info:
                    strategy_data = selected_data[selected_data['Strategy'] == strategy_name]
                    if not strategy_data.empty:
                        # 使用 PositionValue 计算持仓市值
                        position_value = strategy_data['PositionValue'].sum()
                        if strategy_info['styles'][0] in style_market_value:
                            style_market_value[strategy_info['styles'][0]] += position_value
                        else:
                            style_market_value[strategy_info['styles'][0]] = position_value
            style_df = pd.DataFrame(list(style_market_value.items()), columns=['Style', 'MarketValue'])
            fig_style_position_pie = chart_factory.create_pie_chart(
                style_df,
                values='MarketValue',
                names='Style'
            )
            return fig_style_position_pie
    return chart_factory.create_pie_chart(pd.DataFrame(columns=['Style', 'MarketValue']), values='MarketValue', names='Style')

# 新增回调函数处理持仓数据
@app.callback(
    Output('holdings-table', 'data'),
    Input('date-picker', 'date')
)
def update_holdings_table(selected_date):
#    import json
#    from portfolio import get_stock_prices
    
    # 获取项目根目录下的 holdings 文件夹中的所有 txt 文件
    holdings_dir = os.path.join(os.path.dirname(__file__), 'holdings')
    holdings_files = [f for f in os.listdir(holdings_dir) if f.endswith('.txt')]
    
    # 合并持仓数据
    holdings = {}
    code2name = {}  # 用于存储股票代码到名称的映射
    
    for file in holdings_files:
        with open(os.path.join(holdings_dir, file), 'r', encoding='utf-8') as f:
            account_data = json.load(f)
            for account in account_data.values():
                if 'holding' in account:
                    for stock_code, quantity in account['holding'].items():
                        code = stock_code  # 保持完整的股票代码格式（包含.SZ/.SH）
                        if code in holdings:
                            holdings[code] += quantity
                        else:
                            holdings[code] = quantity

    # 获取所有股票的价格
    with open(r'c:\qmt_record\cookies.txt', 'r') as f:
        cookies = json.load(f)
        cookie = cookies['xueqiu']  # 获取雪球的cookie
    
    prices = get_stock_prices(list(holdings.keys()), cookie)

    # 计算市值并创建排序后的数据
    holdings_data = []
    for code, quantity in holdings.items():
        stock_data = prices.get(code, {})
        holdings_data.append({
            '股票代码': code,
            '股票名称': stock_data.get('name', ''),  # 使用 get 方法安全获取
            '当前价': stock_data.get('lastPrice', 0),
            '持仓数量': quantity,
            '持股市值': round(quantity * stock_data.get('lastPrice', 0), 2),
            '当日涨幅': stock_data.get('changePercent', 0) / 100 if stock_data.get('changePercent') is not None else 0
        })
    
    # 按持股市值降序排序
    holdings_data = sorted(holdings_data, key=lambda x: x['持股市值'], reverse=True)
    
    return holdings_data

# 新增回调函数：持仓对比
@app.callback(
    Output('holdings-compare-table', 'data'),
    Input('date-picker', 'date')
)
def update_holdings_compare_table(selected_date):
#    import json
    import re
    # 账户持仓明细
    holdings_dir = os.path.join(os.path.dirname(__file__), 'holdings')
    holdings_files = [f for f in os.listdir(holdings_dir) if f.endswith('.txt')]
    holdings = {}
    code2name = {}
    for file in holdings_files:
        with open(os.path.join(holdings_dir, file), 'r', encoding='utf-8') as f:
            account_data = json.load(f)
            for account in account_data.values():
                if 'holding' in account:
                    for stock_code, quantity in account['holding'].items():
                        code = str(stock_code).split('.')[0]
                        if code in holdings:
                            holdings[code] += quantity
                        else:
                            holdings[code] = quantity
                        # 记录名称
                        if 'holding_name' in account and stock_code in account['holding_name']:
                            code2name[code] = account['holding_name'][stock_code]
    # 读取holdings.tsv，建立证券代码到证券名称的映射
    code_name_map = {}
    actual_df = pd.read_csv('holdings.tsv', sep='\t', dtype=str)
    if '证券代码' in actual_df.columns and '证券名称' in actual_df.columns:
        for _, row in actual_df.iterrows():
            code = str(row['证券代码']).split('.')[0]
            name = row['证券名称']
            code_name_map[code] = name

    actual_df['证券代码'] = actual_df['证券代码'].astype(str).str.split('.').str[0]
    actual_df['当前拥股'] = actual_df['当前拥股'].astype(str).str.replace(r'[^\d]', '', regex=True).astype(int)
    actual_map = dict(zip(actual_df['证券代码'], actual_df['当前拥股']))
    # 合并所有股票代码
    all_codes = set(holdings.keys()) | set(actual_map.keys())
    result = []
    for code in sorted(all_codes):
        account_qty = holdings.get(code, 0)
        actual_qty = actual_map.get(code, 0)
        diff = account_qty - actual_qty
        result.append({
            '股票代码': code,
            '股票名称': code_name_map.get(code, code2name.get(code, '')),
            '账户持仓': account_qty,
            '实际持仓': actual_qty,
            '差异': diff
        })
    # 只显示有差异的
    result = [row for row in result if row['差异'] != 0]
    return result

# 新增风格详情回调函数
@app.callback(
    [Output('style-details-modal', 'is_open'),
     Output('style-details-header', 'children'),
     Output('style-details-table', 'data'),
     Output('style-details-table', 'columns'),
     Output('style-details-pie', 'figure')],
    [Input('style-drawdown-table', 'active_cell'),
     Input('style-drawdown-table', 'derived_virtual_data')],  # 添加 derived_virtual_data 输入
    prevent_initial_call=True
)
def show_style_details(active_cell, derived_virtual_data):
    if active_cell is None or derived_virtual_data is None:
        return False, "", [], [], {}
    
    # 获取选中的风格
    row = derived_virtual_data[active_cell['row']]  # 使用 derived_virtual_data 而不是 table_data
    style = row['风格']
    
    # 如果点击的是总计行，不显示详情
    if style == '总计':
        return False, "", [], [], {}
    
    # 获取该风格下的所有策略详情
    strategies_data = []
    total_value = 0

    # 获取属于这个风格的所有策略原始名称
    style_strategies = []
    
    if style == '三年以内':
        # 使用当前日期
        current_date = pd.Timestamp.now()
        # 读取 cubevalue.txt 获取创建时间信息
        with open('cubevalue.txt', 'r') as f:
            cubevalue = json.load(f)
        
        # 查找三年内的雪球策略
        for strategy_name, info in data_processor.STRATEGY_STYLES.items():
            if 'styles' in info and '雪球' in info['styles']:
                if strategy_name in cubevalue and 'create_time' in cubevalue[strategy_name]:
                    create_time = pd.Timestamp(cubevalue[strategy_name]['create_time'])
                    days_diff = (current_date - create_time).days
                    if days_diff <= 1095:  # 3年 * 365天
                        style_strategies.append(strategy_name)
    else:
        # 对于其他风格，从 STRATEGY_STYLES 中查找
        style_strategies = [k for k, v in data_processor.STRATEGY_STYLES.items() 
                          if 'styles' in v and style in v['styles']]
    
    # 从原始数据中获取策略数据
    latest_date = data_processor.df['Date'].max()
    latest_data = data_processor.df[data_processor.df['Date'] == latest_date]
    
    for strategy_name in style_strategies:
        strategy_data = data_processor.df[data_processor.df['Strategy'] == strategy_name]
        if not strategy_data.empty:
            latest_strategy_data = latest_data[latest_data['Strategy'] == strategy_name]
            if not latest_strategy_data.empty:
                latest_strategy_data = latest_strategy_data.iloc[0]
                
                # 计算年化收益率和回撤
                strategy_nav = (1 + strategy_data['收益率']).cumprod()
                max_dd, curr_dd = data_processor.calculate_drawdown(strategy_nav)
                total_days = (strategy_data['Date'].max() - strategy_data['Date'].min()).days
                total_return = strategy_nav.iloc[-1] - 1
                annual_return = (1 + total_return) ** (365 / total_days) - 1 if total_days > 0 else 0.0
                
                strategies_data.append({
                    '策略': data_processor.get_strategy_alias(strategy_name),  # 显示别名
                    '总市值': latest_strategy_data['MarketValue_close'],
                    '持仓市值': latest_strategy_data['PositionValue'],
                    '仓位': latest_strategy_data['PositionValue'] / latest_strategy_data['MarketValue_close'] if latest_strategy_data['MarketValue_close'] > 0 else 0,
                    '年化收益率': annual_return,
                    '最大回撤': max_dd,
                    '当前回撤': curr_dd
                })
                total_value += latest_strategy_data['MarketValue_close']
    
    # 如果没有找到任何策略数据，返回空结果
    if not strategies_data:
        return True, f"{style}风格策略详情 (无数据)", [], [], {}
    
    # 创建表格列定义
    columns = [
        {'name': '策略', 'id': '策略'},
        {'name': '总市值', 'id': '总市值', 'type': 'numeric', 'format': {'specifier': ',.2f'}},
        {'name': '持仓市值', 'id': '持仓市值', 'type': 'numeric', 'format': {'specifier': ',.2f'}},
        {'name': '仓位', 'id': '仓位', 'type': 'numeric', 'format': {'specifier': '.2%'}},
        {'name': '年化收益率', 'id': '年化收益率', 'type': 'numeric', 'format': {'specifier': '.2%'}},
        {'name': '最大回撤', 'id': '最大回撤', 'type': 'numeric', 'format': {'specifier': '.2%'}},
        {'name': '当前回撤', 'id': '当前回撤', 'type': 'numeric', 'format': {'specifier': '.2%'}}
    ]
    
    # 创建饼图数据
    pie_data = pd.DataFrame(strategies_data)
    pie_figure = chart_factory.create_pie_chart(
        pie_data,
        values='总市值',
        names='策略'
    )
    
    return True, f"{style}风格策略详情", strategies_data, columns, pie_figure

# 修改策略持仓明细回调函数
@app.callback(
    Output('strategy-holdings-modal', 'is_open'),
    Output('strategy-holdings-table', 'data'),
    Input('strategy-drawdown-table', 'active_cell'),
    Input('close-strategy-holdings', 'n_clicks'),
    State('strategy-drawdown-table', 'derived_virtual_data'),  # 使用 derived_virtual_data 而不是 data
    prevent_initial_call=True
)
def show_strategy_holdings(active_cell, close_clicks, derived_virtual_data):
    ctx = dash.callback_context
    if not ctx.triggered:
        return False, []
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger_id == 'close-strategy-holdings':
        return False, []
        
    if active_cell is None or derived_virtual_data is None:
        return False, []
        
    strategy_alias = derived_virtual_data[active_cell['row']]['策略']  # 使用 derived_virtual_data 获取当前行的数据
    
    # 通过别名找到实际的策略名称
    actual_strategy_name = None
    for strategy_id, strategy_info in data_processor.STRATEGY_STYLES.items():
        if strategy_info.get('alias') == strategy_alias:
            actual_strategy_name = strategy_id
            break
    
    # 如果没有找到别名对应的策略，尝试直接使用策略名称
    if actual_strategy_name is None:
        actual_strategy_name = strategy_alias
    
    # 从xueqiu.txt、guoren.txt等文件中读取策略持仓数据
    holdings_data = []
    
    # 根据策略名称判断应该从哪个文件读取数据
    if actual_strategy_name.startswith('ZH'):
        # 雪球策略
        try:
            with open('holdings/xueqiu.txt', 'r', encoding='utf-8') as f:
                xueqiu_data = json.load(f)
                if actual_strategy_name in xueqiu_data:
                    strategy_holdings = xueqiu_data[actual_strategy_name].get('holding', {})
                    for code, amount in strategy_holdings.items():
                        holdings_data.append({
                            'code': code,
                            'name': get_stock_name(code),
                            'amount': amount,
                            'value': 0,
                            'cost': 0,
                            'price': 0,
                            'profit_ratio': 0,
                            'day_change': 0
                        })
        except Exception as e:
            print(f"Error reading xueqiu.txt: {e}")
    elif actual_strategy_name.startswith('8844.R.'):
        # 果仁策略
        try:
            with open('holdings/guoren.txt', 'r', encoding='utf-8') as f:
                guoren_data = json.load(f)
                if actual_strategy_name in guoren_data:
                    strategy_holdings = guoren_data[actual_strategy_name].get('holding', {})
                    for code, amount in strategy_holdings.items():
                        holdings_data.append({
                            'code': code,
                            'name': get_stock_name(code),
                            'amount': amount,
                            'value': 0,
                            'cost': 0,
                            'price': 0,
                            'profit_ratio': 0,
                            'day_change': 0
                        })
        except Exception as e:
            print(f"Error reading guoren.txt: {e}")
    elif actual_strategy_name in ['etfdl', 'etfdl2', 'etfdl3', 'ylxy']:
        # ETF动量策略和月历效应
        try:
            with open(f'holdings/{actual_strategy_name}.txt', 'r', encoding='utf-8') as f:
                strategy_data = json.load(f)
                if actual_strategy_name in strategy_data:
                    strategy_holdings = strategy_data[actual_strategy_name].get('holding', {})
                    for code, amount in strategy_holdings.items():
                        holdings_data.append({
                            'code': code,
                            'name': get_stock_name(code),
                            'amount': amount,
                            'value': 0,
                            'cost': 0,
                            'price': 0,
                            'profit_ratio': 0,
                            'day_change': 0
                        })
        except Exception as e:
            print(f"Error reading {actual_strategy_name}.txt: {e}")
    else:
        # 聚宽策略
        try:
            with open('holdings/joinquant.txt', 'r', encoding='utf-8') as f:
                joinquant_data = json.load(f)
                if actual_strategy_name in joinquant_data:
                    strategy_holdings = joinquant_data[actual_strategy_name].get('holding', {})
                    for code, amount in strategy_holdings.items():
                        holdings_data.append({
                            'code': code,
                            'name': get_stock_name(code),
                            'amount': amount,
                            'value': 0,
                            'cost': 0,
                            'price': 0,
                            'profit_ratio': 0,
                            'day_change': 0
                        })
        except Exception as e:
            print(f"Error reading joinquant.txt: {e}")
    
    # 获取所有股票的实时价格和涨跌幅
    if holdings_data:
        try:
            with open(r'c:\qmt_record\cookies.txt', 'r') as f:
                cookies = json.load(f)
                cookie = cookies['xueqiu']  # 获取雪球的cookie
            
            # 获取所有股票代码
            stock_codes = [item['code'] for item in holdings_data]
            prices = get_stock_prices(stock_codes, cookie)
            
            # 更新持仓数据
            for item in holdings_data:
                stock_data = prices.get(item['code'], {})
                last_price = stock_data.get('lastPrice', 0)
                change_percent = stock_data.get('changePercent', 0) / 100 if stock_data.get('changePercent') is not None else 0
                
                item['price'] = last_price
                item['value'] = round(item['amount'] * last_price, 2)
                item['day_change'] = change_percent
        except Exception as e:
            print(f"Error fetching stock prices: {e}")
        
    return True, holdings_data

def get_stock_name(code):
    """从holdings.tsv中获取股票名称"""
    try:
        with open('holdings.tsv', 'r', encoding='utf-8') as f:
            for line in f:
                fields = line.strip().split('\t')
                if len(fields) > 7 and fields[7] == code.split('.')[0]:
                    return fields[8]
    except Exception as e:
        print(f"Error reading holdings.tsv: {e}")
    return code

if __name__ == '__main__':
    app.run_server(debug=True)