import flet as ft
from datetime import datetime, time
from firebase_config import db
from firebase_admin import credentials, firestore
import asyncio
usname = input() 


def Main(page: ft.Page):
    page.title = "NotMax" #Этот бро реально не любит макс 💀
    us_nlc = None

    sct_chat = ft.Ref() #Оно как бы есть, а как бы и нет
    msg_chat = ft.Ref[ft.Column]()
    msg_ipt = ft.Ref[ft.TextField]()
    cntct = ft.Ref[ft.Column]()

    def load_cht(e): #В виде функции просто по приколу
        cntct.current.controls.clear()
        cht = db.collection(usname).stream()
        for cht in cht:
            cntct.current.controls.append(
               ft.TextButton(text=cht.id, on_click=lambda e, name=cht.id: user_slct_chat(name, [])))
        page.update()


    def user_slct_chat(us, lst_msg): #И это в виде функции просто зачем то (я то знаю зачем, а вы нет)
        sct_chat.current.controls.clear()
        sct_chat.current.controls.append(ft.Text(value=us, size=20, weight=ft.FontWeight.BOLD))
        nonlocal us_nlc
        us_nlc = us
        print(us_nlc)
    
    if not db.collection(usname).document("Избранное").get().exists: #Наитупейшая проверка наличия пользователя в системе
        db.collection(usname).document("Избранное").set({})
        db.collection("All_users").document(usname).set({})

    
    async def send_msg(e): #короч функция отправки сообщений
        if msg_ipt.current.value.strip() == "": #Проверка на то, чтобы соо было не пустое
            text = ft.Text("Сообщение пустое!", size=20)
            page.add(ft.Row([text], alignment=ft.MainAxisAlignment.CENTER))
            page.update()
            await asyncio.sleep(1)
            page.controls.remove(text)
            page.update()
            return
        Okak = ключ = f"{usname}-{us_nlc}" #АААА МЕМЧИК ОКАК ОЧЕНЬ СМЕШНО 🤣🤣😂🤣🤣😃🤣😂🤣🤣🤣🤣🤣🤣🤣
        print(usname, us_nlc)
        db.collection(us_nlc).add({Okak : msg_ipt.current.value}) #База менов 💀💀💀💀
        db.collection(usname).add({Okak : msg_ipt.current.value})
        msg_ipt.current.value = "" #и очищаем ввод
        page.update()
        
        
    left_column = ft.Container( #Я не знаю зачем это, но оно нужно
    content=ft.Column(
        ref=cntct, 
        scroll=ft.ScrollMode.AUTO,  
        expand=True),
    border=ft.border.only(right=ft.border.BorderSide(1, ft.Colors.OUTLINE)))

    right_column = ft.Column( #И тут тоже
        [ft.Container(
                content=ft.Column(ref=sct_chat),
                padding=10,
                border=ft.border.only(bottom=ft.border.BorderSide(1, ft.Colors.OUTLINE))),
            ft.Container(
                content=ft.Column(
                    ref=msg_chat, 
                    scroll=ft.ScrollMode.AUTO, 
                    expand=True),
                padding=10,
                expand=True),
            ft.Row(
                [ft.TextField(ref=msg_ipt, expand=True, hint_text="Сообщение"),
                    ft.IconButton(icon=ft.Icons.SEND, on_click=send_msg)],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN)],
        expand=True)
    page.add( #А это знаю, ну хоть что то
        ft.Row(
            [left_column, right_column],
            expand=True))
    load_cht(None)  
    
            
            

ft.app(target=Main)