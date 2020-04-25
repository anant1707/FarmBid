import pickle
import numpy as np
sc_X = pickle.load(open('model/sc_x.sav', 'rb'))
sc_y = pickle.load(open('model/sc_y.sav', 'rb'))
lab1 = pickle.load(open('model/labenc.pkl', 'rb'))
lab2 = pickle.load(open('model/labenc1.pkl', 'rb'))
enco = pickle.load(open('model/onehot.pkl', 'rb'))
model =pickle.load(open('model/finalmodel.sav', 'rb'))
def pred(X):
    global enco,lab1,lab2,sc_X,model
    X[:,1]=lab1.transform(X[:,1])
    X[:,2] =lab2.transform(X[:,2])
    X=enco.transform(X).toarray()
    X=np.delete(X,26,axis=1)
    X=np.delete(X,0,axis=1)
    X=sc_X.transform(X)
    Y=model.predict(X)
    Y=sc_y.inverse_transform(Y)
    print(Y)


pred(np.array([2019,'Paddy','Punjab']).reshape(1,-1))