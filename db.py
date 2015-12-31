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
        self.RATING_NUM = -1 # assign when data loaded
        
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
            self.RATING_NUM = len(self.rating_list)
            #XXX: seems not necessary to dump
            #self._dump_rating_list(self.storage_dir+"dumpable.data")

    def make_train_test_matrix(self, train_test_ratio = 0.8):
        self.train_matrix, self.train_item_id_of_col, _ = \
            self._extract_rating_matrix( \
            self._filtered_rating_list(0, int(self.ITEM_NUM*train_test_ratio)))
        self.test_matrix, self.test_item_id_of_col, _ = \
            self._extract_rating_matrix( \
            self._filtered_rating_list(int(self.ITEM_NUM*train_test_ratio)+1, self.ITEM_NUM-1))

    def add_negative_data(self, source='both', addAllUsers=False):
        """if this is test data for binary classification, then you should choose addAllUsers """
        if source == 'train' or source == 'both':
            self.train_matrix = self._add_neg_to_matrix(self.train_matrix, addAllUsers)
        if source == 'test' or source == 'both':
            self.test_matrix = self._add_neg_to_matrix(self.test_matrix, addAllUsers)

    def dump_libfm_data(self, train_file=None, test_file=None, shuffle=True, omit_item=False):
        #XXX: define source from train or test
        # output libfm format data from core data
        # [rating item attribute] if omit_item==False, [rating attribute] if omit_item==True
        if train_file!=None:
            self._dump_to_libfm_file(train_file, self.train_matrix, self.train_item_id_of_col, shuffle, omit_item)
        if test_file!=None:
            self._dump_to_libfm_file(test_file, self.test_matrix, self.test_item_id_of_col, shuffle, omit_item)

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

    def _add_neg_to_matrix(self, matrix, addAllUsers=False):
        height, width = matrix.get_shape()
        count = 0
        if addAllUsers:
            for i in range(height):
                for j in range(width):
                    if matrix[i, j] == 0:
                        count += 1
                        matrix[i, j] = -1
                        if count%20000==0:
                            print count,"negative rating added..."
        else:
            target = matrix.nnz
            while count < target:
                i = random.randint(0, height-1)
                j = random.randint(0, width-1)
                if matrix[i, j] == 0:
                    count += 1
                    matrix[i, j] = -1
                if count%20000==0:
                    print count,"negative rating added..."
        print count,"negative rating added in total."
        return matrix

    def _dump_to_libfm_file(self, filename, matrix, item_id_of_col, shuffle=True, omit_item=False):
        row, col = matrix.nonzero()
        height, width = matrix.get_shape()
        index = range(len(row))
        if shuffle:
            random.shuffle(index)
        count = 0
        libfm_file = open(filename, 'w')
        for i in index:
            x = row[i]
            y = col[i]
            rating = matrix[x,y]
            libfm_file.write(str(rating)+' '+str(x)+':1')
            filled_num = height 
            if not omit_item:
                libfm_file.write(' '+str(y+filled_num)+':1')
                filled_num += width
            for attribute_pos in self.attribute_list[item_id_of_col[y]]:
                libfm_file.write(' '+str(filled_num+attribute_pos)+':1')
            libfm_file.write('\n')
            count += 1
            if count%20000==0:
                print filename,count,'lines written...'
        libfm_file.close()
        print filename,count,'lines written in total.'

    def _filtered_rating_list(self, head_item_count, tail_item_count):
        item_num_of_id = dict()
        for values in self.rating_list:
            itemID = values[1]
            if not item_num_of_id.has_key(itemID):
                item_num_of_id[itemID] = len(item_num_of_id)
            item_num = item_num_of_id[itemID]
            if item_num>=head_item_count and item_num<=tail_item_count:
                yield values

    def _extract_rating_matrix(self, rating_list):
        # get specific rating matrix from given rating list(one rating per line)
        col_num_of_item = [-1 for i in range(self.ITEM_NUM)] # we may not have all items, so compression is needed
        item_id_of_col = []
        rating_matrix = np.zeros([self.USER_NUM, self.ITEM_NUM])
        item_count = -1
        for values in rating_list:
            userID = values[0]
            itemID = values[1]
            if col_num_of_item[itemID] < 0:
                item_count += 1
                col_num_of_item[itemID] = item_count
                item_id_of_col.append(itemID)
            rating = values[2]
            rating_matrix[userID, col_num_of_item[itemID]] = rating
        rating_matrix = sp.coo_matrix(rating_matrix[:, :item_count]).tolil() # item_count may not reach max_item_num
        print 'rating matrix is {0}*{1}'.format(self.USER_NUM, item_count)
        return rating_matrix, item_id_of_col, col_num_of_item
