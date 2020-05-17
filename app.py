from app import app
from app.models import *

if __name__ == '__main__':
    db.drop_all()
    db.create_all()
    admin = Admin(username='admin')
    password = 'admin'
    admin.password = admin.makePassword(password)
    db.session.add(admin)
    db.session.commit()
    app.run(debug=True)