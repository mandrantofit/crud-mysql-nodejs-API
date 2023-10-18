# Importez les modules Flask requis
from flask import Flask, render_template, request, redirect, url_for, session, flash , jsonify
import MySQLdb
from datetime import datetime
import bcrypt
import smtplib
from email.mime.text import MIMEText

#xozc uknk potb robo 
app = Flask(__name__)
app.secret_key = 'Bel0uh2004'  # Assurez-vous de définir votre propre clé secrète
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False

app.config['EMAIL_SERVER'] = 'smtp.gmail.com'  # Remplacez par l'adresse de votre serveur SMTP
app.config['EMAIL_PORT'] = 587  # Port SMTP (587 est couramment utilisé pour TLS)
app.config['EMAIL_USERNAME'] = 'mandrantofit@gmail.com'
app.config['EMAIL_PASSWORD'] = 'xozc uknk potb robo'


# Configuration de la base de données MySQL
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'db': 'databaseeam'
}

def connect_db():
    return MySQLdb.connect(**db_config)

@app.route('/')
def main():
    return render_template('home.html')

@app.route('/deconnection')
def deconnection():
    session['myvarsession'] = False
    return redirect(url_for('main'))

@app.route('/connection', methods=['POST'])
def connection():
    if request.method == 'POST':
        #username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Vérifiez que les paramètres sont présents
        if  email is None or password is None:
            flash('Tous les champs sont obligatoires', 'danger')
            return redirect(url_for('connection'))

        # Vérifiez que l'utilisateur existe dans la base de données
        db = connect_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM `loginadmin` WHERE  emailR = %s', (email,))
        utilisateur = cursor.fetchone()
        cursor.close()
        db.close()

        if utilisateur:
            # Vérifiez le mot de passe
            password_hash = utilisateur[2]
            if bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')):
                session['myvarsession'] = True
                return redirect(url_for('liste_jeunes'))
            else:
                flash('Mot de passe incorrect', 'danger')
                return redirect(url_for('main'))
        else:
            flash('Nom d\'utilisateur ou adresse e-mail introuvable', 'danger')
            return redirect(url_for('main'))
    return redirect(url_for('connection'))

@app.route('/jeune', methods=['GET'])
def liste_jeunes():
    if session.get('myvarsession') is None or not session['myvarsession'] or session['myvarsession'] == False:
        flash('Connectez-vous d\'abord pour accéder à cette page.', 'danger')
        return redirect(url_for('main'))
    else:
        try:
            db = connect_db()
            cursor = db.cursor()
            cursor.execute('SELECT idJ, nomJ, prenomJ, regionJ , themeJ , telephone1J  FROM jeune') 
            jeunes = cursor.fetchall()

            # Récupérez également la liste des formations
            cursor.execute('SELECT DISTINCT themeJ FROM jeune')
            formations = [formation[0] for formation in cursor.fetchall()]
            
            cursor.close()
            db.close()

            return render_template('./admin/vueJeune.html', jeunes=jeunes, formations=formations), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
  

@app.route('/vue_jeune_detail/<int:jeune_id>', methods=['GET'])
def vue_jeune_detail(jeune_id):
    if session.get('myvarsession') is None or not session['myvarsession'] or session['myvarsession'] == False:
        flash('Connectez-vous d\'abord pour accéder à cette page.', 'danger')
        return redirect(url_for('main'))

    try:
        db = connect_db()
        cursor = db.cursor()
        cursor.execute('SELECT idJ , nomJ, prenomJ, emailJ, datenaissanceJ, regionJ, districtJ, sexeJ, secteurJ, domaineJ, themeJ, activiteJ, lieuxJ, diplomeJ, telephone1J, telephone2J , typeFormation , adresseJ FROM jeune WHERE idJ = %s', (jeune_id,))
        jeune = cursor.fetchone()
        cursor.close()
        db.close()

        if jeune:
            # L'objet "jeune" contient toutes les attributs du jeune
            return render_template('./admin/vueJeunedetail.html', jeunes=jeune), 200
        else:
            flash('Jeune non trouvé', 'danger')
            return redirect(url_for('liste_jeunes'))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


        
