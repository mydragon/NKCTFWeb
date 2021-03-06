from django.http import JsonResponse
from django.views import View
from user.models import Team, User
from message.models import JoinRequest


def JsonResponseZh(json_data):
    """
    因为返回含中文的 Json 数据总是需要设置 {'ensure_ascii': False}，所以直接在此集成
    :param json_data: 需要返回的数据
    """
    return JsonResponse(json_data, json_dumps_params={'ensure_ascii': False})


class UserInformation(View):
    code = data = crt_user = None

    def get_ret_dict(self):
        return {
            0: {"code": 0, "msg": "获取信息成功",
                "data": self.data},
            10: {"code": 10, "msg": "检测到攻击"},
            401: {"code": 401, "msg": "未授权用户"},
        }[self.code]

    def get_user_msg(self):
        self.data = {
            "username": self.crt_user.username,
            "email": self.crt_user.email,
            "score": self.crt_user.score,
            "qq": self.crt_user.qq,
            "github": self.crt_user.github,
            "description": self.crt_user.description,
            # TODO: apply_for -> JoinRequest 所有邮件中当前用户发出，目标战队的名称
            "apply_for": [it.send_to.team_name for it in
                          JoinRequest.objects.filter(send_by=self.crt_user)],
        }
        return 0

    def get(self, request):
        if not request.user.is_authenticated:
            self.code = 401
            return JsonResponseZh(self.get_ret_dict())
        self.crt_user = request.user
        self.code = self.get_user_msg()
        return JsonResponseZh(self.get_ret_dict())

    def post(self, request):
        self.code = 10
        return JsonResponseZh(self.get_ret_dict())


class TeamInformation(View):
    code = data = crt_user = t_obj = None

    def get_ret_dict(self):
        return {
            0: {"code": 0, "msg": "获取信息成功",
                "data": self.data},
            1: {"code": 1, "msg": "您尚未加入战队"},
            10: {"code": 10, "msg": "检测到攻击"},
            401: {"code": 401, "msg": "未授权用户"},
        }[self.code]

    def get_team_msg(self):
        try:
            self.t_obj = self.crt_user.belong
        except Team.DoesNotExist:
            return 1
        self.data = {
            "team_name": self.t_obj.team_name,
            "team_description": self.t_obj.description,
            "my_role": self.crt_user.user_career,
            "join_date": self.crt_user.join_date.strftime("%H:%M:%S in %Y,%m,%d"),
            "is_leader": self.crt_user.is_leader,
            # TODO: application -> JoinRequest 中所有目标为当前战队，发出用户的用户名
            "application": [it.send_by.username for it in
                            JoinRequest.objects.filter(send_to=self.t_obj)],
        }
        return 0

    def get(self, request):
        if not request.user.is_authenticated:
            self.code = 401
            return JsonResponseZh(self.get_ret_dict())
        self.crt_user = request.user
        self.code = self.get_team_msg()
        return JsonResponseZh(self.get_ret_dict())

    def post(self, request):
        self.code = 10
        return JsonResponseZh(self.get_ret_dict())

