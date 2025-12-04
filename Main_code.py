import flet as ft
from datetime import datetime
from firebase_config import db
from firebase_admin import credentials, firestore
import asyncio

def All(page:ft.Page):
    def loading():
        return ft.View(route="/loading",controls=[ft.Container(expand=True, alignment=ft.alignment.center,
        content=ft.Column([ft.Text("Not Max", size=40), ft.Text("Загрузка чатов...", size = 20)],
        alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20))])

    def check():
        page.client_storage.set("STheme", True)
        chk = page.client_storage.get("chk_lgn")
        usname = page.client_storage.get("usname")
        page.views.clear()
        if chk == None:
            page.views.append(LogReg())
        else:
            page.views.append(Main(usname))
            Main(usname)
        page.update()

    def LogReg():
        page.title = "Вход/Регистрация"
        page.views.clear()
        
        title = ft.Text("Войти", size=30, weight="bold")
        login = ft.TextField(label="Логин")
        pswd = ft.TextField(label="Пароль", password=True)
        dop_txt = ft.Text("", size = 15)
        
        def login_db(e):
            dop_db = db.collection(login.value).document("info").get()
            if login.value == "" or pswd.value == "":
                dop_txt.color = "red"
                dop_txt.value = "Поля не могут быть пустыми!"
                
            elif not dop_db.exists:
                dop_txt.color = "red"
                dop_txt.value = "Пользователь не существует."
                page.update()
            elif dop_db.to_dict()["password"] != pswd.value:
                dop_txt.color = "red"
                dop_txt.value = "Неверный логин или пароль."
            elif dop_db.to_dict()["password"] == pswd.value:
                page.client_storage.set("usname", login.value)
                page.client_storage.set("chk_lgn", True)
                dop_txt.color = "green"
                dop_txt.value = "Успешный вход! Приложение сейчас запуститься..."
                page.update()
                usname = login.value
                page.views.append(Main(usname))
                page.client_storage.set("chk_lgn", True)
            else:
                dop_txt.color = "red"
                dop_txt.value = "Неизвесная ошибка! Попробуйте повторить позднее"
            page.update()

        LogBut = ft.ElevatedButton("Войти", width=300, on_click = login_db)
        Pcl = ft.TextButton("Нет аккаунта? Зарегистрироваться.", on_click=lambda e:opn_vw(e))
        lgn_view = ft.View(route="/", controls=
            [ft.Row([ft.Column([title, login, pswd, LogBut, Pcl, dop_txt],
                horizontal_alignment="center", spacing = 20)], alignment = "center")])
        
        def opn_vw(e):
            page.views.append(regs_view())
            page.update()
        
        def rst_lgn(e):
            page.views.pop()
            page.update()

        def regs_view():
            reg_title = ft.Text("Зарегистрироваться", size = 30, weight = "bold")
            reg_login = ft.TextField(label = "Логин")
            reg_pswd1 = ft.TextField(label = "Пароль", password = True)
            reg_pswd2 = ft.TextField(label = "Подтвердите пароль", password = True)
            RegBut = ft.ElevatedButton("Зарегистрироваться", width = 300, on_click=lambda e: auth_db())
            bck_lgn = ft.TextButton("Уже есть аккаунт? Войти.", on_click = rst_lgn)
            dop = ft.Text("", size = 15)

            def auth_db():
                dop_db = db.collection(reg_login.value).document("info").get()
                if  reg_login.value == "" or reg_pswd1.value == "":
                    dop.color = "red"
                    dop.value = "Поля не могут быть пустыми!"
                    page.update()
                elif reg_pswd1.value != reg_pswd2.value:
                    dop.color = "red"
                    dop.value = "Пароли не совпадают."
                    page.update()
                elif dop_db.exists:
                    dop.color = "red"
                    dop.value = "Имя пользователя занято."
                    page.update()
                else:
                    usname = reg_login.value
                    page.client_storage.set("usname", reg_login.value)
                    dop.color = "green"
                    dop.value = "Успешная регистрация! Приложение сейчас запуститься..."
                    page.update()
                    db.collection(reg_login.value).document("info").set({"password":reg_pswd2.value})
                    page.views.append(Main(usname))
                    chk = True
                    Main(usname)
                    
            return ft.View(route = "/reg",controls = [ft.Row([ft.Column([reg_title,
                    reg_login, reg_pswd1, reg_pswd2, RegBut, bck_lgn, dop],horizontal_alignment = "center", spacing = 15)], alignment = "center")])
  
        page.views.append(lgn_view)
        page.update()
        return lgn_view
    
    def Main(usname):
        page.title = "NotMax"
        us_nlc = None

        sct_chat = ft.Ref()
        msg_chat = ft.Ref[ft.Column]()
        msg_ipt = ft.Ref[ft.TextField]()
        cntct = ft.Ref[ft.Column]()

        def settings():
            back_btn = ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=lambda e: page.views.pop() and page.update())
            set_txt = ft.Text(usname, size = 40)
            log_txt = ft.TextButton("Выйти из аккаунта", on_click=lambda e: logout())
            dvr = ft.VerticalDivider(width=1, color="White")
            return ft.View("/settings", controls = [ft.Column([back_btn, set_txt, log_txt, dvr])])
        def opn_settings():
            page.views.append(settings())
            page.update()
        def logout():
            page.client_storage.clear()
            page.views.append(LogReg())
            page.update()
        
        def search():
            schB_btn = ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=lambda e: page.views.pop() and page.update())
            sch_txt = ft.Text("Найти пользователя", size = 25)
            sch_ipt = ft.TextField(hint_text="Юзернейм пользователя", expand=True)
            sch_btn = ft.IconButton(icon=ft.Icons.SEARCH, on_click=lambda e: sch())
            err_txt = ft.Text("", color="red")
            def sch():
                ipt = sch_ipt.value.strip()
                if not ipt:
                    err_txt.value = "Поле не может быть пустым!"
                    page.update()
                    return
                WhyNot = False
                for ij in db.collections():
                    if ipt == ij.id:
                        WhyNot = True
                        break
                if ipt == usname:
                    err_txt.value = "Это ваше имя пользователя!"
                    page.update()
                    return
                if not WhyNot:
                    err_txt.value = "Пользователя не существует!"
                    page.update()
                    return
                user_slct_chat(ipt, None)
                page.views.pop()
                page.update()
            
            return ft.View("/search", controls=[ft.Column([ft.Row([schB_btn, sch_txt]), ft.Row([sch_ipt, sch_btn]), err_txt])])
        def opn_srch():
            page.views.append(search())
            page.update()
            
        ignore = ["info"]
        def load_cht(e):
            cntct.current.controls.clear()
            dop = db.collection(usname).stream()
            for i in dop:
                if i.id in ignore:
                    continue
                dop2 = db.collection(usname).document(i.id).get()
                if dop2.exists:
                    dop3 = dop2.to_dict()
                    if dop3:
                        last_key = sorted(dop3.keys(), key=float)[-1]
                        last_msg = dop3[last_key]
                    else:
                        last_msg = ""
                else:
                    last_msg = ""
                cntct.current.controls.append(ft.ListTile(ft.Text(i.id),subtitle=ft.Text(last_msg), on_click=lambda e, us = i.id:user_slct_chat(us, last_msg)))
            page.update()



        def user_slct_chat(us, lst_msg):
            nonlocal us_nlc
            us_nlc = us
            right_column.visible = True
            right_column.update()
            sct_chat.current.controls.clear()
            sct_chat.current.controls.append(ft.Text(value=us, size=20, weight=ft.FontWeight.BOLD))
            page.update()
            msg_chat.current.controls.clear()

            Upd = db.collection(usname).document(us)
            def on_snapshot(doc_snapshot, changes, read_time):
                msg_chat.current.controls.clear()
                for i in doc_snapshot:
                    if i.exists:
                        data = i.to_dict()
                        if data:
                            for key in sorted(data.keys(), key=float):
                                msg_chat.current.controls.append(ft.Text(value=data[key], size = 15))
                msg_chat.current.update()
            Upd.on_snapshot(on_snapshot)
    

        
        async def send_msg(e):
            if msg_ipt.current.value.strip() == "":
                text = ft.Text("Сообщение пустое!", size=20)
                omgtext = ft.Row([text], alignment=ft.MainAxisAlignment.CENTER)
                page.add(omgtext)
                page.update()
                await asyncio.sleep(1)
                page.controls.remove(omgtext)
                page.update()
                return
            msg_text = msg_ipt.current.value
            key = str(datetime.now().timestamp())
            db.collection(us_nlc).document(usname).set({key: f"{usname}: {msg_text}"}, merge=True)
            db.collection(usname).document(us_nlc).set({key: f"{usname}: {msg_text}"}, merge=True)
            msg_ipt.current.value = ""
            msg_chat.current.controls.append(ft.Text(f"{usname}: {msg_text}"))
            page.update()
            

        left_column = ft.Container(content=ft.Column([ft.Row([
                ft.IconButton(icon=ft.Icons.MENU, on_click=lambda e: opn_settings()),
                ft.Text("Not Max", size = 20),
                ft.IconButton(icon=ft.Icons.SEARCH, on_click=lambda e: opn_srch())], spacing=5, alignment="spaceBetween"),
                ft.Column(ref=cntct, scroll=ft.ScrollMode.AUTO, expand=True)], spacing=5),width=300,
                border=ft.border.only(right=ft.border.BorderSide(1, ft.Colors.OUTLINE)))


        right_column = ft.Container(visible=False, content = ft.Column([
                ft.Container(content = ft.Column(ref=sct_chat), padding=10, border=ft.border.only(bottom=ft.border.BorderSide(1, ft.Colors.OUTLINE))),
                ft.Container(content = ft.ListView(ref=msg_chat, auto_scroll=True, spacing=10, expand=True), padding=10, expand=True),
                ft.Row([ft.TextField(ref = msg_ipt, expand = True, hint_text="Сообщение"),
                ft.IconButton(icon = ft.Icons.SEND, on_click=send_msg)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)]),expand=True)

        Main_view = ft.View(route="/main", controls=[ft.Row([left_column, right_column], expand=True)])

        load_cht(None)
        return Main_view  
    page.views.append(loading())
    page.update()
    check()
ft.app(target=All)