@app.route('/update_jeune/<int:jeune_id>', methods=['GET', 'POST'])
def update_jeune(jeune_id):
    if session.get('myvarsession') is None or not session['myvarsession']:
        flash('Connectez-vous d\'abord pour accéder à cette page.', 'danger')
        return redirect(url_for('main'))

    if request.method == 'POST':
        # Récupérez les données du formulaire de mise à jour
        nom = request.form['nom']
        prenom = request.form['prenom']
        email = request.form['email']
        password = request.form['password']
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        region = request.form['region']
        district = request.form['district']
        adresse= request.form['adresse']
        
        date_str = request.form['datetime']
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            formatted_datetime = date_obj.strftime('%Y-%m-%d')
        except ValueError:
            flash('Format de date invalide. Utilisez le format YYYY-MM-DD.', 'danger')
            return redirect(url_for('update_jeune', jeune_id=jeune_id))

        sexe = request.form['sexe']
        secteur = request.form['secteur']
        domaine = request.form['domaine']
        theme = request.form['theme']
        activite = request.form['activite']
        lieux = request.form['lieux']
        diplome = request.form['diplome']
        telephone = request.form['telephone']
        telephone2 = request.form['telephone2']
        typeFormation = request.form['typeFormation']

        # Mettez à jour les données du jeune dans la base de données en fonction de l'ID
        db = connect_db()
        cursor = db.cursor()
        cursor.execute('UPDATE jeune SET nomJ = %s, prenomJ = %s, emailJ = %s, mdpJ = %s, datenaissanceJ = %s, regionJ = %s, districtJ = %s, adresseJ = %s, sexeJ = %s, secteurJ = %s, domaineJ = %s, themeJ = %s, activiteJ = %s, lieuxJ = %s, diplomeJ = %s, telephone1J = %s, telephone2J = %s, typeFormation = %s WHERE idJ = %s',
               (nom, prenom, email, hashed_password, formatted_datetime, region, district, adresse, sexe, secteur, domaine, theme, activite, lieux, diplome, telephone, telephone2, typeFormation, jeune_id))

        db.commit()
        cursor.close()
        db.close()

        flash('Le jeune a été mis à jour avec succès.', 'success')
        return redirect(url_for('liste_jeunes'))

    else:
        # Récupérez les informations du jeune à partir de la base de données en fonction de l'ID
        db = connect_db()
        cursor = db.cursor()
        cursor.execute('SELECT idJ, nomJ, prenomJ, emailJ, datenaissanceJ, regionJ, districtJ, adresseJ, sexeJ, secteurJ, domaineJ, themeJ, activiteJ, lieuxJ, diplomeJ, telephone1J, telephone2J, typeFormation FROM jeune WHERE idJ = %s', (jeune_id,))
        jeune = cursor.fetchone()
        cursor.close()
        db.close()

        if jeune:
            return render_template('./admin/updateJeune.html', jeune=jeune), 200
        else:
            flash('Jeune non trouvé', 'danger')
            return redirect(url_for('liste_jeunes'))




@app.route('/delete_jeune/<int:jeune_id>', methods=['GET'])
def delete_jeune(jeune_id):
    if session.get('myvarsession') is None or not session['myvarsession']:
        flash('Connectez-vous d\'abord pour accéder à cette page.', 'danger')
        return redirect(url_for('main'))

    # Vérifiez d'abord si le jeune existe dans la base de données
    db = connect_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM jeune WHERE idJ = %s', (jeune_id,))
    jeune = cursor.fetchone()

    if not jeune:
        flash('Jeune non trouvé', 'danger')
        return redirect(url_for('liste_jeunes'))

    # Si le jeune existe, supprimez-le de la base de données
    cursor.execute('DELETE FROM jeune WHERE idJ = %s', (jeune_id,))
    db.commit()
    cursor.close()
    db.close()

    flash('Le jeune a été supprimé avec succès.', 'success')
    return redirect(url_for('liste_jeunes'))




