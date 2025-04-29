# 克隆自聚宽文章：https://www.joinquant.com/post/49001
# 标题：偷鸡摸狗策略
# 作者：MarioC

# 克隆自聚宽文章：https://www.joinquant.com/post/48284
# 标题：蛇皮走位小市值策略V1.0
# 作者：MarioC

# 克隆自聚宽文章：https://www.joinquant.com/post/45510
# 标题：5年15倍的收益，年化79.93%，可实盘，拿走不谢！

import warnings
from jqdata import *

warnings.filterwarnings("ignore")

def initialize(context):
    """
    初始化函数，设置策略参数和基准
    :param context: 策略上下文对象，包含账户、持仓等信息
    """
    # 设置基准
    set_benchmark('000300.XSHG')
    # 开启动态复权模式(真实价格)
    set_option('use_real_price', True)
    # 设置日志级别为error
    log.set_level('order', 'error')

    g.stock_num = 10  # 持股数量
    g.type=''  # 当前策略类型（偷鸡或摸狗）
    g.Counterattack_Days=30  # 偷鸡持续天数
    g.Days=0  # 当前持续天数
    # 准备昨日涨停且正在持有的股票列表
    run_daily(prepare_high_limit_list, time='9:05', reference_security='000300.XSHG')
    # 每天调整昨日涨停股票
    run_daily(check_limit_up, time='14:00')
    run_daily(consistent, time='9:30')
    g.m_days = 25  # 动量参考天数
    g.etf_pool = [  # ETF池，包含不同类型的ETF
        '518880.XSHG',  # 黄金ETF（大宗商品）
        '513100.XSHG',  # 纳指100（海外资产）
        '159915.XSHE',  # 创业板100（成长股，科技股，中小盘）
        '510180.XSHG',  # 上证180（价值股，蓝筹股，中大盘）
    ]

def MOM(etf):
    """
    计算ETF的动量指标
    :param etf: ETF代码
    :return: 动量评分，综合考虑年化收益率和R平方
    """
    df = attribute_history(etf, g.m_days, '1d', ['close'])  # 获取历史收盘价

	################################ 改为以下：
    df = C.get_market_data_ex(['close'],etf,period='1d',start_time='',end_time='',count=25,dividend_type='follow',fill_data=True,subscribe=True)

    y = np.log(df['close'].values)  # 计算对数收益
    n = len(y)  
    x = np.arange(n)  # 时间序列
    weights = np.linspace(1, 2, n)  # 权重
    slope, intercept = np.polyfit(x, y, 1, w=weights)  # 线性回归
    annualized_returns = math.pow(math.exp(slope), 250) - 1  # 年化收益率
    residuals = y - (slope * x + intercept)  # 残差
    weighted_residuals = weights * residuals**2  # 加权残差
    r_squared = 1 - (np.sum(weighted_residuals) / np.sum(weights * (y - np.mean(y))**2))  # R平方
    score = annualized_returns * r_squared  # 动量评分
    return score

def get_rank(etf_pool):
    """
    对ETF池中的ETF进行排名
    :param etf_pool: ETF代码列表
    :return: 按动量评分排序后的ETF列表
    """
    score_list = []  # 存储每个ETF的动量评分
    for etf in etf_pool:
        score = MOM(etf)  # 计算动量评分
        score_list.append(score)  # 添加到评分列表
    df = pd.DataFrame(index=etf_pool, data={'score':score_list})  # 创建DataFrame
    df = df.sort_values(by='score', ascending=False)  # 按评分排序
    rank_list = list(df.index)  # 获取排序后的ETF列表
    return rank_list

def DDDD(context):
    """
    计算市场波动率和平均收益率，用于判断当前市场状态
    :param context: 策略上下文对象
    :return: 市场波动率, 平均收益率
    """
    # 你要偷鸡还是摸狗呢？
    yesterday = context.previous_date  # 获取昨日日期
    stocks = get_index_stocks('399101.XSHE', yesterday)  # 获取昨日的股票列表

    ############################### 改为以下：
    stocks = C.get_sector('399101.XSHE')

    q = query(
        valuation.code, valuation.circulating_market_cap, indicator.eps
    ).filter(
        valuation.code.in_(stocks)  # 过滤股票
    ).order_by(
        valuation.circulating_market_cap.asc()  # 按市值升序排列
    )
    df = get_fundamentals(q, date=yesterday)  # 获取基本面数据
    lst = list(df.code)[:20]  # 取市值前20的股票
    h_ratio = get_price(lst, end_date=yesterday, frequency='1d', fields=['close'], count=2, panel=False
                        ).pivot(index='time', columns='code', values='close')  # 获取收盘价
    change_BIG = (h_ratio.iloc[-1] / h_ratio.iloc[0] - 1) * 100  # 计算涨幅
    A1 = np.array(change_BIG)  # 转换为数组
    norm = np.linalg.norm(A1)  # 计算范数
    normalized_array = A1 / norm  # 归一化
    variance = np.var(normalized_array)  # 计算方差
    mean = np.mean(normalized_array)  # 计算均值
    return variance, mean  # 返回方差和均值

