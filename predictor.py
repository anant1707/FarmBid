def pred (X,sc_X,sc_y,lab1,lab2,enco,model):
    X[:,1]=lab1.transform(X[:,1])
    X[:, 2] = lab1.transform(X[:, 2])
    X=enco.transform(X)
    X=sc_X.tranform(X)
    Y=model.predict(X)
    Y=sc_y.inverse_transform(Y)
    return Y
