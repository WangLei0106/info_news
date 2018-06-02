from flask import current_app, session, render_template, abort,request, jsonify
from info import response_code, db
from . import news_blue
from info.models import News, constants, Comment, CommentLike
from info.utils.comment import user_login_data,g



@news_blue.route('/comment_like', methods=['POST'])
@user_login_data
def new_comment_like():
    """用户点攒与取消点攒"""
    # 验证用户是否登录
    user = g.user
    if not user:
        return jsonify(errno=response_code.RET.SESSIONERR, errmsg="用户未登录")
    # 获取参数
    json_dic = request.json
    comment_id = json_dic.get('comment_id')
    news_id = json_dic.get('news_id')
    action = json_dic.get('action')

    # 验证参数信息
    if not all([comment_id, news_id, action]):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg="参数不足")

    if action not in ('add', 'remove'):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg="参数信息有误")


    # 获取评论信息
    try:
        comment = Comment.query.get(comment_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg="获取数据失败")

    if not comment:
        return jsonify(errno=response_code.RET.NODATA, errmsg="评论信息不存在")

    # 添加点攒
    if action == 'add':
        try:
            comment_like = CommentLike.query.filter_by(comment_id=comment_id, user_id=g.user.id).first()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=response_code.RET.DBERR, errmsg="获取信息失败")

        if not comment_like:
            comment_like = CommentLike()
            comment_like.comment_id = comment_id
            comment_like.user_id = user.id
            db.session.add(comment_like)
            # 点攒次数加一
            comment.like_count += 1

    else:
        comment_like = CommentLike.query.filter_by(comment_id=comment_id, user_id=g.user.id).first()
        db.session.delete(comment_like)
        # 点攒次数减一
        comment.like_count -= 1

    # 提交数据
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=response_code.RET.DBERR, errmsg="提交失败")



    return jsonify(errno=response_code.RET.OK, errmsg="ok")



@news_blue.route('/news_comment', methods=['POST'])
@user_login_data
def news_comment():
    """用户评论新闻
    1.获取参数信息
    2.验证参数信息
    3.添加用户评论
    4.返回数据
    """
    # 获取用户信息
    user = g.user
    # 判断用户是否登录
    if not user:
        return jsonify(errno=response_code.RET.SESSIONERR, errmsg="用户未登录")

    # 获取参数信息
    json_dic = request.json
    news_id = json_dic.get('news_id')
    comment = json_dic.get('comment')
    parent_id = json_dic.get('parent_id')

    # 验证参数信息
    if not all([news_id, comment]):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg="参数不足")

    # 查询新闻是否存在
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg="数据查询不到")

    if not news:
        return jsonify(errno=response_code.RET.NODATA, errmsg="新闻不存在")

    # 添加评论对象
    com = Comment()
    com.content = comment
    com.news_id = news_id
    com.user_id = user.id
    if parent_id:
        com.parent_id = parent_id

    # 添加评论对象到数据库
    try:
        db.session.add(com)
        db.session.commit()
    except Exception as e:
        current_app.logger.error()
        db.session.rollback()
        return jsonify(errno=response_code.RET.DBERR, errmsg="评论失败")

    data = {
        'comment': com.to_dict()
    }

    # 返回响应信息
    return jsonify(errno=response_code.RET.OK, errmsg="OK", data = data)


@news_blue.route('/new_fans', methods=['POST'])
@user_login_data
def news_fans():
    """关注与取消关注"""
    pass


@news_blue.route('/news_collect', methods=['POST'])
@user_login_data
def news_collect():
    """新闻的收藏与取消
    1.接收参数：news_id，action
    ２．判断参数信息是否有无
    3.向ｍｙｓｅｌ数据库查询新闻信息
    ４．添加收藏
    ５．提交数据信息
    ６．返回响应信息
    :return: response
    """
    # 1.接收参数：news_id，action,获取g变量里存储的用户登录信息
    user = g.user
    json_dic = request.json
    news_id = json_dic.get('news_id')
    action = json_dic.get('action')
    # ２．判断参数信息是否有无
    if not user:
        return jsonify(errno=response_code.RET.SESSIONERR, errmsg="用户未登录")

    if not all([news_id, action]):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg="参数错误")

    if action not in ('collect', 'cancel_collect'):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg="参数信息错误")

    if not news_id:
        return jsonify(errno=response_code.RET.PARAMERR, errmsg="参数错误")
    # .向ｍｙｓｅｌ数据库查询新闻信息
    try:
        new = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg="数据不存在")

    if not new:
        return jsonify(errno=response_code.RET.PARAMERR, errmsg="新闻信息不存在")

    # ４．添加收藏
    if action=="collect":
        user.collection_news.append(new)
    else:
        user.collection_news.remove(new)

    # ５．提交收藏的数据信息
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=response_code.RET.DBERR, errmsg="收藏失败")
    # ６．返回响应信息

    return jsonify(errno=response_code.RET.OK, errmsg="ok")


@news_blue.route('/<int:news_id>')
@user_login_data
def news_detail(news_id):
    """详情页的数据处理
    1.新闻数据获取
    2.判断是否收藏该新闻，默认值为 false
    3.用户点击量的记录
    4.获取点击排行的信息
    5.获取评论信息
    6.返回响应体

    """
    # 新闻数据获取
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        abort(404)
        # 判断用户是否收藏过该新闻
    if not news:
        # 返回数据未找到的页面
        abort(404)

    # 判断是否收藏该新闻，默认值为 false
    is_collected = False
    if g.user:
        if news in g.user.collection_news:
            is_collected = True

    # 用户点击量的记录
    news.clicks += 1
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()

    # 获取点击排行的信息
    new_clicks=[]
    try:
        new_clicks = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)



    # 获取评论的内容并按照最新消息显示信息
    try:
        comment = Comment.query.filter(Comment.news_id==news_id).order_by(Comment.create_time.desc()).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg="查询评论信息失败")
    # 取出所有评论的id


    comment_like_ids = []
    if g.user:
        # 如果当前用户已登录
        try:
            # 获取当前新闻所有评论ｉｄ
            comment_ids = [comment.id for comment in comment]
            if len(comment_ids) > 0:
                # 取到当前用户在当前新闻的所有评论点赞的记录
                comment_likes = CommentLike.query.filter(CommentLike.comment_id.in_(comment_ids),
                                                         CommentLike.user_id == g.user.id).all()
                # 取出记录中所有的评论id
                comment_like_ids = [comment_like.comment_id for comment_like in comment_likes]
        except Exception as e:
            current_app.logger.error(e)


    # 添加一条属性判断该用户是否点攒
    comment_list = []
    for item in comment if comment else []:
        comments = item.to_dict()
        comments['is_like'] = False
        if g.user.id and item.id in comment_like_ids:
            comments['is_like'] = True
        comment_list.append(comments)

    # 返回响应体数据
    context = {
        "user": g.user.to_dict() if g.user else None,
        'new':news.to_dict(),
        'new_clicks': new_clicks,
        'is_collected':is_collected,
        'comment':comment_list
    }
    return render_template('news/detail.html', context = context)