__author__ = 'fenixlin'

import os
import cPickle
import random
import numpy as np
import scipy.sparse as sp
from parser import MLParser

class Database(object):

    def __init__(self, dataFormat, user_num, item_num, ratingfile, itemfile=None, userfile=None):
        if dataFormat=="movielens":
            self.parser = MLParser(ratingfile, itemfile, userfile)
        elif dataFormat=="amazon":
            self.parser = AmazonParser(ratingfile, itemfile, userfile)
        else:
            raise ValueError
            
        # nums must be explicitly assigned, since we won't get it from recovered data directly 
        self.USER_NUM = user_num
        self.ITEM_NUM = item_num
        
        self.storage_dir = "./Generate"
        self.itemfile = itemfile
        self.ratingfile = ratingfile
        self.userfile = userfile

        # holding all underlying data
        self.rating_list = []
        self.attribute_list = []

        # holding substitutable training and testing data
        self.train_matrix = None
        self.train_item_id_of_col = None
        self.test_matrix = None
        self.test_item_id_of_col = None

    def load_data(self, sort_data=True):
        #XXX: specify dumpable.data, use more assigning
        try:
            self._recover_dumpable_data(self.storage_dir+"dumpable.data")
        except:
            self.parser.load_raw_data()
            self.attribute_list = self.parser.extract_attr_list()
            self.rating_list = self.parser.extract_rating_list(sort_data)
            #XXX: seems not necessary to dump
            #self._dump_rating_list(self.storage_dir+"dumpable.data")

    def make_train_test_matrix(self, train_test_ratio = 0.8):
        #FIXME: maybe separate by item is more appropriate
        self.train_matrix, self.train_item_id_of_col, _ = self._extract_rating_matrix(0, int(self.ITEM_NUM*train_test_ratio))
        self.test_matrix, self.test_item_id_of_col, _ = self._extract_rating_matrix(int(self.ITEM_NUM*train_test_ratio)+1, self.ITEM_NUM-1)

    def _recover_dumpable_data(self, filename):
        f = open(filename, mode='rb')
        self.rating_list = cPickle.load(f)
        f.close()

    def _dump_rating_list(self, filename):
        #XXX: seems not necessary
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)
        f = open(self.storage_dir+filename, 'wb')
        cPickle.dump(self.rating_list, f, protocol=2)
        f.close()

    def add_negative_data(self, source='both', addAllUsers=False):
        #XXX: merge it into making training data
        """if this is test data for binary classification, then you should choose addAllUsers """
        if source == 'train' or source == 'both':
            self.train_matrix = self._add_neg_to_matrix(self.train_matrix, addAllUsers)
        if source == 'test' or source == 'both':
            self.test_matrix = self._add_neg_to_matrix(self.test_matrix, addAllUsers)

    def _add_neg_to_matrix(self, matrix, addAllUsers=False):
        height, width = matrix.get_shape()
        if addAllUsers:
            for i in range(height):
                for j in range(width):
                    if matrix[i, j] == 0:
                        matrix[i, j] = -1
        else:
            count = 0
            target = matrix.nnz
            while count < target:
                i = random.randint(0, height-1)
                j = random.randint(0, width-1)
                if matrix[i, j] == 0:
                    count += 1
                    matrix[i, j] = -1
        return matrix

    def dump_libfm_data(self, train_file=None, test_file=None, shuffle=True, omit_item=False):
        #XXX: define source from train or test
        # output libfm format data from core data
        # [rating item attribute] if omit_item==False, [rating attribute] if omit_item==True
        if train_file!=None:
            self._dump_to_libfm_file(train_file, self.train_matrix, self.train_item_id_of_col, shuffle, omit_item)
        if test_file!=None:
            self._dump_to_libfm_file(test_file, self.test_matrix, self.test_item_id_of_col, shuffle, omit_item)

    def _dump_to_libfm_file(self, filename, matrix, idx, shuffle=True, omit_item=False):
        row, col = matrix.nonzero()
        height, width = matrix.get_shape()
        libfm_data = []
        for i in range(len(row)):
            x = row[i]
            y = col[i]
            rating = matrix[x,y]
            libfm_line = [str(rating), str(x)+':1']
            filled_num = height 
            if not omit_item:
                libfm_line.append(str(y+filled_num) + ':1')
                filled_num += width
            for attribute_pos in self.attribute_list[idx[y]]:
                libfm_line.append(str(filled_num+attribute_pos) + ':1')
            libfm_data.append(libfm_line)
        if shuffle:
            random.shuffle(libfm_data)
        libfm_file = open(filename, 'w')
        for line in libfm_data:
            for i in range(len(line)-1):
                libfm_file.write(line[i]+' ')
            libfm_file.write(line[len(line)-1]+'\n')
        libfm_file.close()

    def _extract_rating_matrix(self, head, tail):
        # get specific rating matrix from sorted rating data(one rating per line)
        col_num_of_item = [-1 for i in range(self.ITEM_NUM)] # we may not have all items, so compression is needed
        item_id_of_col = []
        rating_matrix = np.zeros([self.USER_NUM, tail-head+1])
        item_count = -1
        for values in self.rating_list:
            userID = values[0]
            itemID = values[1]
            if itemID < head or itemID > tail:
                continue
            if col_num_of_item[itemID] < 0:
                item_count += 1
                col_num_of_item[itemID] = item_count
                item_id_of_col.append(itemID)
            rating = values[2]
            rating_matrix[userID, col_num_of_item[itemID]] = rating
        rating_matrix = sp.coo_matrix(rating_matrix[:, :item_count]).tolil() # item_count is actual compressed column num
        print 'rating matrix is {0}*{1}'.format(self.USER_NUM, item_count)
        return rating_matrix, item_id_of_col, col_num_of_item

