import pandas as pd
import numpy as np
from typing import Tuple, Dict
from functools import lru_cache
from .config import STRATEGY_STYLES
import plotly.graph_objects as go
import plotly.express as px
import json

class DataProcessor:
    def __init__(self, file_path):
        """初始化数据处理器"""
        self.STRATEGY_STYLES = STRATEGY_STYLES
        try:
            self.df = self._load_and_process_data(file_path)
            self.strategy_aliases = {k: v.get('alias', k) for k, v in self.STRATEGY_STYLES.items()}
            self.daily_profit_loss = None  # 新增 daily_profit_loss 属性
            self._calculate_daily_metrics()
            self.update_drawdown_analysis()  # 确保在初始化时调用该方法
            self.csi300_data = self._load_csi300_data()  # 加载沪深300数据
        except Exception as e:
            print(f"初始化数据处理器时出错: {str(e)}")
            self._init_empty_metrics()
    
    def _load_and_process_data(self, file_path: str) -> pd.DataFrame:
        """加载数据并进行预处理"""
        try:
            # 读取数据
            print(f"正在读取文件: {file_path}")
            df = pd.read_csv(file_path, encoding='ansi')
            print("列名:", df.columns.tolist())
            
            # 确保必要的列存在
            required_columns = ['Date', 'MarketValue', 'PositionValue', 'Strategy', 'Time']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"缺少必要的列: {missing_columns}")
            
            # 数据类型转换
            df['Date'] = pd.to_datetime(df['Date'])
            df['MarketValue'] = pd.to_numeric(df['MarketValue'], errors='coerce')
            df['PositionValue'] = pd.to_numeric(df['PositionValue'], errors='coerce')
            
            # 处理盘前盘后数据
            pre_open = df[df['Time'] == 'pre_open'].copy()
            close = df[df['Time'] == 'close'].copy()
            
            if pre_open.empty or close.empty:
                print("警告: 没有找到盘前或盘后数据")
                return pd.DataFrame()
            
            # 计算日收益率
            result = pd.DataFrame()
            for date in pre_open['Date'].unique():
                date_pre = pre_open[pre_open['Date'] == date]
                date_close = close[close['Date'] == date]
                
                for strategy in date_pre['Strategy'].unique():
                    pre_value = date_pre[date_pre['Strategy'] == strategy]['MarketValue'].iloc[0]
                    try:
                        close_value = date_close[date_close['Strategy'] == strategy]['MarketValue'].iloc[0]
                        position_value = date_close[date_close['Strategy'] == strategy]['PositionValue'].iloc[0]
                        daily_return = (close_value - pre_value) / pre_value if pre_value != 0 else 0
                        
                        result = pd.concat([result, pd.DataFrame({
                            'Date': [date],
                            'Strategy': [strategy],
                            'MarketValue_pre': [pre_value],
                            'MarketValue_close': [close_value],
                            'PositionValue': [position_value],
                            '收益率': [daily_return]
                        })])
                    except IndexError:
                        print(f"警告: {date} 的策略 {strategy} 缺少盘后数据")
            
            result = result.reset_index(drop=True)
            
            # 计算策略净值
            result['净值'] = result.groupby('Strategy')['收益率'].transform(
                lambda x: (1 + x).cumprod()
            )
            
            print(f"数据处理完成，共 {len(result)} 条记录")
            return result
            
        except Exception as e:
            print(f"加载数据时出错: {str(e)}")
            return pd.DataFrame()
    
    def _calculate_daily_metrics(self):
        """计算当日指标"""
        if self.df.empty:
            self._init_empty_metrics()
            return
            
        latest_date = self.df['Date'].max()
        latest_data = self.df[self.df['Date'] == latest_date]
        
        # 计算当日组合收益率（按市值加权）
        self.daily_return = (
            latest_data['MarketValue_close'] * latest_data['收益率']
        ).sum() / latest_data['MarketValue_close'].sum()

        # 计算当日组合盈亏金额（元）
        self.daily_profit_loss = (
            latest_data['MarketValue_close'] * latest_data['收益率']
        ).sum().round(2)
        
        # 计算历史累计收益率
        historical_returns = self.df.groupby('Date').apply(
            lambda x: (x['MarketValue_close'] * x['收益率']).sum() / x['MarketValue_close'].sum()
        )
        
        # 计算组合净值
        self.daily_net_value = (1 + historical_returns).cumprod()
        
        # 计算回撤
        self.max_drawdown, self.current_drawdown = self.calculate_drawdown(self.daily_net_value)
        
        # 准备显示数据
        self.display_df = self._prepare_display_data()
    
    def _init_empty_metrics(self):
        """初始化空指标"""
        self.df = pd.DataFrame(columns=['Date', 'Strategy', 'MarketValue_pre', 'MarketValue_close', 'PositionValue', '收益率', '净值'])
        self.daily_return = None
        self.daily_net_value = pd.Series([1.0])
        self.max_drawdown = 0.0
        self.current_drawdown = 0.0
        self.display_df = pd.DataFrame(columns=['策略', '最大回撤', '当前回撤'])
        self.daily_profit_loss = None  # 新增 daily_profit_loss 属性
    
    def calculate_drawdown(self, nav_series: pd.Series) -> Tuple[float, float]:
        """计算最大回撤和当前回撤"""
        if nav_series.empty:
            return 0.0, 0.0
        
        peak = nav_series.expanding(min_periods=1).max()
        drawdown = (nav_series - peak) / peak
        max_drawdown = drawdown.min()
        current_drawdown = drawdown.iloc[-1]
        
        return max_drawdown, current_drawdown
    
    def calculate_daily_profit_loss(self, selected_date):
        # 假设已经有一个方法来计算每日盈亏
        # 这里只是一个示例，实际计算逻辑需要根据具体需求实现
        selected_data = self.df[self.df['Date'] == selected_date]
        if not selected_data.empty:
            self.daily_profit_loss = (
                (selected_data['MarketValue_close'] * selected_data['收益率']).sum()
            )
        else:
            self.daily_profit_loss = None
    
    def _prepare_display_data(self) -> pd.DataFrame:
        """准备显示用的数据框"""
        latest_date = self.df['Date'].max()
        latest_data = self.df[self.df['Date'] == latest_date]
        strategies = latest_data['Strategy'].unique()
        
        display_data = []
        for strategy in strategies:
            strategy_data = self.df[self.df['Strategy'] == strategy]
            latest_strategy_data = latest_data[latest_data['Strategy'] == strategy].iloc[0]
            strategy_nav = (1 + strategy_data['收益率']).cumprod()
            max_dd, curr_dd = self.calculate_drawdown(strategy_nav)
            total_days = (strategy_data['Date'].max() - strategy_data['Date'].min()).days
            total_return = strategy_nav.iloc[-1] - 1
            annual_return = (1 + total_return) ** (365 / total_days) - 1 if total_days > 0 else 0.0
            
            display_data.append({
                '策略': self.get_strategy_alias(strategy),
                '年化收益率': annual_return,
                '最大回撤': max_dd,
                '当前回撤': curr_dd,
                '总市值': latest_strategy_data['MarketValue_close'],
                '持仓市值': latest_strategy_data['PositionValue'],
                '仓位': latest_strategy_data['PositionValue'] / latest_strategy_data['MarketValue_close'] if latest_strategy_data['MarketValue_close'] > 0 else 0
            })
        
        df = pd.DataFrame(display_data)
        return df.sort_values('总市值', ascending=False)  # 按总市值降序排序
    
    def get_strategy_alias(self, strategy: str) -> str:
        """获取策略别名"""
        return self.strategy_aliases.get(strategy, strategy)

    def init_figures(self):
        """初始化所有图表"""
        try:
            # 获取最新日期数据
            latest_date = self.df['Date'].max()
            latest_data = self.df[self.df['Date'] == latest_date]

            # 计算每日总市值，确保不重复计算
            daily_total_market_value = latest_data.groupby('Date')['MarketValue_close'].sum().reset_index()
            daily_total_position_value = latest_data.groupby('Date')['PositionValue'].sum().reset_index()
            # 1. 收益率排名图（使用别名）
            latest_data['Strategy_Alias'] = latest_data['Strategy'].map(self.get_strategy_alias)
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
                    style_data_temp = self.df[
                        self.df['Strategy'].isin(style_strategies)
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
            nav_data = self.df.copy()
            nav_data['Strategy_Alias'] = nav_data['Strategy'].map(self.get_strategy_alias)
            self.fig_nav = px.line(
                nav_data,
                x='Date',
                y='净值',
                color='Strategy_Alias'
            )
            self.fig_nav.update_layout(**self.CHART_LAYOUT, showlegend=False)

            # 5. 总净值趋势图
            total_returns = self.df.groupby('Date').apply(
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
    
    def get_daily_details(self, date) -> pd.DataFrame:
        """获取指定日期的各策略盈亏详情"""
        date_data = self.df[self.df['Date'] == date].copy()
        if date_data.empty:
            return pd.DataFrame()
            
        date_data['Strategy_Alias'] = date_data['Strategy'].map(self.get_strategy_alias)
        date_data['盈亏金额'] = (date_data['MarketValue_close'] - date_data['MarketValue_pre']).round(2)
        
        result = pd.DataFrame({
            '策略': date_data['Strategy_Alias'],
            '市值': date_data['MarketValue_close'].round(2),
            '收益率': date_data['收益率'],
            '盈亏金额': date_data['盈亏金额']
        })
        
        return result.sort_values('盈亏金额', ascending=False)
    
    def get_nav_contribution(self) -> pd.DataFrame:
        """计算各策略对整体收益的贡献度"""
        contributions = []
        total_market_value = self.df.groupby('Date')['MarketValue_close'].sum()
        
        for strategy in self.df['Strategy'].unique():
            strategy_data = self.df[self.df['Strategy'] == strategy].copy()
            strategy_data['weight'] = strategy_data['MarketValue_close'] / \
                                    total_market_value[strategy_data['Date']].values
            strategy_data['weighted_return'] = strategy_data['weight'] * strategy_data['收益率']
            contribution = (1 + strategy_data['weighted_return']).cumprod().iloc[-1] - 1
            
            contributions.append({
                '策略': self.get_strategy_alias(strategy),
                '净值贡献': contribution
            })
        
        result = pd.DataFrame(contributions)
        return result.sort_values('净值贡献', ascending=False)
    
    def update_drawdown_analysis(self) -> None:
        """更新回撤分析，包含年化收益率计算"""
        strategies_data = []
        
        # 获取最新日期的数据
        latest_date = self.df['Date'].max()
        latest_data = self.df[self.df['Date'] == latest_date]

        # 获取当前持有的策略
        current_strategies = latest_data['Strategy'].unique()  # 只获取最新日期中出现的策略

        for strategy in current_strategies:
            strategy_data = self.df[self.df['Strategy'] == strategy].sort_values('Date')
            strategy_data.set_index('Date', inplace=True)
            
            # 获取最新的市值数据
            latest_strategy_data = latest_data[latest_data['Strategy'] == strategy].iloc[0]
            
            # 计算净值序列
            nav_series = (1 + strategy_data['收益率']).cumprod()
            
            # 计算年化收益率
            total_days = (nav_series.index.max() - nav_series.index.min()).days
            total_return = nav_series.iloc[-1] / nav_series.iloc[0] - 1
            annual_return = float((1 + total_return) ** (365 / total_days) - 1) if total_days > 0 else 0.0
            
            # 计算最大回撤和当前回撤
            running_max = nav_series.expanding().max()
            drawdown = nav_series / running_max - 1
            max_dd = float(drawdown.min())
            curr_dd = float(drawdown.iloc[-1])
            
            strategies_data.append({
                '策略': self.get_strategy_alias(strategy),
                '总市值': latest_strategy_data['MarketValue_close'],
                '持仓市值': latest_strategy_data['PositionValue'],
                '仓位': latest_strategy_data['PositionValue'] / latest_strategy_data['MarketValue_close'] if latest_strategy_data['MarketValue_close'] > 0 else 0,
                '年化收益率': annual_return,
                '最大回撤': max_dd,
                '当前回撤': curr_dd
            })
        
        self.display_df = pd.DataFrame(strategies_data)
        self.display_df = self.display_df.sort_values('总市值', ascending=False)  # 按总市值降序排序
    
    def calculate_annual_return(self, nav_series: pd.Series) -> float:
        """计算年化收益率"""
        total_days = (nav_series.index.max() - nav_series.index.min()).days
        total_return = nav_series.iloc[-1] / nav_series.iloc[0] - 1
        annual_return = (1 + total_return) ** (365 / total_days) - 1 if total_days > 0 else 0
        return float(annual_return)  # 确保返回 float 类型

    def get_style_drawdowns(self) -> pd.DataFrame:
        """计算各个风格的回撤指标和年化收益率（只考虑第一风格）"""
        style_data = []
        
        # 获取最新日期的数据
        latest_date = self.df['Date'].max()
        latest_data = self.df[self.df['Date'] == latest_date]
        total_market_value = latest_data['MarketValue_close'].sum()  # 计算总市值
        
        # 获取所有策略的第一个风格
        all_styles = set()
        current_date = pd.Timestamp.now()  # 使用当前日期
        with open('cubevalue.txt', 'r') as f:
            cubevalue = json.load(f)
            
        # 首次遍历：收集所有风格，包括"三年以内"
        three_year_strategies = []  # 存储三年内的雪球策略
        for strategy_id, strategy_info in self.STRATEGY_STYLES.items():
            if not ('styles' in strategy_info and strategy_info['styles']):
                continue
                
            if '雪球' in strategy_info['styles']:
                if strategy_id in cubevalue and 'create_time' in cubevalue[strategy_id]:
                    create_time = pd.Timestamp(cubevalue[strategy_id]['create_time'])
                    days_diff = (current_date - create_time).days
                    if days_diff <= 1095:  # 3年 * 365天
                        all_styles.add('三年以内')
                        three_year_strategies.append(strategy_id)
                        continue
            
            all_styles.add(strategy_info['styles'][0])
        
        # 对每个风格计算指标
        style_data = []
        for style in all_styles:
            if style == '三年以内':
                style_strategies = three_year_strategies
            else:
                # 对于其他风格，只选择不在three_year_strategies中的策略
                style_strategies = [k for k, v in self.STRATEGY_STYLES.items() 
                                if 'styles' in v and v['styles'] and v['styles'][0] == style
                                and k not in three_year_strategies]  # 排除三年内的雪球策略
            
            if style_strategies:
                # 获取该风格的所有策略数据
                style_df = self.df[self.df['Strategy'].isin(style_strategies)].copy()
                
                # 获取该风格的最新市值数据
                latest_style_data = latest_data[latest_data['Strategy'].isin(style_strategies)]
                style_total_value = latest_style_data['MarketValue_close'].sum()
                style_position_value = latest_style_data['PositionValue'].sum()
                style_ratio = style_total_value / total_market_value if total_market_value > 0 else 0
                
                if not style_df.empty:
                    # 按日期分组计算风格收益率（按市值加权）
                    daily_data = style_df.groupby('Date').apply(
                        lambda x: pd.Series({
                            'return': (x['MarketValue_close'] * x['收益率']).sum() / x['MarketValue_close'].sum()
                        })
                    ).reset_index()
                    
                    # 计算风格净值序列
                    daily_data['nav'] = (1 + daily_data['return']).cumprod()
                    
                    # 计算年化收益率
                    total_days = (daily_data['Date'].max() - daily_data['Date'].min()).days
                    total_return = daily_data['nav'].iloc[-1] - 1
                    annual_return = float((1 + total_return) ** (365 / total_days) - 1) if total_days > 0 else 0.0
                    
                    # 计算最大回撤和当前回撤
                    nav_series = daily_data['nav']
                    running_max = nav_series.expanding().max()
                    drawdown = nav_series / running_max - 1
                    max_dd = float(drawdown.min())
                    curr_dd = float(drawdown.iloc[-1])
                    
                    style_data.append({
                        '风格': style,
                        '总市值': style_total_value,
                        '持仓市值': style_position_value,
                        '配置比例': style_ratio,
                        '年化收益率': annual_return,
                        '最大回撤': max_dd,
                        '当前回撤': curr_dd
                    })
        
        # 转换为DataFrame并按总市值降序排序
        df = pd.DataFrame(style_data)
        return df.sort_values('总市值', ascending=False)

    def _load_csi300_data(self) -> pd.DataFrame:
        """加载沪深300指数数据"""
        try:
            # 读取cubevalue.txt文件
            with open('cubevalue.txt', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 直接获取CSI300的nav_series数据
            csi300_data = data.get('CSI300', {}).get('nav_series', {})
            
            if not csi300_data:
                print("未找到沪深300指数数据")
                return pd.DataFrame()
            
            # 转换为DataFrame
            csi300_df = pd.DataFrame({
                'Date': pd.to_datetime(list(csi300_data.keys())),
                '净值': list(csi300_data.values())
            })
            
            # 按日期排序
            csi300_df = csi300_df.sort_values('Date')
            
            # 仅保留与策略数据相同时间范围内的数据
            if not self.df.empty:
                first_strategy_date = self.df['Date'].min()
                csi300_df = csi300_df[csi300_df['Date'] >= first_strategy_date]
            
            # 计算相对净值（确保第一个值为1）
            if not csi300_df.empty:
                first_value = csi300_df['净值'].iloc[0]
                csi300_df['净值'] = csi300_df['净值'] / first_value
                print(f"沪深300第一天净值: {csi300_df['净值'].iloc[0]}")
            
            print(f"成功加载沪深300数据，共 {len(csi300_df)} 条记录")
            print(f"日期范围: {csi300_df['Date'].min()} 到 {csi300_df['Date'].max()}")
            
            return csi300_df
            
        except Exception as e:
            print(f"加载沪深300数据时出错: {str(e)}")
            return pd.DataFrame()
    
    def get_csi300_data(self, start_date=None, end_date=None) -> pd.DataFrame:
        """获取指定时间范围内的沪深300数据"""
        if self.csi300_data.empty:
            return pd.DataFrame()
        
        if start_date is None:
            start_date = self.df['Date'].min()
        if end_date is None:
            end_date = self.df['Date'].max()
        
        mask = (self.csi300_data['Date'] >= start_date) & (self.csi300_data['Date'] <= end_date)
        return self.csi300_data[mask].copy()

    def get_strategy_data(self, start_date=None, end_date=None) -> pd.DataFrame:
        """获取指定时间范围内的策略数据"""
        if self.df.empty:
            return pd.DataFrame()
        
        # 设置默认日期范围
        if start_date is None:
            start_date = self.df['Date'].min()
        if end_date is None:
            end_date = self.df['Date'].max()
        
        # 筛选日期范围内的数据
        mask = (self.df['Date'] >= start_date) & (self.df['Date'] <= end_date)
        filtered_data = self.df[mask].copy()
        
        # 将策略ID映射为别名
        filtered_data['Strategy_Alias'] = filtered_data['Strategy'].map(self.get_strategy_alias)
        
        # 重命名列以匹配create_net_value_trend_chart方法中的引用
        filtered_data = filtered_data.rename(columns={
            '净值': 'NetValue'
        })
        
        print(f"获取策略数据: {len(filtered_data)} 条记录")
        if not filtered_data.empty:
            print(f"日期范围: {filtered_data['Date'].min()} 到 {filtered_data['Date'].max()}")
            print(f"策略数量: {filtered_data['Strategy'].nunique()}")
            print(f"数据列: {filtered_data.columns.tolist()}")
        
        return filtered_data