# 1-3 整体调整持仓
def consistent(context):
    """
    核心策略逻辑，根据市场状态调整持仓
    1. 偷鸡模式：小市值股票策略
    2. 摸狗模式：ETF动量策略
    :param context: 策略上下文对象
    """
    print(g.type)  # 打印当前策略类型
    if g.type == '偷鸡':
        if g.Days < g.Counterattack_Days:
            g.Days = g.Days + 1  # 增加持续天数
            pass
        if g.Days == g.Counterattack_Days:
            g.type = '摸狗'  # 切换策略类型
            for stock in context.portfolio.positions.keys():
                order_target_value(stock, 0)  # 清仓
            g.Days = 0  # 重置持续天数
    else:
        variance, mean = DDDD(context)  # 计算市场波动率和平均收益率
        if variance < 0.02 and mean > 0:
            g.type = '偷鸡'  # 切换到偷鸡模式
        else:
            g.type = '摸狗'  # 切换到摸狗模式

    if g.type == '摸狗':
        target_num = 1  # 目标持有的ETF数量
        target_list = get_rank(g.etf_pool)[:target_num]  # 获取目标ETF列表
        hold_list = list(context.portfolio.positions)  # 获取当前持仓
        for etf in hold_list:
            if etf not in target_list:
                order_target_value(etf, 0)  # 卖出不在目标列表中的ETF
                print('卖出' + str(etf))
            else:
                print('继续持有' + str(etf))
                pass
        value = context.portfolio.available_cash  # 可用现金
        if value > 10000:
            for s in target_list:
                order_value(s, value)  # 买入目标ETF

    if g.type == '偷鸡':
        if g.Days == 0:
            target_list = choose_stocks(context)  # 选择小市值股票
            current_data = get_current_data()  # 获取当前数据
            for s in context.portfolio.positions:
                if s in target_list or current_data[s].paused or current_data[s].last_price == current_data[s].high_limit:
                    continue  # 跳过持有的目标股票
                log.info('Sell: %s %s' % (s, get_current_data()[s].name))  # 记录卖出信息
                order_target(s, 0)  # 卖出不在目标列表中的股票
            to_buy(context, target_list)  # 买入目标股票

def prepare_high_limit_list(context):
    """
    准备昨日涨停且正在持有的股票列表
    :param context: 策略上下文对象
    """
    g.high_limit_list = []  # 初始化涨停股票列表
    hold_list = list(context.portfolio.positions)  # 获取当前持仓
    if hold_list:
        g.high_limit_list = get_price(
            hold_list, end_date=context.previous_date, frequency='daily',
            fields=['close', 'high_limit', 'paused'],
            count=1, panel=False).query('close == high_limit and paused == 0')['code'].tolist()  # 获取涨停股票

def check_limit_up(context):
    """
    检查持仓股票的涨停状态，并进行相应操作
    :param context: 策略上下文对象
    """
    hold_list = list(context.portfolio.positions)  # 获取当前持仓
    num = 0  # 记录卖出数量
    now_time = context.current_dt  # 当前时间
    if g.high_limit_list != []:
        for stock in g.high_limit_list:
            current_data = get_price(stock, end_date=now_time, frequency='1m', fields=['close', 'high_limit'],
                                     skip_paused=False, fq='pre', count=1, panel=False, fill_paused=True)  # 获取当前价格
            if current_data.iloc[0, 0] < current_data.iloc[0, 1]:
                log.info("[%s]涨停打开，卖出" % (stock))  # 记录卖出信息
                close_position(context, stock)  # 卖出股票
                num = num + 1
            else:
                log.info("[%s]涨停，继续持有" % (stock))  # 记录持有信息
    SS = []  # 存储止损股票
    S = []  # 存储股票代码
    for stock in hold_list:
        if stock not in g.etf_pool:  # 过滤ETF
            if stock in list(context.portfolio.positions.keys()):
                if context.portfolio.positions[stock].price < context.portfolio.positions[stock].avg_cost * 0.90:
                    order_target_value(stock, 0)  # 止损卖出
                    log.debug("止损 Selling out %s" % (stock))  # 记录止损信息
                    num = num + 1
                else:
                    S.append(stock)  # 添加到股票列表
                    NOW = (context.portfolio.positions[stock].price - context.portfolio.positions[stock].avg_cost) / context.portfolio.positions[stock].avg_cost  # 计算收益率
                    SS.append(np.array(NOW))  # 添加到收益率列表
    if num >= 1:
        if len(SS) > 0:
            NNN = 3  # 选择补跌的股票数量
            min_values = sorted(SS)[:NNN]  # 获取最小收益率的股票
            min_indices = [SS.index(value) for value in min_values]  # 获取索引
            min_strings = [S[index] for index in min_indices]  # 获取股票代码
            cash = context.portfolio.cash / NNN  # 每只股票的投资金额
            for ss in min_strings:
                order_value(ss, cash)  # 买入补跌股票
                log.debug("补跌最多的N支 Order %s" % (ss))  # 记录买入信息

