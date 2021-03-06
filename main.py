import os

from flask import Flask, render_template, redirect, request
from flask_login import LoginManager, login_user, login_required, logout_user, \
    current_user

from forms.search import SearchForm
from forms.users import RegisterForm, LoginForm
from forms.add import AddForm
from forms.pay import PayForm
from data.goods import Goods
from data.users import User
from data.association import Association
from data import db_session

# from forms.check import ChecksForm  # new


import sqlite3  # new!!!!!!!!!

db = 'db/db.db'  # new !!!!!!!

UPLOAD_FOLDER = 'static/img/'

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'secreret123123'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

res = []

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}


def get_favs():
    favs = []
    db_sess = db_session.create_session()
    goods = db_sess.query(Goods)
    a = db_sess.query(Association)
    if current_user.is_authenticated:
        for i in goods:
            for j in a:
                if current_user.id == j.user_id:
                    if i.id == j.favs_id:
                        favs.append(i.id)
    return favs


def get_category():
    category = []
    db_sess = db_session.create_session()
    goods = db_sess.query(Goods)
    if current_user.is_authenticated:
        for item in goods:
            if item.category not in category:
                category.append(item.category)
    return category


def get_ords():
    ords = []
    db_sess = db_session.create_session()
    goods = db_sess.query(Goods)
    a = db_sess.query(Association)
    if current_user.is_authenticated:
        for i in goods:
            for j in a:
                if current_user.id == j.user_id:
                    if i.id == j.orders_id:
                        ords.append(i.id)
    return ords


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


def main():
    db_session.global_init("db/db.db")
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


# new
@app.route('/func_run')
def func_run():
    x = request.args.get('par_1')
    y = request.args.get('par_2')
    z = request.args.get('par_3')
    if z == '2':
        if y == 'true':
            db_sess = db_session.create_session()
            product = Association(
                user_id=int(str(current_user).split()[1]),
                favs_id=None,
                orders_id=int(x) - 100,
                o_count=1
            )
            db_sess.add(product)
            db_sess.commit()
        else:
            db_sess = db_session.create_session()
            a = db_sess.query(Association).filter(Association.user_id == int(str(current_user).split()[1]),
                                                  Association.orders_id == int(x) - 100).first()
            db_sess.delete(a)
            db_sess.commit()
    elif z == "remove":
        if current_user.is_authenticated and current_user.role == "admin":
            print("delete", x, y, z)
            db_sess = db_session.create_session()
            item = db_sess.query(Goods).filter(Goods.id == int(x)).first()
            if item:
                db_sess.delete(item)

                db_sess.commit()

    elif z.startswith('sale'):
        if current_user.is_authenticated and current_user.role == "admin":
            print("add sale", x, y, z)

            con = sqlite3.connect(db)
            cur = con.cursor()
            if len(z.split(' ')[1]) == 0:
                print('???????????? ????????????')
            else:
                cur.execute("UPDATE goods SET sale = ? WHERE id = ?", (z.split(' ')[1], int(x)))
                con.commit()

    else:
        if y == 'true':
            db_sess = db_session.create_session()
            product = Association(
                user_id=int(str(current_user).split()[1]),
                favs_id=int(x),
                orders_id=None,
                o_count=None
            )
            db_sess.add(product)
            db_sess.commit()
        else:
            db_sess = db_session.create_session()
            a = db_sess.query(Association).filter(Association.user_id == int(str(current_user).split()[1]),
                                                  Association.favs_id == int(x)).first()
            db_sess.delete(a)
            db_sess.commit()
    return '', 204


@app.route("/", methods=['GET', 'POST'])
def index():
    global res
    categories = get_category()
    res.clear()
    form = SearchForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        goods = db_sess.query(Goods)
        for i in goods:
            if str(form.ttle.data).lower() in str(i.title).lower():
                res.append(i.id)
        return redirect('/search_results')
    db_sess = db_session.create_session()
    goods = db_sess.query(Goods)
    # form4 = FavsForm()
    # form4 = ChecksForm()  # new
    # if form4.validate_on_submit():
    #     db_sess = db_session.create_session()
    #     assoc = Association(
    #         user_id=current_user.id,
    #         favs_id=form4.favs_id.data,
    #         orders_id=0,
    #         o_count=0
    #     )
    #     db_sess.add(assoc)
    #     db_sess.commit()
    if current_user.is_authenticated:
        return render_template("main.html", title='?????????????? ????????????????', goods=goods,
                               favs=get_favs(), ords=get_ords(),
                               form2=form, cats=categories, role=current_user.role)
    else:
        return render_template("main.html", title='?????????????? ????????????????', goods=goods,
                               favs=get_favs(), ords=get_ords(),
                               form2=form, cats=categories, role=False)


