from django.shortcuts import render, redirect, HttpResponse

# Create your views here.
from django.http import JsonResponse
from django.contrib import auth
from blog import forms, models
from geetest import GeetestLib
from django.db.models import Count

#用户登录校验视图
def login1(request):
    if request.method=="POST":
        ret = {"status": 0, "msg": ""}
        username = request.POST.get("username")
        pwd = request.POST.get("password")
        valid_code = request.POST.get("valid_code")  # 获取用户填写的验证码
        print(valid_code)
        print("用户输入的验证码".center(120, "="))
        if valid_code and valid_code.upper() == request.session.get("valid_code", "").upper():
            # 验证码正确
            # 利用auth模块做用户名和密码的校验
            user = auth.authenticate(username=username, password=pwd)
            if user:
                # 用户名密码正确
                # 给用户做登录
                auth.login(request, user)
                ret["msg"] = "/index/"
            else:
                # 用户名密码错误
                ret["status"] = 1
                ret["msg"] = "用户名或密码错误！"
        else:
            ret["status"] = 1
            ret["msg"] = "验证码错误"

        return JsonResponse(ret)
    return render(request, "login1.html")


def logout(request):
    auth.logout(request)
    return redirect("/index/")

#返回主页的视图
def index(request):
    article_list=models.Article.objects.all()
    return render(request,"index.html",{"article_list":article_list})


# 正常获取验证码图片的视图
def get_valid_img(request):
    # with open("valid_code.png", "rb") as f:
    #     data = f.read()
    # 自己生成一个图片
    from PIL import Image, ImageDraw, ImageFont
    import random

    # 获取随机颜色的函数
    def get_random_color():
        return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)

    # 生成一个图片对象
    img_obj = Image.new(
        'RGB',
        (220, 35),
        get_random_color()
    )
    # 在生成的图片上写字符
    # 生成一个图片画笔对象
    draw_obj = ImageDraw.Draw(img_obj)
    # 加载字体文件， 得到一个字体对象
    font_obj = ImageFont.truetype("static/font/kumo.ttf", 28)
    # 开始生成随机字符串并且写到图片上
    tmp_list = []
    for i in range(5):
        u = chr(random.randint(65, 90))  # 生成大写字母
        l = chr(random.randint(97, 122))  # 生成小写字母
        n = str(random.randint(0, 9))  # 生成数字，注意要转换成字符串类型

        tmp = random.choice([u, l, n])
        tmp_list.append(tmp)
        draw_obj.text((20+40*i, 0), tmp, fill=get_random_color(), font=font_obj)

    print("".join(tmp_list))
    print("生成的验证码".center(120, "="))
    # 不能保存到全局变量
    # global VALID_CODE
    # VALID_CODE = "".join(tmp_list)

    # 保存到session
    request.session["valid_code"] = "".join(tmp_list)
    # 加干扰线
    # width = 220  # 图片宽度（防止越界）
    # height = 35
    # for i in range(5):
    #     x1 = random.randint(0, width)
    #     x2 = random.randint(0, width)
    #     y1 = random.randint(0, height)
    #     y2 = random.randint(0, height)
    #     draw_obj.line((x1, y1, x2, y2), fill=get_random_color())
    #
    # # 加干扰点
    # for i in range(40):
    #     draw_obj.point((random.randint(0, width), random.randint(0, height)), fill=get_random_color())
    #     x = random.randint(0, width)
    #     y = random.randint(0, height)
    #     draw_obj.arc((x, y, x+4, y+4), 0, 90, fill=get_random_color())

    # 将生成的图片保存在磁盘上
    # with open("s10.png", "wb") as f:
    #     img_obj.save(f, "png")
    # # 把刚才生成的图片返回给页面
    # with open("s10.png", "rb") as f:
    #     data = f.read()

    # 不需要在硬盘上保存文件，直接在内存中加载就可以
    from io import BytesIO
    io_obj = BytesIO()
    # 将生成的图片数据保存在io对象中
    img_obj.save(io_obj, "png")
    # 从io对象里面取上一步保存的数据
    data = io_obj.getvalue()
    return HttpResponse(data)