##########################################################################
    #XXX:not that necessary

    def store_data_to_file(self, data_list=None, fileName='a.out', serialization=False, slice_range=None):
        #XXX:dumping core data
        """ slice_range is only a slice of record's position in this data_list """
        if data_list is None:
            data_list = self.core_rating_list
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

    def make_shuffle(self):
        #XXX:we use it nowhere
        self.out_rating_list = self.core_rating_list[:]
        random.shuffle(self.out_rating_list)

    def make_alternative_user_item_matrix(self, data_list):
        #XXX:we use it nowhere!
        self.alternative_user_item_matrix.clear()
        self.alternative_item_user_matrix.clear()

        self.alternative_user_set.clear()
        self.alternative_item_set.clear()
        for values in data_list:
            userID = values[0]
            itemID = values[1]
            self.alternative_user_set.add(userID)
            self.alternative_item_set.add(itemID)
            if self.alternative_user_item_matrix.get(userID) is None:
                self.alternative_user_item_matrix[userID] = dict()
                self.alternative_user_item_matrix[userID][itemID] = True
            else:
                self.alternative_user_item_matrix[userID][itemID] = True

            if self.alternative_item_user_matrix.get(itemID) is None:
                self.alternative_item_user_matrix[itemID] = dict()
                self.alternative_item_user_matrix[itemID][userID] = True
            else:
                self.alternative_item_user_matrix[itemID][userID] = True

    def make_slice(self, userID_slice=None, itemID_slice=None, rating_slice=None, data_list=None,
                   itemProductionDate_slice=None, count_item_slice=None):
        #XXX: slice into train and test items?
        """ id slice = set([x1,x2,x3, ...])   itemProduction_slice = [start, end]
        count_item_slice reads items and takes counts, it will select the number start to end items
        """
        if data_list is None:
            data_list = self.core_rating_list

        def f(x):
            if x is not None:
                return set(x)
            return None
        userID_slice = f(userID_slice)
        itemID_slice = f(itemID_slice)
        rating_slice = f(rating_slice)
        count_item_slice = f(count_item_slice)

        start_date = end_date = 0
        if itemProductionDate_slice:
            start_date = itemProductionDate_slice[0]
            end_date = itemProductionDate_slice[1]

        already_count_item_set = set()
        self.out_rating_list = []
        for values in data_list:
            already_count_item_set.add(values[1])  # add this item into count_item set
            item_ranking_number = len(already_count_item_set)  # this item's No
            if (userID_slice and values[0] not in userID_slice) or (itemID_slice and values[1] not in itemID_slice) \
                or (rating_slice and values[2] not in rating_slice) \
                    or (count_item_slice and item_ranking_number not in count_item_slice) \
                    or (itemProductionDate_slice and (end_date < values[5] or values[5] < start_date)):
                continue
            self.out_rating_list.append(values)

    def load_core_rating_list(self, data_list):
        #XXX:
        self.core_rating_list = data_list[:]

    def extract_data_from_file(self, fileName):
        #XXX:
        f = open('./Generate/'+fileName, mode='rb')
        self.core_rating_list = cPickle.load(f)
        f.close()

    def _calculate_item_avg_user_mse(self):
        #XXX:cal with numpy
        self.make_user_item_rating_matrix(self.rating_list)
        self.item_avg_rating = [0] * (self.TOTAL_NUM+1)
        self.user_MSE = [0] * (self.TOTAL_USERS+1)
        for itemID in self.item_user_rating_matrix:
            rating_sum = 0
            rating_num = 0
            for userID in self.item_user_rating_matrix[itemID]:
                rating_num += 1
                rating_sum += self.item_user_rating_matrix[itemID][userID]
            self.item_avg_rating[itemID] = float(rating_sum)/rating_num
        for userID in self.user_item_rating_matrix:
            for itemID in self.user_item_rating_matrix[userID]:
                difference = (float(self.user_item_rating_matrix[userID][itemID])-self.item_avg_rating[itemID])
                self.user_MSE[userID] += difference*difference

        self.calculate_item_avg_user_mse()

    #XXX
