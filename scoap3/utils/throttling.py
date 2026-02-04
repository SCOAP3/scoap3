from rest_framework.settings import api_settings
from rest_framework.throttling import SimpleRateThrottle


class UserGroupThrottle(SimpleRateThrottle):
    def __init__(self):
        pass

    def get_rate(self) -> str | None:
        if not self.user_groups:
            return api_settings.DEFAULT_THROTTLE_RATES["DefaultUser"]
        elif "Admin" in self.user_groups:
            return api_settings.DEFAULT_THROTTLE_RATES["Admin"]
        elif "Advanced_user" in self.user_groups:
            return api_settings.DEFAULT_THROTTLE_RATES["Advanced_user"]
        elif "API_user" in self.user_groups:
            return api_settings.DEFAULT_THROTTLE_RATES["API_user"]

    def allow_request(self, request, view) -> bool:
        self.user_groups = request.user.groups.values_list("name", flat=True)
        self.rate = self.get_rate()
        self.num_requests, self.duration = self.parse_rate(self.rate)
        return super().allow_request(request, view)

    def get_cache_key(self, request, view) -> str | None:
        ident = (
            request.user.pk
            if request.user and request.user.is_authenticated
            else self.get_ident(request)
        )

        return self.cache_format % {"scope": "_".join(self.user_groups), "ident": ident}