# 每月选股
def choose_stocks(context):
    """
    选股函数，筛选符合条件的小市值股票
    :param context: 策略上下文对象
    :return: 选中的股票列表
    """
    # 2-6 过滤次新股
    by_date = context.previous_date - datetime.timedelta(days=250)  # 获取250天前的日期
    stocks = get_all_securities('stock', by_date).index.tolist()  # 获取所有股票
    # 4 各种过滤
    stocks = filter_stock_basic(stocks)  # 基础过滤
    # 5 低价股
    stocks = filter_high_price_stock(stocks)  # 过滤高价股
    # 3 基本面筛选，并根据小市值排序
    stocks = get_peg(stocks)  # 基本面选股
    # 截取不超过最大持仓数的股票量
    return stocks[:g.stock_num]  # 返回选中的股票

def filter_stock_basic(stock_list):
    """
    基础股票过滤，排除ST股、停牌股等
    :param stock_list: 待筛选的股票列表
    :return: 过滤后的股票列表
    """
    curr_data = get_current_data()  # 获取当前数据
    return [
        stock for stock in stock_list if not
        (
                stock.startswith(('68', '4', '8', '3')) or  # '3', 创业，科创，北交所
                curr_data[stock].paused or  # 停牌股
                curr_data[stock].is_st or  # ST股
                (curr_data[stock].last_price >= curr_data[stock].high_limit * 0.97) or  # 涨停开盘
                (curr_data[stock].last_price <= curr_data[stock].low_limit * 1.04)  # 跌停开盘
        )]

# 2-4 过滤股价高于10元的股票
def filter_high_price_stock(stock_list):
    """
    过滤高价股，只保留价格低于10元的股票
    :param stock_list: 待筛选的股票列表
    :return: 过滤后的股票列表
    """
    last_prices = history(1, unit='1m', field='close', security_list=stock_list).iloc[0]  # 获取最新价格
    return last_prices[last_prices < 10].index.tolist()  # 返回价格低于10元的股票

def to_buy(context, target_list):
    """
    执行买入操作
    :param context: 策略上下文对象
    :param target_list: 目标买入股票列表
    """
    position_count = len(context.portfolio.positions)  # 当前持仓数量
    if position_count < g.stock_num:  # 如果持仓数量小于最大持仓数
        value = context.portfolio.available_cash / (g.stock_num - position_count)  # 每只股票的投资金额
        for s in target_list:
            if s not in context.portfolio.positions:  # 如果不在持仓中
                log.info('buy: %s %s' % (s, get_current_data()[s].name))  # 记录买入信息
                order_value(s, value)  # 买入股票
                if len(context.portfolio.positions) == g.stock_num:  # 达到最大持仓数
                    break

# 基本面筛选，并根据小市值排序
def get_peg(stocks):
    """
    基本面选股，筛选ROE和ROA符合要求的股票
    :param stocks: 待筛选的股票列表
    :return: 按市值排序后的股票列表
    """
    # 基本面选股
    stocks = get_fundamentals(
        query(
            valuation.code,
        ).filter(
            indicator.roe > 0.15,  # ROE大于15%
            indicator.roa > 0.10,  # ROA大于10%
            valuation.code.in_(stocks)  # 在待筛选股票中
        ).order_by(
            valuation.market_cap.asc()  # 按市值升序排列
        )
    )['code'].tolist()  # 返回符合条件的股票代码
    return stocks

# 3-3 交易模块-平仓
def close_position(context, security):
    """
    平仓操作
    :param context: 策略上下文对象
    :param security: 需要平仓的证券代码
    :return: 平仓是否成功
    """
    if security in context.portfolio.positions and context.portfolio.positions[security].closeable_amount > 0:
        _order = order_target_value(security, 0)  # 平仓操作
        if _order is not None:
            if _order.status == OrderStatus.held and _order.filled == _order.amount:
                return True  # 平仓成功
    return False  # 平仓失败