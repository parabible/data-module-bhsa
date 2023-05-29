from accents import Accents
from tf.app import use
A = use('bhsa', hoist=globals(), silent=True)

AObj = Accents(A)
AObj.atype2name2set.keys()
AObj.atype2name2set["disjunct"].keys()
