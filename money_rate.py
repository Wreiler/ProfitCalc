import ctypes
from tkinter import *
from tkinter.ttk import Checkbutton
from tkinter.filedialog import *
from tkinter.messagebox import *
from functools import partial
import json
import datetime
from yaml import safe_load, dump
from idlelib.tooltip import Hovertip


# Для вывода иконки в панель задач
myappid = 'mycompany.myproduct.subproduct.version'
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

# Вывод основного окна программы
window = Tk()
window.title("ProfitCalc")  # Название окна
window.iconphoto(False, PhotoImage(file='img2.png'))  # Иконка на рамке окна
w, h = window.winfo_screenwidth(), window.winfo_screenheight()
xax, yax = (int(w*0.7), int(h*0.8)) if w <= 1366 and h <= 768 else (int(w*0.5), int(h*0.6))
window.geometry(f'{xax}x{yax}')
window.resizable(0, 0)

# Константы, необходимые для работы программы
frame_d1, frame_d2 = 0, 0  # - блоки набора коробок за день
d_ac1, d_ac2 = [], []  # - контейнеры для количества коробок за день

f = open('coefs.yaml', mode='r', encoding='utf-8')
temp = safe_load(f)
std, stn = temp['rates']['day_hour'], temp['rates']['night_hour']  # - ставки в день и ночь
hours = 11.3  # - часы работы
file_name = ''  # - default для имени файла
alt1, alt2 = [0, 0, 0], [0, 0, 0]  # - контейнеры окон для ввода процентов n-% премии
prem_n1, prem_n2 = [], []  # - контейнеры для всех n-% премий
inp_ver = []  # - контейнер для вставляемых значений
now_pg = 0  # - номер текущей страницы


# ФУНКЦИИ МЕНЮ ПРОГРАММЫ
def about():
    """
    Функция для вывода справки из меню программы
    """

    showinfo("Справка", "Программа для расчета оклада труда.\nВерсия 2.1.0\n\nby Wreiler")


def open_file():
    """
    Функция для открытия файла из меню программы
    """

    global file_name, ac1_list, ac2_list, inp_ver
    file = askopenfile()
    if file:
        file_name = file.name
        with open(file.name, 'r') as filej:
            ac1_list, ac2_list, inp_ver = json.load(filej)
        back(1)


def save_as_file():
    """
    Функция для сохранения файла в новый из меню программы
    """

    global file_name
    now = datetime.datetime.now()
    file = asksaveasfile(defaultextension=".json", initialfile=f'Расчет от {now.strftime("%d-%m-%Y")}')
    if file:
        file_name = file.name
        with open(file.name, 'w') as filej:
            data_package(now_pg)
            if now_pg == 1:
                pack = [ac1_list, [[[]]], inp_ver]
            elif now_pg in (2, 3):
                pack = [ac1_list, ac2_list, inp_ver]
            json.dump(pack, filej)


def save_file():
    """
    Функция для сохранения текущего файла из меню программы
    """

    global file_name
    file = file_name
    if file not in [None, '']:
        with open(file, "w") as filej:
            data_package(now_pg)
            if now_pg == 1:
                pack = [ac1_list, [[[]]], inp_ver]
            elif now_pg in (2, 3):
                pack = [ac1_list, ac2_list, inp_ver]
            json.dump(pack, filej)


def do_popup(event):
    """
    Функция для отображения меню программы
    """

    popup = Menu(window, tearoff=0)
    popup.add_command(label="Save", command=save_file)
    popup.add_command(label="About", command=about)
    popup.add_command(label="Exit", command=_exit)
    popup.tk_popup(event.x_root, event.y_root, 0)
    popup.grab_release()


def _exit():
    """
    Функция для выхода из программы с помощью кнопки из меню
    """

    if askyesno("Выход", "Хотите сохранить файл перед выходом?"):
        save_as_file()
    window.destroy()


def new_file():
    """
    Функция для создания нового фала из меню программы (очистка полей)
    """

    global file_name
    if askyesno("Новый файл", "Хотите сохранить файл перед созданием нового?"):
        save_as_file()
    for x in window.winfo_children():
        x.destroy()
    win_1st()
    file_name = ''


def make_menu(n):
    """
    Функция для создания и исполнения функционала меню программы
    """

    m = Menu(window)  # создается объект Меню на главном окне
    window.config(menu=m)  # окно конфигурируется с указанием меню для него

    fm = Menu(m, tearoff=0)  # создается пункт меню с размещением на основном меню (m)
    m.add_cascade(label="Файл", menu=fm)  # пункт располагается на основном меню (m)
    if n == 1:
        fm.add_command(label="Новый расчет", command=new_file)
        fm.add_command(label="Открыть...", command=open_file)
        fm.add_command(label="Сохранить", command=save_file)
        fm.add_command(label="Сохранить как...", command=save_as_file)
    else:
        fm.add_command(label="Сохранить результаты", command=save_file)
        fm.add_command(label="Сохранить результаты как...", command=save_as_file)
    fm.add_separator()
    fm.add_command(label="Выход", command=_exit)

    hm = Menu(m, tearoff=0)  # второй пункт меню
    m.add_cascade(label="Помощь", menu=hm)
    hm.add_command(label="Справка", command=about)