#新用户注册视图
def register(request):
    if request.method == "POST":
        ret = {"status": 0, "msg": ""}
        form_obj = forms.RegForm(request.POST)
        print(request.POST)
        # 帮我做校验
        if form_obj.is_valid():
            # 校验通过，去数据库创建一个新的用户
            form_obj.cleaned_data.pop("re_password")
            avatar_img = request.FILES.get("avatar")
            models.UserInfo.objects.create_user(**form_obj.cleaned_data, avatar=avatar_img)
            ret["msg"] = "/index/"
            return JsonResponse(ret)
        else:
            print(form_obj.errors)
            ret["status"] = 1
            ret["msg"] = form_obj.errors
            print(ret)
            print("=" * 120)
            return JsonResponse(ret)
    # 生成一个form对象
    form_obj = forms.RegForm()
    print(form_obj.fields)
    return render(request, "register.html", {"form_obj": form_obj})


#返回主页的视图
def home(request):
    return render(request,"home.html")


pc_geetest_id = "b46d1900d0a894591916ea94ea91bd2c"
pc_geetest_key = "36fc3fe98530eea08dfc6ce76e3d24c4"
#极速验证科技校验视图
def login(request):
    # if request.is_ajax():  # 如果是AJAX请求
    if request.method == "POST":
        # 初始化一个给AJAX返回的数据
        ret = {"status": 0, "msg": ""}
        # 从提交过来的数据中 取到用户名和密码
        username = request.POST.get("username")
        pwd = request.POST.get("password")
        # 获取极验 滑动验证码相关的参数
        gt = GeetestLib(pc_geetest_id, pc_geetest_key)
        challenge = request.POST.get(gt.FN_CHALLENGE, '')
        validate = request.POST.get(gt.FN_VALIDATE, '')
        seccode = request.POST.get(gt.FN_SECCODE, '')
        status = request.session[gt.GT_STATUS_SESSION_KEY]
        user_id = request.session["user_id"]
        if status:
            result = gt.success_validate(challenge, validate, seccode, user_id)
        else:
            result = gt.failback_validate(challenge, validate, seccode)
        if result:
            # 验证码正确
            # 利用auth模块做用户名和密码的校验
            user = auth.authenticate(username=username, password=pwd)
            if user:
                # 用户名密码正确
                # 给用户做登录
                auth.login(request, user)
                ret["msg"] = "/index/"
            else:
                # 用户名密码错误
                ret["status"] = 1
                ret["msg"] = "用户名或密码错误！"
        else:
            ret["status"] = 1
            ret["msg"] = "验证码错误"

        return JsonResponse(ret)
    return render(request, "login.html")


# 处理极验 获取验证码的视图
def get_geetest(request):
    user_id = 'test'
    gt = GeetestLib(pc_geetest_id, pc_geetest_key)
    status = gt.pre_process(user_id)
    request.session[gt.GT_STATUS_SESSION_KEY] = status
    request.session["user_id"] = user_id
    response_str = gt.get_response_str()
    return HttpResponse(response_str)



# 校验用户名是否已被注册
def check_username_exist(request):
    ret = {"status": 0, "msg": ""}
    username = request.GET.get("username")
    print(username)
    is_exist = models.UserInfo.objects.filter(username=username)
    if is_exist:
        ret["status"] = 1
        ret["msg"] = "用户名已被注册！"
    return JsonResponse(ret)




# 个人博客主页
def home(request, username):
    print(username)
    # 去UserInfo表里把用户对象取出来
    user = models.UserInfo.objects.filter(username=username).first()
    if not user:
        return HttpResponse("404")
    # 如果用户存在需要将TA写的所有文章找出来
    blog = user.blog

    # 我的文章列表
    article_list = models.Article.objects.filter(user=user)
    # 我的文章分类及每个分类下文章数
    # 将我的文章按照我的分类分组，并统计出每个分类下面的文章数
    # category_list = models.Category.objects.filter(blog=blog)
    category_list = models.Category.objects.filter(blog=blog).annotate(c=Count("article")).values("title", "c")
    # [{'title': '技术', 'c': 2}, {'title': '生活', 'c': 1}, {'title': 'LOL', 'c': 1}]
    # 统计当前站点下有哪一些标签，并且按标签统计出文章数
    tag_list = models.Tag.objects.filter(blog=blog).annotate(c=Count("article")).values("title", "c")

    # 按日期归档
    archive_list = models.Article.objects.filter(user=user).extra(
        select={"archive_ym": "date_format(create_time,'%%Y-%%m')"}
    ).values("archive_ym").annotate(c=Count("nid")).values("archive_ym", "c")

    return render(request, "home.html", {
        "username": username,
        "blog": blog,
        "article_list": article_list,
    })


