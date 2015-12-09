__author__ = 'frankhe'
import subprocess
from Generate import compute_error
from Generate import compute_classification
from libFM_tool import DataProcess
import numpy
import scipy.io
dataProcess = DataProcess()


def experiment3_user_similarity(active_learning_ratio=0.1):
    print '\n==================================='
    print 'experiment3 choosing special active learning users after classification started'
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
        [dataProcess.movieDataBase.TOTAL_USERS, dataProcess.TEST_MOVIES], dtype=numpy.bool_)
    for index in selected_data_positions:
        userId = dataProcess.test_addAllNegative_data[index][0]
        movieId = dataProcess.test_addAllNegative_data[index][1]
        positive_user_id_movie_id[userId-1][dataProcess.test_from_movie_id_get_movie_num[movieId]-1] = numpy.True_

    print '\n==================================='
    print 'step2: regression started'
    print '==================================='

    subprocess.call("./Generate/libFM -task r -train Generate/train_step2.libfm -test Generate/test_step2.libfm "
                    "-method mcmc -iter 1 -out Generate/prediction", shell=True)
    f1 = open('Generate/prediction')
    step2_pred_rating = f1.readlines()
    f1.close()
    step2_pred_rating = [float(x.strip()) for x in step2_pred_rating]
    step2_pred_data = []
    for i in range(len(dataProcess.test_addAllNegative_data)):
        step2_pred_data.append([dataProcess.test_addAllNegative_data[i][0],
                                dataProcess.test_addAllNegative_data[i][1], step2_pred_rating[i]])

    dataProcess.movieDataBase.compute_numpy_matrix(step2_pred_data)
    pred_rating_numpy_matrix = dataProcess.movieDataBase.numpy_rating_matrix
    pred_from_movie_id_get_movie_num = dataProcess.movieDataBase.from_movie_id_get_movie_num
    # print pred_rating_numpy_matrix[10][pred_from_movie_id_get_movie_num[743]-1]

    dictionary = dict()
    dictionary['train_rating'] = dataProcess.train_rating_numpy_matrix
    dictionary['predict_rating'] = pred_rating_numpy_matrix
    dictionary['positive_rating'] = positive_user_id_movie_id
    scipy.io.savemat('step2.mat', dictionary)
    """next we have to use Matlab"""
    return

    print '\n==================================='
    print 'choosing users with special similarity'
    print '==================================='

    number_of_index = len(test_addAllNegative_data)
    alternative_user_movie_list = []

    alternative_user_movie_list.append([userId, movieId])
    alternative_user_movie_list_sorted = sorted(alternative_user_movie_list, key=lambda x: x[1])
    # for x, y in alternative_user_movie_list_sorted:
    #     print x, y

    # alternative_user_movie_list = []
    # invited_user_movies = [0] * (movieDataBase.TOTAL_USERS+1)
    # for userId, movieId in alternative_user_movie_list_sorted:
    #     if invited_user_movies[userId] < MAX_INVITATION:
    #         invited_user_movies[userId] += 1
    #         alternative_user_movie_list.append([userId, movieId])
    #         if len(alternative_user_movie_list) >= int(number_of_index*active_learning_ratio):
    #             break

    # for x, y in alternative_user_movie_list:
    #     print x, y

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
                    "-method sgd -dim '1,1, 200' -learn_rate 0.001 -iter 10 -out Generate/prediction", shell=True)
    print 'number of alternative user-movie requests=', len(alternative_user_movie_list)
    print 'number of gained active learning user-movie data=', count
    compute_error.computer_error()

if __name__ == '__main__':
    experiment3_user_similarity()