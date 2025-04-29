import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any
from .config import COLORS, CHART_LAYOUT, STRATEGY_STYLES  # 添加 STRATEGY_STYLES 导入

class ChartFactory:
    """图表工厂类，用于创建和管理所有图表"""
    
    def __init__(self, data_processor=None):
        """初始化图表工厂，创建所有初始图表"""
        self.data_processor = data_processor
        self.CHART_LAYOUT = CHART_LAYOUT
        self.STRATEGY_STYLES = STRATEGY_STYLES  # 保存为实例变量
        
        # 创建初始图表
        if data_processor is not None:
            self.init_figures()
        else:
            self.create_empty_figures()
    
    def init_figures(self):
        """初始化所有图表"""
        try:
            # 获取最新日期数据并创建完整的副本
            latest_date = self.data_processor.df['Date'].max()
            latest_data = self.data_processor.df[self.data_processor.df['Date'] == latest_date].copy()  # 创建完整副本
            
            # 1. 收益率排名图（使用别名）
            latest_data.loc[:, 'Strategy_Alias'] = latest_data['Strategy'].map(self.data_processor.get_strategy_alias)
            latest_returns = latest_data.sort_values('收益率', ascending=False)
            top_5 = latest_returns.head()
            bottom_5 = latest_returns.tail()
            
            self.fig_returns = go.Figure()
            self.fig_returns.add_trace(go.Bar(
                x=top_5['Strategy_Alias'],
                y=top_5['收益率'],
                marker_color='#ff0000'
            ))
            self.fig_returns.add_trace(go.Bar(
                x=bottom_5['Strategy_Alias'],
                y=bottom_5['收益率'],
                marker_color='#00ff00'
            ))
            self.fig_returns.update_layout(**self.CHART_LAYOUT, showlegend=False)
            
            # 2. 市值占比饼图（使用别名）
            self.fig_pie = self.create_pie_chart(
                latest_data,
                values='MarketValue_close',
                names='Strategy_Alias'
            )
            
            # 3. 风格净值趋势图
            style_data = []
            # 从 STRATEGY_STYLES 中获取风格列表
            all_styles = set()
            for v in self.STRATEGY_STYLES.values():
                if 'styles' in v:
                    all_styles.update(v['styles'])
            for style in all_styles:
                style_strategies = [k for k, v in self.STRATEGY_STYLES.items() 
                                  if 'styles' in v and style in v['styles']]
                if style_strategies:
                    style_data_temp = self.data_processor.df[
                        self.data_processor.df['Strategy'].isin(style_strategies)
                    ].copy()
                    style_data_temp['风格'] = style
                    style_data.append(style_data_temp)
            
            if style_data:
                style_df = pd.concat(style_data)
                style_grouped = style_df.groupby(['Date', '风格']).apply(
                    lambda x: (x['MarketValue_close'] * x['收益率']).sum() / x['MarketValue_close'].sum()
                ).reset_index(name='收益率')
                style_grouped['净值'] = style_grouped.groupby('风格')['收益率'].transform(
                    lambda x: (1 + x).cumprod()
                )
                
                self.fig_style_nav = px.line(
                    style_grouped,
                    x='Date',
                    y='净值',
                    color='风格'
                )
                self.fig_style_nav.update_layout(**self.CHART_LAYOUT, showlegend=False)
            else:
                self.fig_style_nav = go.Figure()
                self.fig_style_nav.update_layout(**self.CHART_LAYOUT)
            
            # 4. 策略净值趋势图
            nav_data = self.data_processor.df.copy()
            nav_data['Strategy_Alias'] = nav_data['Strategy'].map(self.data_processor.get_strategy_alias)
            self.fig_nav = px.line(
                nav_data,
                x='Date',
                y='净值',
                color='Strategy_Alias'
            )
            self.fig_nav.update_layout(**self.CHART_LAYOUT, showlegend=False)
            
            # 5. 总净值趋势图
            total_returns = self.data_processor.df.groupby('Date').apply(
                lambda x: (x['MarketValue_close'] * x['收益率']).sum() / x['MarketValue_close'].sum()
            )
            total_nav = pd.DataFrame({
                'Date': total_returns.index,
                '总净值': (1 + total_returns).cumprod()
            })
            self.fig_total = px.line(total_nav, x='Date', y='总净值')
            self.fig_total.update_layout(**self.CHART_LAYOUT, showlegend=False)
            
        except Exception as e:
            print(f"创建图表时出错: {str(e)}")
            self.create_empty_figures()
    
    def create_empty_figures(self):
        """创建空图表"""
        self.fig_returns = go.Figure()
        self.fig_pie = go.Figure()
        self.fig_nav = go.Figure()
        self.fig_style_nav = go.Figure()
        self.fig_total = go.Figure()
        
        for fig in [self.fig_returns, self.fig_pie, self.fig_nav, 
                   self.fig_style_nav, self.fig_total]:
            fig.update_layout(**self.CHART_LAYOUT)
    
    def create_pie_chart(self, data: pd.DataFrame, values: str, names: str) -> go.Figure:
        """创建饼图"""
        fig = px.pie(data, values=values, names=names)
        fig.update_layout(**self.CHART_LAYOUT, showlegend=False)
        return fig
    
    @staticmethod
    def create_line_chart(data: pd.DataFrame, x: str, y: str, color: str = None) -> go.Figure:
        """创建折线图"""
        fig = px.line(data, x=x, y=y, color=color)
        fig.update_layout(**CHART_LAYOUT)
        return fig
    
    @staticmethod
    def create_returns_chart(top_5: pd.DataFrame, bottom_5: pd.DataFrame) -> go.Figure:
        """创建收益率排名图"""
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=top_5['Strategy'], 
            y=top_5['收益率'],
            name='收益率最高的5个策略',
            marker_color='#00ff00'
        ))
        fig.add_trace(go.Bar(
            x=bottom_5['Strategy'], 
            y=bottom_5['收益率'],
            name='收益率最低的5个策略',
            marker_color='#ff0000'
        ))
        fig.update_layout(
            **CHART_LAYOUT,
            showlegend=True,
            bargap=0.3,
            yaxis_title='收益率',
            xaxis_title=''
        )
        return fig
    
    @staticmethod
    def create_nav_chart(data: pd.DataFrame) -> go.Figure:
        """创建净值趋势图"""
        fig = px.line(data, x='Date', y='净值', color='Strategy_Alias')
        fig.update_layout(
            **CHART_LAYOUT,
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            )
        )
        return fig
    
    @staticmethod
    def create_total_nav_chart(data: pd.DataFrame) -> go.Figure:
        """创建总净值趋势图"""
        fig = px.line(data, x='Date', y='MarketValue_close')
        fig.update_layout(
            **CHART_LAYOUT,
            showlegend=False,
            yaxis_title='市值'
        )
        return fig

    def create_style_pie_chart(self):
        # 1. 初始化一个字典来存储每种风格的总市值
        style_market_value = {}

        # 2. 遍历所有策略
        for strategy_name, strategy_info in self.STRATEGY_STYLES.items():
            if 'styles' in strategy_info and strategy_info['styles']:
                # 获取该策略的第一种风格
                key_style = strategy_info['styles'][0]
                
                # 筛选出与该风格相关的数据
                filtered_data = self.data_processor.df[self.data_processor.df['Strategy'] == strategy_name]
                
                # 计算该风格的合计市值
                total_market_value = filtered_data['MarketValue_close'].sum()
                
                # 将结果存储到字典中
                style_market_value[key_style] = style_market_value.get(key_style, 0) + total_market_value

        # 3. 创建饼图
        fig = go.Figure(data=[go.Pie(
            labels=list(style_market_value.keys()),
            values=list(style_market_value.values()),
            hole=0.4  # 如果需要，可以设置为环形图
        )])
        
        # 更新布局以匹配策略市值占比饼图的样式
        fig.update_layout(
            title_text='',  # 去掉标题
            showlegend=False,  # 去掉图例
            margin=dict(l=0, r=0, t=0, b=0),  # 去掉外部边距
            paper_bgcolor='rgba(0,0,0,0)',  # 设置背景透明
            plot_bgcolor='rgba(0,0,0,0)'  # 设置绘图区域背景透明
        )
        
        return fig

    def create_style_position_pie_chart(self):
        # 1. 初始化一个字典来存储每种风格的总市值
        style_position_value = {}

        # 2. 遍历所有策略
        for strategy_name, strategy_info in self.STRATEGY_STYLES.items():
            if 'styles' in strategy_info and strategy_info['styles']:
                # 获取该策略的第一种风格
                key_style = strategy_info['styles'][0]
                
                # 筛选出与该风格相关的数据
                filtered_data = self.data_processor.df[self.data_processor.df['Strategy'] == strategy_name]
                # 计算该风格的合计市值
                total_position_value = filtered_data['PositionValue'].sum()
                
                # 将结果存储到字典中
                style_position_value[key_style] = style_position_value.get(key_style, 0) + total_position_value

        # 3. 创建饼图
        fig = go.Figure(data=[go.Pie(
            labels=list(style_position_value.keys()),
            values=list(style_position_value.values()),
            hole=0.4  # 如果需要，可以设置为环形图
        )])
        
        # 更新布局以匹配策略市值占比饼图的样式
        fig.update_layout(
            title_text='',  # 去掉标题
            showlegend=False,  # 去掉图例
            margin=dict(l=0, r=0, t=0, b=0),  # 去掉外部边距
            paper_bgcolor='rgba(0,0,0,0)',  # 设置背景透明
            plot_bgcolor='rgba(0,0,0,0)'  # 设置绘图区域背景透明
        )
        
        return fig
