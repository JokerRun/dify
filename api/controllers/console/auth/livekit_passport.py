import os

from dotenv import load_dotenv
from flask_login import current_user
from flask_restful import Resource

# livekit-api https://github.com/livekit/python-sdks
from livekit import api as lk_api

from controllers.console import api
from libs.login import login_required

load_dotenv()


class LivekitPassportApi(Resource):
    """Resource for user login."""

    @login_required
    def get(self):
        # 生成随机房间名
        room_name = f"room-{os.urandom(4).hex()}-{os.urandom(4).hex()}"
        
        # 创建带完整权限的 token
        token = lk_api.AccessToken(
            api_key=os.getenv("LIVEKIT_API_KEY"),
            api_secret=os.getenv("LIVEKIT_API_SECRET")
        ) \
            .with_identity(current_user.email) \
            .with_name(current_user.email) \
            .with_grants(lk_api.VideoGrants(
                room_join=True,
                room=room_name,  # 修复: 使用正确的 room_name 变量
                can_publish=True,
                can_publish_data=True,
                can_subscribe=True,
            )).to_jwt()
            
        return {
            "result": "success", 
            "data": {
                "identity": current_user.email,
                "accessToken": token,
                "room": room_name,
            }
        }


api.add_resource(LivekitPassportApi, "/livekit-passport")
