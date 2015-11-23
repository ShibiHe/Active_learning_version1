__author__ = 'frankhe'
import os
import cPickle
import random
import subprocess
from Generate import compute_classification
from Generate import compute_error


class MovieDataBase(object):
    """ total users=943 total movies=1682 total ratings=100,000 total occupations=21
    """
    def __init__(self):
        file_u_dot_item = open('u.item')
        movie_information_list = file_u_dot_item.readlines()
        self.movie_information_list = [x.split('|') for x in movie_information_list]
        # print len(self.movie_information_list) 1682

        file_u_dot_item.close()
        file_u_dot_attribute = open('u.attribute')
        self.movie_attribute_list = file_u_dot_attribute.readlines()
        self.movie_attribute_list = [''.join(x.split()) for x in self.movie_attribute_list]
        file_u_dot_attribute.close()
        # print len(self.movie_attribute_list) 1682

        file_u_dot_data = open('u.data')
        self.original_rating_data = file_u_dot_data.readlines()
        file_u_dot_data.close()
        # print len(self.original_rating_data) 100,000

        file_u_dot_genre = open('u.genre')
        movie_genre = file_u_dot_genre.readlines()
        self.movie_genre = [x.split('|')[0] for x in movie_genre]
        # print len(self.movie_genre) 19

        file_u_dot_user = open('u.user')
        user_information = file_u_dot_user.readlines()
        self.user_information = [x.split('|') for x in user_information]
        file_u_dot_user.close()
        # print len(self.user_information) 943

        file_u_dot_occupation = open('u.occupation')
        self.user_occupation = file_u_dot_occupation.readlines()
        file_u_dot_occupation.close()
        # print len(self.user_occupation) 21

        self.complete_rating_data = []
        self.out_rating_data = []

        """ this is the prime data, slice and sort are all executed on this data list"""
        self.core_rating_data = []
        self.user_movie_rating_matrix = dict()
        self.movie_user_rating_matrix = dict()
        self.userId_set = set()
        self.movieId_set = set()

        self.libfm_data = []

        """ this is the alternative data, used in step 1 binary classification """
        self.alternative_user_movie_matrix = dict()
        self.alternative_movie_user_matrix = dict()
        self.alternative_user_set = set()
        self.alternative_movie_set = set()

    @staticmethod
    def convert_date_to_int(productionDate):
        """ convert 01-Jan-1995 to 19950101 """
        values = productionDate.split('-')
        dictionary = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 'Jun': '06',
                      'Jul': '07', 'Aug': '08', 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'}
        values[1] = dictionary[values[1]]
        if len(values[0]) == 1:
            values[0] = '0'+values[0]
        return int(values[2]+values[1]+values[0])

    def get_movie_information(self, movieId):
        """movie 267 does not have information """
        if movieId == 267:
            attribute = self.movie_attribute_list[movieId-1]
            return "unknown", 22222222, "unknown", attribute
        movieId -= 1
        movieName = self.movie_information_list[movieId][1]
        movieProductionDate = self.movie_information_list[movieId][2]
        movieProductionDate = self.convert_date_to_int(movieProductionDate)
        movieWebsite = self.movie_information_list[movieId][3]
        attribute = self.movie_attribute_list[movieId]
        return movieName, movieProductionDate, movieWebsite, attribute

    def get_user_information(self, userId):
        userId -= 1
        userAge = int(self.user_information[userId][1])
        userGender = self.user_information[userId][2]
        userOccupation = self.user_information[userId][3]
        userZipCode = self.user_information[userId][4].strip()
        return userAge, userGender, userOccupation, userZipCode

    def generate_complete_rating_data(self, regenerate=False):
        """ Every rating record contains: 0:userId 1:movieId 2:rating 3:commentDate 4:movieName 5:movieProductionDate
        6:movieAttribute 7:userAge 8:userGender 9:userOccupation 10:userZipCode
        this complete_rating data will be stored in ./Generate/complete_rating_data which is a cPickle file
        """
        if not os.path.exists('./Generate'):
            os.makedirs('./Generate')
        if not os.path.exists('./Generate/complete_rating_data'):
            regenerate = True
        if not regenerate:
            file1 = open('./Generate/complete_rating_data', mode='rb')
            self.complete_rating_data = cPickle.load(file1)
            file1.close()
            self.core_rating_data = self.complete_rating_data
            return
        else:
            file1 = open('./Generate/complete_rating_data', mode='wb+')

        self.complete_rating_data = []
        for record in self.original_rating_data:
            values = record.split()
            userId = int(values[0])
            movieId = int(values[1])
            rating = int(values[2])
            commentDate = values[3]
            movieName, movieProductionDate, movieWebsite, movieAttribute = self.get_movie_information(movieId)
            userAge, userGender, userOccupation, userZipCode = self.get_user_information(userId)
            one_record = [userId, movieId, rating, commentDate, movieName, movieProductionDate, movieAttribute,
                              userAge, userGender, userOccupation, userZipCode]
            self.complete_rating_data.append(one_record)
        cPickle.dump(self.complete_rating_data, file1, protocol=2)
        self.core_rating_data = self.complete_rating_data[:]
        self.out_rating_data = self.complete_rating_data[:]
        file1.close()

    def make_slice(self, userId_slice=None, movieId_slice=None, rating_slice=None, data_list=None,
                   movieProductionDate_slice=None, count_movie_slice=None):
        """ id slice = set([x1,x2,x3, ...])   movieProduction_slice = [start, end]
        count_movie_slice reads movies and takes counts, it will select the number start to end movies
        """
        if data_list is None:
            data_list = self.core_rating_data

        def f(x):
            if x is not None:
                return set(x)
            return None
        userId_slice = f(userId_slice)
        movieId_slice = f(movieId_slice)
        rating_slice = f(rating_slice)
        count_movie_slice = f(count_movie_slice)

        start_date = end_date = 0
        if movieProductionDate_slice:
            start_date = movieProductionDate_slice[0]
            end_date = movieProductionDate_slice[1]

        already_count_movie_set = set()
        self.out_rating_data = []
        for values in data_list:
            already_count_movie_set.add(values[1])  # add this movie into count_movie set
            movie_ranking_number = len(already_count_movie_set)  # this movie's No
            if (userId_slice and values[0] not in userId_slice) or (movieId_slice and values[1] not in movieId_slice) \
                or (rating_slice and values[2] not in rating_slice) \
                    or (count_movie_slice and movie_ranking_number not in count_movie_slice) \
                        or (movieProductionDate_slice and (end_date < values[5] or values[5] < start_date)):
                continue
            self.out_rating_data.append(values)

    def make_sorted_rating_data(self, keyTuple, data_list=None):
        """ keyTuple is a list or tuple contains the keywords in sorting.
        keywords are in [0,10] the first keyword is prime key, and the second is the second key, etc.
        """
        if data_list is None:
            data_list = self.core_rating_data

        def f(x):
            keyList = []
            for number in keyTuple:
                keyList.append(x[number])
            return tuple(keyList)
        self.out_rating_data = sorted(data_list, key=lambda x: f(x))

    def make_user_movie_rating_matrix(self, data_list=None):
        if data_list is None:
            data_list = self.core_rating_data

        self.user_movie_rating_matrix.clear()
        self.movie_user_rating_matrix.clear()
        self.userId_set.clear()
        self.movieId_set.clear()
        for values in data_list:
            userId = values[0]
            movieId = values[1]
            self.userId_set.add(userId)
            self.movieId_set.add(movieId)
            rating = values[2]
            if self.user_movie_rating_matrix.get(userId) is None:
                self.user_movie_rating_matrix[userId] = dict()
                self.user_movie_rating_matrix[userId][movieId] = rating
            else:
                self.user_movie_rating_matrix[userId][movieId] = rating

            if self.movie_user_rating_matrix.get(movieId) is None:
                self.movie_user_rating_matrix[movieId] = dict()
                self.movie_user_rating_matrix[movieId][userId] = rating
            else:
                self.movie_user_rating_matrix[movieId][userId] = rating

    def make_alternative_user_movie_matrix(self, data_list):
        self.alternative_user_movie_matrix.clear()
        self.alternative_movie_user_matrix.clear()

        self.alternative_user_set.clear()
        self.alternative_movie_set.clear()
        for values in data_list:
            userId = values[0]
            movieId = values[1]
            self.alternative_user_set.add(userId)
            self.alternative_movie_set.add(movieId)
            if self.alternative_user_movie_matrix.get(userId) is None:
                self.alternative_user_movie_matrix[userId] = dict()
                self.alternative_user_movie_matrix[userId][movieId] = True
            else:
                self.alternative_user_movie_matrix[userId][movieId] = True

            if self.alternative_movie_user_matrix.get(movieId) is None:
                self.alternative_movie_user_matrix[movieId] = dict()
                self.alternative_movie_user_matrix[movieId][userId] = True
            else:
                self.alternative_movie_user_matrix[movieId][userId] = True

    def make_shuffle(self):
        self.out_rating_data = self.core_rating_data[:]
        random.shuffle(self.out_rating_data)

    def add_negative_data(self, data_list=None, addAllUsers=False):
        """if this is test data for binary classification, then you should choose addAllUsers """
        if data_list is None:
            data_list = self.core_rating_data

        self.out_rating_data = data_list[:]
        self.make_user_movie_rating_matrix(data_list)

        negative_data = []
        if addAllUsers:
            for movieId in self.movieId_set:
                for userId in range(1, 944):
                    if self.movie_user_rating_matrix[movieId].get(userId) is None:
                        negative_data.append([userId, movieId, -1])
        else:
            while len(negative_data) < len(data_list):
                userId = random.choice(list(self.userId_set))
                movieId = random.choice(list(self.movieId_set))
                if self.user_movie_rating_matrix[userId].get(movieId) is None:
                    negative_data.append([userId, movieId, -1])

        self.out_rating_data.extend(negative_data)

    def generate_libfm_data(self, data_list=None, shuffle=True, omitMovie=False):
        """ the output will be libfm file
        rating user:0-942 movie:943-2624 attribute:2625-2643
        rating user:0-942 attribute:943-961 (omitMovie=True)
        """
        if data_list is None:
            data_list = self.core_rating_data

        libfm_data = []
        for values in data_list:
            userId = values[0]
            movieId = values[1]
            rating = values[2]
            libfm_line = [rating, str(userId-1)+':1']

            count = 943
            if not omitMovie:
                libfm_line.append(str(movieId+count-1) + ':1')
                count = 943+1682  # 2625

            for attribute_pos in range(len(self.movie_attribute_list[movieId-1])):
                if self.movie_attribute_list[movieId-1][attribute_pos] == '1':
                    libfm_line.append(str(count+attribute_pos) + ':1')
            libfm_data.append(libfm_line)

        if shuffle:
            random.shuffle(libfm_data)
        self.libfm_data = libfm_data

    def store_data_to_file(self, data_list=None, fileName='a.out', serialization=False, slice_range=None):
        """ slice_range is only a slice of record's position in this data_list """
        if data_list is None:
            data_list = self.core_rating_data
        if slice_range:
            slice_range = set(slice_range)

        f = open('./Generate/'+fileName, mode='w+' if not serialization else 'wb+')
        data_list_dumped = []
        for data_pos in range(len(data_list)):
            if slice_range and data_pos not in slice_range:
                continue
            one_data = data_list[data_pos]
            if serialization:
                data_list_dumped.append(one_data)
            else:
                for i in range(len(one_data)):
                    f.write(str(one_data[i]))
                    if i != len(one_data)-1:
                        f.write(' ')
                f.write('\n')
        if serialization:
            cPickle.dump(data_list_dumped, f, protocol=2)
        f.close()

    def extract_data_from_file(self, fileName):
        f = open('./Generate/'+fileName, mode='rb')
        self.core_rating_data = cPickle.load(f)
        f.close()

    def load_core_rating_data(self, data_list):
        self.core_rating_data = data_list[:]

    def synchronize(self):
        self.core_rating_data = self.out_rating_data[:]