@app.route('/inscription_jeune', methods=['GET', 'POST'])
def inscription_jeune():
    if session.get('myvarsession') is None or not session['myvarsession']:
        flash('Connectez-vous d\'abord pour accéder à cette page.', 'danger')
        return redirect(url_for('main'))

    if request.method == 'POST':
        # Récupérez les données du formulaire d'inscription
        nom = request.form['nom']
        prenom = request.form['prenom']
        email = request.form['email']
        password = request.form['password']
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        region = request.form['region']
        district = request.form['district']
        adresse= request.form['adresse']
        
        date_str = request.form['datetime']
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        formatted_datetime = date_obj.strftime('%Y-%m-%d')
        
        #datetime = request.form['datetime'] #encore a rectifier
        
        sexe = request.form['sexe']
        secteur = request.form['secteur']
        domaine = request.form['domaine']
        theme = request.form['theme']
        activite = request.form['activite']
        lieux = request.form['lieux']
        diplome = request.form['diplome']
        telephone = request.form['telephone']
        telephone2 = request.form['telephone2']
        typeFormation = request.form['typeFormation']
        
        # Vérifiez si l'adresse e-mail est déjà utilisée
        db = connect_db()
        cursor = db.cursor()
        cursor.execute('SELECT idJ FROM jeune WHERE emailJ = %s', (email,))
        existing_user = cursor.fetchone()
        cursor.close()
        
        if existing_user:
            flash('Cette adresse e-mail est déjà utilisée. Veuillez utiliser une autre adresse e-mail.', 'danger')
            return redirect(url_for('inscription_jeune'))
        
        # Insérez les données du jeune dans la base de données
        db = connect_db()
        cursor = db.cursor()
        cursor.execute('INSERT INTO jeune (nomJ, prenomJ, emailJ, datenaissanceJ,adresseJ, regionJ, districtJ, sexeJ, secteurJ, domaineJ, themeJ, activiteJ, lieuxJ, diplomeJ, telephone1J, telephone2J, mdpJ, typeFormation) VALUES (%s, %s , %s , %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
    (nom, prenom, email, formatted_datetime,adresse, region, district, sexe, secteur, domaine, theme, activite, lieux, diplome, telephone, telephone2, hashed_password, typeFormation))

        db.commit()
        cursor.close()
        db.close()
        
        def send_email(recipient, subject, message):
            from_email = app.config['EMAIL_USERNAME']
            to_email = recipient

            msg = MIMEText(message)
            msg['Subject'] = subject
            msg['From'] = from_email
            msg['To'] = to_email

            try:
                server = smtplib.SMTP(app.config['EMAIL_SERVER'], app.config['EMAIL_PORT'])
                server.starttls()
                server.login(app.config['EMAIL_USERNAME'], app.config['EMAIL_PASSWORD'])
                server.sendmail(from_email, to_email, msg.as_string())
                server.quit()
                return True
            except Exception as e:
                print(f"Erreur lors de l'envoi de l'e-mail : {str(e)}")
                return False    
         # Envoi de l'e-mail de confirmation
        recipient_email = email
        subject = 'Confirmation d\'inscription'
        message = 'Cher jeune, votre inscription s\'est déroulée avec succès. Bienvenue sur notre plateforme.'
        #send_email(recipient_email, subject, message)
        if send_email(recipient_email, subject, message):
            flash('Le jeune a été inscrit avec succès. Un e-mail de confirmation a été envoyé.', 'success')
        else:
            flash('Le jeune a été inscrit avec succès, mais l\'e-mail de confirmation n\'a pas pu être envoyé.', 'warning')

        return redirect(url_for('liste_jeunes'))
    else:
        return render_template('./admin/inscriptionJeune.html'), 200


@app.route('/liste_jeunes_recherche', methods=['GET'])
def liste_jeunes_recherche():
    search_term = request.args.get('search_term', '')

    if session.get('myvarsession') is None or not session['myvarsession'] or session['myvarsession'] == False:
        flash('Connectez-vous d\'abord pour accéder à cette page.', 'danger')
        return redirect(url_for('main'))
    else:
        try:
            db = connect_db()
            cursor = db.cursor()

            # Effectuez la recherche dans la base de données en fonction du terme de recherche
            if search_term:
                query = "SELECT idJ, nomJ, prenomJ, regionJ, themeJ, telephone1J FROM jeune WHERE nomJ LIKE %s OR prenomJ LIKE %s OR regionJ LIKE %s OR themeJ LIKE %s OR telephone1J LIKE %s "
                cursor.execute(query, (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%", f"%{search_term}%" , f"%{search_term}%"))
            else:
                cursor.execute('SELECT idJ, nomJ, prenomJ, regionJ , themeJ, telephone1J  FROM jeune')

            jeunes = cursor.fetchall()
            cursor.close()
            db.close()
            return render_template('./admin/vueJeune.html', jeunes=jeunes, search_term=search_term), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@app.route('/triage_jeunes_formation', methods=['POST'])
def triage_jeunes_formation():
    # Récupérez la formation sélectionnée depuis le formulaire
    formation = request.form.get('formation')

    if not formation:
        flash('Sélectionnez une formation pour effectuer le tri.', 'danger')
        return redirect(url_for('liste_jeunes'))

    # Écrivez le code pour trier les jeunes par formation en utilisant la variable "formation"
    db = connect_db()
    cursor = db.cursor()
    cursor.execute('SELECT idJ, nomJ, prenomJ, regionJ, themeJ, telephone1J FROM jeune WHERE formationJ = %s', (formation,))
    jeunes_triés = cursor.fetchall()
    cursor.close()
    db.close()

    # Affichez les résultats triés
    return render_template('votre_template.html', jeunes=jeunes_triés, formation=formation)




if __name__ == '__main__':
    app.run(host='192.168.88.167',port=5000, debug=True)
