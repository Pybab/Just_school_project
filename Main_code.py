import flet as ft
from datetime import datetime, time
from firebase_config import db
from firebase_admin import credentials, firestore
import asyncio


def All(page:ft.Page):
    page.client_storage.clear()
    def check():
        chk = page.client_storage.get("chk_lgn")
        usname = page.client_storage.get("usname")
        if chk == None:
            LogReg()
        else:
            Main(usname)

    def LogReg():
        page.clean()
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
                dop_txt.color = "green"
                dop_txt.value = "Успешный вход! Приложение сейчас запуститься..."
                page.update()
                usname = login.value
                page.views.append(Main(usname))
                page.update()
                page.client_storage.set("chk_lgn", True)
            else:
                dop_txt.color = "red"
                dop_txt.value = "Неизвесная ошибка! Попробуйте повторить позднее"

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
            reg_phone = ft.TextField(label = "Номер телефона")
            reg_pswd1 = ft.TextField(label = "Пароль", password = True)
            reg_pswd2 = ft.TextField(label = "Подтвердите пароль", password = True)
            RegBut = ft.ElevatedButton("Зарегистрироваться", width = 300, on_click=lambda e: auth_db())
            bck_lgn = ft.TextButton("Уже есть аккаунт? Войти.", on_click = rst_lgn)
            dop = ft.Text("", size = 15)

            def auth_db():
                dop_db = db.collection(reg_login.value).document("info").get()
                if  reg_login.value == "" or reg_phone.value == "" or reg_pswd1.value == "":
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
                    db.collection(reg_login.value).document("info").set({"password":reg_pswd2.value, "PN":reg_phone.value})
                    page.views.append(Main(usname))
                    chk = True
                    Main(usname)
                    

            return ft.View(route = "/reg",controls = [ft.Row([ft.Column([reg_title,
                    reg_login, reg_phone, reg_pswd1, reg_pswd2, RegBut, bck_lgn, dop],horizontal_alignment = "center", spacing = 15)], alignment = "center")])


            
        page.views.append(lgn_view)
        page.update()
    

    def Main(usname):
        page.clean()
        page.title = "NotMax" #Этот бро реально не любит макс 💀
        us_nlc = None

        sct_chat = ft.Ref() #Оно как бы есть, а как бы и нет
        msg_chat = ft.Ref[ft.Column]()
        msg_ipt = ft.Ref[ft.TextField]()
        cntct = ft.Ref[ft.Column]()

        def settings():
            return ft.View("/settings",
                [ft.AppBar(title=ft.text("Настройки"))])

        ignore = ["info"]

        def load_cht(e):
            cntct.current.controls.clear()
            dop = db.collection(usname).stream()
            for i in dop:
                if i.id in ignore:
                    continue
                cntct.current.controls.append(
                    ft.TextButton(text = i.id, on_click=lambda e, name = i.id: user_slct_chat(name, []))
                )
            page.update()


        def user_slct_chat(us, lst_msg): #Обновление + ну тип если на чат кликаешь шаришь типо бро
            nonlocal us_nlc
            us_nlc = us
            sct_chat.current.controls.clear()
            sct_chat.current.controls.append(ft.Text(value=us, size=20, weight=ft.FontWeight.BOLD))
            sct_chat.current.update()

            msg_chat.current.controls.clear()

            Upd = db.collection(usname).document(us)

            def on_snapshot(doc_snapshot, changes, read_time):
                msg_chat.current.controls.clear()
                for doc in doc_snapshot:
                    if doc.exists:
                        data = doc.to_dict()
                        for key, val in sorted(data.items()):
                            msg_chat.current.controls.append(ft.Text(val))
                msg_chat.current.update()

            # Ставим слушатель на обновления
            Upd.on_snapshot(on_snapshot)
        
        if not db.collection(usname).document("Избранное").get().exists: #Наитупейшая проверка наличия пользователя в системе
            db.collection(usname).document("Избранное").set({})
            db.collection("All_users").document(usname).set({})

        
        async def send_msg(e): #короч функция отправки сообщений
            if msg_ipt.current.value.strip() == "": #Проверка на то, чтобы соо было не пустое
                text = ft.Text("Сообщение пустое!", size=20)
                omgtext = ft.Row([text], alignment=ft.MainAxisAlignment.CENTER)
                page.add(omgtext)
                page.update()
                await asyncio.sleep(1)
                page.controls.remove(omgtext)
                page.update()
                return
            Okak = f"{usname} - {us_nlc}" #АААА МЕМЧИК ОКАК ОЧЕНЬ СМЕШНО 🤣🤣😂🤣🤣😃🤣😂🤣🤣🤣🤣🤣🤣🤣
            print(usname, us_nlc)
            db.collection(us_nlc).document(usname).set({Okak : msg_ipt.current.value}, merge=True) #База менов 💀💀💀💀
            db.collection(usname).document(us_nlc).set({Okak : msg_ipt.current.value}, merge=True)
            msg_ipt.current.value = ""
            page.update()
            


        left_column = ft.Container(content=ft.Column(ref=cntct, scroll=ft.ScrollMode.AUTO, expand=True),
        border=ft.border.only(right=ft.border.BorderSide(1, ft.Colors.OUTLINE)))

        right_column = ft.Container(content=ft.Column([
                ft.Container(content=ft.Column(ref=sct_chat), padding=10, border=ft.border.only(bottom=ft.border.BorderSide(1, ft.Colors.OUTLINE))),
                ft.Container(content=ft.Column(ref=msg_chat, scroll=ft.ScrollMode.AUTO, expand=True), padding=10, expand=True),
                ft.Row([ft.TextField(ref=msg_ipt, expand=True, hint_text="Сообщение"),
                ft.IconButton(icon=ft.Icons.SEND, on_click=send_msg)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)]),expand=True)
        Main_view = ft.View(route = "/main", controls=[left_column, right_column])
        load_cht(None)
        return Main_view  
    check()

ft.app(target=All)
