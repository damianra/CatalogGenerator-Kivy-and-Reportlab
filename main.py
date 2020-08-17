from kivy.uix.popup import Popup
import kivy
import os
import sqlite3

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen

from PdfObject import CreatePDF

kivy.require('1.11.1')


# Conection or create database and table
def connect_to_database(path):
    try:
        con = sqlite3.connect(path)
        cursor = con.cursor()
        create_table_products(cursor)
        con.commit()
        con.close()
    except Exception as e:
        print(e)


def create_table_products(cursor):
    cursor.execute(
        """
        CREATE TABLE Products(
        ID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        Name TEXT NOT NULL,
        Description TEXT NOT NULL,
        Price TEXT NOT NULL,
        IMG TEXT NOT NULL
        )
        """
    )



class MainWid(ScreenManager):
    def __init__(self, **kwargs):
        super(MainWid, self).__init__()
        # application folder
        self.APP_PATH = os.getcwd()
        # Database location
        self.DB_PATH = self.APP_PATH + '/catalog.db'
        self.HomeWid = HomeWid(self)
        self.ProductsWid = ProductsWid(self)
        self.AddWid = AddWid(self)
        self.UpdateDataWid = BoxLayout()
        self.Configuration = Configuration(self)

        wid = Screen(name='home')
        wid.add_widget(self.HomeWid)
        self.add_widget(wid)
        wid = Screen(name='products')
        wid.add_widget(self.ProductsWid)
        self.add_widget(wid)
        wid = Screen(name='add')
        wid.add_widget(self.AddWid)
        self.add_widget(wid)
        wid = Screen(name='update')
        wid.add_widget(self.UpdateDataWid)
        self.add_widget(wid)
        wid = Screen(name='config')
        wid.add_widget(self.Configuration)
        self.add_widget(wid)


        connect_to_database(self.DB_PATH)
        self.goto_home()

    def goto_home(self):
        self.ProductsWid.poblar()
        self.current = 'home'

    def goto_products(self):
        self.ProductsWid.poblar()
        self.current = 'products'

    def goto_add(self):
        self.current = 'add'

    def goto_update(self, data_id):
        self.UpdateDataWid.clear_widgets()
        wid = UpdateDataWid(self, data_id)
        self.UpdateDataWid.add_widget(wid)
        self.current = 'update'

    def delete_data(self, data_id):
        con = sqlite3.connect(self.DB_PATH)
        cursor = con.cursor()
        cursor.execute('DELETE FROM Products WHERE ID='+str(data_id))
        con.commit()
        con.close()
        self.goto_products()

    def goto_configuration(self):
        self.current = 'config'


"""
    POPUP Select image
"""
class SelectImgWid(Popup):
    def __init__(self, addwid, **kwargs):
        super(SelectImgWid, self).__init__(**kwargs)
        self.addwid = addwid

    def select(self, *args):
        print(args[1][0])

        self.addwid.ids.imgurl.text = args[1][0]
        self.addwid.ids.img.source = args[1][0]
        self.addwid.ids.img.reload()
        self.dismiss()
"""
    STANDAR POPUP WINDOW
"""
# Popup widget
class MyPopup(Popup):
    def __init__(self, message):
        super(MyPopup, self).__init__()
        self.ids.label.text = message


class HomeWid(BoxLayout):
    def __init__(self, mainwid, **kwargs):
        super(HomeWid, self).__init__()
        self.mainwid = mainwid

    def btn_products(self):
        self.mainwid.goto_products()

    def btn_pdf(self):
        con = sqlite3.connect(self.mainwid.DB_PATH)
        cursor = con.cursor()
        cursor.execute('select * from Products')
        pdf = CreatePDF('catalogo_bettasdelsur.pdf', cursor)
        pdf.add_data()
        popup = MyPopup('PDF creado con exito!')
        popup.open()

    def go_config(self):
        self.mainwid.goto_configuration()

