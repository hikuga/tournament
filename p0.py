from flask import Flask, render_template, request, redirect, url_for, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, CategoryItem

app = Flask(__name__)

engine = create_engine('sqlite:///itemscatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

class fake_item(object):
    def __init__(self, name, price):
        self.name = name
        self.price = price

class fake_catagory(object):
    def __init__(self, name, items):
        self.name = name
        self.items = items

def getFakeData():
    item1_1 = fake_item('item1_1', 24)
    item1_2 = fake_item('item1_2', 22)
    item2_1 = fake_item('item2_1', 25)
    item2_2 = fake_item('item2_2', 20)
    cat1 = fake_catagory('cat1', [item1_1, item1_2])
    cat2 = fake_catagory('cat2', [item2_1, item2_2])
    return [cat1, cat2]

def addFakeData():
    print 'adding fake data to db ...'
    cat1 = Category(name='cat1')
    session.add(cat1)
    session.commit()
    curr_cats = session.query(Category).all()
    print 'len(curr_cats) = '+str(len(curr_cats))
    curr_cat = curr_cats[0]

    item1_1 = CategoryItem(name='item1_1', description='desc item1_1', price=31, category_id = curr_cat.id)
    session.add(item1_1)
    session.commit()
    item1_2 = CategoryItem(name='item1_2', description='desc item1_2', price=20, category_id = curr_cat.id)
    session.add(item1_2)
    session.commit()
    print 'done adding data to db.'

def getData():
    all_cats = [(cat.id, cat.name) for cat in session.query(Category).all()]
    all_items = [ (item.id, item.name) for item in session.query(CategoryItem).all()]
    print 'catagories = '+str(all_cats)+' \n items = '+str(all_items)
    return (all_cats, all_items)

@app.route('/')
def mainPage():
    mainpageData = getData()
    maxlen = max(len(mainpageData[0]), len(mainpageData[1]))
    return render_template('mainpage.html', data=mainpageData, num=maxlen, l0 = len(mainpageData[0]),
        l1=len(mainpageData[1]))

if __name__ == '__main__':
    app.debug = True
    #addFakeData()
    app.run(host='0.0.0.0', port=5000)
