import flet as ft
from datetime import datetime, time
from firebase_config import db
from firebase_admin import credentials, firestore
import asyncio
usname = input("Введите ваше имя пользователя: ")
chk = False
def check(chk):
    if chk == False:
        ft.app(target = LogReg)

def LogReg(page: ft.Page):
    page.title = "Вход/Регистрация"
    page.views.clear()
    
    title = ft.Text("Войти", size=30, weight="bold")
    login = ft.TextField(label="Логин")
    pswd = ft.TextField(label="Пароль", password=True)
    LogBut = ft.ElevatedButton("Войти", width=300)
    Pcl = ft.TextButton("Нет аккаунта? Зарегестрироваться.", on_click = opn_vw)

    def opn_vw(e):
        page.views.append(regs())
        page.update()
    
    login = ft.View(route="/", controls=
        [ft.Row([ft.Coloumn([title, login, pswd, LogBut, Pcl],
            horizontal_aligment="center", spacing = 20)], aligment = "center")])
    
    def rst_lgn(e):
        page.views.pop()
        page.update()

    def regs():
        reg_title = ft.Text("Зарегестрироваться", size = 30, weight = "bold")
        reg_login = ft.TextField(label = "Логин")
        reg_email = ft.textField(label = "Почта")
        reg_pswd1 = ft.textField(label = "Пароль", password = True)
        reg_pswd2 = ft.textField(label = "Подтвердите пароль", password = True)
        if reg_pswd1.current.elue() != reg_pswd2.current.value():
            err = ft.Text("Пароли не совпадают", color = "red", size = 12)
        RegBut = ft.ElevatedButton("Зарегистрироваться", width = 300)
        bck_lgn = ft.TextButton("Уже есть аккаунт? Войти.", on_click=auth_db)

        return ft.View(route = "/reg",controls = [ft.Row([ft.Coloumn([reg_title,
                reg_login, reg_email, reg_pswd1, reg_pswd2, err],horizontal_aligment = "center", spacing = 15)], aligment = "center")])
        def auth_db(e):
            db.collection(reg_login.currents.value).document(reg_pswd2).set({})
    page.views.append(rst_lgn)
    page.update
    
    def chk_true():
        pass

def Main(page: ft.Page):
    page.title = "NotMax" #Этот бро реально не любит макс 💀
    page.window_maximized = True
    us_nlc = None

    sct_chat = ft.Ref() #Оно как бы есть, а как бы и нет
    msg_chat = ft.Ref[ft.Column]()
    msg_ipt = ft.Ref[ft.TextField]()
    cntct = ft.Ref[ft.Column]()

    def settings():
        return ft.View("/settings",
            [ft.AppBar(title=ft.text("Настройки"))])

    def load_cht(e): #В виде функции просто по приколу
        cntct.current.controls.clear()
        cht = db.collection(usname).stream()
        for cht in cht:
            cntct.current.controls.append(
               ft.TextButton(text=cht.id, on_click=lambda e, name=cht.id: user_slct_chat(name, [])))
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
        


    left_column = ft.Container( #Я не знаю зачем это, но оно нужно
    content=ft.Column(ref=cntct, scroll=ft.ScrollMode.AUTO, expand=True),
    border=ft.border.only(right=ft.border.BorderSide(1, ft.Colors.OUTLINE)))

    right_column = ft.Container([ft.Container(content=ft.Column(ref=sct_chat), padding=10, border=ft.border.only(bottom=ft.border.BorderSide(1, ft.Colors.OUTLINE))),
            ft.Container(content=ft.Column(ref=msg_chat, scroll=ft.ScrollMode.AUTO, expand=True),padding=10,expand=True),
            ft.Row([ft.IconButton(icon=ft.Icons.SETTINGS, on_click = settings)], alignment=ft.MainAxisAlignment.END),
            ft.Row([ft.TextField(ref=msg_ipt, expand=True, hint_text="Сообщение"), ft.IconButton(icon=ft.Icons.SEND, on_click=send_msg)],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN)], expand=True)
    page.add(ft.Row([left_column, right_column], expand=True))
    load_cht(None)  


