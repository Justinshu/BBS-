/**
 * Created by Administrator on 2019/2/27.
 */


$("#div_digg .action").click(function () {
    // 点赞或踩灭
    if ($(".info").attr("username")) {
        var is_up = $("#div_digg .action").hasClass("diggit");
        var article_id =$(".info").attr("article_pk");
        $.ajax({
            url: "/blog/up_down/",
            type: "post",
            data: {
                is_up: is_up,
                article_id: article_id,
                csrfmiddlewaretoken: $("[name='csrfmiddlewaretoken']").val(),

            },
            success: function (data) {

                console.log(data);
                if (data.status) {
                    //第一次提交成功

                    if (is_up) {
                        var val = $("#digg_count").text();
                        val = parseInt(val) + 1;
                        $("#digg_count").text(val);
                    } else {
                        var val = $("#bury_count").text();
                        val = parseInt(val) + 1;
                        $("#bury_count").text(val);
                    }
                } else {
                    //拒绝重复提交
                    if (data.first_action) {
                        $("#digg_tips").html("您已经推荐过了");
                    } else {
                        $("#digg_tips").html("您已经反对过了");
                    }
                    setTimeout(function () {
                        $("#digg_tips").html("")
                    }, 1000)
                }
            }
        })
    } else {
        location.href='/login/';
    }
})




