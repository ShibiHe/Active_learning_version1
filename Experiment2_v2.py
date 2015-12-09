__author__ = 'frankhe'
import subprocess
from Generate import compute_error
from Generate import compute_classification
from libFM_tool import DataProcess
import random
import numpy
""" version2 is different from version1 because version2 choose users for every movie individually"""
dataProcess = DataProcess()


def baseline1_random(active_learning_ratio=0.1):
    print '\n==================================='
    print 'baseline1 with random choosing active learning data started'
    print '==================================='

    """ Choose active learning data randomly """
    number_of_index = len(dataProcess.test_addAllNegative_data)
    alternative_user_movie_list = []

    for choose_movie_num in range(1, dataProcess.TEST_MOVIES+1):
        choose_user_id_set = set()
        while len(choose_user_id_set) < dataProcess.movieDataBase.TOTAL_USERS*active_learning_ratio:
            choose_user_id_set.add(random.randint(1, dataProcess.movieDataBase.TOTAL_USERS))
        choose_user_id_set = list(choose_user_id_set)[:int(dataProcess.movieDataBase.TOTAL_USERS*active_learning_ratio)-1]

        for choose_user_id in choose_user_id_set:
            alternative_user_movie_list.append([choose_user_id, dataProcess.test_from_movie_num_get_movie_id[choose_movie_num]])

    # movieDataBase.make_alternative_user_movie_matrix(alternative_user_movie_list)

    """ add active learning result into train_original_data """
    print '\n==================================='
    print 'active learning regression started'
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
                    "-method sgd -dim '1,1, 200' -learn_rate 0.001 -iter 30 -out Generate/prediction", shell=True)
    print 'number of alternative user-movie requests=', len(alternative_user_movie_list)
    print 'number of gained active learning user-movie data=', count
    compute_error.computer_error()


def baseline2_random_after_classification(active_learning_ratio=0.1):
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
    selected_data_positions = compute_classification.compute_classification(len(dataProcess.test_original_data))

    positive_user_id_movie_id = numpy.zeros(
        [dataProcess.movieDataBase.TOTAL_USERS+1, dataProcess.movieDataBase.TOTAL_MOVIES+1], dtype=numpy.bool_)

    for index in selected_data_positions:
        userId = dataProcess.test_addAllNegative_data[index][0]
        movieId = dataProcess.test_addAllNegative_data[index][1]
        positive_user_id_movie_id[userId][movieId] = numpy.True_

    alternative_user_movie_list = []
    for choose_movie_num in range(1, dataProcess.TEST_MOVIES+1):
        movieId = dataProcess.test_from_movie_num_get_movie_id[choose_movie_num]
        choose_user_id_set = set()
        """first add all positive users"""
        for userId in range(1, dataProcess.movieDataBase.TOTAL_USERS+1):
            if positive_user_id_movie_id[userId][movieId] == numpy.True_:
                choose_user_id_set.add(userId)

        if len(choose_user_id_set) > dataProcess.movieDataBase.TOTAL_USERS*active_learning_ratio:
            choose_user_id_set = list(choose_user_id_set)[:int(dataProcess.movieDataBase.TOTAL_USERS*active_learning_ratio)]
        else:
            while len(choose_user_id_set) < dataProcess.movieDataBase.TOTAL_USERS*active_learning_ratio:
                choose_user_id_set.add(random.randint(1, dataProcess.movieDataBase.TOTAL_USERS))
        choose_user_id_set = list(choose_user_id_set)[:int(dataProcess.movieDataBase.TOTAL_USERS*active_learning_ratio)-1]

        for choose_user_id in choose_user_id_set:
            alternative_user_movie_list.append([choose_user_id, movieId])

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
                    "-method sgd -dim '1,1, 200' -learn_rate 0.01 -iter 30 -out Generate/prediction", shell=True)
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

    positive_user_id_movie_id = numpy.zeros(
        [dataProcess.movieDataBase.TOTAL_USERS+1, dataProcess.movieDataBase.TOTAL_MOVIES+1], dtype=numpy.bool_)

    for index in selected_data_positions:
        userId = dataProcess.test_addAllNegative_data[index][0]
        movieId = dataProcess.test_addAllNegative_data[index][1]
        positive_user_id_movie_id[userId][movieId] = numpy.True_

    user_mse_list = list(enumerate(dataProcess.movieDataBase.user_MSE))
    user_mse_sorted_list = sorted(user_mse_list, key=lambda x: x[1])

    alternative_user_movie_list = []
    for choose_movie_num in range(1, dataProcess.TEST_MOVIES+1):
        movieId = dataProcess.test_from_movie_num_get_movie_id[choose_movie_num]
        choose_user_id_set = set()
        """first add qualified and positive users"""
        for userId, _ in user_mse_sorted_list:
            if positive_user_id_movie_id[userId][movieId] == numpy.True_:
                choose_user_id_set.add(userId)

        if len(choose_user_id_set) > dataProcess.movieDataBase.TOTAL_USERS*active_learning_ratio:
            choose_user_id_set = list(choose_user_id_set)[:int(dataProcess.movieDataBase.TOTAL_USERS*active_learning_ratio)]
        else:
            """second add qualified users"""
            for userId, _ in user_mse_sorted_list:
                choose_user_id_set.add(userId)
                if len(choose_user_id_set) >= dataProcess.movieDataBase.TOTAL_USERS*active_learning_ratio:
                    break
        choose_user_id_set = list(choose_user_id_set)[:int(dataProcess.movieDataBase.TOTAL_USERS*active_learning_ratio)-1]
        for choose_user_id in choose_user_id_set:
            alternative_user_movie_list.append([choose_user_id, movieId])

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
                    "-method sgd -dim '1,1, 200' -learn_rate 0.01 -iter 50 -out Generate/prediction", shell=True)
    print 'number of alternative user-movie requests=', len(alternative_user_movie_list)
    print 'number of gained active learning user-movie data=', count
    compute_error.computer_error()


