from flask import Flask ,session, redirect , render_template , request , url_for , flash 
from flask_sqlalchemy import SQLAlchemy 
from flask_login import LoginManager , login_user ,logout_user , login_required , current_user , UserMixin
from passlib.hash import pbkdf2_sha256 
from werkzeug.security import check_password_hash, generate_password_hash
import secrets , string 
web = Flask(__name__)
web.config.from_object('config2.Config2')
web.secret_key = "234567"

login_manager = LoginManager()
login_manager.init_app(web)
login_manager.login_view = 'dangnhap'
db = SQLAlchemy(web)

class login(db.Model,UserMixin):
    __tablename__ = 'login'
    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(45) , nullable = False)
    last_name = db.Column(db.String(45) , nullable = False)
    username = db.Column(db.String(50) , nullable = False)
    email = db.Column(db.String(50) , nullable = False , unique = True)
    password_user = db.Column(db.String(50),nullable = False , unique = True)
    password_hash = db.Column(db.String(10000) , nullable = False ,unique = True)
    secret_pass = db.Column(db.String(10),nullable = False , unique = True)
    def __repr__(self):
        return f"User {self.username}"
    #Overridding
    def get_id(self):
        return str(self.ID)
class product(db.Model , UserMixin):
    __tablename__ = 'product'
    productID = db.Column(db.Integer, primary_key=True, autoincrement=True)  
    nameProduct = db.Column(db.String(100), nullable=True)
    priceProduct = db.Column(db.Integer, nullable=True)
    RAM = db.Column(db.Integer, nullable=True)
    ROM = db.Column(db.Integer, nullable=True)
    Color = db.Column(db.String(45), nullable=True)
    Chip = db.Column(db.String(45), nullable=True)
    image_url = db.Column(db.String(1000),nullable = True)
def get_user_by_username(username):
    user = db.session.query(login).filter_by(username=username).first()
    return user

def validate_password(password):
   #kiem tra do dai cua mat khau
    if len(password) < 10:
        return "Mật khẩu quá ngắn. Độ dài phải từ 10 ký tự trở lên."
    
    #kiem tra mat khau co cac ki tu dac biet hay khong 
    special_characters = ["@", "#", "$", "%", "!", "*", "&"]
    if not any(char in special_characters for char in password):
        return "Mật khẩu cần có ít nhất một ký tự đặc biệt."

   #kiem tra mat khau can it nhat mot chu cai thuong , in hoa va mot chi so 
    if not any(char.islower() for char in password):
        return "Mật khẩu cần chứa ít nhất một chữ cái thường."
    if not any(char.isupper() for char in password):
        return "Mật khẩu cần chứa ít nhất một chữ cái hoa."
    if not any(char.isdigit() for char in password):
        return "Mật khẩu cần chứa ít nhất một chữ số."

    return None  

@login_manager.user_loader
def load_user(user_id):
    return login.query.get(int(user_id))

#dam bao du lieu tao
with web.app_context():
    db.create_all()

@web.route('/')
@login_required
def home():
    return render_template("home1.html" , user = current_user) 

def home1():
    return render_template('home.html', current_page=1, total_pages=2)


 
@web.route('/dangky', methods=['GET', 'POST'])
def dangky():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        username = request.form['username']
        email = request.form['email']
        password_user = request.form['password']
        
        
       #mat khau phu hop
        length = 10
        special_characters = ["@", "#", "$", "%", "!", "*", "&"]

        
        if len(password_user) < length:
            flash("Mật khẩu quá ngắn", "danger")
            return render_template("dangky.html")

        
        if not any(char in special_characters for char in password_user):
            flash("Mật khẩu cần có một ký tự đặc biệt", "danger")
            return render_template("dangky.html")

        
        existing_user = login.query.filter_by(username=username).first()
        existing_email = login.query.filter_by(email=email).first()

        if existing_user or existing_email:
            flash("Tài khoản này đã tồn tại", "error")
            return render_template('dangky.html')
        secret_pass = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(10))
        password_hash = pbkdf2_sha256.hash(password_user)
        
        new_user = login(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            password_user = password_user,
            password_hash=password_hash,
            secret_pass = secret_pass
        )
        db.session.add(new_user)
        db.session.commit()

        flash("Đăng ký thành công! Vui lòng đăng nhập", "success")
        return redirect(url_for('dangnhap'))

    return render_template('dangky.html')

