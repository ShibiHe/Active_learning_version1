__author__ = 'fenixlin'
from Generate import compute_error
from Generate import compute_classification
from db import Database
from libfm import LibFM

def sample_exp():
    # step 1: binary classification
    libfm = LibFM()
    db = Database('movielens', 718, 8928, 'ratings.csv', 'movies.attr')
    db.load_data()
    db.make_train_test_matrix()
    db.add_negative_data()
    db.dump_libfm_data('train_step1.libfm', 'test_step1.libfm')
    #
    #libfm.run('c', 'train_step1.libfm', 'test_step1.libfm')
    #selected_user = myutil.compute_classification()# XXX: dont get result directly....
    # XXX: is getting positive needed?

    # step 2: regression 
    #libfm.run('r', 'train_step1.libfm', 'test_step1.libfm')



if __name__ == '__main__':
    sample_exp()
