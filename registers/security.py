from flask_security import Security, login_user, login_required, logout_user, auth_required
from flask_security.models import fsqla_v3 as fsqla



def register_sec(db, app) -> Security:
    fsqla.FsModels.set_db_info(db)
    security = Security(app)
    return security