def update():
    """
    Функция для обновления окна программы и пересчета процентов выполненных коробок
    """

    if d_ac1:
        for i in d_ac1:
            i[2].config(state=NORMAL)
            try:
                i[2].delete(1.0, END)
                i[2].insert(0.0, round((int(i[1].get(0.0, END))/int(i[0].get(0.0, END)))*100))
            except:
                i[2].delete(1.0, END)
                i[2].insert(0.0, 0)
            i[2].config(state=DISABLED)
    if d_ac2:
        for i in d_ac2:
            i[2].config(state=NORMAL)
            try:
                i[2].delete(1.0, END)
                i[2].insert(0.0, round((int(i[1].get(0.0, END))/int(i[0].get(0.0, END)))*100))
            except:
                i[2].delete(1.0, END)
                i[2].insert(0.0, 0)
            i[2].config(state=DISABLED)
    window.after(800, update)


# ФУНКЦИИ ОТОБРАЖЕНИЯ ОСНОВНЫХ ОКОН И ПОЛЕЙ ПРОГРАММЫ
def win_1st():
    """
    Функция для отображения полей и элементов первого окна программы (ввод данных для AC1)
    """

    make_menu(1)

    letter = Label(window, text='ВХОДНЫЕ ДАННЫЕ ДЛЯ АС1:', font=("Times", int(yax * 0.036)),
                   bg='#dbdbdb', bd=3, relief='raised')
    letter.place(relx=0.5, rely=0.05, anchor=CENTER)

    # дни и ночи для AC1
    global dlab_ac1, dtext_ac1, nlab_ac1, ntext_ac1, but_ac1, ogib1
    dlab_ac1 = Label(window, text='Количество дней (АС1):', font=("Times", int(yax * 0.0245)))
    dlab_ac1.place(relx=0.39, rely=0.15, anchor=CENTER)
    dtext_ac1 = Text(window, width=3, height=1)
    dtext_ac1.place(relx=0.52, rely=0.15, anchor=CENTER)
    dtext_ac1.configure(font=f'garamond {round(yax * 0.0195)}')
    dtext_ac1.bind('<Key>', partial(check_keys, field=dtext_ac1))

    nlab_ac1 = Label(window, text='и ночей (АС1):', font=("Times", int(yax * 0.0245)))
    nlab_ac1.place(relx=0.61, rely=0.15, anchor=CENTER)
    ntext_ac1 = Text(window, width=3, height=1)
    ntext_ac1.place(relx=0.7, rely=0.15, anchor=CENTER)
    ntext_ac1.configure(font=f'garamond {round(yax * 0.0195)}')
    ntext_ac1.bind('<Key>', partial(check_keys, field=ntext_ac1))

    # кнопка для принятия количества дней
    ogib1 = Canvas(width=65, height=30)
    ogib1.place(relx=0.5, rely=0.215, anchor=CENTER)
    but_ac1 = Button(ogib1, text="Принять", font=("Times", round(yax * 0.0165)), bg='#D8D8D8',
                     width=7, height=1, relief='groove', command=ac1_print)
    but_ac1.place(relx=0.5, rely=0.5, anchor=CENTER)

    window.after(800, update)

    # кнопка перехода ко второму окну
    but_sec = Button(window, text="Далее", font=("Times", int(yax * 0.018)), bg='#D8D8D8',
                     width=10, height=1, relief='groove', command=partial(evaluate, page=1))
    but_sec.place(relx=0.5, rely=0.93, anchor=CENTER)

    # текущая страница
    global now_pg
    now_pg = 1


def win_2nd():
    """
    Функция для отображения полей и элементов второго окна программы (ввод данных для AC2)
    """

    make_menu(1)

    letter = Label(window, text='ВХОДНЫЕ ДАННЫЕ ДЛЯ АС2:', font=("Times", int(yax * 0.036)),
                   bg='#dbdbdb', bd=3, relief='raised')
    letter.place(relx=0.5, rely=0.05, anchor=CENTER)

    # дни и ночи для AC2
    global dlab_ac2, dtext_ac2, nlab_ac2, ntext_ac2, but_ac2, ogib2
    dlab_ac2 = Label(window, text='Количество дней (АС2):', font=("Times", int(yax * 0.0245)))
    dlab_ac2.place(relx=0.39, rely=0.15, anchor=CENTER)
    dtext_ac2 = Text(window, width=3, height=1)
    dtext_ac2.place(relx=0.52, rely=0.15, anchor=CENTER)
    dtext_ac2.configure(font=f'garamond {round(yax * 0.0195)}')
    dtext_ac2.bind('<Key>', partial(check_keys, field=dtext_ac2))

    nlab_ac2 = Label(window, text='и ночей (АС2):', font=("Times", int(yax * 0.0245)))
    nlab_ac2.place(relx=0.61, rely=0.15, anchor=CENTER)
    ntext_ac2 = Text(window, width=3, height=1)
    ntext_ac2.place(relx=0.7, rely=0.15, anchor=CENTER)
    ntext_ac2.configure(font=f'garamond {round(yax * 0.0195)}')
    ntext_ac2.bind('<Key>', partial(check_keys, field=ntext_ac2))

    # кнопка для принятия количества дней
    ogib2 = Canvas(width=65, height=30)
    ogib2.place(relx=0.5, rely=0.215, anchor=CENTER)
    but_ac2 = Button(ogib2, text="Принять", font=("Times", round(yax * 0.0165)), bg='#D8D8D8',
                     width=7, height=1, relief='groove', command=ac2_print)
    but_ac2.place(relx=0.5, rely=0.5, anchor=CENTER)

    window.after(800, update)

    # кнопка перехода к третьему окну
    but_sec = Button(window, text="Далее", font=("Times", int(yax * 0.018)), bg='#D8D8D8',
                     width=10, height=1, relief='groove', command=partial(evaluate, page=2))
    but_sec.place(relx=0.55, rely=0.93, anchor=CENTER)

    # кнопка для возвращения назад к первому окну
    but_sec = Button(window, text="Назад", font=("Times", int(yax * 0.018)), bg='#D8D8D8',
                     width=10, height=1, relief='groove', command=partial(back, page=1))
    but_sec.place(relx=0.45, rely=0.93, anchor=CENTER)

    # текущая страница
    global now_pg
    now_pg = 2