@app.route('/basket', methods=['GET', 'POST'])
def basket():
    global res
    ords = get_ords()
    form = SearchForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        goods = db_sess.query(Goods)
        for i in goods:
            if str(form.ttle.data).lower() in str(i.title).lower():
                res.append(i.id)
        return redirect('/search_results')

    db_sess = db_session.create_session()
    goods = db_sess.query(Goods)
    summ = 0
    for i in goods:
        if i.id in ords:
            summ += i.cost

    return render_template("basket.html", title='??????????????', goods=goods,
                           ords=ords, summ=summ, form2=form)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_category_choice():
    category = [('???????????????? ??????????????????', '???????????????? ??????????????????')]
    buffer = []
    db_sess = db_session.create_session()
    goods = db_sess.query(Goods)
    if current_user.is_authenticated:
        for item in goods:
            if item.category not in buffer:
                category.append((item.category, item.category))
                buffer.append(item.category)
    return category


@app.route('/add', methods=['GET', 'POST'])
def add():
    if current_user.is_authenticated and current_user.role == "admin":
        form2 = SearchForm()
        if form2.validate_on_submit():
            db_sess = db_session.create_session()
            goods = db_sess.query(Goods)
            for i in goods:
                if str(form2.ttle.data).lower() in str(i.title).lower():
                    res.append(i.id)
            return redirect('/search_results')
        form3 = AddForm()
        cats = get_category_choice()
        form3.category.choices = cats
        if form3.validate_on_submit() and (
                (form3.category.data == "???????????????? ??????????????????" and form3.new_category.data != "") or (
                form3.category.data != "???????????????? ??????????????????" and form3.new_category.data == "")):
            db_sess = db_session.create_session()

            file = request.files["file"]
            filename = file.filename

            caty = ""
            if form3.category.data == "???????????????? ??????????????????":
                caty = form3.new_category.data
            else:
                caty = form3.category.data

            product = Goods(
                title=form3.title.data,
                cost=form3.cost.data,
                description=form3.description.data,
                category=caty,
                rate=0,
                image="/static/img/" + filename,
            )
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # img = form3.image
            # img.file.save(os.path.join(app.config['UPLOAD_FOLDER'], form3.image.file.filename))

            db_sess.add(product)
            db_sess.commit()
            return redirect('/')
        return render_template('add.html', title='???????????????????? ????????????', form2=form2,
                               form3=form3)
    else:
        return redirect('/')


@app.route('/pay', methods=['GET', 'POST'])
def pay():
    global res
    ords = get_ords()
    db_sess = db_session.create_session()
    goods = db_sess.query(Goods)
    summ = 0
    for i in goods:
        if i.id in ords:
            summ += i.cost

    form2 = SearchForm()
    if form2.validate_on_submit():
        db_sess = db_session.create_session()
        goods = db_sess.query(Goods)
        for i in goods:
            if str(form2.ttle.data).lower() in str(i.title).lower():
                res.append(i.id)
        return redirect('/search_results')

    form3 = PayForm()
    if form3.validate_on_submit():
        if current_user.balance >= summ:
            new_bal = current_user.balance - summ
            db_sess = db_session.create_session()
            for i in ords:
                a = db_sess.query(Association).filter(Association.user_id == int(current_user.id),
                                                      Association.orders_id == i).first()
                db_sess.delete(a)
                db_sess.commit()

            con = sqlite3.connect(db)
            cur = con.cursor()
            cur.execute("UPDATE users SET balance = ? WHERE id = ?", (new_bal, current_user.id))
            con.commit()

        return redirect('/')

    return render_template("pay.html", title='????????????', goods=goods,
                           ords=ords, summ=summ, form2=form2, form3=form3, balance=current_user.balance)