# Product list widget
class ProductsWid(BoxLayout):
    def __init__(self, mainwid, **kwargs):
        super(ProductsWid, self).__init__()
        self.mainwid = mainwid

        self.poblar()

    def poblar(self):
        con = sqlite3.connect(self.mainwid.DB_PATH)
        cursor = con.cursor()
        cursor.execute('select * from Products ORDER BY ID DESC')
        self.ids.rv.data = [{'data_id': x[0],'valor': x[1], 'img': x[4], 'mainwid': self.mainwid}
                        for x in cursor]
        con.close()

    def go_home(self):
        self.mainwid.goto_home()

    def go_add(self):
        self.mainwid.goto_add()


# Add products widget
class AddWid(BoxLayout):
    def __init__(self, mainwid, **kwargs):
        super(AddWid, self).__init__()
        self.mainwid = mainwid

    def btn_back(self):
        self.ids.name.text = ''
        self.ids.description.text = ''
        self.ids.price.text = ''
        self.ids.imgurl.text = ''
        self.ids.img.source = 'eLearning.png'
        self.mainwid.goto_products()

    def btn_insert(self):
        con = sqlite3.connect(self.mainwid.DB_PATH)
        cursor = con.cursor()
        name = self.ids.name.text
        description = self.ids.description.text
        price = self.ids.price.text
        img = self.ids.imgurl.text
        listdata = (name, description, price, img)
        query = 'INSERT INTO Products (Name,Description,Price,IMG)'
        val = 'VALUES("%s","%s","%s","%s")' % listdata
        try:
            cursor.execute(query + ' ' + val)
            con.commit()
            con.close()
            self.ids.name.text = ''
            self.ids.description.text = ''
            self.ids.price.text = ''
            self.ids.imgurl.text = ''
            self.ids.img.source = 'eLearning.png'
            self.mainwid.goto_products()
        except Exception as e:
            if '' in listdata:
                print('uno o mas campos esta vacios')
            print(e)

    def load_img(self):
        dialog = SelectImgWid(self)
        dialog.open()


# Update widget
class UpdateDataWid(BoxLayout):
    def __init__(self, mainwid, data_id, **kwargs):
        super(UpdateDataWid, self).__init__()
        self.mainwid = mainwid
        self.data_id = str(data_id)
        self.check_memory()

    def check_memory(self):
        con = sqlite3.connect(self.mainwid.DB_PATH)
        cursor = con.cursor()
        query = 'select * from Products where ID='
        cursor.execute(query + self.data_id)
        for i in cursor:
            self.ids.name.text = i[1]
            self.ids.description.text = i[2]
            self.ids.price.text = i[3]
            self.ids.imgurl.text = i[4]
        con.close()
        self.ids.img.source = self.ids.imgurl.text
        self.ids.img.reload()

    def load_img(self):
        dialog = SelectImgWid(self)
        dialog.open()

    def update_data(self):
        con = sqlite3.connect(self.mainwid.DB_PATH)
        cursor = con.cursor()
        name = self.ids.name.text
        description = self.ids.description.text
        price = self.ids.price.text
        img = self.ids.imgurl.text
        a1 = (name, description, price, img)
        s1 = 'UPDATE Products SET'
        s2 = 'Name="%s",Description="%s",Price="%s",IMG="%s"' % a1
        s3 = 'WHERE ID=%s' % self.data_id

        cursor.execute(s1 + ' ' + s2 + ' ' + s3)
        con.commit()
        con.close()
        self.mainwid.goto_products()

    def btn_back(self):
        self.ids.name.text = ''
        self.ids.description.text = ''
        self.ids.price.text = ''
        self.ids.imgurl.text = ''
        self.mainwid.goto_products()


class Row(BoxLayout):
    def __init__(self, **kwargs):
        super(Row, self).__init__()


class Configuration(BoxLayout):
    def __init__(self, mainwid, **kwargs):
        super(Configuration, self).__init__()
        self.mainwid = mainwid

    def back_btn(self):
        self.mainwid.goto_home()


class MainApp(App):
    title = 'Catalog Application'

    def build(self):
        return MainWid()


if __name__ == '__main__':
    app = MainApp()
    app.run()