# -*- coding: utf-8 -*-
import datetime

from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from app import db
from app.config import APP_SECRET_KEY, TOKEN_SCHEME, TOKEN_EXPIRE_TIME
from app.models.user_token_model import UserModel, UserTokenModel, expire_with_token


def token_generate(email=None, expires_in=TOKEN_EXPIRE_TIME):
    user = UserModel.query\
        .filter(UserModel.email == email)\
        .first()

    created_at = datetime.datetime.now()
    expired_at = created_at + datetime.timedelta(seconds=expires_in)

    data = {
        'user_id': user.id,
        'permission': user.permission,
        'created_at': created_at.isoformat(),
        'expired_at': expired_at.isoformat(),
        'expires_in': expires_in,
        'scheme': TOKEN_SCHEME
    }

    data['token'] = Serializer(APP_SECRET_KEY, expires_in=expires_in).dumps(data)

    user_token = UserTokenModel(
        user_id=user.id,
        token=data['token'],
        expired_at=expired_at
    )

    db.session.add(user_token)
    db.session.commit()

    return data


def token_load(auth=None):
    return Serializer(APP_SECRET_KEY).loads(auth.split()[1])


def token_is_auth(_auth=None, _id=0):
    if _auth is not None:
        data = token_load(_auth)

        if data['permission'] == 'ADMIN' or data['user_id'] == _id:
            if data['expired_at'] > datetime.datetime.now().isoformat():
                return True

    return False