def win_3rd():
    """
    Функция для отображения полей и элементов третьего окна программы (ввод данных для аванса и ставок)
    """

    make_menu(1)

    letter = Label(window, text='ВХОДНЫЕ ДАННЫЕ ДЛЯ АВАНСА И СТАВОК:', font=("Times", int(yax * 0.036)),
                   bg='#dbdbdb', bd=3, relief='raised')
    letter.place(relx=0.5, rely=0.05, anchor=CENTER)

    # аванс
    global lab_ava, text_ava
    lab_ava = Label(window, text='Аванс:', font=("Times", int(yax * 0.0245)))
    lab_ava.place(relx=0.45, rely=0.26, anchor=CENTER)

    text_ava = Text(window, width=8, height=1)
    text_ava.place(relx=0.53, rely=0.26, anchor=CENTER)
    text_ava.configure(font=f'garamond {round(yax * 0.0195)}')
    text_ava.bind('<Key>', partial(check_keys, field=text_ava))

    # ставка в час для дня
    global st_day_lab, st_day_t, stav_d
    st_day_lab = Label(window, text='Ставка в час (день):', font=("Times", int(yax * 0.0245)))
    st_day_lab.place(relx=0.44, rely=0.44, anchor=CENTER)

    # поле для ставки для дня и управление им
    st_day_t = Text(window, width=8, height=1)
    st_day_t.place(relx=0.58, rely=0.44, anchor=CENTER)
    st_day_t.configure(font=f'garamond {round(yax * 0.0195)}', bg='#f2f2f2')
    st_day_t.bind('<Key>', partial(check_keys, field=st_day_t))
    st_day_t.insert(0.0, std)
    st_day_t.configure(state=DISABLED)

    stav_d = BooleanVar()
    ch_day = Checkbutton(text='', variable=stav_d, command=partial(ch_but, 0), takefocus=0)
    ch_day.place(relx=0.635, rely=0.44, anchor=CENTER)
    stav_d.set(True)
    Hovertip(ch_day, 'При активном режиме - значение перезаписывается в файл coefs.yaml\n'
                     'При неактивном режиме - значение используется лишь для текущего расчета', hover_delay=100)

    # ставка в час для ночи
    global st_nig_lab, st_nig_t, stav_n
    st_nig_lab = Label(window, text='Ставка в час (ночь):', font=("Times", int(yax * 0.0245)))
    st_nig_lab.place(relx=0.44, rely=0.62, anchor=CENTER)

    # поле для ставки для ночи и управление им
    st_nig_t = Text(window, width=8, height=1)
    st_nig_t.place(relx=0.58, rely=0.62, anchor=CENTER)
    st_nig_t.configure(font=f'garamond {round(yax * 0.0195)}', bg='#f2f2f2')
    st_nig_t.bind('<Key>', partial(check_keys, field=st_nig_t))
    st_nig_t.insert(0.0, stn)
    st_nig_t.configure(state=DISABLED)

    stav_n = BooleanVar()
    ch_nig = Checkbutton(text='', variable=stav_n, command=partial(ch_but, 1), takefocus=0)
    ch_nig.place(relx=0.635, rely=0.62, anchor=CENTER)
    stav_n.set(True)
    Hovertip(ch_nig, 'При активном режиме - значение перезаписывается в файл coefs.yaml\n'
                     'При неактивном режиме - значение используется лишь для текущего расчета', hover_delay=100)

    # кнопка для вычисления и перехода к четвертому окну
    but_culc = Button(window, text="Вычислить", font=("Times", int(yax * 0.0178), 'bold'), bg='#D8D8D8',
                      width=10, height=1, relief='groove', command=partial(evaluate, 3))
    but_culc.place(relx=0.55, rely=0.93, anchor=CENTER)

    # кнопка для возвращения назад ко второму окну
    but_sec = Button(window, text="Назад", font=("Times", int(yax * 0.0178)), bg='#D8D8D8',
                     width=10, height=1, relief='groove', command=partial(back, page=2))
    but_sec.place(relx=0.45, rely=0.93, anchor=CENTER)

    # текущая страница
    global now_pg
    now_pg = 3


def win_4th():
    """
    Функция для отображения полей и элементов четвертого окна программы (окна результатов)
    """

    make_menu(2)

    res = Label(window, text='РЕЗУЛЬТАТЫ:', font=("Times", int(yax * 0.036)),
                bg='#dbdbdb', bd=3, relief='raised')
    res.place(relx=0.5, rely=0.05, anchor=CENTER)

    but_back = Button(window, text="Назад", font=("Times", int(yax * 0.0178)), bg='#D8D8D8',
                      width=10, height=1, relief='groove', command=partial(back, page=3))
    but_back.place(relx=0.5, rely=0.93, anchor=CENTER)

    # текущая страница
    global now_pg
    now_pg = 3