def naive_baseline(omitMovie=True):
    movieDataBase = MovieDataBase()
    movieDataBase.generate_complete_rating_data(regenerate=False)

    movieDataBase.make_sorted_rating_data([5, 1, 0])
    sorted_rating_data = movieDataBase.out_rating_data[:]
    movieDataBase.synchronize()
    movieDataBase.make_slice(count_movie_slice=range(1, 1201))
    movieDataBase.synchronize()
    movieDataBase.store_data_to_file(fileName='train_data')
    movieDataBase.generate_libfm_data(omitMovie=omitMovie)
    movieDataBase.store_data_to_file(movieDataBase.libfm_data, 'train.libfm')

    movieDataBase.load_core_rating_data(sorted_rating_data)
    movieDataBase.make_slice(count_movie_slice=range(1201, 1441))
    movieDataBase.synchronize()
    movieDataBase.store_data_to_file(fileName='test_data')
    movieDataBase.generate_libfm_data(omitMovie=omitMovie, shuffle=False)
    movieDataBase.store_data_to_file(movieDataBase.libfm_data, 'test.libfm')


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
    # subprocess.call("./Generate/libFM -task r -train Generate/train_step2.libfm -test Generate/test_step2.libfm "
    #                 "-method mcmc -out Generate/prediction", shell=True)
    subprocess.call("./Generate/libFM -task r -train Generate/train_step2.libfm -test Generate/test_step2.libfm "
                    "-method sgd -learn_rate 0.001 -iter 70 -out Generate/prediction", shell=True)

    """ step 3  add active learning result into train_original_data """
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
                    "-method sgd -dim '1,1, 80' -learn_rate 0.001 -iter 160 -out Generate/prediction", shell=True)
    compute_error.computer_error()

if __name__ == '__main__':
    experiment1()
