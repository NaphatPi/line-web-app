import secrets, shutil, zipfile
from pdf2image import convert_from_path
from urllib.parse import urlencode, quote_plus
import os
from web_app import db, app, dbx
from web_app.models import Document, Admin
from web_app.chatbot import set_rich_menu, unlink_rich_menu, push_text_msg

from flask import session, current_app
from flask_login import current_user
from datetime import datetime

from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import resolve1

dbx_path = app.config.get('DROP_BOX_PATH')

users_to_update = []

btn_map = {
    "requested":"btn-warning",
    "member": "btn-success",
    "blocked": "btn-danger",
}

action_allowed = {
    "requested":['approve', 'reject', 'block'],
    "member":["block"],
    "blocked":["unblock", "delete"],
    "rejected":["delete"]
}


def update_session():
    if session.get('userId') in users_to_update:
        users_to_update.pop(users_to_update.index(session.get('userId')))
        session.clear()


def change_user_status(user, action):
    if action in action_allowed[user.status]:
        if action == 'delete' or action == 'reject':
            db.session.delete(user)
        elif action == 'unblock':
            last_status = user.log.split('|')[-2].split('#')[-1]
            user.status = last_status
            log(user, user.status)
        else:
            user.status = 'member' if action == 'approve' else 'blocked'
            log(user, user.status)
        if user.status == 'member':
            try:
                print('setting rm')
                set_rich_menu(user.userId, app.config['MAIN_RICH_MENU'])
            except:
                return (False, f"Cannot set richmenu for: {user.name} {user.surname}")
            if action == 'approve':
                try:
                    push_text_msg(user.userId, 'บัญชีของท่านได้รับการอนุมัติแล้ว!')
                except:
                    return (False, f"Cannot send approval notification to: {user.name} {user.surname}")
        elif user.status == 'blocked':
            unlink_rich_menu(user.userId)
        try:
            db.session.commit()
        except:
            return (False, "Data base error: cannot perform the action")
        users_to_update.append(user.userId)
        return (True, f'Succesfully {action} - {user.name} {user.surname}')
    else:
        return (False, f'Method {action} not allowed for this user - {user.name} {user.surname}')


def log(user, status):
    user.log += f"|{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}#{status}"


def save_pdf(form_pdf):
    pdf = form_pdf.docFile.data
    random_hex = secrets.token_urlsafe(16)
    path = os.path.join(current_app.root_path, 'static', 'docs', random_hex)
    pic_path = os.path.join(path, 'pic')
    try:
        os.makedirs(pic_path)
    except:
        return (False, "Failed to create directory. Please try again")
    file_name = "source_pdf.pdf"
    file_path = os.path.join(path, file_name)
    try: #save pdf file to local storage
        pdf.save(file_path)
        size = os.path.getsize(file_path) / (1024*1024)
        if size > 10:
            shutil.rmtree(path)
            return (False, f"Failed to save pdf file: PDF size exceeds max_file_size: 10  got: {size:.2f}")
    except:
        shutil.rmtree(path)
        return (False, "Failed to save pdf file")
    try:
        numPage = count_pdf_pages(file_path)
        if numPage > 30:
            shutil.rmtree(path)
            return (False, f"Failed to upload file: PDF exceeds num_page_limit: 30  got: {numPage}")
    except:
        shutil.rmtree(path)
        return (False, "Failed to upload file: PDF file invalid")
    try: #convert pdf file to images and save to local storage
        pdf_to_image(path, file_name)
    except:
        shutil.rmtree(path)
        return (False, "Failed to convert pdf file")
    try: #save entire folder to dropbox
        local_path = os.path.join(current_app.root_path, 'static', 'docs')
        send_to_dropbox(local_path, random_hex, dbx_path)
    except:
        delete_dropbox_folder(dbx_path, random_hex)
        return (False, "Failed to save files to dropbox")
    try:
        save_document_to_database(form_pdf, random_hex)
    except:
        delete_dropbox_folder(dbx_path, random_hex)
        return (False, "Failed to save to database")
    return (True, "")



