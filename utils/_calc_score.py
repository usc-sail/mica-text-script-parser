import numpy as np

def calc_score(true, pred, class_):
    true = np.array(list(true))
    pred = np.array(list(pred))
    prec = np.sum((pred == class_) & (true == class_))/np.sum(pred == class_)
    recl = np.sum((true == class_) & (pred == class_))/np.sum(true == class_)
    f1 = 2*prec*recl/(prec + recl)
    return prec, recl, f1