class DataProcess(object):

    def __init__(self):
        self.train_original_data = []
        self.train_addNegative_data = []
        self.test_original_data = []
        self.test_addAllNegative_data = []

        self.train_rating_numpy_matrix = []
        self.train_from_item_id_get_item_num = []
        self.train_from_item_num_get_item_id = []
        self.test_rating_numpy_matrix = []
        self.test_from_item_id_get_item_num = []
        self.test_from_item_num_get_item_id = []
        self.itemDataBase = None
        self.generate_data()

    def generate_data(self):
        db = Database()
        db.load_data_from_file()
        db.generate_dumpable_data(regenerate=False)

        self.TRAIN_NUM = 1200
        self.TEST_NUM = 240

        itemDataBase.make_sorted_rating_list([5, 1, 0])
        sorted_rating_list = itemDataBase.out_rating_list[:]
        itemDataBase.synchronize()
        itemDataBase.make_slice(count_item_slice=range(1, self.TRAIN_NUM+1))
        itemDataBase.synchronize()
        itemDataBase.compute_numpy_matrix()
        self.train_rating_numpy_matrix = itemDataBase.numpy_rating_matrix
        self.train_from_item_num_get_item_id = itemDataBase.from_item_num_get_item_id
        self.train_from_item_id_get_item_num = itemDataBase.from_item_id_get_item_num

        self.train_original_data = itemDataBase.core_rating_list[:]
        itemDataBase.store_data_to_file(fileName='train_original_data')
        itemDataBase.generate_libfm_data(omit=True)
        itemDataBase.store_data_to_file(itemDataBase.libfm_data, 'train_step2.libfm')

        itemDataBase.add_negative_data()
        itemDataBase.synchronize()
        self.train_addNegative_data = itemDataBase.core_rating_list[:]
        itemDataBase.store_data_to_file(fileName='train_addNegative_data')
        itemDataBase.generate_libfm_data(omit=True)
        itemDataBase.store_data_to_file(itemDataBase.libfm_data, 'train_step1.libfm')

        itemDataBase.load_core_rating_list(sorted_rating_list)
        itemDataBase.make_slice(count_item_slice=range(self.TRAIN_NUM+1, self.TRAIN_NUM+self.TEST_NUM+1))
        itemDataBase.synchronize()
        itemDataBase.compute_numpy_matrix()
        self.test_rating_numpy_matrix = itemDataBase.numpy_rating_matrix
        self.test_from_item_num_get_item_id = itemDataBase.from_item_num_get_item_id
        self.test_from_item_id_get_item_num = itemDataBase.from_item_id_get_item_num

        self.test_original_data = itemDataBase.core_rating_list[:]
        itemDataBase.store_data_to_file(fileName='test_original_data')
        itemDataBase.generate_libfm_data(shuffle=False)
        itemDataBase.store_data_to_file(itemDataBase.libfm_data, fileName='test_step3.libfm')

        itemDataBase.add_negative_data(addAllUsers=True)
        itemDataBase.synchronize()
        self.test_addAllNegative_data = itemDataBase.core_rating_list[:]
        itemDataBase.store_data_to_file(fileName='test_addAllNegative_data')
        itemDataBase.generate_libfm_data(omit=True, shuffle=False)
        itemDataBase.store_data_to_file(itemDataBase.libfm_data, 'test_step1.libfm')
        itemDataBase.store_data_to_file(itemDataBase.libfm_data, 'test_step2.libfm')
        self.itemDataBase = itemDataBase