@app.route('/favorites', methods=['GET', 'POST'])
def favorites():
    global res
    form = SearchForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        goods = db_sess.query(Goods)
        for i in goods:
            if str(form.ttle.data).lower() in str(i.title).lower():
                res.append(i.id)
        return redirect('/search_results')

    db_sess = db_session.create_session()
    goods = db_sess.query(Goods)
    return render_template("favorites.html", title='??????????????????', goods=goods,
                           favs=get_favs(), form2=form)


@app.route('/search_results', methods=['GET', 'POST'])
def search_results():
    global res
    categories = get_category()
    form = SearchForm()
    if form.validate_on_submit():
        res.clear()
        db_sess = db_session.create_session()
        goods = db_sess.query(Goods)
        for i in goods:
            if str(form.ttle.data).lower() in str(i.title).lower():
                res.append(i.id)
        return redirect('/search_results')

    # form.button.data true - false
    db_sess = db_session.create_session()
    goods = db_sess.query(Goods)

    return render_template('search_results.html', title='???????????????????? ????????????',
                           res=res, form2=form,
                           goods=goods,
                           favs=get_favs(), ords=get_ords(), cats=categories)


@app.route("/categories/<int:r>", methods=['GET', 'POST'])
def cat(r):
    global res
    categories = get_category()
    form = SearchForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        goods = db_sess.query(Goods)
        for i in goods:
            if str(form.ttle.data).lower() in str(i.title).lower():
                res.append(i.id)
        return redirect('/search_results')

    db_sess = db_session.create_session()
    goods = db_sess.query(Goods)
    col = 0
    for i in goods:
        if i.category == categories[r - 1]:
            col += 1
    return render_template("categories.html", title='?????????? ???? ????????????????????',
                           goods=goods, favs=get_favs(),
                           ords=get_ords(),
                           form2=form, cat=categories[r - 1], col=col, cats=categories)


@app.route("/product/<int:r>", methods=['GET', 'POST'])
def product(r):
    global res
    form = SearchForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        goods = db_sess.query(Goods)
        for i in goods:
            if str(form.ttle.data).lower() in str(i.title).lower():
                res.append(i.id)
        return redirect('/search_results')

    db_sess = db_session.create_session()
    goods = db_sess.query(Goods)
    for i in goods:
        if i.id == r:
            tl = i.title
    return render_template("product.html", title=f'{tl}', goods=goods,
                           favs=get_favs(),
                           ords=get_ords(),
                           form2=form, i_id=r)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    global res

    form2 = SearchForm()
    if form2.validate_on_submit():
        db_sess = db_session.create_session()
        goods = db_sess.query(Goods)
        for i in goods:
            if str(form2.ttle.data).lower() in str(i.title).lower():
                res.append(i.id)
        return redirect('/search_results')

    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='??????????????????????',
                                   form=form,
                                   message="???????????? ???? ??????????????????", form2=form2)
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='??????????????????????',
                                   form=form,
                                   message="?????????? ???????????????????????? ?????? ????????",
                                   form2=form2)
        if form.email.data == "adminpanel@adminpanel.adminpanel":
            user = User(
                surname=form.surname.data,
                name=form.name.data,
                email=form.email.data,
                role="admin",
                balance=0
            )
        else:
            user = User(
                surname=form.surname.data,
                name=form.name.data,
                email=form.email.data,
                role="user"
            )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='??????????????????????', form=form,
                           form2=form2)


@app.route('/login', methods=['GET', 'POST'])
def login():
    global res

    form2 = SearchForm()
    if form2.validate_on_submit():
        db_sess = db_session.create_session()
        goods = db_sess.query(Goods)
        for i in goods:
            if str(form2.ttle.data).lower() in str(i.title).lower():
                res.append(i.id)
        return redirect('/search_results')

    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="???????????????????????? ?????????? ?????? ????????????",
                               form=form,
                               form2=form2)
    return render_template('login.html', title='??????????????????????', form=form,
                           form2=form2)


if __name__ == '__main__':
    main()
