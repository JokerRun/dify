import uuid

from flask import request
from flask_restful import Resource
from werkzeug.exceptions import NotFound, Unauthorized

from controllers.web import api
from controllers.web.error import WebSSOAuthRequiredError
from extensions.ext_database import db
from libs.passport import PassportService
from models.model import App, EndUser, Site
from services.feature_service import FeatureService


class PassportResource(Resource):
    """Base resource for passport."""
    def get(self):

        system_features = FeatureService.get_system_features()
        if system_features.sso_enforced_for_web:
            raise WebSSOAuthRequiredError()

        app_code = request.headers.get('X-App-Code')
        if app_code is None:
            raise Unauthorized('X-App-Code header is missing.')

        user_id = None

        # 尝试从Authorization头中获取用户信息
        auth_header = request.headers.get('Authorization')
        if auth_header and ' ' in auth_header:
            auth_scheme, tk = auth_header.split(None, 1)
            if auth_scheme.lower() == 'bearer':
                try:
                    decoded = PassportService().verify(tk)
                    user_id = decoded.get('user_id')
                except:
                    pass

        # 如果从Authorization头中未获取到用户信息，则尝试从referrer中获取console token
        if not user_id:
            referrer = request.referrer
            console_token = referrer.split('?')[1].split('=')[1] if '?' in referrer and '=' in referrer.split('?')[1] else ''
            if console_token:
                decoded = PassportService().verify(console_token)
                user_id = decoded.get('user_id')
            else:
                raise Unauthorized('console_token is missing.')

        # 检查用户是否存在
        if user_id:
            from models.account import Account
            account = db.session.query(Account).filter(Account.id == user_id).first()
            if not account:
                raise Unauthorized('account is missing.')

        # get site from db and check if it is normal
        site = db.session.query(Site).filter(
            Site.code == app_code,
            Site.status == 'normal'
        ).first()
        if not site:
            raise NotFound()
        # get app from db and check if it is normal and enable_site
        app_model = db.session.query(App).filter(App.id == site.app_id).first()
        if not app_model or app_model.status != 'normal' or not app_model.enable_site:
            raise NotFound()

        end_user = db.session.query(EndUser).filter(EndUser.id == user_id).first()
        if not end_user:
            end_user = EndUser(
                id=user_id,
                tenant_id=app_model.tenant_id,
                app_id=app_model.id,
                type='browser',
                is_anonymous=True,
                session_id=generate_session_id(),
            )
            db.session.add(end_user)
            db.session.commit()

        payload = {
            "iss": site.app_id,
            'sub': 'Web API Passport',
            'app_id': site.app_id,
            'app_code': app_code,
            'end_user_id': end_user.id,
        }

        tk = PassportService().issue(payload)

        return {
            'access_token': tk,
        }


api.add_resource(PassportResource, '/passport')


def generate_session_id():
    """
    Generate a unique session ID.
    """
    while True:
        session_id = str(uuid.uuid4())
        existing_count = db.session.query(EndUser) \
            .filter(EndUser.session_id == session_id).count()
        if existing_count == 0:
            return session_id
