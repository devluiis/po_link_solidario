from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import random
import string

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'sua_chave_secreta_padrao_muito_segura_aqui')

# --- Configuração do Banco de Dados ---
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST', 'localhost')}/{os.getenv('DB_NAME')}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
# --- Fim Configuração do Banco de Dados ---

# --- Configuração de Upload de Imagens ---
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
# --- Fim Configuração de Upload ---


# --- Modelos de Dados ---

class Usuario(db.Model):
    __tablename__ = 'Usuario'
    id_usuario = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    telefone = db.Column(db.String(20))
    senha = db.Column(db.String(255), nullable=False)
    tipo_perfil = db.Column(db.Enum('Morador', 'ONG', 'Associação', 'Admin'), nullable=False)
    localizacao = db.Column(db.String(150))
    ativo = db.Column(db.Boolean, default=True)

    produtos = db.relationship('Produto', backref='dono', lazy=True)
    interesses = db.relationship('Interesse', backref='interessado', lazy=True, foreign_keys='Interesse.id_interessado')
    doacoes_feitas = db.relationship('Transacao', backref='doador', lazy=True, foreign_keys='Transacao.id_doador')
    doacoes_recebidas = db.relationship('Transacao', backref='receptor', lazy=True, foreign_keys='Transacao.id_receptor')
    doacoes_direcionadas_instituicao = db.relationship('DoacaoDirecionada', backref='instituicao_alvo', lazy=True, foreign_keys='DoacaoDirecionada.id_instituicao')
    notificacoes_recebidas = db.relationship('Notificacao', backref='usuario_notificado', lazy=True, foreign_keys='Notificacao.id_usuario_notificado')
    notificacoes_enviadas = db.relationship('Notificacao', backref='remetente', lazy=True, foreign_keys='Notificacao.id_remetente')


    def __repr__(self):
        return f'<Usuario {self.email}>'