def send_to_dropbox(local_path, target_folder, dbx_folder):
    for folderName, _, filenames in os.walk(os.path.join(local_path, target_folder)):
        db_target_path =  dbx_folder + folderName[-(len(folderName)-len(local_path)):].replace('\\', '/')
        for filename in filenames:
            print(f"Sending file to: {db_target_path + '/' + filename}")
            with open(os.path.join(folderName, filename), mode='rb') as f:
                dbx.files_upload(f.read(), db_target_path + '/' + filename)
    print('File send succesful!!!')



def delete_dropbox_folder(drop_box_path, target_folder):
    for entry in dbx.files_list_folder(drop_box_path).entries:
        if entry.name == target_folder:
            print('Deleting ' + entry.name)
            dbx.files_delete(entry.path_display)
            print('File delete successful')


def download_dropbox_folder(dbx_folder, target_file, local_path):
    print('---- Download from dbx ----')
    local_file = os.path.join(local_path, target_file + ".zip")
    print('Local file target to save: ' + local_file)
    try:
        print('Download from path: ' + dbx_folder + '/' + target_file)
        dbx.files_download_zip_to_file(local_file, dbx_folder + '/' + target_file)
    except Exception as e:
        print(e)
        return (False, "Cannot download files from dbx: " + str(target_file), 503)
    try:
        zf = zipfile.ZipFile(local_file)
        zf.extractall(local_path)
        zf.close()
    except:
        return (False, "Failed to extract files", 503)
    try:
        os.unlink(local_file)
    except:
        pass
    return (True, "")

    

def pdf_to_image(pdf_path, file_name):
    images = convert_from_path(os.path.join(pdf_path, file_name))
    out_path = os.path.join(pdf_path, "pic")
    for i in range(len(images)):
        fn = str(i) +'.jpg'
        images[i].save(os.path.join(out_path, fn), 'JPEG')


def save_document_to_database(form, hex):
    doc = Document(
            title = form.title.data.strip(),
            description = form.description.data.strip(),
            hex = hex,
            link= "line://app/" + app.config['LIFF_ID'] + "?" + urlencode({"liff.state":"/docs/" + hex}, quote_via=quote_plus),
            uploadBy = current_user.username.upper(),
            uploadDate = datetime.now(),
            tag = form.tag.data.strip()
        )
    db.session.add(doc)
    db.session.commit()


def delete_doc(hex):
    path = os.path.join(current_app.root_path, 'static', 'docs', hex)
    doc = Document.query.filter_by(hex=hex).first()
    if doc is not None:
        if os.path.isdir(path):
            try:
                shutil.rmtree(path)
            except:
                pass
        delete_dropbox_folder(dbx_path, hex)
        try:
            db.session.delete(doc)
            db.session.commit()
        except:
            return (False, "Failed to delete file from database")
        return (True, "")
    else:
        return (False, "Failed to delete file: File not found in database")


def preview_doc(hex):
    doc = Document.query.filter_by(hex=hex).first()
    if not doc:
        return (False, "Failed to preview document: File not found on server", 404)
    path = os.path.join(current_app.root_path, 'static', 'docs', hex)
    if not os.path.isdir(path): #  Check local files exist
        print('Current app root path:' + current_app.root_path)
        res = download_dropbox_folder(dbx_path, hex, os.path.join(current_app.root_path, 'static', 'docs'))
        if not res[0]:
            return res
    numPage = count_file(os.path.join(path,'pic'))
    return (True, numPage, doc.title)


def count_pdf_pages(pdf_path):
    with open(pdf_path, 'rb') as f:
        parser = PDFParser(f)
        document = PDFDocument(parser)
        return resolve1(document.catalog['Pages'])['Count']
        


def count_file(path):
    totalFiles = 0
    for base, dirs, files in os.walk(path):
        for file in files:
            totalFiles += 1
    return totalFiles
    

def create_admin():
    # Add new admins
    for i in range(1,5):
        admin = Admin(
            id = i,
            username = 'tseoa00' + str(i),
            password = '',  # Admin password here
            role=4
        )
        db.session.add(admin)
        print(admin)
    db.session.commit()
    print('Admin added!')