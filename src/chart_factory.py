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
                # 设置每个风格线条的悬停模板，不显示日期
                for trace in self.fig_style_nav.data:
                    trace.hovertemplate = '%{fullData.name}: %{y:.4f}<extra></extra>'
                
                self.fig_style_nav.update_layout(**self.CHART_LAYOUT, showlegend=False)
                # 设置风格净值趋势图的交互模式为x轴统一显示
                self.fig_style_nav.update_layout(hovermode='x unified')
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
                '总收益率': (1 + total_returns).cumprod() - 1  # 转换为收益率格式（净值-1）
            }).reset_index(drop=True)  # 重置索引，确保Date只作为列存在
            self.fig_total = px.line(total_nav, x='Date', y='总收益率')
            # 设置总收益率的悬停模板，不显示日期
            for trace in self.fig_total.data:
                trace.hovertemplate = '总收益率: %{y:.2%}<extra></extra>'  # 更新为百分比格式
            
            self.fig_total.update_layout(
                **self.CHART_LAYOUT,
                showlegend=True,  # 显示图例
                legend=dict(
                    orientation="h",  # 水平布局
                    yanchor="bottom",
                    y=1.02,  # 将图例放在图表上方
                    xanchor="right",
                    x=1
                )
            )
            
            # 添加沪深300基准线到总净值趋势图
            csi300_data = self.data_processor.get_csi300_data()
            if not csi300_data.empty:
                # 计算沪深300收益率（净值-1）
                csi300_data = csi300_data.copy()
                csi300_data['收益率'] = csi300_data['净值'] - 1
                
                # 添加沪深300收益率线，显示日期
                self.fig_total.add_trace(go.Scatter(
                    x=csi300_data['Date'],
                    y=csi300_data['收益率'],
                    name='沪深300',
                    line=dict(
                        color='#808080',  # 灰色
                        width=2,
                        dash='dash'  # 虚线
                    ),
                    mode='lines',
                    hovertemplate='%{x|%Y-%m-%d}<br>沪深300: %{y:.2%}<extra></extra>'  # 更新为百分比格式
                ))
                
                # 添加超额收益线 - 计算总收益率相对于沪深300的超额收益
                # 首先确保日期匹配
                common_dates = set(total_nav['Date']).intersection(set(csi300_data['Date']))
                if common_dates:
                    # 筛选共同日期的数据并复制出新的DataFrame，避免修改原始数据
                    filtered_total = total_nav[total_nav['Date'].isin(common_dates)].copy().sort_values('Date')
                    filtered_csi300 = csi300_data[csi300_data['Date'].isin(common_dates)].copy().sort_values('Date')
                    
                    # 创建包含超额收益的数据框，确保Date不是索引
                    excess_return_df = pd.DataFrame({
                        'Date': filtered_total['Date'].values,
                        '超额收益': filtered_total['总收益率'].values - filtered_csi300['收益率'].values
                    })
                    
                    # 添加超额收益线
                    self.fig_total.add_trace(go.Scatter(
                        x=excess_return_df['Date'],
                        y=excess_return_df['超额收益'],
                        name='超额收益',
                        line=dict(
                            color='#00ff00',  # 绿色
                            width=2
                        ),
                        mode='lines',
                        hovertemplate='%{x|%Y-%m-%d}<br>超额收益: %{y:.2%}<extra></extra>'  # 更新为百分比格式
                    ))
                
                # 设置交互模式为x轴统一显示
                self.fig_total.update_layout(hovermode='x unified')
            
            # 设置风格净值趋势图的交互模式为x轴统一显示
            if style_data and not csi300_data.empty:
                # 修改所有风格线条的悬停模板，不显示日期
                for trace in self.fig_style_nav.data:
                    trace.hovertemplate = '%{fullData.name}: %{y:.4f}<extra></extra>'
                
                # 添加沪深300，显示日期
                self.fig_style_nav.add_trace(go.Scatter(
                    x=csi300_data['Date'],
                    y=csi300_data['净值'],
                    name='沪深300',
                    line=dict(
                        color='#808080',  # 灰色
                        width=2,
                        dash='dash'  # 虚线
                    ),
                    mode='lines',
                    hovertemplate='%{x|%Y-%m-%d}<br>沪深300: %{y:.4f}<extra></extra>'
                ))
                # 设置交互模式为x轴统一显示
                self.fig_style_nav.update_layout(hovermode='x unified')
            
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

    def create_net_value_trend_chart(self, start_date=None, end_date=None):
        """创建净值趋势图"""
        try:
            # 获取策略数据
            strategy_data = self.data_processor.get_strategy_data(start_date, end_date)
            if strategy_data.empty:
                return None
            
            # 获取沪深300数据
            csi300_data = self.data_processor.get_csi300_data(start_date, end_date)
            print(f"沪深300数据: {len(csi300_data)} 条记录")
            
            # 创建图表
            fig = go.Figure()
            
            # 添加策略净值线
            for strategy in strategy_data['Strategy'].unique():
                strategy_df = strategy_data[strategy_data['Strategy'] == strategy]
                style = self.data_processor.STRATEGY_STYLES.get(strategy, {})
                fig.add_trace(go.Scatter(
                    x=strategy_df['Date'],
                    y=strategy_df['NetValue'],
                    name=style.get('alias', strategy),
                    line=dict(
                        color=style.get('color', '#000000'),
                        width=style.get('line_width', 2),
                        dash=style.get('line_style', 'solid')
                    ),
                    mode='lines'
                ))
            
            # 添加沪深300指数线
            if not csi300_data.empty:
                print("添加沪深300基准线")
                fig.add_trace(go.Scatter(
                    x=csi300_data['Date'],
                    y=csi300_data['净值'],
                    name='沪深300',
                    line=dict(
                        color='#808080',  # 灰色
                        width=2,
                        dash='dash'
                    ),
                    mode='lines'
                ))
            
            # 设置图表布局
            fig.update_layout(
                title='净值趋势',
                xaxis_title='日期',
                yaxis_title='净值',
                hovermode='x unified',
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                margin=dict(l=50, r=50, t=50, b=50),
                height=400
            )
            
            return fig
            
        except Exception as e:
            print(f"创建净值趋势图时出错: {str(e)}")
            return None