def experiment2_user_qualification_invited_limitation(active_learning_ratio=0.1, MAX_INVITED = 50):
    print '\n==================================='
    print 'experiment2 choosing qualified active learning data after classification started with invitation limit'
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

    positive_user_id_movie_id = numpy.zeros(
        [dataProcess.movieDataBase.TOTAL_USERS+1, dataProcess.movieDataBase.TOTAL_MOVIES+1], dtype=numpy.bool_)

    for index in selected_data_positions:
        userId = dataProcess.test_addAllNegative_data[index][0]
        movieId = dataProcess.test_addAllNegative_data[index][1]
        positive_user_id_movie_id[userId][movieId] = numpy.True_

    user_mse_list = list(enumerate(dataProcess.movieDataBase.user_MSE))
    user_mse_sorted_list = sorted(user_mse_list, key=lambda x: x[1])
    user_invited_times = [0] * (dataProcess.movieDataBase.TOTAL_USERS+1)

    alternative_user_movie_list = []
    """ notice that I shuffle the list here"""
    movie_choose_list = range(1, dataProcess.TEST_MOVIES+1)
    random.shuffle(movie_choose_list)
    for choose_movie_num in movie_choose_list:
        movieId = dataProcess.test_from_movie_num_get_movie_id[choose_movie_num]
        choose_user_id_set = set()
        """first add qualified and positive users"""
        for userId, _ in user_mse_sorted_list:
            if positive_user_id_movie_id[userId][movieId] == numpy.True_ and user_invited_times[userId] < MAX_INVITED:
                choose_user_id_set.add(userId)

        if len(choose_user_id_set) > dataProcess.movieDataBase.TOTAL_USERS*active_learning_ratio:
            choose_user_id_set = list(choose_user_id_set)[:int(dataProcess.movieDataBase.TOTAL_USERS*active_learning_ratio)]
        else:
            """second add positive users"""
            for userId, _ in user_mse_sorted_list:
                if user_invited_times[userId]<MAX_INVITED and positive_user_id_movie_id[userId][movieId] == numpy.True_:
                    choose_user_id_set.add(userId)
                if len(choose_user_id_set) >= dataProcess.movieDataBase.TOTAL_USERS*active_learning_ratio:
                    break
            """third add users with low mse"""
            for userId, _ in user_mse_sorted_list:
                if user_invited_times[userId]<MAX_INVITED:
                    choose_user_id_set.add(userId)
                if len(choose_user_id_set) >= dataProcess.movieDataBase.TOTAL_USERS*active_learning_ratio:
                    break
        choose_user_id_set = list(choose_user_id_set)[:int(dataProcess.movieDataBase.TOTAL_USERS*active_learning_ratio)-1]
        # print len(choose_user_id_set)
        for choose_user_id in choose_user_id_set:
            alternative_user_movie_list.append([choose_user_id, movieId])
            user_invited_times[choose_user_id] += 1

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
                    "-method sgd -dim '1,1, 200' -learn_rate 0.01 -iter 30 -out Generate/prediction", shell=True)
    print 'number of alternative user-movie requests=', len(alternative_user_movie_list)
    print 'number of gained active learning user-movie data=', count
    compute_error.computer_error()

if __name__ == '__main__':
    # baseline1_random()
    # baseline2_random_after_classification()
    # experiment2_user_qualification()
    experiment2_user_qualification_invited_limitation()