def get_left_menu(username):
    user = models.UserInfo.objects.filter(username=username).first()
    blog = user.blog
    category_list = models.Category.objects.filter(blog=blog).annotate(c=Count("article")).values("title", "c")
    tag_list = models.Tag.objects.filter(blog=blog).annotate(c=Count("article")).values("title", "c")
    # 按日期归档
    archive_list = models.Article.objects.filter(user=user).extra(
        select={"archive_ym": "date_format(create_time,'%%Y-%%m')"}
    ).values("archive_ym").annotate(c=Count("nid")).values("archive_ym", "c")

    return category_list, tag_list, archive_list


def article_detail(request, username, pk):
    """
    :param username: 被访问的blog的用户名
    :param pk: 访问的文章的主键id值
    :return:
    """
    user = models.UserInfo.objects.filter(username=username).first()
    if not user:
        return HttpResponse("404")
    blog = user.blog
    # 找到当前的文章
    article_obj = models.Article.objects.filter(pk=pk).first()

    #所有评论列表
    comment_list=models.Comment.objects.filter(article_id=pk)

    return render(
        request,
        "article_detail.html",
        {
            'comment_list':comment_list,
            "username": username,
            "article": article_obj,
            "blog": blog,
         }
    )

import json
from django.db.models import F

def up_down(request):

    article_id=request.POST.get('article_id')
    is_up=json.loads(request.POST.get('is_up'))
    user=request.user
    response={"status":True}

    try:
        models.ArticleUpDown.objects.create(user=user,article_id=article_id,is_up=is_up)
        models.Article.objects.filter(pk=article_id).update(up_count=F("up_count")+1)

    except Exception as e:
        response["status"]=False
        response["first_action"]=models.ArticleUpDown.objects.filter(user=user,article_id=article_id).first().is_up


    return JsonResponse(response)



def comment(request):
    pid=request.POST.get("pid")
    article_id=request.POST.get("article_id")
    content=request.POST.get("content")
    user_pk=request.user.pk
    response={}
    if not pid:  #根评论
        comment_obj=models.Comment.objects.create(article_id=article_id,user_id=user_pk,content=content)
    else:
        comment_obj=models.Comment.objects.create(article_id=article_id,user_id=user_pk,content=content,parent_comment_id=pid)
    response["create_time"]=comment_obj.create_time.strftime("%Y-%m-%d")
    response["content"]=comment_obj.content
    response["username"]=comment_obj.user.username

    return JsonResponse(response)

def comment_tree(request,article_id):

    ret=list(models.Comment.objects.filter(article_id=article_id).values("pk","content","parent_comment_id"))
    print(ret)
    return JsonResponse(ret,safe=False)

def add_article(request):

    if request.method=="POST":
        title=request.POST.get('title')
        article_content=request.POST.get('article_content')
        user=request.user

        from bs4 import BeautifulSoup

        bs=BeautifulSoup(article_content,"html.parser")
        desc=bs.text[0:150]+"..."


        # 过滤非法标签
        for tag in bs.find_all():

            print(tag.name)

            if tag.name in ["script", "link"]:
                tag.decompose()

        article_obj=models.Article.objects.create(user=user,title=title,desc=desc)
        models.ArticleDetail.objects.create(content=str(bs),article=article_obj)


        return HttpResponse("添加成功")




    return render(request,"add_article.html")



from bbs import settings
import os,json
def upload(request):
    print(request.FILES)
    obj = request.FILES.get("upload_img")

    print("name",obj.name)

    path=os.path.join(settings.MEDIA_ROOT,"add_article_img",obj.name)

    with open(path,"wb") as f:
        for line in obj:
            f.write(line)


    res={
        "error":0,
        "url":"/media/add_article_img/"+obj.name
    }


    return HttpResponse(json.dumps(res))


