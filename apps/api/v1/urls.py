from apps.api.v1 import app_api_v1
from apps.api.v1.users import (
    UsersListResource, UserResource, UserLoginResource,
    UserProfileResource, UserRegistrationResource,
)

app_api_v1.add_resource(
    UserLoginResource,
    "/users/login/",
    endpoint="user_login",
)
app_api_v1.add_resource(
    UserProfileResource,
    "/users/profile/",
    endpoint="current_user_profile",
)
app_api_v1.add_resource(
    UserRegistrationResource,
    "/users/registration/",
    endpoint="user_registration",
)
app_api_v1.add_resource(
    UsersListResource,
    "/users/",
    endpoint="users_list",
)
app_api_v1.add_resource(
    UserResource,
    "/users/<int:resource_id>",
    endpoint="user_details",
)
