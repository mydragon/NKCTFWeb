from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from message.models import JoinRequest
from user.models import Team, User
# TODO: 导入 check 包用户检测战队名是否合法
import user.check.views as check


def JsonResponseZh(json_data):
    """
    因为返回含中文的 Json 数据总是需要设置 {'ensure_ascii': False}，所以直接在此集成
    :param json_data: 需要返回的数据
    """
    return JsonResponse(json_data, json_dumps_params={'ensure_ascii': False})


@method_decorator(csrf_exempt, name="dispatch")
class AlterPersonal(View):
    code = error = crt_user = None
    target_attr = new_value = None
    allow_attr = ["username", "description", "email", "qq",
                  "github", "user_career"]

    def get_ret_dict(self):
        return {
            0: {"code": 0, "msg": "更改信息成功"},
            1: {"code": 1, "msg": "请指定更改对象与新值"},
            2: {"code": 2, "msg": "不允许更改字段或不存在字段"},
            3: {"code": 3, "msg": "更改数据库错误",
                "error": self.error},
            10: {"code": 10, "msg": "检测到攻击"},
            401: {"code": 401, "msg": "未授权用户"},
        }[self.code]

    def set_user_msg(self):
        try:
            if self.target_attr not in self.allow_attr:
                return 2
            setattr(self.crt_user, self.target_attr, self.new_value)
            self.ctr_user.save()
            return 0
        except Exception as e:
            self.error = str(e)
            return 3

    def get(self, request):
        print(request.method)
        self.code = 10
        return JsonResponseZh(self.get_ret_dict())

    def post(self, request):
        if not request.user.is_authenticated:
            self.code = 401
            return JsonResponseZh(self.get_ret_dict())
        self.crt_user = request.user
        self.target_attr = request.POST.get("attribute")
        self.new_value = request.POST.get("value")
        self.code = self.set_user_msg() if (self.target_attr is not None
                                            and self.new_value is not None) else 1
        return JsonResponseZh(self.get_ret_dict())


@method_decorator(csrf_exempt, name="dispatch")
class AlterTeam(View):
    code = error = crt_user = None
    target_attr = new_value = None
    allow_attr = ["team_name", "description"]

    def get_ret_dict(self):
        return {
            0: {"code": 0, "msg": "更改信息成功"},
            1: {"code": 1, "msg": "请指定更改对象与新值"},
            2: {"code": 2, "msg": "不允许更改字段或不存在字段"},
            3: {"code": 3, "msg": "更改数据库错误",
                "error": self.error},
            4: {"code": 4, "msg": "只有队长有权限修改队伍信息"},
            10: {"code": 10, "msg": "检测到攻击"},
            401: {"code": 401, "msg": "未授权用户"},
        }[self.code]

    def set_team_msg(self):
        try:
            if self.target_attr not in self.allow_attr:
                return 2
            target_team = self.crt_user.belong
            setattr(target_team, self.target_attr, self.new_value)
            target_team.save()
            return 0
        except Exception as e:
            self.error = str(e)
            return 3

    def get(self, request):
        self.code = 10
        return JsonResponseZh(self.get_ret_dict())

    def post(self, request):
        if not request.user.is_authenticated:
            self.code = 401
            return JsonResponseZh(self.get_ret_dict())
        self.crt_user = request.user
        self.target_attr = request.POST.get("attribute")
        self.new_value = request.POST.get("value")
        self.code = (self.set_user_msg() if self.crt_user.is_leader else 4)\
            if (self.target_attr is not None and self.new_value is not None) else 1
        return JsonResponseZh(self.get_ret_dict())