@web.route('/dangnhap', methods=['GET', 'POST'])
def dangnhap():
    if request.method == 'POST':
        username = request.form['username']
        password_user = request.form['password']

       
        user = login.query.filter_by(username=username).first()

        if user and pbkdf2_sha256.verify(password_user, user.password_hash):  # Compare with password_hash
            login_user(user)
            return redirect(url_for('home'))  # Redirect to the homepage or dashboard
        else:
            flash("Tài khoản hoặc mật khẩu không chính xác", "danger")
    
    return render_template('dangnhap.html')

@web.route('/quenmatkhau', methods=['GET', 'POST'])
def quenmatkhau():
    if request.method == 'POST':
        username = request.form['username']
        secret_pass = request.form['secret_pass']

        
        user = login.query.filter_by(username=username).first()
        
        if not user:
            flash("Tài khoản không tồn tại!", "danger")
            return redirect(url_for('quenmatkhau'))

        
        if secret_pass != user.secret_pass:
            flash("Mã bảo mật không đúng!", "danger")
            return redirect(url_for('quenmatkhau'))  # Giữ lại ở trang quên mật khẩu

        
        return redirect(url_for('doimatkhau'))

    return render_template('quenmatkhau.html')

@web.route('/doimatkhau', methods=['GET', 'POST'])
@login_required
def doimatkhau():
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

         if not check_password_hash(current_user.password_hash, current_password):
            flash("Mật khẩu cũ không chính xác!", "danger")
            return render_template('doimatkhau.html', user=current_user)

        
        if new_password != confirm_password:
            flash("Mật khẩu mới và xác nhận mật khẩu không trùng khớp!", "danger")
            return render_template('doimatkhau.html', user=current_user)

        
        password_error = validate_password(new_password)
        if password_error:
            flash(password_error, "danger")
            return render_template('doimatkhau.html', user=current_user)

        
        current_user.password_hash = generate_password_hash(new_password)
        db.session.commit()

        flash("Mật khẩu đã được thay đổi thành công!", "success")
        return redirect(url_for('home'))

    return render_template('doimatkhau.html', user=current_user)


@web.route('/dangxuat')
@login_required 
def dangxuat():
    logout_user()
    return redirect(url_for("dangnhap"))


@web.route('/thongtin', methods=['GET', 'POST'])
@login_required  # Ensure only logged-in users can update their info
def thongtin():
    if request.method == 'POST':
        #API Get cho form
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        username = request.form.get('username')
        password_user = request.form.get('password')  #mau khau moi

        #cap nhat 
        current_user.first_name = first_name
        current_user.last_name = last_name

        if username != current_user.username:
            current_user.username = username    

       
        if password_user:
            if pbkdf2_sha256.verify(password_user, current_user.password_hash):
                flash("Mật khẩu mới không được giống với mật khẩu cũ!", "danger")
                return render_template('thongtin.html', user=current_user)

            
            length = 10
            special_characters = ["@", "#", "$", "%", "!", "*", "&"]

            
            if len(password_user) < length:
                flash("Mật khẩu mới quá ngắn. Độ dài phải từ 10 ký tự trở lên.", "danger")
                return render_template('thongtin.html', user=current_user)

            
            if not any(char in special_characters for char in password_user):
                flash("Mật khẩu mới cần có ít nhất một ký tự đặc biệt.", "danger")
                return render_template('thongtin.html', user=current_user)

            
            if not password_user:
                flash("Mật khẩu không được để trống!", "danger")
                return render_template('thongtin.html', user=current_user)

            
            current_user.password_hash = pbkdf2_sha256.hash(password_user)

        
        db.session.commit()

        flash("Thông tin cá nhân đã được cập nhật thành công!", "success")

        return redirect(url_for('home'))

    return render_template('thongtin.html', user=current_user)



