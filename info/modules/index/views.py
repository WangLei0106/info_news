from info import response_code, constants
from info.models import User, News, Category
from info.modules.index import index_blu
from flask import render_template, current_app, session, request, jsonify
from info.utils.comment import user_login_data, g

@index_blu.route('/news_list')
def index_news_list():
    """提供主页新闻列表的数据
    １　接受参数
    ２　检验参数
    ３　根据参数查询用户想看的新闻列表数据
    ４　构造响应的新闻列表数据
    ５　响应新闻列表数据
    """
    # １　接受参数
    args_dict = request.args
    page = args_dict.get('page', '1')
    per_page = args_dict.get('per_page', constants.HOME_PAGE_MAX_NEWS)
    category_id = args_dict.get('cid', '1')

    # ２　检验参数
    try:
        page = int(page)
        per_page = int(per_page)
        category_id = int(category_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.PARAMERR, errmsg="参数错误")

    # ３　根据参数查询用户想看的新闻列表数据

    # 如果分类id不为１，那么添加分类id的过滤
    try:
        if category_id == 1:
            # 从所有新闻中，根据时间倒序，每页取出１０条数据
            paginate = News.query.order_by(News.create_time.desc()).paginate(page,per_page,False)

        else:
            # 从指定的分类中查询新闻根据时间倒序每页取１０条数据
            paginate = News.query.filter(News.category_id==category_id).order_by(News.create_time.desc()).paginate(page, per_page, False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg="数据查询失败")
    # 获取查询出来的数据
    items = paginate.items
    # 获取到总页数
    total_page = paginate.pages
    # 获取当前所在页码
    current_page = paginate.page

    news_li = []
    for news in items:
        news_li.append(news.to_basic_dict())

    data = {
        'news_li':news_li,
        'total_page':total_page,
        'current_page':current_page
    }


    #  返回数据
    return jsonify(errno=response_code.RET.OK, errmsg="ok", data = data)


@index_blu.route('/')
@user_login_data
def index():
    """首页
    1.处理网页右上角用户展示数据
    2.新闻点击排行的展示
    3.新闻分类
    """
    # redis_store.set("name",'zxc')
    # 1.处理网页右上角用户展示数据
    # user_id = session.get('user_id', None)
    # user = None
    # if user_id:
    #     # 表示用户已经登录，然后查询用户信息
    #     try:
    #         user = User.query.get(user_id)
    #     except Exception as e:
    #         current_app.logger.error(e)

    # 2.新闻点击排行的展示
    try:
        new_clicks = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)


    # 获取新闻分类
    categories = Category.query.all()
    # 定义列表保存分类数据
    categories_dicts = []


    for category in categories:
        # 拼接内容
        categories_dicts.append(category.to_dict())


    # 构造渲染模板上下文数据
    context = {
        'user':g.user.to_dict() if g.user else None,
        'new_clicks':new_clicks,
        'categories_dicts':categories_dicts
    }


    return render_template('news/index.html', context = context)


@index_blu.route('/favicon.ico', methods=['GET'])
def favicon():
    """title左侧图标"""
    return current_app.send_static_file('news/favicon.ico')