class Produto(db.Model):
    __tablename__ = 'Produto'
    id_produto = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('Usuario.id_usuario', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    categoria = db.Column(db.String(50))
    condicao = db.Column(db.String(50))
    status = db.Column(db.String(50), default='Aguardando Moderação', nullable=False)
    data_cadastro = db.Column(db.DateTime, default=db.func.now())

    fotos = db.relationship('FotoProduto', backref='produto', lazy=True)
    interesses_recebidos = db.relationship('Interesse', backref='produto_interessado', lazy=True)
    transacoes_produto = db.relationship('Transacao', backref='produto_transacao', lazy=True)
    doacoes_direcionadas_produto = db.relationship('DoacaoDirecionada', backref='produto_doacao_direcionada', lazy=True)

    def __repr__(self):
        return f'<Produto {self.nome}>'

class FotoProduto(db.Model):
    __tablename__ = 'FotoProduto'
    id_foto = db.Column(db.Integer, primary_key=True)
    id_produto = db.Column(db.Integer, db.ForeignKey('Produto.id_produto', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    url_foto = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'<FotoProduto {self.url_foto}>'

class Interesse(db.Model):
    __tablename__ = 'Interesse'
    id_interesse = db.Column(db.Integer, primary_key=True)
    id_produto = db.Column(db.Integer, db.ForeignKey('Produto.id_produto', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    id_interessado = db.Column(db.Integer, db.ForeignKey('Usuario.id_usuario', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    data_interesse = db.Column(db.DateTime, default=db.func.now())
    mensagem = db.Column(db.Text)

    def __repr__(self):
        return f'<Interesse {self.id_interesse} - Prod:{self.id_produto} User:{self.id_interessado}>'

class Transacao(db.Model):
    __tablename__ = 'Transacao'
    id_transacao = db.Column(db.Integer, primary_key=True)
    id_produto = db.Column(db.Integer, db.ForeignKey('Produto.id_produto', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    id_doador = db.Column(db.Integer, db.ForeignKey('Usuario.id_usuario', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    id_receptor = db.Column(db.Integer, db.ForeignKey('Usuario.id_usuario', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    tipo_transacao = db.Column(db.Enum('Troca', 'Doação'), nullable=False)
    data_transacao = db.Column(db.DateTime, default=db.func.now())

    def __repr__(self):
        return f'<Transacao {self.id_transacao} - Prod:{self.id_produto} Doador:{self.id_doador} Receptor:{self.id_receptor}>'

class DoacaoDirecionada(db.Model):
    __tablename__ = 'DoacaoDirecionada'
    id_doacao = db.Column(db.Integer, primary_key=True)
    id_produto = db.Column(db.Integer, db.ForeignKey('Produto.id_produto', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    id_instituicao = db.Column(db.Integer, db.ForeignKey('Usuario.id_usuario', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    descricao_necessidade = db.Column(db.Text)
    status = db.Column(db.Enum('Pendente', 'Realizada'), default='Pendente', nullable=False)

    def __repr__(self):
        return f'<DoacaoDirecionada {self.id_doacao} - Prod:{self.id_produto} Inst:{self.id_instituicao}>'

class Notificacao(db.Model):
    __tablename__ = 'Notificacao'
    id_notificacao = db.Column(db.Integer, primary_key=True)
    id_usuario_notificado = db.Column(db.Integer, db.ForeignKey('Usuario.id_usuario', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    id_remetente = db.Column(db.Integer, db.ForeignKey('Usuario.id_usuario', ondelete='SET NULL', onupdate='CASCADE'))
    tipo_notificacao = db.Column(db.String(50), nullable=False)
    mensagem = db.Column(db.Text, nullable=False)
    url_redirecionamento = db.Column(db.String(255))
    data_criacao = db.Column(db.DateTime, default=db.func.now())
    lida = db.Column(db.Boolean, default=False)

    remetente_obj = db.relationship('Usuario', foreign_keys=[id_remetente], backref='notificacoes_enviadas_custom')

    def __repr__(self):
        return f'<Notificacao {self.id_notificacao} para User {self.id_usuario_notificado}>'

# --- Fim Modelos de Dados ---


# --- Context Processor para injetar o usuário logado e notificações em todos os templates ---
@app.context_processor
def inject_user_and_notifications():
    user_id = session.get('user_id')
    current_user = None
    unread_notifications_count = 0
    recent_notifications = []
    if user_id:
        current_user = Usuario.query.get(user_id)
        if current_user:
            unread_notifications_count = Notificacao.query.filter_by(id_usuario_notificado=user_id, lida=False).count()
            recent_notifications = Notificacao.query.filter_by(id_usuario_notificado=user_id).order_by(Notificacao.data_criacao.desc()).limit(5).all()
    return dict(current_user=current_user, unread_notifications_count=unread_notifications_count, recent_notifications=recent_notifications)


# --- Funções Auxiliares (Para upload de arquivos) ---
def generate_unique_filename(filename):
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    ext = filename.rsplit('.', 1)[1].lower()
    return f"{timestamp}_{random_string}.{ext}"

# --- Rotas da Aplicação ---

@app.route('/')
def index():
    featured_products = Produto.query.filter_by(status='Disponível').order_by(Produto.data_cadastro.desc()).limit(3).all()
    return render_template('index.html', featured_products=featured_products)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome = request.form['name']
        email = request.form['email']
        telefone = request.form.get('phone')
        localizacao = request.form['location']
        tipo_perfil = request.form['profile_type']
        senha = request.form['password']
        confirm_senha = request.form['confirm_password']

        if senha != confirm_senha:
            flash('As senhas não coincidem!', 'danger')
            return render_template('auth/register.html', form=request.form)

        existing_user = Usuario.query.filter_by(email=email).first()
        if existing_user:
            flash('E-mail já cadastrado. Tente outro ou faça login.', 'danger')
            return render_template('auth/register.html', form=request.form)

        hashed_password = generate_password_hash(senha)

        new_user = Usuario(
            nome=nome,
            email=email,
            senha=hashed_password,
            telefone=telefone,
            localizacao=localizacao,
            tipo_perfil=tipo_perfil,
            ativo=True
        )
        db.session.add(new_user)
        db.session.commit()

        flash('Cadastro realizado com sucesso! Faça login para continuar.', 'success')
        return redirect(url_for('login'))
    return render_template('auth/register.html')

@app.route('/about')
def about():
    """Página 'Saiba Mais' sobre o projeto."""
    return render_template('about.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['password']

        user = Usuario.query.filter_by(email=email).first()

        if user and check_password_hash(user.senha, senha):
            if not user.ativo:
                flash('Sua conta está inativa. Entre em contato com a administração.', 'warning')
                return render_template('auth/login.html', form=request.form)

            session['user_id'] = user.id_usuario
            flash(f'Bem-vindo(a) de volta, {user.nome}!', 'success')
            return redirect(url_for('profile'))
        else:
            flash('E-mail ou senha incorretos.', 'danger')
    return render_template('auth/login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('index'))

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if not session.get('user_id'):
        flash('Você precisa estar logado para acessar esta página.', 'warning')
        return redirect(url_for('login'))

    current_user_data = Usuario.query.get(session['user_id'])
    if not current_user_data:
        session.pop('user_id', None)
        flash('Erro ao carregar perfil do usuário. Por favor, faça login novamente.', 'danger')
        return redirect(url_for('login'))

    # Pega produtos que o usuário cadastrou
    user_products = Produto.query.filter_by(id_usuario=current_user_data.id_usuario).all()
    # Pega interesses que o usuário manifestou
    user_interests = Interesse.query.filter_by(id_interessado=current_user_data.id_usuario).all()


    if request.method == 'POST':
        current_user_data.nome = request.form['name']
        current_user_data.telefone = request.form.get('phone')
        current_user_data.localizacao = request.form['location']

        db.session.commit()
        flash('Perfil atualizado com sucesso!', 'success')
        return redirect(url_for('profile'))

    return render_template('user/profile.html', user_products=user_products, current_user=current_user_data, user_interests=user_interests)

@app.route('/products/add', methods=['GET', 'POST'])
def add_product():
    if not session.get('user_id'):
        flash('Você precisa estar logado para cadastrar produtos.', 'warning')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        nome = request.form['name']
        descricao = request.form['description']
        categoria = request.form['category']
        condicao = request.form['condition']
        trans_type_from_form = request.form['trans_type']

        if 'image_upload' not in request.files:
            flash('Nenhuma imagem selecionada para upload.', 'danger')
            return render_template('product/add_product.html', categories=categories_list)
        
        file = request.files['image_upload']
        if file.filename == '':
            flash('Nenhum arquivo selecionado.', 'danger')
            return render_template('product/add_product.html', categories=categories_list)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_filename = generate_unique_filename(filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(file_path)
            image_url_to_save = url_for('static', filename=f'uploads/{unique_filename}')
        else:
            flash('Tipo de arquivo não permitido. Apenas PNG, JPG, JPEG, GIF.', 'danger')
            return render_template('product/add_product.html', categories=categories_list)


        new_product = Produto(
            nome=nome,
            descricao=descricao,
            categoria=categoria,
            condicao=condicao,
            status='Aguardando Moderação',
            id_usuario=session['user_id']
        )
        db.session.add(new_product)
        db.session.commit()

        new_foto = FotoProduto(id_produto=new_product.id_produto, url_foto=image_url_to_save)
        db.session.add(new_foto)
        db.session.commit()

        flash('Produto cadastrado com sucesso! Ele estará visível após a moderação.', 'success')
        return redirect(url_for('products_list'))
    
    categories_list = [
        'Roupas', 'Móveis', 'Eletrodomésticos', 'Materiais Escolares',
        'Livros', 'Brinquedos', 'Eletrônicos', 'Outros'
    ]
    return render_template('product/add_product.html', categories=categories_list)


@app.route('/products/edit/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    if not session.get('user_id'):
        flash('Você precisa estar logado para editar produtos.', 'warning')
        return redirect(url_for('login'))

    product_to_edit = Produto.query.get(product_id)

    if not product_to_edit or product_to_edit.id_usuario != session['user_id']:
        flash('Produto não encontrado ou você não tem permissão para editá-lo.', 'danger')
        return redirect(url_for('profile'))
    
    categories_list = [
        'Roupas', 'Móveis', 'Eletrodomésticos', 'Materiais Escolares',
        'Livros', 'Brinquedos', 'Eletrônicos', 'Outros'
    ]

    if request.method == 'POST':
        product_to_edit.nome = request.form['name']
        product_to_edit.descricao = request.form['description']
        product_to_edit.categoria = request.form['category']
        product_to_edit.condicao = request.form['condition']
        
        if 'image_upload' in request.files:
            file = request.files['image_upload']
            if file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                unique_filename = generate_unique_filename(filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(file_path)
                image_url_to_save = url_for('static', filename=f'uploads/{unique_filename}')

                for foto in product_to_edit.fotos:
                    try:
                        relative_path = foto.url_foto.split(url_for('static', filename=''))[1]
                        full_path = os.path.join(app.root_path, 'static', relative_path)
                        if os.path.exists(full_path):
                            os.remove(full_path)
                    except Exception as e:
                        print(f"Erro ao deletar arquivo de imagem antiga {foto.url_foto}: {e}")
                    db.session.delete(foto)
                db.session.commit()
                
                new_foto = FotoProduto(id_produto=product_to_edit.id_produto, url_foto=image_url_to_save)
                db.session.add(new_foto)
                
            elif file.filename != '':
                 flash('Tipo de arquivo da nova imagem não permitido. Apenas PNG, JPG, JPEG, GIF.', 'danger')
                 return render_template('product/edit_product.html', product=product_to_edit, categories=categories_list)

        product_to_edit.status = 'Aguardando Moderação'

        db.session.commit()
        flash('Produto atualizado com sucesso! Ele estará visível após a moderação.', 'success')
        return redirect(url_for('profile'))

    return render_template('product/edit_product.html', product=product_to_edit, categories=categories_list)


@app.route('/products/delete/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    if not session.get('user_id'):
        flash('Você precisa estar logado para remover produtos.', 'warning')
        return redirect(url_for('login'))

    product_to_delete = Produto.query.get(product_id)

    if not product_to_delete or product_to_delete.id_usuario != session['user_id']:
        flash('Produto não encontrado ou você não tem permissão para removê-lo.', 'danger')
        return redirect(url_for('profile'))

    for foto in product_to_delete.fotos:
        try:
            relative_path = foto.url_foto.split(url_for('static', filename=''))[1]
            full_path = os.path.join(app.root_path, 'static', relative_path)
            if os.path.exists(full_path):
                os.remove(full_path)
        except Exception as e:
            print(f"Erro ao deletar arquivo de imagem {foto.url_foto}: {e}")

    db.session.delete(product_to_delete)
    db.session.commit()
    flash('Produto removido com sucesso!', 'success')
    return redirect(url_for('profile'))


@app.route('/products')
def products_list():
    category_filter = request.args.get('category')
    location_filter = request.args.get('location')
    trans_type_filter = request.args.get('type')
    search_query = request.args.get('q')

    query = Produto.query.filter_by(status='Disponível')

    if category_filter and category_filter != 'all':
        query = query.filter_by(categoria=category_filter)
    if location_filter:
        query = query.join(Usuario).filter(Usuario.localizacao.ilike(f'%{location_filter}%'))
    
    if search_query:
        search_pattern = f"%{search_query}%"
        query = query.filter(
            (Produto.nome.ilike(search_pattern)) | (Produto.descricao.ilike(search_pattern))
        )
    
    products = query.all()
    
    categories_list = [
        'Roupas', 'Móveis', 'Eletrodomésticos', 'Materiais Escolares',
        'Livros', 'Brinquedos', 'Eletrônicos', 'Outros'
    ]

    return render_template('product/products_list.html', products=products,
                           selected_category=category_filter, selected_location=location_filter,
                           selected_type=trans_type_filter, search_query=search_query,
                           categories=categories_list)


@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Produto.query.get(product_id)
    if not product or product.status != 'Disponível':
        flash('Produto não encontrado ou não está disponível.', 'danger')
        return redirect(url_for('products_list'))

    owner = Usuario.query.get(product.id_usuario)
    product_photos = FotoProduto.query.filter_by(id_produto=product.id_produto).all()
    
    return render_template('product/product_detail.html', product=product, owner=owner, photos=product_photos)

@app.route('/product/<int:product_id>/express_interest', methods=['POST'])
def express_interest(product_id):
    if not session.get('user_id'):
        flash('Você precisa estar logado para manifestar interesse.', 'warning')
        return redirect(url_for('login'))

    product = Produto.query.get(product_id)
    if not product or product.status != 'Disponível':
        flash('Produto não encontrado ou não está disponível para manifestação de interesse.', 'danger')
        return redirect(url_for('products_list'))
    
    if product.id_usuario == session['user_id']:
        flash('Você não pode manifestar interesse no seu próprio produto.', 'warning')
        return redirect(url_for('product_detail', product_id=product.id_produto))

    existing_interest = Interesse.query.filter_by(
        id_produto=product.id_produto,
        id_interessado=session['user_id']
    ).first()

    if existing_interest:
        flash('Você já manifestou interesse neste produto. Aguarde o contato do proprietário.', 'info')
        return redirect(url_for('product_detail', product_id=product.id_produto))

    mensagem_interesse = request.form.get('message_of_interest')

    new_interest = Interesse(
        id_produto=product.id_produto,
        id_interessado=session['user_id'],
        mensagem=mensagem_interesse
    )
    db.session.add(new_interest)
    
    owner_id = product.id_usuario
    interested_user_obj = Usuario.query.get(session['user_id'])
    
    notification_message = f'O usuário "{interested_user_obj.nome}" manifestou interesse no seu produto "{product.nome}".'
    notification_url = url_for('product_detail', product_id=product.id_produto)
    
    new_notification = Notificacao(
        id_usuario_notificado=owner_id,
        id_remetente=session['user_id'],
        tipo_notificacao='interesse_produto',
        mensagem=notification_message,
        url_redirecionamento=notification_url,
        lida=False
    )
    db.session.add(new_notification)

    db.session.commit()

    flash(f'Seu interesse no produto "{product.nome}" foi registrado. O proprietário foi notificado!', 'success')
    
    return redirect(url_for('product_detail', product_id=product.id_produto))

# Nova rota para cancelar interesse
@app.route('/interest/cancel/<int:interest_id>', methods=['POST'])
def cancel_interest(interest_id):
    if not session.get('user_id'):
        flash('Você precisa estar logado para realizar esta ação.', 'warning')
        return redirect(url_for('login'))

    interest_to_cancel = Interesse.query.get(interest_id)

    # Garante que o interesse existe e pertence ao usuário logado
    if not interest_to_cancel or interest_to_cancel.id_interessado != session['user_id']:
        flash('Interesse não encontrado ou você não tem permissão para cancelá-lo.', 'danger')
        return redirect(url_for('profile'))
    
    product_name = interest_to_cancel.produto_interessado.nome # Pega o nome do produto antes de deletar o interesse
    db.session.delete(interest_to_cancel)
    db.session.commit()

    flash(f'Seu interesse no produto "{product_name}" foi cancelado com sucesso.', 'info')
    return redirect(url_for('profile'))


@app.route('/product/<int:product_id>/complete_transaction', methods=['POST'])
def complete_transaction(product_id):
    if not session.get('user_id'):
        flash('Você precisa estar logado para completar transações.', 'warning')
        return redirect(url_for('login'))

    product = Produto.query.get(product_id)

    if not product or product.id_usuario != session['user_id']:
        flash('Produto não encontrado ou você não tem permissão para completar esta transação.', 'danger')
        return redirect(url_for('profile'))

    tipo_transacao = request.form.get('transaction_type')
    receptor_email = request.form.get('receptor_email')

    if not receptor_email:
        flash('É necessário informar o e-mail do receptor para registrar a transação.', 'danger')
        return redirect(url_for('profile'))

    receptor_user = Usuario.query.filter_by(email=receptor_email).first()

    if not receptor_user:
        flash(f'Usuário receptor com e-mail "{receptor_email}" não encontrado.', 'danger')
        return redirect(url_for('profile'))
    
    if receptor_user.id_usuario == session['user_id']:
        flash('Você não pode ser o doador e o receptor da mesma transação.', 'danger')
        return redirect(url_for('profile'))

    product.status = tipo_transacao
    db.session.commit()

    new_transacao = Transacao(
        id_produto=product.id_produto,
        id_doador=session['user_id'],
        id_receptor=receptor_user.id_usuario,
        tipo_transacao=tipo_transacao
    )
    db.session.add(new_transacao)

    notification_message_receptor = f'Parabéns! Você recebeu o produto "{product.nome}" (via {tipo_transacao}).'
    notification_url_receptor = url_for('product_detail', product_id=product.id_produto)
    new_notification_receptor = Notificacao(
        id_usuario_notificado=receptor_user.id_usuario,
        id_remetente=session['user_id'],
        tipo_notificacao='transacao_concluida',
        mensagem=notification_message_receptor,
        url_redirecionamento=notification_url_receptor,
        lida=False
    )
    db.session.add(new_notification_receptor)

    db.session.commit()

    flash(f'Transação de "{product.nome}" marcada como {product.status} e registrada com {receptor_user.nome}!', 'success')
    return redirect(url_for('profile'))

@app.route('/donations/directed', methods=['GET', 'POST'])
def directed_donation():
    if not session.get('user_id'):
        flash('Você precisa estar logado para acessar esta página.', 'warning')
        return redirect(url_for('login'))

    current_user_obj = Usuario.query.get(session['user_id'])
    
    institutions = Usuario.query.filter(
        (Usuario.tipo_perfil == 'ONG') | (Usuario.tipo_perfil == 'Associação')
    ).all()

    available_products = Produto.query.filter_by(id_usuario=current_user_obj.id_usuario, status='Disponível').all()

    if request.method == 'POST':
        id_produto = request.form['product_id']
        id_instituicao = request.form['institution_id']
        descricao_necessidade = request.form.get('necessity_description')

        product_to_donate = Produto.query.get(id_produto)
        institution_target = Usuario.query.get(id_instituicao)

        if not product_to_donate or product_to_donate.id_usuario != session['user_id'] or product_to_donate.status != 'Disponível':
            flash('Produto inválido ou você não tem permissão para doar este item ou ele não está disponível.', 'danger')
            return redirect(url_for('directed_donation'))
        
        if not institution_target or (institution_target.tipo_perfil != 'ONG' and institution_target.tipo_perfil != 'Associação'):
            flash('Instituição selecionada inválida.', 'danger')
            return redirect(url_for('directed_donation'))

        new_directed_donation = DoacaoDirecionada(
            id_produto=id_produto,
            id_instituicao=id_instituicao,
            descricao_necessidade=descricao_necessidade,
            status='Pendente'
        )
        db.session.add(new_directed_donation)
        
        notification_message_institution = f'Uma doação direcionada para você: o usuário "{current_user_obj.nome}" ofereceu "{product_to_donate.nome}".'
        notification_url_institution = url_for('product_detail', product_id=product_to_donate.id_produto)
        new_notification_institution = Notificacao(
            id_usuario_notificado=institution_target.id_usuario,
            id_remetente=session['user_id'],
            tipo_notificacao='doacao_direcionada',
            mensagem=notification_message_institution,
            url_redirecionamento=notification_url_institution,
            lida=False
        )
        db.session.add(new_notification_institution)

        db.session.commit()
        flash(f'Doação de "{product_to_donate.nome}" direcionada para {institution_target.nome} com sucesso!', 'success')
        return redirect(url_for('directed_donation'))

    doacoes_como_doador = DoacaoDirecionada.query.join(Produto).filter(Produto.id_usuario == current_user_obj.id_usuario).all()
    doacoes_como_instituicao = []
    if current_user_obj.tipo_perfil == 'ONG' or current_user_obj.tipo_perfil == 'Associação':
        doacoes_como_instituicao = DoacaoDirecionada.query.filter_by(id_instituicao=current_user_obj.id_usuario).all()

    return render_template('product/directed_donation.html',
                           institutions=institutions,
                           available_products=available_products,
                           doacoes_como_doador=doacoes_como_doador,
                           doacoes_como_instituicao=doacoes_como_instituicao)


@app.route('/notifications_page')
def notifications_page():
    if not session.get('user_id'):
        flash('Você precisa estar logado para ver suas notificações.', 'warning')
        return redirect(url_for('login'))
    
    user_notifications = Notificacao.query.filter_by(id_usuario_notificado=session['user_id']).order_by(Notificacao.data_criacao.desc()).all()
    
    return render_template('user/all_notifications.html', notifications=user_notifications)


@app.route('/notifications/mark_read/<int:notification_id>', methods=['POST'])
def mark_notification_read(notification_id):
    if not session.get('user_id'):
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401
    
    notification = Notificacao.query.get(notification_id)
    
    if notification and notification.id_usuario_notificado == session['user_id']:
        notification.lida = True
        db.session.commit()
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'message': 'Notificação não encontrada ou não pertence ao usuário'}), 404


@app.route('/admin/users')
def admin_users():
    if not session.get('user_id'):
        flash('Você precisa estar logado para acessar esta página.', 'warning')
        return redirect(url_for('login'))
    
    current_user_obj = Usuario.query.get(session['user_id'])
    if not current_user_obj or current_user_obj.tipo_perfil != 'Admin':
        flash('Acesso não autorizado. Apenas administradores podem acessar esta página.', 'danger')
        return redirect(url_for('index'))

    users = Usuario.query.all()
    return render_template('admin/admin_users.html', users=users)

@app.route('/admin/users/<int:user_id>/toggle_status', methods=['POST'])
def admin_toggle_user_status(user_id):
    if not session.get('user_id'):
        flash('Você precisa estar logado para realizar esta ação.', 'warning')
        return redirect(url_for('login'))
    current_user_obj = Usuario.query.get(session['user_id'])
    if not current_user_obj or current_user_obj.tipo_perfil != 'Admin':
        flash('Acesso não autorizado. Apenas administradores podem realizar esta ação.', 'danger')
        return redirect(url_for('index'))

    user_to_toggle = Usuario.query.get(user_id)
    if user_to_toggle:
        user_to_toggle.ativo = not user_to_toggle.ativo
        db.session.commit()
        flash(f'Status do usuário {user_to_toggle.nome} alterado para {"Ativo" if user_to_toggle.ativo else "Inativo"}.', 'info')
    else:
        flash('Usuário não encontrado.', 'danger')
    return redirect(url_for('admin_users'))


@app.route('/admin/products')
def admin_products():
    if not session.get('user_id'):
        flash('Você precisa estar logado para acessar esta página.', 'warning')
        return redirect(url_for('login'))
    current_user_obj = Usuario.query.get(session['user_id'])
    if not current_user_obj or current_user_obj.tipo_perfil != 'Admin':
        flash('Acesso não autorizado. Apenas administradores podem acessar esta página.', 'danger')
        return redirect(url_for('index'))

    products = Produto.query.all()
    return render_template('admin/admin_products.html', products=products)

@app.route('/admin/products/<int:product_id>/moderate', methods=['POST'])
def admin_moderate_product(product_id):
    if not session.get('user_id'):
        flash('Você precisa estar logado para realizar esta ação.', 'warning')
        return redirect(url_for('login'))
    current_user_obj = Usuario.query.get(session['user_id'])
    if not current_user_obj or current_user_obj.tipo_perfil != 'Admin':
        flash('Acesso não autorizado. Apenas administradores podem realizar esta ação.', 'danger')
        return redirect(url_for('index'))

    product = Produto.query.get(product_id)
    if not product:
        flash('Produto não encontrado.', 'danger')
        return redirect(url_for('admin_products'))

    action = request.form.get('action')
    try:
        if action == 'approve':
            product.status = 'Disponível'
            owner_user = Usuario.query.get(product.id_usuario)
            notification_message = f'Seu produto "{product.nome}" foi aprovado e agora está disponível para doação/troca!'
            notification_url = url_for('product_detail', product_id=product.id_produto)
            new_notification = Notificacao(
                id_usuario_notificado=owner_user.id_usuario,
                id_remetente=session['user_id'],
                tipo_notificacao='produto_aprovado',
                mensagem=notification_message,
                url_redirecionamento=notification_url,
                lida=False
            )
            db.session.add(new_notification)
            flash(f'Produto "{product.nome}" aprovado.', 'success')

        elif action == 'reject':
            product.status = 'Reprovado'
            owner_user = Usuario.query.get(product.id_usuario)
            notification_message = f'Seu produto "{product.nome}" foi reprovado. Verifique os detalhes e tente novamente.'
            notification_url = url_for('profile')
            new_notification = Notificacao(
                id_usuario_notificado=owner_user.id_usuario,
                id_remetente=session['user_id'],
                tipo_notificacao='produto_reprovado',
                mensagem=notification_message,
                url_redirecionamento=notification_url,
                lida=False
            )
            db.session.add(new_notification)
            flash(f'Produto "{product.nome}" reprovado.', 'warning')

        elif action == 'remove':
            for foto in product.fotos:
                try:
                    relative_path = foto.url_foto.split(url_for('static', filename=''))[1]
                    full_path = os.path.join(app.root_path, 'static', relative_path)
                    if os.path.exists(full_path):
                        os.remove(full_path)
                except Exception as e:
                    print(f"Erro ao deletar arquivo de imagem {foto.url_foto}: {e}")
            db.session.delete(product)
            owner_user = Usuario.query.get(product.id_usuario)
            notification_message = f'Seu produto "{product.nome}" foi removido da plataforma.'
            notification_url = url_for('profile')
            new_notification = Notificacao(
                id_usuario_notificado=owner_user.id_usuario,
                id_remetente=session['user_id'],
                tipo_notificacao='produto_removido',
                mensagem=notification_message,
                url_redirecionamento=notification_url,
                lida=False
            )
            db.session.add(new_notification)
            flash(f'Produto "{product.nome}" removido.', 'danger')
        
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash(f'Ocorreu um erro ao moderar o produto: {str(e)}', 'danger')
    
    return redirect(url_for('admin_products'))


# --- Comandos CLI para gerenciar o banco de dados ---
@app.cli.command('create-db')
def create_db_command():
    with app.app_context():
        db.create_all()
        print("Banco de dados e tabelas criadas!")

@app.cli.command('seed-db')
def seed_db_command():
    with app.app_context():
        admin_user_exists = Usuario.query.filter_by(email='admin@example.com').first()
        if not admin_user_exists:
            hashed_password = generate_password_hash('admin123')
            admin_user = Usuario(
                nome='Admin Teste',
                email='admin@example.com',
                senha=hashed_password,
                telefone='(63)99999-0000',
                localizacao='Capital',
                tipo_perfil='Admin',
                ativo=True
            )
            db.session.add(admin_user)
            db.session.commit()
            print("Usuário Admin 'admin@example.com' criado com senha 'admin123'.")
        
        user_test_exists = Usuario.query.filter_by(email='user@example.com').first()
        if not user_test_exists:
            hashed_password = generate_password_hash('user1234')
            user_test = Usuario(
                nome='Usuário Comum',
                email='user@example.com',
                senha=hashed_password,
                telefone='(63)98888-7777',
                localizacao='Palmas',
                tipo_perfil='Morador',
                ativo=True
            )
            db.session.add(user_test)
            db.session.commit()
            print("Usuário 'user@example.com' criado com senha 'user1234'.")

        ong_user_exists = Usuario.query.filter_by(email='ong@example.com').first()
        if not ong_user_exists:
            hashed_password = generate_password_hash('ong12345')
            ong_user = Usuario(
                nome='ONG Amiga',
                email='ong@example.com',
                senha=hashed_password,
                telefone='(63)97777-6666',
                localizacao='Porto Nacional',
                tipo_perfil='ONG',
                ativo=True
            )
            db.session.add(ong_user)
            db.session.commit()
            print("Usuário ONG 'ong@example.com' criado com senha 'ong12345'.")

        if not Produto.query.first():
            user1 = Usuario.query.filter_by(email='user@example.com').first()
            ong1 = Usuario.query.filter_by(email='ong@example.com').first()

            if user1 and ong1:
                products_data = [
                    {'user': user1, 'name': 'Bicicleta Infantil', 'desc': 'Bicicleta para crianças de 5 a 8 anos, bom estado.', 'cat': 'Brinquedos', 'cond': 'Usado - Boa', 'status': 'Disponível'},
                    {'user': ong1, 'name': 'Sofá 3 Lugares', 'desc': 'Sofá confortável, tecido um pouco desgastado, ideal para reforma.', 'cat': 'Móveis', 'cond': 'Usado - Razoável', 'status': 'Disponível'},
                    {'user': user1, 'name': 'Máquina de Costura', 'desc': 'Máquina antiga, funcionando. Ótima para iniciantes.', 'cat': 'Outros', 'cond': 'Usado - Boa', 'status': 'Aguardando Moderação'}
                ]
                
                for p_data in products_data:
                    new_prod = Produto(
                        id_usuario=p_data['user'].id_usuario,
                        nome=p_data['name'],
                        descricao=p_data['desc'],
                        categoria=p_data['cat'],
                        condicao=p_data['cond'],
                        status=p_data['status']
                    )
                    db.session.add(new_prod)
                    db.session.flush()
                    
                    dummy_filename = secure_filename(f"{p_data['name'].lower().replace(' ', '_')}_{random.randint(1000,9999)}.jpg")
                    unique_dummy_filename = generate_unique_filename(dummy_filename)
                    dummy_image_url = url_for('static', filename=f'uploads/{unique_dummy_filename}')
                    
                    try:
                        if not os.path.exists(app.config['UPLOAD_FOLDER']):
                            os.makedirs(app.config['UPLOAD_FOLDER'])
                        with open(os.path.join(app.config['UPLOAD_FOLDER'], unique_dummy_filename), 'wb') as f:
                            f.write(b'GIF89a\x01\x00\x01\x00\x00\x00\x00!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;')
                    except Exception as e:
                        print(f"Não foi possível criar imagem dummy para {unique_dummy_filename}: {e}")

                    db.session.add(FotoProduto(id_produto=new_prod.id_produto, url_foto=dummy_image_url))

                db.session.commit()
                print("Produtos de teste adicionados.")
            else:
                print("Usuários de teste não encontrados para adicionar produtos.")

        print("Banco de dados populado com dados iniciais.")

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)