@method_decorator(csrf_exempt, name="dispatch")
class CreateTeam(View):
    code = crt_user = team_name = new_team = team_description = None
    ret_dict = {
        0: {"code": 0, "msg": "创建战队成功，你现在是队长了"},
        1: {"code": 1, "msg": "请提供一个战队名"},
        2: {"code": 2, "msg": "战队名不合法"},
        3: {"code": 3, "msg": "您已经加入一个战队"},
        10: {"code": 10, "msg": "检测到攻击"},
        401: {"code": 401, "msg": "未授权用户"},
    }

    def create(self):
        t_check = check.TeamName(team_name=self.team_name)
        if t_check.check() is not 0:
            return 2
        self.crt_user.create_team(self.team_name, self.team_description)
        return 0

    def get(self, request):
        print(request.method)
        self.code = 10
        return JsonResponseZh(self.ret_dict[self.code])

    def post(self, request):
        if not request.user.is_authenticated:
            self.code = 401
            return JsonResponseZh(self.ret_dict[self.code])
        self.crt_user = request.user
        self.team_name = request.POST.get("team_name")
        self.team_description = request.POST.get("team_description")

        self.code = (self.create() if self.crt_user.belong is None else 3)\
            if self.team_name is not None else 1
        return JsonResponseZh(self.ret_dict[self.code])


@method_decorator(csrf_exempt, name="dispatch")
class JoinTeam(View):
    code = crt_user = team_name = t_obj = None
    email_content = email_title = None
    ret_dict = {
        0: {"code": 0, "msg": "已经发出入队申请"},
        1: {"code": 1, "msg": "请提供一个战队名"},
        2: {"code": 2, "msg": "战队不存在"},
        3: {"code": 3, "msg": "您已经加入一个战队"},
        10: {"code": 10, "msg": "检测到攻击"},
        401: {"code": 401, "msg": "未授权用户"},
    }

    def apply(self):
        if self.crt_user.belong is not None:
            return 3
        try:
            self.t_obj = Team.objects.get(team_name=self.team_name)
        except Team.DoesNotExist:
            return 2
        JoinRequest.objects.create(send_to=self.t_obj, send_by=self.crt_user,
                                   title=self.email_title or "Join team request.",
                                   content=self.email_content or "I want to join your team.")
        return 0

    def get(self, request):
        self.code = 10
        return JsonResponseZh(self.ret_dict[self.code])

    def post(self, request):
        if not request.user.is_authenticated:
            self.code = 401
            return JsonResponseZh(self.ret_dict[self.code])
        self.crt_user = request.user
        self.team_name = request.POST.get("team_name")
        self.email_title = request.POST.get("email_title")
        self.email_content = request.POST.get("email_content")
        self.code = self.apply() if self.team_name is not None else 1
        return JsonResponseZh(self.ret_dict[self.code])


@method_decorator(csrf_exempt, name="dispatch")
class ExecuteApplication(View):
    code = exe_username = is_agree = None
    crt_user = exe_user = crt_team = request_mail = None
    ret_dict = {
        0: {"code": 0, "msg": "操作成功"},
        1: {"code": 1, "msg": "只有战队队长拥有操作权限"},
        2: {"code": 2, "msg": "请求用户名不存在"},
        3: {"code": 3, "msg": "当前操作用户未申请加入您的战队"},
        4: {"code": 4, "msg": "当前操作用户已经加入了一个战队"},
        401: {"code": 401, "msg": "未授权用户"},
    }

    def execute(self):
        try:
            self.exe_user = User.objects.get(username=self.exe_username)
        except User.DoesNotExist:
            return 2
        try:
            self.request_mail = JoinRequest.objects.get(send_by=self.exe_user,
                                                        send_to=self.crt_team)
        except JoinRequest.DoesNotExist:
            return 3
        if self.exe_user.belong is not None:
            return 4
        self.request_mail.execute_apply(self.is_agree)
        return 0

    def get(self, request):
        self.code = 10
        return JsonResponseZh(self.ret_dict[self.code])

    def post(self, request):
        if not request.user.is_authenticated:
            self.code = 401
            return JsonResponseZh(self.ret_dict[self.code])
        self.crt_user = request.user
        self.crt_team = self.crt_user.belong
        self.exe_username = request.POST.get("username")
        # TODO: 是否允许该用户加入战队，1 表示同意，0 表示拒绝
        self.is_agree = request.POST.get("is_agree") is not 0
        self.code = self.execute() if self.crt_user.is_leader else 1
        return JsonResponseZh(self.ret_dict[self.code])