#
@web.route('/xoa_tai_khoan', methods=['POST', 'GET'])
@login_required
def xoa_tai_khoan():
    if request.method == 'POST':
        # Xóa tài khoản của người dùng hiện tại
        db.session.delete(current_user)
        db.session.commit()

        # Đăng xuất người dùng
        logout_user()

        # Hiển thị thông báo
        flash("Tài khoản đã được xóa thành công!", "success")

        # Chuyển hướng về trang đăng nhập
        return redirect(url_for("dangnhap"))

    return render_template("thongtin.html")

@web.route('/page2')
def page2():
   return render_template('page2.html',current_page=2,total_pages=2)

@web.route('/page3', methods=['GET', 'POST'])
def page3():
    all_products = product.query.all()
    products = all_products.copy()
    search_performed = False
    
    if request.method == "POST":
        search_query = request.form.get("search")
        sort_type = request.form.get("sort_type")
        sort_order = request.form.get("sort_order", "asc")
        
        if search_query:
            search_performed = True
            # Binary search
            products.sort(key=lambda x: x.nameProduct.lower() if x.nameProduct else '')
            left, right = 0, len(products) - 1
            matching_products = []
            while left <= right:
                mid = (left + right) // 2
                if products[mid].nameProduct and products[mid].nameProduct.lower() == search_query.lower():
                    matching_products.append(products[mid])
                    # Check for other matching products
                    i = mid - 1
                    while i >= 0 and products[i].nameProduct and products[i].nameProduct.lower() == search_query.lower():
                        matching_products.append(products[i])
                        i -= 1
                    i = mid + 1
                    while i < len(products) and products[i].nameProduct and products[i].nameProduct.lower() == search_query.lower():
                        matching_products.append(products[i])
                        i += 1
                    break
                elif not products[mid].nameProduct or products[mid].nameProduct.lower() < search_query.lower():
                    left = mid + 1
                else:
                    right = mid - 1
            products = matching_products
            if not products:
                flash("Không tìm thấy sản phẩm nào", "danger")
        
        if sort_type:
            reverse = sort_order == 'desc'
            if sort_type == 'price':
                # Quicksort implementation for price
                def quicksort(arr, low, high):
                    if low < high:
                        pi = partition(arr, low, high)
                        quicksort(arr, low, pi - 1)
                        quicksort(arr, pi + 1, high)
                
                def partition(arr, low, high):
                    i = low - 1
                    pivot = arr[high].priceProduct
                    for j in range(low, high):
                        if (arr[j].priceProduct >= pivot if reverse else arr[j].priceProduct <= pivot):
                            i += 1
                            arr[i], arr[j] = arr[j], arr[i]
                    arr[i + 1], arr[high] = arr[high], arr[i + 1]
                    return i + 1
                
                quicksort(products, 0, len(products) - 1)
            
            elif sort_type == 'ram_rom':
                # Updated merge sort implementation for RAM and ROM
                def merge_sort(arr):
                    if len(arr) > 1:
                        mid = len(arr) // 2
                        L = arr[:mid]
                        R = arr[mid:]
                        merge_sort(L)
                        merge_sort(R)
                        i = j = k = 0
                        while i < len(L) and j < len(R):
                            if reverse:
                                
                                if L[i].RAM > R[j].RAM or (L[i].RAM == R[j].RAM and L[i].ROM > R[j].ROM):
                                    arr[k] = L[i]
                                    i += 1
                                else:
                                    arr[k] = R[j]
                                    j += 1
                            else:
                                
                                if L[i].RAM < R[j].RAM or (L[i].RAM == R[j].RAM and L[i].ROM < R[j].ROM):
                                    arr[k] = L[i]
                                    i += 1
                                else:
                                    arr[k] = R[j]
                                    j += 1
                            k += 1
                        while i < len(L):
                            arr[k] = L[i]
                            i += 1
                            k += 1
                        while j < len(R):
                            arr[k] = R[j]
                            j += 1
                            k += 1

                merge_sort(products)

    return render_template('page3.html', products=products, all_products=all_products, search_performed=search_performed, current_page=3, total_pages=3)

if __name__ == '__main__':
    web.run(debug = True , host = '0.0.0.0' , port = 5000)