def ac1_print():
    """
    Функция для вывода блока полей для ввода коробок на AC1
    """

    global frame_d1, d_ac1

    # проверка на ввод количества дней на AC1
    d_ac1 = []
    if frame_d1 != 0:
        frame_d1.destroy()
    days = incorrect_input(dtext_ac1)
    if days is None:
        frame_d1 = 0
        return
    ogib1.configure(highlightthickness=0)

    frame_d1 = Canvas(width=xax - 10, height=yax * 0.068 * (days // 10 if days % 10 == 0 else (days // 10) + 1),
                      highlightthickness=0, selectborderwidth=3)
    frame_d1.place(relx=0.5, rely=0.265, anchor='n')
    rs, cs = 1, 2
    for i in range(days):
        if i in [10, 20, 30]:
            rs += 1
            cs -= 10

        # обозначения для полей ввода коробок
        m = Canvas(frame_d1, width=xax * 0.02, height=yax * 0.16)
        m.grid(row=rs, column=1, sticky='e', padx=0.5, pady=5)

        p_let = Button(m, text="П", font=("garamond", int(yax * 0.016), 'bold'), fg='#2a7485',
                       width=1, height=1, relief=GROOVE, justify=CENTER, state=DISABLED, borderwidth=0)
        p_let.place(relx=0.5, rely=0.4, anchor=CENTER)
        v_let = Button(m, text="В", font=("garamond", int(yax * 0.016), 'bold'), fg='#2a7485',
                       width=1, height=1, relief=GROOVE, justify=CENTER, state=DISABLED, borderwidth=0)
        v_let.place(relx=0.55, rely=0.57, anchor=CENTER)
        pers_let = Button(m, text="%", font=("garamond", int(yax * 0.016), 'bold'), fg='#2a7485',
                       width=1, height=1, relief=GROOVE, justify=CENTER, state=DISABLED, borderwidth=0)
        pers_let.place(relx=0.53, rely=0.82, anchor=CENTER)

        Hovertip(p_let, 'П - плановое количество коробок', hover_delay=100)
        Hovertip(v_let, 'В - количество выполненных коробок', hover_delay=100)
        Hovertip(pers_let, '% - соотношение выполненных к плановым', hover_delay=100)

        f = Canvas(frame_d1, width=xax * 0.09, height=yax * 0.16,
                   highlightthickness=0.5, highlightbackground="black", bg='#dedede')
        f.grid(row=rs, column=cs + i, sticky='e', padx=1, pady=5)
        f.create_text(xax * 0.09 * 0.5, yax * 0.16 * 0.165, text=f'{i + 1}',
                      font=("Times", int(yax * 0.0175), 'italic'))
        f.create_line(5, yax * 0.16 * 0.72, xax * 0.09 - 5, yax * 0.16 * 0.72, fill='#333', width=1)
        for k in range(3):
            text1 = Text(f, width=3, height=1)
            text1.place(relx=0.25 * (k + 1), rely=0.4, anchor=CENTER)
            text1.configure(font=f'garamond {round(yax * 0.014)}')
            text1.bind('<Key>', partial(check_keys, field=text1))
            text2 = Text(f, width=3, height=1)
            text2.place(relx=0.25 * (k + 1), rely=0.58, anchor=CENTER)
            text2.configure(font=f'garamond {round(yax * 0.014)}')
            text2.bind('<Key>', partial(check_keys, field=text2))
            text3 = Text(f, width=3, height=1, bg='#f2f2f2')
            text3.place(relx=0.25 * (k + 1), rely=0.84, anchor=CENTER)
            text3.configure(font=f'garamond {round(yax * 0.015)} bold', state=DISABLED, fg='#1aab6e')
            d_ac1.append((text1, text2, text3))


def ac2_print():
    """
    Функция для вывода блока полей для ввода коробок на AC2
    """

    global frame_d2, d_ac2, days

    # проверка на ввод количества дней на AC2
    d_ac2 = []
    if frame_d2 != 0:
        frame_d2.destroy()
    days = incorrect_input(dtext_ac2)
    if days is None:
        frame_d2 = 0
        return
    ogib2.configure(highlightthickness=0)
    frame_d2 = Canvas(width=xax - 10, height=yax * 0.068 * (days // 10 if days % 10 == 0 else (days // 10) + 1),
                      highlightthickness=0)
    frame_d2.place(relx=0.5, rely=0.265, anchor='n')
    rs, cs = 1, 2
    for i in range(days):
        if i in [10, 20, 30]:
            rs += 1
            cs -= 10

        # обозначения для полей ввода коробок
        m = Canvas(frame_d2, width=xax * 0.02, height=yax * 0.16)
        m.grid(row=rs, column=1, sticky='e', padx=0.5, pady=5)

        p_let = Button(m, text="П", font=("garamond", int(yax * 0.016), 'bold'), fg='#2a7485',
                       width=1, height=1, relief=GROOVE, justify=CENTER, state=DISABLED, borderwidth=0)
        p_let.place(relx=0.5, rely=0.4, anchor=CENTER)
        v_let = Button(m, text="В", font=("garamond", int(yax * 0.016), 'bold'), fg='#2a7485',
                       width=1, height=1, relief=GROOVE, justify=CENTER, state=DISABLED, borderwidth=0)
        v_let.place(relx=0.55, rely=0.57, anchor=CENTER)
        pers_let = Button(m, text="%", font=("garamond", int(yax * 0.016), 'bold'), fg='#2a7485',
                          width=1, height=1, relief=GROOVE, justify=CENTER, state=DISABLED, borderwidth=0)
        pers_let.place(relx=0.53, rely=0.82, anchor=CENTER)

        Hovertip(p_let, 'П - плановое количество коробок', hover_delay=100)
        Hovertip(v_let, 'В - количество выполненных коробок', hover_delay=100)
        Hovertip(pers_let, '% - соотношение выполненных к плановым', hover_delay=100)

        f = Canvas(frame_d2, width=xax * 0.09, height=yax * 0.16,
                   highlightthickness=0.5, highlightbackground="black", bg='#dedede')
        f.grid(row=rs, column=cs + i, sticky='e', padx=1, pady=5)
        f.create_text(xax * 0.09 * 0.5, yax * 0.16 * 0.165, text=f'{i + 1}',
                      font=("Times", int(yax * 0.0175), 'italic'))
        f.create_line(5, yax * 0.16 * 0.72, xax * 0.09 - 5, yax * 0.16 * 0.72, fill='#333', width=1)
        for k in range(3):
            text1 = Text(f, width=3, height=1)
            text1.place(relx=0.25 * (k + 1), rely=0.4, anchor=CENTER)
            text1.configure(font=f'garamond {round(yax * 0.014)}')
            text1.bind('<Key>', partial(check_keys, field=text1))
            text2 = Text(f, width=3, height=1)
            text2.place(relx=0.25 * (k + 1), rely=0.58, anchor=CENTER)
            text2.configure(font=f'garamond {round(yax * 0.014)}')
            text2.bind('<Key>', partial(check_keys, field=text2))
            text3 = Text(f, width=3, height=1, bg='#f2f2f2')
            text3.place(relx=0.25 * (k + 1), rely=0.84, anchor=CENTER)
            text3.configure(font=f'garamond {round(yax * 0.015)} bold', state=DISABLED, fg='#1aab6e')
            d_ac2.append((text1, text2, text3))


def back(page):
    """
    Функция для возвращения к первому окну программы и вставки введенных значений обратно в поля
    """

    # очистка экрана и отображение первого окна
    for x in window.winfo_children():
        x.destroy()
    if page == 1:
        win_1st()
    elif page == 2:
        win_2nd()
    elif page == 3:
        win_3rd()

    # обработка значений из "памяти ввода"
    global inp_ver
    if page == 1:
        global d_ac2
        d_ac2 = []
        txts = ('dtext_ac1', 'ntext_ac1')
        [eval(f'{txts[x]}.insert(0.0, inp_ver[x])') for x in range(len(txts))]
        if file_name == '':
            inp_ver = []

        # вставка значений в поля на свои места
        if ac1_list != [[[]]]:
            ac1_print()
            temp1 = [[k for k in x] for i in ac1_list for x in i]
            [[(x[0].insert(0.0, temp1[d_ac1.index(x)][0]), x[1].insert(0.0, temp1[d_ac1.index(x)][1]))
              for x in d_ac1[i:i + 3]] for i in range(0, len(d_ac1), 3)]
    if page == 2:
        txts = ('dtext_ac2', 'ntext_ac2')
        [eval(f'{txts[x]}.insert(0.0, inp_ver[x+2])') for x in range(len(txts))]
        if file_name == '':
            inp_ver = inp_ver[:2]

        # вставка значений в поля на свои места
        if ac2_list != [[[]]]:
            ac2_print()
            temp2 = [[k for k in x] for i in ac2_list for x in i]
            [[(x[0].insert(0.0, temp2[d_ac2.index(x)][0]), x[1].insert(0.0, temp2[d_ac2.index(x)][1]))
              for x in d_ac2[i:i + 3]] for i in range(0, len(d_ac2), 3)]
    if page == 3:
        sts = ('st_day_t', 'st_nig_t')
        eval('text_ava.insert(0.0, inp_ver[4])')
        [eval(f'{sts[x]}.configure(state=NORMAL)') for x in range(len(sts))]
        [eval(f'{sts[x]}.delete(0.0, END)') for x in range(len(sts))]
        [eval(f'{sts[x]}.insert(0.0, inp_ver[x+5])') for x in range(len(sts))]
        [eval(f'{sts[x]}.configure(state=DISABLED)') for x in range(len(sts))]
        if file_name == '':
            inp_ver = inp_ver[:4]


# ФУНКЦИИ ВЫЧИСЛЕНИЙ И ОБРАБОТКИ РЕЗУЛЬТАТОВ ПРОГРАММЫ
def data_package(page):
    """
    Функция для "запаковывания" введенных данных для удобства работы
    """

    global ac1_list, ac2_list, inp_ver
    if page == 1:
        if push_check(d_ac1, ogib1):
            ac1_list = [[(x[0].get(0.0, END).strip(), x[1].get(0.0, END).strip()) for x in d_ac1[i:i + 3]]
                        for i in range(0, len(d_ac1), 3)]
            elements = (dtext_ac1, ntext_ac1)
            res = [incorrect_input(x) for x in elements]
            print(inp_ver)
            if len(inp_ver) < 2 or None in inp_ver:
                inp_ver = res
            if res != inp_ver[:2]:
                inp_ver[:2] = res
        else:
            ac1_list = [[[]]]
    elif page == 2:
        if push_check(d_ac2, ogib2):
            ac2_list = [[(x[0].get(0.0, END).strip(), x[1].get(0.0, END).strip()) for x in d_ac2[i:i + 3]]
                        for i in range(0, len(d_ac2), 3)]
            elements = (dtext_ac2, ntext_ac2)
            res = [incorrect_input(x) for x in elements]
            if len(inp_ver) < 4 or None in inp_ver:
                inp_ver = af_1 + res
            if res != inp_ver[2:4]:
                inp_ver[2:4] = res
        else:
            ac2_list = [[[]]]
    elif page == 3:
        elements = (text_ava, st_day_t, st_nig_t)
        res = [incorrect_input(x, 'fl') if x in (st_day_t, st_nig_t) else incorrect_input(x) for x in elements]
        if len(inp_ver) < 7 or None in inp_ver:
            inp_ver = af_2 + res
        if res != inp_ver[4:]:
            inp_ver[4:] = res


def evaluate(page):
    """
    Функция для управления вычислениями и их отображением
    """

    # запаковка данных и их проверка
    data_package(page)
    if page == 1:
        check1 = proof_days(ac1_list, frame_d1)
        el_check1 = [incorrect_input(x) for x in [dtext_ac1, ntext_ac1]]
        if check1 == 0 or None in el_check1:
            return
        for x in window.winfo_children():
            x.destroy()
        global d_ac1
        d_ac1 = []
        print(f'Результаты: {inp_ver}')
        global af_1
        af_1 = inp_ver
        try:
            back(2)
        except:
            win_2nd()
    elif page == 2:
        check2 = proof_days(ac2_list, frame_d2)
        el_check2 = [incorrect_input(x) for x in [dtext_ac2, ntext_ac2]]
        if check2 == 0 or None in el_check2:
            return
        for x in window.winfo_children():
            x.destroy()
        global d_ac2
        d_ac2 = []
        print(f'Результаты: {inp_ver}')
        global af_2
        af_2 = inp_ver
        try:
            back(3)
        except:
            win_3rd()
    elif page == 3:
        if None in inp_ver:
            return

        # сохранение коэффициентов в yaml-файл
        if stav_d.get():
            coef1 = incorrect_input(st_day_t, 'fl')
            to_yaml1 = {'rates': {'day_hour': coef1, 'night_hour': stn}}

            with open('coefs.yaml', 'w') as t:
                dump(to_yaml1, t, default_flow_style=False)
        elif stav_n.get():
            coef2 = incorrect_input(st_nig_t, 'fl')
            to_yaml2 = {'rates': {'day_hour': std, 'night_hour': coef2}}

            with open('coefs.yaml', 'w') as t:
                dump(to_yaml2, t, default_flow_style=False)
        elif stav_d.get() and stav_n.get():
            coef1 = incorrect_input(st_day_t, 'fl')
            coef2 = incorrect_input(st_nig_t, 'fl')
            to_yaml3 = {'rates': {'day_hour': coef1, 'night_hour': coef2}}

            with open('coefs.yaml', 'w') as t:
                dump(to_yaml3, t, default_flow_style=False)

        # очистка и переход к вычислениям и отображению их результатов
        for x in window.winfo_children():
            x.destroy()
        calculation(ac1_list, ac2_list, inp_ver)
        win_4th()


def calculation(days_ac1, days_ac2, fields):
    """
    Функция для вычислений и расчетов требуемых значений
    """

    global res_ac1, res_ac2, canx, cany, ocl1, ocl2, premia1, premia2, premia201, premia202
    print(days_ac1, days_ac2, sep='\n')
    print(fields)

    # расчет процентов по каробка в день
    p_temp1 = [[round(int(x[1] if x[1] != '' else 0) / int(x[0]) * 100)
                if (x[0] != '' or x[1] != '') else '' for x in i] for i in days_ac1]
    pers_dac1 = [sum([x for x in i if x != '']) // len([x for x in i if x != ''])
                 if any([x != '' for x in i]) else 0 for i in p_temp1]
    p_temp2 = [[round(int(x[1] if x[1] != '' else 0) / int(x[0]) * 100)
                if (x[0] != '' or x[1] != '') else '' for x in i] for i in days_ac2]
    pers_dac2 = [sum([x for x in i if x != '']) // len([x for x in i if x != ''])
                 if any([x != '' for x in i]) else 0 for i in p_temp2]
    print(pers_dac1, pers_dac2)

    # результаты для AC1
    canx, cany = (xax * 0.5) - 30, yax * 0.5
    res_ac1 = Canvas(width=canx, height=cany, bg='#e0e0e0', highlightthickness=1, highlightbackground="black")
    res_ac1.place(relx=0.255, rely=0.35, anchor=CENTER)
    res_ac1.create_text(canx * 0.5, cany * 0.065, text='AC1', font=("Times", int(yax * 0.0265), 'bold'), fill='#2a7485')
    ocl1 = fields[-2] * hours * fields[0]
    res_ac1.create_text(canx * 0.5, cany * 0.2, text=f'Оклад:  {round(ocl1, 2)}  руб.',
                        font=("Times", int(yax * 0.0225)))
    premia1 = sum([(fields[-2] * hours * x) // 100 for x in pers_dac1])
    res_ac1.create_text(canx * 0.5, cany * 0.32,
                        text=f'Премия:  {round(premia1, 2)}  руб.',
                        font=("Times", int(yax * 0.0225)))
    res_ac1.create_text(canx * 0.39, cany * 0.44, text=f'Премия          %:', font=("Times", int(yax * 0.0225)))
    res_ac1.create_text(canx * 0.39, cany * 0.59, text=f'Премия          %:', font=("Times", int(yax * 0.0225)))
    res_ac1.create_text(canx * 0.39, cany * 0.74, text=f'Премия          %:', font=("Times", int(yax * 0.0225)))

    per_text1_1 = Text(res_ac1, width=3, height=1)
    per_text1_1.place(relx=0.449, rely=0.44, anchor=CENTER)
    per_text1_1.configure(font=("Times", int(yax * 0.0225)))
    per_text1_1.bind('<Key>', partial(check_keys, field=per_text1_1))
    per_text1_1.insert(0.0, 10)

    per_text1_2 = Text(res_ac1, width=3, height=1)
    per_text1_2.place(relx=0.449, rely=0.59, anchor=CENTER)
    per_text1_2.configure(font=("Times", int(yax * 0.0225)))
    per_text1_2.bind('<Key>', partial(check_keys, field=per_text1_2))
    per_text1_2.insert(0.0, 10)

    per_text1_3 = Text(res_ac1, width=3, height=1)
    per_text1_3.place(relx=0.449, rely=0.74, anchor=CENTER)
    per_text1_3.configure(font=("Times", int(yax * 0.0225)))
    per_text1_3.bind('<Key>', partial(check_keys, field=per_text1_3))
    per_text1_3.insert(0.0, 0)

    but_per1 = Button(res_ac1, text="Пересчитать", font=("Times", 11), bg='#D8D8D8',
                      width=10, height=1, relief='groove',
                      command=partial(prem_pers, [per_text1_1, per_text1_2, per_text1_3]))
    but_per1.place(relx=0.5, rely=0.9, anchor=CENTER)

    # результаты для AC2
    res_ac2 = Canvas(width=(xax // 2) - 30, height=yax // 2, bg='#e0e0e0', highlightthickness=1,
                     highlightbackground="black")
    res_ac2.place(relx=0.745, rely=0.35, anchor=CENTER)
    res_ac2.create_text(canx * 0.5, cany * 0.065, text='AC2', font=("Times", int(yax * 0.0265), 'bold'), fill='#2a7485')
    ocl2 = fields[-2] * hours * fields[2] / 2
    res_ac2.create_text(canx * 0.5, cany * 0.2, text=f'Оклад:  {round(ocl2, 2)}  руб.',
                        font=("Times", int(yax * 0.0225)))
    premia2 = sum([(fields[-2] * hours * x) // 200 for x in pers_dac2])
    res_ac2.create_text(canx * 0.5, cany * 0.32,
                        text=f'Премия:  {round(premia2, 2)}  руб.',
                        font=("Times", int(yax * 0.0225)))
    res_ac2.create_text(canx * 0.39, cany * 0.44, text=f'Премия          %:', font=("Times", int(yax * 0.0225)))
    res_ac2.create_text(canx * 0.39, cany * 0.59, text=f'Премия          %:', font=("Times", int(yax * 0.0225)))
    res_ac2.create_text(canx * 0.39, cany * 0.74, text=f'Премия          %:', font=("Times", int(yax * 0.0225)))

    per_text2_1 = Text(res_ac2, width=3, height=1)
    per_text2_1.place(relx=0.449, rely=0.44, anchor=CENTER)
    per_text2_1.configure(font=("Times", int(yax * 0.0225)))
    per_text2_1.bind('<Key>', partial(check_keys, field=per_text2_1))
    per_text2_1.insert(0.0, 10)

    per_text2_2 = Text(res_ac2, width=3, height=1)
    per_text2_2.place(relx=0.449, rely=0.59, anchor=CENTER)
    per_text2_2.configure(font=("Times", int(yax * 0.0225)))
    per_text2_2.bind('<Key>', partial(check_keys, field=per_text2_2))
    per_text2_2.insert(0.0, 10)

    per_text2_3 = Text(res_ac2, width=3, height=1)
    per_text2_3.place(relx=0.449, rely=0.74, anchor=CENTER)
    per_text2_3.configure(font=("Times", int(yax * 0.0225)))
    per_text2_3.bind('<Key>', partial(check_keys, field=per_text2_3))
    per_text2_3.insert(0.0, 0)

    but_per2 = Button(res_ac2, text="Пересчитать", font=("Times", 11), bg='#D8D8D8',
                      width=10, height=1, relief='groove',
                      command=partial(prem_pers, [per_text2_1, per_text2_2, per_text2_3]))
    but_per2.place(relx=0.5, rely=0.9, anchor=CENTER)

    # линии для разделения
    line_ver = Canvas(width=xax // 100, height=yax // 2)
    line_ver.place(relx=0.5, rely=0.35, anchor=CENTER)
    line_ver.create_line(xax // 150, 0, xax // 150, yax // 2 + 40, fill='#1aab6e', width=3)
    line_hor = Canvas(width=xax - 45, height=yax // 170)
    line_hor.place(relx=0.5, rely=0.62, anchor=CENTER)
    line_hor.create_line(0, yax // 255, xax, yax // 255, fill='#1aab6e', width=3)

    # итоговые результаты
    global totx, toty, res_tot
    totx, toty = xax // 1.6, yax // 4
    res_tot = Canvas(width=totx, height=toty, bg='#e0e0e0', highlightthickness=3, highlightbackground="#2a7485")
    res_tot.place(relx=0.5, rely=0.76, anchor=CENTER)

    prem_pers([per_text1_1, per_text1_2, per_text1_3])
    prem_pers([per_text2_1, per_text2_2, per_text2_3])


def prem_pers(tf):
    """
    Функция для расчета n-% премии и перерасчета итоговых результатов
    """

    global ocl1, ocl2, alt1, alt2, prem_n1, prem_n2, res_tot
    pers = [int(x.get(0.0, END).strip()) for x in tf]
    parent = tf[0].master
    rely = 0.44

    # расчет n-% премии для AC1
    if parent == res_ac1:
        prem_n1 = [(i / 100) * ocl1 for i in pers]
        for i in range(3):
            ln = len(str(round(prem_n1[i], 2)).strip())
            if alt1[i] != 0:
                parent.delete(alt1[i])
                alt1[i] = parent.create_text(canx * 0.63 + canx * 0.01 * (ln-3), cany * rely,
                                             text=f'  {round(prem_n1[i], 2)}  руб.',
                                             font=("Times", int(yax * 0.0225)))
            else:
                alt1[i] = parent.create_text(canx * 0.63 + canx * 0.01 * (ln-3), cany * rely,
                                             text=f'  {round(prem_n1[i], 2)}  руб.',
                                             font=("Times", int(yax * 0.0225)))
            rely += 0.15
    # расчет n-% премии для AC2
    else:
        prem_n2 = [(i / 100) * ocl2 for i in pers]
        for i in range(3):
            ln = len(str(round(prem_n2[i], 2)).strip())
            if alt2[i] != 0:
                parent.delete(alt2[i])
                alt2[i] = parent.create_text(canx * 0.63 + canx * 0.01 * (ln-3), cany * rely,
                                             text=f'  {round(prem_n2[i], 2)}  руб.',
                                             font=("Times", int(yax * 0.0225)))
            else:
                alt2[i] = parent.create_text(canx * 0.63 + canx * 0.01 * (ln-3), cany * rely,
                                             text=f'  {round(prem_n2[i], 2)}  руб.',
                                             font=("Times", int(yax * 0.0225)))
            rely += 0.15

    # перерасчет итоговых значений
    res_tot.delete('all')
    sum_res = ocl1 + ocl2 + premia1 + premia2 + sum(prem_n1) + sum(prem_n2) + \
              (inp_ver[1] * inp_ver[-1]) + (inp_ver[3] * inp_ver[-1])
    res_tot.create_text(totx * 0.5, toty * 0.15, text=f'Сумма:  {round(sum_res, 2)}  руб.',
                        font=("Times", int(yax * 0.0225)))
    sum_res_per = sum_res - (sum_res * 0.13)
    res_tot.create_text(totx * 0.5, toty * 0.37, text=f'Сумма (-13%):  {round(sum_res_per, 2)}  руб.',
                        font=("Times", int(yax * 0.0225)))
    res_tot.create_text(totx * 0.5, toty * 0.59, text=f'Аванс:  {inp_ver[4]}  руб.',
                        font=("Times", int(yax * 0.0225)))
    res_tot.create_text(totx * 0.5, toty * 0.81, text=f'Сумма на руки:  {round(sum_res_per - inp_ver[4], 2)}  руб.',
                        font=("Times", int(yax * 0.024), 'bold'))


# ФУНКЦИИ ПРОВЕРКИ И ВЫДЕЛЕНИЯ ОШИБОК ПРОГРАММЫ
def incorrect_input(blog, mode='int'):
    """
    Функция для проверки ввода цифр во все основные поля программы, и пометка их в случае ошибки
    """

    try:
        if mode == 'fl':
            get_s = blog.get(0.0, END).strip()
            get_s = get_s.replace(',', '.') if ',' in get_s else get_s
            res = float(get_s)
        else:
            res = int(blog.get(0.0, END).strip())
        blog.configure(highlightthickness=0, highlightbackground='black', highlightcolor="black")
        return res
    except:
        blog.configure(highlightthickness=3, highlightbackground='red', highlightcolor="red")
        return


def check_keys(event, field):
    """
    Функция для ограничений на ввод символов в поля программы
    """

    s = field.get(0.0, END).strip()
    lim = ((field.winfo_reqwidth() + 8) // 10)
    if (len(s) == lim or (event.state & 4 and event.keysym == "v")) and event.keysym != 'BackSpace':
        return 'break'
    elif event.char == ' ' or event.keysym == 'Return' or event.keysym == 'Tab' or event.char.isalpha():
        return 'break'


def push_check(days, ogib):
    """
    Функция для проверки обязательного выбора количества дней
    """

    if days:
        ogib.configure(highlightthickness=0)
        return True
    else:
        ogib.configure(highlightthickness=3, highlightbackground="red")
        return False


def proof_days(l, frame):
    """
    Функция для проверки наличия хотя бы одного значения в блоке полей для ввода коробок
    """

    control = all([all([k == '' for k in x]) for i in l for x in i])
    if frame != 0:
        if control:
            frame.configure(highlightthickness=3, highlightbackground='red', highlightcolor="red")
            return 0
        else:
            frame.configure(highlightthickness=0, highlightbackground='black', highlightcolor="black")
            return 1
    return 0


def ch_but(but):
    """
    Функция для управлением блокировки полей ввода ставок
    """

    if but == 0:
        if stav_d.get():
            st_day_t.configure(state=DISABLED, bg='#f2f2f2')
        else:
            st_day_t.configure(state=NORMAL, bg='white')
    else:
        if stav_n.get():
            st_nig_t.configure(state=DISABLED, bg='#f2f2f2')
        else:
            st_nig_t.configure(state=NORMAL, bg='white')


# Начало работы программы - запуск первой основной функции
win_1st()
# win_2nd()
# win_3rd()

# Удержание окна программы открытым
window.mainloop()
