__author__ = 'frankhe'
import subprocess
from Generate import compute_error
from Generate import compute_classification
from libFM_tool import DataProcess
from libFM_tool import MovieDataBase
import random
MAX_INVITATION = 50
""" this experiment2 has restricted every invitation at most invite a user to watch MAX_INVITATION movies"""


dataProcess = DataProcess()
def baseline1_random(active_learning_ratio=0.1):
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

    print '\n==================================='
    print 'baseline1 with random choosing active learning data started'
    print '==================================='

    """ Choose active learning data randomly """
    number_of_index = len(test_addAllNegative_data)
    print number_of_index*active_learning_ratio
    invited_user_movies = [0] * (movieDataBase.TOTAL_USERS+1)
    selected_data_positions = set()
    while len(selected_data_positions) < number_of_index*active_learning_ratio:
        new_index = random.randint(0, number_of_index-1)
        if invited_user_movies[movieDataBase.core_rating_data[new_index][0]] < MAX_INVITATION:
            selected_data_positions.add(new_index)
            invited_user_movies[movieDataBase.core_rating_data[new_index][0]] += 1

    alternative_user_movie_list = []
    for index in selected_data_positions:
        userId = movieDataBase.core_rating_data[index][0]
        movieId = movieDataBase.core_rating_data[index][1]
        alternative_user_movie_list.append([userId, movieId])
    movieDataBase.make_alternative_user_movie_matrix(alternative_user_movie_list)

    """ add active learning result into train_original_data """
    print '\n==================================='
    print 'active learning regression started'
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
                    "-method sgd -dim '1,1, 200' -learn_rate 0.001 -iter 10 -out Generate/prediction", shell=True)
    print 'number of alternative user-movie requests=', len(alternative_user_movie_list)
    print 'number of gained active learning user-movie data=', count
    compute_error.computer_error()


def baseline2_random_after_classification(active_learning_ratio=0.1):
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

    print '\n==================================='
    print 'baseline2 random choosing active learning data after classification started'
    print '==================================='

    """the test data is still in movieDataBase.core. Next is the step 1 """
    print '\n==================================='
    print 'step 1 binary classification started'
    print '==================================='

    subprocess.call("./Generate/libFM -task c -train Generate/train_step1.libfm -test Generate/test_step1.libfm "
                    "-method mcmc -iter 1 -out Generate/prediction", shell=True)
    # subprocess.call("./Generate/libFM -task c -train Generate/train_step1.libfm -test Generate/test_step1.libfm "
    #                 "-method sgd -learn_rate 0.01 -out Generate/prediction", shell=True)
    selected_data_positions_tmp = compute_classification.compute_classification(len(test_original_data))

    number_of_index = len(test_addAllNegative_data)
    invited_user_movies = [0] * (movieDataBase.TOTAL_USERS+1)
    selected_data_positions = set()
    while len(selected_data_positions) < number_of_index*active_learning_ratio:
        new_index = random.choice(selected_data_positions_tmp)
        if invited_user_movies[movieDataBase.core_rating_data[new_index][0]] < MAX_INVITATION:
            selected_data_positions.add(new_index)
            invited_user_movies[movieDataBase.core_rating_data[new_index][0]] += 1

    alternative_user_movie_list = []
    for index in selected_data_positions:
        userId = movieDataBase.core_rating_data[index][0]
        movieId = movieDataBase.core_rating_data[index][1]
        alternative_user_movie_list.append([userId, movieId])
    movieDataBase.make_alternative_user_movie_matrix(alternative_user_movie_list)

    """ add active learning result into train_original_data """
    print '\n==================================='
    print 'step active learning regression started'
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
                    "-method sgd -dim '1,1, 200' -learn_rate 0.001 -iter 20 -out Generate/prediction", shell=True)
    print 'number of alternative user-movie requests=', len(alternative_user_movie_list)
    print 'number of gained active learning user-movie data=', count
    compute_error.computer_error()


