__author__ = 'frankhe'

import random

def generate_sorted_data():
    data = []
    file1 = open("u.data")
    for line in file1:
        values = line.split()
        one_tuple = (values[0], values[1], values[2], values[3])
        data.append(one_tuple)
    file1.close()
    user_sorted_data_raw=sorted(data, key=lambda x: (int(x[0]), int(x[1])))
    movie_sorted_data_raw=sorted(data, key=lambda x: (int(x[1]), int(x[0])))

    data1 = [x[0]+' '+x[1]+' '+x[2]+' '+x[3]+'\n' for x in user_sorted_data_raw]
    data2 = [x[0]+' '+x[1]+' '+x[2]+' '+x[3]+'\n' for x in movie_sorted_data_raw]
    file2 = open('user_sorted.data', mode='w+')
    file3 = open('movie_sorted.data', mode='w+')
    file2.writelines(data1)
    file3.writelines(data2)
    file2.close()
    file3.close()


def generate_negative_data(movie_start=1, movie_end=1682, N=500, writeToFile=False):
    """ every user at most generates N negative rating
    """
    file1 = open('user_sorted.data')
    file2 = open('negative.data',mode='w+')
    negative_data_return = []
    old_user_id = 1
    movie_has_rating = set()
    for line in file1:
        values = line.split()
        user_id = int(values[0])
        if user_id != old_user_id:
            count = 0
            for movie_id_iter in range(movie_start, movie_end+1):
                if movie_id_iter not in movie_has_rating:
                    count += 1
                    s = str(user_id-1) + ' ' + str(movie_id_iter) + ' 0'
                    if writeToFile:
                        file2.write(s+'\n')
                    negative_data_return.append(tuple(s.split()))
                    if count == N:
                        break
            movie_has_rating.clear()
            old_user_id = user_id
        movie_id = int(values[1])
        movie_has_rating.add(movie_id)
    file1.close()
    file2.close()
    return negative_data_return


def generate_libfm_data(data_source='movie_sorted.data' ,outputFileName='out.libfm', movie_start=1, movie_end=1682,
                        omitMovie=False, hasTime=False, binaryRating=False, addNegativeData=False):
    """ the output will be libfm file
    rating user:0-942 movie:943-2624 attribute:2625-2643 time:2644
    rating user:0-942 attribute:943-961 time:962  (omitMovie=True)
    rating user:0-942 attribute:943-961 (omitMovie=True hasTime=False)
    movie's id ranges from start to end
    the function hasTime hasn't been implemented
    """
    file1 = open('u.attribute')
    movie_attributes = []
    for line in file1:
        values = line.split()
        attribute = []
        count = 0
        for value in values:
            count += 1
            if value == '1':
                attribute.append(count)
        movie_attributes.append(attribute)
    file1.close()

    file1 = open(data_source)
    data = []
    for line in file1:
        values = line.split()
        if binaryRating and values[2] >= '1':
            values[2] = '1'
        one_tuple = (values[0], values[1], values[2], values[3])
        # 0:userID 1:movieID 2:rating 3:time
        if movie_start <= int(values[1]) <= movie_end:
            data.append(one_tuple)
    file1.close()

    if addNegativeData:
        negativeData = generate_negative_data(movie_start=movie_start, movie_end=movie_end, writeToFile=False)
        print len(negativeData)
        print len(data)
        choose_set = set()
        while len(choose_set) < len(data):
            choose_set.add(random.randint(0, len(negativeData)-1))
        for i in choose_set:
            data.append(tuple(negativeData[i]))

    file2 = open(outputFileName, mode="w+")
    for one_tuple in data:
        """ 59 7 4 888202941 -> 4 58:1 6:1 attributes time"""
        s = one_tuple[2] + ' ' + str(int(one_tuple[0])-1) + ':1 '
        count = 943
        if not omitMovie:
            s += str(int(one_tuple[1])+count-1) + ':1 '
            count = 943+1682
        for attribute_pos in movie_attributes[int(one_tuple[1])-1]:
            s += str(count+attribute_pos-1) + ':1 '
        if hasTime:
            pass
        file2.write(s+'\n')
    file2.close()

# generate_libfm_data('train.libfm',movie_start=1, movie_end=1000)
# generate_libfm_data('test.libfm',movie_start=1001, movie_end=1100)
# generate_libfm_data('u1.base', 'train_u1.libfm')
# generate_libfm_data('u1.test', 'test_u1.libfm')
# generate_libfm_data(outputFileName='train_binary.libfm', movie_start=1, movie_end=1000, binaryRating=True, addNegativeData=True, omitMovie=False)
# generate_libfm_data(outputFileName='test_binary.libfm', movie_start=1001, movie_end=1001, binaryRating=True, addNegativeData=True, omitMovie=False)
