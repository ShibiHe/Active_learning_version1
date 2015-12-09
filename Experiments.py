__author__ = 'frankhe'
import subprocess
from Generate import compute_error
from Generate import compute_classification
from libFM_tool import MovieDataBase


def naive_baseline(omitMovie=True):
    movieDataBase = MovieDataBase()
    movieDataBase.generate_complete_rating_data(regenerate=False)

    movieDataBase.make_sorted_rating_data([5, 1, 0])
    sorted_rating_data = movieDataBase.out_rating_data[:]
    movieDataBase.synchronize()
    movieDataBase.make_slice(count_movie_slice=range(1, 1201))
    movieDataBase.synchronize()
    movieDataBase.store_data_to_file(fileName='train_original_data')
    movieDataBase.generate_libfm_data(omitMovie=omitMovie)
    movieDataBase.store_data_to_file(movieDataBase.libfm_data, 'train_step1.libfm')

    movieDataBase.load_core_rating_data(sorted_rating_data)
    movieDataBase.make_slice(count_movie_slice=range(1201, 1441))
    movieDataBase.synchronize()
    movieDataBase.store_data_to_file(fileName='test_original_data')
    movieDataBase.generate_libfm_data(omitMovie=omitMovie, shuffle=False)
    movieDataBase.store_data_to_file(movieDataBase.libfm_data, 'test_step1.libfm')

    print '\n==================================='
    print 'naive baseline regression started'
    print '==================================='
    # subprocess.call("./Generate/libFM -task r -train Generate/train_step1.libfm -test Generate/test_step1.libfm "
    #                 "-method sgd -dim '1,1, 80' -learn_rate 0.001 -iter 160 -out Generate/prediction", shell=True)
    subprocess.call("./Generate/libFM -task r -train Generate/train_step1.libfm -test Generate/test_step1.libfm "
                    "-method mcmc -dim '1,1, 80' -out Generate/prediction", shell=True)
    compute_error.computer_error()


def experiment1():
    movieDataBase = MovieDataBase()
    movieDataBase.generate_complete_rating_data(regenerate=False)

    movieDataBase.make_sorted_rating_data([5, 1, 0])
    sorted_rating_data = movieDataBase.out_rating_data[:]
    movieDataBase.synchronize()
    movieDataBase.make_slice(count_movie_slice=range(1, 1201))
    movieDataBase.synchronize()

    train_original_data = movieDataBase.core_rating_data[:]
    movieDataBase.store_data_to_file(fileName='train_original_data')
    movieDataBase.generate_libfm_data(omitMovie=True)
    movieDataBase.store_data_to_file(movieDataBase.libfm_data, 'train_step2.libfm')

    movieDataBase.add_negative_data()
    movieDataBase.synchronize()
    train_addNegative_data = movieDataBase.core_rating_data[:]
    movieDataBase.store_data_to_file(fileName='train_addNegative_data')
    movieDataBase.generate_libfm_data(omitMovie=True)
    movieDataBase.store_data_to_file(movieDataBase.libfm_data, 'train_step1.libfm')

    movieDataBase.load_core_rating_data(sorted_rating_data)
    movieDataBase.make_slice(count_movie_slice=range(1201, 1441))
    movieDataBase.synchronize()

    test_original_data = movieDataBase.core_rating_data[:]
    movieDataBase.store_data_to_file(fileName='test_original_data')
    movieDataBase.generate_libfm_data(shuffle=False)
    movieDataBase.store_data_to_file(movieDataBase.libfm_data, fileName='test_step3.libfm')

    movieDataBase.add_negative_data(addAllUsers=True)
    movieDataBase.synchronize()
    test_addAllNegative_data = movieDataBase.core_rating_data[:]
    movieDataBase.store_data_to_file(fileName='test_addAllNegative_data')
    movieDataBase.generate_libfm_data(omitMovie=True, shuffle=False)
    movieDataBase.store_data_to_file(movieDataBase.libfm_data, 'test_step1.libfm')
    movieDataBase.store_data_to_file(movieDataBase.libfm_data, 'test_step2.libfm')

    """the test data is still in movieDataBase.core. Next is the step 1 """
    print '\n==================================='
    print 'step 1 binary classification started'
    print '==================================='

    subprocess.call("./Generate/libFM -task c -train Generate/train_step1.libfm -test Generate/test_step1.libfm "
                    "-method mcmc -out Generate/prediction", shell=True)
    # subprocess.call("./Generate/libFM -task c -train Generate/train_step1.libfm -test Generate/test_step1.libfm "
    #                 "-method sgd -learn_rate 0.01 -out Generate/prediction", shell=True)
    selected_data_positions = compute_classification.compute_classification(len(test_original_data))
    alternative_user_movie_list = []
    for index in selected_data_positions:
        userId = movieDataBase.core_rating_data[index][0]
        movieId = movieDataBase.core_rating_data[index][1]
        alternative_user_movie_list.append([userId, movieId])
    movieDataBase.make_alternative_user_movie_matrix(alternative_user_movie_list)

    """ step 2 regression"""
    print '\n==================================='
    print 'step 2 regression started'
    print '==================================='
    # subprocess.call("./Generate/libFM -task r -train Generate/train_step2.libfm -test Generate/test_step2.libfm "
    #                 "-method mcmc -out Generate/prediction", shell=True)

    print 'now we skip this part, because we currently regard all positive results as active learning alternative set.'
    # subprocess.call("./Generate/libFM -task r -train Generate/train_step2.libfm -test Generate/test_step2.libfm "
    #                 "-method sgd -learn_rate 0.001 -iter 70 -out Generate/prediction", shell=True)

    """ step 3  add active learning result into train_original_data """
    print '\n==================================='
    print 'step 3 active learning regression started'
    print '==================================='
    movieDataBase.make_user_movie_rating_matrix(test_original_data)
    active_learning_train_data = []

    # this scheme is adding every thing in active learning
    count = 0
    for values in alternative_user_movie_list:
        userId = values[0]
        movieId = values[1]
        ratings = movieDataBase.user_movie_rating_matrix.get(userId)
        if ratings is not None:
            rating = ratings.get(movieId)
            if rating is not None:
                active_learning_train_data.append([userId, movieId, rating])
                count += 1

    train_add_active_learning_data = train_original_data + active_learning_train_data
    movieDataBase.store_data_to_file(train_add_active_learning_data, fileName='train_add_active_learning_data')
    movieDataBase.generate_libfm_data(train_add_active_learning_data)
    movieDataBase.store_data_to_file(movieDataBase.libfm_data, fileName='train_step3.libfm')
    # subprocess.call("./Generate/libFM -task r -train Generate/train_step3.libfm -test Generate/test_step3.libfm "
    #                 "-method mcmc -out Generate/prediction", shell=True)
    # compute_error.computer_error()

    subprocess.call("./Generate/libFM -task r -train Generate/train_step3.libfm -test Generate/test_step3.libfm "
                    "-method sgd -dim '1,1, 200' -learn_rate 0.001 -iter 200 -out Generate/prediction", shell=True)
    print 'number of alternative user-movie requests=', len(alternative_user_movie_list)
    print 'number of gained active learning user-movie data=', count
    compute_error.computer_error()

if __name__ == '__main__':
    # naive_baseline()
    experiment1()