def experiment2_user_qualification(active_learning_ratio=0.1):
    print '\n==================================='
    print 'experiment2 choosing qualified active learning data after classification started'
    print '==================================='

    """the test data is still in movieDataBase.core. Next is the step 1 """
    print '\n==================================='
    print 'step 1 binary classification started'
    print '==================================='

    subprocess.call("./Generate/libFM -task c -train Generate/train_step1.libfm -test Generate/test_step1.libfm "
                    "-method mcmc -iter 1 -out Generate/prediction", shell=True)
    # subprocess.call("./Generate/libFM -task c -train Generate/train_step1.libfm -test Generate/test_step1.libfm "
    #                 "-method sgd -learn_rate 0.01 -out Generate/prediction", shell=True)
    selected_data_positions = compute_classification.compute_classification(len(dataProcess.test_original_data))

    print '\n==================================='
    print 'choosing users with low rating MSE'
    print '==================================='

    number_of_active_data = (int(dataProcess.movieDataBase.TOTAL_USERS*active_learning_ratio)-1)*240
    number_of_index = len(dataProcess.test_addAllNegative_data)
    alternative_user_movie_list = []
    for index in selected_data_positions:
        userId = dataProcess.test_addAllNegative_data[index][0]
        movieId = dataProcess.test_addAllNegative_data[index][1]
        alternative_user_movie_list.append([userId, movieId])

    alternative_user_movie_list_sorted = sorted(alternative_user_movie_list, key=lambda x: dataProcess.movieDataBase.user_MSE[x[0]])
    alternative_user_movie_list = []
    invited_user_movies = [0] * (dataProcess.movieDataBase.TOTAL_USERS+1)
    for userId, movieId in alternative_user_movie_list_sorted:
        if invited_user_movies[userId] < MAX_INVITATION:
            invited_user_movies[userId] += 1
            alternative_user_movie_list.append([userId, movieId])
            if len(alternative_user_movie_list) >= number_of_active_data:
                break

    # for x, y in alternative_user_movie_list:
    #     print x, y

    dataProcess.movieDataBase.make_alternative_user_movie_matrix(alternative_user_movie_list)

    """ add active learning result into train_original_data """
    print '\n==================================='
    print 'step active learning regression started'
    print '==================================='
    dataProcess.movieDataBase.make_user_movie_rating_matrix(dataProcess.test_original_data)
    active_learning_train_data = []

    # this scheme is adding every thing in active learning
    count = 0
    for values in alternative_user_movie_list:
        userId = values[0]
        movieId = values[1]
        ratings = dataProcess.movieDataBase.user_movie_rating_matrix.get(userId)
        if ratings is not None:
            rating = ratings.get(movieId)
            if rating is not None:
                active_learning_train_data.append([userId, movieId, rating])
                count += 1

    train_add_active_learning_data = dataProcess.train_original_data + active_learning_train_data
    dataProcess.movieDataBase.store_data_to_file(train_add_active_learning_data, fileName='train_add_active_learning_data')
    dataProcess.movieDataBase.generate_libfm_data(train_add_active_learning_data)
    dataProcess.movieDataBase.store_data_to_file(dataProcess.movieDataBase.libfm_data, fileName='train_step3.libfm')
    # subprocess.call("./Generate/libFM -task r -train Generate/train_step3.libfm -test Generate/test_step3.libfm "
    #                 "-method mcmc -out Generate/prediction", shell=True)
    # compute_error.computer_error()

    subprocess.call("./Generate/libFM -task r -train Generate/train_step3.libfm -test Generate/test_step3.libfm "
                    "-method sgd -dim '1,1, 200' -learn_rate 0.01 -iter 35 -out Generate/prediction", shell=True)
    print 'number of alternative user-movie requests=', len(alternative_user_movie_list)
    print 'number of gained active learning user-movie data=', count
    compute_error.computer_error()

if __name__ == '__main__':
    # baseline1_random(0.01)
    # baseline2_random_after_classification(0.01)
    experiment2_user_qualification()
